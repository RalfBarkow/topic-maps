(defpackage #:topic-maps.tmdm
  (:use #:cl)
  (:export #:topic-map #:make-topic-map #:topic-map-topics #:topic-map-associations
           #:item-reifier #:set-item-reifier #:topic-reified
           #:reification-error #:reification-error-code
           #:item-identifiers #:add-item-identifier #:item-identifier-error #:item-identifier-error-code
           #:topic-map-item-identifiers #:topic-name-item-identifiers
           #:association-item-identifiers #:association-role-item-identifiers
           #:topic #:topic-parent #:topic-item-identifiers
           #:topic-subject-identifiers #:topic-subject-locators #:topic-names #:topic-occurrences #:topic-roles-played
           #:topic-name-scope #:occurrence-scope #:association-scope #:scope-error #:scope-error-code
           #:topic-name #:topic-name-value #:topic-name-type #:topic-name-parent #:topic-name-variants
           #:variant #:add-variant #:variant-parent #:variant-value #:variant-datatype
           #:variant-scope #:variant-item-identifiers #:canonical-variant #:variant-error #:variant-error-code
           #:intern-topic #:add-topic-identifier #:merge-topics #:normalize-topic-map
           #:canonical-topic #:canonical-topic-name
           #:association #:make-association #:association-parent #:association-type #:association-roles
           #:association-role #:association-role-parent #:association-role-type #:association-role-player
           #:canonical-association #:canonical-association-role
           #:occurrence #:occurrence-parent #:occurrence-type #:occurrence-value
           #:occurrence-datatype #:occurrence-item-identifiers #:canonical-occurrence
           #:add-occurrence #:string-datatype #:iri-datatype #:integer-datatype
           #:integer-lexical-p #:canonical-integer-lexical-form
           #:decimal-datatype #:decimal-lexical-p #:canonical-decimal-lexical-form
           #:date-datatype #:date-lexical-p #:canonical-date-lexical-form
           #:datetime-datatype #:datetime-lexical-p #:canonical-datetime-lexical-form
           #:occurrence-error #:occurrence-error-code
           #:add-name #:add-default-name #:default-name-type-identifier))
