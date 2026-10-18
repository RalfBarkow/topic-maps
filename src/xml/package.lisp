(defpackage #:topic-maps.xml
  (:use #:cl)
  (:export #:parse-octets #:doctype-forbidden #:external-resource-forbidden
           #:unqualified-parser #:denied-system-id))
