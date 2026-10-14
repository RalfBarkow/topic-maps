(in-package #:topic-maps.ctm.tests)

(defun model-observation (map)
  "Plain observation data, not CXTM serialization or canonical ordering."
  (let ((topics (topic-map-topics map)))
    (topic-maps.test-foundation::fields
     "topicCount" (length topics)
     "nameCount" (reduce #'+ topics :key (lambda (topic) (length (topic-names topic))) :initial-value 0)
     "topics"
     (topic-maps.test-foundation::json-array
      (loop for topic in topics for index from 1 collect
        (topic-maps.test-foundation::fields
         "ordinal" index "parentIsMap" (if (eq map (topic-parent topic)) :true :false)
         "itemIdentifiers" (topic-maps.test-foundation::json-array (topic-item-identifiers topic))
         "subjectIdentifiers" (topic-maps.test-foundation::json-array (topic-subject-identifiers topic))
         "subjectLocators" (topic-maps.test-foundation::json-array (topic-subject-locators topic))
         "names"
         (topic-maps.test-foundation::json-array
          (loop for name in (topic-names topic) collect
            (topic-maps.test-foundation::fields
             "value" (topic-name-value name)
             "typeTopicOrdinal" (1+ (position (topic-name-type name) topics :test #'eq))
             "parentTopicOrdinal" (1+ (position (topic-name-parent name) topics :test #'eq)))))))))))

(defun write-slice-report (pathname semantic-pathname)
  (let ((*checks* nil))
    (multiple-value-bind (corpus observations) (exercise-corpus)
      (setf *observations* observations)
      (topic-maps.test-foundation:write-validation-report
       corpus pathname
       :infrastructure-checks topic-maps.tests::*last-checks*
       :implementation '(:ctm t :tmdm t :scope "Slice 1: identity declarations and untyped names; no CXTM canonicalizer"))
      (with-open-file (out semantic-pathname :direction :output :if-exists :supersede :if-does-not-exist :create)
        (topic-maps.test-foundation::emit-json-value
         (topic-maps.test-foundation::fields
          "schemaVersion" 1 "kind" "semantic-observations-not-cxtm"
          "qualification" (getf (topic-maps.test-foundation:corpus-metadata corpus) :qualification)
          "passed" (length *last-checks*) "failed" 0
          "checks" (topic-maps.test-foundation::json-array *last-checks*)
          "cases"
          (topic-maps.test-foundation::json-array
           (loop for observation in observations collect
             (let* ((id (getf observation :id))
                    (case (first (topic-maps.test-foundation:select-cases corpus :id id))))
               (topic-maps.test-foundation::fields
                "id" id "status" "pass" "ctmSource"
                (uiop:read-file-string (topic-maps.test-foundation:test-case-source-pathname case) :external-format :utf-8)
                "documentIRI" (getf observation :document-iri)
                "ctmClauses" (topic-maps.test-foundation::json-array (topic-maps.test-foundation:test-case-clauses case))
                "tmdmClauses" (topic-maps.test-foundation::json-array
                               (append '("TMDM 5.1" "TMDM 5.2" "TMDM 5.3.5")
                                       (when (string= id "ctm/in/name.ctm") '("TMDM 5.4"))))
                "actualObjects" (model-observation (getf observation :topic-map))))))) out)
        (terpri out)))))
