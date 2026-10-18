(defpackage #:topic-maps.relationship.tests
  (:use #:cl #:topic-maps.tmdm)
  (:import-from #:topic-maps.ctm.tests #:check #:read-text #:cxtm #:binary-file)
  (:import-from #:topic-maps.variant.tests #:condition-from)
  (:import-from #:topic-maps.identifier.tests #:si)
  (:export #:run-tests #:relationship-checks #:write-relationship-report))
(in-package #:topic-maps.relationship.tests)
(defvar *last-checks* nil)
(defvar *observations* nil)
(defvar *rejections* nil)
(defparameter *originals*
  '("isa-relationship" "isa-relationship-duplicate" "isa-relationship-duplicate2"
    "isa-relationship-embedded" "isa-relationship-type-qname"
    "ako-relationship" "ako-relationship-duplicate" "ako-relationship-duplicate2"
    "ako-relationship-embedded" "ako-relationship-supertype-qname" "ako-merge-away"
    "subject-identifier-topicref" "item-identifier-topicref"))
(defun relationship-checks () *last-checks*)
(defun core-iri (local) (concatenate 'string "http://psi.topicmaps.org/iso13250/model/" local))
(defun core (map local) (intern-topic map :subject-identifier (core-iri local)))
(defun named (map local) (topic-maps.arity.tests::named-topic map local))
(defun state (map handles) (topic-maps.reification.tests::state map handles))
(defun handles (map) (copy-list (topic-maps.tmdm::map-information-items map)))
(defun valid-model-p (map)
  (and (topic-maps.reification.tests::invariants map) (topic-maps.tmdm::validate-map-core-subjects map)))
(defun with-si (map iri) (find iri (topic-map-topics map) :test (lambda (id topic) (member id (topic-subject-identifiers topic) :test #'string=))))
(defun typed (map local) (find (with-si map (core-iri local)) (topic-map-associations map) :key #'association-type :test #'eq))
(defun role (a local) (find (core-iri local) (association-roles a)
                          :test (lambda (id r) (member id (topic-subject-identifiers (association-role-type r)) :test #'string=))))

(defun rejects-atomically (label map thunk &key (extra nil) (valid t))
  (let* ((all (append (handles map) extra)) (before (state map all)) (c (condition-from thunk))
         (unchanged (equal before (state map all))))
    (check (concatenate 'string label ":condition")
           (and (eq (type-of c) 'core-subject-error) (eq :core-subject-conflict (core-subject-error-code c))))
    (check (concatenate 'string label ":all-original-slots-identifiers-and-forward-links-unchanged") unchanged)
    (check (concatenate 'string label ":no-invalid-state-introduced") (or (not valid) (valid-model-p map)))
    (push (topic-maps.test-foundation::fields "label" label "code" "core-subject-conflict"
            "unchanged" (if unchanged :true :false) "detail" (princ-to-string c)) *rejections*)))

(defun core-tests ()
  (let ((expected (mapcar #'core-iri '("type-instance" "type" "instance" "supertype-subtype" "supertype" "subtype" "sort" "name-type"))))
    (check "core:closed-vocabulary-from-TMDM-7.1-through-7.5" (equal expected (core-subject-identifiers)))
    (let ((copy (core-subject-identifiers)))
      (setf (char (first copy) 0) #\X (rest copy) nil)
      (check "core:public-vocabulary-returns-private-copies" (equal expected (core-subject-identifiers)))))
  (loop for left in (core-subject-identifiers) for i from 1 do
    (loop for right in (core-subject-identifiers) for j from 1 unless (string= left right) do
      (dolist (route '(:explicit :subject :item :locator :intern))
        (let* ((map (make-topic-map)) (a (intern-topic map :subject-identifier left))
               (b (unless (eq route :intern) (intern-topic map :subject-identifier right)))
               (label (format nil "core:~D:~D:~A" i j route)))
          (case route
            (:intern (add-item-identifier a right))
            (:subject (add-item-identifier b "urn:core:bridge"))
            (:locator (add-topic-identifier b :subject-locator "urn:core:bridge")))
          (rejects-atomically label map
            (lambda ()
              (ecase route
                (:explicit (merge-topics a b))
                (:subject (add-topic-identifier a :subject-identifier "urn:core:bridge"))
                (:item (add-item-identifier a right))
                (:locator (add-topic-identifier a :subject-locator "urn:core:bridge"))
                (:intern (intern-topic map :subject-identifier right)))))))))
  (dolist (iri (core-subject-identifiers))
    (let* ((map (make-topic-map)) (a (intern-topic map :subject-identifier iri)) (alias (si map "alias")))
      (check (concatenate 'string "core:same-subject-idempotent:" iri)
             (and (eq a (intern-topic map :subject-identifier iri)) (eq a (add-topic-identifier a :subject-identifier iri))))
      (let ((c (add-topic-identifier alias :subject-identifier iri)))
        (check (concatenate 'string "core:legal-alias-replacement:" iri)
               (and (eq c (canonical-topic a)) (eq c (canonical-topic alias))
                    (not (eq c a)) (= 1 (length (topic-map-topics map))) (valid-model-p map))))))
  (let* ((map (make-topic-map))
         (a (intern-topic map :subject-locator (core-iri "type")))
         (b (intern-topic map :subject-locator (core-iri "instance"))) (c (merge-topics a b)))
    (check "core:protected-spelling-as-subject-locator-is-not-a-Core-Subject-Identifier"
           (and (null (topic-subject-identifiers c)) (= 2 (length (topic-subject-locators c))) (valid-model-p map))))
  (let* ((map (make-topic-map)) (a (core map "type")))
    (add-item-identifier a (core-iri "instance"))
    (check "core:item-locator-alone-does-not-assert-another-Core-Subject"
           (and (eq a (intern-topic map :item-identifier (core-iri "instance"))) (valid-model-p map)))))

(defun chain-tests ()
  ;; Existing legal alias chains: reject an assertion made through old handles.
  (dolist (route '(:explicit :subject))
    (let* ((map (make-topic-map)) (a (core map "type")) (b (core map "instance"))
           (x (si map "x")) (y (si map "y")) (z (si map "z")))
      (merge-topics a x) (merge-topics x y) (merge-topics b z)
      (rejects-atomically (format nil "chain:old-handles:~A" route) map
        (lambda () (ecase route
          (:explicit (merge-topics x z))
          (:subject (add-topic-identifier y :subject-identifier (core-iri "instance")))))
        :extra (list a b x y z))))
  (let* ((map (make-topic-map)) (a (core map "type")) (x (si map "x")) (y (si map "y")))
    (merge-topics a x) (merge-topics x y)
    (add-item-identifier x (core-iri "instance"))
    (rejects-atomically "chain:intern-through-existing-alias-chain" map
      (lambda () (intern-topic map :subject-identifier (core-iri "instance"))) :extra (list a x y)))
  ;; White-box input for NORMALIZE-TOPIC-MAP: the first merges are benign;
  ;; a later SI/II chain would unite the two Core Subjects. This is deliberately
  ;; not an already-normalized public-API state. Rejection must preserve it too.
  (let* ((map (make-topic-map)) (a (core map "type")) (x (si map "x")) (y (si map "y")) (b (core map "instance")))
    (push "urn:edge:1" (topic-maps.tmdm::%topic-subject-identifiers a))
    (push "urn:edge:1" (topic-maps.tmdm::%topic-item-identifiers x))
    (push "urn:edge:2" (topic-maps.tmdm::%topic-subject-identifiers x))
    (push "urn:edge:2" (topic-maps.tmdm::%topic-item-identifiers y))
    (push "urn:edge:3" (topic-maps.tmdm::%topic-subject-identifiers y))
    (push "urn:edge:3" (topic-maps.tmdm::%topic-item-identifiers b))
    (rejects-atomically "chain:normalize-entire-transitive-closure" map (lambda () (normalize-topic-map map)) :valid nil))
  (let* ((map (make-topic-map)) (a (core map "type")))
    (push (core-iri "instance") (topic-maps.tmdm::%topic-subject-identifiers a))
    (rejects-atomically "chain:normalize-preexisting-core-conflict" map (lambda () (normalize-topic-map map)) :valid nil)
    (let ((before (state map (handles map))) (c (condition-from (lambda () (cxtm map)))))
      (check "core:CXTM-rejects-corrupted-core-state-without-changing-it"
             (and (eq (type-of c) 'topic-maps.cxtm:cxtm-error)
                  (eq :core-subject-conflict (topic-maps.cxtm:error-code c))
                  (equal before (state map (handles map))))))))

(defun reifier-tests ()
  (dolist (kind '(topic-name variant occurrence association association-role))
    (dolist (route '(:explicit :subject :item))
      (multiple-value-bind (map a b one two) (topic-maps.reification.tests::paired-items kind)
        (let ((left (core map "type")) (right (core map "instance")))
          (set-item-reifier one left) (set-item-reifier two right)
          (case route ((:subject :item) (add-item-identifier b "urn:parents:join")))
          (rejects-atomically (format nil "reifier:~A:~A" kind route) map
            (lambda () (ecase route
              (:explicit (merge-topics a b))
              (:subject (add-topic-identifier a :subject-identifier "urn:parents:join"))
              (:item (add-item-identifier a "urn:parents:join")))))))))
  (multiple-value-bind (map items) (topic-maps.identifier.tests::fixture)
    (let ((left (core map "type")) (right (core map "instance")) (name (third items)))
      (set-item-reifier name left)
      (rejects-atomically "reifier:direct-setter-core-conflict" map (lambda () (set-item-reifier name right)))))
  ;; Four levels: Name -> Occurrence -> Association -> Role -> Core Reifiers.
  (dolist (route '(:explicit :subject))
    (multiple-value-bind (map a b left right rs ss) (topic-maps.reification.tests::cascade)
      (add-topic-identifier (fourth rs) :subject-identifier (core-iri "type"))
      (add-topic-identifier (fourth ss) :subject-identifier (core-iri "instance"))
      (when (eq route :subject) (add-item-identifier b "urn:root:join"))
      (rejects-atomically (format nil "reifier:four-level-cascade:~A" route) map
        (lambda () (if (eq route :explicit) (merge-topics a b)
                        (add-topic-identifier a :subject-identifier "urn:root:join")))
        :extra (append left right rs ss))))
  ;; A previously unnormalized graph may fail even when interning a fresh,
  ;; unrelated Topic. The constructor must preflight BEFORE appending that item.
  (let* ((map (make-topic-map)) (a (core map "type")) (b (core map "instance")))
    (push "urn:late:join" (topic-maps.tmdm::%topic-subject-identifiers a))
    (push "urn:late:join" (topic-maps.tmdm::%topic-item-identifiers b))
    (rejects-atomically "intern:no-dangling-new-topic-after-late-conflict" map
      (lambda () (intern-topic map :item-identifier "urn:brand-new")) :valid nil)))

(defun semantic-tests ()
  (dolist (keyword '("isa" "ako"))
    (let* ((isa (string= keyword "isa")) (map (read-text (format nil "a ~A b." keyword)))
           (type (if isa "type-instance" "supertype-subtype"))
           (left (if isa "instance" "subtype")) (right (if isa "type" "supertype"))
           (a (typed map type)) (roles (association-roles a))
           (owner (named map "a")) (target (named map "b")))
      (check (concatenate 'string keyword ":exact-items-and-six-vocabulary-subjects-used-correctly")
             (and (= 5 (length (topic-map-topics map))) (= 1 (length (topic-map-associations map)))
                  (= 2 (length roles)) (null (association-scope a)) (null (item-reifier a))
                  (eq owner (association-role-player (role a left))) (eq target (association-role-player (role a right)))
                  (every (lambda (r) (and (eq a (association-role-parent r))
                                          (eq r (first (topic-roles-played (association-role-player r)))))) roles)
                  (valid-model-p map)))
      (loop for local in (list type left right) do
        (check (format nil "~A:standard-Subject-Identifier:~A" keyword local)
               (let ((tpc (with-si map (core-iri local))))
                 (and tpc (equal (list (core-iri local)) (topic-subject-identifiers tpc))
                      (null (topic-item-identifiers tpc)) (null (topic-subject-locators tpc))))))
      (let* ((held (cons a roles)) (before (state map held)) (output (cxtm map)))
        (check (concatenate 'string keyword ":pure-and-repeatable-CXTM")
               (and (string= output (cxtm map)) (equal before (state map held)))))
      (let* ((explicit (make-association map (association-type a)
                         (list (list (association-role-type (role a right)) target)
                               (list (association-role-type (role a left)) owner)))))
        (check (concatenate 'string keyword ":longhand-merges-and-retained-Association-and-Role-handles")
               (and (not (eq explicit a)) (eq explicit (canonical-association a))
                    (every (lambda (r) (member (canonical-association-role r) (association-roles explicit) :test #'eq)) roles)
                    (valid-model-p map))))))
  (let* ((map (read-text "a isa b; isa b; ako c; ako c.")))
    (check "relationships:repeated-tail-elements-use-role-set-merging" (= 2 (length (topic-map-associations map)))))
  (let ((map (read-text "a ako b. b ako a. a isa c. c isa d.")))
    (check "relationships:ako-cycle-and-isa-chain-do-not-merge-subjects-or-materialize-inferences"
           (and (= 4 (length (topic-map-associations map))) (not (eq (named map "a") (named map "b")))
                (not (eq (named map "c") (named map "d"))) (valid-model-p map))))
  (let* ((map (read-text "a isa a; ako a.")))
    (check "relationships:self-player-has-two-distinct-Role-types"
           (every (lambda (a) (and (= 2 (length (association-roles a)))
                                   (every (lambda (r) (eq (named map "a") (association-role-player r))) (association-roles a))))
                  (topic-map-associations map))))
  (dolist (text '("a isa ?target; ako ?target." "?owner isa ?target; ako [ako ?target]."
                  "a isa [isa [-\"C\"]]; ako [ako b]." "a isa =<urn:resource>."
                  "a isa ^<urn:item>." "a isa <urn:subject>."
                  "a isa [^<https://example.invalid/a/doc.ctm#a>]."
                  "a isa b; - \"Name\"." "a ISA: \"N\"; ako b."))
    (check (concatenate 'string "relationships:existing-topic-reference-and-tail-syntax:" text) (valid-model-p (read-text text))))
  (let* ((map (read-text "a isa [^<https://example.invalid/a/doc.ctm#a>].")) (a (first (topic-map-associations map))))
    (check "relationships:RHS-merge-keeps-owner-and-target-canonical-EQ"
           (every (lambda (r) (eq (named map "a") (association-role-player r))) (association-roles a))))
  (let ((map (read-text (format nil "%prefix isa http://example.org/~%a isa isa:t. isa:x."))))
    (check "relationships:keyword-not-confused-with-QName-prefix"
           (and (with-si map "http://example.org/t") (with-si map "http://example.org/x") (valid-model-p map))))
  (check "relationships:keyword-matching-preserves-case-and-identifier-boundaries"
         (let ((map (read-text "isabel. ako2. ISA.")))
           (and (= 3 (length (topic-map-topics map))) (null (topic-map-associations map))))))

(defun diagnostic-tests ()
  (dolist (fixture '(("a isa ." :expected-relationship-topic 6) ("a ako" :expected-relationship-topic 5)
                     ("a isa b,c." :unexpected-relationship-list 7) ("a ako b, c." :unexpected-relationship-list 7)
                     ("a isa b isa c." :expected-separator 8) ("a isa [ako]." :expected-relationship-topic 10)
                     ("a isa ako." :expected-relationship-topic 6) ("isa." :reserved-topic-identifier 0)
                     ("a isa def." :expected-relationship-topic 6) ("a ako end." :expected-relationship-topic 6)
                     ("a isa b @s." :unexpected-token 8) ("a ako b ~r." :unexpected-token 8)))
    (destructuring-bind (text code position) fixture
      (let ((c (condition-from (lambda () (read-text text)))))
        (check (concatenate 'string "diagnostic:class-code-and-position:" text)
               (and (eq (type-of c) 'topic-maps.ctm:ctm-rejection) (eq code (topic-maps.ctm:error-code c))
                    (= position (topic-maps.ctm:error-position c)) (= 1 (topic-maps.ctm:error-line c))
                    (= (1+ position) (topic-maps.ctm:error-column c)))))))
  (let ((c (condition-from (lambda () (read-text (format nil "a isa~%   ."))))))
    (check "diagnostic:missing-RHS-newline-and-column"
           (and (eq :expected-relationship-topic (topic-maps.ctm:error-code c))
                (= 9 (topic-maps.ctm:error-position c)) (= 2 (topic-maps.ctm:error-line c)) (= 4 (topic-maps.ctm:error-column c)))))
  (let ((c (condition-from (lambda () (read-text "a isa bad:t.")))))
    (check "diagnostic:undefined-prefix-remains-its-own-class"
           (and (eq (type-of c) 'topic-maps.ctm:undefined-prefix) (= 6 (topic-maps.ctm:error-position c)))))
  (let* ((text (format nil "a <~A>; <~A>." (core-iri "type") (core-iri "instance")))
         (c (condition-from (lambda () (read-text text)))))
    (check "diagnostic:core-identity-conflict-is-specific-CTM-rejection"
           (and (eq (type-of c) 'topic-maps.ctm:ctm-rejection) (eq :core-subject-conflict (topic-maps.ctm:error-code c))
                (= (search "<http" text :from-end t) (topic-maps.ctm:error-position c)))))
  (let* ((text (format nil "a - \"N\" ~~<~A>; - \"N\" ~~<~A>." (core-iri "type") (core-iri "instance")))
         (c (condition-from (lambda () (read-text text)))))
    (check "diagnostic:core-reifier-conflict-points-to-reifier-marker"
           (and (eq (type-of c) 'topic-maps.ctm:ctm-rejection) (eq :core-subject-conflict (topic-maps.ctm:error-code c))
                (= (position #\~ text :from-end t) (topic-maps.ctm:error-position c))))))

(defun observe-model (map)
  (let ((topics (topic-map-topics map)))
    (flet ((ordinal (tpc) (1+ (position tpc topics :test #'eq))))
      (topic-maps.test-foundation::fields
        "topics" (topic-maps.test-foundation::json-array
          (loop for tpc in topics collect (topic-maps.test-foundation::fields
            "ordinal" (ordinal tpc)
            "itemIdentifiers" (topic-maps.test-foundation::json-array (topic-item-identifiers tpc))
            "subjectIdentifiers" (topic-maps.test-foundation::json-array (topic-subject-identifiers tpc))
            "subjectLocators" (topic-maps.test-foundation::json-array (topic-subject-locators tpc)))))
        "associations" (topic-maps.test-foundation::json-array
          (loop for a in (topic-map-associations map) collect (topic-maps.test-foundation::fields
            "type" (ordinal (association-type a)) "scope" (topic-maps.test-foundation::json-array (mapcar #'ordinal (association-scope a)))
            "parentIsMap" (if (eq map (association-parent a)) :true :false)
            "roles" (topic-maps.test-foundation::json-array
              (loop for r in (association-roles a) collect (topic-maps.test-foundation::fields
                "type" (ordinal (association-role-type r)) "player" (ordinal (association-role-player r))
                "parentIsAssociation" (if (eq a (association-role-parent r)) :true :false)
                "roleIsCanonical" (if (eq r (canonical-association-role r)) :true :false)
                "inverseContainsRole" (if (member r (topic-roles-played (association-role-player r)) :test #'eq) :true :false)))))))))))
(defun original-cases ()
  (setf *observations* nil)
  (dolist (file *originals*)
    (let* ((id (format nil "ctm/in/~A.ctm" file))
           (case (first (topic-maps.test-foundation:select-cases topic-maps.ctm.tests::*cxtm-corpus* :id id)))
           (doc (topic-maps.test-foundation:test-case-document-iri case))
           (map (topic-maps.ctm:deserialize-file (topic-maps.test-foundation:test-case-source-pathname case) :document-iri doc :source-name id))
           (held (handles map)) (before (state map held))
           (actual (topic-maps.cxtm:canonicalize-octets map :base-locator doc))
           (expected (binary-file (topic-maps.test-foundation:test-case-expected-baseline case))))
      (check (concatenate 'string id ":actual-canonical-TMDM-object-references") (valid-model-p map))
      (check (concatenate 'string id ":byte-exact-original-CXTM") (equalp actual expected))
      (check (concatenate 'string id ":pure-repeatable-CXTM-and-retained-handles")
             (and (equalp actual (topic-maps.cxtm:canonicalize-octets map :base-locator doc)) (equal before (state map held))))
      (topic-maps.test-foundation:record-result case :cxtm-match)
      (setf (topic-maps.test-foundation:test-case-clauses case)
            '("CTM 3.9" "CTM 3.3.6-3.3.8" "TMDM 5.3.5" "TMDM 5.7-5.8" "TMDM 6.2" "TMDM 6.6-6.7" "TMDM 7.1-7.3" "CXTM 3.9-3.10" "CXTM 4.10-4.11"))
      (setf topic-maps.ctm.tests::*cxtm-results* (append topic-maps.ctm.tests::*cxtm-results*
        (list (list :id id :base doc :actual (cxtm map doc) :expected (uiop:read-file-string (topic-maps.test-foundation:test-case-expected-baseline case))
                    :match t :bytes (length actual)))))
      (push (topic-maps.test-foundation::fields "id" id "documentIRI" doc
              "ctmSource" (uiop:read-file-string (topic-maps.test-foundation:test-case-source-pathname case))
              "model" (observe-model map)) *observations*)
      (format t "~&RELATIONSHIP-CXTM ~A: PASS (~D bytes)~%" id (length actual))))
  (setf *observations* (nreverse *observations*)))
(defun run-tests ()
  (topic-maps.arity.tests:run-tests)
  (let ((topic-maps.ctm.tests::*checks* nil))
    (setf *rejections* nil)
    (core-tests) (chain-tests) (reifier-tests) (semantic-tests) (diagnostic-tests) (original-cases)
    (check "relationships:only-thirteen-new-imported-contracts"
           (equal '(:pass 120 :fail 2 :unsupported 0 :not-run 151)
                  (getf (topic-maps.test-foundation:summarize-corpus topic-maps.ctm.tests::*cxtm-corpus*) :statuses)))
    (setf *last-checks* (nreverse topic-maps.ctm.tests::*checks*) *rejections* (nreverse *rejections*))
    (format t "~&TYPE-RELATIONSHIPS-PASS: ~D checks; 13 original CXTM contracts; 120 PASS, 2 known FAIL, 151 NOT-RUN.~%" (length *last-checks*)) t))
(defun write-relationship-report (path)
  (with-open-file (out path :direction :output :if-exists :supersede :if-does-not-exist :create)
    (topic-maps.test-foundation::emit-json-value
      (topic-maps.test-foundation::fields "kind" "type-relationship-evidence" "passed" (length *last-checks*) "failed" 0
        "checks" (topic-maps.test-foundation::json-array *last-checks*)
        "coreSubjectIdentifiers" (topic-maps.test-foundation::json-array (core-subject-identifiers))
        "rejections" (topic-maps.test-foundation::json-array *rejections*)
        "cases" (topic-maps.test-foundation::json-array *observations*)) out)
    (terpri out)))
