(in-package #:topic-maps.ctm.tests)

(defun association-model-observation (map)
  "Actual references exposed as local ordinals, not canonical numbering."
  (let ((topics (topic-map-topics map)) (associations (topic-maps.tmdm:topic-map-associations map)))
    (flet ((topic-id (topic) (1+ (position topic topics :test #'eq)))
           (association-id (association) (1+ (position association associations :test #'eq))))
      (topic-maps.test-foundation::fields
       "topicCount" (length topics) "associationCount" (length associations)
       "roleCount" (reduce #'+ associations :key (lambda (a) (length (topic-maps.tmdm:association-roles a))) :initial-value 0)
       "topics" (topic-maps.test-foundation::json-array
        (loop for topic in topics collect
          (topic-maps.test-foundation::fields
           "ordinal" (topic-id topic) "parentIsMap" (if (eq map (topic-parent topic)) :true :false)
           "itemIdentifiers" (topic-maps.test-foundation::json-array (topic-item-identifiers topic))
           "subjectIdentifiers" (topic-maps.test-foundation::json-array (topic-subject-identifiers topic))
           "subjectLocators" (topic-maps.test-foundation::json-array (topic-subject-locators topic))
           "nameCount" (length (topic-names topic))
           "rolesPlayed" (topic-maps.test-foundation::json-array
            (loop for role in (topic-maps.tmdm:topic-roles-played topic)
                  for association = (topic-maps.tmdm:association-role-parent role) collect
              (topic-maps.test-foundation::fields
               "associationOrdinal" (association-id association)
               "roleOrdinal" (1+ (position role (topic-maps.tmdm:association-roles association) :test #'eq))))))))
       "associations" (topic-maps.test-foundation::json-array
        (loop for association in associations collect
          (topic-maps.test-foundation::fields
           "ordinal" (association-id association)
           "parentIsMap" (if (eq map (topic-maps.tmdm:association-parent association)) :true :false)
           "typeTopicOrdinal" (topic-id (topic-maps.tmdm:association-type association))
           "roles" (topic-maps.test-foundation::json-array
            (loop for role in (topic-maps.tmdm:association-roles association) for i from 1 collect
              (topic-maps.test-foundation::fields
               "ordinal" i "parentAssociationOrdinal" (association-id (topic-maps.tmdm:association-role-parent role))
               "typeTopicOrdinal" (topic-id (topic-maps.tmdm:association-role-type role))
               "playerTopicOrdinal" (topic-id (topic-maps.tmdm:association-role-player role))))))))))))

(defun write-association-report (pathname)
  (let ((*checks* nil))
    (let ((observations (exercise-association-corpus)))
      (with-open-file (out pathname :direction :output :if-exists :supersede :if-does-not-exist :create)
        (topic-maps.test-foundation::emit-json-value
         (topic-maps.test-foundation::fields
          "kind" "semantic-observations-not-cxtm"
          "qualification" "Pinned CTM corpus targets draft 2010-03-31; these properties do not prove CXTM equality or full ISO conformity."
          "passed" (length *last-association-checks*) "failed" 0
          "checks" (topic-maps.test-foundation::json-array *last-association-checks*)
          "cases" (topic-maps.test-foundation::json-array
           (loop for observation in observations collect
             (topic-maps.test-foundation::fields
              "id" (getf observation :id) "documentIRI" (getf observation :document-iri)
              "ctmSource" (uiop:read-file-string (asdf:system-relative-pathname "topic-maps"
                            (concatenate 'string "vendor/cxtm/" (getf observation :id))) :external-format :utf-8)
              "actualObjects" (association-model-observation (getf observation :topic-map)))))) out)
        (terpri out)))))
