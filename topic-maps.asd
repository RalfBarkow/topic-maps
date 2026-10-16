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
  :version "0.6.0" :license "MIT" :serial t
  :components ((:file "src/tmdm/package") (:file "src/tmdm/items")
               (:file "src/tmdm/merging") (:file "src/tmdm/occurrences") (:file "src/tmdm/associations")))

(asdf:defsystem "topic-maps/ctm"
  :description "CTM prefixes, identity, names, qualified string/IRI occurrences and associations"
  :version "0.6.0" :license "MIT" :depends-on ("topic-maps/tmdm") :serial t
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
  :version "0.6.0" :license "MIT" :depends-on ("topic-maps/tmdm") :serial t
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
