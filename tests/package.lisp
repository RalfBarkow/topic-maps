(defpackage #:topic-maps.tests
  (:use #:cl)
  (:import-from #:topic-maps.test-foundation
   #:corpus-auxiliaries
   #:corpus-cases
   #:corpus-metadata
   #:corpus-root
   #:discover-corpus
   #:make-test-case
   #:record-result
   #:report-string
   #:reset-result
   #:select-cases
   #:summarize-corpus
   #:test-case-actual-outcome
   #:test-case-clauses
   #:test-case-diagnostics
   #:test-case-document-iri
   #:test-case-expected-baseline
   #:test-case-expected-outcome
   #:test-case-id
   #:test-case-source-pathname
   #:test-case-status
   #:verify-correspondence
   #:write-validation-report
)
  (:export #:run-tests #:write-tested-report))
