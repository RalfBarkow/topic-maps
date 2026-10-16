(in-package #:topic-maps.tmdm)

(defun integer-datatype () "http://www.w3.org/2001/XMLSchema#integer")

(defun integer-lexical-bounds (value)
  "XSD 3.3.13.1/4.3.6: ASCII sign/digits after XML whitespace collapse.
Internal whitespace cannot be part of an integer, so trimming the XML whitespace
at the two ends is sufficient to validate this datatype's collapsed form."
  (let* ((start (position-if-not (lambda (c) (find c '(#\Space #\Tab #\Return #\Newline))) value))
         (end (when start (1+ (position-if-not (lambda (c) (find c '(#\Space #\Tab #\Return #\Newline))) value :from-end t))))
         (negative (and start (char= (char value start) #\-)))
         (digits (when start (if (find (char value start) "+-") (1+ start) start))))
    (when (and digits (< digits end)
               (loop for i from digits below end always (find (char value i) "0123456789")))
      (values digits end negative))))

(defun integer-lexical-p (value)
  "Whether VALUE is an xsd:integer lexical form (including its whitespace facet).
This does not change the string stored in any TMDM information item."
  (check-type value string)
  (not (null (integer-lexical-bounds value))))

(defun canonical-integer-lexical-form (value)
  "Return the canonical xsd:integer string, or NIL for an invalid lexical form.
Pure character processing: no machine-word bounds, Lisp reader, or model mutation.
XSD 3.3.13.2: no plus/leading zeroes; the zero value is represented as 0."
  (check-type value string)
  (multiple-value-bind (start end negative) (integer-lexical-bounds value)
    (when start
      (let ((nonzero (position-if-not (lambda (c) (char= c #\0)) value :start start :end end)))
        (cond ((null nonzero) "0")
              (negative (concatenate 'string "-" (subseq value nonzero end)))
              (t (subseq value nonzero end)))))))
