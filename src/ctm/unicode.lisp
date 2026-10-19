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


;; Slice 20C: inspect only the ASCII encoding header before strict UTF-8 decoding.
;; No new decoder, resource protocol, charset registry or I/O is introduced.
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

(defun compatible-ctm-encoding (current declared position unit)
  (when (and current (not (string-equal current declared)))
    (problem 'ctm-rejection :encoding-conflict position
             (format nil "Encoding ~S conflicts with explicitly selected ~S." declared current) unit))
  declared)

(defun decode-ctm-octets (bytes &key encoding)
  "Apply CTM 3.2 ordering: supplied encoding, BOM, declaration, default, decode.
Only UTF-8 is implemented. Matching names are case-insensitive; no alias table."
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
    (unless (or (null selected) (string-equal selected "UTF-8"))
      (problem 'ctm-unsupported :unsupported-encoding name-position
               (format nil "Charset ~S is recognized but only UTF-8 decoding is implemented." selected) :byte))
    (decode-utf8 bytes :strip-bom t)))
