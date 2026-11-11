(in-package #:topic-maps.tmdm)

;;; Readers for the two relationships of TMDM 2006, 7.2 and 7.3.
;;; They recognize the structure those clauses define and report it; they are added API, not a repair.
;;; They read stored items only: no Topic is interned, nothing is merged, cached or inferred, and Scope
;;; is not evaluated. An Association that uses the Core Subject Identifiers without conforming to the
;;; structural rules is, in the words of both clauses, not considered to represent the relationship.

(defun core-locator (local)
  (concatenate 'string "http://psi.topicmaps.org/iso13250/model/" local))

(defun has-subject-identifier-p (topic iri)
  ;; The clauses name the [subject identifiers] property; an equal Item Identifier or Subject Locator
  ;; does not count.
  (member iri (%topic-subject-identifiers (canonical-topic topic)) :test #'string=))

(defun core-relationship-players (association type first-role second-role)
  "The players of FIRST-ROLE and SECOND-ROLE when ASSOCIATION conforms to the structural rules shared by
TMDM 7.2 and 7.3 for the Core Subject locals TYPE, FIRST-ROLE and SECOND-ROLE; otherwise NIL and NIL."
  (check-type association association)
  (let* ((association (canonical-association association)) (roles (%association-roles association)))
    (if (and (has-subject-identifier-p (%association-type association) (core-locator type))
             (= 2 (length roles)))
        (flet ((role-of (local)
                 (find-if (lambda (role) (has-subject-identifier-p (%association-role-type role) (core-locator local)))
                          roles)))
          (let ((first (role-of first-role)) (second (role-of second-role)))
            (if (and first second (not (eq first second)))
                (values (canonical-topic (%association-role-player first))
                        (canonical-topic (%association-role-player second)))
                (values nil nil))))
        (values nil nil))))

(defun type-instance-relationship (association)
  "TMDM 7.2. Return (values TYPE INSTANCE), the two player Topics, when ASSOCIATION represents a
type-instance relationship: its type has the Subject Identifier .../type-instance, it has exactly two
Roles, one whose type has .../type and one whose type has .../instance. Otherwise (values NIL NIL).
The Association keeps its Scope; this reader does not interpret it."
  (core-relationship-players association "type-instance" "type" "instance"))

(defun supertype-subtype-relationship (association)
  "TMDM 7.3. Return (values SUPERTYPE SUBTYPE), the two player Topics, when ASSOCIATION represents a
supertype-subtype relationship: its type has the Subject Identifier .../supertype-subtype, it has exactly
two Roles, one whose type has .../supertype and one whose type has .../subtype. Otherwise (values NIL NIL).
Only this stated relationship is reported; transitive consequences are not computed."
  (core-relationship-players association "supertype-subtype" "supertype" "subtype"))

(defun relationships-played (topic reader position)
  ;; Computed from the Roles the Topic plays (TMDM 5.3.5); no index is kept.
  (let ((topic (canonical-topic topic)) (found nil))
    (dolist (role (topic-roles-played topic) (nreverse found))
      (let ((association (canonical-association (%association-role-parent role))))
        (unless (member association found :test #'eq)
          (multiple-value-bind (first second) (funcall reader association)
            (when (eq topic (ecase position (:first first) (:second second)))
              (push association found))))))))

(defun topic-type-associations (topic)
  "The Associations that state a type of TOPIC: TMDM 7.2 relationships in which TOPIC is the instance."
  (relationships-played topic #'type-instance-relationship :second))
(defun topic-instance-associations (topic)
  "The Associations that state an instance of TOPIC: TMDM 7.2 relationships in which TOPIC is the type."
  (relationships-played topic #'type-instance-relationship :first))
(defun topic-supertype-associations (topic)
  "The Associations that state a supertype of TOPIC: TMDM 7.3 relationships in which TOPIC is the subtype."
  (relationships-played topic #'supertype-subtype-relationship :second))
(defun topic-subtype-associations (topic)
  "The Associations that state a subtype of TOPIC: TMDM 7.3 relationships in which TOPIC is the supertype."
  (relationships-played topic #'supertype-subtype-relationship :first))
