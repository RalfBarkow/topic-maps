(defpackage #:topic-maps.test-foundation
  (:use #:cl)
  (:export
   #:test-case #:make-test-case #:test-case-id #:test-case-category
   #:test-case-source-pathname #:test-case-document-iri
   #:test-case-expected-outcome #:test-case-expected-baseline
   #:test-case-actual-outcome #:test-case-status #:test-case-diagnostics
   #:test-case-clauses
   #:corpus #:corpus-root #:corpus-origin #:corpus-metadata #:corpus-cases
   #:corpus-baselines #:corpus-auxiliaries
   #:default-corpus-root #:discover-corpus #:verify-correspondence
   #:select-cases #:summarize-corpus #:record-result #:reset-result
   #:write-validation-report #:report-string))
