(defpackage #:topic-maps.ctm
  (:use #:cl)
  (:export #:deserialize-string #:deserialize-file
           #:ctm-resource-error #:ctm-error #:ctm-rejection #:undefined-prefix #:prefix-collision #:ctm-unsupported
           #:error-code #:error-position #:error-line #:error-column
           #:error-source #:error-position-unit #:error-context #:error-cause
           #:mergemap-source-error #:mergemap-source-unsupported
           #:template-error #:duplicate-template #:undefined-template #:template-arity-error
           #:unbound-template-variable #:invalid-template-argument #:invalid-template-body))
