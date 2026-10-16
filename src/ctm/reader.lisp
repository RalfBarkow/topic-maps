(in-package #:topic-maps.ctm)

(defstruct (parser (:constructor make-parser (lexer document-iri)))
  lexer document-iri lookahead (prefixes (make-hash-table :test #'equal)))
(defun look (parser)
  (or (parser-lookahead parser)
      (setf (parser-lookahead parser) (next-token (parser-lexer parser)))))
(defun consume (parser)
  (prog1 (look parser) (setf (parser-lookahead parser) nil)))
(defun punctuation-p (parser character)
  (and (eq :punctuation (token-kind (look parser)))
       (eql character (token-value (look parser)))))

(defun resolve-qname (parser token)
  "CTM 3.3.4: concatenate the resolved binding and local part exactly once."
  (let* ((text (token-value token)) (colon (position #\: text))
         (prefix (subseq text 0 colon)) (bound (gethash prefix (parser-prefixes parser))))
    (unless bound
      (problem 'undefined-prefix :undefined-prefix (token-position token)
               (format nil "Prefix ~S has no binding." prefix)))
    ;; Do not re-resolve or percent-decode an already resolved binding.
    (validate-iri-characters (concatenate 'string bound (subseq text (1+ colon)))
                             (token-position token))))

(defun read-prefix-directive (parser)
  "CTM 3.16.1: document-ordered, per-deserialization bindings; reference is an IRI."
  (consume parser) ; %prefix
  (let ((name (consume parser)) (reference (consume parser)))
    (unless (eq :identifier (token-kind name))
      (problem 'ctm-rejection :expected-prefix-name (token-position name) "Expected a prefix identifier."))
    (unless (eq :iri (token-kind reference))
      (problem 'ctm-rejection :expected-prefix-iri (token-position reference)
               "A prefix binding requires an IRI, not a QName or Topic identifier."))
    (let* ((iri (resolve-iri (token-value reference) (parser-document-iri parser) (token-position reference)))
           (old (gethash (token-value name) (parser-prefixes parser))))
      (when (and old (not (string= old iri)))
        (problem 'prefix-collision :prefix-collision (token-position name)
                 (format nil "Prefix ~S is already bound to ~S, not ~S." (token-value name) old iri)))
      (setf (gethash (token-value name) (parser-prefixes parser)) iri))))

(defun identity-value (parser &optional explicit-kind)
  (let ((token (consume parser)))
    (case (token-kind token)
      (:identifier
       (when explicit-kind
         (problem 'ctm-rejection :expected-iri (token-position token) "Explicit = or ^ needs an IRI reference."))
       (when (member (token-value token) '("def" "isa" "ako" "end") :test #'string=)
         (problem 'ctm-unsupported :unsupported-keyword (token-position token) "This keyword is outside the implemented subset."))
       (values :item-identifier
          (concatenate 'string (parser-document-iri parser) "#" (token-value token))))
      (:iri
       (values (or explicit-kind :subject-identifier)
          (resolve-iri (token-value token) (parser-document-iri parser) (token-position token))))
      (:qname (values (or explicit-kind :subject-identifier) (resolve-qname parser token)))
      (:punctuation
       (case (token-value token)
         (#\= (if explicit-kind
                   (problem 'ctm-rejection :expected-iri (token-position token) "Unexpected identity marker.")
                   (identity-value parser :subject-locator)))
         (#\^ (if explicit-kind
                   (problem 'ctm-rejection :expected-iri (token-position token) "Unexpected identity marker.")
                   (identity-value parser :item-identifier)))
         (otherwise (problem 'ctm-rejection :expected-topic-identity (token-position token) "Expected topic identity."))))
      (otherwise (problem 'ctm-rejection :expected-topic-identity (token-position token) "Expected topic identity.")))))

(defun identity-reference (parser map)
  (multiple-value-bind (kind iri) (identity-value parser)
    (topic-maps.tmdm:intern-topic map kind iri)))

(defun literal-iri-reference (parser)
  "An IRI locator, not a Topic identity. Used for values/datatype syntax."
  (let ((token (consume parser)))
    (case (token-kind token)
      (:iri (resolve-iri (token-value token) (parser-document-iri parser) (token-position token)))
      (:qname (resolve-qname parser token))
      (otherwise (problem 'ctm-rejection :expected-datatype-iri (token-position token)
                          "A datatype qualifier requires an IRI reference, not a Topic identifier.")))))

(defun read-occurrence-literal (parser)
  (let ((token (look parser)))
    (case (token-kind token)
      (:integer
       (consume parser)
       ;; Numeric-literal value policy: represent the unquoted integer value
       ;; canonically; qualified quoted strings retain their lexical value.
       (values (topic-maps.tmdm:canonical-integer-lexical-form (token-value token))
               (topic-maps.tmdm:integer-datatype)))
      (:excluded-literal
       (problem 'ctm-unsupported :occurrence-literal-datatype (token-position token)
                "Decimal/date/dateTime and the separate CTM '*' literal are outside this slice."))
      (:string
       (consume parser)
       (if (punctuation-p parser #\^)
         (let ((caret (consume parser)))
           (unless (and (punctuation-p parser #\^)
                        (= (token-position (look parser)) (1+ (token-position caret))))
             (problem 'ctm-rejection :invalid-datatype-marker (token-position caret) "Expected contiguous '^^'."))
           (consume parser)
           (let ((datatype (literal-iri-reference parser)))
             (when (and (string= datatype (topic-maps.tmdm:integer-datatype))
                        (not (topic-maps.tmdm:integer-lexical-p (token-value token))))
               (problem 'ctm-rejection :invalid-integer-value (token-position token)
                        "Quoted value is not an xsd:integer lexical form."))
             ;; TMDM 4.4 requires absolute anyURI content; quoted content is
             ;; lexical data, never an IRI reference to resolve against the document.
             (when (and (string= datatype (topic-maps.tmdm:iri-datatype))
                        (not (topic-maps.tmdm::absolute-locator-p (token-value token))))
               (problem 'ctm-rejection :relative-uri-value (token-position token)
                        "A quoted anyURI value must already be absolute (TMDM 4.4)."))
             (values (token-value token) datatype)))
           (values (token-value token) (topic-maps.tmdm:string-datatype))))
      ((:iri :qname) (values (literal-iri-reference parser) (topic-maps.tmdm:iri-datatype)))
      (otherwise (problem 'ctm-rejection :expected-occurrence-value (token-position token)
                          "Expected an integer, quoted string or IRI-form Occurrence value.")))))

(defun read-identity-tail (parser map topic)
  (let ((start (look parser)))
    (multiple-value-bind (kind iri) (identity-value parser)
      (if (punctuation-p parser #\:)
          (progn
            (consume parser)
            (multiple-value-bind (value datatype) (read-occurrence-literal parser)
              (let ((type (topic-maps.tmdm:intern-topic map kind iri)))
                (topic-maps.tmdm:add-occurrence topic type value :datatype datatype)
                (topic-maps.tmdm:canonical-topic topic))))
          (if (eq :identifier (token-kind start))
              (if (punctuation-p parser #\()
                  (problem 'ctm-unsupported :topic-tail (token-position start) "Template invocations are outside this subset.")
                  (problem 'ctm-rejection :expected-occurrence-type-separator (token-position (look parser))
                           "Expected ':' after the Occurrence Type."))
              (topic-maps.tmdm:add-topic-identifier topic kind iri))))))

(defun read-topic (parser map &optional (topic (identity-reference parser map)))
  (let ((has-tail nil))
    (loop
      (cond
        ((punctuation-p parser #\.) (consume parser) (return topic))
        ((punctuation-p parser #\-)
         (when has-tail
           (problem 'ctm-rejection :expected-separator (token-position (look parser)) "Topic-tail statements need a semicolon separator."))
         (consume parser)
         (let ((value (consume parser)))
           (when (member (token-kind value) '(:identifier :iri :qname))
             ;; Recognize the typed-name syntax, without resolving its type
             ;; or creating information items for unsupported name semantics.
             (unless (punctuation-p parser #\:)
               (problem 'ctm-rejection :expected-name-type-separator
                        (token-position (look parser)) "Expected ':' after the name type."))
             (consume parser)
             (let ((literal (consume parser)))
               (unless (eq :string (token-kind literal))
                 (problem 'ctm-rejection :expected-name-value (token-position literal)
                          "Expected a quoted name value after the name type separator.")))
             (problem 'ctm-unsupported :typed-name (token-position value)
                      "Typed names are outside the implemented subset (CTM 3.11)."))
           (unless (eq :string (token-kind value))
             (problem 'ctm-rejection :expected-name-value (token-position value)
                      "Expected a quoted name value after '-'."))
           (topic-maps.tmdm:add-default-name topic (token-value value)))
         (setf has-tail t))
        ((and has-tail (punctuation-p parser #\;))
         (consume parser)
         (setf has-tail nil)
         (when (punctuation-p parser #\.) (consume parser) (return topic)))
        ((eq :eof (token-kind (look parser)))
         (problem 'ctm-rejection :missing-period (token-position (look parser)) "Topic declaration requires a final period."))
        ((or (and (eq :punctuation (token-kind (look parser)))
                  (find (token-value (look parser)) "=^"))
             (member (token-kind (look parser)) '(:identifier :iri :qname)))
         (when has-tail
           (problem 'ctm-rejection :expected-separator (token-position (look parser)) "Topic-tail statements need a semicolon separator."))
         (setf topic (read-identity-tail parser map topic) has-tail t))
        ((punctuation-p parser #\()
         (problem 'ctm-unsupported :variant (token-position (look parser)) "Variant names are outside the implemented subset."))
        (t (problem 'ctm-rejection :unexpected-token (token-position (look parser)) "Unexpected token after topic or name."))))))

(defun read-association (parser map type)
  "CTM 3.13, restricted to one or two role declarations; no scope/reifier."
  (consume parser) ; opening parenthesis already recognized by the caller
  (let ((roles nil) (third-position nil))
    (loop
      (when (or (punctuation-p parser #\)) (eq :eof (token-kind (look parser))))
        (problem 'ctm-rejection :expected-role (token-position (look parser)) "Expected a nonempty Association role declaration."))
      (when (= 2 (length roles)) (setf third-position (token-position (look parser))))
      (let* ((role-type (identity-reference parser map))
             (type-end (lexer-cursor (parser-lexer parser)))
             (colon (look parser)))
        (unless (punctuation-p parser #\:)
          (problem 'ctm-rejection :expected-role-type-separator (token-position colon) "Expected ':' after the Role type."))
        (consume parser)
        (let ((player-token (look parser)))
          ;; CTM role production requires layout on at least one side of ':'.
          ;; skip-layout handles whitespace and comments; gaps use source offsets.
          (unless (or (> (token-position colon) type-end)
                      (> (token-position player-token) (1+ (token-position colon))))
            (problem 'ctm-rejection :role-separator-whitespace (token-position colon)
                     "A Role separator needs whitespace or a comment on at least one side."))
          (when (or (eq :eof (token-kind player-token))
                    (punctuation-p parser #\)) (punctuation-p parser #\,))
            (problem 'ctm-rejection :expected-role-player (token-position player-token) "Expected a Topic as the Role player.")))
        (push (list role-type (identity-reference parser map)) roles))
      (cond ((punctuation-p parser #\,) (consume parser))
            ((punctuation-p parser #\)) (consume parser) (return))
            ((eq :eof (token-kind (look parser)))
             (problem 'ctm-rejection :missing-association-close (token-position (look parser)) "Expected ')' after the Roles."))
            (t (problem 'ctm-rejection :expected-role-separator (token-position (look parser)) "Expected ',' or ')' after a Role."))))
    (when (> (length roles) 2)
      (problem 'ctm-unsupported :association-arity third-position "Associations with more than two Role declarations are outside Slice 3."))
    (topic-maps.tmdm:make-association map type (nreverse roles))))

(defun deserialize-string (text &key document-iri source-name)
  "Read the documented CTM subset, with per-document prefixes and qualified strings.
Source positions are zero-based character offsets; lines/columns are one-based."
  (check-type text string)
  (let ((*source-name* source-name) (*source-text* text))
    (require-document-iri document-iri)
    (let ((parser (make-parser (make-lexer text) document-iri))
          (map (topic-maps.tmdm:make-topic-map)))
      (loop until (eq :eof (token-kind (look parser))) do
        (if (eq :directive (token-kind (look parser)))
            (read-prefix-directive parser)
            (let ((topic (identity-reference parser map)))
              (if (punctuation-p parser #\()
                  (read-association parser map topic)
                  (read-topic parser map topic)))))
      map)))

(defun deserialize-file (pathname &key document-iri source-name)
  "Read a UTF-8 CTM file, with optional UTF-8 BOM, using an explicit Document IRI.
Other encoding directives are UNSUPPORTED. File I/O errors propagate unchanged."
  (let ((*source-name* source-name) (*source-text* ""))
    (require-document-iri document-iri)
    (with-open-file (input pathname :direction :input :element-type '(unsigned-byte 8))
      (let ((bytes (make-array (file-length input) :element-type '(unsigned-byte 8))))
        (unless (= (length bytes) (read-sequence bytes input))
          (error "Input file changed or was truncated during reading."))
        (deserialize-string (decode-utf8 bytes :strip-bom t)
                            :document-iri document-iri :source-name source-name)))))
