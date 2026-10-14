(require :asdf)
;; No Quicklisp/user registry, no HyperDoc systems, no persistent Lisp image.
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:initialize-output-translations
 '(:output-translations (t (:root "tmp" "topic-maps-fasls")) :ignore-inherited-configuration))
(let* ((root (uiop:pathname-parent-directory-pathname
              (uiop:pathname-directory-pathname *load-truename*)))
       (report (uiop:getenv "TOPIC_MAPS_REPORT")))
  (asdf:load-asd (merge-pathnames "topic-maps.asd" root))
  (asdf:test-system "topic-maps/tests")
  (asdf:test-system "topic-maps/ctm/tests")
  (asdf:test-system "topic-maps/ctm/merging-tests")
  (when report
    (uiop:symbol-call :topic-maps.ctm.tests :write-slice-report
                     report (concatenate 'string report ".semantics.json"))
    (uiop:symbol-call :topic-maps.ctm.tests :write-merging-report
                     (concatenate 'string report ".merging.json"))))
