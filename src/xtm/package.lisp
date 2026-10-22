(defpackage #:topic-maps.xtm
  (:use #:cl)
  (:export #:deserialize-octets
           #:xtm-error #:xtm-rejection #:xtm-unsupported #:xtm-xml-error #:xtm-resource-error
           #:error-code #:error-detail #:error-document-iri #:error-source-key
           #:error-line #:error-column #:error-cause))
(in-package #:topic-maps.xtm)

(define-condition xtm-error (error)
  ((code :initarg :code :reader error-code)
   (detail :initarg :detail :reader error-detail)
   (document-iri :initarg :document-iri :reader error-document-iri)
   (source-key :initarg :source-key :reader error-source-key)
   (line :initarg :line :initform nil :reader error-line)
   (column :initarg :column :initform nil :reader error-column))
  (:report (lambda (c out)
             (format out "XTM ~A at ~A (~A), approximately ~A:~A: ~A"
                     (error-code c) (error-source-key c) (error-document-iri c)
                     (error-line c) (error-column c) (error-detail c)))))
(define-condition xtm-rejection (xtm-error) ())
(define-condition xtm-unsupported (xtm-error) ())
(define-condition xtm-xml-error (xtm-error)
  ((cause :initarg :cause :reader error-cause)))

(define-condition xtm-resource-error (xtm-error)
  ((cause :initarg :cause :initform nil :reader error-cause)))

(defvar *document-iri*)
(defvar *source-key*)
(defun reject (code detail &optional node (class 'xtm-rejection))
  (error class :code code :detail detail :document-iri *document-iri*
         :source-key *source-key* :line (when node (node-line node))
         :column (when node (node-column node))))
