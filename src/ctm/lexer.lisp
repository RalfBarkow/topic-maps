(in-package #:topic-maps.ctm)

(defstruct token kind value (position 0))
(defstruct (lexer (:constructor make-lexer (text))) text (cursor 0))

(defun peek-character (lexer &optional (delta 0))
  (let ((i (+ (lexer-cursor lexer) delta)))
    (when (< i (length (lexer-text lexer))) (char (lexer-text lexer) i))))
(defun take-character (lexer)
  (prog1 (peek-character lexer) (incf (lexer-cursor lexer))))
(defun whitespace-p (c)
  (and c (find (char-code c) '(#x20 #x0d #x0a #x09))))
(defun name-start-p (c)
  (and c
       (or (ascii-letter-p c) (char= c #\_)
           (let ((n (char-code c)))
             (some (lambda (r) (<= (first r) n (second r)))
                   '((#xc0 #xd6) (#xd8 #xf6) (#xf8 #x2ff) (#x370 #x37d)
                     (#x37f #x1fff) (#x200c #x200d) (#x2070 #x218f) (#x2c00 #x2fef)
                     (#x3001 #xd7ff) (#xf900 #xfdcf) (#xfdf0 #xfffd) (#x10000 #xeffff)))))))
(defun name-part-p (c)
  (and c (or (name-start-p c) (find c "0123456789-") (= (char-code c) #xb7)
             (<= #x300 (char-code c) #x36f) (<= #x203f (char-code c) #x2040))))

(defun skip-layout (lexer)
  (loop
    (cond ((whitespace-p (peek-character lexer)) (take-character lexer))
          ((eql #\# (peek-character lexer))
           (if (eql #\( (peek-character lexer 1))
               (progn
                 (incf (lexer-cursor lexer) 2)
                 (loop with level = 1 while (plusp level) do
                   (cond ((null (peek-character lexer))
                          (problem 'ctm-rejection :unterminated-comment (lexer-cursor lexer) "Unterminated block comment."))
                         ((and (eql #\# (peek-character lexer)) (eql #\( (peek-character lexer 1)))
                          (incf level) (incf (lexer-cursor lexer) 2))
                         ((and (eql #\) (peek-character lexer)) (eql #\# (peek-character lexer 1)))
                          (decf level) (incf (lexer-cursor lexer) 2))
                         (t (take-character lexer)))))
               (loop while (and (peek-character lexer)
                                (not (find (peek-character lexer) '(#\Newline #\Return))))
                     do (take-character lexer))))
          (t (return)))))

(defun read-ctm-string (lexer start)
  (when (and (eql #\" (peek-character lexer)) (eql #\" (peek-character lexer 1)))
    (problem 'ctm-unsupported :triple-quoted-string start "Triple quoted literals are outside Slice 1."))
  (with-output-to-string (out)
    (loop for c = (take-character lexer) do
      (cond ((null c) (problem 'ctm-rejection :unterminated-string start "Unterminated quoted string."))
            ((char= c #\") (return))
            ((char= c #\\)
             (let ((escape (take-character lexer)))
               (case escape
                 (#\n (write-char #\Newline out)) (#\r (write-char #\Return out))
                 (#\t (write-char #\Tab out)) (#\" (write-char #\" out)) (#\\ (write-char #\\ out))
                 ((#\u #\U)
                  (let ((code 0))
                    (dotimes (i (if (char= escape #\u) 4 6))
                      (let* ((digit (take-character lexer)) (value (and digit (digit-char-p digit 16))))
                        (unless value
                          (problem 'ctm-rejection :invalid-unicode-escape (1- (lexer-cursor lexer)) "Expected hexadecimal escape digit."))
                        (setf code (+ (* code 16) value))))
                    (write-char (scalar-character code start) out)))
                 (otherwise (problem 'ctm-rejection :invalid-string-escape (1- (lexer-cursor lexer)) "Unknown string escape.")))))
            (t (write-char c out))))))

(defun scan-name (lexer)
  (loop
    (cond ((name-part-p (peek-character lexer)) (take-character lexer))
          ((eql #\. (peek-character lexer))
           ;; Dots belong to an identifier only if followed by a name-part.
           (let ((delta 0))
             (loop while (eql #\. (peek-character lexer delta)) do (incf delta))
             (if (name-part-p (peek-character lexer delta))
                 (incf (lexer-cursor lexer) delta)
                 (return))))
          (t (return)))))

(defun next-token (lexer)
  (skip-layout lexer)
  (let* ((start (lexer-cursor lexer)) (c (take-character lexer))
         (text (lexer-text lexer)))
    (cond
      ((null c) (make-token :kind :eof :position start))
      ((char= c #\") (make-token :kind :string :value (read-ctm-string lexer start) :position start))
      ((char= c #\<)
       (loop while (and (peek-character lexer) (not (eql #\> (peek-character lexer))))
             do (take-character lexer))
       (unless (peek-character lexer)
         (problem 'ctm-rejection :unterminated-iri start "Expected closing >."))
       (let ((value (subseq text (1+ start) (lexer-cursor lexer))))
         (take-character lexer)
         (when (zerop (length value))
           (problem 'ctm-rejection :empty-iri start "Delimited IRI must not be empty (CTM 3.3.3)."))
         (validate-iri-characters value (1+ start))
         (make-token :kind :iri :value value :position start)))
      ((name-start-p c)
       (scan-name lexer)
       (let ((head (subseq text start (lexer-cursor lexer))))
         (cond
           ((and (scheme-p head) (eql #\: (peek-character lexer))
                 (eql #\/ (peek-character lexer 1)) (eql #\/ (peek-character lexer 2)))
            (incf (lexer-cursor lexer) 3)
            (loop while (and (peek-character lexer) (not (whitespace-p (peek-character lexer)))
                             (not (find (peek-character lexer) "<>\"{}|^`\\[]()")))
                  do (take-character lexer))
            (loop while (and (> (lexer-cursor lexer) start)
                             (find (char text (1- (lexer-cursor lexer))) ";.)"))
                  do (decf (lexer-cursor lexer)))
            (make-token :kind :iri :value (subseq text start (lexer-cursor lexer)) :position start))
           ((and (eql #\: (peek-character lexer))
                 (or (name-start-p (peek-character lexer 1))
                     (and (peek-character lexer 1)
                          (find (peek-character lexer 1) "0123456789"))))
            ;; Only an immediate local part forms a QName (CTM 3.3.4).
            ;; Otherwise ':' remains a separate token, including name types
            ;; followed by a string with or without intervening layout.
            (take-character lexer)
            (if (name-start-p (peek-character lexer))
                (scan-name lexer)
                ;; CTM 3.3.4 production [11]: numeric-leading local parts
                ;; contain name-part characters, which do not include dots.
                (loop while (name-part-p (peek-character lexer)) do (take-character lexer)))
            (make-token :kind :qname :value (subseq text start (lexer-cursor lexer)) :position start))
           (t (make-token :kind :identifier :value head :position start)))))
      ((find c ".;-=^:(),") (make-token :kind :punctuation :value c :position start))
      ((char= c #\%)
       ;; Production [71] has a literal terminal followed by an identifier;
       ;; unlike Role separators it does not require intervening whitespace.
       (if (starts-with "%prefix" (subseq text start))
           (progn (setf (lexer-cursor lexer) (+ start 7))
                  (make-token :kind :directive :value "prefix" :position start))
           (progn
             (scan-name lexer)
             (problem 'ctm-unsupported :unsupported-directive start
                      (format nil "Directive %~A is outside the implemented subset."
                              (subseq text (1+ start) (lexer-cursor lexer)))))))
      ((find c "?[$@~")
       (problem 'ctm-unsupported :unsupported-construct start
                (format nil "Construct starting with ~S is outside the implemented subset." c)))
      (t (problem 'ctm-rejection :unexpected-character start (format nil "Unexpected character ~S." c))))))
