(defpackage #:topic-maps.xml
  (:use #:cl)
  (:export #:parse-octets #:doctype-forbidden #:external-resource-forbidden
           #:unqualified-parser #:denied-system-id
           #:parse-canonical-context #:canonical-context #:resource-data-count
           #:canonicalize-resource-data #:canonicalization-error
           #:canonicalization-error-code #:canonicalization-error-detail))
