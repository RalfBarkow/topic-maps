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
  ;; Reference tests run all retained Date/numeric/identity-dependent suites once.
  (asdf:test-system "topic-maps/tmdm/identifier-tests")
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
                                                (uiop:symbol-call :topic-maps.ctm.tests :scope-checks)
                                                (uiop:symbol-call :topic-maps.variant.tests :variant-checks)
                                                (uiop:symbol-call :topic-maps.reference.tests :reference-checks)
                                                (uiop:symbol-call :topic-maps.identifier.tests :identifier-checks))
                     :scope "Slice 16A: general Item Identifiers on all seven information items; 83 original positive CTM/CXTM comparisons, 10 specific CTM rejections, 2 retained normative baseline FAILs. Manual XTM2-model comparisons are separate; no XTM reader or Reification implemented")
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
                     (concatenate 'string report ".scopes.json"))
    (uiop:symbol-call :topic-maps.variant.tests :write-variant-report
                     (concatenate 'string report ".variants.json"))
    (uiop:symbol-call :topic-maps.reference.tests :write-reference-report
                     (concatenate 'string report ".references.json"))
    (uiop:symbol-call :topic-maps.identifier.tests :write-identifier-report
                     (concatenate 'string report ".identifiers.json"))))
