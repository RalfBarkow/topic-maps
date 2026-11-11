(defpackage #:topic-maps.core-relationship.tests
  (:use #:cl #:topic-maps.tmdm)
  (:import-from #:topic-maps.ctm.tests #:check)
  (:export #:run-tests #:core-relationship-checks #:write-report))
(in-package #:topic-maps.core-relationship.tests)

;;; Readers for TMDM 2006, 7.2 (type-instance) and 7.3 (supertype-subtype).
;;; Each expectation is argued from the clause named in its label or comment. The readers are added
;;; API over stored items; these tests also show that they change nothing and infer nothing.

(defvar *last-checks* nil)
(defvar *original-observations* nil)
(defun core-relationship-checks () *last-checks*)
(defparameter +document+ "https://example.invalid/a/doc.ctm")
(defparameter +originals+
  '("isa-relationship" "isa-relationship-duplicate" "isa-relationship-duplicate2"
    "isa-relationship-embedded" "isa-relationship-type-qname"
    "ako-relationship" "ako-relationship-duplicate" "ako-relationship-duplicate2"
    "ako-relationship-embedded" "ako-relationship-supertype-qname" "ako-merge-away"))

(defun core-iri (local) (concatenate 'string "http://psi.topicmaps.org/iso13250/model/" local))
(defun core (map local) (intern-topic map :subject-identifier (core-iri local)))
(defun plain (map name) (intern-topic map :subject-identifier (concatenate 'string "urn:test:" name)))
(defun read-ctm (text)
  (topic-maps.ctm:deserialize-string text :document-iri +document+ :source-name "core-relationships"))
(defun cxtm (map) (topic-maps.cxtm:canonicalize map :base-locator +document+))
(defun local (map id)
  (find-if (lambda (topic) (member (format nil "~A#~A" +document+ id) (topic-item-identifiers topic) :test #'string=))
           (topic-map-topics map)))
(defun pair (reader association) (multiple-value-list (funcall reader association)))
(defun only (list) (and list (null (rest list)) (first list)))
(defun same-set-p (a b) (null (set-exclusive-or a b :test #'eq)))
(defun counts (map)
  (list (count-if #'type-instance-relationship (topic-map-associations map))
        (count-if #'supertype-subtype-relationship (topic-map-associations map))))

(defun positive-tests ()
  ;; 7.2: type .../type-instance, exactly two Roles, one of type .../type, one of type .../instance.
  (let* ((map (read-ctm "a isa b.")) (a (local map "a")) (b (local map "b"))
         (association (only (topic-map-associations map))))
    (check "7.2:isa-is-recognized-with-type-and-instance"
           (equal (list b a) (pair #'type-instance-relationship association)))
    (check "7.2:isa-is-not-a-supertype-subtype-relationship"
           (equal '(nil nil) (pair #'supertype-subtype-relationship association)))
    (check "7.2:topic-readers-return-the-association"
           (and (equal (list association) (topic-type-associations a))
                (equal (list association) (topic-instance-associations b))
                (null (topic-type-associations b)) (null (topic-instance-associations a))
                (null (topic-supertype-associations a)) (null (topic-subtype-associations b)))))
  ;; 7.3: type .../supertype-subtype, exactly two Roles, of types .../supertype and .../subtype.
  (let* ((map (read-ctm "a ako b.")) (a (local map "a")) (b (local map "b"))
         (association (only (topic-map-associations map))))
    (check "7.3:ako-is-recognized-with-supertype-and-subtype"
           (equal (list b a) (pair #'supertype-subtype-relationship association)))
    (check "7.3:ako-is-not-a-type-instance-relationship"
           (equal '(nil nil) (pair #'type-instance-relationship association)))
    (check "7.3:topic-readers-return-the-association"
           (and (equal (list association) (topic-supertype-associations a))
                (equal (list association) (topic-subtype-associations b))
                (null (topic-supertype-associations b)) (null (topic-subtype-associations a)))))
  ;; 7.2, last sentence: Scope applies as to any other Association; the reader keeps it reachable.
  (let* ((map (make-topic-map)) (a (plain map "a")) (b (plain map "b")) (theme (plain map "theme"))
         (association (make-association map (core map "type-instance")
                                        (list (list (core map "instance") a) (list (core map "type") b))
                                        :scope (list theme))))
    (check "7.2:scoped-association-is-recognized-and-keeps-its-scope"
           (and (equal (list b a) (pair #'type-instance-relationship association))
                (equal (list theme) (association-scope (only (topic-type-associations a)))))))
  ;; [roles] is a set (5.7); the order in which Roles were supplied is not significant.
  (let* ((map (make-topic-map)) (a (plain map "a")) (b (plain map "b"))
         (association (make-association map (core map "supertype-subtype")
                                        (list (list (core map "supertype") b) (list (core map "subtype") a)))))
    (check "7.3:role-order-is-irrelevant"
           (equal (list b a) (pair #'supertype-subtype-relationship association))))
  ;; 7.3 NOTE: loops are allowed and do not imply that the types are the same.
  (let* ((map (read-ctm "a ako b. b ako a.")) (a (local map "a")) (b (local map "b")))
    (check "7.3:loop-is-two-relationships-and-two-topics"
           (and (not (eq (canonical-topic a) (canonical-topic b))) (equal '(0 2) (counts map))
                (= 1 (length (topic-supertype-associations a))) (= 1 (length (topic-subtype-associations a))))))
  ;; Nothing in 7.2 forbids one Topic playing both Roles; the two Roles differ in type and stay two (5.8).
  (let* ((map (read-ctm "a isa a.")) (a (local map "a")) (association (only (topic-map-associations map))))
    (check "7.2:one-topic-playing-both-roles-is-reported-as-stored"
           (and (equal (list a a) (pair #'type-instance-relationship association))
                (equal (list association) (topic-type-associations a))
                (equal (list association) (topic-instance-associations a))))))

(defun negative-tests ()
  "Associations that use the Core Subject Identifiers without the structure of 7.2/7.3 are not relationships."
  (flet ((unrecognized-p (association)
           (and (equal '(nil nil) (pair #'type-instance-relationship association))
                (equal '(nil nil) (pair #'supertype-subtype-relationship association)))))
    (let* ((map (make-topic-map)) (a (plain map "a")) (b (plain map "b")) (c (plain map "c")))
      (check "7.2:three-roles-are-not-exactly-two"
             (unrecognized-p (make-association map (core map "type-instance")
                               (list (list (core map "instance") a) (list (core map "type") b)
                                     (list (plain map "extra") c)))))
      (check "7.2:one-role-is-not-exactly-two"
             (unrecognized-p (make-association map (core map "type-instance") (list (list (core map "instance") a)))))
      (check "7.2:two-instance-roles-lack-the-type-role"
             (unrecognized-p (make-association map (core map "type-instance")
                               (list (list (core map "instance") a) (list (core map "instance") b)))))
      (check "7.2:association-type-without-the-core-identifier"
             (unrecognized-p (make-association map (plain map "type-instance")
                               (list (list (core map "instance") a) (list (core map "type") b)))))
      (check "7.2:role-types-of-the-other-relationship"
             (unrecognized-p (make-association map (core map "type-instance")
                               (list (list (core map "subtype") a) (list (core map "supertype") b)))))
      (check "7.3:role-types-of-the-other-relationship"
             (unrecognized-p (make-association map (core map "supertype-subtype")
                               (list (list (core map "instance") a) (list (core map "type") b)))))
      (check "7.3:one-role-is-not-exactly-two"
             (unrecognized-p (make-association map (core map "supertype-subtype") (list (list (core map "subtype") a)))))
      (check "negative:no-topic-reader-reports-these"
             (and (null (topic-type-associations a)) (null (topic-instance-associations b))
                  (null (topic-supertype-associations a)) (null (topic-subtype-associations b)))))
    ;; The clauses name the [subject identifiers] property. The same string as a Subject Locator or as an
    ;; Item Identifier is another property.
    (dolist (kind '(:subject-locator :item-identifier))
      (let* ((map (make-topic-map)) (a (plain map "a")) (b (plain map "b"))
             (association (make-association map (intern-topic map kind (core-iri "type-instance"))
                            (list (list (intern-topic map kind (core-iri "instance")) a)
                                  (list (intern-topic map kind (core-iri "type")) b)))))
        (check (format nil "7.2:core-locator-only-as-~(~A~)-is-not-recognized" kind)
               (and (unrecognized-p association) (null (topic-type-associations a))))))))

(defun merge-tests ()
  "5.3.5: a Topic whose Item Identifier equals another Topic's Subject Identifier merges with it;
after that merge the Association's type has the Subject Identifier, and 7.2 holds."
  (let* ((map (make-topic-map)) (a (plain map "a")) (b (plain map "b"))
         (type (intern-topic map :item-identifier (core-iri "type-instance")))
         (association (make-association map type (list (list (core map "instance") a) (list (core map "type") b)))))
    (check "merge:not-recognized-before" (equal '(nil nil) (pair #'type-instance-relationship association)))
    (let ((merged (core map "type-instance")))
      (check "merge:item-and-subject-identifier-merged" (eq merged (canonical-topic type)))
      (check "merge:recognized-after-through-the-retained-handle"
             (and (equal (list b a) (pair #'type-instance-relationship association))
                  (equal (list (canonical-association association)) (topic-type-associations a)))))))

(defun no-inference-tests ()
  "7.3 does not require Associations for inferred relationships; the readers report stated ones only."
  (let* ((map (read-ctm "a isa b. b ako c.")) (a (local map "a")) (b (local map "b")) (c (local map "c")))
    (check "no-inference:instance-of-subtype-is-not-reported-as-instance-of-supertype"
           (and (equal (list b) (mapcar #'type-instance-relationship (topic-type-associations a)))
                (null (topic-instance-associations c)))))
  (let* ((map (read-ctm "a ako b. b ako c.")) (a (local map "a")) (b (local map "b")))
    (check "no-inference:supertype-subtype-is-not-closed-transitively"
           (equal (list b) (mapcar #'supertype-subtype-relationship (topic-supertype-associations a))))))

(defun no-mutation-tests ()
  "The readers intern no Topic and leave every item and the canonical output as they were."
  (let* ((map (read-ctm "a - \"A\" . r(p: a, q: b)")) (topics (topic-map-topics map))
         (associations (topic-map-associations map)) (before (cxtm map)))
    (dolist (association associations)
      (type-instance-relationship association) (supertype-subtype-relationship association))
    (dolist (topic topics)
      (topic-type-associations topic) (topic-instance-associations topic)
      (topic-supertype-associations topic) (topic-subtype-associations topic))
    (check "no-mutation:no-core-topic-is-created"
           (and (same-set-p topics (topic-map-topics map))
                (notany (lambda (topic) (intersection (topic-subject-identifiers topic) (core-subject-identifiers)
                                                      :test #'string=))
                        (topic-map-topics map))))
    (check "no-mutation:items-and-cxtm-unchanged"
           (and (same-set-p associations (topic-map-associations map)) (string= before (cxtm map)))))
  (let* ((map (read-ctm "a isa b. c ako d.")) (before (cxtm map)) (topics (topic-map-topics map)))
    (dolist (topic topics) (topic-type-associations topic) (topic-subtype-associations topic))
    (check "no-mutation:reading-relationships-changes-nothing"
           (and (equal '(1 1) (counts map)) (same-set-p topics (topic-map-topics map)) (string= before (cxtm map))))))

(defun original-tests ()
  "The eleven original isa/ako inputs: what the readers report for the maps the CTM reader builds."
  (setf *original-observations* nil)
  (let ((corpus (topic-maps.test-foundation:discover-corpus)))
    (dolist (name +originals+)
      (let* ((id (format nil "ctm/in/~A.ctm" name))
             (case (first (topic-maps.test-foundation:select-cases corpus :id id)))
             (map (topic-maps.ctm:deserialize-file (topic-maps.test-foundation:test-case-source-pathname case)
                    :document-iri (topic-maps.test-foundation:test-case-document-iri case) :source-name id))
             (counts (counts map)))
        (check (concatenate 'string id ":at-least-one-relationship") (plusp (+ (first counts) (second counts))))
        (check (concatenate 'string id ":only-the-keyword's-relationship")
               (zerop (if (eql 0 (search "isa" name)) (second counts) (first counts))))
        (push (list id (first counts) (second counts)) *original-observations*))))
  (setf *original-observations* (nreverse *original-observations*)))

(defun write-report (path)
  "Counts per original input, for comparison with an evaluation of the stored CXTM baselines."
  (with-open-file (out path :direction :output :if-exists :supersede)
    (format out "{\"cases\": [~%")
    (loop for (id type-instance supertype-subtype) in *original-observations* for first = t then nil
          do (format out "~:[,~%~;~]  {\"id\": \"~A\", \"type_instance\": ~D, \"supertype_subtype\": ~D}"
                     first id type-instance supertype-subtype))
    (format out "~%]}~%"))
  path)

(defun run-tests ()
  (let ((topic-maps.ctm.tests::*checks* nil))
    (positive-tests) (negative-tests) (merge-tests) (no-inference-tests) (no-mutation-tests) (original-tests)
    (setf *last-checks* (reverse topic-maps.ctm.tests::*checks*))
    (format t "~&CORE-RELATIONSHIP-PASS: ~D checks; TMDM 7.2 and 7.3 recognized as stated, ~D original inputs, nothing inferred or changed.~%"
            (length *last-checks*) (length *original-observations*))
    *last-checks*))
