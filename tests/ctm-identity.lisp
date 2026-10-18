(in-package #:topic-maps.ctm.tests)

(defvar *checks* nil)
(defvar *last-checks* nil)
(defvar *observations* nil)
(defun observations () *observations*)
(defparameter *positive-ids*
  '("ctm/in/simple.ctm" "ctm/in/subject-identifier.ctm" "ctm/in/subject-locator.ctm"
    "ctm/in/item-identifier.ctm" "ctm/in/name.ctm"))

(defmacro check (label assertion)
  `(progn (unless ,assertion (error "Semantic check failed: ~A" ,label))
          (push ,label *checks*)))

(defun read-text (text &optional (document "https://example.invalid/a/doc.ctm"))
  (deserialize-string text :document-iri document :source-name "independent-fixture"))
(defun first-topic (map) (first (topic-map-topics map)))
(defun rejection (text &optional (document "https://example.invalid/a/doc.ctm"))
  ;; Catch only a real CTM rejection; unsupported and generic errors propagate.
  (handler-case (progn (read-text text document) nil) (ctm-rejection (e) e)))
(defun unsupported-p (text)
  (handler-case (progn (read-text text) nil) (ctm-unsupported () t)))

(defun verify-item-invariants (map)
  (let ((topics (topic-map-topics map)))
    (and
     (every (lambda (topic)
              (and (eq map (topic-parent topic))
                   (or (topic-item-identifiers topic) (topic-subject-identifiers topic)
                       (topic-subject-locators topic))
                   (every (lambda (name)
                            (and (typep name 'topic-maps.tmdm:topic-name)
                                 (eq topic (topic-name-parent name))
                                 (member (topic-name-type name) topics :test #'eq)
                                 (stringp (topic-name-value name))))
                          (topic-names topic)))) topics)
     (= (length topics) (length (remove-duplicates topics :test #'eq))))))

(defun verify-selected-map (id document map)
  (let* ((topics (topic-map-topics map)) (topic (first topics))
         (ii (topic-item-identifiers topic)) (si (topic-subject-identifiers topic))
         (sl (topic-subject-locators topic))
         (named (string= id "ctm/in/name.ctm")))
    (check (concatenate 'string id ":item-invariants") (verify-item-invariants map))
    (check (concatenate 'string id ":topic-count") (= (length topics) (if named 2 1)))
    (cond
      ((or named (string= id "ctm/in/simple.ctm"))
       (check (concatenate 'string id ":local-item-identity")
              (and (equal ii (list (concatenate 'string document "#topic"))) (null si) (null sl))))
      ((string= id "ctm/in/subject-identifier.ctm")
       (check "selected-subject-identifier-only"
              (and (equal si '("http://psi.example.org/fake")) (null ii) (null sl))))
      ((string= id "ctm/in/subject-locator.ctm")
       (check "selected-subject-locator-only"
              (and (equal sl '("http://www.example.org/resource")) (null ii) (null si))))
      ((string= id "ctm/in/item-identifier.ctm")
       (check "selected-explicit-item-identifier-only"
              (and (equal ii '("http://www.example.org/#topic")) (null si) (null sl))))
      (t (error "Unreviewed selected case ~A" id)))
    (if named
        (let* ((names (topic-names topic)) (name (first names)) (type (second topics)))
          (check "selected-name-is-one-information-item" (= 1 (length names)))
          (check "selected-name-value" (string= "Name" (topic-name-value name)))
          (check "selected-name-type-is-the-second-topic" (eq type (topic-name-type name)))
          (check "selected-default-name-type-identification"
                 (and (equal (topic-subject-identifiers type) (list (default-name-type-identifier)))
                      (null (topic-item-identifiers type)) (null (topic-subject-locators type))
                      (null (topic-names type)))))
        (check (concatenate 'string id ":no-unwarranted-name-or-type-topic") (null (topic-names topic))))
    map))

(defun exercise-corpus (&optional (corpus (topic-maps.test-foundation:discover-corpus)))
  "Return original corpus plus separate real semantic observations; no CXTM output."
  (let ((results nil))
    (dolist (id *positive-ids*)
      (let* ((case (first (topic-maps.test-foundation:select-cases corpus :id id)))
             (document (topic-maps.test-foundation:test-case-document-iri case))
             (map (deserialize-file (topic-maps.test-foundation:test-case-source-pathname case)
                                    :document-iri document :source-name id)))
        (verify-selected-map id document map)
        ;; Do not change the imported CXTM equality contract or result status.
        (check (concatenate 'string id ":canonical-contract-remains-not-run")
               (and (eq :cxtm-equal (topic-maps.test-foundation:test-case-expected-outcome case))
                    (eq :not-run (topic-maps.test-foundation:test-case-status case))
                    (null (topic-maps.test-foundation:test-case-actual-outcome case))))
        (push (list :id id :document-iri document :status :pass :topic-map map) results)))
    (let* ((id "ctm/invalid/prefix-undefined.ctm")
           (case (first (topic-maps.test-foundation:select-cases corpus :id id)))
           (condition
             (handler-case
                 (progn (deserialize-file (topic-maps.test-foundation:test-case-source-pathname case)
                                          :document-iri (topic-maps.test-foundation:test-case-document-iri case)
                                          :source-name id)
                        nil)
               (undefined-prefix (e) e))))
      (check "pinned-prefix-rejected-for-correct-reason"
             (and condition (eq :undefined-prefix (error-code condition))))
      (check "pinned-prefix-source-position"
             (and (= 1 (error-position condition)) (= 2 (error-line condition)) (= 1 (error-column condition))))
      (topic-maps.test-foundation:record-result case :ctm-rejection :diagnostics (list (princ-to-string condition)))
      (check "only-pinned-rejection-is-imported-pass"
             (equal (getf (topic-maps.test-foundation:summarize-corpus corpus) :statuses)
                    '(:pass 1 :fail 0 :unsupported 0 :not-run 272))))
    (values corpus (nreverse results))))

(defun run-tests ()
  (let ((*checks* nil))
    (multiple-value-bind (corpus observations) (exercise-corpus)
      (declare (ignore corpus)) (setf *observations* observations))
    (let* ((a (read-text "same." "https://example.invalid/a.ctm"))
           (b (read-text "same." "https://example.invalid/b.ctm")))
      (check "local-identifier-uses-explicit-document"
             (equal (topic-item-identifiers (first-topic a)) '("https://example.invalid/a.ctm#same")))
      (check "different-document-iris-different-item-identities"
             (not (equal (topic-item-identifiers (first-topic a)) (topic-item-identifiers (first-topic b)))))
      (check "local-identifiers-do-not-assert-subject-identity"
             (and (not (eq (first-topic a) (first-topic b)))
                  (null (topic-subject-identifiers (first-topic a))) (null (topic-subject-locators (first-topic b))))))
    (dolist (text '("same. same." "<https://example.invalid/id>. <https://example.invalid/id>."
                    "=<https://example.invalid/id>. =<https://example.invalid/id>."
                    "^<https://example.invalid/id>. ^<https://example.invalid/id>."))
      (check (concatenate 'string "same-document-reference-reuses-topic:" text)
             (= 1 (length (topic-map-topics (read-text text))))))
    (let ((map (read-text "^<https://example.invalid/id>. <https://example.invalid/id>.")))
      (check "tmdm-item-subject-identifier-overlap-reuses-topic" (= 1 (length (topic-map-topics map))))
      (check "overlap-keeps-both-identity-properties"
             (and (equal (topic-item-identifiers (first-topic map)) '("https://example.invalid/id"))
                  (equal (topic-subject-identifiers (first-topic map)) '("https://example.invalid/id"))
                  (null (topic-subject-locators (first-topic map))))))
    (let ((map (read-text "^<https://example.invalid/id>. =<https://example.invalid/id>.")))
      (check "item-identity-does-not-equal-subject-locator" (= 2 (length (topic-map-topics map)))))
    (let ((map (read-text "<https://example.invalid/id>. =<https://example.invalid/id>.")))
      (check "subject-identifier-does-not-equal-subject-locator" (= 2 (length (topic-map-topics map)))))
    (let* ((map (read-text "a - \"One\"; - \"One\". b - \"Two\". a - \"Three\"."))
           (a (first-topic map)) (b (third (topic-map-topics map))))
      (check "one-shared-default-type-no-extra-items" (= 3 (length (topic-map-topics map))))
      (check "equal-unscoped-name-items-coalesce" (= 2 (length (topic-names a))))
      (check "different-name-values-remain-distinct"
             (equal (mapcar #'topic-name-value (topic-names a)) '("One" "Three")))
      (check "name-type-and-parent-object-identity"
             (and (eq (topic-name-type (first (topic-names a))) (topic-name-type (first (topic-names b))))
                  (eq a (topic-name-parent (first (topic-names a)))))))
    (let ((map (read-text "<http://psi.topicmaps.org/iso13250/model/topic-name>. a - \"Name\".")))
      (check "existing-default-type-reused" (= 2 (length (topic-map-topics map))))
      (check "type-is-existing-original-topic"
             (eq (first-topic map) (topic-name-type (first (topic-names (second (topic-map-topics map))))))))
    (let* ((map (read-text "ÄΩ - \"München🙂\".")) (topic (first-topic map)))
      (check "unicode-identifier-preserved" (search "#ÄΩ" (first (topic-item-identifiers topic))))
      (check "unicode-name-preserved" (string= "München🙂" (topic-name-value (first (topic-names topic))))))
    (check "case-sensitive-local-identifiers" (= 2 (length (topic-map-topics (read-text "Topic. topic.")))))
    (check "internal-dots-remain-in-identifiers"
           (search "#one..two" (first (topic-item-identifiers (first-topic (read-text "one..two."))))))
    (check "comment-layout-no-extra-topics"
           (= 1 (length (topic-map-topics (read-text (format nil "# comment~%a. #( nested #( ignored )# )#"))))))
    (check "plain-unwrapped-absolute-iri"
           (equal (topic-subject-identifiers (first-topic (read-text "https://example.invalid/path.")))
                  '("https://example.invalid/path")))
    (check "relative-iri-resolution"
           (equal (topic-subject-identifiers (first-topic (read-text "<../object#s>.")))
                  '("https://example.invalid/object#s")))
    (check "same-document-fragment-resolution"
           (equal (topic-item-identifiers (first-topic (read-text "^<#topic>.")))
                  '("https://example.invalid/a/doc.ctm#topic")))
    (check "percent-utf8-iri-decoding"
           (equal (topic-subject-identifiers (first-topic (read-text "<https://example.invalid/%C3%A4>.")))
                  '("https://example.invalid/ä")))
    (check "absolute-iri-case-preserved"
           (equal (topic-subject-identifiers (first-topic (read-text "<HTTPS://Example.invalid/Case>.")))
                  '("HTTPS://Example.invalid/Case")))
    (check "document-iri-required" (eq :invalid-document-iri (error-code (rejection "a." nil))))
    (check "relative-document-iri-rejected" (eq :invalid-document-iri (error-code (rejection "a." "local.ctm"))))
    (check "fragment-document-iri-rejected"
           (eq :invalid-document-iri (error-code (rejection "a." "https://example.invalid/doc#x"))))
    (check "missing-terminator-rejected" (eq :missing-period (error-code (rejection "a"))))
    (check "missing-tail-separator-rejected" (eq :expected-separator (error-code (rejection "a - \"x\" - \"y\"."))))
    (check "unbalanced-string-rejected" (eq :unterminated-string (error-code (rejection "a - \"oops"))))
    (check "invalid-string-escape-rejected" (eq :invalid-string-escape (error-code (rejection "a - \"\\q\"."))))
    (check "unicode-escapes-decoded"
           (string= "Ä🙂" (topic-name-value (first (topic-names (first-topic (read-text "a - \"\\u00C4\\U01F642\".")))))))
    (let ((condition (rejection (format nil "a.~%  ex:fake."))))
      (check "undefined-prefix-condition-class" (typep condition 'undefined-prefix))
      (check "error-line-column" (and (= 2 (error-line condition)) (= 3 (error-column condition)))))
    (check "identity-feature-boundary:a isa person."
           (let ((map (read-text "a isa person.")))
             (= 1 (length (topic-maps.tmdm:topic-map-associations map)))))
    (dolist (text '("def tpl() a. end" "%include <other.ctm>"
                    "? - \"anonymous\" ~r."  "a - \"\"\"triple\"\"\"."))
      (check (if (search "%include" text) "identity:Include-requires-explicit-resolver"
                 (concatenate 'string "identity-feature-boundary:" text))
             (cond ((search "def " text) (null (topic-map-topics (read-text text))))
                   ((search "%include" text)
                    (handler-case (progn (read-text text) nil)
                      (ctm-unsupported (c) (eq :resource-resolver-required (error-code c)))))
                   ((find #\~ text) (typep (read-text text) 'topic-maps.tmdm:topic-map))
                   (t (unsupported-p text)))))
    (check "scope-on-bare-topic-rejected"
           (eq :unexpected-token (error-code (rejection "a @theme."))))
    (check "scoped-name-now-deserialized"
           (= 1 (length (topic-maps.tmdm:topic-name-scope
                          (first (topic-names (first-topic (read-text "a - \"name\" @theme."))))))))
    (check "association-now-deserialized"
           (= 1 (length (topic-maps.tmdm:topic-map-associations (read-text "relation(role: a)")))))
    (check "empty-document-has-no-accidental-type-topic"
           (null (topic-map-topics (read-text ""))))
    (let ((map (deserialize-file (asdf:system-relative-pathname "topic-maps" "tests/fixtures/ctm/utf8-bom.ctm")
                                 :document-iri "https://example.invalid/unicode.ctm")))
      (check "utf8-file-and-bom-decoded"
             (and (equal (topic-item-identifiers (first-topic map)) '("https://example.invalid/unicode.ctm#Ž"))
                  (string= "🙂" (topic-name-value (first (topic-names (first-topic map))))))))
    (let ((condition (handler-case
                         (deserialize-file (asdf:system-relative-pathname "topic-maps" "tests/fixtures/ctm/invalid-utf8.ctm")
                                           :document-iri "https://example.invalid/invalid.ctm")
                       (ctm-rejection (e) e))))
      (check "malformed-utf8-is-specific-rejection" (eq :invalid-utf8 (error-code condition))))
    (check "file-io-error-not-ctm-rejection"
           (handler-case
               (progn (deserialize-file (asdf:system-relative-pathname "topic-maps" "tests/fixtures/ctm/absent.ctm")
                                        :document-iri "https://example.invalid/absent.ctm") nil)
             (ctm-rejection () nil)
             (file-error () t)))
    (check "typed-name-explicitly-supported" (verify-item-invariants (read-text "a - fullname:\"Name\".")))
    ;; CTM 3.11 requires a string, with or without an explicit type.
    ;; CTM 3.3.1 permits layout between the type separator and that string.
    (dolist (fixture '(("a - ." ctm-rejection :expected-name-value 4)
                       ("a -" ctm-rejection :expected-name-value 3)))
      (destructuring-bind (text class code position) fixture
        (let ((condition (handler-case (progn (read-text text) nil)
                           (ctm-error (e) e))))
          (check (concatenate 'string "name-classification-class:" text)
                 (and condition (eq class (type-of condition))))
          (check (concatenate 'string "name-classification-code:" text)
                 (eq code (error-code condition)))
          (check (concatenate 'string "name-classification-position:" text)
                 (= position (error-position condition)))
          (check (concatenate 'string "name-classification-source:" text)
                 (and (= 1 (error-line condition))
                      (= (1+ position) (error-column condition))
                      (eq :character (topic-maps.ctm:error-position-unit condition))
                      (string= "independent-fixture" (topic-maps.ctm:error-source condition))))
          (check (concatenate 'string "name-classification-diagnostic:" text)
                 (search (if (eq class 'ctm-rejection) "quoted name value" "Typed names")
                         (princ-to-string condition))))))
    (dolist (text '("a - type:\"Name\"." "a - type: \"Name\"."))
      (let* ((map (read-text text)) (owner (first-topic map))
             (name (first (topic-names owner))) (type (topic-name-type name)))
        (check (concatenate 'string "name-classification-supported:" text) (typep name 'topic-maps.tmdm:topic-name))
        (check (concatenate 'string "name-classification-value:" text) (string= "Name" (topic-name-value name)))
        (check (concatenate 'string "name-classification-parent:" text) (eq owner (topic-name-parent name)))
        (check (concatenate 'string "name-classification-type:" text)
               (equal '("https://example.invalid/a/doc.ctm#type") (topic-item-identifiers type)))
        (check (concatenate 'string "name-classification-no-extra-topic:" text) (= 2 (length (topic-map-topics map))))))
    ;; A type-like token alone must not turn a malformed name into UNSUPPORTED.
    (check "name-type-without-separator-is-rejected"
           (eq :expected-name-type-separator (error-code (rejection "a - type \"Name\"."))))
    (check "typed-name-without-value-is-rejected"
           (eq :expected-name-value (error-code (rejection "a - type:."))))
    (check "typed-name-layout-supported"
           (verify-item-invariants (read-text (format nil "a - type:~%#( layout )# \"Name\"."))))
    (check "additional-identity-now-deserialized"
           (let* ((map (read-text "a <https://example.invalid/alias>.")) (topic (first-topic map)))
             (and (= 1 (length (topic-map-topics map)))
                  (equal (topic-subject-identifiers topic) '("https://example.invalid/alias"))
                  (equal (topic-item-identifiers topic) '("https://example.invalid/a/doc.ctm#a")))))
    (dolist (ending (list (string #\Return) (format nil "~C~C" #\Return #\Newline)))
      (let ((condition (rejection (concatenate 'string "a." ending "ex:fake."))))
        (check (if (= 1 (length ending)) "cr-error-line" "crlf-error-line")
               (and (= 2 (error-line condition)) (= 1 (error-column condition))))))
    (check "empty-delimited-iri-rejected" (eq :empty-iri (error-code (rejection "<>."))))
    (check "invalid-relative-colon-rejected" (eq :invalid-iri (error-code (rejection "<1bad:thing>."))))
    (check "multiple-fragments-rejected" (eq :invalid-iri (error-code (rejection "<https://example.invalid/#a#b>."))))
    (dolist (pair '(("g:h" "g:h") ("g" "http://a/b/c/g")
                    ("./g" "http://a/b/c/g") ("../g" "http://a/b/g")
                    ("//g" "http://g") ("?y" "http://a/b/c/d;p?y")
                    ("#s" "http://a/b/c/d;p?q#s") ("." "http://a/b/c/")
                    (".." "http://a/b/") ("../../g" "http://a/g")
                    ("/./g" "http://a/g") ("g/../h" "http://a/b/c/h")))
      (check (concatenate 'string "iri-resolution:" (first pair))
             (equal (topic-subject-identifiers
                     (first-topic (read-text (format nil "<~A>." (first pair)) "http://a/b/c/d;p?q")))
                    (list (second pair)))))
    (check "reader-does-not-depend-on-canonicalizer"
           (equal (asdf:system-depends-on (asdf:find-system "topic-maps/ctm"))
                  '("topic-maps/tmdm")))
    (setf *last-checks* (nreverse *checks*))
    (format t "~&CTM-IDENTITY-SEMANTICS-PASS: ~D checks, 5 imported semantic cases, required prefix rejection; no CXTM equality passes.~%"
            (length *last-checks*))
    t))
