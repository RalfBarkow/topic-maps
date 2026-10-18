(in-package #:topic-maps.ctm)

(defun directive-iri (parser code message)
  ;; Reuse the existing IRI/QName path without interning a datatype/identity Topic.
  (unless (member (token-kind (look parser)) '(:iri :qname))
    (problem 'ctm-rejection code (token-position (look parser)) message))
  (literal-iri-reference parser))

(defun resource-octets-p (value)
  (and (vectorp value) (not (stringp value))
       (every (lambda (byte) (and (integerp byte) (<= 0 byte 255))) value)))

(defun read-mergemap-directive (parser map)
  "CTM 3.16.3: immediately read a separate Map and import only its content."
  (let* ((start (consume parser))
         (resource (directive-iri parser :expected-mergemap-resource "Mergemap requires a resource IRI reference."))
         (notation (directive-iri parser :expected-mergemap-notation "Mergemap requires a notation IRI reference."))
         (position (token-position start))
         (frame (list :purpose :mergemap :source *source-name* :document-iri (parser-document-iri parser)
                      :position position :position-unit :character :resource-iri resource :notation notation :resource-source nil))
         (*resource-context* (cons frame *resource-context*)))
    (cond ((string= notation "http://psi.topicmaps.org/iso13250/xtm")
           (problem 'ctm-unsupported :xtm-mergemap-notation position "XTM is a mandatory standard notation, but its deserializer is not implemented."))
          ((not (string= notation "http://psi.topicmaps.org/iso13250/ctm"))
           (problem 'ctm-rejection :unknown-mergemap-notation position "The notation IRI is not supported by this processor.")))
    (unless (parser-resource-resolver parser)
      (problem 'ctm-unsupported :resource-resolver-required position "Mergemap needs an explicit resource resolver; no resource was loaded."))
    ;; This stack tracks active deserializations only. A repeated completed
    ;; resource is read again, with a fresh parser and its own wildcard state.
    (when (member resource *active-resource-iris* :test #'string=)
      (problem 'ctm-unsupported :cyclic-mergemap position "Active recursive resource dependency; cycle rejection is implementation policy."))
    (when (>= (length *active-resource-iris*) (1+ (parser-max-resource-depth parser)))
      (problem 'ctm-unsupported :resource-depth-limit position "Configured nested-resource limit reached; this is not a CTM syntax rule."))
    (multiple-value-bind (bytes source-key)
        (handler-case
            (funcall (parser-resource-resolver parser) resource :purpose :mergemap
                     :from-document-iri (parser-document-iri parser) :notation notation)
          (error (condition)
            (problem 'ctm-resource-error :resource-resolver-failure position (princ-to-string condition))))
      (setf (getf frame :resource-source) (or source-key resource))
      (unless bytes
        (problem 'ctm-resource-error :resource-unavailable position "Resolver declined or did not supply the requested resource."))
      (unless (and (resource-octets-p bytes) (or (null source-key) (stringp source-key)))
        (problem 'ctm-resource-error :invalid-resource-result position "Resolver must return an octet vector and a string source key or NIL."))
      (let ((source
              (let ((*source-name* (or source-key resource)) (*source-text* ""))
                ;; Decoding uses the existing strict UTF-8 decoder and BOM policy.
                ;; The key is diagnostic only; RESOURCE remains the Document IRI.
                (deserialize-string (decode-utf8 bytes :strip-bom t) :document-iri resource
                  :source-name *source-name* :resource-resolver (parser-resource-resolver parser)
                  :max-resource-depth (parser-max-resource-depth parser)))))
        (handler-case (topic-maps.tmdm:import-map-content map source)
          (topic-maps.tmdm:item-identifier-error (c)
            (problem 'ctm-rejection (topic-maps.tmdm:item-identifier-error-code c) position (princ-to-string c)))
          (topic-maps.tmdm:core-subject-error (c)
            (problem 'ctm-rejection (topic-maps.tmdm:core-subject-error-code c) position (princ-to-string c)))
          (topic-maps.tmdm:variant-error (c)
            (problem 'ctm-rejection (topic-maps.tmdm:variant-error-code c) position (princ-to-string c)))
          (topic-maps.tmdm:reification-error (c)
            (problem 'ctm-rejection (topic-maps.tmdm:reification-error-code c) position (princ-to-string c))))))))

(defun read-directive (parser map)
  (cond ((string= "prefix" (token-value (look parser))) (read-prefix-directive parser))
        ((string= "mergemap" (token-value (look parser))) (read-mergemap-directive parser map))
        (t (problem 'ctm-unsupported :unsupported-directive (token-position (look parser)) "Directive is outside the supported subset."))))
