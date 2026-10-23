(defpackage #:topic-maps.equivalence.tests
  (:use #:cl #:topic-maps.tmdm)
  (:import-from #:topic-maps.xtm-mergemap.tests #:check)
  (:export #:run-tests #:write-report))
(in-package #:topic-maps.equivalence.tests)
(defvar *rows* nil)
(defvar *checks* nil)
(defun fields (&rest args) (apply #'topic-maps.test-foundation::fields args))
(defun octets (text) (babel:string-to-octets text :encoding :utf-8 :use-bom nil))
(defun xml (body &optional reifier)
  (format nil "<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'~A>~A</topicMap>"
    (if reifier (format nil " reifier='~A'" reifier) "") body))
(defun sorted-set (values)
  ;; Sort only temporary property lists. Never edit model collections/CXTM bytes.
  (sort (copy-list values) #'string< :key (lambda (v) (write-to-string v :readably t))))
(defun ids (topic)
  (list (sorted-set (item-identifiers topic)) (sorted-set (topic-subject-identifiers topic))
    (sorted-set (topic-subject-locators topic))))
(defun refs (topics) (sorted-set (mapcar #'ids topics)))
(defun assoc-key (a)
  (list :association (ids (association-type a)) (refs (association-scope a))
    (sorted-set (mapcar (lambda (r) (list (ids (association-role-type r)) (ids (association-role-player r)))) (association-roles a)))))
(defun ref (item)
  ;; Ephemeral test property tuples based on native TMDM equality rules, not
  ;; another identity registry or an alternate Topic Maps object model.
  (when item
    (etypecase item
      (topic-map (list :map))
      (topic (cons :topic (ids item)))
      (topic-name (list :name (ids (topic-name-parent item)) (ids (topic-name-type item))
        (topic-name-value item) (refs (topic-name-scope item))))
      (variant (list :variant (ref (variant-parent item)) (variant-value item) (variant-datatype item) (refs (variant-scope item))))
      (occurrence (list :occurrence (ids (occurrence-parent item)) (ids (occurrence-type item))
        (occurrence-value item) (occurrence-datatype item) (refs (occurrence-scope item))))
      (association (assoc-key item))
      (association-role (list :role (assoc-key (association-role-parent item))
        (ids (association-role-type item)) (ids (association-role-player item)))))))
(defun properties (map)
  (sorted-set (loop for item in (topic-maps.tmdm::map-information-items map) collect
    (list (ref item) (sorted-set (item-identifiers item))
      (when (topic-maps.tmdm::reifiable-p item) (ref (item-reifier item)))
      (typecase item
        (topic-map (list (refs (topic-map-topics item)) (sorted-set (mapcar #'ref (topic-map-associations item)))))
        (topic (list (sorted-set (mapcar #'ref (topic-names item)))
          (sorted-set (mapcar #'ref (topic-occurrences item))) (sorted-set (mapcar #'ref (topic-roles-played item)))
          (ref (topic-reified item))))
        (topic-name (sorted-set (mapcar #'ref (topic-name-variants item)))))))))
(defun counts (map)
  (list (length (topic-map-topics map))
    (loop for topic in (topic-map-topics map) sum (length (topic-names topic)))
    (loop for topic in (topic-map-topics map) sum (loop for n in (topic-names topic) sum (length (topic-name-variants n))))
    (loop for topic in (topic-map-topics map) sum (length (topic-occurrences topic)))
    (length (topic-map-associations map))
    (loop for a in (topic-map-associations map) sum (length (association-roles a)))
    (count-if (lambda (item) (and (topic-maps.tmdm::reifiable-p item) (item-reifier item)))
      (topic-maps.tmdm::map-information-items map))))
(defun model (map)
  (fields "countOrder" #("topics" "names" "variants" "occurrences" "associations" "roles" "reifiedItems")
    "counts" (coerce (counts map) 'vector) "topicIdentities" (write-to-string (refs (topic-map-topics map)) :readably t)
    "completeNativePropertyTuples" (write-to-string (properties map) :readably t)))
(defun handles (map) (topic-maps.import.tests::handles map))
(defun state (map held) (topic-maps.import.tests::state map held))
(defun canonical-eq-p (map)
  (and (topic-maps.reference.tests::references-current-p map)
    (topic-maps.tmdm::validate-import-map map)
    (every (lambda (i) (and (eq i (topic-maps.tmdm::canonical-item i))
      (eq map (topic-maps.tmdm::item-topic-map i)))) (handles map))
    (every (lambda (i) (or (not (topic-maps.tmdm::reifiable-p i)) (null (item-reifier i))
      (and (eq (item-reifier i) (canonical-topic (item-reifier i))) (eq i (topic-reified (item-reifier i)))))) (handles map))))
(defun pure-cxtm (id map base)
  (let* ((held (handles map)) (before (state map held)) (props (properties map))
         (bytes (topic-maps.cxtm:canonicalize-octets map :base-locator base)))
    (check (concatenate 'string "equivalence:" id ":pure-deterministic-cxtm")
      (and (equalp bytes (topic-maps.cxtm:canonicalize-octets map :base-locator base))
        (equal before (state map held)) (equal props (properties map))
        (every (lambda (i) (eq i (topic-maps.tmdm::canonical-item i))) held)))
    bytes))
(defun condition-data (c)
  (when c
    (let ((code (typecase c
                  (topic-maps.ctm:ctm-error (topic-maps.ctm:error-code c))
                  (topic-maps.xtm:xtm-error (topic-maps.xtm:error-code c)))))
      (fields "class" (string (type-of c)) "code" (when code (string-downcase (string code)))
        "line" (typecase c (topic-maps.ctm:ctm-error (topic-maps.ctm:error-line c)) (topic-maps.xtm:xtm-error (topic-maps.xtm:error-line c)))
        "column" (typecase c (topic-maps.ctm:ctm-error (topic-maps.ctm:error-column c)) (topic-maps.xtm:xtm-error (topic-maps.xtm:error-column c)))
        "sourceKey" (typecase c (topic-maps.ctm:ctm-error (topic-maps.ctm:error-source c)) (topic-maps.xtm:xtm-error (topic-maps.xtm:error-source-key c)))
        "documentIRI" (when (typep c 'topic-maps.xtm:xtm-error) (topic-maps.xtm:error-document-iri c))
        "position" (when (typep c 'topic-maps.ctm:ctm-error) (topic-maps.ctm:error-position c))
        "message" (princ-to-string c)))))
(defun local-key (doc name &key si sl ii)
  (list (sorted-set (cons (concatenate 'string doc "#" name) ii)) (sorted-set si) (sorted-set sl)))
(defun default-type () (list nil (list (default-name-type-identifier)) nil))
(defun core-key (local) (list nil (list (concatenate 'string "http://psi.topicmaps.org/iso13250/model/" local)) nil))
(defun pair (id ctm body keys count why clauses &key literal datatype reifier resources)
  (list :id id :ctm ctm :xtm (xml body reifier) :keys keys :counts count :why why :clauses clauses
    :literal literal :datatype datatype :resources resources))
(defun pair-cases ()
  (let ((rows nil))
    (flet ((add (row) (push row rows)))
      (add (pair "local-II" "a." "<topic id='a'/>" '("a") '(1 0 0 0 0 0 0)
        "CTM local identifier and XTM id both assign the common Document IRI followed by #a." '("CTM 3.3.6" "XTM 4.5" "TMDM 5.3.5")))
      (dolist (row '(("SI" "<urn:subject>" "subjectIdentifier" :si)
                    ("SL" "=<urn:subject>" "subjectLocator" :sl)
                    ("II" "^<urn:item>" "itemIdentity" :ii)))
        (destructuring-bind (id tail tag kind) row
          (let ((value (if (eq kind :ii) "urn:item" "urn:subject")))
            (add (pair (concatenate 'string "identity-" id) (format nil "a ~A." tail)
              (format nil "<topic id='a'><~A href='~A'/></topic>" tag value)
              (list (list "a" kind (list value))) '(1 0 0 0 0 0 0)
              "Both sources preserve the local II and add the same locator in the same identity category."
              '("CTM 3.3.6,3.9" "XTM 4.5-4.8" "TMDM 5.3.5")))
            (add (pair (concatenate 'string "merge-" id) (format nil "a ~A. b ~A." tail tail)
              (format nil "<topic id='b'><~A href='~A'/></topic><topic id='a'><~A href='~A'/></topic>" tag value tag value)
              (list (if (eq kind :ii) (list "a" :ii (list value "#b")) (list "a" kind (list value) :ii '("#b")))) '(1 0 0 0 0 0 0)
              "The shared locator merges two Topics; both document-local IIs must survive. Creation order differs."
              '("CTM 3.3.6,3.9" "XTM 4.5-4.8" "TMDM 5.3.5,6.2"))))))
      (add (pair "isa-instanceOf" "a isa t." "<topic id='a'><instanceOf><topicRef href='#t'/></instanceOf></topic>"
        (list "a" "t" (core-key "type-instance") (core-key "type") (core-key "instance")) '(5 0 0 0 1 2 0)
        "Both create the same type-instance Association with instance/type Roles and identical Core Subject SIs."
        '("CTM 3.9" "XTM 4.9" "TMDM 7.2")))
      (add (pair "isa-multiple-normalized" "a isa t; isa u; isa t."
        "<topic id='u'/><topic id='a'><instanceOf><topicRef href='#t'/><topicRef href='#u'/><topicRef href='#t'/></instanceOf></topic>"
        (list "a" "t" "u" (core-key "type-instance") (core-key "type") (core-key "instance")) '(6 0 0 0 2 4 0)
        "Two distinct type-instance Associations remain; repeating one relation is normalized."
        '("CTM 3.9" "XTM 4.9" "TMDM 6.6,7.2")))
      (add (pair "default-name" "a - \"Name\"." "<topic id='a'><name><value>Name</value></name></topic>"
        (list "a" (default-type)) '(2 1 0 0 0 0 0) "Both create one Name of the same implicit topic-name Core Subject type."
        '("CTM 3.11" "XTM 4.10-4.11" "TMDM 5.4,7.5") :literal "Name"))
      (add (pair "typed-scoped-name" "a - t:\"Name\"@s2,s1,s1."
        "<topic id='a'><name><type><topicRef href='#t'/></type><scope><topicRef href='#s1'/><topicRef href='#s2'/></scope><value>Name</value></name></topic>"
        '("a" "t" "s1" "s2") '(4 1 0 0 0 0 0) "Name Type and Scope are identical native references; Scope is a set."
        '("CTM 3.3.9,3.11" "XTM 4.10,4.13-4.14" "TMDM 5.4") :literal "Name"))
      (add (pair "unicode-whitespace-escaping" "a - \" 馬🦊 & < > \\n \\t \\\" \\\\ \"."
        "<topic id='a'><name><value> 馬🦊 &amp; &lt; &gt; &#xA; &#x9; &quot; \\ </value></name></topic>"
        (list "a" (default-type)) '(2 1 0 0 0 0 0) "CTM escapes and XML references encode the same Unicode characters and whitespace."
        '("CTM 3.4.2,3.11" "XTM 4.11" "TMDM 5.4")))
      (add (pair "empty-name" "a - \"\"." "<topic id='a'><name><value/></name></topic>" (list "a" (default-type)) '(2 1 0 0 0 0 0)
        "Both Name values are the empty string." '("CTM 3.11" "XTM 4.11" "TMDM 5.4") :literal ""))
      (add (pair "duplicate-names" "a - \"N\"; - \"N\"." "<topic id='a'><name><value>N</value></name><name><value>N</value></name></topic>"
        (list "a" (default-type)) '(2 1 0 0 0 0 0) "Equal Names normalize to one native Name in both maps."
        '("CTM 3.11" "XTM 4.10" "TMDM 5.4,6.3") :literal "N"))
      (add (pair "variant-inherited-scope" "a - \"N\"@base (\"V\"@extra)."
        "<topic id='a'><name><scope><topicRef href='#base'/></scope><value>N</value><variant><scope><topicRef href='#extra'/></scope><resourceData>V</resourceData></variant></name></topic>"
        (list "a" "base" "extra" (default-type)) '(4 1 1 0 0 0 0) "Variant Scope is Name Scope union explicit Scope, a proper superset."
        '("CTM 3.12" "XTM 4.12" "TMDM 5.5") :literal "V" :datatype (string-datatype)))
      (dolist (row (list (list "integer" "+00042" (integer-datatype)) (list "decimal" "01.50" (decimal-datatype))
        (list "date" "2000-02-29" (date-datatype)) (list "datetime" "2000-02-29T01:02:03Z" (datetime-datatype))
        (list "unknown-http" "literal%GG" "https://types.example.invalid/custom") (list "unknown-urn" " urn:literal " "urn:custom")))
        (destructuring-bind (id value dtype) row
          (add (pair (concatenate 'string "variant-datatype-" id)
            (format nil "a - \"N\" (\"~A\"^^<~A>@s)." value dtype)
            (format nil "<topic id='a'><name><value>N</value><variant><scope><topicRef href='#s'/></scope><resourceData datatype='~A'>~A</resourceData></variant></name></topic>" dtype value)
            (list "a" "s" (default-type)) '(3 1 1 0 0 0 0)
            "Both quoted resource forms retain the same lexical value and exact datatype IRI; datatype is not a Topic."
            '("CTM 3.4.1,3.12" "XTM 4.12,4.16" "TMDM 4.4,5.5") :literal value :datatype dtype))))
      (dolist (kind '("resourceRef" "anyURI-data"))
        (add (pair (concatenate 'string "variant-" kind) "a - \"N\" (<../sound>@s)."
          (format nil "<topic id='a'><name><value>N</value><variant><scope><topicRef href='#s'/></scope>~A</variant></name></topic>"
            (if (equal kind "resourceRef") "<resourceRef href='../sound'/>" "<resourceData datatype='http://www.w3.org/2001/XMLSchema#anyURI'>../sound</resourceData>"))
          (list "a" "s" (default-type)) '(3 1 1 0 0 0 0) "IRI-valued literals resolve against the same explicit Document IRI without Topic creation."
          '("CTM 3.4.1" "XTM 4.16-4.17" "TMDM 4.4,5.5") :literal "https://equivalence.example.invalid/sound" :datatype (iri-datatype))))
      (add (pair "variant-ctm-integer-star" "a - \"N\" (*@s)."
        "<topic id='a'><name><value>N</value><variant><scope><topicRef href='#s'/></scope><resourceData datatype='http://psi.topicmaps.org/iso13250/ctm-integer'>*</resourceData></variant></name></topic>"
        (list "a" "s" (default-type)) '(3 1 1 0 0 0 0) "The literal * is an opaque lexical value with ctm-integer datatype in both maps."
        '("CTM 3.4.1,Annex A" "XTM 4.16" "TMDM 4.4") :literal "*" :datatype "http://psi.topicmaps.org/iso13250/ctm-integer"))
      (add (pair "name-variant-reification" "a - \"N\"~nr (\"V\"@s ~vr)."
        "<topic id='a'><name reifier='#nr'><value>N</value><variant reifier='#vr'><scope><topicRef href='#s'/></scope><resourceData>V</resourceData></variant></name></topic>"
        (list "a" "nr" "vr" "s" (default-type)) '(5 1 1 0 0 0 2)
        "The same local-II Topics reify the Name and Variant, with inverse references within each map."
        '("CTM 3.3.10,3.11-3.12" "XTM 4.3.2,4.10,4.12" "TMDM 5.3.4") :literal "V" :datatype (string-datatype)))
      (add (pair "map-reification" "~r a." "<topic id='a'/>" '("a" "r") '(2 0 0 0 0 0 1)
        "The same local-II Topic reifies the fresh Map item; neither Map has explicit item identifiers."
        '("CTM 3.5" "XTM 4.3.2,4.4" "TMDM 5.2,5.3.4") :reifier "#r"))
      (add (pair "content-import" (format nil "%mergemap <child.xtm> <http://psi.topicmaps.org/iso13250/xtm>~%local.")
        "<mergeMap href='child.xtm'/><topic id='local'/>" nil '(9 1 1 0 1 2 0)
        "Both readers import the same supported XTM child using its resource IRI; child Map metadata is excluded."
        '("CTM 3.16.3" "XTM 4.21" "TMDM 5.2,6.2") :resources t)))
    (nreverse rows)))
(defun expanded-keys (spec doc)
  (sorted-set (loop for key in spec collect
    (cond ((stringp key) (local-key doc key))
          ((stringp (first key))
           (local-key doc (first key) :si (getf (rest key) :si) :sl (getf (rest key) :sl)
             :ii (mapcar (lambda (iri) (if (and (plusp (length iri)) (char= #\# (char iri 0)))
                   (concatenate 'string doc iri) iri)) (getf (rest key) :ii))))
          (t key)))))
(defun execute (kind source doc key &optional resource-iri resource-raw)
  (let* ((raw (octets source)) (copy (copy-seq raw)) (text-copy (copy-seq source))
         (resource-copy (when resource-raw (copy-seq resource-raw))) (calls nil) (parses nil) (imports nil)
         (old-parser (symbol-function 'topic-maps.xml:parse-octets))
         (old-import (symbol-function 'import-map-content)) (map nil) (condition nil)
         (resolver (when resource-raw (lambda (iri &key purpose from-document-iri notation)
           (push (list iri purpose from-document-iri notation) calls)
           (unless (equal iri resource-iri) (error "Unexpected equivalence resource ~A" iri))
           (values resource-raw (concatenate 'string key ":child"))))))
    (unwind-protect
        (handler-case
            (progn
              (setf (symbol-function 'topic-maps.xml:parse-octets)
                (lambda (input &rest args)
                  (push (list topic-maps.xtm::*document-iri* topic-maps.xtm::*source-key*
                    (eq input raw) (eq input resource-raw) (length input)) parses)
                  (apply old-parser input args)))
              (setf (symbol-function 'import-map-content)
                (lambda (target child)
                  (let* ((held (handles child)) (before (state child held)) (cx (topic-maps.cxtm:canonicalize-octets child :base-locator resource-iri))
                         (source-map-ids (copy-list (item-identifiers child))) (source-reifier (item-reifier child)))
                    (multiple-value-bind (result resolve) (funcall old-import target child)
                      (push (list source-map-ids (not (null source-reifier))
                        (and (equal before (state child held))
                          (equalp cx (topic-maps.cxtm:canonicalize-octets child :base-locator resource-iri)))) imports)
                      (values result resolve)))))
              (setf map (ecase kind
                (:ctm (topic-maps.ctm:deserialize-string source :document-iri doc :source-name key :resource-resolver resolver))
                (:xtm (topic-maps.xtm:deserialize-octets raw :document-iri doc :source-key key :resource-resolver resolver)))))
          (error (c) (setf condition c)))
      (setf (symbol-function 'topic-maps.xml:parse-octets) old-parser
            (symbol-function 'import-map-content) old-import))
    (list :entry-point (ecase kind (:ctm "topic-maps.ctm:deserialize-string") (:xtm "topic-maps.xtm:deserialize-octets"))
      :document-iri doc :source-key key :map map :condition condition :calls (nreverse calls) :parses (nreverse parses) :imports (nreverse imports)
      :source-preserved (and (equalp raw copy) (equal source text-copy)
        (or (null resource-raw) (equalp resource-raw resource-copy))))))
(defun trace-data (result)
  (fields "entryPoint" (getf result :entry-point) "documentIRI" (getf result :document-iri) "sourceKey" (getf result :source-key)
    "resolverCalls" (coerce (mapcar (lambda (c) (fields "resourceIRI" (first c) "purpose" (string-downcase (string (second c)))
    "fromDocumentIRI" (third c) "notation" (fourth c))) (getf result :calls)) 'vector)
    "qualifiedXMLParserCalls" (coerce (mapcar (lambda (p) (fields "documentIRI" (first p) "sourceKey" (second p)
      "originalRootOctetsEQ" (if (third p) :true :false) "originalResourceOctetsEQ" (if (fourth p) :true :false) "bytes" (fifth p))) (getf result :parses)) 'vector)
    "imports" (coerce (mapcar (lambda (i) (fields "sourceMapItemIdentifiers" (coerce (first i) 'vector)
      "sourceMapReifierPresent" (if (second i) :true :false) "sourceMapPreserved" (if (third i) :true :false))) (getf result :imports)) 'vector)
    "sourcePreserved" (if (getf result :source-preserved) :true :false)))
(defun expected-features (id map doc case)
  (when (getf case :keys)
    (check (format nil "equivalence:~A:~A:expected-topic-identities" (getf case :id) id)
      (equal (expanded-keys (getf case :keys) doc) (refs (topic-map-topics map)))))
  (check (format nil "equivalence:~A:~A:expected-native-counts" (getf case :id) id) (equal (getf case :counts) (counts map)))
  (when (getf case :literal)
    (check (format nil "equivalence:~A:~A:expected-exact-value-datatype" (getf case :id) id)
      (if (getf case :datatype)
        (some (lambda (topic) (some (lambda (name) (some (lambda (v)
          (and (equal (getf case :literal) (variant-value v)) (equal (getf case :datatype) (variant-datatype v))))
          (topic-name-variants name))) (topic-names topic))) (topic-map-topics map))
        (some (lambda (topic) (find (getf case :literal) (topic-names topic) :key #'topic-name-value :test #'equal)) (topic-map-topics map)))))
  (when (search "isa-" (getf case :id))
    (let ((instance (find (concatenate 'string doc "#a") (topic-map-topics map)
      :test (lambda (iri tpc) (member iri (item-identifiers tpc) :test #'equal)))))
      (check (format nil "equivalence:~A:~A:actual-core-associations-role-types-players" (getf case :id) id)
        (every (lambda (a)
          (and (equal (list "http://psi.topicmaps.org/iso13250/model/type-instance") (topic-subject-identifiers (association-type a)))
            (= 2 (length (association-roles a)))
            (some (lambda (r) (and (eq instance (association-role-player r))
              (member "http://psi.topicmaps.org/iso13250/model/instance" (topic-subject-identifiers (association-role-type r)) :test #'equal))) (association-roles a))
            (some (lambda (r) (member "http://psi.topicmaps.org/iso13250/model/type" (topic-subject-identifiers (association-role-type r)) :test #'equal)) (association-roles a))))
          (topic-map-associations map))))))
(defun run-pair (case)
  (let* ((id (getf case :id)) (doc (format nil "https://equivalence.example.invalid/~A/map" id))
         (child (format nil "https://equivalence.example.invalid/~A/child.xtm" id))
         (resource (when (getf case :resources) (octets (xml
           "<itemIdentity href='urn:child-map'/><topic id='owner'><instanceOf><topicRef href='#t'/></instanceOf><name><value>Imported</value><variant><scope><topicRef href='#s'/></scope><resourceData datatype='urn:custom'>V</resourceData></variant></name></topic>" "#child-r"))))
         (ctm (execute :ctm (getf case :ctm) doc (concatenate 'string "ctm:" id) child resource))
         (xtm (execute :xtm (getf case :xtm) doc (concatenate 'string "xtm:" id) child resource))
         (a (getf ctm :map)) (b (getf xtm :map)) (ac nil) (bc nil) (props-equal nil))
    (when resource
      (setf (getf case :keys) (list "local" (local-key child "owner") (local-key child "t")
        (local-key child "s") (local-key child "child-r") (default-type)
        (core-key "type-instance") (core-key "instance") (core-key "type"))))
    (when (and a b)
      (setf props-equal (equal (properties a) (properties b))
            ac (pure-cxtm (concatenate 'string id ":CTM") a doc)
            bc (pure-cxtm (concatenate 'string id ":XTM") b doc)))
    ;; Record both actual states before an assertion can stop the suite.
    (push (fields "id" id "kind" "direct-reader-equivalence-pair" "normativeReason" (getf case :why)
      "clauses" (coerce (getf case :clauses) 'vector) "documentIRI" doc "canonicalBaseIRI" doc
      "ctmSource" (getf case :ctm) "xtmSource" (getf case :xtm)
      "resourceIRI" (when resource child) "resourceSource" (when resource (babel:octets-to-string resource :encoding :utf-8))
      "ctmTrace" (trace-data ctm) "xtmTrace" (trace-data xtm)
      "ctmCondition" (condition-data (getf ctm :condition)) "xtmCondition" (condition-data (getf xtm :condition))
      "ctmModel" (when a (model a)) "xtmModel" (when b (model b))
      "nativePropertiesEqual" (if props-equal :true :false)
      "ctmCanonicalEQ" (if (and a (canonical-eq-p a)) :true :false)
      "xtmCanonicalEQ" (if (and b (canonical-eq-p b)) :true :false) "crossMapEQRequired" :false
      "ctmCXTM" (when ac (babel:octets-to-string ac :encoding :utf-8))
      "xtmCXTM" (when bc (babel:octets-to-string bc :encoding :utf-8))
      "ctmBytes" (when ac (length ac)) "xtmBytes" (when bc (length bc))
      "firstDifferentByte" (when (and ac bc) (mismatch ac bc))
      "byteExact" (if (and ac bc (equalp ac bc)) :true :false)) *rows*)
    (check (format nil "equivalence:~A:both-productive-readers-succeeded" id)
      (and a b (null (getf ctm :condition)) (null (getf xtm :condition))))
    (dolist (pair (list (list "CTM" a ctm) (list "XTM" b xtm)))
      (destructuring-bind (language map result) pair
        (check (format nil "equivalence:~A:~A:canonical-EQ-parents-types-players-scopes-reifier-inverses" id language) (canonical-eq-p map))
        (check (format nil "equivalence:~A:~A:source-preserved" id language) (getf result :source-preserved))
        (expected-features language map doc case)))
    (check (format nil "equivalence:~A:independent-maps-no-cross-map-objects-shared" id)
      (and (not (eq a b)) (null (intersection (handles a) (handles b) :test #'eq))))
    (check (format nil "equivalence:~A:native-properties-equal" id) props-equal)
    (check (format nil "equivalence:~A:complete-unmodified-CXTM-bytes-equal" id) (equalp ac bc))
    (check (format nil "equivalence:~A:qualified-XML-path-and-document-IRIs" id)
      (and (= (length (getf ctm :parses)) (if resource 1 0))
        (= (length (getf xtm :parses)) (if resource 2 1))
        (every (lambda (p) (if (equal (first p) doc) (third p) (and (equal (first p) child) (fourth p))))
          (append (getf ctm :parses) (getf xtm :parses)))))
    (when resource
      (check "equivalence:content-import:actual-resolver-arguments-both-contexts"
        (and (equal (getf ctm :calls) (getf xtm :calls))
          (equal (getf ctm :calls) (list (list child :mergemap doc "http://psi.topicmaps.org/iso13250/xtm")))))
      (check "equivalence:content-import:source-map-metadata-excluded-preserved"
        (and (null (item-identifiers a)) (null (item-identifiers b)) (null (item-reifier a)) (null (item-reifier b))
          (every (lambda (record) (and (equal '("urn:child-map") (first record)) (second record) (third record)))
            (append (getf ctm :imports) (getf xtm :imports))))))
    ;; Repeat both genuine deserializations with different diagnostic keys.
    (let ((aa (getf (execute :ctm (getf case :ctm) doc "other:CTM-key" child resource) :map))
          (bb (getf (execute :xtm (getf case :xtm) doc "other:XTM-key" child resource) :map)))
      (check (format nil "equivalence:~A:source-keys-do-not-change-model-identities" id)
        (and aa bb (equal (properties a) (properties aa)) (equal (properties b) (properties bb))
          (equalp ac (topic-maps.cxtm:canonicalize-octets aa :base-locator doc))
          (equalp bc (topic-maps.cxtm:canonicalize-octets bb :base-locator doc)))))))
(defun run-contrast (id ctm-source xtm-source doc-a doc-b base reason)
  (let* ((ar (execute :ctm ctm-source doc-a "contrast:CTM")) (br (execute :xtm xtm-source doc-b "contrast:XTM"))
         (a (getf ar :map)) (b (getf br :map)))
    (check (concatenate 'string "equivalence:contrast:" id ":both-real-readers-succeeded")
      (and a b (null (getf ar :condition)) (null (getf br :condition))))
    (let ((ac (pure-cxtm (concatenate 'string "contrast:" id ":CTM") a base))
          (bc (pure-cxtm (concatenate 'string "contrast:" id ":XTM") b base)))
      (push (fields "id" id "kind" "intentional-semantic-difference" "reason" reason
        "ctmSource" ctm-source "xtmSource" xtm-source "ctmDocumentIRI" doc-a "xtmDocumentIRI" doc-b "canonicalBaseIRI" base
        "ctmModel" (model a) "xtmModel" (model b) "ctmBytes" (length ac) "xtmBytes" (length bc)
        "ctmCXTM" (babel:octets-to-string ac :encoding :utf-8) "xtmCXTM" (babel:octets-to-string bc :encoding :utf-8)
        "firstDifferentByte" (mismatch ac bc) "nativePropertiesEqual" :false "byteExact" :false) *rows*)
      (check (concatenate 'string "equivalence:contrast:" id ":native-and-cxtm-differences-preserved")
        (and (not (equal (properties a) (properties b))) (not (equalp ac bc)) (canonical-eq-p a) (canonical-eq-p b))))))
(defun contrast-tests ()
  (let ((doc "https://equivalence.example.invalid/contrast/map"))
    (run-contrast "different-document-IRIs" "a." (xml "<topic id='a'/>")
      "https://equivalence.example.invalid/contrast/a.ctm" "https://equivalence.example.invalid/contrast/b.xtm" doc
      "Different document-local IIs are real TMDM properties. A single shared CXTM base preserves the difference.")
    (run-contrast "SI-versus-SL" "a <urn:identity>." (xml "<topic id='a'><subjectLocator href='urn:identity'/></topic>") doc doc doc
      "Equal locator spelling in SI versus SL does not identify equal TMDM properties.")
    (run-contrast "non-topic-item-Identifier" "a - \"N\"." (xml "<topic id='a'><name><itemIdentity href='urn:name-item'/><value>N</value></name></topic>") doc doc doc
      "The XTM Name has an extra II that CTM cannot express here. It is not removed for comparison.")))
(defun write-report (path &optional failure)
  (with-open-file (out path :direction :output :if-exists :supersede :external-format :utf-8)
    (topic-maps.test-foundation::emit-json-value
      (fields "kind" "direct-CTM-XTM-semantic-equivalence-not-corpus-registration"
        "runtime" (lisp-implementation-version) "checks" (coerce *checks* 'vector)
        "pairs" (coerce (reverse *rows*) 'vector) "condition" (condition-data failure)
        "productionModelChanges" :false "originalCorpusRegistrationsAdded" 0) out)
    (terpri out)))
(defun run-tests ()
  ;; Reuse the existing adapter check function while preserving its 217-check
  ;; snapshot and all original-corpus registries. Only this dynamic list is new.
  (let ((topic-maps.xtm-mergemap.tests::*checks* nil))
    (setf *rows* nil *checks* nil)
    (let ((path (let ((prefix (uiop:getenv "TOPIC_MAPS_XTM_MERGEMAP_REPORT")))
                  (when prefix (concatenate 'string prefix ".equivalence.json")))))
      (handler-case
          (progn (mapc #'run-pair (pair-cases))
            (run-pair (list :id "explicit-association" :ctm "rel(role: a)"
              :xtm (xml "<association><type><topicRef href='#rel'/></type><role><type><topicRef href='#role'/></type><topicRef href='#a'/></role></association>")
              :keys '("rel" "role" "a") :counts '(3 0 0 0 1 1 0)
              :why "CTM relation and explicit XTM association have the same type and one role with equal type/player, no scope or metadata."
              :clauses '("CTM 3.13" "XTM 4.18-4.20" "TMDM 5.7-5.8,6.6-6.7")))
            (run-pair (list :id "occurrence-scope-reifier"
              :ctm "a t:\"42\"^^<http://www.w3.org/2001/XMLSchema#integer>@s ~r."
              :xtm (xml "<topic id='a'><occurrence reifier='#r'><type><topicRef href='#t'/></type><scope><topicRef href='#s'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#integer'>42</resourceData></occurrence></topic>")
              :keys '("a" "t" "s" "r") :counts '(4 0 0 1 0 0 1)
              :why "Both readers create the same typed scoped integer Occurrence and the same II-identified Reifier with inverse relation."
              :clauses '("CTM 3.10" "XTM 4.3.2,4.15" "TMDM 5.3.4-5.3.5,5.6,6.5")))
            (run-pair (list :id "association-role-scope-reifiers"
              :ctm "rel(role: a ~rr)@s ~ar"
              :xtm (xml "<association reifier='#ar'><type><topicRef href='#rel'/></type><scope><topicRef href='#s'/></scope><role reifier='#rr'><type><topicRef href='#role'/></type><topicRef href='#a'/></role></association>")
              :keys '("rel" "role" "a" "rr" "s" "ar") :counts '(6 0 0 0 1 1 2)
              :why "Same native scoped Association and Role with independently II-identified Reifiers and inverse references; no cross-Map EQ required."
              :clauses '("CTM 3.3.9-3.3.10,3.13" "XTM 4.3.2,4.18-4.19" "TMDM 5.3.4,5.7-5.8,6.6-6.7")))
            (contrast-tests)
            (check "equivalence:unique-check-labels"
              (= (length topic-maps.xtm-mergemap.tests::*checks*)
                 (length (remove-duplicates topic-maps.xtm-mergemap.tests::*checks* :test #'equal)))))
        (error (c) (setf *checks* (reverse topic-maps.xtm-mergemap.tests::*checks*))
          (when path (write-report path c)) (error c)))
      (setf *checks* (reverse topic-maps.xtm-mergemap.tests::*checks*))
      (when path (write-report path))
      (format t "CTM-XTM-EQUIVALENCE-PASS: ~D checks; ~D actual reader pairs; 3 contrasts; 0 capability gaps.~%"
        (length *checks*) (+ 3 (length (pair-cases))))
      (length *checks*))))
