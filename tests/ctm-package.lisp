(defpackage #:topic-maps.ctm.tests
  (:use #:cl)
  (:import-from #:topic-maps.ctm #:deserialize-string #:deserialize-file
                #:ctm-error #:ctm-rejection #:undefined-prefix #:ctm-unsupported
                #:error-code #:error-line #:error-column #:error-position)
  (:import-from #:topic-maps.tmdm #:topic-map-topics #:topic-parent #:topic-names
                #:topic-item-identifiers #:topic-subject-identifiers #:topic-subject-locators
                #:topic-name-value #:topic-name-type #:topic-name-parent
                #:default-name-type-identifier)
  (:export #:run-tests #:exercise-corpus #:write-slice-report #:observations))
