(in-package #:topic-maps.ctm)

(defstruct (parser (:constructor make-parser (lexer document-iri wildcard-iri wildcard-counter)))
  lexer document-iri wildcard-iri wildcard-counter lookahead
  (wildcards (make-hash-table :test #'equal)) (prefixes (make-hash-table :test #'equal)))
(defun look (parser)
  (or (parser-lookahead parser)
      (setf (parser-lookahead parser) (next-token (parser-lexer parser)))))
(defun consume (parser)
  (prog1 (look parser) (setf (parser-lookahead parser) nil)))
(defun punctuation-p (parser character)
  (and (eq :punctuation (token-kind (look parser)))
       (eql character (token-value (look parser)))))

(defun require-wildcard-environment (iri counter)
  (handler-case (require-document-iri iri)
    (ctm-rejection () (problem 'ctm-rejection :invalid-wildcard-iri 0 "Wildcard IRI must be an absolute, fragment-free IRI.")))
  (unless (and (integerp counter) (>= counter 0))
    (problem 'ctm-rejection :invalid-wildcard-counter 0 "Wildcard counter must be a non-negative integer.")))

(defun wildcard-locator (parser &optional name)
  "CTM 3.3.8: cache locators, not Lisp object handles; identity uses INTERN-TOPIC."
  (or (and name (gethash name (parser-wildcards parser)))
      (let ((iri (format nil "~A#$__~D~@[.~A~]" (parser-wildcard-iri parser)
                         (incf (parser-wildcard-counter parser)) name)))
        (when name (setf (gethash name (parser-wildcards parser)) iri)) iri)))

(defun topic-reference-start-p (token)
  (or (member (token-kind token) '(:identifier :iri :qname :wildcard))
      (and (eq :punctuation (token-kind token)) (find (token-value token) "=^["))))

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
      (:wildcard
       (when explicit-kind
         (problem 'ctm-rejection :expected-iri (token-position token) "Explicit = or ^ needs an IRI reference."))
       (values :item-identifier (wildcard-locator parser (token-value token))))
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

(defun topic-reference (parser map)
  "CTM 3.3.7: one recursive reference path for Types, Players and Scope themes."
  (if (punctuation-p parser #\[)
      (progn
        (consume parser)
        (let ((topic (topic-maps.tmdm:intern-topic map :item-identifier (wildcard-locator parser))))
          (read-topic-tail parser map topic #\] :required t)))
      (identity-reference parser map)))

(defun read-scope (parser map)
  "CTM 3.3.9: optional @ followed by a nonempty comma-separated Topic set.
Use the shared Topic reference resolver, including Embedded Topics and Wildcards.
The owning information item is not constructed until this function finishes."
  (when (punctuation-p parser #\@)
    (consume parser)
    (let ((themes nil))
      (loop
        ;; A reifier marker where a Theme is required is malformed Scope,
        ;; while a reifier after a complete Scope belongs to its statement.
        (unless (parser-lookahead parser)
          (skip-layout (parser-lexer parser))
          (when (eql #\~ (peek-character (parser-lexer parser)))
            (problem 'ctm-rejection :expected-scope-theme (lexer-cursor (parser-lexer parser))
                     "Expected a Theme, not a reifier marker.")))
        (let ((token (look parser)))
          (unless (topic-reference-start-p token)
            (problem 'ctm-rejection :expected-scope-theme (token-position token)
                     "Expected a Topic reference after '@' or the scope comma."))
          (push (topic-reference parser map) themes))
        (if (punctuation-p parser #\,) (consume parser) (return (nreverse themes)))))))

(defun literal-iri-reference (parser)
  "An IRI locator, not a Topic identity. Used for values/datatype syntax."
  (let ((token (consume parser)))
    (case (token-kind token)
      (:iri (resolve-iri (token-value token) (parser-document-iri parser) (token-position token)))
      (:qname (resolve-qname parser token))
      (otherwise (problem 'ctm-rejection :expected-datatype-iri (token-position token)
                          "A datatype qualifier requires an IRI reference, not a Topic identifier.")))))

(defun read-literal (parser &optional (context :occurrence))
  "Shared CTM 3.4.1 literal reader for Occurrences and Variants."
  (let ((token (look parser)))
    (case (token-kind token)
      (:integer
       (consume parser)
       ;; Numeric-literal value policy: represent the unquoted integer value
       ;; canonically; qualified quoted strings retain their lexical value.
       (values (topic-maps.tmdm:canonical-integer-lexical-form (token-value token))
               (topic-maps.tmdm:integer-datatype)))
      (:decimal
       (consume parser)
       ;; Same value-representation policy as bare integers; token spelling is
       ;; retained by the lexer, qualified strings remain lexical model data.
       (values (topic-maps.tmdm:canonical-decimal-lexical-form (token-value token))
               (topic-maps.tmdm:decimal-datatype)))
      (:date
       (consume parser)
       (values (topic-maps.tmdm:canonical-date-lexical-form (token-value token)) (topic-maps.tmdm:date-datatype)))
      (:datetime
       (consume parser)
       (multiple-value-bind (value reason) (topic-maps.tmdm:canonical-datetime-lexical-form (token-value token))
         (unless value (problem 'ctm-unsupported
                         (if (eq reason :unsupported-bce-timezone-rollover)
                             :datetime-bce-timezone-rollover :datetime-leap-second-context)
                         (token-position token) "DateTime normalization is outside the supported BCE/leap-second calendar context."))
         (values value (topic-maps.tmdm:datetime-datatype))))
      (:excluded-literal
       (problem 'ctm-unsupported (if (eq context :variant) :variant-literal-datatype :occurrence-literal-datatype) (token-position token)
                "The separate CTM '*' literal is outside this slice."))
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
             (when (and (string= datatype (topic-maps.tmdm:decimal-datatype))
                        (not (topic-maps.tmdm:decimal-lexical-p (token-value token))))
               (problem 'ctm-rejection :invalid-decimal-value (token-position token)
                        "Quoted value is not an xsd:decimal lexical form."))
             (when (and (string= datatype (topic-maps.tmdm:date-datatype))
                        (not (topic-maps.tmdm:date-lexical-p (token-value token))))
               (problem 'ctm-rejection :invalid-date-value (token-position token)
                        "Quoted value is not a valid XSD 1.0 date lexical form."))
             (when (and (string= datatype (topic-maps.tmdm:datetime-datatype))
                        (not (topic-maps.tmdm:datetime-lexical-p (token-value token))))
               (problem 'ctm-rejection :invalid-datetime-value (token-position token)
                        "Quoted value is not a valid XSD 1.0 dateTime."))
             ;; TMDM 4.4 requires absolute anyURI content; quoted content is
             ;; lexical data, never an IRI reference to resolve against the document.
             (when (and (string= datatype (topic-maps.tmdm:iri-datatype))
                        (not (topic-maps.tmdm::absolute-locator-p (token-value token))))
               (problem 'ctm-rejection :relative-uri-value (token-position token)
                        "A quoted anyURI value must already be absolute (TMDM 4.4)."))
             (values (token-value token) datatype)))
           (values (token-value token) (topic-maps.tmdm:string-datatype))))
      ((:iri :qname) (values (literal-iri-reference parser) (topic-maps.tmdm:iri-datatype)))
      (otherwise (problem 'ctm-rejection (if (eq context :variant) :expected-variant-value :expected-occurrence-value)
                          (token-position token) "Expected a supported CTM literal value.")))))

(defun read-reifier (parser map)
  "CTM 3.3.10: reuse the full Topic reference resolver, retaining the marker position."
  (when (punctuation-p parser #\~)
    (let ((position (token-position (consume parser))))
      (unless (topic-reference-start-p (look parser))
        (problem 'ctm-rejection :expected-reifier-topic (token-position (look parser)) "Expected a Topic reference after '~'."))
      (values (topic-reference parser map) position))))
(defun attach-reifier (item topic position)
  (when topic
    (handler-case (setf item (topic-maps.tmdm:set-item-reifier item topic))
      (topic-maps.tmdm:reification-error (c)
        (problem 'ctm-rejection (topic-maps.tmdm:reification-error-code c) position (princ-to-string c)))
      (topic-maps.tmdm:variant-error (c)
        (problem 'ctm-rejection (topic-maps.tmdm:variant-error-code c) position (princ-to-string c)))))
  item)

(defun read-identity-tail (parser map topic)
  (let* ((start (look parser)) (embedded (punctuation-p parser #\[))
         (type (when embedded (topic-reference parser map))))
    ;; Identity tail statements add directly to their owner, without constructing
    ;; an intermediate Topic. Identity-form Type references use the same resolver.
    (multiple-value-bind (kind iri) (unless embedded (identity-value parser))
      (if (punctuation-p parser #\:)
          (progn
            (consume parser)
            (multiple-value-bind (value datatype) (read-literal parser)
              (let* ((type (or type (topic-maps.tmdm:intern-topic map kind iri)))
                     (scope (read-scope parser map)))
                (multiple-value-bind (r position) (read-reifier parser map)
                  (attach-reifier (topic-maps.tmdm:add-occurrence topic type value :datatype datatype :scope scope) r position))
                (topic-maps.tmdm:canonical-topic topic))))
          (if (or embedded (member (token-kind start) '(:identifier :wildcard)))
              (if (and (eq :identifier (token-kind start)) (punctuation-p parser #\())
                  (problem 'ctm-unsupported :topic-tail (token-position start) "Template invocations are outside this subset.")
                  (problem 'ctm-rejection :expected-occurrence-type-separator (token-position (look parser))
                           "Expected ':' after the Occurrence Type."))
              (topic-maps.tmdm:add-topic-identifier topic kind iri))))))

(defun read-variant (parser map name)
  (consume parser)
  (multiple-value-bind (value datatype) (read-literal parser :variant)
    (unless (punctuation-p parser #\@)
      (problem 'ctm-rejection :expected-variant-scope (token-position (look parser)) "A Variant requires an explicit '@' Scope."))
    (let* ((scope-position (token-position (look parser))) (themes (read-scope parser map)))
      (multiple-value-bind (r position) (read-reifier parser map)
        (unless (punctuation-p parser #\))
          (problem 'ctm-rejection :missing-variant-close (token-position (look parser)) "Expected ')' after the Variant Scope/Reifier."))
        (consume parser)
        (handler-case
            (attach-reifier (topic-maps.tmdm:add-variant name value :datatype datatype
              :scope (append (topic-maps.tmdm:topic-name-scope name) themes)) r position)
          (topic-maps.tmdm:variant-error (c)
            (problem 'ctm-rejection (topic-maps.tmdm:variant-error-code c) scope-position (princ-to-string c))))))))

(defun read-name (parser map topic)
  "CTM 3.11: optional Topic reference plus ':' followed by a string.
Use the shared Topic reference resolver."
  (let* ((token (look parser))
         (typed (topic-reference-start-p token))
         (type (when typed (topic-reference parser map))))
    (when typed
      (unless (punctuation-p parser #\:)
        (problem 'ctm-rejection :expected-name-type-separator
                 (token-position (look parser)) "Expected ':' after the name type."))
      (consume parser))
    (let ((value (consume parser)))
      (unless (eq :string (token-kind value))
        (problem 'ctm-rejection :expected-name-value (token-position value)
                 "Expected a quoted name value after '-' or the name type separator."))
      (let ((scope (read-scope parser map)))
        (multiple-value-bind (r position) (read-reifier parser map)
          (let ((name (attach-reifier
                        (if typed (topic-maps.tmdm:add-name topic (token-value value) :type type :scope scope)
                            (topic-maps.tmdm:add-name topic (token-value value) :scope scope)) r position)))
            (loop while (punctuation-p parser #\() do (read-variant parser map name))))))
    (topic-maps.tmdm:canonical-topic topic)))

(defun read-topic-tail (parser map topic terminator &key required)
  "CTM 3.9: the same Tail reader ends at '.' or the caller's Embedded ']'."
  (let ((has-tail nil) (seen-tail nil))
    (loop
      (cond
        ((punctuation-p parser terminator)
         (when (and required (not seen-tail))
           (problem 'ctm-rejection :expected-topic-tail (token-position (look parser)) "An Embedded Topic requires a nonempty Topic Tail."))
         (consume parser) (return (topic-maps.tmdm:canonical-topic topic)))
        ((and (char= terminator #\]) (punctuation-p parser #\.))
         (problem 'ctm-rejection :missing-embedded-close (token-position (look parser)) "Embedded Topics end with ']', not a period."))
        ((punctuation-p parser #\-)
         (when has-tail
           (problem 'ctm-rejection :expected-separator (token-position (look parser)) "Topic-tail statements need a semicolon separator."))
         (consume parser)
         (setf topic (read-name parser map topic))
         (setf has-tail t seen-tail t))
        ((and has-tail (punctuation-p parser #\;))
         (consume parser)
         (setf has-tail nil))
        ((eq :eof (token-kind (look parser)))
         (problem 'ctm-rejection (if (char= terminator #\]) :missing-embedded-close :missing-period)
                  (token-position (look parser)) "Expected the closing Topic/Embedded Topic delimiter."))
        ((topic-reference-start-p (look parser))
         (when has-tail
           (problem 'ctm-rejection :expected-separator (token-position (look parser)) "Topic-tail statements need a semicolon separator."))
         (setf topic (read-identity-tail parser map topic) has-tail t seen-tail t))
        ((punctuation-p parser #\()
         (problem 'ctm-rejection :unexpected-variant (token-position (look parser)) "A Variant must immediately follow a Topic Name."))
        (t (problem 'ctm-rejection :unexpected-token (token-position (look parser)) "Unexpected token after topic or name."))))))

(defun read-association (parser map type)
  "CTM 3.13: one or more Role declarations; optional Scope and Reifiers."
  (consume parser) ; opening parenthesis already recognized by the caller
  (let ((roles nil) (role-reifiers nil))
    (loop
      (when (or (punctuation-p parser #\)) (eq :eof (token-kind (look parser))))
        (problem 'ctm-rejection :expected-role (token-position (look parser)) "Expected a nonempty Association role declaration."))
      (let* ((role-type (topic-reference parser map))
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
        (let ((player (topic-reference parser map)))
          (push (list role-type player) roles)
          (multiple-value-bind (r position) (read-reifier parser map)
            (push (list role-type player r position) role-reifiers))))
      (cond ((punctuation-p parser #\,) (consume parser))
            ((punctuation-p parser #\)) (consume parser) (return))
            ((eq :eof (token-kind (look parser)))
             (problem 'ctm-rejection :missing-association-close (token-position (look parser)) "Expected ')' after the Roles."))
            (t (problem 'ctm-rejection :expected-role-separator (token-position (look parser)) "Expected ',' or ')' after a Role."))))
    (let ((scope (read-scope parser map)))
      (multiple-value-bind (r position) (read-reifier parser map)
        (let ((association (topic-maps.tmdm:make-association map type (nreverse roles) :scope scope)))
          (dolist (entry (nreverse role-reifiers))
            (destructuring-bind (role-type player reifier marker) entry
              (let ((role (find-if (lambda (role)
                            (and (eq (topic-maps.tmdm:canonical-topic role-type) (topic-maps.tmdm:association-role-type role))
                                 (eq (topic-maps.tmdm:canonical-topic player) (topic-maps.tmdm:association-role-player role))))
                                  (topic-maps.tmdm:association-roles association))))
                (attach-reifier role reifier marker))))
          (attach-reifier (topic-maps.tmdm:canonical-association association) r position))))))

(defun deserialize-string (text &key document-iri source-name (wildcard-iri document-iri) (wildcard-counter 0))
  "Read the documented CTM subset, with per-document prefixes and qualified strings.
Return the Map and final Wildcard Counter as two values. Wildcard IRI defaults
to Document IRI; local identifiers and relative IRIs still use Document IRI.
Source positions are zero-based character offsets; lines/columns are one-based."
  (check-type text string)
  (let ((*source-name* source-name) (*source-text* text))
    (require-document-iri document-iri)
    (require-wildcard-environment wildcard-iri wildcard-counter)
    (let ((parser (make-parser (make-lexer text) document-iri wildcard-iri wildcard-counter))
          (map (topic-maps.tmdm:make-topic-map)))
      (handler-bind ((topic-maps.tmdm:variant-error
                       (lambda (c) (problem 'ctm-rejection (topic-maps.tmdm:variant-error-code c)
                                             (lexer-cursor (parser-lexer parser)) (princ-to-string c))))
                     (topic-maps.tmdm:reification-error
                       (lambda (c) (problem 'ctm-rejection (topic-maps.tmdm:reification-error-code c)
                                             (lexer-cursor (parser-lexer parser)) (princ-to-string c)))))
        (loop while (eq :directive (token-kind (look parser))) do (read-prefix-directive parser))
        (multiple-value-bind (r position) (read-reifier parser map) (attach-reifier map r position))
        (loop until (eq :eof (token-kind (look parser))) do
          (when (punctuation-p parser #\~)
            (problem 'ctm-rejection :topic-map-reifier-position (token-position (look parser))
                     "Topic Map Reifier must precede all body declarations."))
          (if (eq :directive (token-kind (look parser)))
              (read-prefix-directive parser)
              (let* ((embedded (punctuation-p parser #\[)) (topic (topic-reference parser map)))
                (if (punctuation-p parser #\()
                    (read-association parser map topic)
                    (if embedded
                        (problem 'ctm-rejection :embedded-topic-at-top-level (token-position (look parser))
                                 "An Embedded Topic at top level must be an Association Type, not a standalone declaration.")
                        (read-topic-tail parser map topic #\.)))))))
      (values map (parser-wildcard-counter parser)))))

(defun deserialize-file (pathname &key document-iri source-name (wildcard-iri document-iri) (wildcard-counter 0))
  "Read a UTF-8 CTM file, with optional UTF-8 BOM, using an explicit Document IRI.
Other encoding directives are UNSUPPORTED. File I/O errors propagate unchanged."
  (let ((*source-name* source-name) (*source-text* ""))
    (require-document-iri document-iri)
    (require-wildcard-environment wildcard-iri wildcard-counter)
    (with-open-file (input pathname :direction :input :element-type '(unsigned-byte 8))
      (let ((bytes (make-array (file-length input) :element-type '(unsigned-byte 8))))
        (unless (= (length bytes) (read-sequence bytes input))
          (error "Input file changed or was truncated during reading."))
        (deserialize-string (decode-utf8 bytes :strip-bom t)
                            :document-iri document-iri :source-name source-name
                            :wildcard-iri wildcard-iri :wildcard-counter wildcard-counter)))))
