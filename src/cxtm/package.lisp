(defpackage #:topic-maps.cxtm
  (:use #:cl #:topic-maps.tmdm)
  (:export #:canonicalize #:canonicalize-octets #:write-cxtm
           #:cxtm-error #:cxtm-unsupported #:error-code #:error-detail))
(in-package #:topic-maps.cxtm)
(define-condition cxtm-error (error)
  ((code :initarg :code :reader error-code)
   (detail :initarg :detail :reader error-detail))
  (:report (lambda (c out) (format out "CXTM ~A: ~A" (error-code c) (error-detail c)))))
(define-condition cxtm-unsupported (cxtm-error) ())
(defun fail (code detail &optional unsupported)
  (error (if unsupported 'cxtm-unsupported 'cxtm-error) :code code :detail detail))
