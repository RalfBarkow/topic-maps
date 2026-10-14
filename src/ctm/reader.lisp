(in-package #:topic-maps.ctm)

(defstruct (parser (:constructor make-parser (lexer document-iri))) lexer document-iri lookahead)
(defun look (parser)
  (or (parser-lookahead parser)
      (setf (parser-lookahead parser) (next-token (parser-lexer parser)))))
(defun consume (parser)
  (prog1 (look parser) (setf (parser-lookahead parser) nil)))
(defun punctuation-p (parser character)
  (and (eq :punctuation (token-kind (look parser)))
       (eql character (token-value (look parser)))))

(defun identity-reference (parser map &optional explicit-kind)
  (let ((token (consume parser)))
    (case (token-kind token)
      (:identifier
       (when explicit-kind
         (problem 'ctm-rejection :expected-iri (token-position token) "Explicit = or ^ needs an IRI reference."))
       (when (member (token-value token) '("def" "isa" "ako" "end") :test #'string=)
         (problem 'ctm-unsupported :unsupported-keyword (token-position token) "This keyword is outside Slice 1."))
       (topic-maps.tmdm:intern-topic map :item-identifier
          (concatenate 'string (parser-document-iri parser) "#" (token-value token))))
      (:iri
       (topic-maps.tmdm:intern-topic map (or explicit-kind :subject-identifier)
          (resolve-iri (token-value token) (parser-document-iri parser) (token-position token))))
      (:qname
       ;; No prefix declarations are supported in Slice 1. This is a specific
       ;; semantic rejection, not an I/O failure or an unsupported-parser stub.
       (problem 'undefined-prefix :undefined-prefix (token-position token)
                (format nil "Prefix ~S has no binding." (subseq (token-value token) 0
                                                               (position #\: (token-value token))))))
      (:punctuation
       (case (token-value token)
         (#\= (if explicit-kind
                   (problem 'ctm-rejection :expected-iri (token-position token) "Unexpected identity marker.")
                   (identity-reference parser map :subject-locator)))
         (#\^ (if explicit-kind
                   (problem 'ctm-rejection :expected-iri (token-position token) "Unexpected identity marker.")
                   (identity-reference parser map :item-identifier)))
         (otherwise (problem 'ctm-rejection :expected-topic-identity (token-position token) "Expected topic identity."))))
      (otherwise (problem 'ctm-rejection :expected-topic-identity (token-position token) "Expected topic identity.")))))

(defun read-topic (parser map)
  (let ((topic (identity-reference parser map)) (has-tail nil))
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
                      "Typed names are outside Slice 1 (CTM 3.11)."))
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
        ((and (eq :punctuation (token-kind (look parser)))
              (find (token-value (look parser)) "=^"))
         (problem 'ctm-unsupported :additional-identity (token-position (look parser)) "Topic-tail identity assignments are outside Slice 1."))
        ((member (token-kind (look parser)) '(:iri :qname))
         (problem 'ctm-unsupported :additional-identity (token-position (look parser)) "Topic-tail identity assignments are outside Slice 1."))
        ((eq :identifier (token-kind (look parser)))
         (problem 'ctm-unsupported :topic-tail (token-position (look parser)) "Type/identity/template topic tails are outside Slice 1."))
        (t (problem 'ctm-rejection :unexpected-token (token-position (look parser)) "Unexpected token after topic or name."))))))

(defun deserialize-string (text &key document-iri source-name)
  "Read the documented Slice 1 CTM subset into a new TMDM Topic Map.
Source positions are zero-based character offsets; lines/columns are one-based."
  (check-type text string)
  (let ((*source-name* source-name) (*source-text* text))
    (require-document-iri document-iri)
    (let ((parser (make-parser (make-lexer text) document-iri))
          (map (topic-maps.tmdm:make-topic-map)))
      (loop until (eq :eof (token-kind (look parser))) do (read-topic parser map))
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
