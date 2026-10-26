(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/project-work-example")
(use-package '(:topic-maps.tmdm :topic-maps.project-work.example))

(defparameter *example-source* #p"/Users/rgb/workspace/topic-maps/examples/project-work.ctm")
(defparameter *example-map* (load-map *example-source*))
(defparameter *held-question*
  (find-topic *example-map* "urn:topic-maps:question:Q-XTM-LOOP"))
(describe *held-question*)
(show-topic *held-question*)
;; Native Associations and their actual Role Items are navigable:
(dolist (association (relations *held-question*))
  (describe association)
  (dolist (role (association-roles association)) (describe role)))

(defparameter *before-edit*
  (topic-maps.cxtm:canonicalize-octets *example-map* :base-locator *document-iri*))
(defparameter *exercise-occurrence* (add-exercise-note *example-map*))
(assert (eq *held-question*
  (find-topic *example-map* "urn:topic-maps:question:Q-XTM-LOOP")))
(show-topic *held-question*)
(defparameter *after-edit*
  (topic-maps.cxtm:canonicalize-octets *example-map* :base-locator *document-iri*))
(list (length *before-edit*) (length *after-edit*) (mismatch *before-edit* *after-edit*))
;; => (7914 8191 5141); mismatch uses a zero-based byte position.

(defparameter *same-note-again* (add-exercise-note *example-map*))
(assert (eq (canonical-occurrence *exercise-occurrence*) *same-note-again*))
(assert (equalp *after-edit*
  (topic-maps.cxtm:canonicalize-octets *example-map* :base-locator *document-iri*)))
;; The original CTM is untouched; a fresh read contains no exercise annotation:
(defparameter *fresh-original* (load-map *example-source* :source-key "re-read original"))
(assert (equalp *before-edit*
  (topic-maps.cxtm:canonicalize-octets *fresh-original* :base-locator *document-iri*)))
