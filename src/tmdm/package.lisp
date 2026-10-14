(defpackage #:topic-maps.tmdm
  (:use #:cl)
  (:export #:topic-map #:make-topic-map #:topic-map-topics
           #:topic #:topic-parent #:topic-item-identifiers
           #:topic-subject-identifiers #:topic-subject-locators #:topic-names
           #:topic-name #:topic-name-value #:topic-name-type #:topic-name-parent
           #:intern-topic #:add-default-name #:default-name-type-identifier))
