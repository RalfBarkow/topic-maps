(in-package #:topic-maps.tmdm)

(defun date-datatype () "http://www.w3.org/2001/XMLSchema#date")

(defun date-lexical-bounds (value)
  "XSD 1.0 Second Edition 3.2.7.1/3.2.9.1/D/E.1, with XML whitespace collapse.
Return start, date-end, end, NIL for a valid lexical date; otherwise NIL bounds
and a diagnostic code. Timezone syntax is validated, never converted here.
The year is accumulated modulo 400, so input length has no machine-word limit.
BCE leap validation applies E.1 to the signed lexical year; the XSD 1.0
ambiguity is qualified in reading-date-occurrences.md."
  (let* ((start (position-if-not (lambda (c) (find c '(#\Space #\Tab #\Return #\Newline))) value))
         (end (when start (1+ (position-if-not (lambda (c) (find c '(#\Space #\Tab #\Return #\Newline))) value :from-end t)))))
    (labels ((bad (code) (return-from date-lexical-bounds (values nil nil nil code)))
             (digits (a b) (and (<= b end) (< a b)
                               (loop for i from a below b always (find (char value i) "0123456789"))))
             (two (i) (+ (* 10 (position (char value i) "0123456789")) (position (char value (1+ i)) "0123456789"))))
      (unless start (bad :invalid-date-syntax))
      (when (char= #\+ (char value start)) (bad :invalid-date-year))
      (let* ((year-start (if (char= #\- (char value start)) (1+ start) start))
             (dash (position #\- value :start year-start :end end)))
        (unless (and dash (>= (- dash year-start) 4) (digits year-start dash)) (bad :invalid-date-year))
        (when (and (> (- dash year-start) 4) (char= #\0 (char value year-start))) (bad :invalid-date-year))
        (let ((residue 0) (nonzero nil))
          (loop for i from year-start below dash for digit = (position (char value i) "0123456789") do
            (unless (zerop digit) (setf nonzero t))
            (setf residue (mod (+ (* residue 10) digit) 400)))
          (unless nonzero (bad :invalid-date-year))
          (unless (and (<= (+ dash 6) end) (digits (1+ dash) (+ dash 3))
                       (char= #\- (char value (+ dash 3))) (digits (+ dash 4) (+ dash 6)))
            (bad :invalid-date-syntax))
          (let* ((month (two (1+ dash))) (day (two (+ dash 4))) (date-end (+ dash 6))
                 (leap (or (zerop residue) (and (zerop (mod residue 4)) (not (zerop (mod residue 100)))))))
            (unless (<= 1 month 12) (bad :invalid-date-month))
            (unless (<= 1 day (case month (2 (if leap 29 28)) ((4 6 9 11) 30) (otherwise 31)))
              (bad :invalid-date-day))
            (unless (or (= end date-end)
                        (and (= end (1+ date-end)) (char= #\Z (char value date-end)))
                        (and (= end (+ date-end 6)) (find (char value date-end) "+-")
                             (digits (1+ date-end) (+ date-end 3)) (char= #\: (char value (+ date-end 3)))
                             (digits (+ date-end 4) end)
                             (<= (two (1+ date-end)) 14) (<= (two (+ date-end 4)) 59)
                             (or (< (two (1+ date-end)) 14) (zerop (two (+ date-end 4))))))
              (bad :invalid-date-timezone))
            (values start date-end end nil)))))))

(defun date-lexical-p (value)
  "Validate an XSD 1.0 date, including optional timezone syntax, without rewriting."
  (check-type value string)
  (not (null (date-lexical-bounds value))))

(defun canonical-date-lexical-form (value)
  "Pure timezone-free XSD 3.2.9.2 form. Second value distinguishes :CANONICAL,
:UNSUPPORTED-TIMEZONE and an invalid-date diagnostic. Never changes model data."
  (check-type value string)
  (multiple-value-bind (start date-end end reason) (date-lexical-bounds value)
    (cond ((null start) (values nil reason))
          ((/= date-end end) (values nil :unsupported-timezone))
          (t (values (subseq value start end) :canonical)))))
