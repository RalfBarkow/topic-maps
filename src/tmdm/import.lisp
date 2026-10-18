(in-package #:topic-maps.tmdm)

(define-condition map-import-error (error)
  ((code :initarg :code :reader map-import-error-code)
   (detail :initarg :detail :reader map-import-error-detail))
  (:report (lambda (condition out)
             (format out "Map content import ~A: ~A" (map-import-error-code condition)
                     (map-import-error-detail condition)))))
(defun import-problem (code detail)
  (error 'map-import-error :code code :detail detail))

(defun validate-import-map (map)
  "Check the current graph, without repairing or modifying caller objects.
Public model operations maintain these invariants; raw structure-slot edits are
not an alternative import API. Semantic condition classes remain unchanged."
  (let ((items (map-information-items map)) (topics (%topic-map-topics map)))
    (labels ((ref (item)
               (unless (and (eq item (canonical-item item))
                            (member item items :test #'eq) (eq map (item-topic-map item)))
                 (import-problem :invalid-reference "Expected a current same-map information item.")))
             (topic-ref (topic)
               (unless (and (typep topic 'topic) (member topic topics :test #'eq))
                 (import-problem :invalid-reference "Expected a current same-map Topic."))
               (ref topic))
             (scope (themes)
               (unless (and (proper-list-p themes)
                            (= (length themes) (length (remove-duplicates themes :test #'eq))))
                 (import-problem :invalid-scope "Scope must be a set of current Topic references."))
               (mapc #'topic-ref themes)))
      (unless (= (length items) (length (remove-duplicates items :test #'eq)))
        (import-problem :invalid-reference "An information item occurs in multiple collections."))
      (dolist (item items)
        (ref item)
        (typecase item
          (topic
           (unless (or (%topic-item-identifiers item) (%topic-subject-identifiers item)
                       (%topic-subject-locators item))
             (import-problem :unidentified-topic "TMDM 5.3.5 requires a Topic identifier."))
           (dolist (name (%topic-names item))
             (unless (eq item (%topic-name-parent name))
               (import-problem :invalid-reference "Name Parent differs from its containing Topic.")))
           (dolist (occurrence (%topic-occurrences item))
             (unless (eq item (%occurrence-parent occurrence))
               (import-problem :invalid-reference "Occurrence Parent differs from its containing Topic."))))
          (topic-name
           (topic-ref (%topic-name-type item)) (scope (%topic-name-scope item))
           (dolist (variant (%topic-name-variants item))
             (unless (eq item (%variant-parent variant))
               (import-problem :invalid-reference "Variant Parent differs from its containing Name."))))
          (variant (scope (%variant-scope item)))
          (occurrence (topic-ref (%occurrence-type item)) (scope (%occurrence-scope item)))
          (association
           (topic-ref (%association-type item)) (scope (%association-scope item))
           (unless (%association-roles item)
             (import-problem :invalid-reference "Association must have Roles."))
           (dolist (role (%association-roles item))
             (unless (eq item (%association-role-parent role))
               (import-problem :invalid-reference "Role Parent differs from its containing Association."))))
          (association-role (topic-ref (%association-role-type item))
                            (topic-ref (%association-role-player item)))))))
  (validate-map-item-identifiers map)
  (validate-map-core-subjects map)
  (validate-map-reification map)
  (check-variant-merge-constraints map)
  map)

(defun import-content-into (target source)
  ;; Only called after validation, or on a disposable preflight graph. The copy
  ;; table rewrites references, never decides subject identity. Normalization
  ;; uses the ordinary same-map TMDM merging operations on the completed graph.
  (multiple-value-bind (map ref copies) (copy-map-graph source target :map-item-p nil)
    (declare (ignore ref))
    (normalize-topic-map map)
    (validate-import-map map)
    copies))

(defun import-map-content (target source)
  "Copy SOURCE's Topics, Associations and their children into TARGET.
Return (values TARGET RESOLVE), where (funcall RESOLVE SOURCE-ITEM) returns its
current canonical target representative, including after later target merges.
The mapping describes this import's source snapshot: known old source objects
remain resolvable; new source content is not imported automatically. Retained
source aliases may resolve through a snapshot representative. SOURCE itself,
foreign objects and unimported objects signal MAP-IMPORT-ERROR :NOT-IMPORTED.

Both arguments must be different valid Topic Maps. Their root items are not
merged: SOURCE's map identifiers and map reifier are not copied to TARGET.
SOURCE's objects, forward links and strings are never changed or shared with
new copies. Existing target items may merge, preserving canonical handles.
All semantic rejection is preflighted on a disposable copy of TARGET using
the same TMDM structures/normalization; resource exhaustion and concurrent
external mutation are outside this single-threaded API guarantee."
  (check-type target topic-map) (check-type source topic-map)
  (when (eq target source)
    (import-problem :same-map "Source and target must be different Topic Maps."))
  (validate-import-map target) (validate-import-map source)
  (let ((*merge-mutation-active* t))
    ;; Unconditional preflight is needed even when neither input currently has
    ;; Reifiers/Core Subjects: the combined graph may create identifier conflicts.
    (import-content-into (copy-map-for-preflight target) source)
    (let ((copies (import-content-into target source)))
      (remhash source copies)
      (values target
              (lambda (item)
                (let ((copy (or (gethash item copies)
                                (and (typep item '(or topic topic-name variant occurrence association association-role))
                                     (gethash (canonical-item item) copies)))))
                  (unless copy
                    (import-problem :not-imported "Object is not content of this import's source snapshot."))
                  (canonical-item copy)))))))
