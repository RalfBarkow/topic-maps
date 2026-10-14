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
  :description "Topic identity, same-map merging and unscoped Topic Name items"
  :version "0.2.0" :license "MIT" :serial t
  :components ((:file "src/tmdm/package") (:file "src/tmdm/items") (:file "src/tmdm/merging")))

(asdf:defsystem "topic-maps/ctm"
  :description "CTM identity declarations/tails and default names; no canonicalizer"
  :version "0.2.0" :license "MIT" :depends-on ("topic-maps/tmdm") :serial t
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
