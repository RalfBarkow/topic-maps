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
  ;; Import tests run all retained CTM/TMDM/CXTM suites once.
  (asdf:test-system "topic-maps/ctm/include-tests")
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
                                                (uiop:symbol-call :topic-maps.identifier.tests :identifier-checks)
                                                (uiop:symbol-call :topic-maps.reification.tests :reification-checks)
                                                (uiop:symbol-call :topic-maps.arity.tests :arity-checks)
                                                (uiop:symbol-call :topic-maps.relationship.tests :relationship-checks)
                                                (uiop:symbol-call :topic-maps.template.tests :template-checks)
                                                (uiop:symbol-call :topic-maps.import.tests :import-checks)
                                                (uiop:symbol-call :topic-maps.mergemap.tests :mergemap-checks)
                                                (uiop:symbol-call :topic-maps.include.tests :include-checks))
                     :scope "Slice 19C: controlled CTM Include and Mergemap; 176 byte-equal positives, 28 specific rejections, 2 retained DateTime and 2 explicit Include baseline FAILs. XTM Mergemap remains NOT-RUN")
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
                     (concatenate 'string report ".identifiers.json"))
    (uiop:symbol-call :topic-maps.reification.tests :write-reification-report
                     (concatenate 'string report ".reification.json"))
    (uiop:symbol-call :topic-maps.arity.tests :write-arity-report
                     (concatenate 'string report ".arity.json"))
    (uiop:symbol-call :topic-maps.relationship.tests :write-relationship-report
                     (concatenate 'string report ".relationships.json"))
    (uiop:symbol-call :topic-maps.template.tests :write-template-report
                     (concatenate 'string report ".templates.json"))
    (uiop:symbol-call :topic-maps.import.tests :write-import-report
                     (concatenate 'string report ".map-import.json"))
    (uiop:symbol-call :topic-maps.mergemap.tests :write-mergemap-report
                     (concatenate 'string report ".mergemap.json"))
    (uiop:symbol-call :topic-maps.include.tests :write-include-report
                     (concatenate 'string report ".include.json"))))

;; Explicit opt-in integration after the unchanged core suites and reports.
;; Restore only the caller's qualified source registry, then load the adapter.
(let ((prefix (uiop:getenv "TOPIC_MAPS_XTM_MERGEMAP_REPORT")))
  (when prefix
    (let ((calls 0))
      (handler-case
          (progn
            (uiop:symbol-call :topic-maps.ctm :deserialize-string
              "%mergemap <urn:unfetched> <http://psi.topicmaps.org/iso13250/xtm>"
              :document-iri "urn:adapter-boundary"
              :resource-resolver (lambda (&rest args) (declare (ignore args)) (incf calls)))
            (error "Core CTM unexpectedly accepted XTM without its explicit adapter."))
        (topic-maps.ctm:ctm-unsupported (condition)
          (assert (and (zerop calls) (eq :xtm-mergemap-reader-required (topic-maps.ctm:error-code condition)))))))
    (format t "XTM-ADAPTER-BOUNDARY-PASS: explicit adapter required before resource retrieval~%")
    (asdf:initialize-source-registry
      (let ((*read-eval* nil))
        (read-from-string
          (or (uiop:getenv "CL_SOURCE_REGISTRY")
              (error "XTM integration requires the prepared qualified source registry.")))))
    (asdf:test-system "topic-maps/ctm/xtm-tests")
    (uiop:symbol-call :topic-maps.xtm-mergemap.tests :write-reports prefix)))


;; Slice 20A registration always runs after the retained suites and the optional
;; XTM adapter. Historical reports above remain snapshots of their own stages.
(asdf:test-system "topic-maps/ctm/registered-original-tests")
(let ((prefix (uiop:getenv "TOPIC_MAPS_REGISTERED_ORIGINALS_REPORT")))
  (when prefix
    (uiop:symbol-call :topic-maps.registered-original.tests :write-reports prefix)))
