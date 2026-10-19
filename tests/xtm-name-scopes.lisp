(in-package #:topic-maps.xtm.tests)

(defparameter *scope-original-specs*
  '(("name-scope" 3 "Emne" :default ("norwegian"))
    ("name-scope-multiple" 4 "Emne" :default ("norwegian" "danish"))
    ("name-scope-duplicate" 3 "Emne" :default ("norwegian"))
    ("name-scope-duplicate-merged" 3 "Emne" :default ("no" "norwegian"))
    ("name-type-scope" 3 "Emner" :plural ("norwegian"))))

(defun scope-eq-p (actual expected)
  (let ((expected (remove-duplicates expected :test #'eq)))
    (and (= (length actual) (length expected))
         (every (lambda (theme) (member theme actual :test #'eq)) expected))))

(defun scope-original-model-checks (spec map)
  (destructuring-bind (id count value type-key theme-ids) spec
    (let* ((owner (by-id map "topic")) (names (topic-names owner)) (name (first names))
           (type (if (eq type-key :default) (by-si map (default-name-type-identifier))
                     (find-if (lambda (topic) (member "http://psi.ontopia.net/xtm/basename/#plural"
                       (topic-item-identifiers topic) :test #'equal)) (topic-map-topics map))))
           (themes (mapcar (lambda (id) (by-id map id)) theme-ids))
           (label (concatenate 'string "scope-original:" id)))
      (check (concatenate 'string label ":counts")
        (and (= count (length (topic-map-topics map))) (null (topic-map-associations map))
             (= 1 (loop for topic in (topic-map-topics map) sum (length (topic-names topic))))))
      (check (concatenate 'string label ":parent-type-value-eq")
        (and owner type (= 1 (length names)) (eq name (canonical-topic-name name))
          (eq owner (topic-name-parent name)) (eq type (topic-name-type name))
          (equal value (topic-name-value name))))
      (check (concatenate 'string label ":canonical-theme-set-eq")
        (and (every #'identity themes) (scope-eq-p (topic-name-scope name) themes) (names-current-p map)))
      (check (concatenate 'string label ":no-excluded-properties")
        (and (null (topic-name-variants name)) (null (item-identifiers name)) (null (item-reifier name))))
      (check (concatenate 'string label ":exact-topic-identities")
        (and (equal (list (concatenate 'string *document* "#topic")) (topic-item-identifiers owner))
          (null (topic-subject-identifiers owner)) (null (topic-subject-locators owner))
          (every (lambda (theme)
            (and (null (topic-subject-identifiers theme)) (null (topic-subject-locators theme))
              (same-identifiers-p (topic-item-identifiers theme)
                (loop for id in theme-ids when (eq theme (by-id map id)) collect (concatenate 'string *document* "#" id))))) themes)
          (if (eq type-key :default)
            (and (null (topic-item-identifiers type))
              (equal (list (default-name-type-identifier)) (topic-subject-identifiers type)))
            (and (equal '("http://psi.ontopia.net/xtm/basename/#plural") (topic-item-identifiers type))
                 (null (topic-subject-identifiers type)))))))))

(defun scope-original-contracts ()
  (setf *scope-outputs* nil)
  (dolist (spec *scope-original-specs*)
    (let* ((name (first spec)) (id (format nil "xtm2/in/~A.xtm" name))
           (*document* (concatenate 'string "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/" id))
           (source (corpus-path id)) (baseline (corpus-path (format nil "xtm2/baseline/~A.xtm.cxtm" name)))
           (raw (file-bytes source)) (copy (copy-seq raw)) (expected (file-bytes baseline))
           (case (topic-maps.test-foundation:make-test-case :id id :category :valid :source-pathname source
             :document-iri *document* :expected-outcome :cxtm-equal :expected-baseline baseline
             :clauses '("XTM 2.0 4.2,4.10,4.11,4.13,4.14,4.20" "TMDM 5.3.3,5.4,6.2,6.3" "CXTM 3,4")))
           (map nil) (actual nil) (c nil) (before nil))
      (setf *cases* (append *cases* (list case)))
      (handler-case (setf map (deserialize-octets raw :document-iri *document* :source-key id)
                         before (name-state map)
                         actual (topic-maps.cxtm:canonicalize-octets map :base-locator *document*))
        (error (condition) (setf c condition)))
      ;; A reader or model failure can never satisfy this positive contract.
      (when (null c)
        (handler-case (scope-original-model-checks spec map) (error (condition) (setf c condition))))
      (record-original-result case actual expected c)
      (push (topic-maps.test-foundation::fields "id" id "documentIRI" *document* "sourceKey" id
        "sourceBytes" (length raw) "sourceHex" (format nil "~{~2,'0X~}" (coerce raw 'list))
        "sourceText" (babel:octets-to-string raw :encoding :utf-8)
        "actualCXTM" (when actual (babel:octets-to-string actual :encoding :utf-8))
        "expectedCXTM" (babel:octets-to-string expected :encoding :utf-8)
        "actualBytes" (when actual (length actual)) "expectedBytes" (length expected)
        "firstDifferentByte" (when actual (mismatch actual expected))
        "condition" (negative-condition-data c) "model" (when map (name-model-data map))
        "status" (string-downcase (string (topic-maps.test-foundation:test-case-status case)))) *scope-outputs*)
      (when c (error c))
      (check (concatenate 'string "scope-original:" name ":byte-exact") (equalp actual expected))
      (check (concatenate 'string "scope-original:" name ":source-preserved") (equalp raw copy))
      (check (concatenate 'string "scope-original:" name ":pure") (equal before (name-state map)))
      (check (concatenate 'string "scope-original:" name ":deterministic")
             (equalp actual (topic-maps.cxtm:canonicalize-octets map :base-locator *document*)))
      (check (concatenate 'string "scope-original:" name ":repeat-pure") (equal before (name-state map)))
      (let ((other (deserialize-octets raw :document-iri *document* :source-key "different-name-provenance")))
        (check (concatenate 'string "scope-original:" name ":source-key-only-provenance")
          (and (equalp (name-model-data map) (name-model-data other))
               (equalp actual (topic-maps.cxtm:canonicalize-octets other :base-locator *document*)))))))
  (setf *scope-outputs* (nreverse *scope-outputs*))
  (check "scope-originals:48-unique-case-records"
    (and (= 48 (length *cases*)) (= 41 (count :valid *cases* :key #'topic-maps.test-foundation:test-case-category))
      (= 48 (length (remove-duplicates *cases* :key #'topic-maps.test-foundation:test-case-id :test #'equal))))))

;; These wrappers keep all counterprobes in the existing harness and report
;; format, while retaining the historical Name-controls collection separately.
(defun scope-control (label body verify)
  (let ((*name-controls* nil))
    (name-control (concatenate 'string "scope:" label) body verify)
    (setf *scope-controls* (append *scope-controls* (reverse *name-controls*)))))
(defun scope-error-control (label body class code)
  (let ((*name-controls* nil))
    (name-error-control (concatenate 'string "scope:" label) body class code)
    (setf *scope-controls* (append *scope-controls* (reverse *name-controls*)))))
(defun staged-scope-control (label body after-step verify)
  (let ((*name-controls* nil))
    (staged-name-control (concatenate 'string "scope:" label) body after-step verify)
    (setf *scope-controls* (append *scope-controls* (reverse *name-controls*)))))

(defun scope-positive-controls ()
  (scope-control "single-forward" "<topic id='a'><name><scope><topicRef href='#s'/></scope><value>N</value></name></topic><topic id='s'/>"
    (lambda (map) (check "scope:single-forward-eq"
      (scope-eq-p (topic-name-scope (first (topic-names (by-id map "a")))) (list (by-id map "s"))))))
  (scope-control "set-order-and-duplicates"
    "<topic id='a'><name><scope><topicRef href='#s'/><topicRef href='#t'/><topicRef href='#s'/></scope><value>N</value></name><name><scope><topicRef href='#t'/><topicRef href='#s'/></scope><value>N</value></name></topic>"
    (lambda (map) (let ((names (topic-names (by-id map "a"))))
      (check "scope:set-order-duplicate-name-collapse"
        (and (= 1 (length names)) (scope-eq-p (topic-name-scope (first names)) (list (by-id map "s") (by-id map "t"))))))))
  (scope-control "different-and-unconstrained"
    "<topic id='a'><name><scope><topicRef href='#s'/></scope><value>N</value></name><name><scope><topicRef href='#t'/></scope><value>N</value></name><name><value>N</value></name></topic>"
    (lambda (map) (let* ((names (topic-names (by-id map "a"))) (types (mapcar #'topic-name-type names)))
      (check "scope:different-sets-do-not-merge"
        (and (= 3 (length names)) (= 3 (length (remove-duplicates names :test #'eq)))
             (every (lambda (type) (eq type (first types))) types)
             (scope-eq-p (topic-name-scope (first names)) (list (by-id map "s")))
             (scope-eq-p (topic-name-scope (second names)) (list (by-id map "t")))
             (null (topic-name-scope (third names))))))))
  (scope-control "type-theme-same"
    "<topic id='a'><name><type><topicRef href='#s'/></type><scope><topicRef href='#s'/></scope><value>N</value></name><name><type><topicRef href='#s'/></type><value>N</value></name></topic>"
    (lambda (map) (let ((names (topic-names (by-id map "a"))) (theme (by-id map "s")))
      (check "scope:type-and-scope-separate-properties"
        (and (= 2 (length names)) (eq theme (topic-name-type (first names)))
          (eq theme (first (topic-name-scope (first names))))
          (eq theme (topic-name-type (second names))) (null (topic-name-scope (second names))))))))
  (dolist (kind '("subjectIdentifier" "itemIdentity"))
    (scope-control (concatenate 'string "reference-hit:" kind)
      (format nil "<topic id='s'><~A href='https://themes.invalid/map#theme'/></topic><topic id='a'><name><scope><topicRef href='https://themes.invalid/map#theme'/></scope><value>N</value></name></topic>" kind)
      (lambda (map)
        (let* ((theme (by-id map "s")) (scope (topic-name-scope (first (topic-names (by-id map "a"))))))
          (check (concatenate 'string "scope:reference-hit-no-extra-II:" kind)
            (and (eq theme (first scope)) (= 1 (length scope)) (= 3 (length (topic-map-topics map)))
              (same-identifiers-p (topic-item-identifiers theme)
                (append (list (concatenate 'string *document* "#s"))
                  (when (equal kind "itemIdentity") '("https://themes.invalid/map#theme"))))))))))
  (scope-control "subject-locator-is-not-reference-hit"
    "<topic id='s'><subjectLocator href='https://themes.invalid/map#theme'/></topic><topic id='a'><name><scope><topicRef href='https://themes.invalid/map#theme'/></scope><value>N</value></name></topic>"
    (lambda (map) (let ((theme (first (topic-name-scope (first (topic-names (by-id map "a")))))))
      (check "scope:SL-only-reference-creates-II-placeholder"
        (and (not (eq theme (by-id map "s"))) (= 4 (length (topic-map-topics map)))
             (equal '("https://themes.invalid/map#theme") (topic-item-identifiers theme)))))))
  (scope-control "percent-utf8-external-no-fetch"
    "<topic id='a'><name><scope><topicRef href='https://unfetched.invalid/map#th%C3%A8me'/></scope><value>N</value></name></topic>"
    (lambda (map) (check "scope:percent-utf8-existing-IRI-path"
      (equal '("https://unfetched.invalid/map#thème")
        (topic-item-identifiers (first (topic-name-scope (first (topic-names (by-id map "a"))))))))))
  (scope-control "owner-theme"
    "<topic id='a'><name><scope><topicRef href='#a'/></scope><value>N</value></name></topic>"
    (lambda (map) (check "scope:owner-can-be-theme-eq"
      (eq (by-id map "a") (first (topic-name-scope (first (topic-names (by-id map "a")))))))))
  (scope-control "default-type-is-theme"
    "<topic id='s'><subjectIdentifier href='http://psi.topicmaps.org/iso13250/model/topic-name'/></topic><topic id='a'><name><scope><topicRef href='#s'/></scope><value>N</value></name></topic>"
    (lambda (map) (let ((name (first (topic-names (by-id map "a")))))
      (check "scope:default-type-theme-eq"
        (and (= 2 (length (topic-map-topics map))) (eq (by-id map "s") (topic-name-type name))
             (eq (topic-name-type name) (first (topic-name-scope name))))))))
  (scope-control "parent-merge-scoped-names"
    "<topic id='a'><name><scope><topicRef href='#s'/><topicRef href='#t'/></scope><value>N</value></name></topic><topic id='b'><name><scope><topicRef href='#t'/><topicRef href='#s'/></scope><value>N</value></name></topic><topic id='bridge'><itemIdentity href='#a'/><itemIdentity href='#b'/></topic>"
    (lambda (map) (check "scope:parent-merge-set-equality"
      (and (eq (by-id map "a") (by-id map "b")) (= 1 (length (topic-names (by-id map "a")))))))))

(defun scope-theme-merge-controls ()
  (dolist (kind '("subjectIdentifier" "subjectLocator" "itemIdentity"))
    (let ((themes nil) (names nil) (duplicate-name nil) (label (concatenate 'string "theme-merge:" kind)))
      (staged-scope-control label
        (concatenate 'string
          "<topic id='a'><name><scope><topicRef href='#s1'/></scope><value>N</value></name><name><scope><topicRef href='#s2'/></scope><value>N</value></name><name><scope><topicRef href='#s1'/><topicRef href='#s2'/><topicRef href='#s1'/></scope><value>D</value></name></topic>"
          (if (equal kind "itemIdentity")
            "<topic id='s1'/><topic id='s2'/><topic id='bridge'><itemIdentity href='#s1'/><itemIdentity href='#s2'/></topic>"
            (format nil "<topic id='s1'><~A href='urn:one'/></topic><topic id='s2'><~A href='urn:two'/></topic><topic id='bridge'><~A href='urn:one'/><~A href='urn:two'/></topic>" kind kind kind kind)))
        (lambda (map step)
          (when (= step 1)
            (setf themes (list (by-id map "s1") (by-id map "s2"))
                  names (subseq (topic-names (by-id map "a")) 0 2)
                  duplicate-name (third (topic-names (by-id map "a")))))
          (when (= step 3)
            (check (concatenate 'string "scope:" label ":distinct-before")
              (and (= 3 (length (topic-names (by-id map "a"))))
                   (not (eq (canonical-topic (first themes)) (canonical-topic (second themes))))
                   (not (eq (first names) (second names))) (= 2 (length (topic-name-scope duplicate-name)))))))
        (lambda (map)
          (let* ((theme (by-id map "bridge")) (owner (by-id map "a"))
                 (name (find "N" (topic-names owner) :key #'topic-name-value :test #'equal))
                 (before (name-state map)))
            (check (concatenate 'string "scope:" label ":canonical-themes-and-retained-names-eq")
              (and (= 2 (length (topic-names owner)))
                (every (lambda (old) (eq theme (canonical-topic old))) themes)
                (every (lambda (old) (and (eq name (canonical-topic-name old))
                  (eq owner (topic-name-parent old)) (scope-eq-p (topic-name-scope old) (list theme)))) names)
                (scope-eq-p (topic-name-scope duplicate-name) (list theme))))
            (topic-maps.cxtm:canonicalize-octets map :base-locator *document*)
            (check (concatenate 'string "scope:" label ":cxtm-pure-retained-handles")
              (and (equal before (name-state map))
                (every (lambda (old) (eq name (canonical-topic-name old))) names)))))))))

(defun scope-syntax-controls ()
  (dolist (spec '(("empty" "<scope/>" :empty-scope)
    ("whitespace-only" "<scope> </scope>" :empty-scope)
    ("text-without-topicRef" "<scope>text</scope>" :unexpected-text)
    ("wrong-child" "<scope><subjectIdentifier href='urn:s'/></scope>" :unexpected-element)
    ("attribute" "<scope other='x'><topicRef href='#s'/></scope>" :unexpected-attribute)
    ("multiple" "<scope><topicRef href='#s'/></scope><scope><topicRef href='#t'/></scope>" :duplicate-name-scope)
    ("before-later-type" "<scope><topicRef href='#s'/></scope><type><topicRef href='#t'/></type>" :element-order)
    ("missing-href" "<scope><topicRef/></scope>" :missing-attribute)
    ("empty-href" "<scope><topicRef href=''/></scope>" :invalid-topic-ref)
    ("no-fragment" "<scope><topicRef href='urn:s'/></scope>" :invalid-topic-ref)
    ("invalid-fragment" "<scope><topicRef href='#2bad'/></scope>" :invalid-topic-ref)
    ("bad-percent" "<scope><topicRef href='#s%GG'/></scope>" :invalid-percent-escape)
    ("bad-utf8" "<scope><topicRef href='#s%FF'/></scope>" :invalid-percent-utf8)
    ("bad-IRI" "<scope><topicRef href='#s t'/></scope>" :invalid-iri)
    ("ref-attribute" "<scope><topicRef href='#s' other='x'/></scope>" :unexpected-attribute)
    ("nested-ref" "<scope><topicRef href='#s'><value>N</value></topicRef></scope>" :unexpected-child)
    ("namespace" "<scope xmlns='urn:foreign'><topicRef href='#s'/></scope>" :invalid-namespace)
    ("ref-namespace" "<scope><topicRef xmlns='urn:foreign' href='#s'/></scope>" :invalid-namespace)))
    (scope-error-control (first spec) (format nil "<topic id='a'><name>~A<value>N</value></name></topic>" (second spec)) 'xtm-rejection (third spec)))
  (scope-error-control "after-value" "<topic id='a'><name><value>N</value><scope><topicRef href='#s'/></scope></name></topic>" 'xtm-rejection :element-order)
  (dolist (spec '(("variant-stays-unsupported" "<name><scope><topicRef href='#s'/></scope><value>N</value><variant><scope><topicRef href='#v'/></scope><resourceData>V</resourceData></variant></name>" :unsupported-construct)
    ("name-II-stays-unsupported" "<name><itemIdentity href='#n'/><scope><topicRef href='#s'/></scope><value>N</value></name>" :unsupported-construct)
    ("name-reifier-stays-unsupported" "<name reifier='#r'><scope><topicRef href='#s'/></scope><value>N</value></name>" :reification)))
    (scope-error-control (first spec) (format nil "<topic id='a'>~A</topic>" (second spec)) 'xtm-unsupported (third spec)))
  (scope-error-control "occurrence-stays-unsupported" "<topic id='a'><occurrence><type><topicRef href='#t'/></type><scope><topicRef href='#s'/></scope><resourceData>V</resourceData></occurrence></topic>" 'xtm-unsupported :unsupported-construct)
  (scope-error-control "association-stays-unsupported" "<association><type><topicRef href='#t'/></type><scope><topicRef href='#s'/></scope><role><type><topicRef href='#r'/></type><topicRef href='#a'/></role></association>" 'xtm-unsupported :unsupported-construct))

(defun scope-tests ()
  (setf *scope-controls* nil)
  (scope-positive-controls) (scope-theme-merge-controls) (scope-syntax-controls))
