(in-package #:topic-maps.ctm)

;; Resource policy, not a claim that recursive CTM syntax is invalid.
(defparameter *template-depth-limit* 256)

;;; CTM 3.14-3.15. Stored, grammar-checked concrete syntax is a reader object,
;;; not a second Topic Maps model. Execution reuses the ordinary readers.
(defun identifier-p (token name)
  (and (eq :identifier (token-kind token)) (string= name (token-value token))))

(defun call-with-token-checkpoint (parser thunk)
  (let ((cursor (lexer-cursor (parser-lexer parser)))
        (lookahead (parser-lookahead parser)) (remaining (parser-remaining parser))
        (recording (parser-recording parser)) (recorded (parser-recorded parser)))
    (unwind-protect (progn (setf (parser-recording parser) nil) (funcall thunk))
      (setf (lexer-cursor (parser-lexer parser)) cursor
            (parser-lookahead parser) lookahead (parser-remaining parser) remaining
            (parser-recording parser) recording (parser-recorded parser) recorded))))

(defun next-punctuation-p (parser char)
  (call-with-token-checkpoint parser (lambda () (consume parser) (punctuation-p parser char))))

(defun tail-invocation-p (parser)
  (and (eq :identifier (token-kind (look parser))) (next-punctuation-p parser #\()))

(defun global-invocation-p (parser)
  "Decide by syntax, never by whether a template happens to be defined.
A standalone colon in the first argument denotes a Role; QName colons are
already inside one lexer token. Embedded syntax is skipped with balanced depth."
  (and (tail-invocation-p parser)
       (call-with-token-checkpoint parser
         (lambda ()
           (consume parser) (consume parser)
           (let ((depth 0))
             (loop for token = (consume parser) do
               (when (eq :eof (token-kind token)) (return t))
               (when (eq :punctuation (token-kind token))
                 (let ((c (token-value token)))
                   (cond ((and (zerop depth) (char= c #\:)) (return nil))
                         ((and (zerop depth) (find c ",)")) (return t))
                         ((find c "([") (incf depth))
                         ((find c ")]" ) (decf depth)))))))))))

(defun call-with-tokens (parser tokens thunk)
  (let ((cursor (lexer-cursor (parser-lexer parser)))
        (lookahead (parser-lookahead parser)) (remaining (parser-remaining parser))
        (replay (parser-replay-p parser)))
    (unwind-protect
        (progn (setf (parser-replay-p parser) t (parser-remaining parser) tokens
                     (parser-lookahead parser) nil)
               (funcall thunk))
      (setf (lexer-cursor (parser-lexer parser)) cursor
            (parser-lookahead parser) lookahead (parser-remaining parser) remaining
            (parser-replay-p parser) replay))))

(defun variable-binding (parser token)
  (unless (parser-bindings parser)
    (problem 'unbound-template-variable :variable-outside-template (token-position token)
             "Variables are only allowed within templates."))
  (or (gethash (token-value token) (parser-bindings parser))
      (problem 'unbound-template-variable :unbound-template-variable (token-position token)
               (format nil "No argument is bound to $~A." (token-value token)))))

(defun argument-problem (token expected)
  (problem 'invalid-template-argument :invalid-template-argument (token-position token)
           (format nil "The bound argument cannot be used as ~A." expected)))

(defun bound-identity (parser token explicit-kind)
  (let ((argument (variable-binding parser token)))
    (case (template-argument-kind argument)
      (:iri (values (or explicit-kind :subject-identifier) (template-argument-value argument)))
      (:topic (when explicit-kind (argument-problem token "an IRI after = or ^"))
              (values :bound-topic (topic-maps.tmdm:canonical-topic (template-argument-topic argument))))
      (otherwise (argument-problem token "a Topic reference")))))

(defun bound-literal (parser token)
  (let ((argument (variable-binding parser token)))
    (case (template-argument-kind argument)
      (:iri (values (template-argument-value argument) (topic-maps.tmdm:iri-datatype)))
      (:literal (values (template-argument-value argument) (template-argument-datatype argument)))
      (otherwise (argument-problem token "a literal")))))

(defun bound-name (parser token)
  (let ((argument (variable-binding parser token)))
    (unless (template-argument-plain-string-p argument) (argument-problem token "a quoted name string"))
    (template-argument-value argument)))

(defun read-call-argument (parser map)
  (let ((token (look parser)))
    (case (token-kind token)
      (:variable (consume parser) (variable-binding parser token))
      ((:iri :qname)
       ;; Resolve/validate the locator once in the caller, without interning a
       ;; Topic. In particular an unused QName still needs a bound prefix, and
       ;; a resolved prefix must not be percent-decoded again at variable use.
       (make-template-argument :kind :iri :token token :value (literal-iri-reference parser)))
      ((:string :integer :decimal :date :datetime :ctm-integer)
       (let ((plain (and (eq :string (token-kind token)) (not (next-punctuation-p parser #\^)))))
         (multiple-value-bind (value datatype) (read-literal parser)
           (make-template-argument :kind :literal :token token :value value :datatype datatype :plain-string-p plain))))
      (otherwise
       (unless (topic-reference-start-p token)
         (problem 'invalid-template-argument :expected-template-argument (token-position token) "Expected a Topic reference or literal argument."))
       ;; Evaluate Wildcards/Embedded Topics ONCE in the caller's environment.
       (make-template-argument :kind :topic :token token :topic (topic-reference parser map))))))

(defun read-template-invocation (parser map &optional owner)
  (let* ((name (consume parser)) (arguments nil))
    (consume parser) ; '(' recognized by dispatch
    (unless (punctuation-p parser #\))
      (loop (push (read-call-argument parser map) arguments)
            (unless (punctuation-p parser #\,) (return))
            (consume parser)))
    (unless (punctuation-p parser #\))
      (problem 'template-error :missing-template-close (token-position (look parser)) "Expected ')' after template arguments."))
    (consume parser)
    (setf arguments (nreverse arguments))
    (when owner (push (make-template-argument :kind :topic :token name :topic (topic-maps.tmdm:canonical-topic owner)) arguments))
    (let* ((key (list (token-value name) (length arguments)))
           (definition (gethash key (parser-templates parser))))
      (unless definition
        (let ((same-name (loop for key being the hash-keys of (parser-templates parser)
                              thereis (string= (first key) (token-value name)))))
          (problem (if same-name 'template-arity-error 'undefined-template)
                   (if same-name :template-arity :undefined-template) (token-position name)
                   (format nil "No template ~A/~D is defined at this invocation." (first key) (second key)))))
      (when (>= (length *template-context*) *template-depth-limit*)
        (problem 'ctm-unsupported :template-depth-limit (token-position name)
                 "The configured Template expansion depth limit was reached."))
      (let ((bindings (make-hash-table :test #'equal))
            (old-bindings (parser-bindings parser)) (old-wildcards (parser-wildcards parser))
            (*template-context* (cons (list :name (template-definition-name definition)
                                           :definition-position (template-definition-position definition)
                                           :invocation-position (token-position name)
                                           :definition-source (template-definition-source-name definition)
                                           :definition-document-iri (template-definition-document-iri definition)
                                           :invocation-source *source-name*
                                           :invocation-document-iri (parser-document-iri parser)) *template-context*)))
        (loop for parameter in (template-definition-parameters definition) for argument in arguments
              do (setf (gethash parameter bindings) argument))
        (unwind-protect
            (progn
              (setf (parser-bindings parser) bindings (parser-wildcards parser) (make-hash-table :test #'equal))
              ;; The parser's Document IRI, Prefixes, registry and Counter stay
              ;; in the caller. Only lexical source coordinates switch to the
              ;; definition; nested invocations preserve both source frames.
              (let ((*source-name* (template-definition-source-name definition))
                    (*source-text* (template-definition-source-text definition)))
                (dolist (statement (template-definition-body definition))
                  (call-with-tokens parser (ctm-statement-tokens statement)
                    (lambda () (read-statement parser map))))))
          (setf (parser-bindings parser) old-bindings (parser-wildcards parser) old-wildcards))))))

(defun read-statement (parser map)
  (if (global-invocation-p parser)
      (read-template-invocation parser map)
      (let* ((embedded (punctuation-p parser #\[)) (topic (topic-reference parser map)))
        (if (punctuation-p parser #\()
            (read-association parser map topic)
            (if embedded
                (problem 'ctm-rejection :embedded-topic-at-top-level (token-position (look parser))
                         "An Embedded Topic at top level must be an Association Type, not a standalone declaration.")
                (read-topic-tail parser map topic #\.))))))

;;; Grammar-only traversal. It consumes the SAME lexical tokens, storing checked
;;; statement boundaries. No TMDM constructors, locator interning or wildcard
;;; execution occur here. Argument meaning is checked by the ordinary readers
;;; when the stored statement is invoked, not by textual substitution.
(defun syntax-problem (parser message &optional (code :invalid-template-body))
  (problem 'invalid-template-body code (token-position (look parser)) message))
(defun syntax-expect (parser char)
  (unless (punctuation-p parser char)
    (syntax-problem parser (format nil "Expected '~A' in template syntax." char)))
  (consume parser))
(defun syntax-variable (parser parameters)
  (let ((token (consume parser)))
    (unless (member (token-value token) parameters :test #'string=)
      (problem 'unbound-template-variable :unbound-template-variable (token-position token)
               "A template variable has no corresponding parameter."))))
(defun syntax-reference (parser parameters &optional iri-only)
  (let ((token (look parser)))
    (cond ((eq :variable (token-kind token)) (syntax-variable parser parameters))
          ((member (token-kind token) '(:iri :qname)) (consume parser))
          (iri-only (syntax-problem parser "Expected an IRI reference."))
          ((and (eq :identifier (token-kind token))
                (not (member (token-value token) '("def" "end" "isa" "ako") :test #'string=))) (consume parser))
          ((eq :wildcard (token-kind token)) (consume parser))
          ((or (punctuation-p parser #\=) (punctuation-p parser #\^))
           (consume parser) (syntax-reference parser parameters t))
          ((punctuation-p parser #\[)
           (consume parser) (syntax-tail parser parameters #\] t))
          (t (syntax-problem parser "Expected a Topic reference in template syntax.")))))
(defun syntax-literal (parser parameters)
  (let ((token (look parser)))
    (cond ((eq :variable (token-kind token)) (syntax-variable parser parameters))
          ((member (token-kind token) '(:iri :qname :integer :decimal :date :datetime)) (consume parser))
          ((eq :ctm-integer (token-kind token)) (consume parser))
          ((eq :string (token-kind token))
           (consume parser)
           (when (punctuation-p parser #\^)
             (let ((caret (consume parser)))
               (unless (and (punctuation-p parser #\^) (= (token-position (look parser)) (1+ (token-position caret))))
                 (syntax-problem parser "Expected contiguous '^^'." :invalid-datatype-marker))
               (consume parser)
               (when (eq :variable (token-kind (look parser)))
                 (syntax-problem parser "A datatype qualifier cannot contain a variable." :variable-datatype))
               (unless (member (token-kind (look parser)) '(:iri :qname))
                 (syntax-problem parser "A datatype requires an IRI reference."))
               (consume parser))))
          (t (syntax-problem parser "Expected a literal in template syntax.")))))
(defun syntax-scope (parser parameters)
  (when (punctuation-p parser #\@)
    (consume parser)
    (loop (syntax-reference parser parameters)
          (unless (punctuation-p parser #\,) (return)) (consume parser))))
(defun syntax-reifier (parser parameters)
  (when (punctuation-p parser #\~) (consume parser) (syntax-reference parser parameters)))
(defun syntax-name (parser parameters)
  (consume parser) ; '-'
  (unless (or (eq :string (token-kind (look parser)))
              (and (eq :variable (token-kind (look parser))) (not (next-punctuation-p parser #\:))))
    (syntax-reference parser parameters) (syntax-expect parser #\:))
  (case (token-kind (look parser))
    (:variable (syntax-variable parser parameters))
    (:string (consume parser))
    (otherwise (syntax-problem parser "Expected a string Name value.")))
  (syntax-scope parser parameters) (syntax-reifier parser parameters)
  (loop while (punctuation-p parser #\() do
    (consume parser) (syntax-literal parser parameters)
    (unless (punctuation-p parser #\@) (syntax-problem parser "A Variant requires explicit Scope." :expected-variant-scope))
    (syntax-scope parser parameters) (syntax-reifier parser parameters) (syntax-expect parser #\))))
(defun syntax-invocation (parser parameters)
  (consume parser) (syntax-expect parser #\()
  (unless (punctuation-p parser #\))
    (loop
      (if (member (token-kind (look parser)) '(:string :integer :decimal :date :datetime :ctm-integer))
          (syntax-literal parser parameters) (syntax-reference parser parameters))
      (unless (punctuation-p parser #\,) (return)) (consume parser)))
  (syntax-expect parser #\)))
(defun syntax-tail (parser parameters terminator &optional required)
  (let ((seen nil) (separator nil))
    (loop
      (when (punctuation-p parser terminator)
        (when (and required (not seen)) (syntax-problem parser "An Embedded Topic requires a Tail."))
        (consume parser) (return))
      (when separator (syntax-expect parser #\;)
        (when (punctuation-p parser terminator) (consume parser) (return)))
      (cond
        ((punctuation-p parser #\-) (syntax-name parser parameters))
        ((relationship-keyword-p (look parser)) (consume parser) (syntax-reference parser parameters))
        ((tail-invocation-p parser) (syntax-invocation parser parameters))
        (t
         (let ((start (look parser)))
           (syntax-reference parser parameters)
           (if (punctuation-p parser #\:)
               (progn (consume parser) (syntax-literal parser parameters)
                      (syntax-scope parser parameters) (syntax-reifier parser parameters))
               (when (or (member (token-kind start) '(:variable :identifier :wildcard))
                         (and (eq :punctuation (token-kind start)) (eql #\[ (token-value start))))
                 (syntax-problem parser "Unmarked variable identities in Topic Tails remain outside the supported grammar." :template-identity-tail))))))
      (setf seen t separator t))))
(defun syntax-statement (parser parameters)
  (if (global-invocation-p parser)
      (progn (syntax-invocation parser parameters) :invocation)
      (let ((embedded (punctuation-p parser #\[)))
        (syntax-reference parser parameters)
        (if (punctuation-p parser #\()
            (progn
              (consume parser)
              (loop
                (syntax-reference parser parameters)
                (let* ((end (lexer-cursor (parser-lexer parser))) (colon (look parser)))
                  (syntax-expect parser #\:)
                  (unless (or (> (token-position colon) end)
                              (> (token-position (look parser)) (1+ (token-position colon))))
                    (syntax-problem parser "A Role separator requires layout." :role-separator-whitespace)))
                (syntax-reference parser parameters) (syntax-reifier parser parameters)
                (unless (punctuation-p parser #\,) (return)) (consume parser))
              (syntax-expect parser #\)) (syntax-scope parser parameters) (syntax-reifier parser parameters)
              :association)
            (progn
              (when embedded (syntax-problem parser "Standalone Embedded Topics are not template-body statements."))
              (syntax-tail parser parameters #\.) :topic)))))
(defun read-template-definition (parser)
  (let* ((start (consume parser)) (name (consume parser)) (parameters nil) (body nil))
    (unless (and (eq :identifier (token-kind name))
                 (not (member (token-value name) '("def" "end") :test #'string=)))
      (syntax-problem parser "A template name must be an identifier."))
    (syntax-expect parser #\()
    (unless (punctuation-p parser #\))
      (loop
        (unless (eq :variable (token-kind (look parser))) (syntax-problem parser "Expected a parameter variable."))
        (let ((token (consume parser)))
          (when (member (token-value token) parameters :test #'string=)
            (syntax-problem parser "Duplicate parameter names cannot be bound positionally." :duplicate-template-parameter))
          (push (token-value token) parameters))
        (unless (punctuation-p parser #\,) (return)) (consume parser)))
    (syntax-expect parser #\))
    (setf parameters (nreverse parameters))
    (let ((key (list (token-value name) (length parameters))))
      (when (gethash key (parser-templates parser))
        (problem 'duplicate-template :duplicate-template (token-position name) "The template name/arity is already defined."))
      (loop until (identifier-p (look parser) "end") do
        (when (or (eq :eof (token-kind (look parser))) (eq :directive (token-kind (look parser)))
                  (identifier-p (look parser) "def") (punctuation-p parser #\~))
          (syntax-problem parser "Expected a Topic, Association or Invocation, followed by 'end'."))
        (let ((position (token-position (look parser))))
          (setf (parser-recording parser) t (parser-recorded parser) nil)
          (unwind-protect
              (let ((kind (syntax-statement parser parameters)))
                (push (make-ctm-statement :kind kind :position position
                        :tokens (nreverse (parser-recorded parser))) body))
            (setf (parser-recording parser) nil (parser-recorded parser) nil))))
      (consume parser)
      (setf (gethash key (parser-templates parser))
            (make-template-definition :name (token-value name) :parameters parameters
              :position (token-position start) :body (nreverse body)
              :source-name *source-name* :source-text *source-text*
              :document-iri (parser-document-iri parser))))))
