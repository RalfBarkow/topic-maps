(in-package #:topic-maps.ctm)

(defun scalar-character (code position)
  (unless (and (<= 0 code #x10ffff) (not (<= #xd800 code #xdfff)))
    (problem 'ctm-rejection :invalid-unicode position "Not a Unicode scalar value."))
  (or (code-char code)
      (problem 'ctm-unsupported :character-repertoire position
               "The Common Lisp implementation cannot represent this Unicode character.")))

(defun decode-utf8 (octets &key (position 0) (strip-bom nil))
  "Strict UTF-8 decoding without implementation-specific external-format flags."
  (let* ((size (length octets))
         (i (if (and strip-bom (>= size 3)
                     (= (aref octets 0) #xef) (= (aref octets 1) #xbb)
                     (= (aref octets 2) #xbf)) 3 0)))
    (with-output-to-string (output)
      (loop while (< i size) do
        (let* ((first (aref octets i))
               (width (cond ((< first #x80) 1) ((<= #xc2 first #xdf) 2)
                            ((<= #xe0 first #xef) 3) ((<= #xf0 first #xf4) 4)
                            (t 0))))
          (when (or (zerop width) (> (+ i width) size))
            (problem 'ctm-rejection :invalid-utf8 (+ position i)
                     "Invalid or incomplete UTF-8 sequence." :byte))
          (let ((code (logand first (ecase width (1 #x7f) (2 #x1f) (3 #x0f) (4 #x07)))))
            (loop for j from 1 below width for byte = (aref octets (+ i j)) do
              (unless (<= #x80 byte #xbf)
                (problem 'ctm-rejection :invalid-utf8 (+ position i j)
                         "Expected UTF-8 continuation byte." :byte))
              (setf code (+ (ash code 6) (logand byte #x3f))))
            (unless (and (>= code (ecase width (1 0) (2 #x80) (3 #x800) (4 #x10000)))
                         (<= code #x10ffff) (not (<= #xd800 code #xdfff)))
              (problem 'ctm-rejection :invalid-utf8 (+ position i)
                       "Overlong or invalid Unicode UTF-8 sequence." :byte))
            (write-char (scalar-character code (+ position i)) output))
          (incf i width))))))

(defun unescape-iri (text position)
  "CTM 3.3.3: decode consecutive percent octets as UTF-8, preserving other chars."
  (with-output-to-string (out)
    (loop for i from 0 below (length text) do
      (if (char= (char text i) #\%)
          (let ((bytes nil) (start i))
            (loop while (and (< i (length text)) (char= (char text i) #\%)) do
              (unless (< (+ i 2) (length text))
                (problem 'ctm-rejection :invalid-percent-escape (+ position i) "Incomplete IRI escape."))
              (let ((a (digit-char-p (char text (1+ i)) 16))
                    (b (digit-char-p (char text (+ i 2)) 16)))
                (unless (and a b)
                  (problem 'ctm-rejection :invalid-percent-escape (+ position i) "IRI escape needs two hex digits."))
                (push (+ (* 16 a) b) bytes))
              (incf i 3))
            (write-string (decode-utf8 (coerce (nreverse bytes) '(vector (unsigned-byte 8)))
                                       :position (+ position start)) out)
            (decf i))
          (write-char (char text i) out)))))


;; Inspect the ASCII header before decoding (CTM 3.2). The strict UTF-8
;; decoder above is unchanged; only the qualified ISO-8859-5 path is added.
(defun ctm-unit-code (sequence position)
  (let ((value (aref sequence position)))
    (if (characterp value) (char-code value) value)))

(defun ctm-ascii-prefix-p (sequence position prefix)
  (and (<= (+ position (length prefix)) (length sequence))
       (loop for c across prefix for i from position
             always (= (char-code c) (ctm-unit-code sequence i)))))

(defun ctm-encoding-name (sequence position unit)
  "Return the ASCII charset name, end after its quote, and name position.
CTM 3.2/3.6 permits only SP/TAB before this initial header's opening quote."
  (let ((cursor (+ position (length "%encoding"))) (size (length sequence)))
    (loop while (and (< cursor size) (member (ctm-unit-code sequence cursor) '(9 32))) do (incf cursor))
    (unless (and (< cursor size) (= 34 (ctm-unit-code sequence cursor)))
      (problem 'ctm-rejection :invalid-encoding-declaration cursor "Expected an encoding name in double quotes." unit))
    (let ((start (incf cursor)))
      (loop while (and (< cursor size) (/= 34 (ctm-unit-code sequence cursor))) do
        (unless (and (<= 33 (ctm-unit-code sequence cursor) 126)
                     (/= 92 (ctm-unit-code sequence cursor)))
          (problem 'ctm-rejection :invalid-encoding-declaration cursor "Expected an ASCII charset name." unit))
        (incf cursor))
      (unless (and (< cursor size) (> cursor start))
        (problem 'ctm-rejection :invalid-encoding-declaration cursor "Encoding name must be nonempty and have a closing quote." unit))
      (values (map 'string (lambda (value) (if (characterp value) value (code-char value)))
                   (subseq sequence start cursor)) (1+ cursor) start))))

(defun ctm-encoding-kind (name)
  "Only the IANA identities implemented here; ASCII names are case-insensitive."
  (cond ((member name '("UTF-8" "csUTF8") :test #'string-equal) :utf-8)
        ((member name '("ISO-8859-5" "ISO_8859-5:1988" "ISO_8859-5"
                       "iso-ir-144" "cyrillic" "csISOLatinCyrillic")
                 :test #'string-equal) :iso-8859-5)))

(defun ctm-encoding-identity (name)
  (or (ctm-encoding-kind name) (string-downcase name)))

(defun decode-iso-8859-5 (bytes)
  "SBCL's existing total single-byte codec, qualified against all 256 values."
  #+sbcl
  (sb-ext:octets-to-string (map '(vector (unsigned-byte 8)) #'identity bytes)
                          :external-format :iso-8859-5)
  #-sbcl
  (problem 'ctm-unsupported :unsupported-encoding 0
           "ISO-8859-5 decoding is qualified only on SBCL." :byte))

(defun compatible-ctm-encoding (current declared position unit)
  (when (and current (not (equal (ctm-encoding-identity current) (ctm-encoding-identity declared))))
    (problem 'ctm-rejection :encoding-conflict position
             (format nil "Encoding ~S conflicts with explicitly selected ~S." declared current) unit))
  declared)

(defun decode-ctm-octets (bytes &key encoding)
  "Apply CTM 3.2 ordering: supplied encoding, BOM, declaration, default, decode.
UTF-8 and ISO-8859-5 use their small, explicit IANA identity sets."
  (check-type encoding (or null string))
  (let* ((bom (and (>= (length bytes) 3) (= (aref bytes 0) #xef)
                   (= (aref bytes 1) #xbb) (= (aref bytes 2) #xbf)))
         (start (if bom 3 0)) (selected encoding) (name-position 0))
    (when bom (setf selected (compatible-ctm-encoding selected "UTF-8" 0 :byte)))
    (when (ctm-ascii-prefix-p bytes start "%encoding")
      (multiple-value-bind (name end position) (ctm-encoding-name bytes start :byte)
        (declare (ignore end))
        (setf selected (compatible-ctm-encoding selected name position :byte)
              name-position position)))
    (case (ctm-encoding-kind (or selected "UTF-8"))
      (:utf-8 (decode-utf8 bytes :strip-bom t))
      (:iso-8859-5 (decode-iso-8859-5 bytes))
      (otherwise
       (problem 'ctm-unsupported :unsupported-encoding name-position
                (format nil "Charset ~S is not implemented; supported CTM encodings are UTF-8 and ISO-8859-5." selected) :byte)))))
