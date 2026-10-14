(defpackage #:topic-maps.tmdm
  (:use #:cl)
  (:export #:topic-map #:make-topic-map #:topic-map-topics #:topic-map-associations
           #:topic #:topic-parent #:topic-item-identifiers
           #:topic-subject-identifiers #:topic-subject-locators #:topic-names #:topic-occurrences #:topic-roles-played
           #:topic-name #:topic-name-value #:topic-name-type #:topic-name-parent
           #:intern-topic #:add-topic-identifier #:merge-topics #:normalize-topic-map
           #:canonical-topic #:canonical-topic-name
           #:association #:make-association #:association-parent #:association-type #:association-roles
           #:association-role #:association-role-parent #:association-role-type #:association-role-player
           #:canonical-association #:canonical-association-role
           #:occurrence #:occurrence-parent #:occurrence-type #:occurrence-value
           #:occurrence-datatype #:occurrence-item-identifiers #:canonical-occurrence
           #:add-occurrence #:string-datatype #:iri-datatype
           #:occurrence-error #:occurrence-error-code
           #:add-default-name #:default-name-type-identifier))
