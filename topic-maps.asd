;;;; The foundation remains independent; reader/model are opt-in secondary systems.
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
  :description "Topics, Names, Occurrences, Associations and Roles with same-map merging"
  :version "0.12.0" :license "MIT" :serial t
  :components ((:file "src/tmdm/package") (:file "src/tmdm/integers") (:file "src/tmdm/decimals") (:file "src/tmdm/dates") (:file "src/tmdm/datetimes") (:file "src/tmdm/items")
               (:file "src/tmdm/merging") (:file "src/tmdm/occurrences") (:file "src/tmdm/associations")))

(asdf:defsystem "topic-maps/ctm"
  :description "CTM identity/names/associations and integer/decimal/date/dateTime/string/IRI occurrences"
  :version "0.12.0" :license "MIT" :depends-on ("topic-maps/tmdm") :serial t
  :components ((:file "src/ctm/package") (:file "src/ctm/conditions")
               (:file "src/ctm/unicode") (:file "src/ctm/iri")
               (:file "src/ctm/lexer") (:file "src/ctm/reader")))

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
  :version "0.11.0" :license "MIT" :depends-on ("topic-maps/tmdm") :serial t
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
