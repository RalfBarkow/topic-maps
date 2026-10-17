(in-package #:topic-maps.tmdm)

;;; Only Topic Map, Topic, Name/Occurrence, Association and Role properties used
;;; by the current subset are materialized.
;;; Omitted set-valued properties are implicitly empty, single-valued ones null
;;; (CTM 3.2). Scope is a materialized Topic set; Variants belong to Names.
(defstruct (topic-map (:constructor make-topic-map ()) (:conc-name %topic-map-)) topics associations)
(defstruct (topic (:constructor %make-topic (parent)) (:conc-name %topic-))
  (parent nil :read-only t) item-identifiers subject-identifiers subject-locators names occurrences
  ;; Implementation bookkeeping, not a TMDM property or another information item.
  forward)

(defstruct (association (:constructor %make-association (parent type)) (:conc-name %association-))
  (parent nil :type topic-map :read-only t) (type nil :type topic) roles scope forward)
(defstruct (association-role (:constructor %make-association-role (parent type player))
                            (:conc-name %association-role-))
  (parent nil :type association) (type nil :type topic) (player nil :type topic) forward)
(defstruct (topic-name (:constructor %make-topic-name (value type parent)) (:conc-name %topic-name-))
  (value "" :type string :read-only t)
  (type nil :type topic)
  (parent nil :type topic)
  scope variants forward)

(defstruct (variant (:constructor %make-variant (value datatype parent)) (:conc-name %variant-))
  (value "" :type string :read-only t) (datatype "" :type string :read-only t)
  (parent nil :type topic-name) scope forward)

(defstruct (occurrence (:constructor %make-occurrence (value datatype type parent))
                       (:conc-name %occurrence-))
  (value "" :type string :read-only t) (datatype "" :type string :read-only t)
  (type nil :type topic) (parent nil :type topic) item-identifiers scope forward)

(defun canonical-occurrence (occurrence)
  "Resolve a retained Occurrence replaced by TMDM duplicate removal; no compression."
  (check-type occurrence occurrence)
  (loop for current = occurrence then (%occurrence-forward current)
        unless (%occurrence-forward current) return current))
(defun string-datatype () "http://www.w3.org/2001/XMLSchema#string")
(defun iri-datatype () "http://www.w3.org/2001/XMLSchema#anyURI")

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

(defun canonical-variant (item)
  "Resolve a retained Variant replaced by duplicate removal, without mutation."
  (check-type item variant)
  (loop for current = item then (%variant-forward current)
        unless (%variant-forward current) return current))
(defun topic-name-variants (name) (copy-list (%topic-name-variants (canonical-topic-name name))))
(defun variant-value (item) (%variant-value (canonical-variant item)))
(defun variant-datatype (item) (%variant-datatype (canonical-variant item)))
(defun variant-parent (item) (%variant-parent (canonical-variant item)))
(defun variant-scope (item) (copy-list (%variant-scope (canonical-variant item))))
(defun variant-item-identifiers (item)
  "Item identifiers are implicitly empty in the supported unreified Variant subset."
  (canonical-variant item) nil)

(defun canonical-association (association)
  "Resolve a retained Association handle after duplicate association merging."
  (check-type association association)
  (loop for current = association then (%association-forward current)
        unless (%association-forward current) return current))
(defun canonical-association-role (role)
  "Resolve a retained Role handle after role/association duplicate removal."
  (check-type role association-role)
  (loop for current = role then (%association-role-forward current)
        unless (%association-role-forward current) return current))

;; Public readers resolve obsolete handles and expose copies of set storage.
;; Mutations must use the identity/merge API to maintain model invariants.
(defun topic-map-topics (map) (copy-list (%topic-map-topics map)))
(defun topic-map-associations (map) (copy-list (%topic-map-associations map)))
(defun topic-parent (topic) (%topic-parent (canonical-topic topic)))
(defun topic-item-identifiers (topic) (copy-list (%topic-item-identifiers (canonical-topic topic))))
(defun topic-subject-identifiers (topic) (copy-list (%topic-subject-identifiers (canonical-topic topic))))
(defun topic-subject-locators (topic) (copy-list (%topic-subject-locators (canonical-topic topic))))
(defun topic-names (topic) (copy-list (%topic-names (canonical-topic topic))))
(defun topic-occurrences (topic) (copy-list (%topic-occurrences (canonical-topic topic))))
(defun occurrence-value (item) (%occurrence-value (canonical-occurrence item)))
(defun occurrence-datatype (item) (%occurrence-datatype (canonical-occurrence item)))
(defun occurrence-parent (item) (%occurrence-parent (canonical-occurrence item)))
(defun occurrence-type (item) (%occurrence-type (canonical-occurrence item)))
(defun occurrence-item-identifiers (item) (copy-list (%occurrence-item-identifiers (canonical-occurrence item))))
(defun topic-name-value (name) (%topic-name-value (canonical-topic-name name)))
(defun topic-name-type (name) (%topic-name-type (canonical-topic-name name)))
(defun topic-name-scope (name) (copy-list (%topic-name-scope (canonical-topic-name name))))
(defun occurrence-scope (item) (copy-list (%occurrence-scope (canonical-occurrence item))))
(defun association-scope (item) (copy-list (%association-scope (canonical-association item))))
(defun topic-name-parent (name) (%topic-name-parent (canonical-topic-name name)))
(defun association-parent (association) (%association-parent (canonical-association association)))
(defun association-type (association) (%association-type (canonical-association association)))
(defun association-roles (association) (copy-list (%association-roles (canonical-association association))))
(defun association-role-parent (role) (%association-role-parent (canonical-association-role role)))
(defun association-role-type (role) (%association-role-type (canonical-association-role role)))
(defun association-role-player (role) (%association-role-player (canonical-association-role role)))
(defun topic-roles-played (topic)
  "Computed TMDM 5.3.5 property; no independently maintained inverse index."
  (let ((topic (canonical-topic topic)))
    (loop for association in (%topic-map-associations (%topic-parent topic)) append
      (remove-if-not (lambda (role) (eq topic (%association-role-player role)))
                     (%association-roles association)))))

;; Avoid recursive printing through parent/type links; DESCRIBE remains useful.
(defmethod print-object ((item topic-map) stream)
  (print-unreadable-object (item stream :type t :identity t)
    (format stream "~D topics, ~D associations" (length (topic-map-topics item))
            (length (topic-map-associations item)))))
(defmethod print-object ((item topic) stream)
  (print-unreadable-object (item stream :type t :identity t)
    (format stream "II=~S SI=~S SL=~S" (topic-item-identifiers item)
            (topic-subject-identifiers item) (topic-subject-locators item))))
(defmethod print-object ((item topic-name) stream)
  (print-unreadable-object (item stream :type t :identity t)
    (format stream "~S" (topic-name-value item))))
(defmethod print-object ((item variant) stream)
  (print-unreadable-object (item stream :type t :identity t)
    (format stream "~S datatype=~S" (variant-value item) (variant-datatype item))))
(defmethod print-object ((item association) stream)
  (print-unreadable-object (item stream :type t :identity t)
    (format stream "~D roles" (length (association-roles item)))))
(defmethod print-object ((item association-role) stream)
  (print-unreadable-object (item stream :type t :identity t)))

(defun default-name-type-identifier ()
  "http://psi.topicmaps.org/iso13250/model/topic-name")

(defmethod print-object ((item occurrence) stream)
  (print-unreadable-object (item stream :type t :identity t)
    (format stream "~S datatype=~S" (occurrence-value item) (occurrence-datatype item))))
