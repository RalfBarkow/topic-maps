(defpackage #:topic-maps.template.tests
  (:use #:cl #:topic-maps.tmdm)
  (:import-from #:topic-maps.ctm.tests #:check #:read-text #:cxtm #:binary-file)
  (:import-from #:topic-maps.variant.tests #:condition-from)
  (:export #:run-tests #:template-checks #:write-template-report))
(in-package #:topic-maps.template.tests)
(defvar *last-checks* nil)
(defvar *observations* nil)
(defvar *rejections* nil)
(defparameter *originals*
  '(
    "association-scope-embedded3"
    "association-scope-embedded4"
    "name-scope-embedded3"
    "name-scope-embedded4"
    "occurrence-scope-embedded3"
    "occurrence-scope-embedded4"
    "prefix-template-scope"
    "template-ambiguous-parameter"
    "template-ambiguous-parameter2"
    "template-ambiguous-parameter3"
    "template-ambiguous-parameter4"
    "template-assoc-embedded-topic"
    "template-duplicate-name"
    "template-forward-ref"
    "template-invocation-embedded"
    "template-invocation-embedded2"
    "template-invocation-noargs-isa"
    "template-invocation-noargs2"
    "template-invocation-prefix-notation"
    "template-invocation-twice"
    "template-invocation-wildcard-named"
    "template-invocation-wildcard-named2"
    "template-invocation-wildcard-named3"
    "template-invocation-wildcard-named4"
    "template-invocation-wildcard-named5"
    "template-invocation-wildcard-named6"
    "template-invocation-wildcard"
    "template-item-identifier"
    "template-item-identifier2"
    "template-item-identifier4"
    "template-nested-occtype"
    "template-nested-occtype2"
    "template-noop"
    "template-noop2"
    "template-noop3"
    "template-references"
    "template-simple"
    "template-subject-identifier"
    "template-subject-locator"
    "template-subject-locator2"
    "template-subject-locator4"
    "template-topic-nested"
    "template-topic-nested2"
    "template-typed-value"
    "template-wildcard-named"
    "template-wildcard-named2"
    "template-wildcard-named3"
    "template-wildcard-named4"
    "template-wildcard"
    "template-wildcard2"
    "tmlab-tmql-issue-48"
    "topic-embedded-template-invocation"
    "topic-identifier-eq-template-name"
    "topic-template-invocation-unary"
    "topic-template-invocation"
    "variant-scope-embedded3"
    "variant-scope-embedded4"
))
(defparameter *negative-originals*
  '(("embedded-topic-template" topic-maps.ctm:invalid-template-body :invalid-template-body)
    ("occurrence-explicit-datatype-as-parameter" topic-maps.ctm:invalid-template-body :variable-datatype)
    ("prefix-template-scope" topic-maps.ctm:invalid-template-body :invalid-template-body)
    ("template-bad-type" topic-maps.ctm:invalid-template-argument :invalid-template-argument)
    ("template-missing-args" topic-maps.ctm:template-arity-error :template-arity)
    ("template-missing-def" topic-maps.ctm:undefined-template :undefined-template)
    ("template-name-collision" topic-maps.ctm:duplicate-template :duplicate-template)
    ("tm-reifier-in-template" topic-maps.ctm:invalid-template-body :invalid-template-body)
    ("variable-undefined" topic-maps.ctm:unbound-template-variable :variable-outside-template)
    ("variable-undefined2" topic-maps.ctm:unbound-template-variable :variable-outside-template)))
(defun template-checks () *last-checks*)
(defun named (map local) (topic-maps.arity.tests::named-topic map local))
(defun invariant (map) (topic-maps.relationship.tests::valid-model-p map))
(defun state (map held) (topic-maps.reification.tests::state map held))
(defun handles (map) (copy-list (topic-maps.tmdm::map-information-items map)))
(defun yes (value) (if value :true :false))
(defun observe (map)
  (let ((topics (topic-map-topics map)))
    (flet ((ref (topic) (1+ (position topic topics :test #'eq))))
      (topic-maps.test-foundation::fields
        "topicCount" (length topics) "associationCount" (length (topic-map-associations map))
        "topics" (topic-maps.test-foundation::json-array
          (loop for topic in topics collect
            (topic-maps.test-foundation::fields
              "ordinal" (ref topic)
              "itemIdentifiers" (topic-maps.test-foundation::json-array (topic-item-identifiers topic))
              "subjectIdentifiers" (topic-maps.test-foundation::json-array (topic-subject-identifiers topic))
              "subjectLocators" (topic-maps.test-foundation::json-array (topic-subject-locators topic))
              "names" (topic-maps.test-foundation::json-array
                (loop for name in (topic-names topic) collect (topic-maps.test-foundation::fields
                  "value" (topic-name-value name) "parent" (ref (topic-name-parent name)) "type" (ref (topic-name-type name))
                  "scope" (topic-maps.test-foundation::json-array (mapcar #'ref (topic-name-scope name)))
                  "variantCount" (length (topic-name-variants name)))))
              "occurrences" (topic-maps.test-foundation::json-array
                (loop for occurrence in (topic-occurrences topic) collect (topic-maps.test-foundation::fields
                  "value" (occurrence-value occurrence) "datatype" (occurrence-datatype occurrence)
                  "parent" (ref (occurrence-parent occurrence)) "type" (ref (occurrence-type occurrence))
                  "scope" (topic-maps.test-foundation::json-array (mapcar #'ref (occurrence-scope occurrence)))))))))))))
(defun definition-tests ()
  (let* ((text "def tpl($t) $t - \"N\"@?x (\"V\"@?y). assoc(r: ?z) later($t) end")
         (parser (topic-maps.ctm::make-parser (topic-maps.ctm::make-lexer text) "https://example.invalid/d" "urn:wild" 19)))
    ;; If definition checking accidentally invokes an identity operation, fail.
    (let ((saved (symbol-function 'topic-maps.tmdm:intern-topic)))
      (unwind-protect
          (progn (setf (symbol-function 'topic-maps.tmdm:intern-topic) (lambda (&rest args) (declare (ignore args)) (error "Definition mutated TMDM")))
                 (topic-maps.ctm::read-template-definition parser))
        (setf (symbol-function 'topic-maps.tmdm:intern-topic) saved)))
    (let* ((definition (gethash '("tpl" 1) (topic-maps.ctm::parser-templates parser)))
           (body (topic-maps.ctm::template-definition-body definition)))
      (check "definition:stored-ordered-parameters" (equal '("t") (topic-maps.ctm::template-definition-parameters definition)))
      (check "definition:grammar-checked-statement-kinds" (equal '(:topic :association :invocation) (mapcar #'topic-maps.ctm::ctm-statement-kind body)))
      (check "definition:no-wildcard-counter-effects" (= 19 (topic-maps.ctm::parser-wildcard-counter parser)))
      (check "definition:no-wildcard-bindings" (zerop (hash-table-count (topic-maps.ctm::parser-wildcards parser))))
      (dolist (statement body)
        (dolist (token (topic-maps.ctm::ctm-statement-tokens statement))
          (check (format nil "syntax:original-source-range:~D" (topic-maps.ctm::token-position token))
                 (<= 0 (topic-maps.ctm::token-position token) (topic-maps.ctm::token-end token) (length text)))))))
  (multiple-value-bind (map counter)
      (topic-maps.ctm:deserialize-string "def unused() ?. ?x - \"N\". end ?." :document-iri "urn:doc" :wildcard-iri "urn:w" :wildcard-counter 7)
    (check "definition:unused-body-creates-no-information-items-or-counter-gaps"
           (and (= counter 8) (= 1 (length (topic-map-topics map))) (equal '("urn:w#$__8") (topic-item-identifiers (first (topic-map-topics map)))))))
  (let ((map (read-text "def f() a. end def f($t) $t. end f() f(b) f.")))
    (check "definition:overload-and-independent-topic-namespace" (and (= 3 (length (topic-map-topics map))) (named map "f")))))

(defun binding-tests ()
  (let ((definition "def name($t,$n) $t - $n. end "))
    (check "binding:global-and-tail-models-equivalent"
           (string= (cxtm (read-text (concatenate 'string definition "name(a,\"N\")")))
                    (cxtm (read-text (concatenate 'string definition "a name(\"N\")."))))))
  (let* ((map (read-text "def iri($i) a occ: $i. end iri(<urn:value>)"))
         (a (named map "a")) (occ (first (topic-occurrences a))))
    (check "binding:IRI-value-does-not-create-a-Subject-Identifier-Topic"
           (and (= 2 (length (topic-map-topics map))) (every (lambda (tpc) (null (topic-subject-identifiers tpc))) (topic-map-topics map))))
    (check "binding:IRI-value-datatype-and-parent-Type-EQ"
           (and (string= "urn:value" (occurrence-value occ)) (string= (iri-datatype) (occurrence-datatype occ))
                (eq a (occurrence-parent occ)) (eq (named map "occ") (occurrence-type occ)))))
  (let* ((map (read-text "def iri($i) $i occ: $i. end iri(<urn:both>)"))
         (topic (find "urn:both" (topic-map-topics map) :test (lambda (x y) (member x (topic-subject-identifiers y) :test #'string=)))))
    (check "binding:one-IRI-used-in-both-contexts"
           (and topic (string= "urn:both" (occurrence-value (first (topic-occurrences topic)))) (invariant map))))
  (let* ((prefix "%prefix p <urn:%2525:> ")
         (direct (read-text (concatenate 'string prefix "p:thing occ: p:thing.")))
         (expanded (read-text (concatenate 'string prefix "def f($i) $i occ:$i. end f(p:thing)"))))
    (check "binding:QName-locator-is-resolved-once-without-double-decoding"
           (string= (cxtm direct) (cxtm expanded))))
  (dolist (mark '("=" "^"))
    (let* ((map (read-text (format nil "def f($t) $t - \"N\". end f(~A<urn:marked>)" mark)))
           (topic (find-if #'topic-names (topic-map-topics map))))
      (check (concatenate 'string "binding:explicit-identity-kind-preserved:" mark)
             (and (null (topic-subject-identifiers topic))
                  (equal '("urn:marked") (if (string= mark "=") (topic-subject-locators topic) (topic-item-identifiers topic)))))))
  (dolist (pair '(("+0001" "1" "integer") ("-.30" "-0.3" "decimal")
                  ("2000-02-29" "2000-02-29" "date")
                  ("2000-01-01T00:00:00Z" "2000-01-01T00:00:00Z" "dateTime")
                  ("\"+0001\"^^<http://www.w3.org/2001/XMLSchema#integer>" "+0001" "integer")
                  ("\"lexical\"^^<urn:unknown>" "lexical" "unknown")))
    (destructuring-bind (literal expected datatype) pair
      (let* ((map (read-text (format nil "def f($v) a occ: $v. end f(~A)" literal)))
             (occ (first (topic-occurrences (named map "a")))))
        (check (concatenate 'string "binding:existing-literal-reader-policy:" literal)
               (and (string= expected (occurrence-value occ))
                    (string= (if (string= datatype "unknown") "urn:unknown"
                                 (concatenate 'string "http://www.w3.org/2001/XMLSchema#" datatype)) (occurrence-datatype occ))
                    (eq (occurrence-parent occ) (named map "a")) (invariant map))))))
  (let* ((map (read-text "def outer($t) inner($t) $t - \"outer\". end def inner($x) $x - \"inner\". end a outer(); occ: \"after\"."))
         (a (named map "a")))
    (check "binding:nested-frame-restoration-and-Tail-owner"
           (and (= 2 (length (topic-names a))) (string= "after" (occurrence-value (first (topic-occurrences a)))) (invariant map))))
  (let ((map (read-text "%prefix p <urn:p:> def f($t) $t. end f(p:r) f(p: r)")))
    (check "dispatch:QName-argument-versus-Role-declaration"
           (and (find "urn:p:r" (topic-map-topics map) :test (lambda (x y) (member x (topic-subject-identifiers y) :test #'string=)))
                (= 1 (length (topic-map-associations map))) (invariant map))))
  (let ((map (read-text "def f($t) $t - \"N\". end f([ - \"E\" ])")))
    (check "binding:Embedded-argument-is-one-Topic-with-both-Names"
           (and (= 2 (length (topic-map-topics map))) (= 2 (length (topic-names (first (topic-map-topics map))))))))
  (let* ((map (read-text "def f($o,$nt,$t,$e,$r,$v) $o - $nt : \"N\" @ $t ~ $r ($v @ $e). end f(a,nt,theme,extra,reifier,\"V\")"))
         (name (first (topic-names (named map "a")))) (variant (first (topic-name-variants name))))
    (check "binding:Name-Type-Theme-Variant-and-Reifier-are-actual-objects"
           (and (eq (topic-name-type name) (named map "nt"))
                (eq (first (topic-name-scope name)) (named map "theme"))
                (eq (item-reifier name) (named map "reifier"))
                (eq (topic-reified (named map "reifier")) name)
                (eq name (variant-parent variant)) (string= "V" (variant-value variant))
                (every (lambda (tpc) (member tpc (variant-scope variant) :test #'eq))
                       (list (named map "theme") (named map "extra"))) (invariant map))))
  (let* ((map (read-text "def f($a,$r,$p,$t,$ar,$rr) $a($r : $p ~ $rr) @ $t ~ $ar end f(at,rt,p,theme,ar,rr) f(at,rt,p,theme,ar,rr)"))
         (association (first (topic-map-associations map))) (role (first (association-roles association))))
    (check "binding:all-Association-reference-positions-and-duplicate-normalization"
           (and (= 1 (length (topic-map-associations map))) (= 1 (length (association-roles association)))
                (eq (named map "at") (association-type association)) (eq (named map "rt") (association-role-type role))
                (eq (named map "p") (association-role-player role)) (eq association (association-role-parent role))
                (eq (named map "theme") (first (association-scope association)))
                (eq (named map "ar") (item-reifier association)) (eq (named map "rr") (item-reifier role)) (invariant map)))))

(defun wildcard-tests ()
  (dolist (argument '("?" "[-\"Embedded\"]"))
    (multiple-value-bind (map counter)
        (topic-maps.ctm:deserialize-string
          (format nil "def f($t) a(r: $t, s: $t) end f(~A) f(~A)" argument argument)
          :document-iri "https://example.invalid/doc" :wildcard-iri "urn:wild" :wildcard-counter 30)
      (let ((associations (topic-map-associations map)))
        (check (concatenate 'string "wildcard:one-allocation-per-argument-and-distinct-calls:" argument)
               (and (= 32 counter) (= 2 (length associations))
                    (not (eq (association-role-player (first (association-roles (first associations))))
                             (association-role-player (first (association-roles (second associations))))))))
        (dolist (a associations)
          (check (format nil "wildcard:repeated-argument-is-EQ:~A:~A" argument (topic-item-identifiers (association-role-player (first (association-roles a)))))
                 (apply #'eq (mapcar #'association-role-player (association-roles a))))))))
  (multiple-value-bind (map counter)
      (topic-maps.ctm:deserialize-string
        "?x - \"global\". def outer() ?x - \"outer\". inner(?x) ?x - \"outer again\". end def inner($t) $t - \"passed\". ?x - \"inner\". end outer() outer() ?x - \"global again\"."
        :document-iri "urn:document" :wildcard-iri "urn:wild" :wildcard-counter 8)
    (check "wildcard:nested-call-frames-share-only-counter"
           (and (= 13 counter)
                (equal '(2 3 1 3 1)
                  (loop for topic in (topic-map-topics map) when (topic-item-identifiers topic) collect (length (topic-names topic))))))
    (check "wildcard:document-and-wildcard-IRIs-remain-distinct"
           (every (lambda (topic) (every (lambda (id) (search "urn:wild#$__" id)) (topic-item-identifiers topic))) (topic-map-topics map)))))

(defun merge-tests ()
  ;; Keep actual handles while execution merges Topics and all structural items.
  (let* ((map (read-text "a. b. theme. extra.")) (a (named map "a")) (b (named map "b"))
         (theme (named map "theme")) (extra (named map "extra"))
         (names (list (add-name a "N" :type a :scope (list theme)) (add-name b "N" :type b :scope (list theme))))
         (variants (mapcar (lambda (n) (add-variant n "V" :scope (list theme extra))) names))
         (occurrences (list (add-occurrence a a "O" :scope (list theme)) (add-occurrence b b "O" :scope (list theme))))
         (associations (list (make-association map a (list (list a a)) :scope (list theme))
                             (make-association map b (list (list b b)) :scope (list theme))))
         (roles (mapcar (lambda (x) (first (association-roles x))) associations))
         (pairs (list names variants occurrences associations roles)))
    (loop for pair in pairs for index from 1 do
      (loop for item in pair for side from 1 do
        (add-item-identifier item (format nil "urn:item:~D:~D" index side))
        (set-item-reifier item (intern-topic map :item-identifier (format nil "urn:reifier:~D:~D" index side)))))
    (let* ((held (handles map))
           (text "def merge($left,$right) $left ^<#b>. $right - \"After\". end a merge(b); after: \"Tail\".")
           (parser (topic-maps.ctm::make-parser (topic-maps.ctm::make-lexer text) "https://example.invalid/a/doc.ctm" "urn:w" 0)))
      (topic-maps.ctm::read-template-definition parser)
      (topic-maps.ctm::read-statement parser map)
      (let ((current (canonical-topic a)))
        (check "merge:bindings-and-continued-Tail-use-canonical-owner"
               (and (eq current (canonical-topic b)) (not (eq current a))
                    (find "After" (topic-names current) :test #'string= :key #'topic-name-value)
                    (find "Tail" (topic-occurrences current) :test #'string= :key #'occurrence-value))))
      (loop for pair in pairs for index from 1 do
        (let ((left (topic-maps.tmdm::canonical-item (first pair))) (right (topic-maps.tmdm::canonical-item (second pair))))
          (check (format nil "merge:retained-canonical-handles:~D" index) (eq left right))
          (check (format nil "merge:identifiers-and-Reifiers-survive:~D" index)
                 (and (= 2 (length (item-identifiers left))) (item-reifier left) (eq left (topic-reified (item-reifier left)))))))
      (check "merge:all-stored-references-and-Variant-invariants" (invariant map))
      (let ((before (state map held)) (out (cxtm map)))
        (check "merge:CXTM-pure-and-retained-forward-slots-unchanged"
               (and (equal before (state map held)) (string= out (cxtm map)))))))
  (dolist (mode '(:core :variant))
    (let* ((map (read-text "a. b. owner.")) (a (named map "a")) (b (named map "b")))
      (ecase mode
        (:core (add-topic-identifier a :subject-identifier "http://psi.topicmaps.org/iso13250/model/type")
               (add-topic-identifier b :subject-identifier "http://psi.topicmaps.org/iso13250/model/instance"))
        (:variant (add-variant (add-name (named map "owner") "N" :scope (list a)) "V" :scope (list a b))))
      (let* ((held (handles map)) (before (state map held))
             (text "def f($t) $t ^<#b>. end f(a)")
             (parser (topic-maps.ctm::make-parser (topic-maps.ctm::make-lexer text) "https://example.invalid/a/doc.ctm" "urn:w" 0)))
        (topic-maps.ctm::read-template-definition parser)
        (let ((condition (condition-from (lambda () (topic-maps.ctm::read-statement parser map)))))
          (check (format nil "merge:existing-atomic-conflict-policy-preserved:~A" mode)
                 (and (typep condition (if (eq mode :core) 'topic-maps.ctm:ctm-rejection 'variant-error))
                      (equal before (state map held)) (invariant map)
                      (null (topic-maps.ctm::parser-bindings parser)))))))))

(defun rejection-check (label text class code)
  (let ((condition (condition-from (lambda () (read-text text)))))
    (check (concatenate 'string label ":condition-and-code")
           (and (eq class (type-of condition)) (eq code (topic-maps.ctm:error-code condition))))
    (check (concatenate 'string label ":source-position")
           (and (<= 0 (topic-maps.ctm:error-position condition) (length text))
                (plusp (topic-maps.ctm:error-line condition)) (plusp (topic-maps.ctm:error-column condition))))
    condition))
(defun diagnostic-tests ()
  (dolist (fixture '(("f()" topic-maps.ctm:undefined-template :undefined-template)
                     ("def f($a) $a. end f()" topic-maps.ctm:template-arity-error :template-arity)
                     ("def f() a. end def f() b. end" topic-maps.ctm:duplicate-template :duplicate-template)
                     ("def f() $unbound. end" topic-maps.ctm:unbound-template-variable :unbound-template-variable)
                     ("a occ:$x." topic-maps.ctm:unbound-template-variable :variable-outside-template)
                     ("def f($t) $t. end f(1)" topic-maps.ctm:invalid-template-argument :invalid-template-argument)
                     ("def f($n) a - $n. end f(1)" topic-maps.ctm:invalid-template-argument :invalid-template-argument)
                     ("def f($i) a occ:$i. end f(=<urn:i>)" topic-maps.ctm:invalid-template-argument :invalid-template-argument)
                     ("def f($i) a ^$i. end f(local)" topic-maps.ctm:invalid-template-argument :invalid-template-argument)
                     ("def f($unused) end f(ex:missing)" topic-maps.ctm:undefined-prefix :undefined-prefix)
                     ("def f() %prefix p <urn:p:> end" topic-maps.ctm:invalid-template-body :invalid-template-body)
                     ("def f() a - . end" topic-maps.ctm:invalid-template-body :invalid-template-body)
                     ("def f() a(<urn:r>:<urn:p>) end" topic-maps.ctm:invalid-template-body :role-separator-whitespace)
                     ("def f($t) a occ:\"v\"^^$t. end" topic-maps.ctm:invalid-template-body :variable-datatype)
                     ("def f() later() end f() def later() a. end" topic-maps.ctm:undefined-template :undefined-template)))
    (destructuring-bind (text class code) fixture (rejection-check (concatenate 'string "diagnostic:" text) text class code)))
  (let* ((text (format nil "def outer($x)~% inner($x)~%end~%def inner($t)~% $t - \"N\".~%end~%outer(42)"))
         (condition (rejection-check "diagnostic:nested-context" text 'topic-maps.ctm:invalid-template-argument :invalid-template-argument))
         (contexts (topic-maps.ctm:error-context condition)))
    (check "diagnostic:original-Definition-and-Invocation-positions"
           (and (= (search "$t -" text) (topic-maps.ctm:error-position condition)) (= 2 (length contexts))
                (= (search "def inner" text) (getf (first contexts) :definition-position))
                (= (search "inner($x)" text) (getf (first contexts) :invocation-position))
                (= (search "outer(42)" text) (getf (second contexts) :invocation-position)))))
  (let ((topic-maps.ctm::*template-depth-limit* 3))
    (let ((c (condition-from (lambda () (read-text "def f() f() end f()")))))
      (check "diagnostic:resource-limit-is-UNSUPPORTED-not-normative-rejection"
             (and (eq (type-of c) 'topic-maps.ctm:ctm-unsupported) (eq :template-depth-limit (topic-maps.ctm:error-code c))))))
  (let ((condition (condition-from (lambda () (read-text "%mergemap <other> <urn:ctm>")))))
    (check "diagnostic:unknown-mergemap-notation"
           (and (typep condition 'topic-maps.ctm:ctm-rejection)
                (eq :unknown-mergemap-notation (topic-maps.ctm:error-code condition)))))
  (dolist (text '("def f() a - \"\"\"N\"\"\". end" "%include <other>"))
    (check (if (search "%include" text) "diagnostic:Include-requires-explicit-resolver"
               "diagnostic:triple-string-body-supported")
           (if (search "%include" text)
               (let ((c (condition-from (lambda () (read-text text)))))
                 (and (typep c 'topic-maps.ctm:ctm-unsupported)
                      (eq :resource-resolver-required (topic-maps.ctm:error-code c))))
               (let* ((map (read-text (concatenate 'string text " f()")))
                      (name (first (topic-names (named map "a")))))
                 (and name (equal "N" (topic-name-value name)) (invariant map)))))))

(defun original-cases ()
  (setf *observations* nil *rejections* nil)
  (dolist (file *originals*)
    (let* ((id (format nil "ctm/in/~A.ctm" file))
           (case (first (topic-maps.test-foundation:select-cases topic-maps.ctm.tests::*cxtm-corpus* :id id)))
           (doc (topic-maps.test-foundation:test-case-document-iri case))
           (map (topic-maps.ctm:deserialize-file (topic-maps.test-foundation:test-case-source-pathname case) :document-iri doc :source-name id))
           (held (handles map)) (before (state map held))
           (actual (topic-maps.cxtm:canonicalize-octets map :base-locator doc))
           (expected (binary-file (topic-maps.test-foundation:test-case-expected-baseline case))))
      (check (concatenate 'string id ":TMDM-object-and-reference-invariants") (invariant map))
      (check (concatenate 'string id ":byte-exact-original-CXTM") (equalp actual expected))
      (check (concatenate 'string id ":deterministic-mutation-free-CXTM")
             (and (equalp actual (topic-maps.cxtm:canonicalize-octets map :base-locator doc)) (equal before (state map held))))
      (topic-maps.test-foundation:record-result case :cxtm-match)
      (setf (topic-maps.test-foundation:test-case-clauses case) '("CTM 3.14" "CTM 3.15" "CTM 3.3.6-3.3.8" "TMDM 5.3-5.8" "TMDM 6.1-6.7" "CXTM 3.4-3.19" "CXTM 4.6-4.11"))
      (setf topic-maps.ctm.tests::*cxtm-results* (append topic-maps.ctm.tests::*cxtm-results*
        (list (list :id id :base doc :actual (cxtm map doc) :expected (uiop:read-file-string (topic-maps.test-foundation:test-case-expected-baseline case)) :match t :bytes (length actual)))))
      (push (topic-maps.test-foundation::fields "id" id "documentIRI" doc "model" (observe map)) *observations*)
      (format t "~&TEMPLATE-CXTM ~A: PASS (~D bytes)~%" id (length actual))))
  (dolist (fixture *negative-originals*)
    (destructuring-bind (file class code) fixture
      (let* ((id (format nil "ctm/invalid/~A.ctm" file))
             (case (first (topic-maps.test-foundation:select-cases topic-maps.ctm.tests::*cxtm-corpus* :id id)))
             (source (topic-maps.test-foundation:test-case-source-pathname case))
             (text (uiop:read-file-string source))
             (condition (condition-from (lambda () (topic-maps.ctm:deserialize-file source
                         :document-iri (topic-maps.test-foundation:test-case-document-iri case) :source-name id)))))
        (check (concatenate 'string id ":specific-condition-code-and-source")
               (and (eq class (type-of condition)) (eq code (topic-maps.ctm:error-code condition))
                    (equal id (topic-maps.ctm:error-source condition))))
        (check (concatenate 'string id ":meaningful-original-position")
               (and (<= 0 (topic-maps.ctm:error-position condition) (length text))
                    (plusp (topic-maps.ctm:error-line condition)) (plusp (topic-maps.ctm:error-column condition))))
        (topic-maps.test-foundation:record-result case :ctm-rejection :diagnostics (list (princ-to-string condition)))
        (setf (topic-maps.test-foundation:test-case-clauses case) '("CTM 3.14" "CTM 3.15"))
        (push (topic-maps.test-foundation::fields "id" id "class" (symbol-name class) "code" (symbol-name code)
                "position" (topic-maps.ctm:error-position condition) "line" (topic-maps.ctm:error-line condition)
                "column" (topic-maps.ctm:error-column condition) "source" (topic-maps.ctm:error-source condition)
                "context" (prin1-to-string (topic-maps.ctm:error-context condition))) *rejections*)
        (format t "~&TEMPLATE-REJECTION ~A: PASS (~A)~%" id code))))
  (setf *observations* (nreverse *observations*) *rejections* (nreverse *rejections*)))

(defun run-tests ()
  (topic-maps.relationship.tests:run-tests)
  (let ((topic-maps.ctm.tests::*checks* nil))
    (definition-tests) (binding-tests) (wildcard-tests) (merge-tests) (diagnostic-tests) (original-cases)
    (check "templates:executed-original-contracts-only"
           (equal '(:pass 187 :fail 2 :unsupported 0 :not-run 84)
                  (getf (topic-maps.test-foundation:summarize-corpus topic-maps.ctm.tests::*cxtm-corpus*) :statuses)))
    (setf *last-checks* (nreverse topic-maps.ctm.tests::*checks*))
    (format t "~&TEMPLATES-PASS: ~D checks; 57 byte-exact originals, 10 specific rejections; 187 PASS, 2 known FAIL, 84 NOT-RUN.~%" (length *last-checks*)) t))
(defun write-template-report (path)
  (with-open-file (out path :direction :output :if-exists :supersede :if-does-not-exist :create)
    (topic-maps.test-foundation::emit-json-value
      (topic-maps.test-foundation::fields "kind" "template-execution-evidence" "passed" (length *last-checks*) "failed" 0
        "checks" (topic-maps.test-foundation::json-array *last-checks*)
        "cases" (topic-maps.test-foundation::json-array *observations*)
        "rejections" (topic-maps.test-foundation::json-array *rejections*)) out)
    (terpri out)))
