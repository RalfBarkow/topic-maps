(in-package #:topic-maps.test-foundation)

;;; A small JSON encoder for our report data, not a parser and not a general
;;; serialization framework. It emits ASCII, so output encoding is portable.
(defstruct (json-object (:constructor json-object (members))) members)

(defun json-string (value stream)
  (write-char #\" stream)
  (loop for c across value for n = (char-code c) do
    (case c
      (#\" (write-string "\\\"" stream))
      (#\\ (write-string "\\\\" stream))
      (otherwise
       (cond ((and (>= n 32) (< n 127)) (write-char c stream))
             ((<= n #xffff) (format stream "\\u~4,'0X" n))
             (t (let ((rest (- n #x10000)))
                  (format stream "\\u~4,'0X\\u~4,'0X"
                          (+ #xd800 (ash rest -10))
                          (+ #xdc00 (logand rest #x3ff)))))))))
  (write-char #\" stream))

(defun json-array (items)
  ;; NIL is JSON null; a zero-length vector represents an empty JSON array.
  (coerce items 'vector))

(defun emit-json-value (value stream)
  (typecase value
    (json-object
     (write-char #\{ stream)
     (loop for (key . item) in (json-object-members value) for first = t then nil do
       (unless first (write-char #\, stream))
       (json-string key stream) (write-char #\: stream) (emit-json-value item stream))
     (write-char #\} stream))
    (string (json-string value stream))
    (vector
     (write-char #\[ stream)
     (loop for item across value for first = t then nil do
       (unless first (write-char #\, stream)) (emit-json-value item stream))
     (write-char #\] stream))
    (integer (format stream "~D" value))
    (symbol (write-string (case value (:true "true") (:false "false")
                                  ((nil) "null")
                                  (otherwise (error "Unsupported JSON symbol ~S" value))) stream))
    (t (error "Unsupported JSON value ~S" value))))

(defun word (keyword)
  (when keyword (string-downcase (symbol-name keyword))))

(defun fields (&rest alternating)
  (json-object (loop for (key value) on alternating by #'cddr collect (cons key value))))

(defun counts-object (plist)
  (json-object (loop for (key value) on plist by #'cddr collect (cons (word key) value))))

(defun correspondence-object (value)
  (fields "ok" (if (getf value :ok) :true :false)
          "missingInputs" (json-array (getf value :missing-inputs))
          "missingBaselines" (json-array (getf value :missing-baselines))
          "unmatchedBaselines" (json-array (getf value :unmatched-baselines))
          "duplicateIDs" (json-array (getf value :duplicate-ids))))

(defun report-data (corpus infrastructure-checks)
  (let ((summary (summarize-corpus corpus)) (root (corpus-root corpus)))
    (fields
     "schemaVersion" 1
     "origin" (word (corpus-origin corpus))
     "repository" (getf summary :repository) "commit" (getf summary :commit)
     "qualification" (getf summary :qualification)
     "implemented" (fields "ctmParsing" :false "tmdmDeserialization" :false
                            "cxtmCanonicalization" :false)
     "counts" (counts-object (getf summary :counts))
     "countsMatchPin" (if (getf summary :counts-match-pin) :true :false)
     "statuses" (counts-object (getf summary :statuses))
     "correspondence" (correspondence-object (getf summary :correspondence))
     "infrastructureChecks" (json-array infrastructure-checks)
     "cases"
     (json-array
      (loop for case in (corpus-cases corpus) collect
        (fields "id" (test-case-id case) "category" (word (test-case-category case))
                "sourcePathname" (relative-file-name (test-case-source-pathname case) root)
                "documentIRI" (test-case-document-iri case)
                "expectedOutcome" (word (test-case-expected-outcome case))
                "expectedCXTM" (when (test-case-expected-baseline case)
                                 (relative-file-name (test-case-expected-baseline case) root))
                "actualOutcome" (word (test-case-actual-outcome case))
                "status" (word (test-case-status case))
                "diagnostics" (json-array (test-case-diagnostics case))
                "specificationClauses" (json-array (test-case-clauses case)))))
     "baselines" (json-array (mapcar (lambda (p) (relative-file-name p root))
                                     (corpus-baselines corpus)))
     "auxiliaryResources"
     (json-array
      (loop for auxiliary in (corpus-auxiliaries corpus) collect
        (fields "id" (getf auxiliary :id) "role" (word (getf auxiliary :role))
                "sourcePathname" (relative-file-name (getf auxiliary :source-pathname) root)
                "documentIRI" (getf auxiliary :document-iri)))))))

(defun report-string (corpus &key infrastructure-checks)
  (with-output-to-string (stream)
    (emit-json-value (report-data corpus infrastructure-checks) stream)
    (terpri stream)))

(defun write-validation-report (corpus pathname &key infrastructure-checks)
  (with-open-file (stream pathname :direction :output :if-exists :supersede
                         :if-does-not-exist :create)
    (write-string (report-string corpus :infrastructure-checks infrastructure-checks) stream))
  pathname)
