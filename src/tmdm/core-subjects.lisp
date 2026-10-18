(in-package #:topic-maps.tmdm)

;; TMDM 2006, 7.1-7.5. These are locator constants, not a second Topic registry.
;; In particular 7.5's NAME-TYPE is not silently equated to CTM 3.11's
;; TOPIC-NAME locator; the existing CTM default-name mapping is unchanged.
(defparameter *core-subject-identifiers*
  (mapcar (lambda (local) (concatenate 'string "http://psi.topicmaps.org/iso13250/model/" local))
          '("type-instance" "type" "instance" "supertype-subtype" "supertype" "subtype" "sort" "name-type")))

(defun core-subject-identifiers ()
  "Return fresh locator strings for the eight Core Subjects of TMDM 2006, 7."
  (mapcar #'copy-seq *core-subject-identifiers*))
(define-condition core-subject-error (error)
  ((code :initarg :code :reader core-subject-error-code)
   (detail :initarg :detail :reader core-subject-error-detail))
  (:report (lambda (c out) (format out "Core Subject ~A: ~A" (core-subject-error-code c)
                                  (core-subject-error-detail c)))))
(defun check-core-subject-identifiers (identifiers)
  (let ((core (remove-duplicates
                (intersection identifiers *core-subject-identifiers* :test #'string=) :test #'string=)))
    (when (rest core)
      (error 'core-subject-error :code :core-subject-conflict
             :detail (format nil "TMDM 7.1: distinct Core Subjects cannot share a Topic: ~{~A~^, ~}." core))))
  t)
(defun map-has-core-subject-p (map)
  (some (lambda (topic) (intersection (%topic-subject-identifiers topic) *core-subject-identifiers* :test #'string=))
        (%topic-map-topics map)))
(defun validate-map-core-subjects (map)
  "Check stored Subject Identifiers without merging or mutating any item."
  (dolist (topic (%topic-map-topics map)) (check-core-subject-identifiers (%topic-subject-identifiers topic)))
  t)
