(in-package #:topic-maps.xml)

;;; W3C Canonical XML 1.0 (2001-03-15), restricted to the XTM 2.0
;;; 4.16.3 node set. Not an arbitrary XPath, Exclusive C14N or C14N 1.1 API.
(defparameter +xml-namespace+ "http://www.w3.org/XML/1998/namespace")
(defparameter +xmlns-namespace+ "http://www.w3.org/2000/xmlns/")
(defparameter +xtm-namespace+ "http://www.topicmaps.org/xtm/")

(define-condition canonicalization-error (error)
  ((code :initarg :code :reader canonicalization-error-code)
   (detail :initarg :detail :reader canonicalization-error-detail))
  (:report (lambda (c s) (format s "XML canonicalization ~S: ~A"
    (canonicalization-error-code c) (canonicalization-error-detail c)))))

(defstruct (canonical-context (:constructor %make-canonical-context (document))
                              (:copier nil) (:conc-name %canonical-context-))
  ;; Private DOM, built only from qualified raw bytes; never returned for mutation.
  (document nil :read-only t))

(defun parse-canonical-context (bytes)
  "Parse original XML octets into an opaque namespace/QName-preserving context.
This additional entry point does not change PARSE-OCTETS or global SAX settings.
The existing qualification markers, closed handler, DOCTYPE prohibition, fresh
DTD cache and non-returning external-resource denial remain mandatory."
  (check-type bytes (vector (unsigned-byte 8)))
  (unless (and (boundp 'cxml::*topic-maps-encoding-patch*)
               (equal (symbol-value 'cxml::*topic-maps-encoding-patch*) "19d0b-1")
               (boundp 'runes-encoding::*topic-maps-encoding-patch*)
               (equal (symbol-value 'runes-encoding::*topic-maps-encoding-patch*) "19d0b-1"))
    (error 'unqualified-parser))
  (let ((sax:*namespace-processing* t) (sax:*include-xmlns-attributes* t)
        (sax:*use-xmlns-namespace* t) (cxml:*catalog* nil)
        (cxml:*cache-all-dtds* nil) (cxml:*dtd-cache* (cxml:make-dtd-cache)))
    (%make-canonical-context
      (cxml:parse-octets bytes
        (make-instance 'closed-handler :chained-handler (cxml-dom:make-dom-builder))
        :validate nil :disallow-internal-subset t :entity-resolver #'deny-external-resource))))

(defun %dom-list (nodes)
  (loop for i below (dom:length nodes) collect (dom:item nodes i)))
(defun %element-p (node) (eq (dom:node-type node) :element))
(defun %namespace (node) (or (dom:namespace-uri node) ""))
(defun %prefix (node) (or (dom:prefix node) ""))
(defun %namespace-attribute-p (node) (string= (%namespace node) +xmlns-namespace+))
(defun %attributes (element)
  (remove-if #'%namespace-attribute-p (%dom-list (dom:attributes element))))
(defun %children (node) (%dom-list (dom:child-nodes node)))
(defun %elements (nodes)
  (loop for node in nodes when (%element-p node)
        append (cons node (%elements (%children node)))))
(defun %resource-elements (context)
  (remove-if-not (lambda (e) (and (string= (%namespace e) +xtm-namespace+)
                                 (string= (dom:local-name e) "resourceData")))
    (%elements (%children (%canonical-context-document context)))))

(defun resource-data-count (context)
  "Number of XTM-namespace resourceData elements in document order. No XTM validation."
  (check-type context canonical-context)
  (length (%resource-elements context)))

(defun %absolute-namespace-p (uri)
  ;; C14N 1.0 2.1 prohibits relative namespace URIs, even unused ones.
  ;; XML namespace well-formedness and character validity belong to the parser.
  (let ((colon (position #\: uri)))
    (and colon (plusp colon) (find (char uri 0) "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
         (every (lambda (c) (find c "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-."))
                (subseq uri 1 colon)))))
(defun %check-namespace-uris (document)
  (dolist (e (%elements (%children document)))
    (dolist (a (%dom-list (dom:attributes e)))
      (when (and (%namespace-attribute-p a) (plusp (length (dom:value a)))
                 (not (%absolute-namespace-p (dom:value a))))
        (error 'canonicalization-error :code :relative-namespace-uri :detail (dom:value a))))))

(defun %in-scope-namespaces (element)
  ;; DOM stores declarations, not the XPath namespace axis. Reconstruct that
  ;; axis from nearest ancestors, preserving the original prefix and URI.
  (let ((seen nil) (bindings nil))
    (loop for e = element then (dom:parent-node e) while (and e (%element-p e)) do
      (dolist (a (%dom-list (dom:attributes e)))
        (when (%namespace-attribute-p a)
          (let ((prefix (if (string= (dom:name a) "xmlns") "" (dom:local-name a))))
            (unless (member prefix seen :test #'string=)
              (push prefix seen)
              (unless (zerop (length (dom:value a))) (push (cons prefix (dom:value a)) bindings)))))))
    bindings))
(defun %used-namespace-pairs (elements)
  ;; XTM's filter is over the ENTIRE selected node set, not just visibly used
  ;; prefixes on the current element. QName-valued attribute values do not count.
  (remove-duplicates
    (loop for e in elements append
      (loop for n in (cons e (%attributes e))
            unless (zerop (length (%namespace n))) collect (cons (%prefix n) (%namespace n))))
    :test #'equal))
(defun %selected-namespaces (element used)
  (sort (remove-if-not (lambda (binding)
                         (and (not (equal binding (cons "xml" +xml-namespace+)))
                              (member binding used :test #'equal)))
                       (%in-scope-namespaces element))
        #'string< :key #'car))
(defun %apex-attributes (element)
  ;; C14N 1.0 2.4: inherit nearest xml:* attributes when the parent is omitted.
  ;; This is not C14N 1.1: xml:id/base are NOT given 1.1 special treatment.
  (let* ((attributes (%attributes element))
         (seen (loop for a in attributes when (string= (%namespace a) +xml-namespace+)
                     collect (dom:local-name a))))
    (loop for e = (dom:parent-node element) then (dom:parent-node e)
          while (and e (%element-p e)) do
      (dolist (a (%attributes e))
        (when (and (string= (%namespace a) +xml-namespace+)
                   (not (member (dom:local-name a) seen :test #'string=)))
          (push (dom:local-name a) seen) (push a attributes))))
    attributes))
(defun %attribute-less-p (a b)
  (or (string< (%namespace a) (%namespace b))
      (and (string= (%namespace a) (%namespace b))
           (string< (dom:local-name a) (dom:local-name b)))))
(defun %write-canonical-value (value stream attribute-p)
  (loop for c across value do
    (let ((escape (case c
                    (#\& "&amp;") (#\< "&lt;")
                    (#\> (unless attribute-p "&gt;"))
                    (#\" (when attribute-p "&quot;"))
                    (#\Return "&#xD;")
                    (#\Tab (when attribute-p "&#x9;"))
                    (#\Newline (when attribute-p "&#xA;")))))
      (if escape (write-string escape stream) (write-char c stream)))))
(defun %write-canonical-attribute (name value stream)
  (write-char #\Space stream) (write-string name stream) (write-string "=\"" stream)
  (%write-canonical-value value stream t) (write-char #\" stream))

(defun %canonical-subtrees (nodes)
  "Internal engine: all element/attribute/text descendants, XTM namespace filter.
NODES are the apex children of the omitted resourceData container."
  (let ((used (%used-namespace-pairs (%elements nodes))))
    (with-output-to-string (stream)
      (labels ((emit (node parent-namespaces apex-p)
                 (case (dom:node-type node)
                   (:element
                     (let ((namespaces (%selected-namespaces node used)))
                       (write-char #\< stream) (write-string (dom:tag-name node) stream)
                       ;; Namespace absence refers to the nearest SELECTED parent,
                       ;; not a cumulative rendered-prefix table (C14N 2.3).
                       (when (and (not (assoc "" namespaces :test #'string=))
                                  (assoc "" parent-namespaces :test #'string=))
                         (%write-canonical-attribute "xmlns" "" stream))
                       (dolist (binding namespaces)
                         (unless (equal binding (assoc (car binding) parent-namespaces :test #'string=))
                           (%write-canonical-attribute
                             (if (zerop (length (car binding))) "xmlns" (concatenate 'string "xmlns:" (car binding)))
                             (cdr binding) stream)))
                       (dolist (a (sort (if apex-p (%apex-attributes node) (%attributes node)) #'%attribute-less-p))
                         (%write-canonical-attribute (dom:name a) (dom:value a) stream))
                       (write-char #\> stream)
                       (dolist (child (%children node)) (emit child namespaces nil))
                       (write-string "</" stream) (write-string (dom:tag-name node) stream) (write-char #\> stream)))
                   ((:text :cdata-section) (%write-canonical-value (dom:data node) stream nil))
                   ;; PI and comments are NOT selected by XTM 4.16.3.
                   ((:processing-instruction :comment) nil)
                   (otherwise (error 'canonicalization-error :code :unexpected-node-type :detail (dom:node-type node))))))
        (dolist (node nodes) (emit node nil t))))))

(defun canonicalize-resource-data (context &key (index 0))
  "Return (values Unicode-string UTF-8-octets) for resourceData INDEX (zero based).
Selection is by expanded name and document order in the qualified opaque CONTEXT.
The container itself is omitted. This function does not validate XTM syntax or
choose a datatype, and never constructs or changes a Topic Maps model. The
result can be a text fragment, several apex elements, or the empty string."
  (check-type context canonical-context)
  (check-type index (integer 0 *))
  (%check-namespace-uris (%canonical-context-document context))
  (let ((element (nth index (%resource-elements context))))
    (unless element
      (error 'canonicalization-error :code :resource-data-index :detail index))
    (let ((string (%canonical-subtrees (%children element))))
      (values string (babel:string-to-octets string :encoding :utf-8 :use-bom nil)))))
