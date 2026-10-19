(in-package #:topic-maps.ctm)

(defun directive-iri (parser code message)
  ;; Reuse the existing IRI/QName path without interning an identity Topic.
  (unless (member (token-kind (look parser)) '(:iri :qname))
    (problem 'ctm-rejection code (token-position (look parser)) message))
  (literal-iri-reference parser))

(defun resource-octets-p (value)
  (and (vectorp value) (not (stringp value))
       (every (lambda (byte) (and (integerp byte) (<= 0 byte 255))) value)))

(defgeneric mergemap-reader (notation)
  (:documentation "Internal notation dispatch. The explicit CTM/XTM adapter adds :XTM."))
(defmethod mergemap-reader ((notation t)) nil)
(defmethod mergemap-reader ((notation (eql :ctm)))
  (lambda (bytes resource source-key parser)
    (deserialize-string (decode-ctm-resource bytes source-key)
      :document-iri resource :source-name source-key
      :resource-resolver (parser-resource-resolver parser)
      :max-resource-depth (parser-max-resource-depth parser))))
(defun mergemap-notation-kind (notation position)
  (cond ((string= notation "http://psi.topicmaps.org/iso13250/ctm") :ctm)
        ((string= notation "http://psi.topicmaps.org/iso13250/xtm") :xtm)
        (t (problem 'ctm-rejection :unknown-mergemap-notation position
                    "The notation IRI is not supported by this processor."))))
(defun decode-ctm-resource (bytes source-key)
  ;; Only CTM resources use the CTM decoder, including the existing BOM policy.
  (let ((*source-name* source-key) (*source-text* ""))
    (decode-ctm-octets bytes)))

(defun call-with-resource (parser resource purpose position notation continuation)
  "Controlled retrieval of untouched octets. Decoding belongs to the notation reader."
  (let* ((frame (list :purpose purpose :source *source-name* :document-iri (parser-document-iri parser)
                      :position position :position-unit :character :resource-iri resource :notation notation :resource-source nil))
         (*resource-context* (cons frame *resource-context*)))
    (when (eq purpose :mergemap) (mergemap-notation-kind notation position))
    (unless (parser-resource-resolver parser)
      (problem 'ctm-unsupported :resource-resolver-required position "An explicit resource resolver is required; no resource was loaded."))
    (when (and (eq purpose :mergemap)
               (not (mergemap-reader (mergemap-notation-kind notation position))))
      (problem 'ctm-unsupported :xtm-mergemap-reader-required position
               "Load topic-maps/ctm/xtm with the qualified XML source environment before XTM Mergemap."))
    ;; Active recursion and depth limits are implementation resource policy,
    ;; not claims that recursive dependencies are invalid CTM syntax.
    (when (member resource *active-resource-iris* :test #'string=)
      (problem 'ctm-unsupported (ecase purpose (:mergemap :cyclic-mergemap) (:include :cyclic-include)) position
               "Active recursive resource dependency; cycle rejection is implementation policy."))
    (when (>= (length *active-resource-iris*) (1+ (parser-max-resource-depth parser)))
      (problem 'ctm-unsupported :resource-depth-limit position "Configured nested-resource limit reached; this is not a CTM syntax rule."))
    (multiple-value-bind (bytes source-key)
        (handler-case
            (funcall (parser-resource-resolver parser) resource :purpose purpose
                     :from-document-iri (parser-document-iri parser) :notation notation)
          (error (condition)
            (problem 'ctm-resource-error :resource-resolver-failure position (princ-to-string condition) :character condition)))
      (setf (getf frame :resource-source) (or source-key resource))
      (unless bytes
        (problem 'ctm-resource-error :resource-unavailable position "Resolver declined or did not supply the requested resource."))
      (unless (and (resource-octets-p bytes) (or (null source-key) (stringp source-key)))
        (problem 'ctm-resource-error :invalid-resource-result position "Resolver must return an octet vector and a string source key or NIL."))
      (funcall continuation bytes (or source-key resource)))))

(defun call-with-import-diagnostics (position thunk)
  ;; Keep source errors at the resource source; model transfer/alias errors are
  ;; attributed to the caller's directive with its active resource context.
  (handler-case (funcall thunk)
    (topic-maps.tmdm:item-identifier-error (c)
      (problem 'ctm-rejection (topic-maps.tmdm:item-identifier-error-code c) position (princ-to-string c) :character c))
    (topic-maps.tmdm:core-subject-error (c)
      (problem 'ctm-rejection (topic-maps.tmdm:core-subject-error-code c) position (princ-to-string c) :character c))
    (topic-maps.tmdm:variant-error (c)
      (problem 'ctm-rejection (topic-maps.tmdm:variant-error-code c) position (princ-to-string c) :character c))
    (topic-maps.tmdm:reification-error (c)
      (problem 'ctm-rejection (topic-maps.tmdm:reification-error-code c) position (princ-to-string c) :character c))))

(defun read-mergemap-directive (parser map)
  "CTM 3.16.3: immediately read a separate Map and import only its content."
  (let* ((start (consume parser))
         (resource (directive-iri parser :expected-mergemap-resource "Mergemap requires a resource IRI reference."))
         (notation (directive-iri parser :expected-mergemap-notation "Mergemap requires a notation IRI reference."))
         (position (token-position start)))
    (call-with-resource parser resource :mergemap position notation
      (lambda (bytes source-key)
        (let ((source (funcall (mergemap-reader (mergemap-notation-kind notation position))
                              bytes resource source-key parser)))
          (call-with-import-diagnostics position
            (lambda () (topic-maps.tmdm:import-map-content map source))))))))

(defun add-include-aliases (map child-document parent-document position)
  "CTM 3.16.2: one snapshot/pass per Include level, original IIs retained.
Use literal string-prefix matching, not an assumed fragment/path boundary.
Already resolved locator suffixes are not CTM-percent-decoded again."
  (let ((aliases
          (loop for topic in (topic-maps.tmdm:topic-map-topics map) append
            (loop for identifier in (topic-maps.tmdm:topic-item-identifiers topic)
                  when (starts-with child-document identifier)
                    collect (list topic (resolve-iri (subseq identifier (length child-document))
                                                     parent-document position :unescape nil))))))
    (dolist (alias aliases)
      ;; A preceding addition may replace/merge this Topic. The public operation
      ;; resolves its retained handle and uses the existing identity machinery.
      (topic-maps.tmdm:add-topic-identifier (first alias) :item-identifier (second alias))))
  map)

(defun read-include-directive (parser map)
  "CTM 3.16.2, with caller-context execution of imported Template bodies."
  (let* ((start (consume parser)) (position (token-position start))
         (resource (directive-iri parser :expected-include-resource "Include requires a resource IRI reference.")))
    (call-with-resource parser resource :include position nil
      (lambda (bytes source-key)
        (multiple-value-bind (source counter child)
            (deserialize-context (decode-ctm-resource bytes source-key) :document-iri resource :source-name source-key
              :wildcard-iri (parser-document-iri parser) :wildcard-counter (parser-wildcard-counter parser)
              :resource-resolver (parser-resource-resolver parser)
              :max-resource-depth (parser-max-resource-depth parser))
          ;; Reject register conflicts before modifying the caller's Map,
          ;; registry or Counter. Prefix bindings and named-Wildcard caches are
          ;; per processor and are deliberately not transferred.
          (maphash (lambda (key definition)
                     (when (gethash key (parser-templates parser))
                       (problem 'duplicate-template :duplicate-template position
                                (format nil "Included Template ~A/~D is already defined (source ~A, character ~D)."
                                        (first key) (second key) (template-definition-source-name definition)
                                        (template-definition-position definition)))))
                   (parser-templates child))
          (call-with-import-diagnostics position
            (lambda ()
              (add-include-aliases source resource (parser-document-iri parser) position)
              (topic-maps.tmdm:import-map-content map source)))
          (maphash (lambda (key definition) (setf (gethash key (parser-templates parser)) definition))
                   (parser-templates child))
          (setf (parser-wildcard-counter parser) counter)
          map)))))

(defun read-directive (parser map)
  (cond ((string= "prefix" (token-value (look parser))) (read-prefix-directive parser))
        ((string= "mergemap" (token-value (look parser))) (read-mergemap-directive parser map))
        ((string= "include" (token-value (look parser))) (read-include-directive parser map))
        ((member (token-value (look parser)) '("encoding" "version") :test #'string=)
         (problem 'ctm-rejection
                  (if (string= "encoding" (token-value (look parser))) :misplaced-encoding :misplaced-version)
                  (token-position (look parser)) "Encoding and version are allowed only once, in the initial prolog."))
        (t (problem 'ctm-rejection :unknown-directive (token-position (look parser)) "Unknown CTM directive."))))
