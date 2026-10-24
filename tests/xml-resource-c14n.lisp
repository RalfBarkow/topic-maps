(in-package #:topic-maps.xtm.tests)

(defvar *cr-results* nil)
(defvar *cr-native* nil)
(defvar *cr-controls* nil)
(defvar *cr-executed* nil)
(defun cr-hex (octets) (format nil "~{~2,'0X~}" (coerce octets 'list)))
(defun cr-dom-state (node)
  (list (dom:node-type node) (dom:node-name node) (dom:node-value node)
    (when (eq (dom:node-type node) :element)
      (loop for i below (dom:length (dom:attributes node)) for a = (dom:item (dom:attributes node) i)
            collect (list (dom:name a) (dom:namespace-uri a) (dom:local-name a) (dom:value a))))
    (loop for i below (dom:length (dom:child-nodes node)) collect (cr-dom-state (dom:item (dom:child-nodes node) i)))))
(defun cr-native (id value)
  (let* ((map (make-topic-map)) (owner (intern-topic map :item-identifier "urn:cr:owner"))
         (type (intern-topic map :subject-identifier "urn:cr:type"))
         (nt (intern-topic map :subject-identifier "urn:cr:name-type"))
         (base (intern-topic map :subject-identifier "urn:cr:base"))
         (extra (intern-topic map :subject-identifier "urn:cr:extra"))
         (name (add-name owner "N" :type nt :scope (list base)))
         (dt "http://www.w3.org/2001/XMLSchema#anyType")
         (o (add-occurrence owner type value :datatype dt :scope (list extra)))
         (v (add-variant name value :datatype dt :scope (list base extra)))
         (before (ik-state map))
         (a (topic-maps.cxtm:canonicalize-octets map :base-locator "urn:cr:map"))
         (b (topic-maps.cxtm:canonicalize-octets map :base-locator "urn:cr:map")))
    (check (format nil "resource-c14n-native:~A:lossless-occurrence-variant" id)
      (and (equal value (occurrence-value o)) (equal value (variant-value v))
           (equal dt (occurrence-datatype o)) (equal dt (variant-datatype v))))
    (check (format nil "resource-c14n-native:~A:canonical-parent-type-scope-EQ" id)
      (and (eq owner (occurrence-parent o)) (eq type (occurrence-type o))
           (eq name (variant-parent v)) (eq o (canonical-occurrence o)) (eq v (canonical-variant v))
           (scope-eq-p (list extra) (occurrence-scope o)) (scope-eq-p (list base extra) (variant-scope v))))
    (check (format nil "resource-c14n-native:~A:pure-CXTM-no-topics-from-XML" id)
      (and (= 5 (length (topic-map-topics map))) (equalp a b) (equal before (ik-state map))))
    (push (mm-fields "id" id "value" value "datatype" dt "occurrenceValue" (occurrence-value o)
      "variantValue" (variant-value v) "canonicalReferencesEQ" :true "topicCount" 5
      "repeatedCXTMPure" :true "readerIntegration" :false "actualCXTMHex" (cr-hex a)) *cr-native*)))
(defun cr-probe (id raw expected origin &key root-vector)
  (let* ((copy (copy-seq raw)) (ctx (topic-maps.xml:parse-canonical-context raw))
         (doc (topic-maps.xml::%canonical-context-document ctx)) (state (cr-dom-state doc))
         (want (bytes expected)))
    (flet ((run ()
             (if root-vector
                 ;; Independent W3C examples with document root selected. This
                 ;; private engine is the SAME engine as the public XTM adapter.
                 ;; The examples use all their namespace bindings, so XTM's
                 ;; filter makes no change to their published node set/result.
                 (let ((s (topic-maps.xml::%canonical-subtrees (list (dom:document-element doc)))))
                   (values s (bytes s)))
                 (topic-maps.xml:canonicalize-resource-data ctx))))
      (multiple-value-bind (value actual) (run)
        (multiple-value-bind (again repeated) (run)
          (check (format nil "resource-c14n:~A:exact-independent-bytes" id) (equalp want actual))
          (check (format nil "resource-c14n:~A:UTF8-string-and-repeat" id)
            (and (equal expected value) (equalp actual (bytes value)) (equal value again) (equalp actual repeated))))
        (check (format nil "resource-c14n:~A:input-context-unchanged" id)
          (and (equalp raw copy) (equal state (cr-dom-state doc))))
        (unless root-vector (cr-native id value))
        (push (mm-fields "id" id "origin" origin "inputHex" (cr-hex raw) "expectedHex" (cr-hex want)
          "actualHex" (cr-hex actual) "expectedXML" expected "actualXML" value
          "expectedBytes" (length want) "actualBytes" (length actual) "firstDifferentByte" (mismatch want actual)
          "byteIdentical" :true "repeatedPure" :true "publicXTMProjection" (if root-vector :false :true)) *cr-results*)))))

(defun cr-extra-specs ()
  (list
    (list "prefix-shadowing" (cq-wrap "<p:a><p:b xmlns:p='urn:two'><p:c/></p:b><p:d/></p:a>" " xmlns:p='urn:one'")
      "<p:a xmlns:p=\"urn:one\"><p:b xmlns:p=\"urn:two\"><p:c></p:c></p:b><p:d></p:d></p:a>" "C14N 2.3: original prefixes, nearest namespace bindings")
    (list "default-namespace-changes" (cq-wrap "<a><b xmlns=''><c xmlns='urn:inner'/></b><d/></a>" " xmlns='urn:outer'")
      "<a xmlns=\"urn:outer\"><b xmlns=\"\"><c xmlns=\"urn:inner\"></c></b><d></d></a>" "C14N 2.3: selected-parent default namespace and empty reset")
    (list "global-namespace-filter" (cq-wrap "<a><p:b/></a>" " xmlns:p='urn:p' xmlns:q='urn:unused'")
      "<a xmlns:p=\"urn:p\"><p:b></p:b></a>" "XTM 4.16.3: namespace pair used anywhere in selected set; not Exclusive C14N")
    (list "same-URI-different-prefix" (cq-wrap "<p:a><q:b q:v='1'/></p:a>" " xmlns:p='urn:same' xmlns:q='urn:same' xmlns:z='urn:same'")
      "<p:a xmlns:p=\"urn:same\" xmlns:q=\"urn:same\"><q:b q:v=\"1\"></q:b></p:a>" "XTM 4.16.3 filters by URI AND prefix, not URI alone")
    (list "QName-attribute-value-not-namespace-use" (cq-wrap "<a hint='p:x'/>" " xmlns:p='urn:p'")
      "<a hint=\"p:x\"></a>" "Only element/attribute names establish namespace use, not values")
    (list "filtered-parent-namespace-gap" (cq-wrap "<p:a><b xmlns:p='urn:unused'><p:c xmlns:p='urn:one'/></b></p:a>" " xmlns:p='urn:one'")
      "<p:a xmlns:p=\"urn:one\"><b><p:c xmlns:p=\"urn:one\"></p:c></b></p:a>" "C14N 2.3 compares namespace nodes of nearest selected parent, not cumulative rendered map")
    (list "xml-attributes-inherited" "<outer xml:lang='de' xml:space='preserve'><xtm:resourceData xmlns:xtm='http://www.topicmaps.org/xtm/' xml:lang='fr'><x/><x xml:lang='en'><y/></x></xtm:resourceData></outer>"
      "<x xml:lang=\"fr\" xml:space=\"preserve\"></x><x xml:lang=\"en\" xml:space=\"preserve\"><y></y></x>" "C14N 1.0 2.4: nearest inherited xml:* on each apex; local override")
    (list "xml-base-is-1.0-not-1.1" "<outer xml:base='https://example.invalid/' xml:id='ancestor'><xtm:resourceData xmlns:xtm='http://www.topicmaps.org/xtm/' xml:base='child/'><x/></xtm:resourceData></outer>"
      "<x xml:base=\"child/\" xml:id=\"ancestor\"></x>" "C14N 1.0 2.4: all xml:* inherited, no 1.1 base fixup/id exception")
    (list "empty-content" (cq-wrap "") "" "XTM descendant node set may be empty")
    (list "empty-CDATA" (cq-wrap "<![CDATA[]]>") "" "Empty character information contributes no bytes")
    (list "text-only" (cq-wrap " A&amp;B&lt;C&gt;&quot;&#x9;&#xA;&#xD; ")
      (format nil " A&amp;B&lt;C&gt;\"~C~C&#xD; " #\Tab #\Newline) "XTM selected characters, C14N text escaping without container")
    (list "several-apices-mixed-text" (cq-wrap "a<x/>b<y/>c") "a<x></x>b<y></y>c" "Selected document order, no invented fragment wrapper")
    (list "attribute-order-same-URI" (cq-wrap "<x xmlns:a='urn:s' xmlns:z='urn:s' z:a='1' a:z='2' z:A='3' B='4' a='5'/>")
      "<x xmlns:a=\"urn:s\" xmlns:z=\"urn:s\" B=\"4\" a=\"5\" z:A=\"3\" z:a=\"1\" a:z=\"2\"></x>" "C14N 2.2: codepoint order, namespace URI then local name")
    (list "attribute-greater-than-and-whitespace" (cq-wrap (format nil "<x a='>&quot;~C~C&#x9;&#xA;&#xD;'/>" #\Tab #\Newline))
      "<x a=\">&quot;  &#x9;&#xA;&#xD;\"></x>" "XML whitespace normalization vs character references; > not escaped in attributes")
    (list "no-Unicode-normalization-UTF8" (cq-wrap (format nil "<x>e~C</x>" (code-char #x301)))
      (format nil "<x>e~C</x>" (code-char #x301)) "C14N 1.0 4.2: no normalization of UCS-based source character data")
    (list "in-content-BOM-is-text" (cq-wrap (format nil "<x>A~CB</x>" (code-char #xfeff)))
      (format nil "<x>A~CB</x>" (code-char #xfeff)) "Only encoding BOM is removed, not U+FEFF in character content")))

(defun cr-official-vectors ()
  ;; Independent normative examples. The original full examples 3.1/3.3/3.4/
  ;; 3.5/3.7 contain a DTD or arbitrary XPath selection and are NOT claimed run.
  ;; The e5 subvector is copied as a complete element with all its namespaces;
  ;; it has no dependency on the e9 default attribute in the enclosing DTD.
  (let ((ws (format nil "<doc>~%   <clean>   </clean>~%   <dirty>   A   B   </dirty>~%   <mixed>~%      A~%      <clean>   </clean>~%      B~%      <dirty>   A   B   </dirty>~%      C~%   </mixed>~%</doc>")))
    (list
      (list "w3c-3.2-whitespace" (bytes ws) ws "https://www.w3.org/TR/2001/REC-xml-c14n-20010315#Example-WhitespaceInContent; complete unchanged example; root node set")
      (list "w3c-3.3-e5-subvector" (bytes "<e5 a:attr=\"out\" b:attr=\"sorted\" attr2=\"all\" attr=\"I'm\"
      xmlns:b=\"http://www.ietf.org\"
      xmlns:a=\"http://www.w3.org\"
      xmlns=\"http://example.org\"/>")
        "<e5 xmlns=\"http://example.org\" xmlns:a=\"http://www.w3.org\" xmlns:b=\"http://www.ietf.org\" attr=\"I'm\" attr2=\"all\" b:attr=\"sorted\" a:attr=\"out\"></e5>"
        "https://www.w3.org/TR/2001/REC-xml-c14n-20010315#Example-SETags; independent e5 element/output excerpt; NOT the DTD-containing full example")
      (list "w3c-3.6-ISO8859-1" (bytes (format nil "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>~%<doc>&#169;</doc>") :iso-8859-1)
        "<doc>©</doc>" "https://www.w3.org/TR/2001/REC-xml-c14n-20010315#Example-UTF8; complete original input; published C2 A9 byte expectation"))))

(defun cr-security-tests ()
  (dolist (source '("<!DOCTYPE x><x/>" "<!DOCTYPE x [<!ENTITY a 'secret'>]><x>&a;</x>"
                    "<!DOCTYPE x SYSTEM 'file:///tmp/no-resource-c14n-read'><x/>"
                    "<!DOCTYPE x SYSTEM 'https://example.invalid/no-resource-c14n'><x/>"
                    "<!DOCTYPE x [<!ENTITY a SYSTEM 'file:///tmp/no-resource-c14n-read'>]><x>&a;</x>"))
    (let ((c (condition-from (lambda () (topic-maps.xml:parse-canonical-context (bytes source))))))
      (check (format nil "resource-c14n-security:DOCTYPE-denied:~A" source) (typep c 'topic-maps.xml:doctype-forbidden))
      (push (mm-fields "source" source "expected" "DOCTYPE-FORBIDDEN" "condition" (cq-condition c)) *cr-controls*)))
  (dolist (source '("<x><y></x>" "<x xmlns:p='urn:a' xmlns:q='urn:a' p:a='1' q:a='2'/>"
                    "<p:x/>" "<x>&unknown;</x>" "<x a='1' a='2'/>"))
    (let ((c (condition-from (lambda () (topic-maps.xml:parse-canonical-context (bytes source))))))
      (check (format nil "resource-c14n-security:XML-rejected:~A" source) (typep c 'cxml:well-formedness-violation))
      (push (mm-fields "source" source "expected" "WELL-FORMEDNESS-VIOLATION" "condition" (cq-condition c)) *cr-controls*)))
  (let ((raw (concatenate '(vector (unsigned-byte 8)) (bytes (cq-wrap "")) #(255))))
    (let ((c (condition-from (lambda () (topic-maps.xml:parse-canonical-context raw)))))
      (check "resource-c14n-security:invalid-UTF8-rejected" (typep c 'cxml:well-formedness-violation))
      (push (mm-fields "id" "invalid-UTF8" "inputHex" (cr-hex raw) "condition" (cq-condition c)) *cr-controls*)))
  (dolist (marker '(cxml::*topic-maps-encoding-patch* runes-encoding::*topic-maps-encoding-patch*))
    (let ((c (progv (list marker) '(nil)
               (condition-from (lambda () (topic-maps.xml:parse-canonical-context (bytes "<x/>")))))))
      (check (format nil "resource-c14n-security:qualification-required:~S" marker) (typep c 'topic-maps.xml:unqualified-parser))
      (push (mm-fields "id" (format nil "marker:~S" marker) "condition" (cq-condition c)) *cr-controls*)))
  ;; Observe the actual new parser call, including the deny function. Calling it
  ;; directly proves it signals rather than returning NIL (which enables OPEN).
  (let ((original (symbol-function 'cxml:parse-octets)) (args nil))
    (unwind-protect
      (progn
        (setf (symbol-function 'cxml:parse-octets)
          (lambda (raw handler &rest options) (setf args options) (apply original raw handler options)))
        (topic-maps.xml:parse-canonical-context (bytes "<x/>")))
      (setf (symbol-function 'cxml:parse-octets) original))
    (check "resource-c14n-security:actual-parser-options"
      (and (null (getf args :validate)) (getf args :disallow-internal-subset)
           (eq (getf args :entity-resolver) #'topic-maps.xml::deny-external-resource)))
    (dolist (uri '("file:///tmp/no-resource-c14n-read" "https://example.invalid/no-resource-c14n"))
      (let ((c (condition-from (lambda () (funcall (getf args :entity-resolver) nil uri)))))
        (check (format nil "resource-c14n-security:resolver-never-returns:~A" uri)
          (and (typep c 'topic-maps.xml:external-resource-forbidden) (equal uri (topic-maps.xml:denied-system-id c))))
        (push (mm-fields "id" uri "condition" (cq-condition c)) *cr-controls*))))
  (let* ((symbols '(sax:*namespace-processing* sax:*include-xmlns-attributes* sax:*use-xmlns-namespace* cxml:*catalog* cxml:*cache-all-dtds* cxml:*dtd-cache*))
         (before (mapcar #'symbol-value symbols)))
    (let ((sax:*namespace-processing* nil) (sax:*include-xmlns-attributes* nil) (sax:*use-xmlns-namespace* nil))
      (check "resource-c14n-security:explicit-context-overrides-ambient-parser-flags"
        (equal "<p:x xmlns:p=\"urn:p\"></p:x>"
          (topic-maps.xml:canonicalize-resource-data (topic-maps.xml:parse-canonical-context (bytes (cq-wrap "<p:x/>" " xmlns:p='urn:p'")))))))
    (check "resource-c14n-security:all-global-parser-settings-unchanged" (equal before (mapcar #'symbol-value symbols))))
  (let ((c (condition-from (lambda () (topic-maps.xml:parse-octets (bytes "<x/>") (cxml-dom:make-dom-builder))))))
    (check "resource-c14n-security:old-XML-byte-boundary-still-unchanged"
      (and c (search "SAX configuration is incompatible with DOM" (princ-to-string c)))))
  (dolist (source (list (cq-wrap "<x xmlns:p='relative'/>")
                        "<outer xmlns:p='relative'><xtm:resourceData xmlns:xtm='http://www.topicmaps.org/xtm/'/></outer>"))
    (let ((c (condition-from (lambda () (topic-maps.xml:canonicalize-resource-data (topic-maps.xml:parse-canonical-context (bytes source)))))))
      (check (format nil "resource-c14n-security:relative-namespace-rejected:~A" source)
        (and (typep c 'topic-maps.xml:canonicalization-error) (eq :relative-namespace-uri (topic-maps.xml:canonicalization-error-code c))))
      (push (mm-fields "source" source "condition" (cq-condition c)) *cr-controls*)))
  (let* ((ctx (topic-maps.xml:parse-canonical-context (bytes "<x/>")))
         (c (condition-from (lambda () (topic-maps.xml:canonicalize-resource-data ctx)))))
    (check "resource-c14n-api:missing-resourceData-is-an-explicit-error"
      (and (zerop (topic-maps.xml:resource-data-count ctx)) (typep c 'topic-maps.xml:canonicalization-error)
           (eq :resource-data-index (topic-maps.xml:canonicalization-error-code c)))))
  (check "resource-c14n-api:raw-context-constructor-not-exported"
    (not (eq :external (nth-value 1 (find-symbol "%MAKE-CANONICAL-CONTEXT" :topic-maps.xml)))))
  t)

(defun cr-tests ()
  (setf *cr-results* nil *cr-native* nil *cr-controls* nil *cr-executed* nil)
  ;; Reuse all existing 22Q input/expected strings; never edit its oracle.
  (dolist (spec (cq-specs))
    (destructuring-bind (id source expected rule) spec
      (cr-probe id (bytes source) expected (concatenate 'string "unchanged Slice 22Q: " rule))))
  (dolist (encoding '(:utf-16le :utf-16be))
    (destructuring-bind (id source expected rule) (find "unicode" (cq-specs) :key #'first :test #'equal)
      (cr-probe (format nil "~A/~A" id encoding)
        (bytes (concatenate 'string "<?xml version='1.0' encoding='UTF-16'?>" source) encoding t) expected
        (concatenate 'string "unchanged Slice 22Q: " rule))))
  (dolist (spec (cr-extra-specs))
    (destructuring-bind (id source expected rule) spec (cr-probe id (bytes source) expected rule)))
  (dolist (spec '(("UTF8-BOM" :utf-8 t "UTF-8") ("UTF16LE-no-BOM" :utf-16le nil "UTF-16LE")
                  ("UTF16BE-no-BOM" :utf-16be nil "UTF-16BE") ("ISO8859-1" :iso-8859-1 nil "ISO-8859-1")))
    (destructuring-bind (id encoding bom declaration) spec
      (let ((text (if (eq encoding :iso-8859-1) "<x>Grüße ©</x>" "<x>Grüße 水 🦊</x>")))
        (cr-probe (concatenate 'string "encoding/" id)
          (bytes (concatenate 'string (format nil "<?xml version='1.0' encoding='~A'?>" declaration) (cq-wrap text)) encoding bom)
          text "Qualified source encoding; mandatory UTF8 output, no BOM"))))
  (dolist (spec (cr-official-vectors))
    (destructuring-bind (id raw expected source) spec
      (cr-probe id raw expected source :root-vector t)
      ;; Also exercise the PUBLIC adapter with the independently published
      ;; expectation. Adaptation: insert only the omitted resourceData wrapper;
      ;; keep the XML declaration and omit outside-root prolog whitespace.
      ;; All three original inputs contain ASCII only, including the ISO-8859-1
      ;; vector's numeric character reference, so this transport is lossless.
      (let* ((text (babel:octets-to-string raw :encoding :utf-8))
             (end (search "?>" text))
             (declaration (if end (subseq text 0 (+ end 2)) ""))
             (content (if end (string-left-trim '(#\Space #\Tab #\Newline #\Return) (subseq text (+ end 2))) text)))
        (cr-probe (concatenate 'string id "/XTM-wrapper")
          (bytes (concatenate 'string declaration (cq-wrap content))) expected
          (concatenate 'string source "; adaptation: wrapper inserted, outside-root whitespace omitted; expectation unchanged")))))
  (let ((ctx (topic-maps.xml:parse-canonical-context
               (bytes "<x xmlns:t='http://www.topicmaps.org/xtm/' xmlns:p='urn:p'><t:resourceData><p:a/></t:resourceData><resourceData>ignore</resourceData><t:resourceData>B</t:resourceData></x>"))))
    (check "resource-c14n-api:expanded-name-and-document-order"
      (and (= 2 (topic-maps.xml:resource-data-count ctx))
           (equal "<p:a xmlns:p=\"urn:p\"></p:a>" (topic-maps.xml:canonicalize-resource-data ctx :index 0))
           (equal "B" (topic-maps.xml:canonicalize-resource-data ctx :index 1)))))
  (cr-security-tests)
  (setf *cr-results* (nreverse *cr-results*) *cr-native* (nreverse *cr-native*) *cr-controls* (nreverse *cr-controls*) *cr-executed* t)
  t)
(defun cr-feature-report ()
  (mm-fields "kind" "XTM-4.16.3-closed-XML-C14N-1.0-infrastructure"
    "executed" (if *cr-executed* :true :false) "qualifiedForClosedXTMNodeSet" (if *cr-executed* :true :false)
    "generalXPathC14N" :false "XTMReaderIntegration" :false "corpusRegistrationsAdded" 0
    "probes" (coerce *cr-results* 'vector) "nativeValues" (coerce *cr-native* 'vector)
    "controls" (coerce *cr-controls* 'vector)))
