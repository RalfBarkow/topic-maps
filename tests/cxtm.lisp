(in-package #:topic-maps.ctm.tests)

(defparameter *cxtm-ids*
  '("simple" "subject-identifier" "subject-locator" "item-identifier" "name"
    "topic-subject-identifier" "topic-subject-identifier-wrapped" "topic-subject-identifier-duplicate"
    "topic-subject-locator" "topic-subject-locator-wrapped" "topic-subject-locator-semi"
    "topic-subject-locator-duplicate" "topic-item-identifier" "topic-item-identifier-wrapped"
    "topic-item-identifier-duplicate" "name-duplicate" "association" "association-binary"
    "association-binary-duplicate" "association-type-sid" "association-with-comment"
    "association-with-comment2" "association-with-comment3" "association-with-comment4"))
(defvar *last-cxtm-checks* nil)
(defvar *cxtm-results* nil)
(defvar *cxtm-corpus* nil)
(defstruct (extended-cxtm-map (:include topic-maps.tmdm:topic-map)) occurrences)
(defun cxtm (map &optional (base "https://example.invalid/a/doc.ctm"))
  (topic-maps.cxtm:canonicalize map :base-locator base))
(defun binary-file (path)
  (with-open-file (in path :element-type '(unsigned-byte 8))
    (let ((out (make-array (file-length in) :element-type '(unsigned-byte 8))))
      (read-sequence out in) out)))
(defun cxtm-condition (thunk)
  (handler-case (progn (funcall thunk) nil) (topic-maps.cxtm:cxtm-error (c) c)))
(defun map-state (map)
  ;; Includes object handles, all forward links, raw stored references/sets.
  (list (copy-list (topic-maps.tmdm::%topic-map-topics map))
        (copy-list (topic-maps.tmdm::%topic-map-associations map))
        (loop for topic in (topic-map-topics map) collect
          (list topic (topic-maps.tmdm::%topic-forward topic) (topic-parent topic)
                (topic-item-identifiers topic) (topic-subject-identifiers topic) (topic-subject-locators topic)
                (loop for n in (topic-names topic) collect
                  (list n (topic-maps.tmdm::%topic-name-forward n) (topic-name-parent n)
                        (topic-name-type n) (topic-name-value n)))
                (loop for o in (topic-maps.tmdm:topic-occurrences topic) collect
                  (list o (topic-maps.tmdm::%occurrence-forward o) (topic-maps.tmdm:occurrence-parent o)
                        (topic-maps.tmdm:occurrence-type o) (topic-maps.tmdm:occurrence-value o)
                        (topic-maps.tmdm:occurrence-datatype o) (topic-maps.tmdm:occurrence-item-identifiers o)))))
        (loop for a in (topic-maps.tmdm:topic-map-associations map) collect
          (list a (topic-maps.tmdm::%association-forward a) (topic-maps.tmdm:association-type a)
                (topic-maps.tmdm:association-parent a)
                (loop for r in (topic-maps.tmdm:association-roles a) collect
                  (list r (topic-maps.tmdm::%association-role-forward r)
                        (topic-maps.tmdm:association-role-type r) (topic-maps.tmdm:association-role-player r)
                        (topic-maps.tmdm:association-role-parent r)))))))
(defun compare-cxtm-cases ()
  (let ((corpus (topic-maps.test-foundation:discover-corpus)) (results nil))
    (dolist (name *cxtm-ids*)
      (let* ((id (format nil "ctm/in/~A.ctm" name))
             (case (first (topic-maps.test-foundation:select-cases corpus :id id)))
             (base (topic-maps.test-foundation:test-case-document-iri case)))
        (setf (topic-maps.test-foundation:test-case-clauses case)
              (append (topic-maps.test-foundation:test-case-clauses case)
                      '("CXTM 3.1" "CXTM 3.3" "CXTM 3.4" "CXTM 3.5" "CXTM 3.11" "CXTM 3.12"
                        "CXTM 3.13" "CXTM 3.17" "CXTM 3.18" "CXTM 3.19" "CXTM 3.20"
                        "CXTM 3.21" "CXTM 3.22" "CXTM 3.23" "CXTM 4.1" "CXTM 4.3"
                        "CXTM 4.4" "CXTM 4.5" "CXTM 4.6")
                      (when (search "name" name) '("CXTM 3.6" "CXTM 3.15" "CXTM 3.16" "CXTM 4.7"))
                      (when (search "association" name)
                        '("CXTM 3.9" "CXTM 3.10" "CXTM 3.15" "CXTM 4.10" "CXTM 4.11"))))
        (handler-case
            (let* ((map (deserialize-file (topic-maps.test-foundation:test-case-source-pathname case)
                                         :document-iri base :source-name id))
                   (before (map-state map))
                   (actual (topic-maps.cxtm:canonicalize-octets map :base-locator base))
                   (expected (binary-file (topic-maps.test-foundation:test-case-expected-baseline case)))
                   (different (mismatch actual expected)))
              (check (concatenate 'string id ":canonicalization-is-pure") (equal before (map-state map)))
              (topic-maps.test-foundation:record-result case (if different :cxtm-mismatch :cxtm-match)
                :diagnostics (when different (list (format nil "First different byte: ~D; actual ~D bytes, expected ~D bytes."
                                                          different (length actual) (length expected)))))
              (push (list :id id :base base :actual (cxtm map base)
                          :expected (uiop:read-file-string (topic-maps.test-foundation:test-case-expected-baseline case)
                                                          :external-format :utf-8)
                          :match (null different) :bytes (length actual)) results))
          ((or ctm-unsupported topic-maps.cxtm:cxtm-unsupported) (c)
            (topic-maps.test-foundation:record-result case :unsupported :diagnostics (list (princ-to-string c))))
          (error (c) (topic-maps.test-foundation:record-result case :execution-error :diagnostics (list (princ-to-string c)))))
        (format t "~&CXTM ~A: ~A~{ ~A~}~%" id (topic-maps.test-foundation:test-case-status case)
                (topic-maps.test-foundation:test-case-diagnostics case))))
    (let* ((case (first (topic-maps.test-foundation:select-cases corpus :id "ctm/invalid/prefix-undefined.ctm")))
           (condition (handler-case
                          (progn (deserialize-file (topic-maps.test-foundation:test-case-source-pathname case)
                                     :document-iri (topic-maps.test-foundation:test-case-document-iri case)) nil)
                        (undefined-prefix (c) c))))
      (check "cxtm-executor-retains-specific-negative-contract"
             (and condition (eq :undefined-prefix (error-code condition))))
      (topic-maps.test-foundation:record-result case :ctm-rejection :diagnostics (list (princ-to-string condition))))
    (setf results (nreverse results) *cxtm-corpus* corpus *cxtm-results* results)
    (check "24-original-byte-comparisons-pass"
           (and (= 24 (length results)) (every (lambda (r) (getf r :match)) results)))
    (check "25-imported-passes-248-unexecuted"
           (equal (getf (topic-maps.test-foundation:summarize-corpus corpus) :statuses)
                  '(:pass 25 :fail 0 :unsupported 0 :not-run 248)))))

(defun permutations (items)
  (if (null items) (list nil)
      (loop for item in items append
        (mapcar (lambda (rest) (cons item rest)) (permutations (remove item items :count 1))))))

(defun canonical-order-tests ()
  (let* ((map (read-text "z. a. a - \"Zulu\"; - \"Alpha\";. a - \"Middle\";."))
         (out (cxtm map)))
    (check "topic-order-not-insertion-order" (< (search "#a<" out) (search "#z<" out)))
    (check "name-value-order" (< (search "<value>Alpha" out) (search "<value>Middle" out) (search "<value>Zulu" out)))
    (check "names-numbered-within-parent" (and (search "<name number=\"1\">" out) (search "<name number=\"3\">" out)))
    (check "root-has-mandated-final-lf" (char= #\Newline (char out (1- (length out))))))
  (let ((map (topic-maps.tmdm:make-topic-map)))
    (let ((many (api-topic map "urn:ii:a")) (one (api-topic map "urn:ii:z")))
      (topic-maps.tmdm:add-topic-identifier many :item-identifier "urn:ii:b")
      (check "identifier-set-size-before-lexical-value"
             (< (search "urn:ii:z" (cxtm map)) (search "urn:ii:a" (cxtm map))))
      (topic-maps.tmdm:add-topic-identifier one :subject-locator "urn:sl:z")
      (check "topic-si-then-sl-then-ii" (< (search "urn:ii:a" (cxtm map)) (search "urn:sl:z" (cxtm map))))))
  (let* ((text "a(z: b, y: c) a(y: b) d(y: b)") (out (cxtm (read-text text))))
    (check "association-role-set-cardinality-first" (< (search "<association number=\"1\">" out)
                                                       (search "<association number=\"2\">" out)))
    (check "role-player-before-type" (search (format nil "<role number=\"1\">~%<player topicref=\"2\"></player>~%<type topicref=\"6\"></type>") out))
    (check "rolePlayed-parent-tie-order"
           (< (search "ref=\"association.1.role.1\"" out) (search "ref=\"association.3.role.1\"" out)
              (search "ref=\"association.2.role.1\"" out))))
  (let* ((map (read-text "a.")) (state (map-state map)))
    (uiop:with-temporary-file (:pathname path :type "cxtm")
      (topic-maps.cxtm:write-cxtm map path :base-locator "https://example.invalid/a/doc.ctm")
      (check "file-api-exact-canonical-octets"
             (equalp (binary-file path) (topic-maps.cxtm:canonicalize-octets map :base-locator "https://example.invalid/a/doc.ctm")))
      (check "file-api-does-not-mutate-map" (equal state (map-state map)))))
  (let ((reference nil))
    (dolist (order (permutations '("a" "b" "r" "s")))
      (dolist (reverse '(nil t))
        (let ((map (topic-maps.tmdm:make-topic-map)) (table (make-hash-table :test #'equal)))
          (dolist (id order) (setf (gethash id table) (api-topic map (concatenate 'string "urn:item:" id))))
          (dolist (roles (if reverse '(("s" "a") ("r" "b")) '(("r" "b") ("s" "a"))))
            (topic-maps.tmdm:make-association map (gethash "a" table)
                                            (list (mapcar (lambda (id) (gethash id table)) roles))))
          (let ((out (cxtm map)))
            (unless reference (setf reference out))
            (check (format nil "construction-permutation:~{~A~}:~A" order reverse) (string= out reference)))))))
  (let* ((map (read-text "a(r: b, s: c)")) (expected (cxtm map))
         (*print-base* 16) (*print-radix* t) (*print-escape* nil))
    (check "independent-of-lisp-printer-settings" (string= expected (cxtm map)))))

(defun canonical-merge-tests ()
  ;; Force Topic, Name, Association and Role replacement in one connected map.
  (let* ((map (read-text "a - \"Same\";. b - \"Same\";. a(r: a, s: b) b(r: b, s: a)"))
         (topics (topic-map-topics map))
         (a (find "https://example.invalid/a/doc.ctm#a" topics :test #'string= :key (lambda (x) (first (topic-item-identifiers x)))))
         (b (find "https://example.invalid/a/doc.ctm#b" topics :test #'string= :key (lambda (x) (first (topic-item-identifiers x)))))
         (r (find "https://example.invalid/a/doc.ctm#r" topics :test #'string= :key (lambda (x) (first (topic-item-identifiers x)))))
         (s (find "https://example.invalid/a/doc.ctm#s" topics :test #'string= :key (lambda (x) (first (topic-item-identifiers x)))))
         (names (append (topic-names a) (topic-names b)))
         (associations (topic-maps.tmdm:topic-map-associations map))
         (roles (mapcan #'topic-maps.tmdm:association-roles (copy-list associations))))
    (topic-maps.tmdm:merge-topics a b)
    (topic-maps.tmdm:merge-topics r s)
    (let* ((expected (read-text "a ^<#b>; - \"Same\";. r ^<#s>;. a(r: a)"))
           (state (map-state map)) (out (cxtm map)))
      (check "all-four-merge-kinds-canonical-output" (string= out (cxtm expected)))
      (check "merged-output-is-pure" (equal state (map-state map)))
      (check "old-topic-alias-survives-canonicalization" (eq (topic-maps.tmdm:canonical-topic a) (topic-maps.tmdm:canonical-topic b)))
      (check "old-name-aliases-survive-canonicalization" (eq (topic-maps.tmdm:canonical-topic-name (first names)) (topic-maps.tmdm:canonical-topic-name (second names))))
      (check "old-association-aliases-survive-canonicalization"
             (apply #'eq (mapcar #'topic-maps.tmdm:canonical-association associations)))
      (check "all-old-role-aliases-survive-canonicalization"
             (every (lambda (role) (eq (topic-maps.tmdm:canonical-association-role role)
                                      (topic-maps.tmdm:canonical-association-role (first roles)))) roles))
      (check "postmerge-reference-integrity" (association-invariants map)))))

(defun unicode-and-locator-tests ()
  (let ((topic-maps.cxtm::*base-locator* "http://example.org/a/b.ctm?query#fragment")
        (topic-maps.cxtm::*locator-cache* (make-hash-table :test #'equal)))
    (dolist (pair '(("http://example.org/a/b.ctm#id" "#id") ("http://example.org/a/c.ctm#id" "c.ctm#id")
                    ("http://example.org/x" "x") ("http://other.example/x" "http://other.example/x")
                    ("http://example.org/a/b.ctmextra" "extra") ("http://example.org/a/b.ctm" "")))
      (check (concatenate 'string "normative-locator-prefix:" (first pair))
             (string= (second pair) (topic-maps.cxtm::normalized-locator (first pair))))))
  (dolist (base '("http://example.org/a/" "http://example.org/a///" "urn:base:document"))
    (let ((topic-maps.cxtm::*base-locator* base) (topic-maps.cxtm::*locator-cache* (make-hash-table :test #'equal)))
      (check (concatenate 'string "trailing-slash-or-opaque:" base)
             (string= "#x" (topic-maps.cxtm::normalized-locator (concatenate 'string (string-right-trim "/" base) "#x"))))))
  (dolist (pair '(((101 769) (233)) ((65 778) (197)) ((8491) (197)) ((4352 4449 4520) (44033))
                  ((44033) (44033)) ((97 769 807) (225 807)) ((65 768 769) (192 769))
                  ((769 768) (769 768)) ((97 847 769) (97 847 769)) ((832) (768))))
    (let ((text (map 'string #'code-char (first pair))) (expected (map 'string #'code-char (second pair))))
      (check (format nil "nfc:~S" (first pair)) (string= expected (topic-maps.cxtm::nfc text)))))
  (let* ((map (read-text "a."))
         (value (concatenate 'string "<&>\"" (string #\Return) (string #\Newline) (string #\Tab)
                             (map 'string #'code-char '(101 769 #x1f600)))))
    (topic-maps.tmdm:add-default-name (first-topic map) value)
    (let ((out (cxtm map)) (bytes (topic-maps.cxtm:canonicalize-octets map :base-locator "https://example.invalid/a/doc.ctm")))
      (check "canonical-xml-character-escaping" (search "&lt;&amp;&gt;\"&#xD;" out))
      (check "nfc-name-emitted" (find (code-char 233) out))
      (check "utf8-supplementary-character" (search #(#xf0 #x9f #x98 #x80) bytes))
      (check "no-bom-mandated-final-newline" (and (= 60 (aref bytes 0)) (= 10 (aref bytes (1- (length bytes))))))))
  (let ((map (read-text "a.")))
    (topic-maps.tmdm:add-default-name (first-topic map) (string (code-char 0)))
    (check "xml-invalid-character-explicit-error"
           (eq :xml-character (topic-maps.cxtm:error-code (cxtm-condition (lambda () (cxtm map)))))))
  (check "newer-unicode-character-explicit-unsupported"
         (typep (cxtm-condition (lambda () (topic-maps.cxtm::nfc (string (code-char #x1c89)))))
                'topic-maps.cxtm:cxtm-unsupported))
  (check "base-locator-required" (eq :invalid-base-locator (topic-maps.cxtm:error-code
                                    (cxtm-condition (lambda () (topic-maps.cxtm:canonicalize (read-text "a.")))))))
  (check "unsupported-model-input-explicit"
         (typep (cxtm-condition (lambda () (cxtm '(:occurrence "unsupported")))) 'topic-maps.cxtm:cxtm-unsupported))
  (check "extended-model-property-not-silently-discarded"
         (eq :unsupported-information-item
             (topic-maps.cxtm:error-code (cxtm-condition
               (lambda () (cxtm (make-extended-cxtm-map :occurrences '("unsupported"))))))))
  (let* ((map (read-text "a(r: b)"))
         (a (first (topic-maps.tmdm:topic-map-associations map)))
         (role (first (topic-maps.tmdm:association-roles a)))
         (foreign (api-topic (topic-maps.tmdm:make-topic-map) "urn:foreign")))
    ;; Deliberately corrupt only this fixture to exercise defensive validation.
    (setf (topic-maps.tmdm::%association-role-player role) foreign)
    (let ((state (map-state map)))
      (check "foreign-role-player-explicit-error"
             (eq :invalid-topic-reference (topic-maps.cxtm:error-code (cxtm-condition (lambda () (cxtm map))))))
      (check "error-path-is-pure" (equal state (map-state map)))))
  (let ((map (topic-maps.tmdm:make-topic-map)))
    (api-topic map (concatenate 'string "urn:id:" (map 'string #'code-char '(101 769))))
    (api-topic map (concatenate 'string "urn:id:" (string (code-char 233))))
    (check "nfc-identity-tie-explicit-unsupported"
           (eq :ambiguous-topic-order (topic-maps.cxtm:error-code (cxtm-condition (lambda () (cxtm map))))))))

(defun run-cxtm-tests ()
  (let ((*checks* nil))
    (compare-cxtm-cases)
    (canonical-order-tests) (canonical-merge-tests) (canonical-graph-tests) (unicode-and-locator-tests)
    (setf *last-cxtm-checks* (nreverse *checks*))
    (format t "~&CXTM-PASS: ~D checks; 24 original byte comparisons; 25 imported PASS, 248 NOT-RUN.~%" (length *last-cxtm-checks*)) t))

(defun write-cxtm-report (validation-path detail-path &key additional-checks
                         (scope "Slice 4: 24 byte-equal original baselines, explicit base locator"))
  (topic-maps.test-foundation:write-validation-report *cxtm-corpus* validation-path
    :infrastructure-checks topic-maps.tests::*last-checks*
    :implementation (list :ctm t :tmdm t :cxtm t :scope scope))
  (with-open-file (out detail-path :direction :output :if-exists :supersede :if-does-not-exist :create)
    (topic-maps.test-foundation::emit-json-value
     (topic-maps.test-foundation::fields
      "kind" "cxtm-byte-equality" "passed" (+ (length *last-cxtm-checks*) (length additional-checks)) "failed" 0
      "checkOutcomeInterpretation" "passed/failed count local assertions; contractCounts and case status report imported comparisons independently"
      "contractCounts" (topic-maps.test-foundation::fields "pass" (count-if (lambda (r) (getf r :match)) *cxtm-results*)
                                                         "fail" (count-if-not (lambda (r) (getf r :match)) *cxtm-results*))
      "checks" (topic-maps.test-foundation::json-array (append *last-cxtm-checks* additional-checks))
      "cases" (topic-maps.test-foundation::json-array
       (loop for r in *cxtm-results* collect
         (topic-maps.test-foundation::fields "id" (getf r :id) "baseLocator" (getf r :base)
           "status" (if (getf r :match) "pass" "fail") "byteCount" (getf r :bytes)
           "actualCXTM" (getf r :actual) "expectedCXTM" (getf r :expected))))) out)
    (terpri out)))

(defun canonical-graph-tests ()
  ;; The 64 independent edge sets induce different identity partitions. Compare
  ;; full CXTM after both edge insertion orders, including all live references.
  (let ((possible '((0 1) (0 2) (0 3) (1 2) (1 3) (2 3))))
    (dotimes (mask 64)
      (let ((edges (loop for edge in possible for bit from 0 when (logbitp bit mask) collect edge))
            (reference nil))
        (dolist (reverse '(nil t))
          (let* ((map (topic-maps.tmdm:make-topic-map))
                 (topics (loop for i below 4 collect (api-topic map (format nil "urn:node:~D" i))))
                 (a (topic-maps.tmdm:make-association map (first topics)
                      (list (list (second topics) (third topics)) (list (third topics) (fourth topics))))))
            (declare (ignore a))
            (dolist (edge (if reverse (reverse edges) edges))
              (dolist (node edge)
                (topic-maps.tmdm:add-topic-identifier (nth node topics) :subject-identifier
                  (format nil "urn:edge:~D:~D" (first edge) (second edge)))))
            (let* ((state (map-state map)) (out (cxtm map)))
              (if reference
                  (check (format nil "canonical-graph:~D:edge-order-independent" mask) (string= reference out))
                  (setf reference out))
              (check (format nil "canonical-graph:~D:~A:pure" mask reverse) (equal state (map-state map)))
              (check (format nil "canonical-graph:~D:~A:references" mask reverse) (association-invariants map)))))))))
