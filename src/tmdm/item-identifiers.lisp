(in-package #:topic-maps.tmdm)

(define-condition item-identifier-error (error)
  ((code :initarg :code :reader item-identifier-error-code)
   (detail :initarg :detail :reader item-identifier-error-detail))
  (:report (lambda (c out)
             (format out "Item Identifier ~A: ~A" (item-identifier-error-code c)
                     (item-identifier-error-detail c)))))
(defun identifier-problem (code detail)
  (error 'item-identifier-error :code code :detail detail))

(defun absolute-locator-p (value)
  ;; Callers supply validated/resolved locators, not CTM source or CXTM output.
  (and (stringp value)
       (let ((colon (position #\: value)))
         (and colon (plusp colon)
              (let ((head (subseq value 0 colon)))
                (and (or (char<= #\a (char head 0) #\z) (char<= #\A (char head 0) #\Z))
                     (every (lambda (c) (or (char<= #\a c #\z) (char<= #\A c #\Z)
                                           (char<= #\0 c #\9) (find c "+-."))) head)))))))

(defun canonical-item (item)
  (etypecase item
    (topic-map item) (topic (canonical-topic item)) (topic-name (canonical-topic-name item))
    (variant (canonical-variant item)) (occurrence (canonical-occurrence item))
    (association (canonical-association item)) (association-role (canonical-association-role item))))
(defun %item-identifiers (item)
  (etypecase item
    (topic-map (%topic-map-item-identifiers item)) (topic (%topic-item-identifiers item))
    (topic-name (%topic-name-item-identifiers item)) (variant (%variant-item-identifiers item))
    (occurrence (%occurrence-item-identifiers item)) (association (%association-item-identifiers item))
    (association-role (%association-role-item-identifiers item))))
(defun (setf %item-identifiers) (value item)
  (etypecase item
    (topic-map (setf (%topic-map-item-identifiers item) value))
    (topic (setf (%topic-item-identifiers item) value))
    (topic-name (setf (%topic-name-item-identifiers item) value))
    (variant (setf (%variant-item-identifiers item) value))
    (occurrence (setf (%occurrence-item-identifiers item) value))
    (association (setf (%association-item-identifiers item) value))
    (association-role (setf (%association-role-item-identifiers item) value))))
(defun item-identifiers (item)
  "Return a fresh list of fresh locator strings for any of the seven TMDM items.
Retained handles resolve without modifying forward links."
  (mapcar #'copy-seq (%item-identifiers (canonical-item item))))
(defun item-topic-map (item)
  (let ((item (canonical-item item)))
    (etypecase item
      (topic-map item) (topic (%topic-parent item))
      (topic-name (item-topic-map (%topic-name-parent item)))
      (variant (item-topic-map (%variant-parent item)))
      (occurrence (item-topic-map (%occurrence-parent item)))
      (association (%association-parent item))
      (association-role (item-topic-map (%association-role-parent item))))))
(defun map-information-items (map)
  "Enumerate current information items, including MAP; no independent identity index."
  (append (list map)
          (loop for topic in (%topic-map-topics map) append
            (append (list topic) (copy-list (%topic-names topic))
                    (loop for name in (%topic-names topic) append (copy-list (%topic-name-variants name)))
                    (copy-list (%topic-occurrences topic))))
          (loop for association in (%topic-map-associations map) append
            (cons association (copy-list (%association-roles association))))))
(defun validate-item-identifiers (map identifiers &key allowed topic-p)
  "Check an assignment before mutation. ALLOWED contains identical/equal current
items that this operation will retain or merge. Only Topics merge by II alone."
  (unless (and (proper-list-p identifiers) (every #'absolute-locator-p identifiers))
    (identifier-problem :invalid-item-identifiers "Supply a proper finite list of resolved absolute locators."))
  (dolist (other (map-information-items map))
    (unless (or (member other allowed :test #'eq) (and topic-p (typep other 'topic)))
      (when (intersection identifiers (%item-identifiers other) :test #'string=)
        (identifier-problem :duplicate-item-identifier "Locator already identifies a different information item."))))
  identifiers)
(defun validate-map-item-identifiers (map)
  "Validate current sets/uniqueness without normalizing or changing the map."
  (let ((items (map-information-items map)))
    (dolist (item items)
      (let ((ids (%item-identifiers item)))
        (unless (and (proper-list-p ids) (every #'absolute-locator-p ids)
                     (= (length ids) (length (remove-duplicates ids :test #'string=))))
          (identifier-problem :invalid-item-identifiers "Item Identifier storage must be a locator set."))))
    (loop for tail on items for ids = (%item-identifiers (first tail)) do
      (dolist (other (rest tail))
        (when (intersection ids (%item-identifiers other) :test #'string=)
          (identifier-problem :duplicate-item-identifier "Different live items share an Item Identifier.")))))
  t)
(defun add-item-identifier (item iri)
  "Add an already resolved absolute locator, returning the canonical item.
TMDM locator equality is STRING=, never CXTM base/NFC normalization.
Topics delegate to ADD-TOPIC-IDENTIFIER and its existing merge/preflight rules.
Non-Topics do not become equal merely by sharing identifiers."
  (let* ((item (canonical-item item)) (map (item-topic-map item)))
    (unless (member item (map-information-items map) :test #'eq)
      (identifier-problem :invalid-item "Item is not a current member of its Topic Map."))
    (unless (absolute-locator-p iri)
      (identifier-problem :invalid-item-identifiers "Supply a resolved absolute locator."))
    (if (typep item 'topic)
        (add-topic-identifier item :item-identifier iri)
        (progn
          (validate-item-identifiers map (list iri) :allowed (list item))
          ;; Retain the Occurrence constructor compatibility condition contract.
          (when (typep item 'occurrence)
            (validate-occurrence-identifiers map (%occurrence-parent item) (%occurrence-type item)
              (%occurrence-value item) (%occurrence-datatype item) (list iri) (%occurrence-scope item)))
          (pushnew (copy-seq iri) (%item-identifiers item) :test #'string=)
          item))))
