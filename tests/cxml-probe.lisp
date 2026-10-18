;;;; Slice 19D0: parser qualification only; no XTM deserializer or model.
(require :asdf)
(setf *compile-verbose* nil *load-verbose* nil)
(assert (string= (lisp-implementation-version) "2.5.4"))
(assert (asdf:find-system "cxml" nil))
(asdf:load-system "cxml")

(defpackage #:topic-maps.cxml-probe (:use #:cl))
(in-package #:topic-maps.cxml-probe)

(defvar *checks* nil)
(defvar *failed-checks* nil)
(defvar *resolver-calls* nil)
(defvar *fallback-calls* 0)

(defun check (name truth)
  (push name *checks*)
  (unless truth (push name *failed-checks*))
  (format t "CXML-CHECK-~A ~A~%" (if truth "PASS" "FAIL") name))

(defun expect-condition (name class thunk)
  ;; An I/O failure or a different generic exception is never a PASS.
  (let ((condition (handler-case (progn (funcall thunk) nil)
                     (error (c) c))))
    (check name (typep condition class))
    (format t "CXML-REJECTION ~A ~A~%" name (type-of condition))))

(define-condition doctype-forbidden (error) ())
(define-condition external-resource-forbidden (error)
  ((system-id :initarg :system-id :reader denied-system-id)))
(define-condition fallback-reached (error) ())

(defclass observation (sax:default-handler)
  ((elements :initform nil :accessor elements)
   (text :initform "" :accessor text)
   ;; Enabled only in tests that exercise the resolver defense separately.
   (allow-doctype :initform nil :initarg :allow-doctype :reader allow-doctype)))

(defmethod sax:start-element ((handler observation) uri local qname attributes)
  (push (list uri local qname
              (mapcar (lambda (a)
                        (list (sax:attribute-namespace-uri a)
                              (sax:attribute-local-name a)
                              (sax:attribute-qname a) (sax:attribute-value a)))
                      attributes))
        (elements handler)))

(defmethod sax:characters ((handler observation) data)
  (setf (text handler) (concatenate 'string (text handler) data)))

(defmethod sax:end-document ((handler observation)) handler)

(defmethod sax:start-dtd ((handler observation) name public-id system-id)
  (declare (ignore name public-id system-id))
  (unless (allow-doctype handler) (error 'doctype-forbidden)))

(defun deny-external-resource (public-id system-id)
  (declare (ignore public-id))
  (push (puri:render-uri system-id nil) *resolver-calls*)
  ;; NIL would permit CXML's file-opening fallback (xml-parse.lisp:1064).
  (error 'external-resource-forbidden :system-id system-id))

(defun parse-bytes (bytes &key resolver-probe)
  (let ((sax:*namespace-processing* t)
        (sax:*include-xmlns-attributes* nil)
        (cxml:*catalog* nil)
        (cxml:*cache-all-dtds* nil)
        (cxml:*dtd-cache* (cxml:make-dtd-cache)))
    (cxml:parse-octets
     bytes (make-instance 'observation :allow-doctype resolver-probe)
     :validate nil :disallow-internal-subset (not resolver-probe)
     :entity-resolver #'deny-external-resource)))

(defun octets (string &optional (encoding :utf-8) bom)
  ;; Explicit BOM bytes: Babel's endian-specific encoders do not supply a
  ;; BOM vector for :USE-BOM T. Encoding itself stays with the existing library.
  (concatenate '(vector (unsigned-byte 8))
               (if bom (ecase encoding
                         (:utf-8 #(239 187 191))
                         (:utf-16le #(255 254))
                         (:utf-16be #(254 255))) #())
               (babel:string-to-octets string :encoding encoding :use-bom nil)))

(defun parse-text (string) (parse-bytes (octets string)))

(defun check-decoded-text (name bytes expected)
  (handler-case (check name (string= (text (parse-bytes bytes)) expected))
    (error (c)
      (check name nil)
      (format t "CXML-UNEXPECTED-REJECTION ~A ~A: ~A~%" name (type-of c) c))))

(check "asdf-cxml-found-and-loaded" (find-package :cxml))
(dolist (name '("closure-common" "puri" "babel" "alexandria"
                "trivial-features" "trivial-gray-streams"))
  (check (concatenate 'string "asdf-dependency:" name)
         (asdf:component-loaded-p (asdf:find-system name))))

(let* ((source "<x:root xmlns:x='urn:element' xmlns:y='urn:attr' plain='v' y:a='ä'>🦊</x:root>")
       (doc (parse-text source))
       (root (first (elements doc))))
  (check "namespace-expanded-element" (equal (subseq root 0 3) '("urn:element" "root" "x:root")))
  (check "unprefixed-attribute-has-no-namespace"
         (member '(nil "plain" "plain" "v") (fourth root) :test #'equal))
  (check "prefixed-attribute-namespace"
         (member '("urn:attr" "a" "y:a" "ä") (fourth root) :test #'equal))
  (check "unicode-astral-character" (string= (text doc) "🦊")))
(let ((roots (reverse (elements (parse-text "<r xmlns='urn:a'><s xmlns='urn:b'/><t/></r>")))))
  (check "default-namespace-and-nested-rebinding"
         (equal (mapcar #'first roots) '("urn:a" "urn:b" "urn:a"))))

(dolist (spec '(("utf8-no-bom" :utf-8 nil "UTF-8")
                ("utf8-bom" :utf-8 t "UTF-8")
                ("utf16le-bom" :utf-16le t "UTF-16")
                ("utf16be-bom" :utf-16be t "UTF-16")
                ("utf16le-explicit-no-bom" :utf-16le nil "UTF-16LE")
                ("utf16be-explicit-no-bom" :utf-16be nil "UTF-16BE")))
  (destructuring-bind (name encoding bom declaration) spec
    (dolist (content '("Grüße 水" "Grüße 水 🦊"))
      (let ((source (format nil "<?xml version='1.0' encoding='~A'?><r>~A</r>" declaration content)))
        (check-decoded-text (concatenate 'string name (if (find #\🦊 content) ":astral" ":bmp"))
                            (octets source encoding bom) content)))))
(check-decoded-text "utf16-bom-without-declaration:bmp"
                    (octets "<r>水</r>" :utf-16le t) "水")
(check-decoded-text "utf16-bom-without-declaration:astral"
                    (octets "<r>水🦊</r>" :utf-16le t) "水🦊")
(check "predefined-entities-and-character-references"
       (string= (text (parse-text "<r>&lt;&gt;&amp;&quot;&apos;&#xE4;&#x1F98A;</r>")) "<>&\"'ä🦊"))
(check "xml-line-end-normalization"
       (string= (text (parse-text (format nil "<r>a~C~Cb~Cc</r>" #\Return #\Newline #\Return)))
                (format nil "a~%b~%c")))
(check "xml-attribute-whitespace-normalization"
       (equal (fourth (first (elements (parse-text (format nil "<r a='a~Cb~Cc'/>" #\Tab #\Newline)))))
              '((nil "a" "a" "a b c"))))

(dolist (pair '(("misnested" . "<r><a></r>")
                ("duplicate-attribute" . "<r a='1' a='2'/>")
                ("duplicate-expanded-attribute" . "<r xmlns:a='urn:x' xmlns:b='urn:x' a:v='1' b:v='2'/>")
                ("undeclared-prefix" . "<q:r/>")
                ("multiple-roots" . "<r/><s/>")
                ("unclosed-root" . "<r>")
                ("undefined-entity" . "<r>&missing;</r>")
                ("forbidden-nul-reference" . "<r>&#0;</r>")
                ("forbidden-surrogate-reference" . "<r>&#xD800;</r>")))
  (expect-condition (car pair) 'cxml:well-formedness-violation
                    (lambda () (parse-text (cdr pair)))))
(expect-condition "invalid-utf8" 'cxml:well-formedness-violation
                  (lambda () (parse-bytes (concatenate '(vector (unsigned-byte 8))
                                           (octets "<r>") #(195 40) (octets "</r>")))))
(handler-case
    (format t "CXML-OBSERVATION invalid-utf8 decoded:~{ U+~4,'0X~}~%"
            (map 'list #'char-code
                 (text (parse-bytes (concatenate '(vector (unsigned-byte 8))
                                      (octets "<r>") #(195 40) (octets "</r>"))))))
  (cxml:well-formedness-violation () nil))

;; Every DOCTYPE is deliberately outside the selected safe input policy.
(dolist (pair '(("doctype-without-subset" . "<!DOCTYPE r><r/>")
                ("internal-entity" . "<!DOCTYPE r [<!ENTITY e 'value'>]><r>&e;</r>")
                ("external-file-dtd" . "<!DOCTYPE r SYSTEM 'file:///tmp/cxml-must-not-read.dtd'><r/>")
                ("external-network-dtd" . "<!DOCTYPE r SYSTEM 'http://127.0.0.1:9/must-not-fetch.dtd'><r/>")
                ("external-general-entity" . "<!DOCTYPE r [<!ENTITY e SYSTEM 'file:///tmp/cxml-must-not-read'>]><r>&e;</r>")
                ("external-parameter-entity" . "<!DOCTYPE r [<!ENTITY % e SYSTEM 'file:///tmp/cxml-must-not-read'>%e;]><r/>")))
  (expect-condition (car pair) 'doctype-forbidden
                    (lambda () (parse-text (cdr pair)))))
(check "safe-policy-never-invokes-external-resolver" (null *resolver-calls*))

;; Exercise the second defense without the DOCTYPE guard. Trap the exact
;; CXML fallback before it can turn a URI into a pathname and call OPEN.
;; This test-only interception is restored in this disposable process.
(let ((original (fdefinition 'cxml::uri-to-pathname)))
  (unwind-protect
       (progn
         (setf (fdefinition 'cxml::uri-to-pathname)
               (lambda (uri) (declare (ignore uri))
                 (incf *fallback-calls*) (error 'fallback-reached)))
         (dolist (pair '(("resolver-file-dtd" . "<!DOCTYPE r SYSTEM 'file:///tmp/cxml-must-not-read.dtd'><r/>")
                         ("resolver-network-dtd" . "<!DOCTYPE r SYSTEM 'http://127.0.0.1:9/must-not-fetch.dtd'><r/>")
                         ("resolver-file-entity" . "<!DOCTYPE r [<!ENTITY e SYSTEM 'file:///tmp/cxml-must-not-read'>]><r>&e;</r>")
                         ("resolver-network-entity" . "<!DOCTYPE r [<!ENTITY e SYSTEM 'http://127.0.0.1:9/must-not-fetch'>]><r>&e;</r>")
                         ("resolver-parameter-entity" . "<!DOCTYPE r [<!ENTITY % e SYSTEM 'file:///tmp/cxml-must-not-read'>%e;]><r/>")))
           (let ((before (length *resolver-calls*)))
             (expect-condition (car pair) 'external-resource-forbidden
                               (lambda () (parse-bytes (octets (cdr pair)) :resolver-probe t)))
             (check (concatenate 'string (car pair) ":called")
                    (= (length *resolver-calls*) (1+ before)))))
         ;; Counterprobe: returning NIL really would reach the fallback.
         (expect-condition "nil-resolver-reaches-cxml-fallback" 'fallback-reached
                           (lambda ()
                             (cxml:parse-octets
                              (octets "<!DOCTYPE r SYSTEM 'file:///tmp/cxml-must-not-read.dtd'><r/>")
                              (make-instance 'observation :allow-doctype t)
                              :entity-resolver (lambda (public system)
                                                 (declare (ignore public system)) nil))))
         (check "exactly-one-fallback-only-in-nil-counterprobe" (= *fallback-calls* 1)))
    (setf (fdefinition 'cxml::uri-to-pathname) original)))

(format t "CXML-SUMMARY ~D PASS ~D FAIL~%"
        (- (length *checks*) (length *failed-checks*)) (length *failed-checks*))
(when *failed-checks* (uiop:quit 1))
