(in-package #:topic-maps.tmdm)

(define-condition occurrence-error (error)
  ((code :initarg :code :reader occurrence-error-code)
   (detail :initarg :detail :reader occurrence-error-detail))
  (:report (lambda (c out) (format out "Occurrence ~A: ~A" (occurrence-error-code c) (occurrence-error-detail c)))))
(defun occurrence-problem (code detail) (error 'occurrence-error :code code :detail detail))
(define-condition occurrence-identifier-error (occurrence-error item-identifier-error) ())
(defun legacy-identifier-problem (condition)
  ;; Existing callers may still catch OCCURRENCE-ERROR; the uniform API also
  ;; exposes ITEM-IDENTIFIER-ERROR without breaking that condition contract.
  (error 'occurrence-identifier-error :code (item-identifier-error-code condition)
         :detail (item-identifier-error-detail condition)))
(defun same-occurrence-properties-p (a value datatype type scope)
  ;; Parent is the containing topic; Scope is compared as a Topic set.
  (and (string= (%occurrence-value a) value) (string= (%occurrence-datatype a) datatype)
       (eq (%occurrence-type a) type) (same-scope-p (%occurrence-scope a) scope)))
(defun check-topic-occurrence-identifiers (map kind iri)
  ;; TMDM 5.3.5's SI/II cross-identity rule concerns two Topics, not an
  ;; implicit Reification between a Topic and a non-Topic construct.
  (when (eq kind :item-identifier)
    (handler-case (validate-item-identifiers map (list iri) :topic-p t)
      (item-identifier-error (c) (legacy-identifier-problem c)))))
(defun validate-occurrence-identifiers (map topic type value datatype identifiers scope)
  (handler-case
      (validate-item-identifiers map identifiers
        :allowed (remove-if-not (lambda (other) (same-occurrence-properties-p other value datatype type scope))
                                (%topic-occurrences topic)))
    (item-identifier-error (c) (legacy-identifier-problem c))))
(defun normalize-occurrences (map)
  "TMDM 5.6/6.5: rescan live owners after Reifier-induced merges."
  (loop for entry = (loop for topic in (%topic-map-topics map)
                         for pair = (equal-pair (%topic-occurrences topic)
                           (lambda (a b) (same-occurrence-properties-p a (%occurrence-value b)
                             (%occurrence-datatype b) (%occurrence-type b) (%occurrence-scope b))))
                         when pair return (cons topic pair))
        while entry do
    (let* ((topic (first entry)) (a (second entry)) (b (third entry))
           (c (%make-occurrence (%occurrence-value a) (%occurrence-datatype a) (%occurrence-type a) topic)))
      (setf (%occurrence-scope c) (copy-list (%occurrence-scope a))
            (%occurrence-item-identifiers c) (set-union (%occurrence-item-identifiers a) (%occurrence-item-identifiers b) #'string=)
            (%topic-occurrences topic) (replace-pair (%topic-occurrences topic) a b c)
            (%occurrence-forward a) c (%occurrence-forward b) c)
      (merge-item-reifiers c a b)))
  map)
(defun add-occurrence (topic type value &key (datatype (string-datatype)) item-identifiers scope)
  "Create an Occurrence with a Scope Topic set; TYPE must be a same-map Topic. VALUE and DATATYPE
are strings; DATATYPE is any absolute locator (TMDM 4.4). Supported Integer/Decimal/Date/DateTime
lexical forms are validated; stored strings are never rewritten.
anyURI VALUE must already be absolute, never resolved here.
Validate before mutation, return current representative after duplicate replacement."
  (check-type value string) (check-type datatype string)
  ;; TMDM 4.4/5.6: datatype is a locator, never a Topic or a whitelist.
  (unless (absolute-locator-p datatype)
    (occurrence-problem :invalid-datatype "Datatype must be a resolved absolute locator."))
  (when (and (string= datatype (integer-datatype)) (not (integer-lexical-p value)))
    (occurrence-problem :invalid-integer-value "Value is not an xsd:integer lexical form."))
  (when (and (string= datatype (decimal-datatype)) (not (decimal-lexical-p value)))
    (occurrence-problem :invalid-decimal-value "Value is not an xsd:decimal lexical form."))
  (when (and (string= datatype (date-datatype)) (not (date-lexical-p value)))
    (occurrence-problem :invalid-date-value "Value is not an XSD 1.0 date lexical form or valid Gregorian date."))
  (when (and (string= datatype (datetime-datatype)) (not (datetime-lexical-p value)))
    (occurrence-problem :invalid-datetime-value "Value is not an XSD 1.0 dateTime lexical form."))
  (when (and (string= datatype (iri-datatype)) (not (absolute-locator-p value)))
    (occurrence-problem :relative-uri-value "TMDM IRI-valued Occurrences require an absolute locator."))
  (let* ((topic (live-topic topic)) (type (live-topic type)) (map (%topic-parent topic))
         (scope (canonical-scope map scope)))
    (unless (eq map (%topic-parent type))
      (occurrence-problem :foreign-type "Occurrence Parent and Type must belong to the same map."))
    (validate-occurrence-identifiers map topic type value datatype item-identifiers scope)
    (let ((item (%make-occurrence value datatype type topic)))
      (setf (%occurrence-scope item) scope
            (%occurrence-item-identifiers item) (mapcar #'copy-seq (remove-duplicates item-identifiers :test #'string= :from-end t))
            (%topic-occurrences topic) (append (%topic-occurrences topic) (list item)))
      (normalize-occurrences map)
      (canonical-occurrence item))))
