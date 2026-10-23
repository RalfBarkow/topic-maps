(require :asdf)
(setf *compile-verbose* nil *load-verbose* nil)
(assert (string= "2.5.4" (lisp-implementation-version)))
(asdf:load-asd #P"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/xtm/tests")
(unless (fboundp 'topic-maps.xtm.tests::arr-native-tests)
  (load #P"/Users/rgb/workspace/topic-maps/tests/xtm-association-reifier-native.lisp"))
(in-package #:topic-maps.xtm.tests)
(setf *checks* nil)
(arr-native-tests)
(let ((path (uiop:getenv "TOPIC_MAPS_22M_NATIVE_REPORT")))
  (when path
    (with-open-file (out path :direction :output :if-exists :supersede :external-format :utf-8)
      (topic-maps.test-foundation::emit-json-value
        (mm-fields "runtime" (lisp-implementation-version) "kind" "native-Association-Reification-gate-before-Reader-change"
          "checks" (coerce (reverse *checks*) 'vector) "observations" (coerce *association-reifier-native* 'vector)
          "ReaderInvoked" :false "originalRegistrationsAdded" 0) out)
      (terpri out))))
(format t "ASSOCIATION-REIFIER-NATIVE-PREFLIGHT-PASS: ~D native checks; no Reader calls; no corpus registration~%" (length *checks*))
