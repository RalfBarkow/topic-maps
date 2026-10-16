(in-package #:topic-maps.cxtm)

(defvar *base-locator*)
(defvar *locator-cache*)

(defun path-start (iri)
  (let* ((colon (position #\: iri)) (start (if colon (1+ colon) 0)))
    (if (and (<= (+ start 2) (length iri))
             (string= "//" iri :start2 start :end2 (+ start 2)))
        (or (position #\/ iri :start (+ start 2)) (length iri)) start)))
(defun normalized-locator (locator)
  "CXTM 3.18, literal prefix removal, NOT RFC relative-IRI resolution."
  (or (gethash locator *locator-cache*)
      (setf (gethash locator *locator-cache*)
            (nfc
             (let ((prefix (string-right-trim "/" (subseq *base-locator* 0
                                     (position-if (lambda (c) (find c "?#")) *base-locator*)))))
               (loop
                 (when (and (<= (length prefix) (length locator))
                            (string= prefix locator :end2 (length prefix)))
                   (return (string-left-trim "/" (subseq locator (length prefix)))))
                 (let ((start (path-start prefix)))
                   (when (>= start (length prefix)) (return locator))
                   (setf prefix (string-right-trim "/"
                          (subseq prefix 0 (or (position #\/ prefix :start start :from-end t) start)))))))))))

(defun string-order (a b)
  ;; Character CODE order, independent of a Lisp implementation's collation.
  (loop for x across a for y across b
        when (< (char-code x) (char-code y)) do (return-from string-order -1)
        when (> (char-code x) (char-code y)) do (return-from string-order 1))
  (signum (- (length a) (length b))))
(defun sorted (items comparison)
  (stable-sort (copy-list items) (lambda (a b) (minusp (funcall comparison a b)))))
(defun set-order (a b comparison)
  (let ((size (signum (- (length a) (length b)))))
    (if (not (zerop size)) size
        (loop for x in (sorted a comparison) for y in (sorted b comparison)
              for c = (funcall comparison x y) when (not (zerop c)) return c
              finally (return 0)))))
(defun locator-order (a b) (string-order (normalized-locator a) (normalized-locator b)))
(defun topic-order (a b)
  (loop for getter in '(topic-subject-identifiers topic-subject-locators topic-item-identifiers)
        for c = (set-order (funcall getter a) (funcall getter b) #'locator-order)
        when (not (zerop c)) return c finally (return 0)))
(defun name-order (a b)
  (let ((c (string-order (nfc (topic-name-value a)) (nfc (topic-name-value b)))))
    (if (not (zerop c)) c
        (let ((type (topic-order (topic-name-type a) (topic-name-type b))))
          (if (not (zerop type)) type (topic-order (topic-name-parent a) (topic-name-parent b)))))))
(defun occurrence-value-order (a b)
  ;; TMDM 4.3/5.6: anyURI values are locators; other supported values are strings.
  ;; CXTM 4.2 orders strings before locators, independent of their spelling.
  (let ((iri-a (string= (occurrence-datatype a) (iri-datatype)))
        (iri-b (string= (occurrence-datatype b) (iri-datatype))))
    (cond ((and iri-a iri-b) (locator-order (occurrence-value a) (occurrence-value b)))
          (iri-a 1) (iri-b -1)
          (t (string-order (nfc (occurrence-value a)) (nfc (occurrence-value b)))))))
(defun occurrence-order (a b)
  (loop for comparison in
        (list (occurrence-value-order a b)
              (locator-order (occurrence-datatype a) (occurrence-datatype b))
              (topic-order (occurrence-type a) (occurrence-type b))
              ;; Both scopes are empty; parent comparison is the final key.
              (topic-order (occurrence-parent a) (occurrence-parent b)))
        when (not (zerop comparison)) return comparison finally (return 0)))

(defun role-signature-order (a b)
  ;; In a single parent's roles set, [parent] is equal. During association
  ;; comparison equal player/type pairs also have equal parent-comparison
  ;; context. Comparing this prefix avoids recursive parent/roles traversal.
  (let ((c (topic-order (association-role-player a) (association-role-player b))))
    (if (not (zerop c)) c (topic-order (association-role-type a) (association-role-type b)))))
(defun association-order (a b)
  (let ((c (topic-order (association-type a) (association-type b))))
    (if (not (zerop c)) c
        (set-order (association-roles a) (association-roles b) #'role-signature-order))))
(defun role-order (a b)
  (let ((c (role-signature-order a b)))
    (if (not (zerop c)) c
        (association-order (association-role-parent a) (association-role-parent b)))))

(defun require-exact-item (item type)
  ;; A future/subclass model carrying extra properties is explicitly unsupported.
  (unless (eq (type-of item) type)
    (fail :unsupported-information-item (format nil "Expected exact ~S, received ~S." type (type-of item)) t)))
(defun require-set (items)
  (unless (and (listp items) (= (length items) (length (remove-duplicates items :test #'eq))))
    (fail :invalid-set "An information-item collection must be a proper set.")))
(defun validate-map (map)
  "Validate current model schema and referential integrity; never normalize/mutate."
  (require-exact-item map 'topic-map)
  (let ((topics (topic-map-topics map)) (associations (topic-map-associations map)))
    (require-set topics) (require-set associations)
    (labels ((reference (topic)
               (require-exact-item topic 'topic)
               (unless (and (eq topic (canonical-topic topic)) (member topic topics :test #'eq))
                 (fail :invalid-topic-reference "Reference must designate a current Topic in this map."))))
      (dolist (topic topics)
        (reference topic)
        (unless (eq (topic-parent topic) map) (fail :invalid-parent "Topic parent mismatch."))
        (unless (or (topic-item-identifiers topic) (topic-subject-identifiers topic) (topic-subject-locators topic))
          (fail :unidentified-topic "CXTM 4.6 requires an identity-bearing Topic." t))
        (dolist (getter '(topic-item-identifiers topic-subject-identifiers topic-subject-locators))
          (let ((ids (funcall getter topic)))
            (unless (and (every (lambda (s) (and (stringp s) (plusp (length s)))) ids)
                         (= (length ids) (length (remove-duplicates ids :test #'string=))))
              (fail :invalid-locators "Locator properties must be sets of nonempty strings."))))
        (require-set (topic-names topic))
        (dolist (name (topic-names topic))
          (require-exact-item name 'topic-name)
          (unless (and (eq name (canonical-topic-name name)) (eq (topic-name-parent name) topic))
            (fail :invalid-parent "Name must be current and owned by its containing Topic."))
          (reference (topic-name-type name)))
        (require-set (topic-occurrences topic))
        (dolist (item (topic-occurrences topic))
          (require-exact-item item 'occurrence)
          (unless (and (eq item (canonical-occurrence item)) (eq (occurrence-parent item) topic))
            (fail :invalid-parent "Occurrence must be current and owned by its containing Topic."))
          (reference (occurrence-type item))
          (unless (topic-maps.tmdm::absolute-locator-p (occurrence-datatype item))
            (fail :invalid-occurrence-datatype "Datatype must be an absolute locator."))
          (when (and (string= (occurrence-datatype item) (integer-datatype))
                     (not (integer-lexical-p (occurrence-value item))))
            (fail :invalid-integer-value "Occurrence value is not an xsd:integer lexical form."))
          (when (and (string= (occurrence-datatype item) (decimal-datatype))
                     (not (decimal-lexical-p (occurrence-value item))))
            (fail :invalid-decimal-value "Occurrence value is not an xsd:decimal lexical form."))
          (when (string= (occurrence-datatype item) (date-datatype))
            (unless (date-lexical-p (occurrence-value item))
              (fail :invalid-date-value "Occurrence value is not a valid XSD 1.0 date."))
            (unless (canonical-date-lexical-form (occurrence-value item))
              (fail :date-timezone-canonicalization "XSD date recoverable-timezone canonicalization is outside this slice." t)))
          (when (string= (occurrence-datatype item) "http://www.w3.org/2001/XMLSchema#dateTime")
            (fail :unsupported-occurrence-datatype "DateTime canonicalization is not implemented." t))
          (when (and (string= (occurrence-datatype item) (iri-datatype))
                     (not (topic-maps.tmdm::absolute-locator-p (occurrence-value item))))
            (fail :invalid-occurrence-value "IRI-valued Occurrences must store an absolute locator."))
          (let ((ids (occurrence-item-identifiers item)))
            (unless (and (every #'topic-maps.tmdm::absolute-locator-p ids)
                         (= (length ids) (length (remove-duplicates ids :test #'string=))))
              (fail :invalid-locators "Occurrence identifiers must be an absolute locator set.")))))
      (dolist (a associations)
        (require-exact-item a 'association)
        (unless (and (eq a (canonical-association a)) (eq (association-parent a) map))
          (fail :invalid-parent "Association must be current and owned by this map."))
        (reference (association-type a)) (require-set (association-roles a))
        (unless (association-roles a) (fail :empty-association "Association requires Roles."))
        (dolist (r (association-roles a))
          (require-exact-item r 'association-role)
          (unless (and (eq r (canonical-association-role r)) (eq (association-role-parent r) a))
            (fail :invalid-parent "Role must be current and owned by its Association."))
          (reference (association-role-type r)) (reference (association-role-player r)))))))

(defun xml-text (text out)
  (loop for c across (nfc text) for n = (char-code c) do
    (unless (or (member n '(9 10 13)) (<= 32 n #xd7ff) (<= #xe000 n #xfffd) (<= #x10000 n #x10ffff))
      (fail :xml-character (format nil "U+~4,'0X cannot be represented in XML 1.0." n)))
    (case c
      (#\& (write-string "&amp;" out)) (#\< (write-string "&lt;" out))
      (#\> (write-string "&gt;" out)) (#\Return (write-string "&#xD;" out))
      (otherwise (write-char c out)))))
(defun emit-locators (tag locators out)
  (when locators
    (format out "<~A>~%" tag)
    (dolist (locator (sorted locators #'locator-order))
      (write-string "<locator>" out) (xml-text (normalized-locator locator) out)
      (format out "</locator>~%"))
    (format out "</~A>~%" tag)))

(defun canonicalize (map &key base-locator)
  "Return CXTM as a string. BASE-LOCATOR is an explicit absolute IRI (CXTM 3.1).
Only the existing TMDM schema is supported: empty Scope, null Reifier, no
Variants or non-Topic identifiers other than Occurrence identifiers. Does not mutate MAP or handles."
  (unless (and (stringp base-locator) (position #\: base-locator)
               (let ((scheme (subseq base-locator 0 (position #\: base-locator))))
                 (and (plusp (length scheme))
                      (or (char<= #\a (char scheme 0) #\z) (char<= #\A (char scheme 0) #\Z))
                      (every (lambda (c) (or (char<= #\a c #\z) (char<= #\A c #\Z)
                                            (char<= #\0 c #\9) (find c "+-."))) scheme))))
    (fail :invalid-base-locator "Supply an absolute base locator."))
  (validate-map map)
  (let* ((*base-locator* base-locator) (*locator-cache* (make-hash-table :test #'equal))
         (topics (sorted (topic-map-topics map) #'topic-order))
         (associations (sorted (topic-map-associations map) #'association-order))
         (topic-numbers (make-hash-table :test #'eq))
         (association-numbers (make-hash-table :test #'eq))
         (role-numbers (make-hash-table :test #'eq)))
    ;; NFC/base normalization can expose distinct, comparator-equal Topics.
    ;; No address/construction-order tie breaker or implicit merge is permitted.
    (loop for (a b) on topics while b do
      (when (zerop (topic-order a b))
        (fail :ambiguous-topic-order "Distinct Topics have identical normalized identity keys; resolve model identity first." t)))
    (loop for topic in topics for number from 1 do (setf (gethash topic topic-numbers) number))
    (loop for a in associations for number from 1 do
      (setf (gethash a association-numbers) number)
      (loop for r in (sorted (association-roles a) #'role-order) for index from 1 do
        (setf (gethash r role-numbers) index)))
    (with-output-to-string (out)
      (labels ((type-ref (topic)
                 (format out "<type topicref=\"~D\"></type>~%" (gethash topic topic-numbers)))
               (role-ref (r)
                 (format out "<rolePlayed ref=\"association.~D.role.~D\"></rolePlayed>~%"
                         (gethash (association-role-parent r) association-numbers)
                         (gethash r role-numbers))))
        (format out "<topicMap>~%")
        (loop for topic in topics for number from 1 do
          (format out "<topic number=\"~D\">~%" number)
          (emit-locators "subjectIdentifiers" (topic-subject-identifiers topic) out)
          (emit-locators "subjectLocators" (topic-subject-locators topic) out)
          (emit-locators "itemIdentifiers" (topic-item-identifiers topic) out)
          (loop for name in (sorted (topic-names topic) #'name-order) for index from 1 do
            (format out "<name number=\"~D\">~%<value>" index)
            (xml-text (topic-name-value name) out) (format out "</value>~%")
            (type-ref (topic-name-type name)) (format out "</name>~%"))
          (loop for item in (sorted (topic-occurrences topic) #'occurrence-order) for index from 1 do
            (format out "<occurrence number=\"~D\">~%<value>" index)
            (xml-text (cond ((string= (occurrence-datatype item) (iri-datatype))
                             (normalized-locator (occurrence-value item)))
                            ((string= (occurrence-datatype item) (integer-datatype))
                             (canonical-integer-lexical-form (occurrence-value item)))
                            ((string= (occurrence-datatype item) (decimal-datatype))
                             (canonical-decimal-lexical-form (occurrence-value item)))
                            ((string= (occurrence-datatype item) (date-datatype))
                             (canonical-date-lexical-form (occurrence-value item)))
                            (t (occurrence-value item))) out)
            (format out "</value>~%<datatype>")
            ;; CXTM 3.14: datatype locator is NOT base-normalized.
            (xml-text (occurrence-datatype item) out) (format out "</datatype>~%")
            (type-ref (occurrence-type item))
            (emit-locators "itemIdentifiers" (occurrence-item-identifiers item) out)
            (format out "</occurrence>~%"))
          (dolist (r (sorted (topic-roles-played topic) #'role-order)) (role-ref r))
          (format out "</topic>~%"))
        (loop for a in associations for number from 1 do
          (format out "<association number=\"~D\">~%" number)
          (type-ref (association-type a))
          (loop for r in (sorted (association-roles a) #'role-order) for index from 1 do
            (format out "<role number=\"~D\">~%<player topicref=\"~D\"></player>~%"
                    index (gethash (association-role-player r) topic-numbers))
            (type-ref (association-role-type r)) (format out "</role>~%"))
          (format out "</association>~%"))
        ;; CXTM 3.1 step 2 appends LF after EVERY element, including the root.
        (format out "</topicMap>~%")))))

(defun canonicalize-octets (map &key base-locator)
  "Return canonical UTF-8 octets, with no BOM and the CXTM-mandated final LF."
  (let ((out (make-array 0 :element-type '(unsigned-byte 8) :adjustable t :fill-pointer 0)))
    (loop for c across (canonicalize map :base-locator base-locator) for n = (char-code c) do
      (flet ((octet (b) (vector-push-extend b out)))
        (cond ((< n #x80) (octet n))
              ((< n #x800) (octet (logior #xc0 (ash n -6))) (octet (logior #x80 (logand n 63))))
              ((< n #x10000) (octet (logior #xe0 (ash n -12)))
               (octet (logior #x80 (logand (ash n -6) 63))) (octet (logior #x80 (logand n 63))))
              (t (octet (logior #xf0 (ash n -18))) (octet (logior #x80 (logand (ash n -12) 63)))
                 (octet (logior #x80 (logand (ash n -6) 63))) (octet (logior #x80 (logand n 63))))))) out))
(defun write-cxtm (map pathname &key base-locator)
  "Write canonical UTF-8 bytes to PATHNAME; MAP is not modified."
  (let ((bytes (canonicalize-octets map :base-locator base-locator)))
    (with-open-file (out pathname :direction :output :element-type '(unsigned-byte 8)
                         :if-exists :supersede :if-does-not-exist :create)
      (write-sequence bytes out))) pathname)
