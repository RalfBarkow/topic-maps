(in-package #:topic-maps.xtm.tests)

(defparameter *iid-original-specs* '(("itemid-name" 1) ("name-duplicate-iid" 2)))

(defun iid-original-model-checks (spec map raw)
  (let* ((label (concatenate 'string "iid-original:" (first spec)))
         (owner (by-id map "topic")) (names (topic-names owner)) (name (first names))
         (type (by-si map (default-name-type-identifier)))
         (locator (concatenate 'string *document* "#the-name"))
         (root (topic-maps.xml:parse-octets raw (make-instance 'topic-maps.xtm::source-handler)))
         (source-names (topic-maps.xtm::elements (first (topic-maps.xtm::elements root)))))
    (check (concatenate 'string label ":original-source-relationships")
      (and (= (second spec) (length source-names))
        (every (lambda (node)
          (let ((children (topic-maps.xtm::elements node)))
            (and (equal "name" (topic-maps.xtm::node-name node)) (= 2 (length children))
              (equal "itemIdentity" (topic-maps.xtm::node-name (first children)))
              (equal "#the-name" (topic-maps.xtm::attr (first children) "href"))
              (equal "value" (topic-maps.xtm::node-name (second children)))
              (equal '("Topic") (topic-maps.xtm::node-children (second children)))))) source-names)))
    (check (concatenate 'string label ":counts-parent-type-value-eq")
      (and (= 2 (length (topic-map-topics map))) (null (topic-map-associations map))
        (= 1 (length names)) (null (topic-names type))
        (eq name (canonical-topic-name name)) (eq owner (topic-name-parent name))
        (eq type (topic-name-type name)) (equal "Topic" (topic-name-value name)) (names-current-p map)))
    (check (concatenate 'string label ":identifier-owned-by-name-only")
      (and (equal (list locator) (item-identifiers name))
        (equal (list (concatenate 'string *document* "#topic")) (topic-item-identifiers owner))
        (null (topic-subject-identifiers owner)) (null (topic-subject-locators owner))
        (null (item-identifiers type)) (equal (list (default-name-type-identifier)) (topic-subject-identifiers type))
        (null (topic-subject-locators type)) (null (item-identifiers map))
        (eq name (find locator (topic-maps.tmdm::map-information-items map) :test
          (lambda (iri item) (member iri (item-identifiers item) :test #'equal))))))
    (check (concatenate 'string label ":scope-and-excluded-properties-empty")
      (and (null (topic-name-scope name)) (null (topic-name-variants name)) (null (item-reifier name))))
    (check (concatenate 'string label ":global-identifier-uniqueness")
      (topic-maps.tmdm::validate-map-item-identifiers map))))

(defun iid-original-contracts ()
  (setf *iid-outputs* nil)
  (dolist (spec *iid-original-specs*)
    (let* ((name (first spec)) (id (format nil "xtm2/in/~A.xtm" name))
           (*document* (concatenate 'string "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/" id))
           (source (corpus-path id)) (baseline (corpus-path (format nil "xtm2/baseline/~A.xtm.cxtm" name)))
           (raw (file-bytes source)) (copy (copy-seq raw)) (expected (file-bytes baseline))
           (case (topic-maps.test-foundation:make-test-case :id id :category :valid :source-pathname source
             :document-iri *document* :expected-outcome :cxtm-equal :expected-baseline baseline
             :clauses '("XTM 2.0 4.2,4.3.1,4.3.3,4.3.4,4.6,4.10" "TMDM 5.1,5.4,6.2,6.3" "CXTM 3,4")))
           (map nil) (actual nil) (c nil) (before nil))
      (setf *cases* (append *cases* (list case)))
      (handler-case (setf map (deserialize-octets raw :document-iri *document* :source-key id)
                         before (name-state map)
                         actual (topic-maps.cxtm:canonicalize-octets map :base-locator *document*))
        (error (condition) (setf c condition)))
      ;; A reader or model failure can never satisfy this positive contract.
      (when (null c)
        (handler-case (iid-original-model-checks spec map raw) (error (condition) (setf c condition))))
      (record-original-result case actual expected c)
      (push (topic-maps.test-foundation::fields "id" id "documentIRI" *document* "sourceKey" id
        "sourceBytes" (length raw) "sourceHex" (format nil "~{~2,'0X~}" (coerce raw 'list))
        "sourceText" (babel:octets-to-string raw :encoding :utf-8)
        "actualCXTM" (when actual (babel:octets-to-string actual :encoding :utf-8))
        "expectedCXTM" (babel:octets-to-string expected :encoding :utf-8)
        "actualBytes" (when actual (length actual)) "expectedBytes" (length expected)
        "firstDifferentByte" (when actual (mismatch actual expected))
        "condition" (negative-condition-data c) "model" (when map (name-model-data map))
        "status" (string-downcase (string (topic-maps.test-foundation:test-case-status case)))) *iid-outputs*)
      (when c (error c))
      (check (concatenate 'string "iid-original:" name ":byte-exact") (equalp actual expected))
      (check (concatenate 'string "iid-original:" name ":source-preserved") (equalp raw copy))
      (check (concatenate 'string "iid-original:" name ":pure") (equal before (name-state map)))
      (check (concatenate 'string "iid-original:" name ":deterministic")
             (equalp actual (topic-maps.cxtm:canonicalize-octets map :base-locator *document*)))
      (check (concatenate 'string "iid-original:" name ":repeat-pure") (equal before (name-state map)))
      (let ((other (deserialize-octets raw :document-iri *document* :source-key "different-name-provenance")))
        (check (concatenate 'string "iid-original:" name ":source-key-only-provenance")
          (and (equalp (name-model-data map) (name-model-data other))
               (equalp actual (topic-maps.cxtm:canonicalize-octets other :base-locator *document*)))))))
  (setf *iid-outputs* (nreverse *iid-outputs*))
  (check "iid-originals:50-unique-case-records"
    (and (= 50 (length *cases*)) (= 43 (count :valid *cases* :key #'topic-maps.test-foundation:test-case-category))
      (= 50 (length (remove-duplicates *cases* :key #'topic-maps.test-foundation:test-case-id :test #'equal))))))

;; All counterprobes use the existing Name harness, native model and reports.
(defun iid-control (label body verify)
  (let ((*name-controls* nil))
    (name-control (concatenate 'string "iid:" label) body
      (lambda (map) (funcall verify map)
        (check (concatenate 'string "iid:" label ":global-identifier-uniqueness")
          (topic-maps.tmdm::validate-map-item-identifiers map))))
    (setf *iid-controls* (append *iid-controls* (reverse *name-controls*)))))
(defun iid-error-control (label body class code)
  (let ((*name-controls* nil))
    (name-error-control (concatenate 'string "iid:" label) body class code)
    (setf *iid-controls* (append *iid-controls* (reverse *name-controls*)))))
(defun iid-conflict-control (label body class)
  (let* ((source (document body)) (c (condition-from (lambda ()
           (deserialize-octets (bytes source) :document-iri *document* :source-key label)))))
    (check (concatenate 'string "iid-conflict:" label ":native-class-code")
      (and (eq class (type-of c)) (eq :duplicate-item-identifier (item-identifier-error-code c))
        (not (typep c 'xtm-rejection)) (not (typep c 'xtm-unsupported))))
    (push (topic-maps.test-foundation::fields "label" label "kind" "reader-TMDM-conflict"
      "sourceText" source "documentIRI" *document* "sourceKey" label
      "condition" (negative-condition-data c)) *iid-controls*)))

(defun iid-positive-controls ()
  (iid-control "no-identifier" "<topic id='a'><name><value>N</value></name></topic>"
    (lambda (map) (check "iid:absent-is-empty" (null (item-identifiers (first (topic-names (by-id map "a"))))))))
  (iid-control "one-owner"
    "<topic id='a'><name><itemIdentity href='#n'/><value>N</value></name></topic>"
    (lambda (map) (let* ((owner (by-id map "a")) (name (first (topic-names owner))))
      (check "iid:actual-name-owner-eq"
        (and (equal (list (concatenate 'string *document* "#n")) (item-identifiers name))
          (eq owner (topic-name-parent name)) (eq name (canonical-topic-name name))
          (equal (list (concatenate 'string *document* "#a")) (item-identifiers owner))
          (null (item-identifiers (topic-name-type name))))))))
  (let ((*document* "https://names.example.invalid/a/maps/example.xtm"))
    (iid-control "multiple-duplicate-relative-absolute"
      "<topic id='a'><name><itemIdentity href='#n'/><itemIdentity href='#n'/><itemIdentity href='../names#n'/><itemIdentity href='urn:name:absolute'/><itemIdentity href='#m%C3%A4'/><value>N</value></name></topic>"
      (lambda (map) (check "iid:resolved-locator-set-document-base"
        (same-identifiers-p (item-identifiers (first (topic-names (by-id map "a"))))
          '("https://names.example.invalid/a/maps/example.xtm#n" "https://names.example.invalid/a/names#n" "urn:name:absolute" "https://names.example.invalid/a/maps/example.xtm#mä"))))))
  (iid-control "empty-reference"
    "<topic id='a'><name><itemIdentity href=''/><value>N</value></name></topic>"
    (lambda (map) (check "iid:empty-anyURI-resolves-to-document"
      (equal (list *document*) (item-identifiers (first (topic-names (by-id map "a"))))))))
  (iid-control "non-topicRef-fragment"
    "<topic id='a'><name><itemIdentity href='#2valid-item-identifier'/><value>N</value></name></topic>"
    (lambda (map) (check "iid:no-topicRef-shorthand-restriction"
      (equal (list (concatenate 'string *document* "#2valid-item-identifier"))
        (item-identifiers (first (topic-names (by-id map "a"))))))))
  (iid-control "equal-names-union-identifiers"
    "<topic id='a'><name><itemIdentity href='urn:first'/><scope><topicRef href='#s'/><topicRef href='#t'/></scope><value>N</value></name><name><itemIdentity href='urn:second'/><itemIdentity href='urn:first'/><scope><topicRef href='#t'/><topicRef href='#s'/></scope><value>N</value></name></topic>"
    (lambda (map) (let ((names (topic-names (by-id map "a"))))
      (check "iid:equal-native-name-union-and-scope-set"
        (and (= 1 (length names)) (same-identifiers-p '("urn:first" "urn:second") (item-identifiers (first names)))
          (scope-eq-p (topic-name-scope (first names)) (list (by-id map "s") (by-id map "t"))))))))
  (dolist (row '(("different-value" "<value>N</value>" "<value>N </value>")
    ("different-type" "<type><topicRef href='#one'/></type><value>N</value>" "<type><topicRef href='#two'/></type><value>N</value>")
    ("different-scope" "<scope><topicRef href='#one'/></scope><value>N</value>" "<scope><topicRef href='#two'/></scope><value>N</value>")))
    (iid-control (first row)
      (format nil "<topic id='a'><name><itemIdentity href='urn:first'/>~A</name><name><itemIdentity href='urn:second'/>~A</name></topic>" (second row) (third row))
      (lambda (map) (let ((names (topic-names (by-id map "a"))))
        (check (concatenate 'string "iid:" (first row) ":distinct-owner-items")
          (and (= 2 (length names)) (not (eq (first names) (second names)))
            (equal '("urn:first") (item-identifiers (first names)))
            (equal '("urn:second") (item-identifiers (second names)))))))))
  (iid-control "different-parent"
    "<topic id='a'><name><itemIdentity href='urn:first'/><value>N</value></name></topic><topic id='b'><name><itemIdentity href='urn:second'/><value>N</value></name></topic>"
    (lambda (map) (check "iid:parent-distinguishes-items"
      (let ((a (first (topic-names (by-id map "a")))) (b (first (topic-names (by-id map "b")))))
        (and (not (eq a b)) (equal '("urn:first") (item-identifiers a)) (equal '("urn:second") (item-identifiers b)))))))
  (iid-control "type-and-scope-and-item-identity"
    "<topic id='a'><name><itemIdentity href='urn:n'/><type><topicRef href='#s'/></type><scope><topicRef href='#s'/><topicRef href='#s'/></scope><value>N</value></name></topic>"
    (lambda (map) (let ((name (first (topic-names (by-id map "a")))))
      (check "iid:all-name-properties-canonical-eq"
        (and (equal '("urn:n") (item-identifiers name)) (eq (by-id map "a") (topic-name-parent name))
          (eq (by-id map "s") (topic-name-type name)) (scope-eq-p (topic-name-scope name) (list (by-id map "s")))
          (not (member "urn:n" (item-identifiers (by-id map "s")) :test #'equal)))))))
  (iid-control "name-II-and-topic-SI-separate"
    "<topic id='s'><subjectIdentifier href='urn:n'/></topic><topic id='a'><name><itemIdentity href='urn:n'/><value>N</value></name></topic>"
    (lambda (map) (let ((name (first (topic-names (by-id map "a")))))
      (check "iid:no-implicit-reification-or-topic-identity"
        (and (equal '("urn:n") (item-identifiers name)) (null (item-reifier name))
             (null (topic-reified (by-id map "s"))) (= 3 (length (topic-map-topics map)))))))))

(defun iid-retained-controls ()
  (dolist (target '("parent" "theme"))
    (dolist (kind '("subjectIdentifier" "subjectLocator" "itemIdentity"))
      (let ((names nil) (themes nil) (*name-controls* nil) (label (format nil "iid-merge:~A:~A" target kind)))
        (flet ((theme-source (id locator)
          (if (equal kind "itemIdentity") (format nil "<topic id='~A'/>" id)
              (format nil "<topic id='~A'><~A href='~A'/></topic>" id kind locator))))
          (staged-name-control label
            (if (equal target "parent")
              (format nil "<topic id='a'>~A<name><itemIdentity href='urn:name:1'/><scope><topicRef href='#s'/></scope><value>N</value></name></topic><topic id='b'>~A<name><itemIdentity href='urn:name:2'/><scope><topicRef href='#s'/></scope><value>N</value></name></topic><topic id='bridge'><~A href='~A'/><~A href='~A'/></topic>"
                (if (equal kind "itemIdentity") "" (format nil "<~A href='urn:one'/>" kind))
                (if (equal kind "itemIdentity") "" (format nil "<~A href='urn:two'/>" kind))
                kind (if (equal kind "itemIdentity") "#a" "urn:one") kind (if (equal kind "itemIdentity") "#b" "urn:two"))
              (concatenate 'string "<topic id='a'><name><itemIdentity href='urn:name:1'/><scope><topicRef href='#s1'/></scope><value>N</value></name><name><itemIdentity href='urn:name:2'/><scope><topicRef href='#s2'/></scope><value>N</value></name></topic>"
                (theme-source "s1" "urn:one") (theme-source "s2" "urn:two")
                (format nil "<topic id='bridge'><~A href='~A'/><~A href='~A'/></topic>"
                  kind (if (equal kind "itemIdentity") "#s1" "urn:one") kind (if (equal kind "itemIdentity") "#s2" "urn:two"))))
            (lambda (map step)
              (if (equal target "parent")
                (when (<= step 2) (push (first (topic-names (by-id map (if (= step 1) "a" "b")))) names))
                (when (= step 1) (setf names (topic-names (by-id map "a")) themes (list (by-id map "s1") (by-id map "s2")))))
              (when (= step (if (equal target "parent") 2 3))
                (check (concatenate 'string label ":distinct-before")
                  (and (= 2 (length names)) (not (eq (first names) (second names)))
                    (equal '("urn:name:1" "urn:name:2")
                      (sort (append (item-identifiers (first names)) (item-identifiers (second names))) #'string<))))))
            (lambda (map)
              (let* ((owner (by-id map "a")) (name (first (topic-names owner))) (before (name-state map)))
                (check (concatenate 'string label ":canonical-handles-and-union")
                  (and (= 1 (length (topic-names owner))) (names-current-p map)
                    (every (lambda (old) (and (eq name (canonical-topic-name old)) (eq owner (topic-name-parent old))
                      (same-identifiers-p '("urn:name:1" "urn:name:2") (item-identifiers old)))) names)
                    (if (equal target "parent") (eq owner (by-id map "b"))
                      (and (every (lambda (old) (eq (by-id map "bridge") (canonical-topic old))) themes)
                        (scope-eq-p (topic-name-scope name) (list (by-id map "bridge")))))))
                (topic-maps.cxtm:canonicalize-octets map :base-locator *document*)
                (check (concatenate 'string label ":pure-cxtm-retains-identifiers")
                  (and (equal before (name-state map))
                    (every (lambda (old) (eq name (canonical-topic-name old))) names)
                    (topic-maps.tmdm::validate-map-item-identifiers map)))))))
        (setf *iid-controls* (append *iid-controls* (reverse *name-controls*)))))))

(defun iid-conflict-controls ()
  (dolist (row '(("name-parent" "<topic id='a'><name><itemIdentity href='#a'/><value>N</value></name></topic>" item-identifier-error)
    ("name-type" "<topic id='a'><name><itemIdentity href='#s'/><type><topicRef href='#s'/></type><value>N</value></name></topic>" item-identifier-error)
    ("map-before-name" "<itemIdentity href='urn:n'/><topic id='a'><name><itemIdentity href='urn:n'/><value>N</value></name></topic>" item-identifier-error)
    ("topic-after-name" "<topic id='a'><name><itemIdentity href='#b'/><value>N</value></name></topic><topic id='b'/>" topic-maps.tmdm::occurrence-identifier-error)
    ("topic-II-after-name" "<topic id='a'><name><itemIdentity href='urn:n'/><value>N</value></name></topic><topic id='b'><itemIdentity href='urn:n'/></topic>" topic-maps.tmdm::occurrence-identifier-error)
    ("different-value-same-II" "<topic id='a'><name><itemIdentity href='urn:n'/><value>N</value></name><name><itemIdentity href='urn:n'/><value>M</value></name></topic>" item-identifier-error)
    ("different-type-same-II" "<topic id='a'><name><itemIdentity href='urn:n'/><type><topicRef href='#s'/></type><value>N</value></name><name><itemIdentity href='urn:n'/><value>N</value></name></topic>" item-identifier-error)
    ("different-scope-same-II" "<topic id='a'><name><itemIdentity href='urn:n'/><scope><topicRef href='#s'/></scope><value>N</value></name><name><itemIdentity href='urn:n'/><value>N</value></name></topic>" item-identifier-error)
    ("different-parent-same-II" "<topic id='a'><name><itemIdentity href='urn:n'/><value>N</value></name></topic><topic id='b'><name><itemIdentity href='urn:n'/><value>N</value></name></topic>" item-identifier-error)))
    (iid-conflict-control (first row) (second row) (third row)))
  ;; Direct native mutation controls use a genuinely deserialized map. They are
  ;; not original contracts and prove that rejected writes do not overwrite IDs.
  (let* ((body "<itemIdentity href='urn:map'/><topic id='a'><name><itemIdentity href='urn:name'/><value>N</value></name><name><itemIdentity href='urn:other'/><value>M</value></name></topic>")
         (map (read-body body)) (owner (by-id map "a")) (name (first (topic-names owner))) (other (second (topic-names owner))))
    (dolist (row (list (list "name-map" name "urn:map" 'item-identifier-error)
      (list "map-name" map "urn:name" 'item-identifier-error)
      (list "name-topic" name (concatenate 'string *document* "#a") 'item-identifier-error)
      (list "topic-name" owner "urn:name" 'topic-maps.tmdm::occurrence-identifier-error)
      (list "name-name" other "urn:name" 'item-identifier-error)))
      (let* ((before (name-state map)) (c (condition-from (lambda () (add-item-identifier (second row) (third row))))))
        (check (concatenate 'string "iid-native-conflict:" (first row) ":specific-and-atomic")
          (and (eq (fourth row) (type-of c)) (eq :duplicate-item-identifier (item-identifier-error-code c))
            (equal before (name-state map)) (eq name (canonical-topic-name name))
            (eq other (canonical-topic-name other)) (topic-maps.tmdm::validate-map-item-identifiers map)))
        (push (topic-maps.test-foundation::fields "label" (first row) "kind" "native-TMDM-conflict-atomicity"
          "sourceText" (document body) "condition" (negative-condition-data c) "modelUnchanged" :true
          "model" (name-model-data map)) *iid-controls*)))))

(defun iid-syntax-controls ()
  (dolist (row '(("missing-href" "<itemIdentity/>" :missing-attribute)
    ("bad-percent" "<itemIdentity href='%GG'/>" :invalid-percent-escape)
    ("bad-percent-utf8" "<itemIdentity href='%FF'/>" :invalid-percent-utf8)
    ("illegal-IRI-character" "<itemIdentity href='bad uri'/>" :invalid-iri)
    ("unexpected-attribute" "<itemIdentity href='urn:n' other='x'/>" :unexpected-attribute)
    ("namespaced-attribute" "<itemIdentity xmlns:q='urn:q' q:href='urn:n'/>" :unexpected-attribute)
    ("nested-element" "<itemIdentity href='urn:n'><value>N</value></itemIdentity>" :unexpected-child)
    ("non-whitespace-text" "<itemIdentity href='urn:n'>text</itemIdentity>" :unexpected-text)
    ("wrong-namespace" "<itemIdentity xmlns='urn:foreign' href='urn:n'/>" :invalid-namespace)
    ("after-type" "<type><topicRef href='#t'/></type><itemIdentity href='urn:n'/>" :element-order)
    ("after-scope" "<scope><topicRef href='#s'/></scope><itemIdentity href='urn:n'/>" :element-order)))
    (iid-error-control (first row) (format nil "<topic id='a'><name>~A<value>N</value></name></topic>" (second row)) 'xtm-rejection (third row)))
  (iid-error-control "after-value" "<topic id='a'><name><value>N</value><itemIdentity href='urn:n'/></name></topic>" 'xtm-rejection :element-order)
  (iid-error-control "variant-reifier-excluded-datatype" "<topic id='a'><name><itemIdentity href='urn:n'/><value>N</value><variant reifier='#r'><scope><topicRef href='#v'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#anyType'>42</resourceData></variant></name></topic>" 'xtm-unsupported :resource-resolver-required)
  (iid-error-control "variant-resourceData-datatype-stays-unsupported" "<topic id='a'><name><itemIdentity href='urn:n'/><scope><topicRef href='#s'/></scope><value>N</value><variant><scope><topicRef href='#v'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#anyType'>42</resourceData></variant></name></topic>" 'xtm-unsupported :resource-resolver-required))

(defun iid-tests ()
  (setf *iid-controls* nil)
  (iid-positive-controls) (iid-retained-controls) (iid-conflict-controls) (iid-syntax-controls))
