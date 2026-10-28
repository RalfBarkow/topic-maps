(defpackage #:topic-maps.normalization-index.tests
  (:use #:cl #:topic-maps.tmdm)
  (:import-from #:topic-maps.ctm.tests #:check #:cxtm)
  (:import-from #:topic-maps.variant.tests #:condition-from)
  (:import-from #:topic-maps.identifier.tests #:si #:current)
  (:export #:run-tests #:normalization-index-checks #:record-expected))
(in-package #:topic-maps.normalization-index.tests)

;;; Which Topics merge next, and the results that must not change while the search for them changes.
;;; The expected CXTM of every case and the class and code of every rejection were recorded from the
;;; unchanged implementation at b2eecffa (RECORD-EXPECTED) before NEXT-TOPIC-MERGE existed; they are not
;;; derived from the implementation under test. SCAN-NEXT-TOPIC-MERGE is the b2eecffa search, kept as the
;;; fallback and used here as the oracle.

(defvar *last-checks* nil)
(defun normalization-index-checks () *last-checks*)
(defparameter +document+ "https://example.invalid/n/doc.ctm")
(defvar *fixture-directory* nil)
(defun fixture-directory ()
  (or *fixture-directory* (asdf:system-relative-pathname "topic-maps" "tests/fixtures/normalization-index/")))
(defun read-case (text) (topic-maps.ctm:deserialize-string text :document-iri +document+ :source-name "normalization-index"))
(defun pick (random sequence) (elt sequence (random (length sequence) random)))

(defun chain-document (topics links)
  "TOPICS Topics with one subject identifier each and a Name, LINKS later statements that give Topic 2I the
item identifier equal to the subject identifier of Topic 2I+1, and one Association per Topic."
  (with-output-to-string (s)
    (dotimes (i topics) (format s "t~D http://example.org/s/~D ; - \"Topic ~D\" .~%" i i i))
    (dotimes (i topics) (format s "rel~D(from: t~D, to: t~D)~%" (mod i 5) i (mod (* 7 (1+ i)) topics)))
    (dotimes (i links) (format s "t~D ^ http://example.org/s/~D .~%" (* 2 i) (1+ (* 2 i))))))

;;; Reifiers: the corpus has 57 reified Associations, each reifier Topic named in its own statement.

(defun reified-document (associations &key (duplicate-every 0))
  "ASSOCIATIONS reified Associations, each reifier Topic with a subject identifier and a Name. Every
DUPLICATE-EVERYth Association is stated a second time with a second reifier Topic: the two Associations are
equal, so their reifier Topics merge although nothing else identifies them."
  (with-output-to-string (s)
    (dotimes (i associations)
      (format s "p~D http://example.org/p/~D ; - \"P ~D\" .~%" i i i)
      (format s "r~D http://example.org/r/~D ; - \"R ~D\" .~%" i i i)
      (format s "rel~D(from: p~D, to: p~D) ~~ r~D~%" (mod i 4) i (mod (* 5 (1+ i)) associations) i))
    (when (plusp duplicate-every)
      (loop for i from 0 below associations by duplicate-every
            do (format s "q~D http://example.org/q/~D ; - \"Q ~D\" .~%" i i i)
               (format s "rel~D(from: p~D, to: p~D) ~~ q~D~%" (mod i 4) i (mod (* 5 (1+ i)) associations) i)))))

;;; Documents whose result must not change, and the nonconflicting-reifier merges among them

(defparameter *documents*
  `(("identifier-acquisition" ,(format nil "a - \"A\" .~%b - \"B\" .~%a ^ https://example.invalid/n/doc.ctm#b ."))
    ("ii-si-cross-identity" ,(format nil "x http://example.org/s .~%y ^ http://example.org/s ."))
    ("transitive-through-third" ,(format nil "a http://example.org/1 .~%b http://example.org/2 .~%c - \"C\" .~%c ^ http://example.org/1 .~%c http://example.org/2 ."))
    ("transitive-late-chain" ,(format nil "p http://example.org/p .~%q http://example.org/q .~%r http://example.org/r .~%q ^ http://example.org/r .~%p http://example.org/q ."))
    ("subject-locator-merge" ,(format nil "s1 = http://example.org/doc .~%s2 = http://example.org/doc ."))
    ("si-and-sl-stay-apart" ,(format nil "t1 http://example.org/z .~%t2 = http://example.org/z ."))
    ("reified-duplicate-associations" ,(format nil "t(r: p) ~~ x~%t(r: p) ~~ y~%x - \"X\" .~%y - \"Y\" ."))
    ("reified-duplicate-names" ,(format nil "n - \"N\" ~~ nr .~%n - \"N\" ~~ nr2 ."))
    ("topic-map-reifier" ,(format nil "~~ mapr~%mapr - \"M\" ."))
    ("reifier-merges-by-identifier" ,(format nil "t(r: p) ~~ x~%u(r: q) ~~ y~%y ^ https://example.invalid/n/doc.ctm#z .~%z - \"Z\" ."))
    ("reifier-acquires-another-topics-identifier" ,(format nil "t(r: p) ~~ x~%x ^ https://example.invalid/n/doc.ctm#w .~%w - \"W\" .~%u(r: q) ~~ v"))
    ("equal-owners-make-the-reified-associations-equal" ,(format nil "a(r: p) ~~ x~%b(r: p) ~~ y~%a ^ https://example.invalid/n/doc.ctm#b ."))
    ("equal-reifiers-of-equal-items" ,(format nil "t(r: p) ~~ x~%t(r: p) ~~ y~%x ^ https://example.invalid/n/doc.ctm#y ."))
    ("isa-ako" ,(format nil "a isa b .~%b ako c .~%d isa b .~%e isa c ."))
    ("isa-duplicates-merge" ,(format nil "a isa k .~%b isa k .~%a isa k .~%k2 http://example.org/k .~%k http://example.org/k .~%b isa k2 ."))
    ("n-ary-duplicate-roles" "t(r1: a, r2: b, r3: c, r1: a)")
    ("wildcard-merge" "?foo . ?foo .")
    ("associations-equal-after-topic-merge" ,(format nil "t(r: a, q: c)~%t(r: b, q: c) ~~ x~%t(r: a, q: c) ~~ y~%b ^ https://example.invalid/n/doc.ctm#a ."))
    ("chain-40-topics" ,(chain-document 40 12))
    ("reified-30-associations" ,(reified-document 30))
    ("reified-30-associations-merging-reifiers" ,(reified-document 30 :duplicate-every 3)))
  "CTM documents whose CXTM is recorded.")

;;; The staged-import scenarios behind the nonconflicting-reifier preference: the Reifier Topics precede
;;; the owners and Types in both maps, and the reified Names become equal only after those Topics merge.

(defun import-outcome (build)
  (multiple-value-bind (target source) (funcall build)
    (import-map-content target source)
    (cxtm target +document+)))

(defun scenario-reifier-first ()
  (let* ((target (make-topic-map)) (source (make-topic-map))
         (r (si target "r")) (s (si source "r")) (a (si target "owner")) (b (si source "owner"))
         (ty (si target "type")) (sy (si source "type")) (n (add-name a "N" :type ty)) (m (add-name b "N" :type sy)))
    (set-item-reifier n r) (set-item-reifier m s)
    (values target source)))

(defun scenario-cascade ()
  ;; Equal Names merge their Reifiers, which are themselves types, players and themes of further items.
  (let* ((target (make-topic-map)) (source (make-topic-map)) (a (si target "owner")) (b (si source "owner"))
         (ty (si target "name-type")) (sy (si source "name-type")) (r (si target "r")) (s (si source "s"))
         (n (add-name a "N" :type ty)) (m (add-name b "N" :type sy)))
    (add-occurrence r r "O" :scope (list r)) (add-occurrence s s "O" :scope (list s))
    (make-association target r (list (list r r)) :scope (list r)) (make-association source s (list (list s s)) :scope (list s))
    (set-item-reifier n r) (set-item-reifier m s)
    (values target source)))

(defun scenario-reifier-chain ()
  ;; Three levels: the Reifiers of equal Names are the owners of further equal Names with their own Reifiers.
  (let* ((target (make-topic-map)) (source (make-topic-map)) (a (si target "owner")) (b (si source "owner"))
         (ty (si target "type")) (sy (si source "type")) (r (si target "r")) (s (si source "s"))
         (r2 (si target "r2")) (s2 (si source "s2"))
         (n (add-name a "N" :type ty)) (m (add-name b "N" :type sy))
         (k (add-name r "K" :type ty)) (l (add-name s "K" :type sy)))
    (set-item-reifier n r) (set-item-reifier m s) (set-item-reifier k r2) (set-item-reifier l s2)
    (values target source)))

(defparameter *scenarios*
  '(("import-reifier-first" scenario-reifier-first) ("import-cascade" scenario-cascade)
    ("import-reifier-chain" scenario-reifier-chain))
  "Staged imports whose resulting CXTM is recorded.")

;;; Rejections: conflict signalling and preflight rejection must stay as recorded

(defparameter *rejections*
  `(("reifier-reifies-two-items" ,(format nil "t(r: p) ~~ x~%u(r: q) ~~ x"))
    ("reifier-merge-conflict" ,(format nil "t(r: p) ~~ x~%u(r: q) ~~ y~%x ^ https://example.invalid/n/doc.ctm#y ."))
    ("core-subject-conflict" ,(format nil "a http://psi.topicmaps.org/iso13250/model/type .~%a http://psi.topicmaps.org/iso13250/model/instance ."))
    ("core-subject-merge-conflict" ,(format nil "a http://psi.topicmaps.org/iso13250/model/type .~%b http://psi.topicmaps.org/iso13250/model/instance .~%a ^ http://psi.topicmaps.org/iso13250/model/instance ."))
    ("unclosed-association" "a(r: b"))
  "CTM documents whose rejection is recorded as condition class and code.")

(defun rejecting-scenario-reifier-conflict ()
  (let* ((target (make-topic-map)) (source (make-topic-map)) (a (si target "owner")) (b (si source "owner"))
         (ty (si target "type")) (sy (si source "type")) (r (si target "r")) (s (si source "r")))
    (set-item-reifier (add-name a "Different" :type ty) r) (set-item-reifier (add-name b "Name" :type sy) s)
    (values target source)))

(defun rejecting-scenario-retained-root-reifier ()
  (let* ((target (make-topic-map)) (source (make-topic-map)) (r (si target "r")) (s (si source "r")) (owner (si source "owner")))
    (set-item-reifier target r) (set-item-reifier (add-default-name owner "N") s)
    (values target source)))

(defparameter *rejecting-scenarios*
  '(("import-reifier-conflict" rejecting-scenario-reifier-conflict)
    ("import-retained-root-reifier" rejecting-scenario-retained-root-reifier)))

(defun condition-code (c)
  (cond ((typep c 'topic-maps.ctm:ctm-error) (topic-maps.ctm:error-code c))
        ((typep c 'reification-error) (reification-error-code c))
        ((typep c 'core-subject-error) (core-subject-error-code c))
        ((typep c 'map-import-error) (map-import-error-code c))
        (t nil)))

(defun outcome (thunk)
  (handler-case (list :read (funcall thunk))
    (error (c) (list :refused (type-of c) (condition-code c)))))

(defun document-outcome (text) (outcome (lambda () (cxtm (read-case text) +document+))))

(defun record-expected ()
  "Write the expected outcomes with the implementation now loaded. Run once, at b2eecffa."
  (ensure-directories-exist (fixture-directory))
  (flet ((record (name value)
           (with-open-file (out (merge-pathnames (concatenate 'string name ".cxtm") (fixture-directory))
                                :direction :output :if-exists :supersede :external-format :utf-8)
             (write-string value out))))
    (dolist (case *documents*)
      (destructuring-bind (kind value &rest rest) (document-outcome (second case))
        (declare (ignore rest))
        (unless (eq kind :read) (error "Case ~A was refused: ~S" (first case) value))
        (record (first case) value)))
    (dolist (case *scenarios*)
      (destructuring-bind (kind value &rest rest) (outcome (lambda () (import-outcome (symbol-function (second case)))))
        (declare (ignore rest))
        (unless (eq kind :read) (error "Scenario ~A was refused: ~S" (first case) value))
        (record (first case) value))))
  (with-open-file (out (merge-pathnames "rejections.sexp" (fixture-directory)) :direction :output :if-exists :supersede)
    (let ((*package* (find-package "KEYWORD")))
      (dolist (case *rejections*)
        (prin1 (cons (first case) (rest (document-outcome (second case)))) out) (terpri out))
      (dolist (case *rejecting-scenarios*)
        (prin1 (cons (first case) (rest (outcome (lambda () (import-outcome (symbol-function (second case))))))) out) (terpri out)))))

(defun expected-cxtm (name)
  (uiop:read-file-string (merge-pathnames (concatenate 'string name ".cxtm") (fixture-directory)) :external-format :utf-8))
(defun expected-rejections ()
  (with-open-file (in (merge-pathnames "rejections.sexp" (fixture-directory)))
    (let ((*read-eval* nil)) (loop for form = (read in nil) while form collect form))))

(defun recorded-outcome-tests ()
  (dolist (case *documents*)
    (let ((o (document-outcome (second case))))
      (check (format nil "document:~A:read" (first case)) (eq :read (first o)))
      (check (format nil "document:~A:cxtm-equals-b2eecffa" (first case)) (string= (second o) (expected-cxtm (first case))))))
  (dolist (case *scenarios*)
    (let ((o (outcome (lambda () (import-outcome (symbol-function (second case)))))))
      (check (format nil "scenario:~A:cxtm-equals-b2eecffa" (first case))
             (and (eq :read (first o)) (string= (second o) (expected-cxtm (first case)))))))
  (let ((expected (expected-rejections)))
    (flet ((same (name o)
             (let ((recorded (rest (assoc name expected :test #'string=))))
               (check (format nil "rejection:~A:recorded" name) recorded)
               (check (format nil "rejection:~A:class-and-code-equal-b2eecffa" name) (equal (rest o) recorded)))))
      (dolist (case *rejections*) (same (first case) (document-outcome (second case))))
      (dolist (case *rejecting-scenarios*)
        (same (first case) (outcome (lambda () (import-outcome (symbol-function (second case))))))))))

;;; Semantics that no recorded text shows: canonical representatives, retained handles, reifier preference

(defun live-p (topic map) (member topic (topic-map-topics map) :test #'eq))

(defun handle-tests (with-reifier)
  (let* ((map (make-topic-map)) (label (if with-reifier "with-reifier" "plain"))
         (a (si map "a")) (b (si map "b")) (c (intern-topic map :item-identifier "urn:c")) (other (si map "other")))
    (when with-reifier
      (set-item-reifier (make-association map other (list (list other a))) (si map "reifier")))
    (add-topic-identifier c :item-identifier "urn:a")
    (check (format nil "handles:~A:c-merged-with-a" label) (eq (canonical-topic a) (canonical-topic c)))
    (check (format nil "handles:~A:b-still-apart" label) (not (eq (canonical-topic a) (canonical-topic b))))
    (add-topic-identifier c :subject-identifier "urn:b")
    (let ((merged (canonical-topic a)))
      (check (format nil "handles:~A:transitive-one-topic" label)
             (and (eq merged (canonical-topic b)) (eq merged (canonical-topic c))))
      (check (format nil "handles:~A:representative-is-live" label) (live-p merged map))
      (check (format nil "handles:~A:obsolete-handles-are-not-live-and-forward" label)
             (every (lambda (h) (or (eq h merged) (and (not (live-p h map)) (eq merged (canonical-topic h))))) (list a b c)))
      (check (format nil "handles:~A:other-untouched" label) (eq other (canonical-topic other)))
      (check (format nil "handles:~A:model-valid" label)
             (and (topic-maps.tmdm::validate-map-item-identifiers map) (topic-maps.tmdm::validate-map-reification map))))))

(defun representative-tests ()
  ;; Three Topics become one; the representative takes the place of the first of them, whatever the order of merging.
  (let* ((map (make-topic-map)) (x (si map "x")) (a (si map "a")) (b (si map "b")) (y (si map "y"))
         (c (intern-topic map :item-identifier "urn:c")))
    (add-topic-identifier c :subject-identifier "urn:a") (add-topic-identifier c :subject-identifier "urn:b")
    (let ((merged (canonical-topic a)))
      (check "representative:one-topic-for-three-handles" (and (eq merged (canonical-topic b)) (eq merged (canonical-topic c))))
      (check "representative:replaces-the-first-merged-topic-in-place"
             (equal (list x merged y) (topic-map-topics map))))))

(defun reifier-preference-tests ()
  ;; Staged: the reifier Topics are equal (same subject identifier) but reify items that become equal only after
  ;; their owners and types merge. The owners and types merge first; the reifiers then merge without conflict.
  (multiple-value-bind (target source) (scenario-reifier-first)
    (let ((r (si target "r")) (n (first (topic-names (si target "owner")))))
      (multiple-value-bind (map resolve) (import-map-content target source)
        (let ((s (si source "r")))
          (check "preference:reifier-topics-merge-after-their-owners" (eq (canonical-topic r) (funcall resolve s)))
          (check "preference:one-name-one-reifier"
                 (let ((names (topic-names (current (si map "owner")))))
                   (and (= 1 (length names)) (eq (canonical-topic r) (item-reifier (first names)))
                        (eq (canonical-topic-name n) (first names)))))
          (check "preference:inverse-is-consistent" (eq (canonical-topic-name n) (topic-reified (canonical-topic r))))
          (check "preference:model-valid" (topic-maps.tmdm::validate-map-reification map))))))
  ;; The conflict itself is still signalled when no nonconflicting merge is available, before any mutation.
  (multiple-value-bind (target source) (rejecting-scenario-reifier-conflict)
    (let* ((before (topic-maps.ctm.tests::map-state target)) (c (condition-from (lambda () (import-map-content target source)))))
      (check "preference:conflict-still-signalled" (and (typep c 'reification-error) (eq :reifier-conflict (reification-error-code c))))
      (check "preference:conflict-leaves-the-target-unchanged" (equal before (topic-maps.ctm.tests::map-state target))))))

;;; The search itself, against the b2eecffa search on unnormalized maps

(defun random-map (random topics)
  "An unnormalized Map: TOPICS raw Topics with identifiers from small pools (so equal Topics are frequent), raw
Associations and Names, and Reifiers set directly. Reifier Topics are often equal to each other while the items
they reify differ, which is the case the nonconflicting preference exists for. Sometimes one Topic reifies two
items (the fallback). Nothing is merged."
  (let* ((map (make-topic-map)) (single (not (zerop (random 4 random))))
         (made (loop repeat topics collect (topic-maps.tmdm::%make-topic map))))
    (flet ((pool (prefix n) (format nil "http://example.org/~A/~D" prefix (random n random))))
      (setf (topic-maps.tmdm::%topic-map-topics map) made)
      (dolist (topic made)
        (dotimes (k (random 3 random)) (push (pool "id" (* 2 topics)) (topic-maps.tmdm::%topic-item-identifiers topic)))
        (dotimes (k (random 2 random)) (push (pool "id" (* 2 topics)) (topic-maps.tmdm::%topic-subject-identifiers topic)))
        (when (zerop (random 4 random)) (push (pool "id" (* 2 topics)) (topic-maps.tmdm::%topic-subject-locators topic))))
      (let ((items nil))
        (dotimes (k (random 5 random))
          (let* ((type (pick random made)) (association (topic-maps.tmdm::%make-association map type)))
            (setf (topic-maps.tmdm::%association-roles association)
                  (list (topic-maps.tmdm::%make-association-role association type (pick random made))))
            (push association (topic-maps.tmdm::%topic-map-associations map))
            (push association items)))
        (dotimes (k (random 4 random))
          (let* ((owner (pick random made)) (name (topic-maps.tmdm::%make-topic-name (format nil "n~D" k) owner owner)))
            (push name (topic-maps.tmdm::%topic-names owner))
            (push name items)))
        (when (zerop (random 5 random)) (push map items))
        (let ((unused (copy-list made)))
          (dolist (item items)
            (when (zerop (random 3 random))
              ;; single reifiers: each Topic reifies at most one item; otherwise any Topic may be taken again
              (let ((reifier (if single
                                 (and unused (let ((r (pick random unused))) (setf unused (remove r unused)) r))
                                 (pick random made))))
                (when reifier (setf (topic-maps.tmdm::%item-reifier item) reifier))))))
        ;; two Topics that reify items now share an identifier: equal Reifiers of (usually) different items
        (let ((reifiers (remove-duplicates (loop for item in items for r = (topic-maps.tmdm::%item-reifier item) when r collect r))))
          (when (and (rest reifiers) (zerop (random 2 random)))
            (let ((iri (pool "reifier" topics)))
              (push iri (topic-maps.tmdm::%topic-subject-identifiers (first reifiers)))
              (push iri (topic-maps.tmdm::%topic-subject-identifiers (pick random (rest reifiers)))))))))
    map))

(defun selection (thunk)
  (handler-case (list :pair (let ((pair (funcall thunk))) (and pair (mapcar #'position-of-topic pair))))
    (reification-error (c) (list :refused (reification-error-code c)))))
(defvar *topics-in-order* nil)
(defun position-of-topic (topic) (position topic *topics-in-order* :test #'eq))

(defun differs-from-first-pair-p (map)
  "True when the oracle's choice is not simply the first equal pair: a nonconflicting pair was preferred."
  (let ((first-pair (ignore-errors (topic-maps.tmdm::equal-pair (topic-maps.tmdm::%topic-map-topics map)
                                                                  #'topic-maps.tmdm::equal-topics-p)))
        (chosen (ignore-errors (topic-maps.tmdm::scan-next-topic-merge map))))
    (and first-pair chosen (not (equal first-pair chosen)))))

(defun selection-equivalence-tests (&key (maps 4000) (seed 20261027))
  (let ((random (sb-ext:seed-random-state seed)) (pairs 0) (none 0) (refused 0) (preferred 0) (differences 0))
    (dotimes (n maps)
      (let* ((map (random-map random (+ 2 (random 14 random))))
             (*topics-in-order* (topic-maps.tmdm::%topic-map-topics map))
             (indexed (selection (lambda () (topic-maps.tmdm::next-topic-merge map))))
             (oracle (selection (lambda () (topic-maps.tmdm::scan-next-topic-merge map)))))
        (cond ((not (equal indexed oracle)) (incf differences))
              ((eq :refused (first oracle)) (incf refused))
              ((second oracle) (incf pairs) (when (differs-from-first-pair-p map) (incf preferred)))
              (t (incf none)))))
    (check "selection:indexed-equals-oracle-on-every-map" (zerop differences))
    (check "selection:maps-with-a-pair-exercised" (> pairs (floor maps 4)))
    (check "selection:maps-without-a-pair-exercised" (> none 0))
    (check "selection:nonconflicting-preference-exercised" (> preferred (floor maps 50)))
    (check "selection:fallback-exercised" (> refused (floor maps 100)))
    (list :maps maps :pair pairs :none none :preferred preferred :refused refused :differences differences)))

;;; Invalidation: the index lives for one search. After every mutation the search starts again from the map.

(defun merge-walk (random topics)
  "Follow normalization on a random unnormalized Map: at every step the indexed and the oracle search must agree,
then the oracle's pair is merged exactly as NORMALIZE-TOPIC-MAP does. Returns the number of steps and how the walk ended."
  (let ((map (random-map random topics)) (steps 0))
    (loop
      (let* ((*topics-in-order* (topic-maps.tmdm::%topic-map-topics map))
             (indexed (selection (lambda () (topic-maps.tmdm::next-topic-merge map))))
             (oracle (selection (lambda () (topic-maps.tmdm::scan-next-topic-merge map)))))
        (unless (equal indexed oracle) (return (values steps :differs)))
        (unless (and (eq :pair (first oracle)) (second oracle)) (return (values steps (if (eq :refused (first oracle)) :refused :done))))
        (let ((pair (topic-maps.tmdm::scan-next-topic-merge map)))
          (handler-case (topic-maps.tmdm::merge-two-topics map (first pair) (second pair))
            (error () (return (values steps :merge-refused))))
          (incf steps))))))

(defun invalidation-tests (&key (walks 800) (seed 20261028))
  (let ((random (sb-ext:seed-random-state seed)) (steps 0) (differs 0) (done 0) (multi-step 0))
    (dotimes (n walks)
      (multiple-value-bind (count how) (merge-walk random (+ 3 (random 12 random)))
        (incf steps count)
        (when (> count 1) (incf multi-step))
        (case how (:differs (incf differs)) (:done (incf done)))))
    (check "invalidation:agrees-after-every-merge-step" (zerop differs))
    (check "invalidation:walks-with-several-merges-exercised" (> multi-step (floor walks 10)))
    (check "invalidation:walks-reaching-a-fixed-point-exercised" (> done (floor walks 4)))
    (list :walks walks :merge-steps steps :several-merges multi-step :fixed-point done :differences differs)))

(defun stale-reference-tests ()
  ;; A pair found before a merge names Topics that are no longer live; the search after the merge never returns them.
  (let* ((map (make-topic-map)) (a (si map "a")) (b (si map "b")) (c (si map "c")))
    ;; make a~b and b~c equal without normalizing: raw identifiers, as an unnormalized staged map has them
    (push "urn:ab" (topic-maps.tmdm::%topic-subject-identifiers a)) (push "urn:ab" (topic-maps.tmdm::%topic-item-identifiers b))
    (push "urn:bc" (topic-maps.tmdm::%topic-subject-identifiers b)) (push "urn:bc" (topic-maps.tmdm::%topic-subject-identifiers c))
    (let ((before (topic-maps.tmdm::next-topic-merge map)))
      (check "stale:pair-found-before-the-merge" (equal (list a b) before))
      (topic-maps.tmdm::merge-two-topics map a b)
      (let ((after (topic-maps.tmdm::next-topic-merge map)) (merged (canonical-topic a)))
        (check "stale:positive-control-old-handles-are-no-longer-live" (and (not (live-p a map)) (not (live-p b map))))
        (check "stale:old-handles-forward-to-the-representative" (and (eq merged (canonical-topic a)) (eq merged (canonical-topic b))))
        (check "stale:search-after-the-merge-names-live-topics-only" (every (lambda (tpc) (live-p tpc map)) after))
        (check "stale:search-after-the-merge-finds-the-next-pair" (equal (list merged c) after))
        (check "stale:search-agrees-with-the-oracle" (equal after (topic-maps.tmdm::scan-next-topic-merge map)))))))

(defun reifier-mutation-tests ()
  ;; The reification inverse changes between searches (set, replace, clear); no search may use an earlier state.
  ;; The reifier Topics r, s precede the owners a, b, so the first equal pair is the reifiers' as soon as they are equal.
  (let* ((map (make-topic-map)) (r (si map "r")) (s (si map "s")) (a (si map "a")) (b (si map "b"))
         (x (add-name a "X" :type r)) (y (add-name b "Y" :type r)))
    (flet ((result (function)
             (handler-case (funcall function map) (reification-error (c) (list :refused (reification-error-code c)))))
           (sid (topic iri) (push iri (topic-maps.tmdm::%topic-subject-identifiers topic))))
      (flet ((agree (label)
               (check (concatenate 'string "reifier-mutation:" label)
                      (equal (result #'topic-maps.tmdm::next-topic-merge) (result #'topic-maps.tmdm::scan-next-topic-merge)))))
        (sid a "urn:ab") (sid b "urn:ab")
        (agree "equal-owners-no-reifier")
        (setf (topic-maps.tmdm::%item-reifier x) r (topic-maps.tmdm::%item-reifier y) s)
        (agree "reifiers-of-different-items-not-equal")
        (sid r "urn:rs") (sid s "urn:rs")
        (check "reifier-mutation:preferred-pair-skips-the-conflicting-reifiers"
               (equal (list a b) (topic-maps.tmdm::next-topic-merge map)))
        (check "reifier-mutation:the-first-equal-pair-is-the-conflicting-one"
               (equal (list r s) (topic-maps.tmdm::equal-pair (topic-map-topics map) #'topic-maps.tmdm::equal-topics-p)))
        (agree "equal-reifiers-of-different-items")
        (setf (topic-maps.tmdm::%item-reifier y) nil)
        (check "reifier-mutation:one-side-cleared-makes-the-reifiers-mergeable"
               (equal (list r s) (topic-maps.tmdm::next-topic-merge map)))
        (agree "one-reifier-cleared")
        (setf (topic-maps.tmdm::%item-reifier y) r)
        (check "reifier-mutation:one-topic-reifying-two-items-is-the-recorded-conflict"
               (equal '(:refused :reifier-conflict) (result #'topic-maps.tmdm::next-topic-merge)))
        (agree "one-topic-reifying-two-items-falls-back")))))

(defun stale-listed-topic-tests ()
  ;; Not reachable through the public API: a Topic that was replaced but is still listed. TOPIC-REIFIED resolves
  ;; it to its representative, so the pairwise search finds the pair although no identifier is shared; the index,
  ;; which would not, must not be trusted here.
  (let* ((map (make-topic-map)) (a (si map "a")) (b (si map "b")) (owner (si map "owner"))
         (name (add-name owner "N" :type a)))
    (setf (topic-maps.tmdm::%item-reifier name) a (topic-maps.tmdm::%topic-forward b) a)
    (check "stale-listed:pairwise-search-finds-the-replaced-topic-equal-to-its-representative"
           (equal (list a b) (topic-maps.tmdm::scan-next-topic-merge map)))
    (check "stale-listed:indexed-search-defers-to-it" (equal (list a b) (topic-maps.tmdm::next-topic-merge map)))))

;;; Whole reads: indexed and oracle searches run the same normalization to the same result

(defun random-document (random)
  "A CTM document with identifier statements from small pools, reified Names and Associations."
  (let ((tops (+ 3 (random 7 random))))
    (with-output-to-string (s)
      (flet ((topic () (format nil "t~D" (random tops random))) (iri (kind) (format nil "http://example.org/~A/~D" kind (random (* 2 tops) random))))
        (dotimes (i (+ 4 (random 14 random)))
          (ecase (random 8 random)
            (0 (format s "~A ~A .~%" (topic) (iri "i")))
            (1 (format s "~A ^ ~A .~%" (topic) (iri "i")))
            (2 (format s "~A = ~A .~%" (topic) (iri "l")))
            (3 (format s "~A - \"n~D\" .~%" (topic) (random 2 random)))
            (4 (format s "~A - \"n~D\" ~~ ~A .~%" (topic) (random 2 random) (topic)))
            (5 (format s "rel~D(r: ~A, q: ~A)~%" (random 2 random) (topic) (topic)))
            (6 (format s "rel~D(r: ~A, q: ~A) ~~ ~A~%" (random 2 random) (topic) (topic) (topic)))
            (7 (format s "~A ^ https://example.invalid/n/doc.ctm#~A .~%" (topic) (topic)))))))))

(defmacro with-oracle-search (&body body)
  `(progn
     (sb-int:encapsulate 'topic-maps.tmdm::next-topic-merge :oracle
                         (lambda (original map) (declare (ignore original)) (topic-maps.tmdm::scan-next-topic-merge map)))
     (unwind-protect (progn ,@body) (sb-int:unencapsulate 'topic-maps.tmdm::next-topic-merge :oracle))))

(defun counting-merges (thunk)
  "The outcome of THUNK and how many Topic merges it performed."
  (let ((merges 0))
    (sb-int:encapsulate 'topic-maps.tmdm::merge-two-topics :count
                        (lambda (original &rest arguments) (incf merges) (apply original arguments)))
    (unwind-protect (values (funcall thunk) (progn merges))
      (sb-int:unencapsulate 'topic-maps.tmdm::merge-two-topics :count))))

(defun reads-equal-tests (&key (documents 400) (seed 20261029))
  (let ((random (sb-ext:seed-random-state seed)) (read 0) (refused 0) (differences 0) (merging 0) (merges 0) (reified 0))
    (dotimes (n documents)
      (let ((text (random-document random)))
        (multiple-value-bind (indexed indexed-merges) (counting-merges (lambda () (document-outcome text)))
          (multiple-value-bind (oracle oracle-merges)
              (with-oracle-search (counting-merges (lambda () (document-outcome text))))
            (cond ((or (not (equal indexed oracle)) (/= indexed-merges oracle-merges)) (incf differences))
                  (t (incf merges indexed-merges)
                     (when (plusp indexed-merges) (incf merging))
                     (cond ((eq :read (first oracle))
                            (incf read)
                            (when (search "reifier=" (second oracle)) (incf reified)))
                           (t (incf refused)))))))))
    (check "reads:indexed-equals-oracle-on-every-document" (zerop differences))
    (check "reads:documents-read-exercised" (> read (floor documents 2)))
    (check "reads:refusals-exercised" (> refused 0))
    (check "reads:merging-documents-exercised" (> merging (floor documents 4)))
    (check "reads:reified-documents-exercised" (> reified (floor documents 20)))
    (list :documents documents :read read :refused refused :merging merging :merges merges :reified reified :differences differences)))

(defun positive-control-for-preference ()
  ;; The comparisons above can tell a search without the preference from the real one: always taking the first
  ;; equal pair refuses the staged import that the preference reads.
  (let ((first-pair-only (lambda (original map) (declare (ignore original))
                           (topic-maps.tmdm::equal-pair (topic-maps.tmdm::%topic-map-topics map) #'topic-maps.tmdm::equal-topics-p)))
        (staged (lambda () (import-outcome #'scenario-reifier-first))))
    (check "control:preferring-search-imports-the-staged-maps" (eq :read (first (outcome staged))))
    (sb-int:encapsulate 'topic-maps.tmdm::next-topic-merge :control first-pair-only)
    (unwind-protect (check "control:first-pair-search-refuses-them-with-a-reifier-conflict"
                           (equal '(:refused reification-error :reifier-conflict) (outcome staged)))
      (sb-int:unencapsulate 'topic-maps.tmdm::next-topic-merge :control))))

;;; Scale: documents of the size the reader was too slow for, read within a stated budget

(defun seconds-to (thunk)
  (let ((start (get-internal-real-time)))
    (values (funcall thunk) (float (/ (- (get-internal-real-time) start) internal-time-units-per-second) 1d0))))

(defun scale-tests (&key (topics 300) (associations 120) (budget 60))
  (multiple-value-bind (map seconds) (seconds-to (lambda () (read-case (chain-document topics (floor topics 4)))))
    (check "scale:chain-read" (= (+ topics 5 2 1 (- (floor topics 4))) (length (topic-map-topics map))))
    (check "scale:chain-associations" (= topics (length (topic-map-associations map))))
    (check (format nil "scale:chain-within-~Ds" budget) (< seconds budget))
    (let ((plain (read-case (reified-document associations))))
      (multiple-value-bind (map reified-seconds) (seconds-to (lambda () (read-case (reified-document associations :duplicate-every 3))))
        (check "scale:reified-associations" (and (= associations (length (topic-map-associations map)))
                                                 (= associations (length (topic-map-associations plain)))))
        (check "scale:duplicate-reifier-topics-merged-into-the-first" (= (length (topic-map-topics plain)) (length (topic-map-topics map))))
        (check "scale:every-association-keeps-its-reifier" (every #'item-reifier (topic-map-associations map)))
        (check (format nil "scale:reified-within-~Ds" budget) (< reified-seconds budget))
        (list :chain seconds :reified reified-seconds)))))

(defun run-tests ()
  (let ((topic-maps.ctm.tests::*checks* nil) (search nil) (walks nil) (reads nil) (seconds nil))
    (recorded-outcome-tests)
    (handle-tests nil)
    (handle-tests t)
    (representative-tests)
    (reifier-preference-tests)
    (stale-reference-tests)
    (stale-listed-topic-tests)
    (reifier-mutation-tests)
    (setf search (selection-equivalence-tests) walks (invalidation-tests) reads (reads-equal-tests))
    (positive-control-for-preference)
    (setf seconds (scale-tests))
    (format t "~&NORMALIZATION-INDEX-SELECTION: ~S~%NORMALIZATION-INDEX-WALKS: ~S~%NORMALIZATION-INDEX-READS: ~S~%NORMALIZATION-INDEX-SCALE: ~S~%"
            search walks reads seconds)
    (setf *last-checks* (reverse topic-maps.ctm.tests::*checks*))
    (format t "~&NORMALIZATION-INDEX-PASS: ~D checks; ~D documents, ~D staged imports and ~D rejections equal to the outcomes recorded at b2eecffa.~%"
            (length *last-checks*) (length *documents*) (length *scenarios*) (+ (length *rejections*) (length *rejecting-scenarios*)))
    *last-checks*))
