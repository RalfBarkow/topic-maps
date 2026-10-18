(in-package #:topic-maps.tmdm)

(define-condition variant-error (error)
  ((code :initarg :code :reader variant-error-code)
   (detail :initarg :detail :reader variant-error-detail))
  (:report (lambda (c out) (format out "Variant ~A: ~A" (variant-error-code c) (variant-error-detail c)))))
(defun variant-problem (code detail) (error 'variant-error :code code :detail detail))
(defun variant-scope-valid-p (scope parent-scope)
  ;; Both operands are sets. TMDM 5.5 requires a *proper* superset.
  (and (> (length scope) (length parent-scope))
       (subsetp parent-scope scope :test #'eq)))

(defun check-variant-merge-constraints (map &key pair identifier)
  "Preflight the full prospective Topic identity closure, without model mutation.
An explicit PAIR and/or proposed IDENTIFIER (Topic Kind IRI) may add edges.
Reject scope collapse atomically; TMDM specifies the invariant, not this API policy."
  (let ((names (mapcan (lambda (topic) (copy-list (%topic-names topic))) (%topic-map-topics map))))
    (when (some #'%topic-name-variants names)
      (let ((parents (make-hash-table :test #'eq)) (topics (%topic-map-topics map)))
        (dolist (topic topics) (setf (gethash topic parents) topic))
        (labels ((root (topic)
                   (loop for current = topic then (gethash current parents)
                         when (eq current (gethash current parents)) return current))
                 (join (a b) (setf (gethash (root a) parents) (root b)))
                 (project (scope) (remove-duplicates (mapcar #'root scope) :test #'eq)))
          (loop for tail on topics do
            (dolist (other (rest tail))
              (when (equal-topics-p (first tail) other) (join (first tail) other))))
          (when pair (join (first pair) (second pair)))
          (when identifier
            (destructuring-bind (topic kind iri) identifier
              (dolist (other topics)
                (when (identifier-matches-p other kind iri) (join topic other)))))
          (dolist (name names)
            (let ((parent-scope (project (%topic-name-scope name))))
              (dolist (item (%topic-name-variants name))
                (unless (variant-scope-valid-p (project (%variant-scope item)) parent-scope)
                  (variant-problem :variant-scope-collapse
                    "Topic merging would remove the Variant's additional scope; no mutation was performed."))))))))))

(defun normalize-variants (map)
  "TMDM 5.5/6.4: union metadata and rescan live parents after cascades."
  (loop for entry = (loop for topic in (%topic-map-topics map) thereis
                     (loop for name in (%topic-names topic)
                           for pair = (equal-pair (%topic-name-variants name)
                             (lambda (a b) (and (string= (%variant-value a) (%variant-value b))
                                               (string= (%variant-datatype a) (%variant-datatype b))
                                               (same-scope-p (%variant-scope a) (%variant-scope b)))))
                           when pair return (cons name pair)))
        while entry do
    (let* ((name (first entry)) (a (second entry)) (b (third entry))
           (c (%make-variant (%variant-value a) (%variant-datatype a) name)))
      (setf (%variant-scope c) (copy-list (%variant-scope a))
            (%variant-item-identifiers c) (set-union (%variant-item-identifiers a) (%variant-item-identifiers b) #'string=)
            (%topic-name-variants name) (replace-pair (%topic-name-variants name) a b c)
            (%variant-forward a) c (%variant-forward b) c)
      (merge-item-reifiers c a b)))
  map)

(defun add-variant (name value &key (datatype (string-datatype)) scope)
  "Add a Variant with actual TMDM SCOPE, a proper superset of NAME's.
The CTM reader unions explicit themes with the Parent Name scope before calling.
Validate before mutation. Quoted lexical values are not rewritten."
  (check-type value string) (check-type datatype string)
  (let* ((name (canonical-topic-name name)) (owner (live-topic (%topic-name-parent name)))
         (map (%topic-parent owner)) (scope (canonical-scope map scope)))
    (unless (member name (%topic-names owner) :test #'eq)
      (variant-problem :invalid-parent "Parent must be a live Name in its Topic Map."))
    (unless (variant-scope-valid-p scope (%topic-name-scope name))
      (variant-problem :invalid-variant-scope "Variant scope must properly contain its Parent Name scope."))
    (unless (absolute-locator-p datatype)
      (variant-problem :invalid-datatype "Datatype must be a resolved absolute locator."))
    (dolist (rule (list (list (integer-datatype) #'integer-lexical-p :invalid-integer-value)
                       (list (decimal-datatype) #'decimal-lexical-p :invalid-decimal-value)
                       (list (date-datatype) #'date-lexical-p :invalid-date-value)
                       (list (datetime-datatype) #'datetime-lexical-p :invalid-datetime-value)
                       (list (iri-datatype) #'absolute-locator-p :relative-uri-value)))
      (when (and (string= datatype (first rule)) (not (funcall (second rule) value)))
        (variant-problem (third rule) "Value is not valid for the specified datatype.")))
    (let ((item (%make-variant value datatype name)))
      (setf (%variant-scope item) scope
            (%topic-name-variants name) (append (%topic-name-variants name) (list item)))
      (normalize-variants map)
      (canonical-variant item))))
