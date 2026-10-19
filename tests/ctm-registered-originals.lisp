(defpackage #:topic-maps.registered-original.tests
  (:use #:cl #:topic-maps.tmdm)
  (:export #:run-tests #:write-reports #:candidate-groups
           #:run-negative-tests #:write-negative-reports))
(in-package #:topic-maps.registered-original.tests)

;; One selection of the existing discovered Case Records, not another registry.
(defparameter *groups*
  '((:comments "comment-ml" "comment-ml-nested" "comment-ml-nested2" "comment-sl" "comment-sl2"
               "comment-sl3" "comment-sl4" "comment-sl5" "comment-sl6" "empty")
    (:identity "association-qname-iid" "item-identifier-INF" "item-identifier-relative" "qname-date" "qname-digits"
               "rootless-uri" "subject-identifier-dot" "subject-identifier-non-http" "subject-identifier-relative"
               "subject-locator-dot" "subject-locator-relative" "topic-identifier-INF" "topic-identifier-unicode")
    (:occurrences "occurrence-decimal-dot-neg2" "occurrence-decimal-dot-pos" "occurrence-decimal-leading-zeros2"
                  "occurrence-duplicate-string" "occurrence-duplicate-uri" "occurrence-qname-value"
                  "occurrence-string-multiline" "occurrence-string-multiline2" "occurrence-uri-semicolon")
    (:prefixes "prefix-multiline2" "prefix-multiline3" "prefix-multiline4" "prefix-with-qm")
    (:escapes "string-escape" "string-escape2" "unicode-escape-u4" "unicode-escape-u6")))
(defun candidate-groups () (copy-tree *groups*))
(defvar *checks* nil)
(defvar *rows* nil)
(defvar *results* nil)
(defvar *entry-statuses* nil)
(defun check (label truth)
  (unless truth (error "Registered original check failed: ~A" label))
  (push label *checks*))
(defun fields (&rest args) (apply #'topic-maps.test-foundation::fields args))
(defun binary (path) (topic-maps.ctm.tests::binary-file path))
(defun same-set (a b &optional (test #'equal))
  (and (= (length a) (length b)) (subsetp a b :test test) (subsetp b a :test test)))
(defun local (map doc name)
  (find-if (lambda (topic) (member (concatenate 'string doc "#" name) (topic-item-identifiers topic) :test #'equal))
           (topic-map-topics map)))
(defun single-identity (map kind value)
  (let ((topics (topic-map-topics map)))
    (and (= 1 (length topics)) (null (topic-map-associations map))
         (let ((topic (first topics)))
           (and (equal (topic-item-identifiers topic) (when (eq kind :ii) (list value)))
                (equal (topic-subject-identifiers topic) (when (eq kind :si) (list value)))
                (equal (topic-subject-locators topic) (when (eq kind :sl) (list value)))
                (null (topic-names topic)) (null (topic-occurrences topic)))))))
(defun plain-locals-p (map doc names)
  (and (= (length names) (length (topic-map-topics map))) (null (topic-map-associations map))
       (every (lambda (name) (let ((topic (local map doc name)))
         (and topic (equal (list (concatenate 'string doc "#" name)) (topic-item-identifiers topic))
              (null (topic-subject-identifiers topic)) (null (topic-subject-locators topic))
              (null (topic-names topic)) (null (topic-occurrences topic))))) names)))
(defun semantic-witness (name group map doc)
  "Independent concrete object properties, in addition to exact XML equality."
  (ecase group
    (:comments
     (plain-locals-p map doc
       (cond ((member name '("empty" "comment-sl3") :test #'equal) nil)
             ((member name '("comment-ml" "comment-ml-nested" "comment-ml-nested2" "comment-sl2") :test #'equal) '("topic1" "topic3"))
             ((equal name "comment-sl6") '("topic" "topic2")) (t '("topic")))))
    (:identity
     (if (equal name "association-qname-iid")
         (let* ((base "http://www.example.org/my-ctm#")
                (a (first (topic-map-associations map))) (roles (when a (association-roles a)))
                (topics (topic-map-topics map)))
           (flet ((named (suffix) (find-if (lambda (topic) (equal (list (concatenate 'string base suffix)) (topic-item-identifiers topic))) topics)))
             (and (= 3 (length topics)) (= 1 (length (topic-map-associations map))) (= 1 (length roles))
                  (every (lambda (topic) (and (null (topic-subject-identifiers topic)) (null (topic-subject-locators topic)))) topics)
                  (eq (named "assoctype") (association-type a)) (eq (named "roletype") (association-role-type (first roles)))
                  (eq (named "topic") (association-role-player (first roles))) (eq a (association-role-parent (first roles))))))
         (let ((expected (cond
            ((member name '("item-identifier-INF" "topic-identifier-INF") :test #'equal) (list :ii (concatenate 'string doc "#INF")))
            ((equal name "item-identifier-relative") (list :ii (concatenate 'string doc "#topic")))
            ((equal name "topic-identifier-unicode") (list :ii (concatenate 'string doc "#ü͡ØΨ㬟͡")))
            ((equal name "qname-date") '(:si "http://psi.semagia.com/iso8601/1947-01-08"))
            ((equal name "qname-digits") '(:si "http://psi.example.org/007"))
            ((equal name "rootless-uri") '(:si "urn:uuid:d84e2777-8928-4bd4-a3e4-8ca835f92304"))
            ((equal name "subject-identifier-dot") '(:si "http://psi.example.org/fake"))
            ((equal name "subject-identifier-non-http") '(:si "ftp://psi.example.org/photo.jpg"))
            ((equal name "subject-identifier-relative") (list :si (concatenate 'string doc "#fake")))
            ((equal name "subject-locator-dot") '(:sl "http://www.example.org/"))
            ((equal name "subject-locator-relative") (list :sl (concatenate 'string doc "#fake"))))))
           (and expected (single-identity map (first expected) (second expected))))))
    (:prefixes
     (if (equal name "prefix-with-qm")
         (single-identity map :sl "http://www.youtube.com/watch?v=fd85SK7dESU")
         (single-identity map :si "http://psi.example.org/fake")))
    (:occurrences
     (let* ((owner (local map doc (if (equal name "occurrence-qname-value") "john" "topic")))
            (type (local map doc (if (equal name "occurrence-qname-value") "wikipedia" "occtype")))
            (items (when owner (topic-occurrences owner))) (o (first items))
            (expected (cond
              ((equal name "occurrence-decimal-dot-neg2") (list "-0.03" (decimal-datatype)))
              ((equal name "occurrence-decimal-dot-pos") (list "0.3" (decimal-datatype)))
              ((equal name "occurrence-decimal-leading-zeros2") (list "2.3" (decimal-datatype)))
              ((equal name "occurrence-duplicate-string") (list "Occurrence" (string-datatype)))
              ((equal name "occurrence-duplicate-uri") (list "http://www.example.org/resource" (iri-datatype)))
              ((equal name "occurrence-qname-value") (list "http://en.wikipedia.org/wiki/John_Lennon" (iri-datatype)))
              ((equal name "occurrence-string-multiline") (list (format nil "Occurrence~%Value") (string-datatype)))
              ((equal name "occurrence-string-multiline2") (list (format nil "Occurrence~C~CValue" #\Return #\Newline) (string-datatype)))
              ((equal name "occurrence-uri-semicolon") (list "http://www.example.org/;something;;somewhere" (iri-datatype))))))
       (and owner type (= 2 (length (topic-map-topics map))) (= 1 (length items)) (null (topic-map-associations map))
            (every (lambda (topic) (null (topic-names topic))) (topic-map-topics map))
            (eq owner (occurrence-parent o)) (eq type (occurrence-type o))
            (equal expected (list (occurrence-value o) (occurrence-datatype o)))
            (null (occurrence-scope o)) (null (item-identifiers o)))))
    (:escapes
     (let* ((owner (local map doc (cond ((equal name "string-escape") "topic") ((equal name "string-escape2") "A00") (t "zztop"))))
            (names (when owner (topic-names owner)))
            (type (find-if (lambda (topic) (member (default-name-type-identifier) (topic-subject-identifiers topic) :test #'equal)) (topic-map-topics map)))
            (expected (cond ((equal name "string-escape") (list "\\" "Quote (\") character" (format nil "Some whitespace ~C~C~C" #\Newline #\Return #\Tab)))
                            ((equal name "string-escape2") '("A00")) (t '("ZZ Top")))))
       (and owner type (= 2 (length (topic-map-topics map))) (null (topic-map-associations map))
            (same-set expected (mapcar #'topic-name-value names))
            (every (lambda (n) (and (eq owner (topic-name-parent n)) (eq type (topic-name-type n))
                                    (null (topic-name-scope n)) (null (topic-name-variants n)))) names))))))

(defun identity-fields (case)
  (list (topic-maps.test-foundation:test-case-id case) (topic-maps.test-foundation:test-case-category case)
        (topic-maps.test-foundation:test-case-source-pathname case) (topic-maps.test-foundation:test-case-document-iri case)
        (topic-maps.test-foundation:test-case-expected-outcome case) (topic-maps.test-foundation:test-case-expected-baseline case)
        (topic-maps.test-foundation:test-case-clauses case)))
(defun exercise-case (case group)
  "Record only an actual comparison. Rejections/errors never become empty Maps."
  (let* ((id (topic-maps.test-foundation:test-case-id case)) (doc (topic-maps.test-foundation:test-case-document-iri case))
         (name (pathname-name (topic-maps.test-foundation:test-case-source-pathname case)))
         (identity (copy-tree (identity-fields case))) (source (binary (topic-maps.test-foundation:test-case-source-pathname case)))
         (evidence nil) (result nil))
    (handler-case
        (let* ((map (topic-maps.ctm:deserialize-file (topic-maps.test-foundation:test-case-source-pathname case) :document-iri doc :source-name id))
               (held (topic-maps.import.tests::handles map)) (before (topic-maps.import.tests::state map held))
               (actual (topic-maps.cxtm:canonicalize-octets map :base-locator doc))
               (expected (binary (topic-maps.test-foundation:test-case-expected-baseline case))) (different (mismatch actual expected)))
          (check (concatenate 'string id ":actual-TMDM-properties-and-EQ-references") (semantic-witness name group map doc))
          (check (concatenate 'string id ":canonicalization-preserves-raw-objects-and-handles")
            (equal before (topic-maps.import.tests::state map held)))
          (check (concatenate 'string id ":deterministic-canonical-octets")
            (equalp actual (topic-maps.cxtm:canonicalize-octets map :base-locator doc)))
          (check (concatenate 'string id ":unmodified-source-bytes") (equalp source (binary (topic-maps.test-foundation:test-case-source-pathname case))))
          (topic-maps.test-foundation:record-result case (if different :cxtm-mismatch :cxtm-match)
            :diagnostics (when different (list (format nil "First different byte ~D; actual ~D bytes, expected ~D bytes." different (length actual) (length expected)))))
          (setf evidence (fields "actualBytes" (length actual) "expectedBytes" (length expected)
                                "firstDifferentByte" different "model" (topic-maps.template.tests::observe map))
                result (list :id id :base doc :actual (topic-maps.ctm::decode-utf8 actual)
                             :expected (topic-maps.ctm::decode-utf8 expected) :match (null different) :bytes (length actual))))
      ((or topic-maps.ctm:ctm-unsupported topic-maps.cxtm:cxtm-unsupported) (condition)
        (topic-maps.test-foundation:record-result case :unsupported :diagnostics (list (format nil "~A: ~A" (type-of condition) condition))))
      (error (condition)
        (topic-maps.test-foundation:record-result case :execution-error :diagnostics (list (format nil "~A: ~A" (type-of condition) condition)))))
    (check (concatenate 'string id ":same-contract-identity-after-execution") (equal identity (identity-fields case)))
    (values
      (fields "id" id "group" (string-downcase (symbol-name group))
              "sourcePathname" id "documentIRI" doc
              "baseline" (format nil "ctm/baseline/~A.ctm.cxtm" name)
              "status" (topic-maps.test-foundation::word (topic-maps.test-foundation:test-case-status case))
              "actualOutcome" (topic-maps.test-foundation::word (topic-maps.test-foundation:test-case-actual-outcome case))
              "diagnostics" (coerce (topic-maps.test-foundation:test-case-diagnostics case) 'vector)
              "sourceBytes" (length source) "comparison" evidence)
      result)))


(defun case-state (case)
  (copy-tree
    (list (identity-fields case)
          (topic-maps.test-foundation:test-case-status case)
          (topic-maps.test-foundation:test-case-actual-outcome case)
          (topic-maps.test-foundation:test-case-diagnostics case))))

(defun run-tests ()
  ;; Use the same Case Records populated by the retained suites. A direct ASDF
  ;; invocation may initialize those suites, but must never replace their corpus.
  (unless topic-maps.ctm.tests::*cxtm-corpus*
    (topic-maps.include.tests:run-tests))
  (setf *checks* nil *rows* nil *results* nil)
  (let* ((corpus topic-maps.ctm.tests::*cxtm-corpus*)
         (root (topic-maps.test-foundation:corpus-root corpus))
         (ids (loop for (group . names) in *groups*
                    append (mapcar (lambda (name) (format nil "ctm/in/~A.ctm" name)) names)))
         (cases (topic-maps.test-foundation:corpus-cases corpus))
         (previous (mapcar (lambda (case) (cons case (case-state case))) cases))
         (old-results (copy-tree topic-maps.ctm.tests::*cxtm-results*))
         (base (format nil "https://ctm-tests.example.invalid/~A/"
                       (getf (topic-maps.test-foundation:corpus-metadata corpus) :commit))))
    (setf *entry-statuses*
          (copy-list (getf (topic-maps.test-foundation:summarize-corpus corpus) :statuses)))
    (check "registration:forty-distinct-selected-originals"
      (and (= 40 (length ids)) (= 40 (length (remove-duplicates ids :test #'equal)))
           (equal '(10 13 9 4 4) (mapcar (lambda (group) (length (cdr group))) *groups*))))
    (check "registration:existing-corpus-correspondence"
      (getf (topic-maps.test-foundation:verify-correspondence corpus) :ok))
    (dolist (group *groups*)
      (dolist (name (cdr group))
        (let* ((id (format nil "ctm/in/~A.ctm" name))
               (selected (topic-maps.test-foundation:select-cases corpus :id id))
               (case (first selected)))
          (check (concatenate 'string id ":unique-existing-positive-contract")
            (and (= 1 (length selected)) (member case cases :test #'eq)
                 (eq :valid (topic-maps.test-foundation:test-case-category case))
                 (eq :cxtm-equal (topic-maps.test-foundation:test-case-expected-outcome case))
                 (eq :not-run (topic-maps.test-foundation:test-case-status case))
                 (null (topic-maps.test-foundation:test-case-actual-outcome case))))
          (check (concatenate 'string id ":pinned-source-baseline-and-document-IRI")
            (and (equal (truename (merge-pathnames id root))
                        (truename (topic-maps.test-foundation:test-case-source-pathname case)))
                 (equal (truename (merge-pathnames (format nil "ctm/baseline/~A.ctm.cxtm" name) root))
                        (truename (topic-maps.test-foundation:test-case-expected-baseline case)))
                 (equal (concatenate 'string base id)
                        (topic-maps.test-foundation:test-case-document-iri case))))
          (multiple-value-bind (row result) (exercise-case case (car group))
            (push row *rows*)
            (when result (push result *results*)))
          (format t "~&REGISTERED-ORIGINAL ~A: ~A~{ ~A~}~%" id
            (topic-maps.test-foundation:test-case-status case)
            (topic-maps.test-foundation:test-case-diagnostics case)))))
    (setf *rows* (nreverse *rows*) *results* (nreverse *results*))
    (check "registration:forty-actual-byte-comparisons-pass"
      (and (= 40 (length *rows*) (length *results*))
           (every (lambda (result) (getf result :match)) *results*)
           (every (lambda (id) (eq :pass (topic-maps.test-foundation:test-case-status
                                (first (topic-maps.test-foundation:select-cases corpus :id id))))) ids)))
    (check "registration:all-previous-case-records-and-observations-preserved"
      (and (eq corpus topic-maps.ctm.tests::*cxtm-corpus*)
           (equal cases (topic-maps.test-foundation:corpus-cases corpus))
           (every (lambda (entry)
                    (if (member (topic-maps.test-foundation:test-case-id (car entry)) ids :test #'equal)
                        (equal (first (cdr entry)) (identity-fields (car entry)))
                        (equal (cdr entry) (case-state (car entry))))) previous)
           (equal old-results topic-maps.ctm.tests::*cxtm-results*)))
    (let ((after (getf (topic-maps.test-foundation:summarize-corpus corpus) :statuses)))
      (check "registration:only-forty-NOT-RUN-to-PASS-transitions"
        (and (= (+ 40 (getf *entry-statuses* :pass)) (getf after :pass))
             (= (- (getf *entry-statuses* :not-run) 40) (getf after :not-run))
             (= (getf *entry-statuses* :fail) (getf after :fail))
             (= (getf *entry-statuses* :unsupported) (getf after :unsupported)))))
    (setf topic-maps.ctm.tests::*cxtm-results*
          (append topic-maps.ctm.tests::*cxtm-results* *results*)))
  (check "registration:unique-check-names"
    (= (length *checks*) (length (remove-duplicates *checks* :test #'equal))))
  (setf *checks* (nreverse *checks*))
  (format t "~&REGISTERED-ORIGINALS-PASS: ~D checks; forty actual byte-exact original contracts~%" (length *checks*))
  t)

(defun write-reports (prefix)
  (with-open-file (out (concatenate 'string prefix ".registration.json")
                       :direction :output :if-exists :supersede :if-does-not-exist :create)
    (topic-maps.test-foundation::emit-json-value
      (fields "kind" "ctm-registered-original-execution"
              "passed" (length *checks*) "failed" 0
              "entryStatuses" (topic-maps.test-foundation::counts-object *entry-statuses*)
              "checks" (coerce *checks* 'vector) "cases" (coerce *rows* 'vector)) out)
    (terpri out))
  (topic-maps.ctm.tests::write-cxtm-report
    (concatenate 'string prefix ".validation.json")
    (concatenate 'string prefix ".cxtm.json")
    :additional-checks *checks*
    :scope "Slice 20A: forty newly executed original CTM comparisons; prior Case Records, observations and four known DateTime/Include FAILs retained. Full retained regression and XTM integration are evidenced separately."))


;;; Slice 20B: a selection of seven existing negative Case Records.
;;; Normative review: docs/slice-20b-negative-registration.md. No reader changes.
(defparameter *negative-contracts*
  '(("occurrence-double-positive-infinity" :expected-occurrence-value 15 2 10
      ("CTM 3.4.1 [28]-[34]" "CTM 3.10 [56]")
      "Bare INF is neither a CTM number nor another literal alternative.")
    ("occurrence-double-negative-infinity" :expected-occurrence-value 15 2 10
      ("CTM 3.4.1 [28]-[34]" "CTM 3.10 [56]")
      "Bare -INF is neither a CTM number nor another literal alternative.")
    ("qname-hyphen" :unexpected-token 38 3 3
      ("CTM 3.3.4 [9]-[11]" "CTM 3.3.6 [14]-[16]")
      "A QName local part cannot start with a hyphen.")
    ("string-unbalanced" :unterminated-string 8 1 9
      ("CTM 3.4.1 [37]-[40]" "CTM 3.4.2 [41]")
      "The escaped quote is content; the quoted string lacks a closing delimiter.")
    ("string-unicode" :invalid-unicode-escape 11 1 12
      ("CTM 3.4.2 [42]")
      "Uppercase U requires six hexadecimal digits; the closing quote follows four.")
    ("string-unicode2" :invalid-unicode-escape 15 1 16
      ("CTM 3.4.2 [42]-[43] and hexadecimal decoding prose")
      "G cannot be decoded as a hexadecimal digit; see the printed-class qualification.")
    ("topic-id-illegal" :unexpected-character 0 1 1
      ("CTM 3.3.6 [14]-[16]")
      "U+0361 is allowed inside an identifier, but not as its first character.")))
(defvar *negative-checks* nil)
(defvar *negative-rows* nil)
(defvar *negative-entry-statuses* nil)

(defun captured-read (thunk)
  (handler-case (values (funcall thunk) nil)
    (error (condition) (values nil condition))))

(defun condition-data (condition)
  (when condition
    (let ((ctm-p (typep condition 'topic-maps.ctm:ctm-error)))
      (fields "condition" (string (type-of condition)) "message" (princ-to-string condition)
              "code" (when ctm-p (topic-maps.test-foundation::word (topic-maps.ctm:error-code condition)))
              "position" (when ctm-p (topic-maps.ctm:error-position condition))
              "line" (when ctm-p (topic-maps.ctm:error-line condition))
              "column" (when ctm-p (topic-maps.ctm:error-column condition))
              "positionUnit" (when ctm-p (topic-maps.test-foundation::word (topic-maps.ctm:error-position-unit condition)))
              "source" (when ctm-p (topic-maps.ctm:error-source condition))
              "cause" (when (and ctm-p (topic-maps.ctm:error-cause condition))
                        (princ-to-string (topic-maps.ctm:error-cause condition)))
              "context" (when (and ctm-p (topic-maps.ctm:error-context condition))
                          (princ-to-string (topic-maps.ctm:error-context condition)))))))

(defun condition-signature (condition)
  (when (typep condition 'topic-maps.ctm:ctm-error)
    (list (type-of condition) (topic-maps.ctm:error-code condition)
          (topic-maps.ctm:error-position condition) (topic-maps.ctm:error-line condition)
          (topic-maps.ctm:error-column condition) (topic-maps.ctm:error-position-unit condition)
          (topic-maps.ctm:error-source condition) (topic-maps.ctm:error-cause condition)
          (topic-maps.ctm:error-context condition) (princ-to-string condition))))

(defun intended-rejection-p (condition spec id)
  ;; Exact syntax class: unsupported/resource/wrapped model errors never qualify.
  (and condition (eq (type-of condition) 'topic-maps.ctm:ctm-rejection)
       (equal (subseq (condition-signature condition) 1 7)
              (list (second spec) (third spec) (fourth spec) (fifth spec) :character id))
       (null (topic-maps.ctm:error-cause condition))
       (null (topic-maps.ctm:error-context condition))))

(defun replace-fragment (text old new)
  (let ((position (search old text)))
    (unless position (error "Missing reviewed source fragment ~S." old))
    (concatenate 'string (subseq text 0 position) new (subseq text (+ position (length old))))))

(defun syntax-witness-and-control (name text)
  "Check the offending source spelling; derive a valid in-memory sibling only."
  (cond
    ((equal name "occurrence-double-positive-infinity")
     (values (equal text (format nil "topic~%occtype: INF."))
             (replace-fragment text "INF" "1") :occurrence "1"))
    ((equal name "occurrence-double-negative-infinity")
     (values (equal text (format nil "topic~%occtype: -INF."))
             (replace-fragment text "-INF" "-1") :occurrence "-1"))
    ((equal name "qname-hyphen")
     (values (equal text (format nil "%prefix ex http://psi.example.org/~%~%ex:-issue.~%"))
             (replace-fragment text "ex:-issue" "ex:issue") :qname "http://psi.example.org/issue"))
    ((equal name "string-unbalanced")
     (values (equal text "topic - \"Foo\\\".")
             (concatenate 'string (subseq text 0 (1- (length text))) "\".") :name "Foo\""))
    ((equal name "string-unicode")
     (values (equal text "a - \"\\U0041\".")
             (replace-fragment text "\\U0041" "\\u0041") :name "A"))
    ((equal name "string-unicode2")
     (values (equal text (format nil "unicode - \"\\U00GG00\".~%"))
             (replace-fragment text "\\U00GG00" "\\U000041") :name "A"))
    ((equal name "topic-id-illegal")
     (let ((mark (code-char #x361)))
       (values (and (> (length text) 3) (char= mark (char text 0)) (equal (subseq text 1 3) "a."))
               (concatenate 'string "a" (string mark) (subseq text 2))
               :identifier (concatenate 'string "a" (string mark)))))
    (t (error "Unreviewed negative contract ~A." name))))

(defun control-model-p (map doc name kind value)
  (and map
    (ecase kind
      (:qname (single-identity map :si value))
      (:identifier (plain-locals-p map doc (list value)))
      (:occurrence
       (let* ((owner (local map doc "topic")) (type (local map doc "occtype"))
              (items (when owner (topic-occurrences owner))) (item (first items)))
         (and owner type (= 2 (length (topic-map-topics map))) (= 1 (length items))
              (null (topic-map-associations map))
              (eq owner (occurrence-parent item)) (eq type (occurrence-type item))
              (equal value (occurrence-value item)) (equal (integer-datatype) (occurrence-datatype item)))))
      (:name
       (let* ((owner (local map doc (cond ((equal name "string-unbalanced") "topic")
                                        ((equal name "string-unicode") "a") (t "unicode"))))
              (names (when owner (topic-names owner))) (item (first names))
              (type (find-if (lambda (topic) (member (default-name-type-identifier)
                                (topic-subject-identifiers topic) :test #'equal)) (topic-map-topics map))))
         (and owner type (= 2 (length (topic-map-topics map))) (= 1 (length names))
              (null (topic-map-associations map)) (eq owner (topic-name-parent item))
              (eq type (topic-name-type item)) (equal value (topic-name-value item))))))))

(defun lexical-evidence (text id)
  ;; Explain the generic QName diagnostic from actual tokens, not its label alone.
  (let ((topic-maps.ctm::*source-text* text) (topic-maps.ctm::*source-name* id)
        (lexer (topic-maps.ctm::make-lexer text)) (tokens nil) (failure nil))
    (handler-case
      (loop for token = (topic-maps.ctm::next-token lexer) do
        (push (list (topic-maps.ctm::token-kind token) (topic-maps.ctm::token-value token)
                    (topic-maps.ctm::token-position token)) tokens)
        until (eq :eof (topic-maps.ctm::token-kind token)))
      (error (condition) (setf failure condition)))
    (values (nreverse tokens) failure)))

(defun exercise-negative-case (case spec)
  (let* ((id (topic-maps.test-foundation:test-case-id case))
         (doc (topic-maps.test-foundation:test-case-document-iri case))
         (name (first spec)) (path (topic-maps.test-foundation:test-case-source-pathname case))
         (source (binary path)) (text (topic-maps.ctm::decode-utf8 source))
         (before (case-state case)))
    (multiple-value-bind (source-witness control-text control-kind control-value)
        (syntax-witness-and-control name text)
      (multiple-value-bind (map condition)
          (captured-read (lambda () (topic-maps.ctm:deserialize-file path :document-iri doc :source-name id)))
        (multiple-value-bind (repeat-map repeat-condition)
            (captured-read (lambda () (topic-maps.ctm:deserialize-file path :document-iri doc :source-name id)))
          (multiple-value-bind (control-map control-condition)
              (captured-read (lambda () (topic-maps.ctm:deserialize-string control-text :document-iri doc :source-name id)))
            (multiple-value-bind (tokens lexical-condition) (lexical-evidence text id)
              (let* ((lexical-witness
                       (if (equal name "qname-hyphen")
                           (and (null lexical-condition)
                                (equal (subseq tokens 3 6)
                                       '((:identifier "ex" 36) (:punctuation #\: 38) (:punctuation #\- 39))))
                           t))
                     (control-ok (and (null control-condition)
                                      (control-model-p control-map doc name control-kind control-value)))
                     (repeat-ok (and (null map) (null repeat-map)
                                     (intended-rejection-p repeat-condition spec id)
                                     (equal (condition-signature condition) (condition-signature repeat-condition))))
                     (qualified (and source-witness lexical-witness control-ok repeat-ok
                                     (intended-rejection-p condition spec id))))
                (check (concatenate 'string id ":immutable-original-and-existing-NOT-RUN-record")
                       (and (equal before (case-state case)) (equalp source (binary path))))
                ;; Observing a different error is evidence, not a conformance PASS.
                (when qualified
                  (topic-maps.test-foundation:record-result case :ctm-rejection
                    :diagnostics (list (princ-to-string condition))))
                (check (concatenate 'string id ":only-reviewed-syntax-rejection-can-be-PASS")
                  (if qualified
                      (and (eq :pass (topic-maps.test-foundation:test-case-status case))
                           (eq :ctm-rejection (topic-maps.test-foundation:test-case-actual-outcome case)))
                      (equal before (case-state case))))
                (format t "~&REGISTERED-NEGATIVE ~A: ~A; ~A~%" id
                  (topic-maps.test-foundation:test-case-status case) (or condition "ACCEPTED"))
                (fields "id" id "sourcePathname" id "documentIRI" doc
                  "status" (topic-maps.test-foundation::word (topic-maps.test-foundation:test-case-status case))
                  "actualOutcome" (topic-maps.test-foundation::word (topic-maps.test-foundation:test-case-actual-outcome case))
                  "condition" (condition-data condition) "repeatCondition" (condition-data repeat-condition)
                  "clauses" (coerce (sixth spec) 'vector) "normativeReason" (seventh spec)
                  "normativeSource" "https://www.isotopicmaps.org/ctm/ctm.html"
                  "qualification" (when (equal name "string-unicode2")
                    "Printed production [43] includes all letters; rejection follows the hexadecimal decoding requirement in 3.4.2 prose, not that character class alone.")
                  "normativeValidated" (if qualified :true :false)
                  "sourceWitness" (if source-witness :true :false)
                  "lexicalWitness" (if lexical-witness :true :false)
                  "reproducibleCondition" (if repeat-ok :true :false)
                  "tokens" (coerce (loop for (kind value position) in tokens collect
                                    (fields "kind" (topic-maps.test-foundation::word kind)
                                            "value" (if (characterp value) (string value) value) "position" position)) 'vector)
                  "lexicalCondition" (condition-data lexical-condition)
                  "control" (fields "inMemoryOnly" :true "source" control-text
                                    "accepted" (if control-ok :true :false) "condition" (condition-data control-condition)
                                    "model" (when control-map (topic-maps.template.tests::observe control-map)))
                  "notRegisteredReason" (unless qualified
                    "Observed condition, syntax witness, reproducibility or accepted control did not establish the intended cause; original record remains NOT-RUN."))))))))))

(defun run-negative-tests ()
  (unless topic-maps.ctm.tests::*cxtm-corpus* (run-tests))
  (let* ((*checks* nil) (corpus topic-maps.ctm.tests::*cxtm-corpus*)
         (cases (topic-maps.test-foundation:corpus-cases corpus))
         (previous (mapcar (lambda (case) (cons case (case-state case))) cases))
         (old-results (copy-tree topic-maps.ctm.tests::*cxtm-results*))
         (root (topic-maps.test-foundation:corpus-root corpus))
         (base (format nil "https://ctm-tests.example.invalid/~A/"
                       (getf (topic-maps.test-foundation:corpus-metadata corpus) :commit)))
         (ids (mapcar (lambda (spec) (format nil "ctm/invalid/~A.ctm" (first spec))) *negative-contracts*)))
    (setf *negative-rows* nil *negative-entry-statuses*
          (copy-list (getf (topic-maps.test-foundation:summarize-corpus corpus) :statuses)))
    (check "negative-registration:seven-distinct-existing-contracts"
      (= 7 (length ids) (length (remove-duplicates ids :test #'equal))))
    (dolist (spec *negative-contracts*)
      (let* ((id (format nil "ctm/invalid/~A.ctm" (first spec)))
             (selected (topic-maps.test-foundation:select-cases corpus :id id)) (case (first selected)))
        (check (concatenate 'string id ":unique-existing-negative-contract-and-document-IRI")
          (and (= 1 (length selected)) (member case cases :test #'eq)
               (eq :invalid (topic-maps.test-foundation:test-case-category case))
               (eq :ctm-rejection (topic-maps.test-foundation:test-case-expected-outcome case))
               (null (topic-maps.test-foundation:test-case-expected-baseline case))
               (eq :not-run (topic-maps.test-foundation:test-case-status case))
               (null (topic-maps.test-foundation:test-case-actual-outcome case))
               (equal (truename (merge-pathnames id root))
                      (truename (topic-maps.test-foundation:test-case-source-pathname case)))
               (equal (concatenate 'string base id) (topic-maps.test-foundation:test-case-document-iri case))))
        (push (exercise-negative-case case spec) *negative-rows*)))
    (check "negative-registration:old-record-identities-and-CXTM-observations-preserved"
      (and (eq corpus topic-maps.ctm.tests::*cxtm-corpus*)
           (equal cases (topic-maps.test-foundation:corpus-cases corpus))
           (equal old-results topic-maps.ctm.tests::*cxtm-results*)
           (every (lambda (entry)
                    (if (member (topic-maps.test-foundation:test-case-id (car entry)) ids :test #'equal)
                        (equal (first (cdr entry)) (identity-fields (car entry)))
                        (equal (cdr entry) (case-state (car entry))))) previous)))
    (let* ((after (getf (topic-maps.test-foundation:summarize-corpus corpus) :statuses))
           (qualified (- (getf after :pass) (getf *negative-entry-statuses* :pass))))
      (check "negative-registration:only-qualified-NOT-RUN-to-PASS-transitions"
        (and (<= 0 qualified 7)
             (= (- (getf *negative-entry-statuses* :not-run) qualified) (getf after :not-run))
             (= (getf *negative-entry-statuses* :fail) (getf after :fail))
             (= (getf *negative-entry-statuses* :unsupported) (getf after :unsupported))))
      (check "negative-registration:unique-check-names"
        (= (length *checks*) (length (remove-duplicates *checks* :test #'equal))))
      (setf *negative-rows* (nreverse *negative-rows*) *negative-checks* (nreverse *checks*))
      (format t "~&REGISTERED-NEGATIVES-PASS: ~D checks; ~D intended original rejections registered; ~D remain NOT-RUN~%"
              (length *negative-checks*) qualified (- 7 qualified))))
  t)

(defun write-negative-reports (prefix)
  (with-open-file (out (concatenate 'string prefix ".negative.json")
                      :direction :output :if-exists :supersede :if-does-not-exist :create)
    (topic-maps.test-foundation::emit-json-value
      (fields "kind" "ctm-negative-original-execution" "passed" (length *negative-checks*) "failed" 0
              "entryStatuses" (topic-maps.test-foundation::counts-object *negative-entry-statuses*)
              "checks" (coerce *negative-checks* 'vector) "cases" (coerce *negative-rows* 'vector)) out)
    (terpri out))
  (topic-maps.ctm.tests::write-cxtm-report
    (concatenate 'string prefix ".validation.json") (concatenate 'string prefix ".cxtm.json")
    :additional-checks *negative-checks*
    :scope "Slice 20B: seven negative originals actually executed; only intended syntax rejections registered. Earlier positive comparisons and four known DateTime/Include FAILs preserved; full retained regression, Slice 20A and XTM evidence separate."))
