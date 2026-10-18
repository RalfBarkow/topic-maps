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
  (or (some (lambda (kind)
              (some (lambda (iri) (identifier-matches-p a kind iri)) (identifiers b kind)))
            '(:item-identifier :subject-identifier :subject-locator))
      (let ((target (topic-reified a))) (and target (eq target (topic-reified b))))))

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

(define-condition scope-error (error)
  ((code :initarg :code :reader scope-error-code)
   (detail :initarg :detail :reader scope-error-detail))
  (:report (lambda (c stream) (format stream "Scope ~A: ~A" (scope-error-code c) (scope-error-detail c)))))
(defun scope-problem (code detail) (error 'scope-error :code code :detail detail))
(defun proper-list-p (value)
  ;; LIST-LENGTH detects cycles; dotted tails signal TYPE-ERROR. ANSI CL only.
  (and (listp value) (handler-case (integerp (list-length value)) (type-error () nil))))
(defun canonical-scope (map themes)
  "Validate before mutation and copy a set of current same-map Topic references."
  (unless (proper-list-p themes)
    (scope-problem :invalid-scope "Supply a proper finite list of Topics."))
  (remove-duplicates
   (mapcar (lambda (theme)
             (unless (typep theme 'topic) (scope-problem :invalid-theme "A theme must be a Topic object."))
             (let ((current (live-topic theme)))
               (unless (eq map (%topic-parent current))
                 (scope-problem :foreign-theme "Every theme must belong to the item's Topic Map."))
               current)) themes)
   :test #'eq :from-end t))
(defun same-scope-p (a b)
  ;; Storage is canonical and duplicate-free; equality has no sequence ordering.
  (and (= (length a) (length b)) (every (lambda (theme) (member theme b :test #'eq)) a)))

(defun normalize-names (map)
  ;; Rescan live owners after each replacement: merging Reifiers can replace
  ;; the owner/type/theme of the very Name currently being normalized.
  (loop for entry = (loop for topic in (%topic-map-topics map)
                         for pair = (equal-pair (%topic-names topic)
                           (lambda (a b) (and (string= (%topic-name-value a) (%topic-name-value b))
                                             (eq (%topic-name-type a) (%topic-name-type b))
                                             (same-scope-p (%topic-name-scope a) (%topic-name-scope b)))))
                         when pair return (cons topic pair))
        while entry do
    (let* ((topic (first entry)) (a (second entry)) (b (third entry))
           (c (%make-topic-name (%topic-name-value a) (%topic-name-type a) topic)))
      (setf (%topic-name-scope c) (copy-list (%topic-name-scope a))
            (%topic-name-item-identifiers c) (set-union (%topic-name-item-identifiers a) (%topic-name-item-identifiers b) #'string=)
            (%topic-name-variants c) (set-union (%topic-name-variants a) (%topic-name-variants b) #'eq)
            (%topic-names topic) (replace-pair (%topic-names topic) a b c)
            (%topic-name-forward a) c (%topic-name-forward b) c)
      (dolist (v (%topic-name-variants c)) (setf (%variant-parent v) c))
      (merge-item-reifiers c a b)))
  (normalize-variants map))

(defun merge-two-topics (map a b)
  ;; TMDM 6.2: create C, union supported properties, replace model references.
  ;; TMDM 6.2 conflict is checked against current targets BEFORE replacement.
  (check-core-subject-identifiers (append (%topic-subject-identifiers a) (%topic-subject-identifiers b)))
  (let ((left (topic-reified a)) (right (topic-reified b)))
    (when (and left right (not (eq left right)))
      (reification-problem :reifier-conflict "Topics reify different information items.")))
  (check-variant-merge-constraints map :pair (list a b))
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
              (%topic-name-type name) (canonical-topic (%topic-name-type name))
              (%topic-name-scope name) (canonical-scope map (%topic-name-scope name)))
        (dolist (item (%topic-name-variants name))
          (setf (%variant-scope item) (canonical-scope map (%variant-scope item))))))
    (dolist (topic (%topic-map-topics map))
      (dolist (occurrence (%topic-occurrences topic))
        (setf (%occurrence-parent occurrence) topic
              (%occurrence-type occurrence) (canonical-topic (%occurrence-type occurrence))
              (%occurrence-scope occurrence) (canonical-scope map (%occurrence-scope occurrence)))))
    (dolist (association (%topic-map-associations map))
      (setf (%association-type association) (canonical-topic (%association-type association))
            (%association-scope association) (canonical-scope map (%association-scope association)))
      (dolist (role (%association-roles association))
        (setf (%association-role-type role) (canonical-topic (%association-role-type role))
              (%association-role-player role) (canonical-topic (%association-role-player role)))))
    (dolist (item (map-information-items map))
      (when (and (reifiable-p item) (%item-reifier item))
        (setf (%item-reifier item) (canonical-topic (%item-reifier item)))))
    (normalize-names map)
    (normalize-occurrences map)
    (normalize-associations map)
    (canonical-topic c)))

(defun normalize-topic-map (map)
  "Reach a fixed point of same-map Topic and structural item merging."
  (check-type map topic-map)
  (when (needs-merge-preflight-p map)
    (return-from normalize-topic-map
      (preflight-merge-mutation map (lambda (ref) (normalize-topic-map (funcall ref map))))))
  (validate-map-core-subjects map)
  (check-variant-merge-constraints map)
  (loop for before = (length (map-information-items map)) do
    (loop for pair = (equal-pair (%topic-map-topics map) #'equal-topics-p)
          while pair do (merge-two-topics map (first pair) (second pair)))
    (normalize-names map) (normalize-occurrences map) (normalize-associations map)
    when (= before (length (map-information-items map))) return map))

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
    (when (needs-merge-preflight-p map)
      (return-from merge-topics (preflight-merge-mutation map
        (lambda (ref) (merge-topics (funcall ref a) (funcall ref b))))))
    (unless (eq a b) (setf a (merge-two-topics map a b)))
    (normalize-topic-map map)
    (canonical-topic a)))

(defun add-topic-identifier (topic kind iri)
  "Add a locator to its distinct identity property and perform required merging.
KIND is :ITEM-IDENTIFIER, :SUBJECT-IDENTIFIER or :SUBJECT-LOCATOR.
IRI is an already resolved, nonempty absolute locator string; CTM validates it."
  (unless (and (stringp iri) (plusp (length iri))) (error "A nonempty locator string is required."))
  (let ((topic (live-topic topic)))
    (when (needs-merge-preflight-p (%topic-parent topic))
      (return-from add-topic-identifier (preflight-merge-mutation (%topic-parent topic)
        (lambda (ref) (add-topic-identifier (funcall ref topic) kind iri)))))
    (when (eq kind :subject-identifier)
      (check-core-subject-identifiers (cons iri (%topic-subject-identifiers topic))))
    (check-topic-occurrence-identifiers (%topic-parent topic) kind iri)
    ;; Check the entire prospective identity closure before adding the locator.
    (check-variant-merge-constraints (%topic-parent topic) :identifier (list topic kind iri))
    (ecase kind
      (:item-identifier (pushnew (copy-seq iri) (%topic-item-identifiers topic) :test #'string=))
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
  ;; Preflight BEFORE creating a new Topic, so rejected cascades cannot leave
  ;; even an empty newly interned item in the original Map.
  (when (needs-merge-preflight-p map)
    (return-from intern-topic (preflight-merge-mutation map
      (lambda (ref) (intern-topic (funcall ref map) kind iri)))))
  (let ((topic (or (find-if (lambda (topic) (identifier-matches-p topic kind iri))
                           (%topic-map-topics map))
                   (let ((new (%make-topic map)))
                     (setf (%topic-map-topics map) (append (%topic-map-topics map) (list new)))
                     new))))
    (add-topic-identifier topic kind iri)))

(defun add-name (topic value &key (type nil type-supplied-p) scope)
  "Add a Name with VALUE, optional TYPE Topic and SCOPE Topic set (TMDM 5.4).
Validate all arguments before interning the default type. Retained Topic handles
are canonicalized, including after default-type identity merging."
  (check-type value string)
  (let* ((topic (live-topic topic)) (map (%topic-parent topic))
         (scope (canonical-scope map scope))
         (type (when type-supplied-p (live-topic type))))
    (when (and type-supplied-p (not (eq map (%topic-parent type))))
      (error "Name type belongs to another map."))
    (unless type-supplied-p
      (setf type (intern-topic map :subject-identifier (default-name-type-identifier))))
    (let* ((topic (canonical-topic topic)) (type (canonical-topic type))
           (scope (canonical-scope map scope))
           (existing (find-if (lambda (name)
                                (and (string= value (%topic-name-value name))
                                     (eq type (%topic-name-type name))
                                     (same-scope-p scope (%topic-name-scope name))))
                              (%topic-names topic))))
      (or existing
          (let ((name (%make-topic-name value type topic)))
            (setf (%topic-name-scope name) scope
                  (%topic-names topic) (append (%topic-names topic) (list name)))
            name)))))

(defun add-default-name (topic value &key scope)
  "Compatibility entry point for ADD-NAME with the CTM 3.11 default type."
  (add-name topic value :scope scope))
