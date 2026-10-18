(in-package #:topic-maps.xml)

(define-condition doctype-forbidden (error) ())
(define-condition external-resource-forbidden (error)
  ((system-id :initarg :system-id :reader denied-system-id)))
(define-condition unqualified-parser (error) ())

(defclass closed-handler (cxml:sax-proxy) ())

(defmethod sax:start-dtd ((handler closed-handler) name public-id system-id)
  (declare (ignore handler name public-id system-id))
  (error 'doctype-forbidden))

(defun deny-external-resource (public-id system-id)
  (declare (ignore public-id))
  ;; Returning NIL enables CXML's OPEN fallback. Always signal instead.
  (error 'external-resource-forbidden :system-id system-id))

(defun parse-octets (bytes handler)
  "Parse XML bytes, returning HANDLER's SAX result. Required XTM boundary.
No parser options can disable namespace processing or external-resource denial.
Reject all DOCTYPEs. Do not accept a filename or an already decoded string."
  (check-type bytes (vector (unsigned-byte 8)))
  (unless (and (boundp 'cxml::*topic-maps-encoding-patch*)
               (equal (symbol-value 'cxml::*topic-maps-encoding-patch*) "19d0b-1")
               (boundp 'runes-encoding::*topic-maps-encoding-patch*)
               (equal (symbol-value 'runes-encoding::*topic-maps-encoding-patch*) "19d0b-1"))
    (error 'unqualified-parser))
  (let ((sax:*namespace-processing* t)
        (sax:*include-xmlns-attributes* nil)
        (cxml:*catalog* nil)
        (cxml:*cache-all-dtds* nil)
        (cxml:*dtd-cache* (cxml:make-dtd-cache)))
    (cxml:parse-octets bytes (make-instance 'closed-handler :chained-handler handler)
                       :validate nil :disallow-internal-subset t
                       :entity-resolver #'deny-external-resource)))
