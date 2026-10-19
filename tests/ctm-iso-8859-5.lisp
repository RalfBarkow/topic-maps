(defpackage #:topic-maps.encoding.tests
  (:use #:cl #:topic-maps.tmdm)
  (:import-from #:topic-maps.registered-original.tests
    #:check #:fields #:binary #:case-state #:identity-fields #:captured-read #:condition-data)
  (:export #:run-tests #:write-reports))
(in-package #:topic-maps.encoding.tests)
(defparameter *doc* "https://example.invalid/encoding/main.ctm")
(defparameter *child* "https://example.invalid/encoding/child.ctm")
(defparameter *iso-names*
  '("ISO-8859-5" "ISO_8859-5:1988" "ISO_8859-5" "iso-ir-144" "cyrillic" "csISOLatinCyrillic"))
(defparameter *utf8-names* '("UTF-8" "csUTF8"))
;; Independent expected A0..FF codepoints, matching the Unicode mapping table.
;; 00..9F are identity mappings. Production code uses the qualified SBCL codec.
(defparameter *iso-high*
  #(
    #x00A0 #x0401 #x0402 #x0403 #x0404 #x0405 #x0406 #x0407 #x0408 #x0409 #x040A #x040B #x040C #x00AD #x040E #x040F
    #x0410 #x0411 #x0412 #x0413 #x0414 #x0415 #x0416 #x0417 #x0418 #x0419 #x041A #x041B #x041C #x041D #x041E #x041F
    #x0420 #x0421 #x0422 #x0423 #x0424 #x0425 #x0426 #x0427 #x0428 #x0429 #x042A #x042B #x042C #x042D #x042E #x042F
    #x0430 #x0431 #x0432 #x0433 #x0434 #x0435 #x0436 #x0437 #x0438 #x0439 #x043A #x043B #x043C #x043D #x043E #x043F
    #x0440 #x0441 #x0442 #x0443 #x0444 #x0445 #x0446 #x0447 #x0448 #x0449 #x044A #x044B #x044C #x044D #x044E #x044F
    #x2116 #x0451 #x0452 #x0453 #x0454 #x0455 #x0456 #x0457 #x0458 #x0459 #x045A #x045B #x045C #x00A7 #x045E #x045F
  ))
(defvar *checks* nil)
(defvar *positives* nil)
(defvar *negatives* nil)
(defvar *codepoints* nil)
(defvar *selection* nil)
(defvar *original* nil)
(defvar *entry-statuses* nil)
(defun octets (text &optional (encoding :iso-8859-5))
  (sb-ext:string-to-octets text :external-format encoding))
(defun header (name body)
  (if name (format nil "%encoding \"~A\"~%~A" name body) body))
(defun canonical (map) (topic-maps.cxtm:canonicalize-octets map :base-locator *doc*))
(defun source-hex (bytes) (format nil "~{~2,'0X~^ ~}" (coerce bytes 'list)))
(defun file-values (label bytes encoding &optional resolver)
  (uiop:with-temporary-file (:pathname path :type "ctm")
    (with-open-file (out path :direction :output :if-exists :supersede :element-type '(unsigned-byte 8))
      (write-sequence bytes out))
    (unwind-protect
        (handler-case
            (multiple-value-bind (map counter)
                (topic-maps.ctm:deserialize-file path :document-iri *doc* :source-name label :encoding encoding
                                               :wildcard-counter 17 :resource-resolver resolver)
              (values map counter nil))
          (topic-maps.ctm:ctm-error (condition) (values nil nil condition)))
      (check (concatenate 'string label ":file-bytes-preserved") (equalp bytes (binary path))))))
(defun observe-positive (label map counter &optional input encoding)
  (let* ((held (topic-maps.import.tests::handles map))
         (before (topic-maps.import.tests::state map held)) (actual (canonical map)))
    (check (concatenate 'string label ":current-model-and-pure-canonicalization")
      (and (topic-maps.reference.tests::references-current-p map)
           (equal before (topic-maps.import.tests::state map held)) (equalp actual (canonical map))))
    (push (fields "label" label "suppliedEncoding" encoding "inputHex" (when input (source-hex input))
                  "finalCounter" counter "actualCXTM" (topic-maps.ctm::decode-utf8 actual)
                  "model" (topic-maps.template.tests::observe map)) *positives*)))
(defun good-file (label input body &optional encoding)
  (multiple-value-bind (map counter condition) (file-values label input encoding)
    (check (concatenate 'string label ":actual-deserialization") (and map (null condition)))
    (multiple-value-bind (expected expected-counter)
        (topic-maps.ctm:deserialize-string body :document-iri *doc* :wildcard-counter 17)
      (check (concatenate 'string label ":Unicode-reference-CXTM-and-identities")
        (and (= counter expected-counter) (equalp (canonical map) (canonical expected)))))
    (observe-positive label map counter input encoding)
    (values map counter)))
(defun specific (label condition class code position unit &optional (source label) purpose byte-position)
  (check (concatenate 'string label ":condition-code-source-position-and-unit")
    (and condition (eq class (type-of condition)) (eq code (topic-maps.ctm:error-code condition))
         (= position (topic-maps.ctm:error-position condition)) (eq unit (topic-maps.ctm:error-position-unit condition))
         (equal source (topic-maps.ctm:error-source condition)) (null (topic-maps.ctm:error-cause condition))
         (if purpose (eq purpose (getf (first (topic-maps.ctm:error-context condition)) :purpose))
             (null (topic-maps.ctm:error-context condition)))))
  (check (concatenate 'string label ":line-and-column-units")
    (if (eq unit :byte)
        (and (null (topic-maps.ctm:error-line condition)) (null (topic-maps.ctm:error-column condition)))
        (and (integerp (topic-maps.ctm:error-line condition)) (integerp (topic-maps.ctm:error-column condition)))))
  (push (fields "label" label "condition" (condition-data condition)
                "positionInOriginalBytes" byte-position) *negatives*))
(defun bad-file (label input encoding class code position unit &optional line column byte-position)
  (multiple-value-bind (map counter condition) (file-values label input encoding)
    (declare (ignore counter)) (check (concatenate 'string label ":not-accepted") (null map))
    (specific label condition class code position unit label nil byte-position)
    (when line
      (check (concatenate 'string label ":exact-line-and-column")
        (and (= line (topic-maps.ctm:error-line condition)) (= column (topic-maps.ctm:error-column condition)))))))
(defun decoder-table-tests ()
  (let* ((bytes (make-array 256 :element-type '(unsigned-byte 8) :initial-contents (loop for i below 256 collect i)))
         (before (copy-seq bytes)) (decoded (topic-maps.ctm::decode-iso-8859-5 bytes)))
    (check "table:total-256-scalars-no-replacement-and-exact-roundtrip"
      (and (= 256 (length decoded)) (not (find (code-char #xfffd) decoded))
           (equalp before bytes) (equalp bytes (octets decoded))))
    (loop for byte below 256 for c across decoded do
      (check (format nil "table:byte-~2,'0X" byte)
        (= (char-code c) (if (< byte 160) byte (aref *iso-high* (- byte 160))))))
    (check "table:generic-resource-vector-also-decodes"
      (equal decoded (topic-maps.ctm::decode-ctm-octets (coerce bytes 'simple-vector) :encoding "cyrillic")))
    (setf *codepoints* (map 'vector #'char-code decoded))))
(defun alias-and-model-tests ()
  (let ((body "russia - \"Россия\". ? - \"ASCII\". ?named - \"Ё№я§џ\". ?named - \"Ё№я§џ\"."))
    (dolist (declared *iso-names*)
      (dolist (supplied (cons nil *iso-names*))
        (let ((label (format nil "iso:decl=~A:provided=~A" declared supplied)))
          (multiple-value-bind (map counter) (good-file label (octets (header declared body)) body supplied)
            (let* ((russia (topic-maps.registered-original.tests::local map *doc* "russia"))
                   (generated (loop for topic in (topic-map-topics map) append
                                (remove-if-not (lambda (iri) (search "#$__" iri)) (topic-item-identifiers topic)))))
              (check (concatenate 'string label ":name-and-wildcard-identities")
                (and (= 19 counter) (equal "Россия" (topic-name-value (first (topic-names russia))))
                     (topic-maps.registered-original.tests::same-set generated
                       (list (concatenate 'string *doc* "#$__18") (concatenate 'string *doc* "#$__19.named"))))))))))
    (dolist (supplied *iso-names*)
      (good-file (concatenate 'string "iso:external-only:" supplied) (octets body) body supplied))
    (good-file "iso:mixed-case-alias" (octets (header "CyRiLlIc" body)) body "iSo-Ir-144")
    ;; Unicode strings are already decoded; their valid header must pass prolog.
    (dolist (alias *iso-names*)
      (multiple-value-bind (map counter)
          (topic-maps.ctm:deserialize-string (header alias body) :document-iri *doc* :wildcard-counter 17)
        (check (concatenate 'string "string-prolog:" alias ":same-value-and-counter")
          (and (= 19 counter) (equal "Россия" (topic-name-value (first (topic-names
            (topic-maps.registered-original.tests::local map *doc* "russia"))))))))))
  (dolist (body (list "russia - \"ASCII\"."
                     (format nil "russia - \"~A\"." (map 'string #'code-char *iso-high*))))
    (good-file (if (find (code-char #xa0) body) "iso:all-A0-FF-in-name" "iso:ASCII-syntax")
               (octets (header "ISO-8859-5" body)) body))
  (let ((body "russia - \"Россия Grüße🙂\"."))
    (dolist (provided (cons nil *utf8-names*))
      (dolist (declared (cons nil *utf8-names*))
        (dolist (bom '(nil t))
          (good-file (format nil "utf8:decl=~A:provided=~A:bom=~A" declared provided bom)
            (concatenate '(vector (unsigned-byte 8)) (if bom #(239 187 191) #())
                         (octets (header declared body) :utf-8)) body provided))))))
(defun negative-tests ()
  (dolist (spec
    (list
      (list "BOM-vs-ISO" (concatenate '(vector (unsigned-byte 8)) #(239 187 191) (octets (header "cyrillic" "russia.") :utf-8) #(255))
            nil 'topic-maps.ctm:ctm-rejection :encoding-conflict 14 :byte)
      (list "external-ISO-vs-BOM" #(239 187 191 255) "iso-ir-144" 'topic-maps.ctm:ctm-rejection :encoding-conflict 0 :byte)
      (list "external-UTF8-vs-ISO-declaration" (octets (header "cyrillic" "russia.")) "csUTF8"
            'topic-maps.ctm:ctm-rejection :encoding-conflict 11 :byte)
      (list "external-ISO-vs-UTF8-declaration" (octets (header "csUTF8" "russia.")) "cyrillic"
            'topic-maps.ctm:ctm-rejection :encoding-conflict 11 :byte)
      (list "unknown-declaration" (octets (header "x-no-such" "russia.")) nil
            'topic-maps.ctm:ctm-unsupported :unsupported-encoding 11 :byte)
      (list "unsupported-declaration" (octets (header "ISO-8859-1" "russia.")) "iso-8859-1"
            'topic-maps.ctm:ctm-unsupported :unsupported-encoding 11 :byte)
      (list "unsupported-external" (octets "russia.") "ISO-8859-1"
            'topic-maps.ctm:ctm-unsupported :unsupported-encoding 0 :byte)
      (list "unknown-external" (octets "russia.") "x-no-such"
            'topic-maps.ctm:ctm-unsupported :unsupported-encoding 0 :byte)
      (list "unregistered-UTF8-name" (octets (header "UTF8" "russia.")) nil
            'topic-maps.ctm:ctm-unsupported :unsupported-encoding 11 :byte)
      (list "unregistered-ISO-name" (octets (header "ISO8859-5" "russia.")) nil
            'topic-maps.ctm:ctm-unsupported :unsupported-encoding 11 :byte)
      (list "ISO-bytes-without-declaration" (octets "russia - \"Россия\".") nil
            'topic-maps.ctm:ctm-rejection :invalid-utf8 10 :byte)
      (list "ISO-bytes-after-UTF8-BOM" (concatenate '(vector (unsigned-byte 8)) #(239 187 191) (octets "russia - \"Россия\".")) nil
            'topic-maps.ctm:ctm-rejection :invalid-utf8 13 :byte)
      (list "encoding-unquoted" (octets "%encoding ISO-8859-5") nil
            'topic-maps.ctm:ctm-rejection :invalid-encoding-declaration 10 :byte)
      (list "encoding-leading-space" (octets " %encoding \"ISO-8859-5\" russia.") nil
            'topic-maps.ctm:ctm-rejection :misplaced-encoding 1 :character)
      (list "encoding-after-version" (octets "%version 1.0 %encoding \"ISO-8859-5\" russia.") "cyrillic"
            'topic-maps.ctm:ctm-rejection :misplaced-encoding 13 :character)
      (list "encoding-after-body" (octets "topic. %encoding \"ISO-8859-5\"") nil
            'topic-maps.ctm:ctm-rejection :misplaced-encoding 7 :character)
      (list "encoding-repeated" (octets "%encoding \"ISO-8859-5\" %encoding \"ISO-8859-5\"") nil
            'topic-maps.ctm:ctm-rejection :misplaced-encoding 23 :character)))
    (apply #'bad-file spec))
  (dolist (charset '("ISO-8859-5" "csUTF8"))
    (let* ((text (header charset (format nil "russia - \"Россия\";~%!.")))
           (encoding (if (equal charset "csUTF8") :utf-8 :iso-8859-5))
           (input (octets text encoding)) (position (position #\! text)) (byte-position (position 33 input))
           (label (concatenate 'string "source-position:" charset)))
      (check (concatenate 'string label ":byte-and-character-offsets-explicit")
        (if (eq encoding :utf-8) (> byte-position position) (= byte-position position)))
      (bad-file label input nil 'topic-maps.ctm:ctm-rejection :unexpected-character position :character 3 1 byte-position)))
  (let* ((text (header "cyrillic" "%version 2.0")) (position (search "2.0" text)))
    (bad-file "version-after-ISO-header" (octets text) nil 'topic-maps.ctm:ctm-rejection :invalid-version position :character 2 10))
  (multiple-value-bind (map condition)
      (captured-read (lambda () (topic-maps.ctm:deserialize-string "%encoding \"x-no-such\"" :document-iri *doc* :source-name "unknown-string-prolog")))
    (check "unknown-string-prolog:not-accepted" (null map))
    (specific "unknown-string-prolog" condition 'topic-maps.ctm:ctm-unsupported :unsupported-encoding 11 :character)))
(defun selection-order-tests ()
  (let ((utf8 (symbol-function 'topic-maps.ctm::decode-utf8))
        (iso (symbol-function 'topic-maps.ctm::decode-iso-8859-5))
        (utf8-calls 0) (iso-calls 0))
    (unwind-protect
      (progn
        (setf (symbol-function 'topic-maps.ctm::decode-utf8) (lambda (&rest args) (incf utf8-calls) (apply utf8 args))
              (symbol-function 'topic-maps.ctm::decode-iso-8859-5) (lambda (&rest args) (incf iso-calls) (apply iso args)))
        (dolist (spec (list (list #(239 187 191 255) "cyrillic" :encoding-conflict)
                            (list (concatenate '(vector (unsigned-byte 8)) #(239 187 191) (octets (header "cyrillic" "")) #(255)) nil :encoding-conflict)
                            (list (octets (header "x-no-such" "")) nil :unsupported-encoding)))
          (destructuring-bind (input supplied code) spec
            (let ((condition (nth-value 1 (captured-read (lambda () (topic-maps.ctm::decode-ctm-octets input :encoding supplied))))))
              (check (format nil "selection:~A:provided=~A:both-codecs-unreached" code supplied)
                (and condition (eq code (topic-maps.ctm:error-code condition)) (= 0 utf8-calls iso-calls))))))
        (setf *selection* (fields "conflictAndUnsupportedUTF8Calls" utf8-calls "conflictAndUnsupportedISOCalls" iso-calls))
        (topic-maps.ctm::decode-ctm-octets (octets "abc") :encoding "cyrillic")
        (check "selection:ISO-only-one-call" (and (= 1 iso-calls) (zerop utf8-calls)))
        (topic-maps.ctm::decode-ctm-octets (octets "abc" :utf-8))
        (check "selection:default-UTF8-only-one-call" (= 1 iso-calls utf8-calls)))
      (setf (symbol-function 'topic-maps.ctm::decode-utf8) utf8
            (symbol-function 'topic-maps.ctm::decode-iso-8859-5) iso))))
(defun resource-tests ()
  (dolist (purpose '(:include :mergemap))
    (dolist (generic '(nil t))
      (let* ((label (format nil "resource:~A:generic=~A" purpose generic))
             (parent (concatenate 'string (if (eq purpose :include) "%include <child.ctm>"
               "%mergemap <child.ctm> <http://psi.topicmaps.org/iso13250/ctm>") " ? - \"Parent\"."))
             (body "russia - \"Россия\". ? - \"Child\". ?named - \"Щ\".")
             (bytes (octets (header "cyrillic" body)))
             (payload (if generic (coerce bytes 'simple-vector) bytes))
             (before (copy-seq payload)) (calls 0) (decoder-calls 0)
             (saved (symbol-function 'topic-maps.ctm::decode-ctm-resource)) (map nil) (counter nil))
        (flet ((resolver (iri &key purpose from-document-iri notation)
                 (assert (equal iri *child*)) (assert (equal from-document-iri *doc*))
                 (assert (if (eq purpose :include) (null notation) (equal notation "http://psi.topicmaps.org/iso13250/ctm")))
                 (incf calls) (values payload "source:iso-child")))
          (unwind-protect
            (progn
              (setf (symbol-function 'topic-maps.ctm::decode-ctm-resource)
                (lambda (raw source)
                  (assert (eq raw payload)) (assert (equal source "source:iso-child")) (incf decoder-calls)
                  (funcall saved raw source)))
              (multiple-value-setq (map counter)
                (topic-maps.ctm:deserialize-string parent :document-iri *doc* :source-name label
                                                  :wildcard-counter 17 :resource-resolver #'resolver)))
            (setf (symbol-function 'topic-maps.ctm::decode-ctm-resource) saved)))
        (let* ((reference-bytes (octets body :utf-8))
               (reference (topic-maps.ctm:deserialize-string parent :document-iri *doc* :wildcard-counter 17
                 :resource-resolver (lambda (&rest args) (declare (ignore args)) (values reference-bytes "source:utf8-reference"))))
               (owner (topic-maps.registered-original.tests::local map *child* "russia")))
          (check (concatenate 'string label ":raw-bytes-model-identities-and-counter")
            (and (= calls 1 decoder-calls) (equalp before payload)
                 (equal "Россия" (topic-name-value (first (topic-names owner))))
                 (= counter (if (eq purpose :include) 20 18))
                 (if (eq purpose :include)
                     (member (concatenate 'string *doc* "#russia") (topic-item-identifiers owner) :test #'equal)
                     (not (member (concatenate 'string *doc* "#russia") (topic-item-identifiers owner) :test #'equal)))
                 (equalp (canonical map) (canonical reference)))))
        (observe-positive label map counter payload)
        (dolist (spec
          (list (list "conflict" (concatenate '(vector (unsigned-byte 8)) #(239 187 191) (octets (header "cyrillic" ""))) 'topic-maps.ctm:ctm-rejection :encoding-conflict 14 :byte)
                (list "unsupported" (octets (header "ISO-8859-1" "")) 'topic-maps.ctm:ctm-unsupported :unsupported-encoding 11 :byte)
                (list "invalid-default-UTF8" (octets "russia - \"Россия\".") 'topic-maps.ctm:ctm-rejection :invalid-utf8 10 :byte)))
          (destructuring-bind (suffix input class code position unit) spec
            (let* ((key (concatenate 'string label ":" suffix))
                   (condition (nth-value 1 (captured-read (lambda ()
                     (topic-maps.ctm:deserialize-string parent :document-iri *doc* :source-name key
                       :resource-resolver (lambda (&rest args) (declare (ignore args)) (values input "source:bad-child"))))))))
              (specific key condition class code position unit "source:bad-child" purpose)))))))
  ;; An external parent charset never leaks into a child resource's default.
  (let* ((parent "%include <child.ctm>") (child (octets "russia - \"Россия🙂\"." :utf-8)))
    (multiple-value-bind (map counter condition)
        (file-values "resource:external-parent-child-default-UTF8" (octets parent) "cyrillic"
                     (lambda (&rest args) (declare (ignore args)) (values child "source:UTF8-child")))
      (check "resource:external-parent-encoding-not-inherited"
        (and (null condition) (= counter 17)
             (equal "Россия🙂" (topic-name-value (first (topic-names
               (topic-maps.registered-original.tests::local map *child* "russia")))))))
      (observe-positive "resource:external-parent-child-default-UTF8" map counter child "cyrillic"))))
(defun original-contract ()
  (let* ((corpus topic-maps.ctm.tests::*cxtm-corpus*) (root (topic-maps.test-foundation:corpus-root corpus))
         (id "ctm/in/encoding-8859-5.ctm") (selected (topic-maps.test-foundation:select-cases corpus :id id))
         (case (first selected)) (cases (topic-maps.test-foundation:corpus-cases corpus))
         (previous (mapcar (lambda (c) (cons c (case-state c))) cases))
         (old-results (copy-tree topic-maps.ctm.tests::*cxtm-results*))
         (*doc* (topic-maps.test-foundation:test-case-document-iri case)))
    (setf *entry-statuses* (copy-list (getf (topic-maps.test-foundation:summarize-corpus corpus) :statuses)))
    (check "original:existing-positive-NOT-RUN-record-and-Document-IRI"
      (and (= 1 (length selected)) (member case cases :test #'eq)
           (eq :valid (topic-maps.test-foundation:test-case-category case))
           (eq :cxtm-equal (topic-maps.test-foundation:test-case-expected-outcome case))
           (eq :not-run (topic-maps.test-foundation:test-case-status case))
           (null (topic-maps.test-foundation:test-case-actual-outcome case))
           (equal (truename (merge-pathnames id root)) (truename (topic-maps.test-foundation:test-case-source-pathname case)))
           (equal *doc* (format nil "https://ctm-tests.example.invalid/~A/~A" (getf (topic-maps.test-foundation:corpus-metadata corpus) :commit) id))))
    (check "original:unchanged-42-octets"
      (equalp (binary (topic-maps.test-foundation:test-case-source-pathname case))
              (concatenate '(vector (unsigned-byte 8)) (octets (format nil "%encoding \"iso-8859-5\"~%russia - \"") :utf-8)
                           #(192 222 225 225 216 239) (octets "\" ." :utf-8))))
    (multiple-value-bind (row result) (topic-maps.registered-original.tests::exercise-case case :escapes)
      (setf *original* row)
      (check "original:actual-pinned-CXTM-comparison-PASS"
        (and result (getf result :match)
             (= (length (binary (topic-maps.test-foundation:test-case-expected-baseline case))) (getf result :bytes))
             (eq :pass (topic-maps.test-foundation:test-case-status case))))
      (let* ((control (topic-maps.ctm:deserialize-string "russia - \"Россия\" ." :document-iri *doc*))
             (name (first (topic-names (topic-maps.registered-original.tests::local control *doc* "russia")))))
        (check "original:Unicode-name-and-UTF8-reference-baseline"
          (and (equal "Россия" (topic-name-value name))
               (equalp (canonical control) (binary (topic-maps.test-foundation:test-case-expected-baseline case))))))
      (check "original:all-prior-records-and-observations-preserved"
        (and (eq corpus topic-maps.ctm.tests::*cxtm-corpus*) (equal cases (topic-maps.test-foundation:corpus-cases corpus))
             (equal old-results topic-maps.ctm.tests::*cxtm-results*)
             (every (lambda (entry) (if (eq case (car entry)) (equal (first (cdr entry)) (identity-fields case))
                                        (equal (cdr entry) (case-state (car entry))))) previous)))
      (setf topic-maps.ctm.tests::*cxtm-results* (append old-results (list result))))
    (let ((after (getf (topic-maps.test-foundation:summarize-corpus corpus) :statuses)))
      (check "original:exactly-one-NOT-RUN-to-PASS"
        (and (= (1+ (getf *entry-statuses* :pass)) (getf after :pass))
             (= (1- (getf *entry-statuses* :not-run)) (getf after :not-run))
             (= (getf *entry-statuses* :fail) (getf after :fail))
             (= (getf *entry-statuses* :unsupported) (getf after :unsupported)))))
    (format t "~&ENCODING-ORIGINAL ~A: PASS; ~D byte-exact CXTM bytes~%" id
            (length (binary (topic-maps.test-foundation:test-case-expected-baseline case))))))
(defun run-tests ()
  (unless topic-maps.ctm.tests::*cxtm-corpus*
    (topic-maps.registered-original.tests:run-tests) (topic-maps.registered-original.tests:run-negative-tests)
    (topic-maps.prolog.tests:run-tests) (topic-maps.registered-original.tests:run-empty2-tests)
    (topic-maps.ctm-integer.tests:run-tests) (topic-maps.triple.tests:run-tests))
  (setf *positives* nil *negatives* nil *original* nil)
  (let ((topic-maps.registered-original.tests::*checks* nil))
    (decoder-table-tests) (alias-and-model-tests) (negative-tests) (selection-order-tests) (resource-tests) (original-contract)
    (check "encoding:unique-check-names"
      (= (length topic-maps.registered-original.tests::*checks*)
         (length (remove-duplicates topic-maps.registered-original.tests::*checks* :test #'equal))))
    (setf *checks* (nreverse topic-maps.registered-original.tests::*checks*)))
  (setf *positives* (nreverse *positives*) *negatives* (nreverse *negatives*))
  (format t "~&ENCODING-PASS: ~D checks; 256 byte mappings, one original, ~D positive and ~D negative controls~%"
          (length *checks*) (length *positives*) (length *negatives*)) t)
(defun write-reports (prefix)
  (with-open-file (out (concatenate 'string prefix ".encoding.json") :direction :output :if-exists :supersede)
    (topic-maps.test-foundation::emit-json-value
      (fields "kind" "ctm-iso-8859-5-execution" "passed" (length *checks*) "failed" 0
              "entryStatuses" (topic-maps.test-foundation::counts-object *entry-statuses*)
              "checks" (coerce *checks* 'vector) "positives" (coerce *positives* 'vector)
              "negativeControls" (coerce *negatives* 'vector) "decoderCodepoints" *codepoints* "selectionEvidence" *selection*
              "ISO88595Names" (coerce *iso-names* 'vector) "UTF8Names" (coerce *utf8-names* 'vector) "original" *original*) out) (terpri out))
  (topic-maps.ctm.tests::write-cxtm-report
    (concatenate 'string prefix ".validation.json") (concatenate 'string prefix ".cxtm.json")
    :additional-checks *checks*
    :scope "Slice 20H: ISO-8859-5 original, all 256 byte mappings and IANA aliases; encoding conflicts before decoding, unchanged UTF-8, Document IRIs/Wildcards and explicit Include/Mergemap resource bytes. Prior contracts and four known FAILs preserved."))
