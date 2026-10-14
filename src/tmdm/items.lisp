(in-package #:topic-maps.tmdm)

;;; Only Topic Map, Topic and unscoped Name properties are materialized.
;;; Omitted set-valued properties are implicitly empty, single-valued ones null
;;; (CTM 3.2). In particular all supported names have empty scope and variants.
(defstruct (topic-map (:constructor make-topic-map ()) (:conc-name %topic-map-)) topics)
(defstruct (topic (:constructor %make-topic (parent)) (:conc-name %topic-))
  (parent nil :read-only t) item-identifiers subject-identifiers subject-locators names
  ;; Implementation bookkeeping, not a TMDM property or another information item.
  forward)
(defstruct (topic-name (:constructor %make-topic-name (value type parent)) (:conc-name %topic-name-))
  (value "" :type string :read-only t)
  (type nil :type topic)
  (parent nil :type topic)
  forward)

(defun canonical-topic (topic)
  "Resolve a retained reference to a Topic replaced by same-map merging.
EQ on obsolete objects does not change; compare their canonical representatives."
  (check-type topic topic)
  (loop for current = topic then (%topic-forward current)
        unless (%topic-forward current) return current))
(defun canonical-topic-name (name)
  "Resolve a retained reference to a Name replaced during duplicate removal."
  (check-type name topic-name)
  (loop for current = name then (%topic-name-forward current)
        unless (%topic-name-forward current) return current))

;; Public readers resolve obsolete handles and expose copies of set storage.
;; Mutations must use the identity/merge API to maintain model invariants.
(defun topic-map-topics (map) (copy-list (%topic-map-topics map)))
(defun topic-parent (topic) (%topic-parent (canonical-topic topic)))
(defun topic-item-identifiers (topic) (copy-list (%topic-item-identifiers (canonical-topic topic))))
(defun topic-subject-identifiers (topic) (copy-list (%topic-subject-identifiers (canonical-topic topic))))
(defun topic-subject-locators (topic) (copy-list (%topic-subject-locators (canonical-topic topic))))
(defun topic-names (topic) (copy-list (%topic-names (canonical-topic topic))))
(defun topic-name-value (name) (%topic-name-value (canonical-topic-name name)))
(defun topic-name-type (name) (%topic-name-type (canonical-topic-name name)))
(defun topic-name-parent (name) (%topic-name-parent (canonical-topic-name name)))

;; Avoid recursive printing through parent/type links; DESCRIBE remains useful.
(defmethod print-object ((item topic-map) stream)
  (print-unreadable-object (item stream :type t :identity t)
    (format stream "~D topics" (length (topic-map-topics item)))))
(defmethod print-object ((item topic) stream)
  (print-unreadable-object (item stream :type t :identity t)
    (format stream "II=~S SI=~S SL=~S" (topic-item-identifiers item)
            (topic-subject-identifiers item) (topic-subject-locators item))))
(defmethod print-object ((item topic-name) stream)
  (print-unreadable-object (item stream :type t :identity t)
    (format stream "~S" (topic-name-value item))))

(defun default-name-type-identifier ()
  "http://psi.topicmaps.org/iso13250/model/topic-name")
