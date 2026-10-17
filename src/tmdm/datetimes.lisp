(in-package #:topic-maps.tmdm)

(defun datetime-datatype () "http://www.w3.org/2001/XMLSchema#dateTime")

(defun datetime-parts (value)
  "XSD 1.0 Second Edition 3.2.7/D.1 lexical validation, not value equality.
Return components and NIL, or NIL and a specific diagnostic. Reuses Date validation."
  (let* ((text (string-trim '(#\Space #\Tab #\Return #\Newline) value))
         (tee (position #\T text)))
    (labels ((bad (reason) (return-from datetime-parts (values nil reason)))
             (digits (s) (and (plusp (length s)) (every (lambda (c) (find c "0123456789")) s)))
             (two (s i) (+ (* 10 (position (char s i) "0123456789"))
                           (position (char s (1+ i)) "0123456789"))))
      (unless tee (bad :invalid-datetime-syntax))
      (let* ((date (subseq text 0 tee)) (time (subseq text (1+ tee))))
        (multiple-value-bind (a date-end end reason) (date-lexical-bounds date)
          (unless (and a (= date-end end)) (bad (or reason :invalid-datetime-date))))
        (unless (and (>= (length time) 8) (digits (subseq time 0 2)) (char= #\: (char time 2))
                     (digits (subseq time 3 5)) (char= #\: (char time 5)) (digits (subseq time 6 8)))
          (bad :invalid-datetime-time))
        (let* ((zone-start (position-if (lambda (c) (find c "Z+-")) time :start 8))
               (fraction (subseq time 8 zone-start)) (zone (if zone-start (subseq time zone-start) ""))
               (hour (two time 0)) (minute (two time 3)) (second (two time 6)))
          (unless (or (zerop (length fraction))
                      (and (> (length fraction) 1) (char= #\. (char fraction 0)) (digits (subseq fraction 1))))
            (bad :invalid-datetime-fraction))
          (unless (date-lexical-p (concatenate 'string date zone)) (bad :invalid-datetime-timezone))
          (unless (<= hour 24) (bad :invalid-datetime-hour))
          (unless (<= minute 59) (bad :invalid-datetime-minute))
          ;; XSD 1.0 D.1 permits whole seconds 60; XSD 1.1 rules are not substituted.
          (unless (<= second 60) (bad :invalid-datetime-second))
          (when (and (= hour 24)
                     (or (plusp minute) (plusp second)
                         (and (plusp (length fraction)) (find-if-not (lambda (c) (char= c #\0)) (subseq fraction 1)))))
            (bad :invalid-datetime-midnight))
          (values (list :date date :hour hour :minute minute :second second
                        :fraction (if (zerop (length fraction)) "" (subseq fraction 1)) :zone zone) nil))))))

(defun datetime-lexical-p (value)
  "Validate the supported XSD 1.0 lexical space, including offset/second-60 syntax."
  (check-type value string)
  (not (null (datetime-parts value))))

(defun next-datetime-year (year)
  "Character arithmetic: arbitrary-length lexical year, skipping XSD 1.0 year zero."
  (let* ((negative (char= #\- (char year 0)))
         (digits (copy-seq (if negative (subseq year 1) year))))
    (when (and negative (string= digits "0001")) (return-from next-datetime-year "0001"))
    (let ((carry t))
      (loop for i downfrom (1- (length digits)) to 0 while carry do
        (cond (negative
               (if (char= #\0 (char digits i)) (setf (char digits i) #\9)
                   (setf (char digits i) (code-char (1- (char-code (char digits i)))) carry nil)))
              ((char= #\9 (char digits i)) (setf (char digits i) #\0))
              (t (setf (char digits i) (code-char (1+ (char-code (char digits i)))) carry nil))))
      (when carry (setf digits (concatenate 'string "1" digits))))
    (loop while (and (> (length digits) 4) (char= #\0 (char digits 0))) do (setf digits (subseq digits 1)))
    (concatenate 'string (if negative "-" "") digits)))

(defun next-datetime-date (date)
  "Next Gregorian day using Slice 9 validity and character year rollover."
  (let* ((dash (position #\- date :start (if (char= #\- (char date 0)) 1 0)))
         (year (subseq date 0 dash))
         (month (+ (* 10 (position (char date (1+ dash)) "0123456789")) (position (char date (+ dash 2)) "0123456789")))
         (day (+ (* 10 (position (char date (+ dash 4)) "0123456789")) (position (char date (+ dash 5)) "0123456789")))
         (candidate (format nil "~A-~2,'0D-~2,'0D" year month (1+ day))))
    (if (date-lexical-p candidate) candidate
        (if (< month 12) (format nil "~A-~2,'0D-01" year (1+ month))
            (concatenate 'string (next-datetime-year year) "-01-01")))))

(defun previous-datetime-year (year)
  "Inverse of NEXT-DATETIME-YEAR, using character arithmetic and no year zero."
  (labels ((negate (text)
             (if (char= #\- (char text 0)) (subseq text 1)
                 (concatenate 'string "-" text))))
    (negate (next-datetime-year (negate year)))))

(defun previous-datetime-date (date)
  "Previous day under the existing Date validator's calendar contract."
  (let* ((dash (position #\- date :start (if (char= #\- (char date 0)) 1 0)))
         (year (subseq date 0 dash))
         (month (parse-integer date :start (1+ dash) :end (+ dash 3)))
         (day (parse-integer date :start (+ dash 4) :end (+ dash 6))))
    (cond ((> day 1) (format nil "~A-~2,'0D-~2,'0D" year month (1- day)))
          ((= month 1) (concatenate 'string (previous-datetime-year year) "-12-31"))
          (t (loop for last-day downfrom 31 to 28
                   for candidate = (format nil "~A-~2,'0D-~2,'0D" year (1- month) last-day)
                   when (date-lexical-p candidate) return candidate)))))

(defun datetime-offset-minutes (zone)
  "Signed whole minutes of an already validated XSD timezone; NIL if absent."
  (cond ((zerop (length zone)) nil)
        ((string= zone "Z") 0)
        (t (* (if (char= #\- (char zone 0)) -1 1)
              (+ (* 60 (parse-integer zone :start 1 :end 3))
                 (parse-integer zone :start 4 :end 6))))))

(defun canonical-datetime-lexical-form (value)
  "Pure XSD 1.0 UTC canonical lexical form, preserving an absent timezone.
Second value :CANONICAL, an invalid diagnostic, :UNSUPPORTED-BCE-TIMEZONE-ROLLOVER,
or :UNSUPPORTED-LEAP-SECOND-CONTEXT. Never change model data/retained handles.
Noncandidate leap dates retain Slice 10's D.1 following-minute interpretation."
  (check-type value string)
  (multiple-value-bind (parts reason) (datetime-parts value)
    (unless parts (return-from canonical-datetime-lexical-form (values nil reason)))
    (let* ((date (getf parts :date)) (hour (getf parts :hour)) (minute (getf parts :minute))
           (second (getf parts :second)) (fraction (string-right-trim "0" (getf parts :fraction)))
           (zone (getf parts :zone)) (zoned (plusp (length zone)))
           (offset (datetime-offset-minutes zone)) (original-date date))
      ;; Do not infer the UTC context of a local leap second. Zero/absent-zone
      ;; behavior below is exactly the pre-existing Slice 10 contract.
      (when (and offset (not (zerop offset)) (= second 60))
        (return-from canonical-datetime-lexical-form (values nil :unsupported-leap-second-context)))
      (when (= hour 24) (setf hour 0 date (next-datetime-date date)))
      (when (and offset (not (zerop offset)))
        ;; Only the hour/minute fields are small integers. Years and fractions
        ;; stay character sequences; no float, system clock or local timezone.
        (multiple-value-bind (days minutes) (floor (- (+ (* 60 hour) minute) offset) 1440)
          (setf hour (floor minutes 60) minute (mod minutes 60)
                date (case days (-1 (previous-datetime-date date)) (1 (next-datetime-date date)) (otherwise date))))
        (when (and (not (string= date original-date))
                   (or (char= #\- (char original-date 0)) (char= #\- (char date 0))))
          (return-from canonical-datetime-lexical-form (values nil :unsupported-bce-timezone-rollover))))
      (when (= second 60)
        (let* ((md (subseq date (- (length date) 5)))
               (candidate (member md '("03-31" "06-30" "09-30" "12-31") :test #'string=)))
          (cond ((and zoned candidate (= hour 23) (= minute 59)))
                ((member md '("03-31" "04-01" "06-30" "07-01" "09-30" "10-01" "12-31" "01-01") :test #'string=)
                 (return-from canonical-datetime-lexical-form (values nil :unsupported-leap-second-context)))
                (t (setf second 0) (incf minute)
                   (when (= minute 60) (setf minute 0) (incf hour))
                   (when (= hour 24) (setf hour 0 date (next-datetime-date date)))))))
      (values (format nil "~AT~2,'0D:~2,'0D:~2,'0D~A~A" date hour minute second
                      (if (zerop (length fraction)) "" (concatenate 'string "." fraction))
                      (if zoned "Z" "")) :canonical))))
