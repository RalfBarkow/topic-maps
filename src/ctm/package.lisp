(defpackage #:topic-maps.ctm
  (:use #:cl)
  (:export #:deserialize-string #:deserialize-file
           #:ctm-error #:ctm-rejection #:undefined-prefix #:prefix-collision #:ctm-unsupported
           #:error-code #:error-position #:error-line #:error-column
           #:error-source #:error-position-unit #:error-context
           #:template-error #:duplicate-template #:undefined-template #:template-arity-error
           #:unbound-template-variable #:invalid-template-argument #:invalid-template-body))
