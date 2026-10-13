(in-package #:topic-maps.test-foundation)

;;; ANSI Common Lisp has no portable recursive-directory API. Keep the UIOP
;;; dependency here. No SBCL-specific API is used by the library.
(defun directory-files-recursively (root)
  (let ((directory (uiop:ensure-directory-pathname root)))
    (when (uiop:directory-exists-p directory)
      (append (uiop:directory-files directory)
              (mapcan #'directory-files-recursively
                      (uiop:subdirectories directory))))))

(defun relative-file-name (pathname root)
  (let ((relative (enough-namestring pathname
                                      (uiop:ensure-directory-pathname root))))
    (when (or (uiop:absolute-pathname-p relative)
              (member :up (pathname-directory relative)))
      (error "Path ~S is outside corpus root ~S." pathname root))
    ;; UIOP's Unix namestring is stable across host pathname conventions.
    (uiop:unix-namestring relative)))

(defun sorted-files (directory root)
  (sort (directory-files-recursively directory) #'string<
        :key (lambda (path) (relative-file-name path root))))

(defun file-type-p (pathname type)
  (equal (pathname-type pathname) type))

(defun default-corpus-root ()
  (asdf:system-relative-pathname "topic-maps" "vendor/cxtm/"))

(defun read-corpus-metadata ()
  (let ((*read-eval* nil))
    (with-open-file (stream (asdf:system-relative-pathname
                            "topic-maps" "references/corpus-lock.sexp"))
      (let ((data (read stream)))
        (unless (eq :eof (read stream nil :eof))
          (error "Corpus metadata contains more than one form."))
        data))))

(defun document-iri (base relative)
  "Assign fixture IRIs, not dereference or resolve CTM identifiers."
  (unless (and (stringp base) (> (length base) 0)
               (char= #\/ (char base (1- (length base))))
               (or (uiop:string-prefix-p "https://" base)
                   (uiop:string-prefix-p "http://" base))
               (not (find #\# base)) (not (find #\? base))
               (every (lambda (c) (and (> (char-code c) 32)
                                      (< (char-code c) 127))) base))
    (error "Document base must be an explicit absolute HTTP(S) directory IRI: ~S" base))
  (unless (every (lambda (c)
                   (or (find c "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._/")
                       nil)) relative)
    (error "Fixture path needs an explicit IRI encoding policy: ~S" relative))
  (concatenate 'string base relative))

(defun read-clause-map ()
  (let ((*read-eval* nil))
    (with-open-file (stream (asdf:system-relative-pathname
                            "topic-maps" "references/reviewed-clauses.sexp"))
      (read stream))))
