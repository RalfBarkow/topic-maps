(in-package #:topic-maps.tests)

(defvar *checks* nil)
(defvar *last-checks* nil)

(defmacro check (label form)
  `(progn
     (unless ,form (error "Infrastructure check failed: ~A" ,label))
     (push ,label *checks*)))

(defun signals-error-p (thunk)
  (handler-case (progn (funcall thunk) nil) (error () t)))

(defun fixture-root ()
  (asdf:system-relative-pathname "topic-maps/tests" "tests/fixtures/corpus/"))

(defun status-fixture (expected)
  ;; This record is not imported from the CTM corpus, and no parser is mocked.
  (make-test-case :id "infrastructure/outcome-protocol"
                    :category (if (eq expected :cxtm-equal) :valid :invalid)
                    :expected-outcome expected))

(defun run-tests ()
  (let* ((*checks* nil)
         (corpus (discover-corpus))
         (summary (summarize-corpus corpus))
         (counts (getf summary :counts))
         (cases (corpus-cases corpus)))
    (check "pin-counts-agree" (getf summary :counts-match-pin))
    (check "input-count-is-valid-plus-invalid"
           (= (length cases) (+ (getf counts :valid) (getf counts :invalid))))
    (check "all-imported-cases-not-run"
           (every (lambda (case) (and (eq :not-run (test-case-status case))
                                     (null (test-case-actual-outcome case)))) cases))
    (check "no-imported-ctm-pass"
           (equal (getf summary :statuses)
                  (list :pass 0 :fail 0 :unsupported 0 :not-run (length cases))))
    (check "source-files-exist" (every (lambda (case) (probe-file (test-case-source-pathname case))) cases))
    (check "valid-baselines-exist"
           (every (lambda (case) (probe-file (test-case-expected-baseline case)))
                  (select-cases corpus :category :valid)))
    (check "invalid-contract-is-rejection-without-baseline"
           (every (lambda (case) (and (eq :ctm-rejection (test-case-expected-outcome case))
                                     (null (test-case-expected-baseline case))))
                  (select-cases corpus :category :invalid)))
    (check "baseline-correspondence" (getf (verify-correspondence corpus) :ok))
    (check "selection-counts"
           (and (= (getf counts :valid) (length (select-cases corpus :category :valid)))
                (= (getf counts :invalid) (length (select-cases corpus :category :invalid)))))
    (let ((selected (select-cases corpus :id "ctm/in/simple.ctm")))
      (check "stable-id-selection" (= 1 (length selected)))
      (check "selected-record-is-original" (member (first selected) cases :test #'eq))
      (check "combined-selection" (null (select-cases corpus :category :invalid :id "ctm/in/simple.ctm")))
      (check "expected-outcome-exposed" (eq :cxtm-equal (test-case-expected-outcome (first selected))))
      (check "document-iri-independent-of-filesystem"
             (string= (test-case-document-iri (first selected))
                      (format nil "https://ctm-tests.example.invalid/~A/ctm/in/simple.ctm"
                              (getf (corpus-metadata corpus) :commit)))))
    (check "reviewed-case-clause-exposed"
           (member "CTM 3.3.6" (test-case-clauses
                               (first (select-cases corpus :id "ctm/in/simple.ctm")))
                   :test #'string=))
    (check "unreviewed-case-clause-not-invented"
           (null (test-case-clauses
                  (first (select-cases corpus :id "ctm/in/template-simple.ctm")))))
    (check "unknown-id-yields-no-cases" (null (select-cases corpus :id "missing")))
    (check "unknown-category-is-error" (signals-error-p (lambda () (select-cases corpus :category :bogus))))
    (check "case-order-is-deterministic"
           (equal (mapcar #'test-case-id cases)
                  (sort (mapcar #'test-case-id cases) #'string<)))
    (check "fresh-discovery-report-equality"
           (string= (report-string corpus) (report-string (discover-corpus))))
    (check "auxiliaries-not-inputs"
           (notany (lambda (resource) (find (getf resource :id) cases :key #'test-case-id :test #'string=))
                   (corpus-auxiliaries corpus)))
    (check "baseline-ctm-artifact-not-input"
           (eq :baseline-non-cxtm-artifact
               (getf (find "ctm/baseline/name-type.ctm" (corpus-auxiliaries corpus)
                           :key (lambda (r) (getf r :id)) :test #'string=) :role)))
    (check "auxiliary-resource-registered"
           (eq :include-or-mergemap-resource
               (getf (find "ctm/in/include-wildcard2.sub2" (corpus-auxiliaries corpus)
                           :key (lambda (r) (getf r :id)) :test #'string=) :role)))
    (check "draft-qualification-preserved"
           (search "2010-03-31" (getf summary :qualification)))
    (check "no-reader-systems-defined"
           (every (lambda (name) (null (asdf:find-system name nil)))
                  '("topic-maps/ctm" "topic-maps/tmdm" "topic-maps/cxtm")))
    ;; Incomplete independent fixture: structural problems must be exposed,
    ;; but must never mark an imported syntax test PASS or FAIL.
    (let* ((fixture (discover-corpus :root (fixture-root)
                     :origin :infrastructure-fixture
                     :metadata '(:commit "fixture" :qualification "Infrastructure only")
                     :document-base "https://fixtures.example.invalid/corpus/"))
           (verification (verify-correspondence fixture)))
      (check "fixture-discovery-counts"
             (equal (getf (summarize-corpus fixture) :counts)
                    '(:valid 2 :invalid 1 :baselines 2 :auxiliary 2)))
      (check "missing-baseline-detected"
             (equal (getf verification :missing-baselines) '("ctm/in/beta.ctm")))
      (check "unmatched-baseline-detected"
             (equal (getf verification :unmatched-baselines) '("ctm/baseline/orphan.ctm.cxtm")))
      (check "correspondence-errors-do-not-pass" (null (getf verification :ok)))
      (check "fixture-cases-still-not-run" (every (lambda (c) (eq :not-run (test-case-status c))) (corpus-cases fixture)))
      (check "fixture-iri-policy-explicit"
             (string= "https://fixtures.example.invalid/corpus/ctm/in/alpha.ctm"
                      (test-case-document-iri (first (corpus-cases fixture)))))
      (check "iri-does-not-follow-fixture-directory"
             (string= (report-string fixture)
                      (report-string (discover-corpus :root (fixture-root)
                                        :origin :infrastructure-fixture
                                        :metadata '(:commit "fixture" :qualification "Infrastructure only")
                                        :document-base "https://fixtures.example.invalid/corpus/"))))
      (let ((case (first (corpus-cases fixture))))
        (setf (test-case-source-pathname case) (merge-pathnames "absent.ctm" (fixture-root)))
        (check "missing-source-detected" (equal (getf (verify-correspondence fixture) :missing-inputs)
                                                '("ctm/in/alpha.ctm"))))
      (let ((case (second (corpus-cases fixture))))
        (setf (test-case-id case) (test-case-id (first (corpus-cases fixture))))
        (check "duplicate-id-detected" (getf (verify-correspondence fixture) :duplicate-ids))))
    ;; Result fixtures exercise only state classification; not CTM recognition.
    (dolist (expected '(:cxtm-equal :ctm-rejection))
      (let ((case (status-fixture expected)))
        (check (format nil "~A-initial-not-run" expected) (eq :not-run (test-case-status case)))
        (record-result case :unsupported :diagnostics '("Fixture capability unavailable"))
        (check (format nil "~A-unsupported-never-pass" expected) (eq :unsupported (test-case-status case)))
        (record-result case :execution-error :diagnostics '("Fixture I/O error, not CTM rejection"))
        (check (format nil "~A-execution-error-fails" expected) (eq :fail (test-case-status case)))
        (record-result case (if (eq expected :cxtm-equal) :cxtm-match :ctm-rejection))
        (check (format nil "~A-contract-success" expected) (eq :pass (test-case-status case)))
        (record-result case (if (eq expected :cxtm-equal) :ctm-rejection :ctm-acceptance))
        (check (format nil "~A-contract-mismatch" expected) (eq :fail (test-case-status case)))
        (record-result case :cxtm-mismatch :diagnostics '("Independent fixture mismatch"))
        (check (format nil "~A-diagnostics-retained" expected)
               (equal '("Independent fixture mismatch") (test-case-diagnostics case)))
        (reset-result case)
        (check (format nil "~A-reset-not-run" expected)
               (and (eq :not-run (test-case-status case)) (null (test-case-actual-outcome case))
                    (null (test-case-diagnostics case))))))
    (check "unknown-outcome-is-error"
           (signals-error-p (lambda () (record-result (status-fixture :cxtm-equal) :bogus))))
    (check "relative-document-base-rejected"
           (signals-error-p (lambda () (discover-corpus :document-base "relative/"))))
    (check "fragment-document-base-rejected"
           (signals-error-p (lambda () (discover-corpus :document-base "https://example.invalid/#fragment/"))))
    (check "report-no-machine-path"
           (and (not (search (namestring (corpus-root corpus)) (report-string corpus)))
                (not (search "file://" (report-string corpus)))))
    (check "report-no-implementation-claim"
           (search "\"ctmParsing\":false" (report-string corpus)))
    (check "report-keeps-all-imported-not-run" (= (length cases) (getf (getf summary :statuses) :not-run)))
    (setf *last-checks* (nreverse *checks*))
    (format t "~&FOUNDATION-PASS: ~D infrastructure checks; ~D valid, ~D invalid, ~D baselines, ~D auxiliaries; ~D CTM cases NOT-RUN, zero CTM passes.~%"
            (length *last-checks*) (getf counts :valid) (getf counts :invalid)
            (getf counts :baselines) (getf counts :auxiliary) (length cases))
    t))

(defun write-tested-report (pathname)
  (run-tests)
  (write-validation-report (discover-corpus) pathname
                            :infrastructure-checks *last-checks*))
