(in-package #:topic-maps.tmdm)

;;; Only the information-item properties used by Slice 1 are materialized.
;;; Omitted set-valued properties are implicitly empty, single-valued ones null
;;; (CTM 3.2). In particular all supported names have empty scope and variants.
(defstruct topic-map topics)
(defstruct (topic (:constructor %make-topic (parent)))
  (parent nil :read-only t) item-identifiers subject-identifiers subject-locators names)
(defstruct (topic-name (:constructor %make-topic-name (value type parent)))
  (value "" :type string :read-only t)
  (type nil :type topic :read-only t)
  (parent nil :type topic :read-only t))

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

(defun identifiers (topic kind)
  (ecase kind
    (:item-identifier (topic-item-identifiers topic))
    (:subject-identifier (topic-subject-identifiers topic))
    (:subject-locator (topic-subject-locators topic))))

(defun intern-topic (map kind iri)
  "Within one map, reuse an equal identity reference (TMDM 5.3.5).
This restricted interning does not implement general merge or cross-map merge."
  (unless (and (typep map 'topic-map) (stringp iri) (plusp (length iri)))
    (error "A map and a nonempty locator string are required."))
  (let* ((kinds (ecase kind
                  ((:item-identifier :subject-identifier)
                   '(:item-identifier :subject-identifier))
                  (:subject-locator '(:subject-locator))))
         (existing
           (find-if (lambda (topic)
                      (some (lambda (property)
                              (member iri (identifiers topic property) :test #'string=))
                            kinds))
                    (topic-map-topics map)))
         (topic (or existing (%make-topic map))))
    (unless existing
      ;; Private storage mutation: list order is observational, not TMDM semantics.
      (setf (topic-map-topics map) (append (topic-map-topics map) (list topic))))
    (ecase kind
      (:item-identifier (pushnew iri (topic-item-identifiers topic) :test #'string=))
      (:subject-identifier (pushnew iri (topic-subject-identifiers topic) :test #'string=))
      (:subject-locator (pushnew iri (topic-subject-locators topic) :test #'string=)))
    topic))

(defun default-name-type-identifier ()
  "http://psi.topicmaps.org/iso13250/model/topic-name")

(defun add-default-name (topic value)
  "CTM 3.11 default type; unscoped name equality per TMDM 5.4."
  (check-type topic topic)
  (check-type value string)
  (let* ((type (intern-topic (topic-parent topic) :subject-identifier
                            (default-name-type-identifier)))
         (existing (find-if (lambda (name)
                              (and (string= value (topic-name-value name))
                                   (eq type (topic-name-type name))))
                            (topic-names topic))))
    (or existing
        (let ((name (%make-topic-name value type topic)))
          (setf (topic-names topic) (append (topic-names topic) (list name)))
          name))))
