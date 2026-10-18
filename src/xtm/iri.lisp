(in-package #:topic-maps.xtm)

;; RFC 3986 5.2 algorithm, shared policy with CTM but no CTM dependency.
;; Do not use PURI rendering here: it removes ports and rewrites locator spellings.

(defstruct iri-parts scheme authority (path "") query fragment)

(defun ascii-letter-p (c)
  (or (char<= #\a c #\z) (char<= #\A c #\Z)))
(defun scheme-p (text)
  (and (plusp (length text)) (ascii-letter-p (char text 0))
       (every (lambda (c) (or (ascii-letter-p c) (find c "0123456789+-."))) text)))
(defun starts-with (prefix string)
  (and (<= (length prefix) (length string))
       (string= prefix string :end2 (length prefix))))

(defun split-iri (iri)
  (let* ((fragment-position (position #\# iri))
         (fragment (when fragment-position (subseq iri (1+ fragment-position))))
         (remaining (subseq iri 0 fragment-position))
         (query-position (position #\? remaining))
         (query (when query-position (subseq remaining (1+ query-position))))
         (head (subseq remaining 0 query-position))
         (colon (position #\: head))
         (scheme (when (and colon (scheme-p (subseq head 0 colon))) (subseq head 0 colon)))
         (rest (if scheme (subseq head (1+ colon)) head))
         (slash (when (starts-with "//" rest) (position #\/ rest :start 2)))
         (authority (when (starts-with "//" rest) (subseq rest 2 slash)))
         (path (if authority (if slash (subseq rest slash) "") rest)))
    (make-iri-parts :scheme scheme :authority authority :path path :query query :fragment fragment)))

(defun join-iri (parts)
  (with-output-to-string (out)
    (when (iri-parts-scheme parts) (format out "~A:" (iri-parts-scheme parts)))
    (when (iri-parts-authority parts) (format out "//~A" (iri-parts-authority parts)))
    (write-string (iri-parts-path parts) out)
    (when (iri-parts-query parts) (format out "?~A" (iri-parts-query parts)))
    (when (iri-parts-fragment parts) (format out "#~A" (iri-parts-fragment parts)))))

(defun remove-dot-segments (path)
  ;; RFC 3986 5.2.4, preserving empty segments and terminal slashes.
  (let ((input path) (output ""))
    (loop while (plusp (length input)) do
      (cond ((starts-with "../" input) (setf input (subseq input 3)))
            ((starts-with "./" input) (setf input (subseq input 2)))
            ((starts-with "/./" input) (setf input (subseq input 2)))
            ((string= input "/.") (setf input "/"))
            ((or (starts-with "/../" input) (string= input "/.."))
             (setf input (if (string= input "/..") "/" (subseq input 3))
                   output (subseq output 0 (or (position #\/ output :from-end t) 0))))
            ((or (string= input ".") (string= input "..")) (setf input ""))
            (t (let ((end (position #\/ input :start (if (char= (char input 0) #\/) 1 0))))
                 (setf output (concatenate 'string output (subseq input 0 end))
                       input (if end (subseq input end) ""))))))
    output))

(defun resolve-iri (reference document node)
  "XTM 4.3.4: percent UTF-8 decoding, then RFC 3986 resolution; never fetch."
  (let* ((reference (validate-decoded-reference (unescape-reference reference node) node))
         (r (split-iri reference)) (b (split-iri document))
         (target (make-iri-parts :fragment (iri-parts-fragment r))))
    (cond
      ((iri-parts-scheme r)
       (setf (iri-parts-scheme target) (iri-parts-scheme r)
             (iri-parts-authority target) (iri-parts-authority r)
             (iri-parts-path target) (remove-dot-segments (iri-parts-path r))
             (iri-parts-query target) (iri-parts-query r)))
      (t
       (setf (iri-parts-scheme target) (iri-parts-scheme b))
       (cond ((iri-parts-authority r)
              (setf (iri-parts-authority target) (iri-parts-authority r)
                    (iri-parts-path target) (remove-dot-segments (iri-parts-path r))
                    (iri-parts-query target) (iri-parts-query r)))
             (t
              (setf (iri-parts-authority target) (iri-parts-authority b))
              (if (zerop (length (iri-parts-path r)))
                  (setf (iri-parts-path target) (iri-parts-path b)
                        (iri-parts-query target) (or (iri-parts-query r) (iri-parts-query b)))
                  (setf (iri-parts-path target)
                        (remove-dot-segments
                         (if (starts-with "/" (iri-parts-path r))
                             (iri-parts-path r)
                             (concatenate 'string
                              (if (and (iri-parts-authority b) (zerop (length (iri-parts-path b))))
                                  "/"
                                  (subseq (iri-parts-path b) 0
                                          (let ((slash (position #\/ (iri-parts-path b) :from-end t)))
                                            (if slash (1+ slash) 0))))
                              (iri-parts-path r))))
                        (iri-parts-query target) (iri-parts-query r)))))))
    (join-iri target)))

(defun unescape-reference (text node)
  ;; XTM 4.3.4 explicitly decodes percent escapes before resolving, including
  ;; reserved characters. Babel is an existing qualified CXML dependency.
  (when (some (lambda (c) (or (<= (char-code c) 32) (find c "<>\"{}|^`\\"))) text)
    (reject :invalid-iri "Illegal character in the original IRI reference." node))
  (when (> (count #\# text) 1) (reject :invalid-iri "Multiple fragment delimiters." node))
  (with-output-to-string (out)
    (loop for i from 0 below (length text) do
      (if (char= (char text i) #\%)
          (let ((bytes nil))
            (loop while (and (< i (length text)) (char= (char text i) #\%)) do
              (unless (and (< (+ i 2) (length text))
                           (digit-char-p (char text (1+ i)) 16)
                           (digit-char-p (char text (+ i 2)) 16))
                (reject :invalid-percent-escape "Expected two hexadecimal digits." node))
              (push (+ (* 16 (digit-char-p (char text (1+ i)) 16))
                       (digit-char-p (char text (+ i 2)) 16)) bytes)
              (incf i 3))
            (handler-case
                (write-string (babel:octets-to-string
                               (coerce (nreverse bytes) '(vector (unsigned-byte 8)))
                               :encoding :utf-8 :errorp t) out)
              (babel:character-decoding-error ()
                (reject :invalid-percent-utf8 "Percent escapes are not valid UTF-8." node)))
            (decf i))
          (write-char (char text i) out)))))

(defun require-document-iri (iri)
  ;; Document IRI is already an absolute locator, not another escaped href.
  (unless (and (stringp iri) (plusp (length iri))
               (iri-parts-scheme (split-iri iri))
               (not (find #\# iri))
               (notany (lambda (c) (or (<= (char-code c) 32) (find c "<>\"{}|^`\\"))) iri))
    (reject :invalid-document-iri "An explicit absolute, fragment-free Document IRI is required."))
  iri)

(defun validate-decoded-reference (iri node)
  ;; Percent-unescaping is required even for reserved characters. It must not
  ;; introduce controls or malformed relative-path/fragment structure.
  (let* ((parts (split-iri iri)) (path (iri-parts-path parts))
         (first-segment (subseq path 0 (position #\/ path))))
    (when (or (some (lambda (c) (or (< (char-code c) 32) (= (char-code c) 127))) iri)
              (> (count #\# iri) 1)
              (and (null (iri-parts-scheme parts)) (find #\: first-segment)))
      (reject :invalid-iri "Invalid decoded IRI reference." node)))
  iri)
