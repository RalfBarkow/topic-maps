;;;; The foundation remains independent; reader/model are opt-in secondary systems.
(asdf:defsystem "topic-maps/xml"
  :description "Pinned, patched CXML byte boundary with mandatory external-resource denial; no XTM"
  :version "0.0.1" :license "MIT" :depends-on ("cxml") :serial t
  :components ((:file "src/xml/package") (:file "src/xml/parser")))

(asdf:defsystem "topic-maps"
  :description "Independent CTM test foundation; no parsing or deserialization"
  :version "0.0.0"
  :license "MIT"
  :depends-on ("uiop")
  :serial t
  :components ((:file "src/package")
               (:file "src/filesystem")
               (:file "src/corpus")
               (:file "src/report"))
  :in-order-to ((asdf:test-op (asdf:test-op "topic-maps/tests"))))

(asdf:defsystem "topic-maps/tests"
  :description "Infrastructure tests only; imported CTM cases remain NOT-RUN"
  :depends-on ("topic-maps")
  :serial t
  :components ((:file "tests/package") (:file "tests/foundation"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.tests :run-tests)))

(asdf:defsystem "topic-maps/tmdm"
  :description "Topics, Names, Variants, Occurrences, Associations and Roles with same-map merging and source-preserving content import"
  :version "0.16.1" :license "MIT" :serial t
  :components ((:file "src/tmdm/package") (:file "src/tmdm/integers") (:file "src/tmdm/decimals") (:file "src/tmdm/dates") (:file "src/tmdm/datetimes") (:file "src/tmdm/items")
               (:file "src/tmdm/core-subjects") (:file "src/tmdm/item-identifiers") (:file "src/tmdm/reification") (:file "src/tmdm/merging") (:file "src/tmdm/occurrences") (:file "src/tmdm/variants") (:file "src/tmdm/associations") (:file "src/tmdm/import")))

(asdf:defsystem "topic-maps/ctm"
  :description "CTM recursive Topic references, Wildcards, names/variants/associations and supported literals"
  :version "0.16.1" :license "MIT" :depends-on ("topic-maps/tmdm") :serial t
  :components ((:file "src/ctm/package") (:file "src/ctm/conditions")
               (:file "src/ctm/unicode") (:file "src/ctm/iri")
               (:file "src/ctm/lexer") (:file "src/ctm/reader") (:file "src/ctm/templates") (:file "src/ctm/resources")))

(asdf:defsystem "topic-maps/ctm/tests"
  :description "Slice 1 semantic tests and explicit imported rejection contract"
  :depends-on ("topic-maps/ctm" "topic-maps/tests") :serial t
  :components ((:file "tests/ctm-package") (:file "tests/ctm-identity")
               (:file "tests/ctm-report"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-tests)))

(asdf:defsystem "topic-maps/ctm/merging-tests"
  :description "Same-map Topic merging and separate pinned baseline property evidence"
  :depends-on ("topic-maps/ctm/tests") :serial t
  :components ((:file "tests/ctm-merging") (:file "tests/merge-graphs"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-merging-tests)))

(asdf:defsystem "topic-maps/ctm/association-tests"
  :description "Association/Role semantics, merge references and separate baseline evidence"
  :depends-on ("topic-maps/ctm/merging-tests") :serial t
  :components ((:file "tests/ctm-associations") (:file "tests/association-graphs")
               (:file "tests/association-report"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-association-tests)))

(asdf:defsystem "topic-maps/cxtm"
  :description "Pure CXTM for the supported TMDM subset; ISO/IEC 13250-4:2009"
  :version "0.16.1" :license "MIT" :depends-on ("topic-maps/tmdm") :serial t
  :components ((:file "src/cxtm/package") (:file "src/cxtm/nfc-data")
               (:file "src/cxtm/unicode") (:file "src/cxtm/canonicalizer")))

(asdf:defsystem "topic-maps/cxtm/tests"
  :description "Real pinned CXTM comparisons and canonicalization regression tests"
  :depends-on ("topic-maps/cxtm" "topic-maps/ctm/association-tests") :serial t
  :components ((:file "tests/cxtm"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-cxtm-tests)))


(asdf:defsystem "topic-maps/ctm/occurrence-tests"
  :description "Occurrence semantics, canonical merge handles and four original CXTM contracts"
  :depends-on ("topic-maps/cxtm/tests") :serial t
  :components ((:file "tests/ctm-occurrences"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-occurrence-tests)))

(asdf:defsystem "topic-maps/ctm/prefix-tests"
  :description "Prefix bindings, explicit string datatypes and seven original contracts"
  :depends-on ("topic-maps/ctm/occurrence-tests") :serial t
  :components ((:file "tests/ctm-prefixes"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-prefix-tests)))

(asdf:defsystem "topic-maps/ctm/integer-tests"
  :description "Integer lexical values, TMDM equality, pure CXTM and six original contracts"
  :depends-on ("topic-maps/ctm/prefix-tests") :serial t
  :components ((:file "tests/ctm-integers"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-integer-tests)))

(asdf:defsystem "topic-maps/ctm/decimal-tests"
  :description "Decimal lexical values, TMDM equality, pure CXTM and seven original contracts"
  :depends-on ("topic-maps/ctm/integer-tests") :serial t
  :components ((:file "tests/ctm-decimals"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-decimal-tests)))

(asdf:defsystem "topic-maps/ctm/date-tests"
  :description "XSD 1.0 Date validation, lexical equality, pure CXTM and ten original contracts"
  :depends-on ("topic-maps/ctm/decimal-tests") :serial t
  :components ((:file "tests/ctm-dates"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-date-tests)))

(asdf:defsystem "topic-maps/ctm/datetime-tests"
  :description "DateTime lexical semantics and explicit normative baseline discrepancies"
  :depends-on ("topic-maps/ctm/date-tests") :serial t
  :components ((:file "tests/ctm-datetimes"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-datetime-tests)))

(asdf:defsystem "topic-maps/ctm/timezone-tests"
  :description "DateTime UTC offsets, pure CXTM and documented baseline mismatches"
  :depends-on ("topic-maps/ctm/datetime-tests") :serial t
  :components ((:file "tests/ctm-datetime-timezones"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-timezone-tests)))

(asdf:defsystem "topic-maps/ctm/typed-name-tests"
  :description "Explicit Name types, canonical merge handles and four original CXTM contracts"
  :depends-on ("topic-maps/ctm/timezone-tests") :serial t
  :components ((:file "tests/ctm-typed-names"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-typed-name-tests)))

(asdf:defsystem "topic-maps/ctm/scope-tests"
  :description "Topic-set Scope, merge handles, CTM diagnostics and three original CXTM contracts"
  :depends-on ("topic-maps/ctm/typed-name-tests") :serial t
  :components ((:file "tests/ctm-scopes"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.ctm.tests :run-scope-tests)))

(asdf:defsystem "topic-maps/ctm/variant-tests"
  :description "Variants, proper scope supersets, canonical handles and four original contracts"
  :depends-on ("topic-maps/ctm/scope-tests") :serial t
  :components ((:file "tests/ctm-variants"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.variant.tests :run-tests)))

(asdf:defsystem "topic-maps/ctm/reference-tests"
  :description "Wildcard environment, recursive Embedded Topics and canonical Topic references"
  :depends-on ("topic-maps/ctm/variant-tests") :serial t
  :components ((:file "tests/ctm-references"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.reference.tests :run-tests)))

(asdf:defsystem "topic-maps/tmdm/identifier-tests"
  :description "General Item Identifiers, global uniqueness, merges and manual XTM2 baseline comparisons"
  :depends-on ("topic-maps/ctm/reference-tests") :serial t
  :components ((:file "tests/item-identifiers"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.identifier.tests :run-tests)))

(asdf:defsystem "topic-maps/tmdm/reification-tests"
  :description "Same-map Reification, canonical references, atomic cascades and original CTM contracts"
  :depends-on ("topic-maps/tmdm/identifier-tests") :serial t
  :components ((:file "tests/reification"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.reification.tests :run-tests)))

(asdf:defsystem "topic-maps/ctm/association-arity-tests"
  :description "Unbounded CTM Role declarations, canonical merges and original CXTM contract"
  :depends-on ("topic-maps/tmdm/reification-tests") :serial t
  :components ((:file "tests/ctm-association-arity"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.arity.tests :run-tests)))

(asdf:defsystem "topic-maps/ctm/type-relationship-tests"
  :description "CTM isa/ako, Core Subject consistency and atomic identity cascades"
  :depends-on ("topic-maps/ctm/association-arity-tests") :serial t
  :components ((:file "tests/ctm-type-relationships"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.relationship.tests :run-tests)))

(asdf:defsystem "topic-maps/ctm/template-tests"
  :description "CTM Templates, contextual argument binding and original conformance contracts"
  :depends-on ("topic-maps/ctm/type-relationship-tests") :serial t
  :components ((:file "tests/ctm-templates"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.template.tests :run-tests)))

(asdf:defsystem "topic-maps/tmdm/import-tests"
  :description "Source-preserving Map content import, identity cascades and atomic conflicts"
  :depends-on ("topic-maps/ctm/template-tests") :serial t
  :components ((:file "tests/map-import"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.import.tests :run-tests)))

(asdf:defsystem "topic-maps/ctm/mergemap-tests"
  :description "Explicit resource resolver, CTM Mergemap isolation and original contracts"
  :depends-on ("topic-maps/tmdm/import-tests") :serial t
  :components ((:file "tests/ctm-mergemap"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.mergemap.tests :run-tests)))

(asdf:defsystem "topic-maps/ctm/include-tests"
  :description "CTM Include, source-preserving Template transport and explicit original baseline discrepancies"
  :depends-on ("topic-maps/ctm/mergemap-tests") :serial t
  :components ((:file "tests/ctm-include"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.include.tests :run-tests)))

(asdf:defsystem "topic-maps/xtm"
  :description "XTM 2.0 identity/instanceOf subset using the qualified XML byte boundary"
  :version "0.19.1" :license "MIT" :depends-on ("topic-maps/tmdm" "topic-maps/xml") :serial t
  :components ((:file "src/xtm/package") (:file "src/xtm/iri") (:file "src/xtm/reader"))
  :in-order-to ((asdf:test-op (asdf:test-op "topic-maps/xtm/tests"))))

(asdf:defsystem "topic-maps/xtm/tests"
  :description "Separate XTM identity model checks and six original CXTM contracts"
  :depends-on ("topic-maps/xtm" "topic-maps/cxtm" "topic-maps") :serial t
  :components ((:file "tests/xtm-identity"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.xtm.tests :run-tests)))

(asdf:defsystem "topic-maps/ctm/xtm"
  :description "Explicit XTM 2.0 notation adapter for controlled CTM Mergemap"
  :version "0.19.2" :license "MIT" :depends-on ("topic-maps/ctm" "topic-maps/xtm")
  :components ((:file "src/ctm/xtm")))

(asdf:defsystem "topic-maps/ctm/xtm-tests"
  :description "Actual XTM Mergemap imports, raw bytes, diagnostics and original baseline"
  :depends-on ("topic-maps/ctm/xtm" "topic-maps/ctm/include-tests")
  :components ((:file "tests/ctm-xtm-mergemap"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.xtm-mergemap.tests :run-tests)))

(asdf:defsystem "topic-maps/ctm/registered-original-tests"
  :description "Slice 20A: register forty original contracts using the existing CTM/CXTM harness"
  :depends-on ("topic-maps/ctm/include-tests")
  :components ((:file "tests/ctm-registered-originals"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.registered-original.tests :run-tests)))


(asdf:defsystem "topic-maps/ctm/registered-negative-tests"
  :description "Slice 20B: intended syntax rejections of seven unchanged negative originals"
  :depends-on ("topic-maps/ctm/registered-original-tests")
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.registered-original.tests :run-negative-tests)))

(asdf:defsystem "topic-maps/ctm/prolog-tests"
  :description "Slice 20C: UTF-8 encoding selection, version prolog and three intended original rejections"
  :depends-on ("topic-maps/ctm/registered-negative-tests")
  :components ((:file "tests/ctm-prolog"))
  :perform (asdf:test-op (operation component)
             (declare (ignore operation component))
             (uiop:symbol-call :topic-maps.prolog.tests :run-tests)))
