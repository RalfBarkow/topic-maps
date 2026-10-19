;; Fault-injection controls exercise the same ASDF executor. They do not add
;; corpus results. Only the first new negative original's call is intercepted;
;; all 26 positive originals must still execute successfully beforehand.
(require :asdf)
(assert (string= "2.5.4" (lisp-implementation-version)))
(setf *compile-verbose* nil *load-verbose* nil)
(asdf:load-asd (merge-pathnames "../../topic-maps.asd" *load-truename*))
(asdf:load-system "topic-maps/xtm/tests")
(let* ((mode (uiop:getenv "TOPIC_MAPS_21C_FAULT"))
       (original (symbol-function 'topic-maps.xtm:deserialize-octets))
       (text (cond ((string= mode "accepted") (topic-maps.xtm.tests::document "<topic id='valid'/>"))
                   ((string= mode "xml") "<a><b></a>")
                   ((string= mode "unsupported") (topic-maps.xtm.tests::document "<topic id='a'><name><value>N</value></name></topic>"))
                   ((string= mode "wrong-cause") (topic-maps.xtm.tests::document "<topic/>"))
                   (t (error "Unknown fault mode ~A" mode)))))
  (setf (symbol-function 'topic-maps.xtm:deserialize-octets)
    (lambda (raw &rest args)
      (apply original
        (if (equal "xtm2/invalid/id-invalid.xtm" (getf args :source-key))
            (topic-maps.xtm.tests::bytes text) raw) args)))
  (asdf:test-system "topic-maps/xtm"))
(error "Negative fault control unexpectedly completed without ASDF failure.")
