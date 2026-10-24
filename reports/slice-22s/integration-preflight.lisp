;; Execute BEFORE any productive Reader edit. Only existing 22R APIs are used.
(require :asdf)
(setf *compile-verbose* nil *load-verbose* nil)
(assert (string= "2.5.4" (lisp-implementation-version)))
(asdf:load-asd (merge-pathnames "../../topic-maps.asd" *load-truename*))
(asdf:load-system "topic-maps/xtm/tests")
(in-package #:topic-maps.xtm.tests)
(defun sp-inventory (node &optional path)
  (let* ((next (append path (list (list (topic-maps.xtm::node-uri node) (topic-maps.xtm::node-name node)))))
         (here (when (and (equal (topic-maps.xtm::node-uri node) "http://www.topicmaps.org/xtm/")
                          (equal (topic-maps.xtm::node-name node) "resourceData"))
                 (list (list node next)))))
    (append here (loop for c in (topic-maps.xtm::node-children node) unless (stringp c)
                      append (sp-inventory c next)))))
(let* ((source "<t:topicMap xmlns:t='http://www.topicmaps.org/xtm/' xmlns:p='urn:parent' version='2.0'><t:topic id='owner'><t:occurrence><t:type><t:topicRef href='#type'/></t:type><t:resourceData datatype='http://www.w3.org/2001/XMLSchema#anyType'><p:x/></t:resourceData></t:occurrence><t:occurrence><t:type><t:topicRef href='#type'/></t:type><t:resourceData>plain</t:resourceData></t:occurrence><t:name><t:value>N</t:value><t:variant><t:scope><t:topicRef href='#s'/></t:scope><t:resourceData datatype='http://www.w3.org/2001/XMLSchema#anyType'><f:resourceData xmlns:f='urn:foreign'>F<p:y/></f:resourceData></t:resourceData></t:variant></t:name><t:occurrence><t:type><t:topicRef href='#type'/></t:type><t:resourceData datatype='urn:custom'>custom</t:resourceData></t:occurrence></t:topic></t:topicMap>")
       (expected '("<p:x xmlns:p=\"urn:parent\"></p:x>" "plain" "<f:resourceData xmlns:f=\"urn:foreign\" xmlns:p=\"urn:parent\">F<p:y></p:y></f:resourceData>" "custom"))
       (results nil) (contexts nil))
  (dolist (encoding '(:utf-8 :utf-16le :utf-16be))
    (let* ((raw (bytes source encoding (not (eq encoding :utf-8))))
           (snapshot (copy-seq raw)) (root (topic-maps.xml:parse-octets raw (make-instance 'topic-maps.xtm::source-handler)))
           (inventory (sp-inventory root)) (ctx (topic-maps.xml:parse-canonical-context raw))
           (index (make-hash-table :test #'eq)) (rows nil))
      (assert (equalp raw snapshot))
      (assert (= (length expected) (length inventory) (topic-maps.xml:resource-data-count ctx)))
      (loop for entry in inventory for ordinal from 0 for want in expected do
        (assert (not (nth-value 1 (gethash (first entry) index))))
        (setf (gethash (first entry) index) ordinal)
        (multiple-value-bind (value utf8) (topic-maps.xml:canonicalize-resource-data ctx :index ordinal)
          (assert (equal want value)) (assert (equalp (bytes want) utf8))
          (push (mm-fields "ordinal" ordinal "expandedPath" (format nil "~S" (second entry))
            "datatype" (topic-maps.xtm::attr (first entry) "datatype") "expected" want "actual" value
            "actualHex" (cr-hex utf8)) rows)))
      ;; Distinct document-local source nodes cannot be looked up by EQ in a
      ;; foreign frame, even with identical bytes, IRI or diagnostic Source Key.
      (let* ((other (topic-maps.xml:parse-octets raw (make-instance 'topic-maps.xtm::source-handler)))
             (other-node (first (first (sp-inventory other)))))
        (assert (not (nth-value 1 (gethash other-node index)))))
      (push ctx contexts)
      (push (mm-fields "encoding" (string encoding) "inputHex" (cr-hex raw)
        "sameOriginalBytesUnchanged" :true "sourceResourceCount" (length inventory)
        "contextResourceCount" (topic-maps.xml:resource-data-count ctx)
        "foreignLocalNameSkipped" :true "foreignSourceNodesNotOwned" :true
        "rows" (coerce (nreverse rows) 'vector)) results)))
  ;; Same resource count alone is NOT a provenance proof. Construct contexts
  ;; exclusively in a private document-local frame from the preserved octets;
  ;; no externally supplied opaque context is accepted by the planned Reader.
  (let ((other (topic-maps.xml:parse-canonical-context (bytes (cq-wrap "DIFFERENT")))))
    (assert (= 1 (topic-maps.xml:resource-data-count other))))
  (let ((out (uiop:getenv "TOPIC_MAPS_INTEGRATION_PREFLIGHT_REPORT")))
    (cq-write out (mm-fields "kind" "pre-Reader-edit-existing-22R-API-contract"
      "readerEdited" :false "readerAnyTypeEnabled" :false "qualificationPassed" :true
      "constructionContract" "private per-document frame; retained original bytes; all XTM-expanded-name resourceData nodes in preorder; EQ node ownership; no supplied contexts; cardinality and immutable bytes checked"
      "opaqueContextProvenanceIntrospectable" :false "countAloneSufficient" :false
      "runs" (coerce (nreverse results) 'vector))))
  (format t "INTEGRATION-PREFLIGHT-PASS: 3 encodings; 12 independent indexed values; unchanged Reader~%"))
