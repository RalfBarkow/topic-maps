(in-package #:topic-maps.test-foundation)

(defstruct test-case
  "A test contract and its recorded result. Creating it executes no CTM."
  (id "" :type string)
  category
  source-pathname
  (document-iri "" :type string)
  expected-outcome
  expected-baseline
  actual-outcome
  (status :not-run)
  diagnostics
  ;; NIL means unreviewed, not that no normative clause applies.
  clauses)

(defstruct corpus root origin metadata cases baselines auxiliaries)

(defun auxiliary-role (relative)
  (cond ((equal relative "ctm/STATUS.txt") :draft-qualification)
        ((equal relative "ctm/MISSING.txt") :upstream-coverage-notes)
        ((uiop:string-prefix-p "ctm/baseline/" relative) :baseline-non-cxtm-artifact)
        ((or (equal (pathname-type relative) "sub")
             (equal (pathname-type relative) "sub2")) :include-or-mergemap-resource)
        (t :unclassified-resource)))

(defun discover-corpus (&key (root (default-corpus-root))
                              (metadata (read-corpus-metadata))
                              (origin :upstream-ctm) document-base)
  "Discover files by directory and extension; do not read CTM syntax."
  (let* ((root (uiop:ensure-directory-pathname (truename root)))
         (ctm (merge-pathnames "ctm/" root))
         (base (or document-base
                   (format nil "https://ctm-tests.example.invalid/~A/"
                           (getf metadata :commit))))
         (cases nil)
         (baselines (remove-if-not #'(lambda (p) (file-type-p p "cxtm"))
                                   (sorted-files (merge-pathnames "baseline/" ctm) root)))
         (inputs nil)
         (clauses (when (eq origin :upstream-ctm) (read-clause-map))))
    (dolist (directory '("in/" "invalid/"))
      (unless (uiop:directory-exists-p (merge-pathnames directory ctm))
        (error "Missing CTM input directory ~A" directory))
      (let* ((valid (equal directory "in/"))
             (input-root (merge-pathnames directory ctm)))
        (dolist (path (sorted-files input-root root))
          (when (file-type-p path "ctm")
            (push path inputs)
            (push (make-test-case
                   :id (relative-file-name path root)
                   :clauses (copy-list (cdr (assoc (relative-file-name path root) clauses :test #'string=)))
                   :category (if valid :valid :invalid)
                   :source-pathname path
                   :document-iri (document-iri base (relative-file-name path root))
                   :expected-outcome (if valid :cxtm-equal :ctm-rejection)
                   :expected-baseline
                   (when valid
                     (merge-pathnames
                      (concatenate 'string
                                   (relative-file-name path input-root) ".cxtm")
                      (merge-pathnames "baseline/" ctm))))
                  cases)))))
    (let ((auxiliary
            (loop for path in (sorted-files ctm root)
                  unless (or (member path inputs :test #'equal)
                             (member path baselines :test #'equal))
                    collect (let ((id (relative-file-name path root)))
                              (list :id id :source-pathname path
                                    :document-iri (document-iri base id)
                                    :role (auxiliary-role id))))))
      (make-corpus :root root :origin origin :metadata (copy-tree metadata)
                   :cases (sort cases #'string< :key #'test-case-id)
                   :baselines baselines :auxiliaries auxiliary))))

(defun select-cases (corpus &key category id)
  "Return cases in stable ID order. An unknown ID yields NIL."
  (unless (member category '(nil :valid :invalid))
    (error "Unknown case category ~S." category))
  (remove-if-not (lambda (case)
                   (and (or (null category) (eq category (test-case-category case)))
                        (or (null id) (string= id (test-case-id case)))))
                 (corpus-cases corpus)))

(defun verify-correspondence (corpus)
  "Return structural evidence without changing execution statuses."
  (let* ((cases (corpus-cases corpus))
         (expected (remove nil (mapcar #'test-case-expected-baseline cases)))
         (missing-inputs
           (loop for case in cases
                 unless (probe-file (test-case-source-pathname case))
                   collect (test-case-id case)))
         (missing-baselines
           (loop for case in cases
                 when (and (test-case-expected-baseline case)
                           (not (probe-file (test-case-expected-baseline case))))
                   collect (test-case-id case)))
         (unmatched
           (loop for path in (corpus-baselines corpus)
                 unless (member path expected :test #'equal)
                   collect (relative-file-name path (corpus-root corpus))))
         (duplicate-ids
           (loop with seen = (make-hash-table :test #'equal)
                 for case in cases for id = (test-case-id case)
                 if (gethash id seen) collect id
                   else do (setf (gethash id seen) t))))
    (list :ok (not (or missing-inputs missing-baselines unmatched duplicate-ids))
          :missing-inputs missing-inputs :missing-baselines missing-baselines
          :unmatched-baselines unmatched :duplicate-ids duplicate-ids)))

(defun reset-result (case)
  (setf (test-case-status case) :not-run
        (test-case-actual-outcome case) nil
        (test-case-diagnostics case) nil)
  case)

(defun record-result (case outcome &key diagnostics)
  "Classify an outcome supplied by an executor. This function executes nothing.
CTM rejection means an identified syntax/semantic rejection, never an I/O or
unsupported-feature exception. Infrastructure fixtures exercise this protocol."
  (unless (and (member outcome '(:cxtm-match :cxtm-mismatch :ctm-rejection
                                :ctm-acceptance :unsupported :execution-error))
               (member (test-case-expected-outcome case) '(:cxtm-equal :ctm-rejection))
               (listp diagnostics) (every #'stringp diagnostics))
    (error "Invalid outcome contract ~S / ~S." outcome diagnostics))
  (setf (test-case-actual-outcome case) outcome
        (test-case-diagnostics case) (copy-list diagnostics)
        (test-case-status case)
        (cond ((eq outcome :unsupported) :unsupported)
              ((or (and (eq (test-case-expected-outcome case) :cxtm-equal)
                        (eq outcome :cxtm-match))
                   (and (eq (test-case-expected-outcome case) :ctm-rejection)
                        (eq outcome :ctm-rejection))) :pass)
              (t :fail)))
  case)

(defun summarize-corpus (corpus)
  (let* ((cases (corpus-cases corpus))
         (counts (list :valid (length (select-cases corpus :category :valid))
                       :invalid (length (select-cases corpus :category :invalid))
                       :baselines (length (corpus-baselines corpus))
                       :auxiliary (length (corpus-auxiliaries corpus))))
         (statuses
           (loop for status in '(:pass :fail :unsupported :not-run)
                 append (list status (count status cases :key #'test-case-status))))
         (expected (getf (corpus-metadata corpus) :expected-counts)))
    (list :origin (corpus-origin corpus) :repository (getf (corpus-metadata corpus) :repository)
          :commit (getf (corpus-metadata corpus) :commit)
          :qualification (getf (corpus-metadata corpus) :qualification)
          :counts counts :counts-match-pin (or (null expected) (equal counts expected))
          :statuses statuses :correspondence (verify-correspondence corpus))))
