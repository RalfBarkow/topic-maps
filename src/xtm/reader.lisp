(in-package #:topic-maps.xtm)

(defparameter +namespace+ "http://www.topicmaps.org/xtm/")
;; This is a source tree of XML events, not a second Topic Maps object model.
;; Positions are SAX approximations at the end of a start tag, never byte spans.
(defstruct node uri name attributes children line column)
(defclass source-handler (sax:default-handler)
  ((stack :initform nil :accessor handler-stack)
   (root :initform nil :accessor handler-root)))
(defmethod sax:start-element ((h source-handler) uri local qname attributes)
  (declare (ignore qname))
  (let ((node (make-node :uri uri :name local :line (sax:line-number h)
                        :column (sax:column-number h)
                        :attributes (mapcar (lambda (a)
                                              (list (sax:attribute-namespace-uri a)
                                                    (sax:attribute-local-name a)
                                                    (sax:attribute-value a))) attributes))))
    (if (handler-stack h) (push node (node-children (first (handler-stack h))))
        (setf (handler-root h) node))
    (push node (handler-stack h))))
(defmethod sax:characters ((h source-handler) data)
  (when (handler-stack h) (push (copy-seq data) (node-children (first (handler-stack h))))))
(defmethod sax:end-element ((h source-handler) uri local qname)
  (declare (ignore uri local qname))
  (let ((node (pop (handler-stack h)))) (setf (node-children node) (nreverse (node-children node)))))
(defmethod sax:end-document ((h source-handler)) (handler-root h))

(defun xml-space-p (c) (find c '(#\Space #\Tab #\Newline #\Return)))
(defun collapse-space (text)
  ;; xsd:ID has whiteSpace=collapse, even with a non-validating XML processor.
  (with-output-to-string (out)
    (let ((written nil) (pending nil))
      (loop for c across text do
        (if (xml-space-p c) (when written (setf pending t))
            (progn (when pending (write-char #\Space out))
                   (write-char c out) (setf written t pending nil)))))))
(defun ncname-p (text)
  ;; Use the pinned XML processor's XML 1.0 name character tables; exclude ':'
  ;; for XML Schema ID/NCName and XPointer shorthand pointers (XTM 4.5/4.20).
  (and (plusp (length text)) (not (find #\: text))
       (cxml::valid-name-p (runes:string-rod text))))
(defun attributes (node allowed required)
  (dolist (attr (node-attributes node))
    (unless (and (or (null (first attr)) (equal (first attr) ""))
                 (member (second attr) allowed :test #'string=))
      (reject :unexpected-attribute (format nil "Attribute ~S on ~A." (second attr) (node-name node)) node)))
  (dolist (name required)
    (unless (find name (node-attributes node) :key #'second :test #'string=)
      (reject (if (string= name "id") :missing-id :missing-attribute)
              (format nil "Required ~A attribute is absent." name) node))))
(defun attr (node name)
  (third (find name (node-attributes node) :key #'second :test #'string=)))
(defun elements (node)
  (loop for child in (node-children node)
        if (stringp child) do
          (unless (every #'xml-space-p child)
            (reject :unexpected-text "Only XML whitespace is allowed here." node))
        else collect child))
(defun check-namespace (node)
  (unless (equal (node-uri node) +namespace+)
    (reject :invalid-namespace "Expected the XTM 2.0 namespace." node)))
(defun unsupported (node)
  (reject :unsupported-construct (format nil "XTM ~A is not implemented in this subset." (node-name node))
          node 'xtm-unsupported))
(defun leaf-href (node)
  (attributes node '("href") '("href"))
  (when (elements node) (reject :unexpected-child "A locator element must be empty." node))
  (resolve-iri (attr node "href") *document-iri* node))
(defun reference-iri (node)
  (let* ((iri (leaf-href node)) (fragment (iri-parts-fragment (split-iri iri))))
    (unless (and fragment (ncname-p fragment))
      (reject :invalid-topic-ref "topicRef requires an XPointer shorthand fragment." node))
    iri))

(defun validate-source (root)
  "Check the supported XTM schema before model construction; keep event order.
Unsupported legal extension points are explicit; no claim to validate excluded
constructs' complete subgrammars is made. XML errors have already been checked."
  (let ((ids (make-hash-table :test #'equal))) ; XML ID uniqueness only, no Topics.
    (labels ((validate (node context)
               (check-namespace node)
               (let ((name (node-name node)))
                 (unless (member name context :test #'string=)
                   (reject :unexpected-element (format nil "Unexpected ~A element." name) node))
                 (cond
                   ((string= name "topicMap")
                    (attributes node '("version" "reifier") '("version"))
                    (unless (equal (attr node "version") "2.0")
                      (reject :invalid-version "This reader accepts XTM version 2.0 only." node))
                    (when (attr node "reifier")
                      (resolve-iri (attr node "reifier") *document-iri* node))
                    (let ((phase 0))
                      (dolist (child (elements node))
                        (let* ((name (node-name child))
                               (next (cond ((string= name "itemIdentity") 0)
                                           ((string= name "mergeMap") 1) (t 2))))
                          (when (< next phase) (reject :element-order "topicMap child order is invalid." child))
                          (setf phase next)
                          (validate child '("itemIdentity" "mergeMap" "topic" "association"))))))
                   ((string= name "mergeMap") (mergemap-iri node))
                   ((string= name "topic")
                    (attributes node '("id") '("id"))
                    (let ((id (collapse-space (attr node "id"))))
                      (unless (ncname-p id) (reject :invalid-id "topic/@id must be an XML Schema ID." node))
                      (when (gethash id ids) (reject :duplicate-id "Duplicate XML ID in this document." node))
                      (setf (gethash id ids) t))
                    (let ((phase 0) (instance-seen nil))
                      (dolist (child (elements node))
                        (let* ((name (node-name child))
                               (next (cond ((member name '("itemIdentity" "subjectLocator" "subjectIdentifier")
                                                    :test #'string=) 0)
                                           ((string= name "instanceOf") 1) (t 2))))
                          (when (< next phase) (reject :element-order "topic child order is invalid." child))
                          (when (= next 1)
                            (when instance-seen (reject :duplicate-instance-of "Only one instanceOf element is allowed." child))
                            (setf instance-seen t))
                          (setf phase next)
                          (validate child '("itemIdentity" "subjectLocator" "subjectIdentifier" "instanceOf" "name" "occurrence"))))))
                   ((string= name "instanceOf")
                    (attributes node nil nil)
                    (unless (elements node) (reject :empty-instance-of "instanceOf needs at least one topicRef." node))
                    (dolist (child (elements node)) (validate child '("topicRef"))))
                   ((string= name "name")
                    (attributes node '("reifier") nil)
                    (when (attr node "reifier")
                      (resolve-iri (attr node "reifier") *document-iri* node))
                    (let ((phase 0) (type-seen nil) (scope-seen nil) (value-seen nil))
                      (dolist (child (elements node))
                        (check-namespace child)
                        (let* ((kind (node-name child))
                               (next (position kind '("itemIdentity" "type" "scope" "value" "variant") :test #'string=)))
                          (unless next (reject :unexpected-element (format nil "Unexpected ~A element." kind) child))
                          (when (or (< next phase) (and (string= kind "variant") (not value-seen)))
                            (reject :element-order "name child order is invalid." child))
                          (setf phase next)
                          (cond
                            ((member kind '("itemIdentity" "variant") :test #'string=) nil)
                            ((string= kind "type")
                             (when type-seen (reject :duplicate-name-type "Only one name type is allowed." child))
                             (setf type-seen t))
                            ((string= kind "scope")
                             (when scope-seen (reject :duplicate-name-scope "Only one name scope is allowed." child))
                             (setf scope-seen t))
                            ((string= kind "value")
                             (when value-seen (reject :duplicate-name-value "Only one name value is allowed." child))
                             (setf value-seen t))
                            ;; Valid extension points remain explicitly unsupported.
                            ;; Their complete subgrammars are outside this subset.
                            (t (unsupported child)))
                          (validate child '("itemIdentity" "type" "scope" "value" "variant"))))
                      (unless value-seen (reject :missing-name-value "name requires a value element." node))))
                   ((string= name "variant")
                    (attributes node '("reifier") nil)
                    (when (attr node "reifier") (resolve-iri (attr node "reifier") *document-iri* node))
                    (let ((phase 0) (scope-seen nil) (resource-seen nil))
                      (dolist (child (elements node))
                        (check-namespace child)
                        (let* ((kind (node-name child))
                               (next (cond ((string= kind "itemIdentity") 0)
                                           ((string= kind "scope") 1)
                                           ((member kind '("resourceData" "resourceRef") :test #'string=) 2))))
                          (unless next (reject :unexpected-element (format nil "Unexpected ~A element." kind) child))
                          (when (< next phase) (reject :element-order "variant child order is invalid." child))
                          (setf phase next)
                          (cond
                            ((string= kind "itemIdentity") nil)
                            ((string= kind "scope")
                             (when scope-seen (reject :duplicate-variant-scope "Only one variant scope is allowed." child))
                             (setf scope-seen t))
                            (t
                             (unless scope-seen (reject :missing-variant-scope "variant requires scope before its resource." child))
                             (when resource-seen (reject :variant-resource-cardinality "variant requires exactly one resource." child))
                             (setf resource-seen t)))
                          (validate child '("itemIdentity" "scope" "resourceData" "resourceRef"))))
                      (unless scope-seen (reject :missing-variant-scope "variant requires a scope element." node))
                      (unless resource-seen (reject :missing-variant-resource "variant requires a resource element." node))))
                   ((string= name "occurrence")
                    (attributes node '("reifier") nil)
                    (when (attr node "reifier")
                      (resolve-iri (attr node "reifier") *document-iri* node))
                    (let ((phase 0) (type-seen nil) (scope-seen nil) (resource-seen nil))
                      (dolist (child (elements node))
                        (check-namespace child)
                        (let* ((kind (node-name child))
                               (next (cond ((string= kind "itemIdentity") 0)
                                           ((string= kind "type") 1)
                                           ((string= kind "scope") 2)
                                           ((member kind '("resourceData" "resourceRef") :test #'string=) 3))))
                          (unless next (reject :unexpected-element (format nil "Unexpected ~A element." kind) child))
                          (when (< next phase) (reject :element-order "occurrence child order is invalid." child))
                          (setf phase next)
                          (cond
                            ((string= kind "itemIdentity") nil)
                            ((string= kind "type")
                             (when type-seen (reject :duplicate-occurrence-type "Only one occurrence type is allowed." child))
                             (setf type-seen t))
                            ((string= kind "scope")
                             (unless type-seen (reject :missing-occurrence-type "occurrence requires type before scope." child))
                             (when scope-seen (reject :duplicate-occurrence-scope "Only one occurrence scope is allowed." child))
                             (setf scope-seen t))
                            (t
                             (unless type-seen (reject :missing-occurrence-type "occurrence requires type before its resource." child))
                             (when resource-seen (reject :occurrence-resource-cardinality "occurrence requires exactly one resource." child))
                             (setf resource-seen t)))
                          (validate child '("itemIdentity" "type" "scope" "resourceData" "resourceRef"))))
                      (unless type-seen (reject :missing-occurrence-type "occurrence requires a type element." node))
                      (unless resource-seen (reject :missing-occurrence-resource "occurrence requires a resource element." node))))
                   ((member name '("association" "role") :test #'string=)
                    (attributes node '("reifier") nil)
                    (when (attr node "reifier")
                      (resolve-iri (attr node "reifier") *document-iri* node))
                    (let ((association-p (string= name "association"))
                          (phase 0) (type-seen nil) (scope-seen nil) (participants 0))
                      (dolist (child (elements node))
                        (check-namespace child)
                        (let* ((kind (node-name child))
                               (next (cond ((string= kind "itemIdentity") 0)
                                           ((string= kind "type") 1)
                                           ((and association-p (string= kind "scope")) 2)
                                           ((string= kind (if association-p "role" "topicRef")) 3))))
                          (unless next (reject :unexpected-element (format nil "Unexpected ~A element." kind) child))
                          (when (< next phase) (reject :element-order (format nil "~A child order is invalid." name) child))
                          (setf phase next)
                          (cond
                            ((string= kind "itemIdentity") nil)
                            ((string= kind "type")
                             (when type-seen (reject :duplicate-type (format nil "Only one ~A type is allowed." name) child))
                             (setf type-seen t))
                            (t
                             (unless type-seen
                               (reject :missing-type (format nil "~A requires type before ~A." name kind) child))
                             (if (string= kind "scope")
                                 (progn
                                   (when scope-seen (reject :duplicate-scope "Only one association scope is allowed." child))
                                   (setf scope-seen t))
                                 (progn
                                   (incf participants)
                                   (when (and (not association-p) (> participants 1))
                                     (reject :role-player-cardinality "role requires exactly one topicRef player." child))))))
                          (validate child (if association-p '("itemIdentity" "type" "scope" "role") '("itemIdentity" "type" "topicRef")))))
                      (unless type-seen (reject :missing-type (format nil "~A requires a type element." name) node))
                      (when (zerop participants)
                        (reject (if association-p :missing-roles :missing-role-player)
                          (if association-p "association requires at least one role." "role requires a topicRef player.") node))))
                   ((string= name "resourceRef") (leaf-href node))
                   ((string= name "resourceData")
                    (attributes node '("datatype") nil)
                    (let ((datatype (attr node "datatype")))
                      ;; DATATYPE is already an absolute IRI, not content to
                      ;; resolve against the document or percent-normalize.
                      (when datatype
                        (unless (iri-parts-scheme (split-iri datatype))
                          (reject :invalid-resource-data-datatype "resourceData datatype must be an absolute IRI." node))
                        (validate-decoded-reference (unescape-reference datatype node) node)
                        (when (equal datatype "http://www.w3.org/2001/XMLSchema#anyType")
                          (reject :resource-data-datatype "xsd:anyType XML canonicalization is outside this subset." node 'xtm-unsupported)))
                      (dolist (child (node-children node))
                        (unless (stringp child)
                          (reject :unexpected-child "Textual resourceData cannot contain child elements." child)))))
                   ((string= name "type")
                    (attributes node nil nil)
                    (let ((refs (elements node)))
                      (unless (= 1 (length refs)) (reject :type-cardinality "type requires exactly one topicRef." node))
                      (validate (first refs) '("topicRef"))))
                   ((string= name "scope")
                    (attributes node nil nil)
                    (unless (elements node) (reject :empty-scope "scope requires at least one topicRef." node))
                    (dolist (child (elements node)) (validate child '("topicRef"))))
                   ((string= name "value")
                    (attributes node nil nil)
                    ;; VALUE accepts all character data, including empty text and
                    ;; whitespace. ELEMENTS would apply the wrong text policy.
                    (dolist (child (node-children node))
                      (unless (stringp child) (reject :unexpected-child "value accepts character data only." child))))
                   ((string= name "topicRef") (reference-iri node))
                   ((member name '("itemIdentity" "subjectIdentifier" "subjectLocator") :test #'string=)
                    (leaf-href node))
                   (t (unsupported node))))))
      (validate root '("topicMap"))))
  root)

(defun find-reference-topic (map iri)
  ;; XTM 4.20 searches the actual model, not a speculative pre-scan registry.
  ;; Unlike INTERN-TOPIC, a hit MUST NOT add another identifier category.
  (let ((topic (find-if (lambda (topic)
                          (or (member iri (topic-maps.tmdm:topic-subject-identifiers topic) :test #'string=)
                              (member iri (topic-maps.tmdm:topic-item-identifiers topic) :test #'string=)))
                        (topic-maps.tmdm:topic-map-topics map))))
    (if topic (topic-maps.tmdm:canonical-topic topic)
        (topic-maps.tmdm:intern-topic map :item-identifier iri))))
(defun read-item-reifier (node item map)
  ;; XTM 4.3.2 looks up Item Identifiers only, unlike topicRef (4.20).
  ;; INTERN-TOPIC adds the II on a miss; any SI/II identity merging then
  ;; follows the existing TMDM rules, independently of this lookup.
  (when (attr node "reifier")
    (let* ((iri (resolve-iri (attr node "reifier") *document-iri* node))
           (topic (or (find iri (topic-maps.tmdm:topic-map-topics map)
                        :test (lambda (iri topic)
                                (member iri (topic-maps.tmdm:topic-item-identifiers topic) :test #'string=)))
                      (topic-maps.tmdm:intern-topic map :item-identifier iri))))
      (return-from read-item-reifier (topic-maps.tmdm:set-item-reifier item topic))))
  item)
(defun read-map-reifier (node map)
  (read-item-reifier node map map))
(defun core-topic (map local)
  (topic-maps.tmdm:intern-topic map :subject-identifier
    (concatenate 'string "http://psi.topicmaps.org/iso13250/model/" local)))
(defun read-instance-of (node owner map)
  (dolist (ref (elements node))
    (let ((type (find-reference-topic map (reference-iri ref))))
      (topic-maps.tmdm:make-association map (core-topic map "type-instance")
        (list (list (core-topic map "type") type)
              (list (core-topic map "instance") (topic-maps.tmdm:canonical-topic owner)))))))
(defun read-item-identities (node item)
  ;; XTM 4.6: assign locators to the actual canonical item, never intern Topics.
  ;; ADD-ITEM-IDENTIFIER owns set semantics and cross-item conflict checks.
  (dolist (child (elements node) item)
    (when (string= (node-name child) "itemIdentity")
      (setf item (topic-maps.tmdm:add-item-identifier item (leaf-href child))))))
(defun read-association (node map)
  ;; Resolve references in source order, then construct the complete native
  ;; Association. The constructor may already merge Associations AND Roles.
  (let ((type nil) (scope nil) (roles nil) (role-nodes nil))
    (labels ((reference (ref) (find-reference-topic map (reference-iri ref)))
             (type-reference (node) (reference (first (elements node)))))
      (dolist (child (elements node))
        (cond ((string= (node-name child) "type") (setf type (type-reference child)))
              ((string= (node-name child) "scope") (setf scope (mapcar #'reference (elements child))))
              ((string= (node-name child) "role")
               (let ((children (elements child)))
                 (push (list (type-reference (find "type" children :key #'node-name :test #'string=))
                             (reference (find "topicRef" children :key #'node-name :test #'string=))) roles)
                 (push child role-nodes)))))
      (let ((association (read-item-identities node
                           (topic-maps.tmdm:make-association map type (reverse roles) :scope scope))))
        ;; Match source metadata to the native Role by its complete signature
        ;; within THIS canonical Parent. Role order/II are not equality keys.
        (loop for pair in (reverse roles) for source in (reverse role-nodes) do
          ;; A preceding Role Reifier may have merged Topics and this Parent.
          (setf association (topic-maps.tmdm:canonical-association association))
          (let ((role (find-if (lambda (role)
                        (and (eq (topic-maps.tmdm:association-role-type role)
                                 (topic-maps.tmdm:canonical-topic (first pair)))
                             (eq (topic-maps.tmdm:association-role-player role)
                                 (topic-maps.tmdm:canonical-topic (second pair)))))
                      (topic-maps.tmdm:association-roles association))))
            (setf role (read-item-identities source role))
            (read-item-reifier source (topic-maps.tmdm:canonical-association-role role) map)))
        ;; Role metadata is now on the native canonical Parent. Reifier merging
        ;; may normalize it again; return the resulting Association handle.
        (topic-maps.tmdm:canonical-association
          (read-item-reifier node association map))))))
(defun read-resource-value (resource)
  "Return value and datatype for a validated resource node (XTM 4.16/4.17).
This operation neither looks up Topics nor fetches resources. ANYTYPE is rejected
by source validation before model construction. Preserve other datatype IRIs."
  (if (string= (node-name resource) "resourceRef")
      (values (leaf-href resource) (topic-maps.tmdm:iri-datatype))
      (let ((datatype (or (attr resource "datatype") (topic-maps.tmdm:string-datatype)))
            (text (with-output-to-string (out)
                    (dolist (part (node-children resource)) (write-string part out)))))
        (values (if (equal datatype (topic-maps.tmdm:iri-datatype))
                    (resolve-iri text *document-iri* resource)
                    text)
                datatype))))
(defun read-variant (node name map)
  (let* ((children (elements node))
         (scope-node (find "scope" children :key #'node-name :test #'string=))
         (resource (find-if (lambda (child) (member (node-name child) '("resourceData" "resourceRef") :test #'string=)) children))
         (explicit (mapcar (lambda (ref) (find-reference-topic map (reference-iri ref))) (elements scope-node))))
    (multiple-value-bind (value datatype) (read-resource-value resource)
      ;; ADD-VARIANT owns canonicalization and the proper-superset constraint.
      (let ((variant (topic-maps.tmdm:add-variant name value :datatype datatype
                       :scope (append (topic-maps.tmdm:topic-name-scope name) explicit))))
        (setf variant (read-item-identities node variant))
        ;; Reification may normalize again; retain the native canonical handle.
        (topic-maps.tmdm:canonical-variant (read-item-reifier node variant map))))))
(defun read-name (node owner map)
  (let* ((children (elements node))
         (type-node (find "type" children :key #'node-name :test #'string=))
         (scope-node (find "scope" children :key #'node-name :test #'string=))
         (type (when type-node (find-reference-topic map (reference-iri (first (elements type-node))))))
         (scope (when scope-node (mapcar (lambda (ref) (find-reference-topic map (reference-iri ref)))
                                        (elements scope-node))))
         (value-node (find "value" children :key #'node-name :test #'string=))
         (value (with-output-to-string (out)
                  (dolist (part (node-children value-node)) (write-string part out)))))
    ;; SAX has already resolved XML character/entity references. Preserve the
    ;; resulting Unicode sequence without trimming or decoding it again.
    ;; ADD-NAME owns canonical set semantics and normalization after merging.
    (let ((name (if type-node
                    (topic-maps.tmdm:add-name owner value :type type :scope scope)
                    (topic-maps.tmdm:add-default-name owner value :scope scope))))
      ;; Item identifiers belong to the canonical Name, never its owner/type.
      ;; Use the shared model API for set semantics and global conflicts.
      (setf name (read-item-identities node name))
      ;; ADD-NAME may have returned an existing canonical Name. Reifier
      ;; resolution/merging can normalize it again: retain the native result
      ;; before processing Variants and return the current Name handle.
      (setf name (read-item-reifier node name map))
      (dolist (child children)
        (when (string= (node-name child) "variant") (read-variant child name map)))
      (topic-maps.tmdm:canonical-topic-name name))))
(defun read-occurrence (node owner map)
  ;; XTM 4.13-4.17/4.20: reuse native Topics and the qualified resource path.
  ;; ADD-OCCURRENCE owns live Parent/Type/Scope handles and TMDM 5.6/6.5 merging.
  (let* ((children (elements node))
         (type-node (find "type" children :key #'node-name :test #'string=))
         (type (find-reference-topic map (reference-iri (first (elements type-node)))))
         (scope-node (find "scope" children :key #'node-name :test #'string=))
         (scope (when scope-node (mapcar (lambda (ref) (find-reference-topic map (reference-iri ref)))
                                        (elements scope-node))))
         (resource (find-if (lambda (child) (member (node-name child) '("resourceData" "resourceRef") :test #'string=)) children)))
    (multiple-value-bind (value datatype) (read-resource-value resource)
      (topic-maps.tmdm:canonical-occurrence
        ;; Resolve Reifier by II only after native Occurrence normalization and
        ;; II assignment. Reifier merging can normalize again: return its handle.
        (read-item-reifier node
          (read-item-identities node
            (topic-maps.tmdm:add-occurrence owner type value :datatype datatype :scope scope)) map)))))
(defun read-topic (node map)
  (let ((topic (topic-maps.tmdm:intern-topic map :item-identifier
                 (concatenate 'string *document-iri* "#" (collapse-space (attr node "id"))))))
    (dolist (child (elements node))
      (let ((name (node-name child)))
        (cond
          ((string= name "instanceOf") (read-instance-of child topic map))
          ((string= name "name") (read-name child topic map))
          ((string= name "occurrence") (read-occurrence child topic map))
          (t (setf topic (topic-maps.tmdm:add-topic-identifier topic
                           (cond ((string= name "itemIdentity") :item-identifier)
                                 ((string= name "subjectIdentifier") :subject-identifier)
                                 (t :subject-locator))
                           (leaf-href child)))))))
    (topic-maps.tmdm:canonical-topic topic)))
(defun mergemap-iri (node)
  (let ((iri (leaf-href node)))
    (when (iri-parts-fragment (split-iri iri))
      (reject :mergemap-fragment "mergeMap href must not have a fragment identifier." node))
    iri))
(defun resource-failure (code detail node &optional cause)
  (error 'xtm-resource-error :code code :detail detail :cause cause
    :document-iri *document-iri* :source-key *source-key*
    :line (node-line node) :column (node-column node)))
(defun resource-octets-p (value)
  ;; Same resolver value convention as CTM, without a dependency on its Reader.
  (and (vectorp value) (not (stringp value))
    (every (lambda (n) (and (integerp n) (<= 0 n 255))) value)))
(defun read-mergemap (node map resolver max-depth active-iris)
  (let ((resource (mergemap-iri node)))
    (unless resolver
      (reject :resource-resolver-required "mergeMap requires an explicit resource resolver; no resource was loaded." node 'xtm-unsupported))
    ;; These are finite resource-policy guards, not normative cycle semantics.
    ;; Each independent public call starts a new active path; siblings may repeat.
    (when (member resource active-iris :test #'string=)
      (reject :cyclic-mergemap "Active recursive XTM resource dependency; cycle processing is not implemented." node 'xtm-unsupported))
    (when (>= (length active-iris) (1+ max-depth))
      (reject :resource-depth-limit "Configured nested XTM resource limit reached; this is implementation policy." node 'xtm-unsupported))
    (multiple-value-bind (bytes source-key)
        (handler-case
            (funcall resolver resource :purpose :mergemap :from-document-iri *document-iri*
              :notation "http://psi.topicmaps.org/iso13250/xtm")
          (error (c) (resource-failure :resource-resolver-failure (princ-to-string c) node c)))
      (unless bytes
        (resource-failure :resource-unavailable "Resolver declined or did not supply the requested XTM resource." node))
      (unless (and (resource-octets-p bytes) (or (null source-key) (stringp source-key)))
        (resource-failure :invalid-resource-result "Resolver must return an octet vector and a string source key or NIL." node))
      (let ((source (deserialize-document
                      (if (typep bytes '(vector (unsigned-byte 8))) bytes
                          (map '(vector (unsigned-byte 8)) #'identity bytes))
                      resource (or source-key resource) resolver max-depth active-iris)))
        ;; Import only Topics/Associations. The existing operation preflights
        ;; conflicts, preserves SOURCE, and excludes its Map identifiers/reifier.
        (handler-case (topic-maps.tmdm:import-map-content map source)
          (error (c) (resource-failure :mergemap-import-failure (princ-to-string c) node c)))))))
(defun deserialize-octets (bytes &key document-iri source-key resource-resolver (max-resource-depth 32))
  "Deserialize raw XTM 2.0 octets into a fresh TMDM Map.
DOCUMENT-IRI is required, absolute and fragment-free. SOURCE-KEY is diagnostic.
RESOURCE-RESOLVER is optional: (resolver absolute-iri :purpose :mergemap
 :from-document-iri parent-iri :notation XTM-notation-IRI)
returns raw octets and an optional diagnostic source key. No implicit I/O.
Children use their resolved IRI as Document IRI and the same explicit resolver.
MAX-RESOURCE-DEPTH bounds nested imports (default 32); active cycles are
Unsupported implementation policy, not a normative XTM invalidity decision.
Child XML/XTM/model errors retain their original contexts; resolver/import
failures use XTM-RESOURCE-ERROR with the original ERROR-CAUSE. No supplied Map
is mutated. Each public call has its own resource recursion context."
  (check-type max-resource-depth (integer 0 *))
  (deserialize-document bytes document-iri source-key resource-resolver max-resource-depth nil))
(defun deserialize-document (bytes document-iri source-key resource-resolver max-resource-depth active-iris)
  (check-type bytes (vector (unsigned-byte 8)))
  (let ((*document-iri* document-iri) (*source-key* source-key)
        (handler (make-instance 'source-handler)))
    (require-document-iri document-iri)
    (let* ((root
             (handler-case (topic-maps.xml:parse-octets bytes handler)
               (cxml:well-formedness-violation (c)
                 (error 'xtm-xml-error :code :xml-not-well-formed :cause c
                        :detail (princ-to-string c) :document-iri document-iri :source-key source-key
                        :line (sax:line-number handler) :column (sax:column-number handler)))
               (topic-maps.xml:doctype-forbidden (c)
                 (error 'xtm-xml-error :code :doctype-forbidden :cause c
                        :detail "DOCTYPE forbidden by the mandatory XML byte boundary."
                        :document-iri document-iri :source-key source-key
                        :line (sax:line-number handler) :column (sax:column-number handler)))))
           (map (topic-maps.tmdm:make-topic-map)))
      (validate-source root)
      ;; The attribute is processed before itemIdentity and later Topic nodes.
      (read-map-reifier root map)
      (dolist (child (elements root))
        (cond ((string= (node-name child) "itemIdentity")
               (topic-maps.tmdm:add-item-identifier map (leaf-href child)))
              ((string= (node-name child) "mergeMap")
               (read-mergemap child map resource-resolver max-resource-depth
                 (cons document-iri active-iris)))
              ((string= (node-name child) "association") (read-association child map))
              (t (read-topic child map))))
      map)))
