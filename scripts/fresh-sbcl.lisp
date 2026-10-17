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
  (asdf:test-system "topic-maps/ctm/association-tests")
  ;; Scope tests run all retained Date/numeric/identity-dependent suites once.
  (asdf:test-system "topic-maps/ctm/scope-tests")
  (when report
    (uiop:symbol-call :topic-maps.ctm.tests :write-slice-report
                     report (concatenate 'string report ".semantics.json"))
    (uiop:symbol-call :topic-maps.ctm.tests :write-merging-report
                     (concatenate 'string report ".merging.json"))
    (uiop:symbol-call :topic-maps.ctm.tests :write-association-report
                     (concatenate 'string report ".associations.json"))
    (uiop:symbol-call :topic-maps.ctm.tests :write-cxtm-report
                     report (concatenate 'string report ".cxtm.json")
                     :additional-checks (append (uiop:symbol-call :topic-maps.ctm.tests :occurrence-checks)
                                                (uiop:symbol-call :topic-maps.ctm.tests :prefix-checks)
                                                (uiop:symbol-call :topic-maps.ctm.tests :integer-checks)
                                                (uiop:symbol-call :topic-maps.ctm.tests :decimal-checks)
                                                (uiop:symbol-call :topic-maps.ctm.tests :date-checks)
                                                (uiop:symbol-call :topic-maps.ctm.tests :datetime-checks)
                                                (uiop:symbol-call :topic-maps.ctm.tests :timezone-checks)
                                                (uiop:symbol-call :topic-maps.ctm.tests :typed-name-checks)
                                                (uiop:symbol-call :topic-maps.ctm.tests :scope-checks))
                     :scope "Slice 13: same-map Scope for Names, Occurrences and Associations; 59 exact positive CXTM baselines, 8 specific rejections, 2 retained normative baseline FAILs; embedded Topics, reification and Variants unsupported")
    (uiop:symbol-call :topic-maps.ctm.tests :write-occurrence-report
                     (concatenate 'string report ".occurrences.json"))
    (uiop:symbol-call :topic-maps.ctm.tests :write-prefix-report
                     (concatenate 'string report ".prefixes.json"))
    (uiop:symbol-call :topic-maps.ctm.tests :write-integer-report
                     (concatenate 'string report ".integers.json"))
    (uiop:symbol-call :topic-maps.ctm.tests :write-decimal-report
                     (concatenate 'string report ".decimals.json"))
    (uiop:symbol-call :topic-maps.ctm.tests :write-date-report
                     (concatenate 'string report ".dates.json"))
    (uiop:symbol-call :topic-maps.ctm.tests :write-datetime-report
                     (concatenate 'string report ".datetimes.json"))
    (uiop:symbol-call :topic-maps.ctm.tests :write-timezone-report
                     (concatenate 'string report ".timezones.json"))
    (uiop:symbol-call :topic-maps.ctm.tests :write-typed-name-report
                     (concatenate 'string report ".typed-names.json"))
    (uiop:symbol-call :topic-maps.ctm.tests :write-scope-report
                     (concatenate 'string report ".scopes.json"))))
