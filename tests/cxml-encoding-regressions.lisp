;;;; Additional checks. The original 58 check names/expectations are retained.
(in-package #:topic-maps.cxml-probe)

(defun encoded-document (encoding content &key bom (declaration "UTF-8"))
  (octets (if declaration
              (format nil "<?xml version='1.0' encoding='~A'?><r>~A</r>" declaration content)
              (format nil "<r>~A</r>" content))
          encoding bom))

(defun bad-content (name content encoding &key bom declaration)
  (let* ((header (if declaration
                     (format nil "<?xml version='1.0' encoding='~A'?><r>" declaration)
                     "<r>"))
         (input (concatenate '(vector (unsigned-byte 8))
                             (octets header encoding bom) content (octets "</r>" encoding))))
    (expect-condition name 'cxml:well-formedness-violation
                      (lambda () (parse-bytes input)))))

(dolist (spec '(("stray-continuation" 128)
                ("bad-continuation" 195 40)
                ("overlong-two" 192 175)
                ("overlong-three" 224 128 175)
                ("overlong-four" 240 128 128 175)
                ("encoded-surrogate" 237 160 128)
                ("above-unicode-limit" 244 144 128 128)
                ("illegal-leading-f5" 245 128 128 128)
                ("obsolete-five-byte-form" 248 128 128 128 175)
                ("obsolete-six-byte-form" 252 128 128 128 128 175)
                ("illegal-leading-ff" 255)))
  (bad-content (concatenate 'string "utf8-invalid:" (car spec))
               (coerce (cdr spec) '(vector (unsigned-byte 8))) :utf-8))

;; EOF is deliberately inside a sequence, rather than followed by XML markup.
(dolist (bytes '(#(194) #(224 160) #(240 159 166)))
  (expect-condition (format nil "utf8-truncated:~{~2,'0X~}" (coerce bytes 'list))
                    'cxml:well-formedness-violation
                    (lambda () (parse-bytes (concatenate '(vector (unsigned-byte 8))
                                              (octets "<r>") bytes)))))

(dolist (encoding '(:utf-16le :utf-16be))
  (let* ((le (eq encoding :utf-16le))
         (label (if le "le" "be")))
    (dolist (spec (if le
                      '(("isolated-low" 0 220) ("high-then-letter" 0 216 65 0)
                        ("high-then-high" 0 216 0 216))
                      '(("isolated-low" 220 0) ("high-then-letter" 216 0 0 65)
                        ("high-then-high" 216 0 216 0))))
      (bad-content (concatenate 'string "utf16-invalid:" label ":" (car spec))
                   (coerce (cdr spec) '(vector (unsigned-byte 8))) encoding :bom t))
    (dolist (spec (if le '(("odd-octet" 65) ("unfinished-high" 0 216))
                         '(("odd-octet" 65) ("unfinished-high" 216 0))))
      (expect-condition (concatenate 'string "utf16-truncated:" label ":" (car spec))
                        'cxml:well-formedness-violation
                        (lambda () (parse-bytes (concatenate '(vector (unsigned-byte 8))
                                                  (octets "<r>" encoding t)
                                                  (coerce (cdr spec) '(vector (unsigned-byte 8))))))))))

(dolist (encoding '(:utf-8 :utf-16le :utf-16be))
  (let* ((bom (not (eq encoding :utf-8)))
         (declaration (if bom "UTF-16" "UTF-8"))
         (characters (coerce (mapcar #'code-char '(#xD7FF #xE000 #xFFFD #x10000 #x10FFFF)) 'string)))
    (check-decoded-text (format nil "scalar-boundaries:~A" encoding)
                        (encoded-document encoding characters :bom bom :declaration declaration)
                        characters)
    (check-decoded-text (format nil "line-ending-normalization:~A" encoding)
                        (encoded-document encoding (format nil "a~C~Cb~Cc" #\Return #\Newline #\Return)
                                          :bom bom :declaration declaration)
                        (format nil "a~%b~%c"))
    ;; Cross the parser's 8192-byte refill with a multi-unit scalar.
    (dolist (length '(8189 8190 8191 8192))
      (let ((content (concatenate 'string (make-string length :initial-element #\x) "🦊水")))
        (check-decoded-text (format nil "refill:~A:~D" encoding length)
                            (encoded-document encoding content :bom bom :declaration declaration)
                            content)))))

;; Signatures alone do not authorize silently treating generic UTF-16 as LE/BE.
(dolist (encoding '(:utf-16le :utf-16be))
  (dolist (declaration '("UTF-16" nil "UTF-8"))
    (let ((source (if declaration
                      (format nil "<?xml version='1.0' encoding='~A'?><r/>" declaration)
                      "<?xml version='1.0'?><r/>")))
      (expect-condition (format nil "bomless-missing-or-wrong-label:~A:~A" encoding declaration)
                        'cxml:well-formedness-violation
                        (lambda () (parse-bytes (octets source encoding))))))
  (expect-condition (format nil "bomless-without-declaration:~A" encoding)
                    'cxml:well-formedness-violation
                    (lambda () (parse-bytes (octets "<r/>" encoding))))
  (expect-condition (format nil "bomless-pi-without-xml-declaration:~A" encoding)
                    'cxml:well-formedness-violation
                    (lambda () (parse-bytes (octets "<?pi?><r/>" encoding))))
  (expect-condition (format nil "bom-declaration-disagreement:~A" encoding)
                    'cxml:well-formedness-violation
                    (lambda () (parse-bytes (encoded-document encoding "x" :bom t :declaration "UTF-8"))))
  (expect-condition (format nil "opposite-endian-declaration:~A" encoding)
                    'cxml:well-formedness-violation
                    (lambda () (parse-bytes (encoded-document encoding "x"
                                              :declaration (if (eq encoding :utf-16le) "UTF-16BE" "UTF-16LE")))))
  (expect-condition (format nil "explicit-endian-label-with-bom:~A" encoding)
                    'cxml:well-formedness-violation
                    (lambda () (parse-bytes (encoded-document encoding "x" :bom t
                                              :declaration (if (eq encoding :utf-16le) "UTF-16LE" "UTF-16BE"))))))
(dolist (declaration '("UTF-16" "UTF-16LE" "UTF-16BE" "ISO-8859-1"))
  (expect-condition (concatenate 'string "utf8-bom-wrong-declaration:" declaration)
                    'cxml:well-formedness-violation
                    (lambda () (parse-bytes (encoded-document :utf-8 "x" :bom t :declaration declaration)))))
(expect-condition "unknown-encoding-is-fatal" 'cxml:well-formedness-violation
                  (lambda () (parse-bytes (encoded-document :utf-8 "x" :declaration "x-not-a-real-encoding"))))
(check-decoded-text "encoding-name-case-insensitive"
                    (encoded-document :utf-16le "🦊" :declaration "utf-16le") "🦊")

;; The public boundary enforces the policy even for a permissive SAX receiver.
(expect-condition "public-api-rejects-string-input" 'type-error
                  (lambda () (topic-maps.xml:parse-octets "<r/>" nil)))
(expect-condition "public-api-no-resolver-override" 'program-error
                  (lambda () (uiop:symbol-call :topic-maps.xml :parse-octets
                                               (octets "<r/>") nil :entity-resolver (constantly nil))))
(expect-condition "public-api-guard-with-nil-handler" 'topic-maps.xml:doctype-forbidden
                  (lambda () (topic-maps.xml:parse-octets
                              (octets "<!DOCTYPE r SYSTEM 'file:///tmp/must-not-open'><r/>") nil)))
(expect-condition "public-resolver-signals" 'topic-maps.xml:external-resource-forbidden
                  (lambda () (topic-maps.xml::deny-external-resource
                              nil (puri:parse-uri "http://127.0.0.1:9/must-not-fetch"))))
(let ((original (symbol-value 'cxml::*topic-maps-encoding-patch*)))
  (unwind-protect
       (progn
         (setf (symbol-value 'cxml::*topic-maps-encoding-patch*) nil)
         (expect-condition "public-api-refuses-unqualified-dependency" 'topic-maps.xml:unqualified-parser
                           (lambda () (topic-maps.xml:parse-octets (octets "<r/>") nil))))
    (setf (symbol-value 'cxml::*topic-maps-encoding-patch*) original)))
(let ((handler (make-instance 'observation)))
  (check "public-api-returns-identical-sax-result"
         (eq handler (topic-maps.xml:parse-octets (octets "<r/>") handler))))

;; Exercise the existing decoder's partial-input contract (no second decoder).
(dolist (encoding '(:utf-8 :utf-16-little-endian :utf-16-big-endian))
  (let* ((input (octets "🦊" (ecase encoding (:utf-8 :utf-8)
                              (:utf-16-little-endian :utf-16le)
                              (:utf-16-big-endian :utf-16be))))
         (output (make-array 8 :element-type '(unsigned-byte 32))))
    (dolist (end '(1 2 3))
      (multiple-value-bind (written read)
          (runes-encoding:decode-sequence encoding input 0 end output 0 8 nil)
        (check (format nil "decoder-needs-more:~A:~D" encoding end)
               (and (zerop written) (zerop read))))
      (expect-condition (format nil "decoder-incomplete-at-eof:~A:~D" encoding end)
                        'runes-encoding:encoding-error
                        (lambda () (runes-encoding:decode-sequence encoding input 0 end output 0 8 t))))))
