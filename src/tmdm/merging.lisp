(in-package #:topic-maps.tmdm)

(defun identifiers (topic kind)
  (ecase kind
    (:item-identifier (%topic-item-identifiers topic))
    (:subject-identifier (%topic-subject-identifiers topic))
    (:subject-locator (%topic-subject-locators topic))))

(defun identifier-matches-p (topic kind iri)
  ;; One identity rule for lookup and merging: TMDM 5.3.5, excluding reification.
  (some (lambda (property) (member iri (identifiers topic property) :test #'string=))
        (ecase kind
          ((:item-identifier :subject-identifier) '(:item-identifier :subject-identifier))
          (:subject-locator '(:subject-locator)))))

(defun equal-topics-p (a b)
  (some (lambda (kind)
          (some (lambda (iri) (identifier-matches-p a kind iri)) (identifiers b kind)))
        '(:item-identifier :subject-identifier :subject-locator)))

(defun set-union (a b test)
  (remove-duplicates (append a b) :test test :from-end t))

(defun replace-pair (items a b replacement)
  ;; Set ordering is not normative; retain the first replaced position.
  (loop with inserted = nil for item in items
        append (if (or (eq item a) (eq item b))
                   (unless inserted (setf inserted t) (list replacement))
                   (list item))))

(defun equal-pair (items predicate)
  (loop for tail on items do
    (let ((other (find-if (lambda (item) (funcall predicate (first tail) item)) (rest tail))))
      (when other (return (list (first tail) other))))))

(defun normalize-names (map)
  ;; TMDM 5.4 and 6.3: all supported names have empty scope/variants/II,
  ;; null reifier. Parent and type may have changed during a Topic merge.
  (dolist (topic (%topic-map-topics map))
    (loop for pair = (equal-pair (%topic-names topic)
                       (lambda (a b)
                         (and (string= (%topic-name-value a) (%topic-name-value b))
                              (eq (%topic-name-type a) (%topic-name-type b)))))
          while pair do
            (let* ((a (first pair)) (b (second pair))
                   (c (%make-topic-name (%topic-name-value a) (%topic-name-type a) topic)))
              (setf (%topic-names topic) (replace-pair (%topic-names topic) a b c)
                    (%topic-name-forward a) c (%topic-name-forward b) c)))))

(defun merge-two-topics (map a b)
  ;; TMDM 6.2: create C, union supported properties, replace model references.
  ;; Scope/reifiers remain unimplemented; Association/Role refs are materialized.
  (let ((c (%make-topic map)))
    (setf (%topic-item-identifiers c) (set-union (%topic-item-identifiers a) (%topic-item-identifiers b) #'string=)
          (%topic-subject-identifiers c) (set-union (%topic-subject-identifiers a) (%topic-subject-identifiers b) #'string=)
          (%topic-subject-locators c) (set-union (%topic-subject-locators a) (%topic-subject-locators b) #'string=)
          (%topic-names c) (set-union (%topic-names a) (%topic-names b) #'eq)
          (%topic-occurrences c) (set-union (%topic-occurrences a) (%topic-occurrences b) #'eq)
          (%topic-map-topics map) (replace-pair (%topic-map-topics map) a b c)
          (%topic-forward a) c (%topic-forward b) c)
    (dolist (topic (%topic-map-topics map))
      (dolist (name (%topic-names topic))
        ;; Parent is the computed containing topic (TMDM 5.4).
        (setf (%topic-name-parent name) topic
              (%topic-name-type name) (canonical-topic (%topic-name-type name)))))
    (dolist (topic (%topic-map-topics map))
      (dolist (occurrence (%topic-occurrences topic))
        (setf (%occurrence-parent occurrence) topic
              (%occurrence-type occurrence) (canonical-topic (%occurrence-type occurrence)))))
    (dolist (association (%topic-map-associations map))
      (setf (%association-type association) (canonical-topic (%association-type association)))
      (dolist (role (%association-roles association))
        (setf (%association-role-type role) (canonical-topic (%association-role-type role))
              (%association-role-player role) (canonical-topic (%association-role-player role)))))
    (normalize-names map)
    (normalize-occurrences map)
    (normalize-associations map)
    c))

(defun normalize-topic-map (map)
  "Apply same-map identity merging, then remove equal Names, Occurrences, Roles and Associations.
Only implemented properties participate; no cross-map merging."
  (check-type map topic-map)
  (loop for pair = (equal-pair (%topic-map-topics map) #'equal-topics-p)
        while pair do (merge-two-topics map (first pair) (second pair)))
  (normalize-names map)
  (normalize-occurrences map)
  (normalize-associations map)
  map)

(defun live-topic (topic)
  (let ((current (canonical-topic topic)))
    (unless (member current (%topic-map-topics (%topic-parent current)) :test #'eq)
      (error "Topic is not a live member of its map."))
    current))

(defun merge-topics (a b)
  "Merge two Topics in the same map, returning their current representative.
Explicit merging may assert shared subject identity beyond locator equality.
Cross-map merging is rejected before mutation. Obsolete handles remain resolvable."
  (let* ((a (live-topic a)) (b (live-topic b)) (map (%topic-parent a)))
    (unless (eq map (%topic-parent b)) (error "Cross-map Topic merging is outside this API."))
    (unless (eq a b) (setf a (merge-two-topics map a b)))
    (normalize-topic-map map)
    (canonical-topic a)))

(defun add-topic-identifier (topic kind iri)
  "Add a locator to its distinct identity property and perform required merging.
KIND is :ITEM-IDENTIFIER, :SUBJECT-IDENTIFIER or :SUBJECT-LOCATOR.
IRI is an already resolved, nonempty absolute locator string; CTM validates it."
  (unless (and (stringp iri) (plusp (length iri))) (error "A nonempty locator string is required."))
  (let ((topic (live-topic topic)))
    (check-topic-occurrence-identifiers (%topic-parent topic) kind iri)
    (ecase kind
      (:item-identifier (pushnew iri (%topic-item-identifiers topic) :test #'string=))
      (:subject-identifier (pushnew iri (%topic-subject-identifiers topic) :test #'string=))
      (:subject-locator (pushnew iri (%topic-subject-locators topic) :test #'string=)))
    (normalize-topic-map (%topic-parent topic))
    (canonical-topic topic)))

(defun intern-topic (map kind iri)
  "Lookup/create a Topic using the same identity rule as same-map merging."
  (check-type map topic-map)
  (unless (and (stringp iri) (plusp (length iri))) (error "A nonempty locator string is required."))
  ;; Validate the category even for an empty map, before adding a Topic.
  (ecase kind ((:item-identifier :subject-identifier :subject-locator)))
  (check-topic-occurrence-identifiers map kind iri)
  (let ((topic (or (find-if (lambda (topic) (identifier-matches-p topic kind iri))
                           (%topic-map-topics map))
                   (let ((new (%make-topic map)))
                     (setf (%topic-map-topics map) (append (%topic-map-topics map) (list new)))
                     new))))
    (add-topic-identifier topic kind iri)))

(defun add-default-name (topic value)
  "CTM 3.11 default type; equal unscoped names share one information item."
  (check-type value string)
  (let* ((topic (live-topic topic))
         (type (intern-topic (%topic-parent topic) :subject-identifier (default-name-type-identifier)))
         (topic (canonical-topic topic))
         (existing (find-if (lambda (name)
                             (and (string= value (%topic-name-value name))
                                  (eq type (%topic-name-type name))))
                           (%topic-names topic))))
    (or existing
        (let ((name (%make-topic-name value type topic)))
          (setf (%topic-names topic) (append (%topic-names topic) (list name)))
          name))))
