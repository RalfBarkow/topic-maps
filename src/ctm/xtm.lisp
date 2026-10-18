(in-package #:topic-maps.ctm)

;; Optional ASDF adapter: neither the standalone XTM model reader nor plain CTM
;; silently loads dependencies or retrieves resources. This method is installed
;; only by explicitly loading topic-maps/ctm/xtm in a qualified XML environment.
(define-condition mergemap-source-error (ctm-resource-error) ())
(define-condition mergemap-source-unsupported (ctm-unsupported) ())

(defmethod mergemap-reader ((notation (eql :xtm)))
  (lambda (bytes resource source-key parser)
    (declare (ignore parser))
    (let ((position (getf (first *resource-context*) :position)))
      (handler-case
          (topic-maps.xtm:deserialize-octets
            ;; Preserve the very same specialized vector. The established
            ;; resolver also accepts generic vectors of byte values; specialize
            ;; only their storage representation, never decode/re-encode XML.
            (if (typep bytes '(vector (unsigned-byte 8))) bytes
                (map '(vector (unsigned-byte 8)) #'identity bytes))
            :document-iri resource :source-key source-key)
        (topic-maps.xtm:xtm-unsupported (c)
          (problem 'mergemap-source-unsupported (topic-maps.xtm:error-code c)
                   position (princ-to-string c) :character c))
        (topic-maps.xtm:xtm-error (c)
          (problem 'mergemap-source-error (topic-maps.xtm:error-code c)
                   position (princ-to-string c) :character c))
        (topic-maps.tmdm:item-identifier-error (c)
          (problem 'mergemap-source-error (topic-maps.tmdm:item-identifier-error-code c)
                   position (princ-to-string c) :character c))
        (topic-maps.tmdm:core-subject-error (c)
          (problem 'mergemap-source-error (topic-maps.tmdm:core-subject-error-code c)
                   position (princ-to-string c) :character c))))))
