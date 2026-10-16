(in-package #:topic-maps.tmdm)

(defun decimal-datatype () "http://www.w3.org/2001/XMLSchema#decimal")

(defun decimal-lexical-bounds (value)
  "XSD 3.2.3.1/4.3.6: optional sign, ASCII digits and at most one decimal point.
At least one digit is required. XML whitespace is collapsed for interpretation;
internal whitespace remains invalid. No numeric conversion or model mutation."
  (let* ((start (position-if-not (lambda (c) (find c '(#\Space #\Tab #\Return #\Newline))) value))
         (end (when start (1+ (position-if-not (lambda (c) (find c '(#\Space #\Tab #\Return #\Newline))) value :from-end t))))
         (negative (and start (char= (char value start) #\-)))
         (digits (when start (if (find (char value start) "+-") (1+ start) start)))
         (point (when digits (position #\. value :start digits :end end))))
    (when (and digits (< digits end)
               (> (- end digits (if point 1 0)) 0)
               (loop for i from digits below end
                     always (or (and point (= i point)) (find (char value i) "0123456789"))))
      (values digits end point negative))))

(defun decimal-lexical-p (value)
  "Whether VALUE is an xsd:decimal lexical form, including XML whitespace.
XSD permits integer-looking forms and an empty fractional component, unlike
CTM's bare-decimal production. The CTM lexer still decides token boundaries."
  (check-type value string)
  (not (null (decimal-lexical-bounds value))))

(defun canonical-decimal-lexical-form (value)
  "Pure character-based XSD 3.2.3.2 canonical form, or NIL for an invalid value.
No plus/unnecessary zeros; required integer/fraction digits; zero is 0.0.
Arbitrary finite input length needs no floating-point or machine-word value."
  (check-type value string)
  (multiple-value-bind (start end point negative) (decimal-lexical-bounds value)
    (when start
      (let* ((integer-end (or point end))
             (integer-start (position-if-not (lambda (c) (char= c #\0)) value :start start :end integer-end))
             (fraction-start (if point (1+ point) end))
             (fraction-end (position-if-not (lambda (c) (char= c #\0)) value :start fraction-start :end end :from-end t)))
        (concatenate 'string
                     (if (and negative (or integer-start fraction-end)) "-" "")
                     (if integer-start (subseq value integer-start integer-end) "0") "."
                     (if fraction-end (subseq value fraction-start (1+ fraction-end)) "0"))))))
