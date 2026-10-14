(defpackage #:topic-maps.ctm
  (:use #:cl)
  (:export #:deserialize-string #:deserialize-file
           #:ctm-error #:ctm-rejection #:undefined-prefix #:ctm-unsupported
           #:error-code #:error-position #:error-line #:error-column
           #:error-source #:error-position-unit))
