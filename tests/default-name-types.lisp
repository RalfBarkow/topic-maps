(defpackage #:topic-maps.default-name-type.tests
  (:use #:cl #:topic-maps.tmdm)
  (:import-from #:topic-maps.ctm.tests #:check)
  (:export #:run-tests #:default-name-type-checks))
(in-package #:topic-maps.default-name-type.tests)

;;; Two documented default name type Subject Identifiers.
;;; The TMDM text dated 2006-06-18 spells clause 7.5's identifier .../model/name-type; the text dated
;;; 2008-06-03 spells it .../model/topic-name, as CTM 3.11 and XTM 2.0 do. Both are supported as different
;;; identifiers. Nothing here equates them, and nothing here decides which text is authoritative.
;;; These tests exercise the unchanged model, CTM reader and CXTM canonicalizer; they add no production code.

(defvar *last-checks* nil)
(defun default-name-type-checks () *last-checks*)
(defparameter +document+ "https://example.invalid/a/doc.ctm")
(defparameter +topic-name+ "http://psi.topicmaps.org/iso13250/model/topic-name")
(defparameter +name-type+ "http://psi.topicmaps.org/iso13250/model/name-type")
(defparameter +type+ "http://psi.topicmaps.org/iso13250/model/type")

(defun read-ctm (text)
  (topic-maps.ctm:deserialize-string text :document-iri +document+ :source-name "default-name-types"))
(defun cxtm (map) (topic-maps.cxtm:canonicalize map :base-locator +document+))
(defun with-si (map iri)
  (find-if (lambda (topic) (member iri (topic-subject-identifiers topic) :test #'string=)) (topic-map-topics map)))
(defun local (map id)
  (find-if (lambda (topic) (member (format nil "~A#~A" +document+ id) (topic-item-identifiers topic) :test #'string=))
           (topic-map-topics map)))
(defun name-types (topic) (mapcar #'topic-name-type (topic-names topic)))

(defun implicit-tests ()
  "CTM 3.11: a name without a type gets the default name type, spelled .../topic-name."
  (let* ((map (read-ctm "a - \"N\" .")) (a (local map "a")) (type (first (name-types a))))
    (check "implicit:ctm-untyped-name-uses-topic-name"
           (and (= 1 (length (topic-names a))) (equal (list +topic-name+) (topic-subject-identifiers type))))
    (check "implicit:no-name-type-topic-is-created" (null (with-si map +name-type+)))
    (check "implicit:identifier-reader-is-unchanged" (string= +topic-name+ (default-name-type-identifier)))))

(defun explicit-tests ()
  "An explicitly stated name type is kept, whichever of the two identifiers it carries."
  (let* ((map (read-ctm (format nil "a - <~A> : \"N\" ." +name-type+)))
         (a (local map "a")) (type (first (name-types a))))
    (check "explicit:name-type-is-preserved-on-import"
           (and (= 1 (length (topic-names a))) (equal (list +name-type+) (topic-subject-identifiers type))))
    (check "explicit:name-type-creates-no-topic-name-topic" (null (with-si map +topic-name+)))
    (check "explicit:name-type-is-preserved-on-cxtm-export"
           (and (search +name-type+ (cxtm map)) (not (search +topic-name+ (cxtm map))))))
  (let* ((map (read-ctm (format nil "a - <~A> : \"N\" ; - \"N\" ." +topic-name+))) (a (local map "a")))
    ;; Same Subject Identifier, hence the same Topic (TMDM 5.3.5) and equal Names (TMDM 5.4).
    (check "explicit:topic-name-is-the-implicit-default"
           (and (= 1 (length (topic-names a))) (eq (with-si map +topic-name+) (first (name-types a)))))))

(defun coexistence-tests ()
  "Both identifiers in one map stay two Topics; equal-looking Names of the two types stay two Names."
  (let* ((map (read-ctm (format nil "a - \"N\" ; - <~A> : \"N\" ." +name-type+)))
         (a (local map "a")) (old (with-si map +name-type+)) (new (with-si map +topic-name+)))
    (check "coexistence:two-type-topics" (and old new (not (eq old new))))
    (check "coexistence:two-names" (= 2 (length (topic-names a))))
    (check "coexistence:each-name-keeps-its-type"
           (null (set-exclusive-or (list old new) (name-types a) :test #'eq)))
    (let ((before (cxtm map)))
      (normalize-topic-map map)
      (check "coexistence:normalization-equates-nothing"
             (and (= 2 (length (topic-names a))) (not (eq (canonical-topic old) (canonical-topic new)))
                  (string= before (cxtm map)))))
    (check "coexistence:both-identifiers-in-cxtm"
           (and (search +name-type+ (cxtm map)) (search +topic-name+ (cxtm map))))))

(defun import-tests ()
  "IMPORT-MAP-CONTENT copies explicit name types of both identifiers unchanged."
  (let* ((source (read-ctm (format nil "a - \"N\" ; - <~A> : \"M\" ." +name-type+)))
         (target (make-topic-map)))
    (import-map-content target source)
    (let ((a (local target "a")))
      (check "import:both-type-topics-arrive"
             (and (with-si target +name-type+) (with-si target +topic-name+)
                  (not (eq (with-si target +name-type+) (with-si target +topic-name+)))))
      (check "import:names-keep-their-types"
             (and (= 2 (length (topic-names a)))
                  (every (lambda (name)
                           (equal (topic-subject-identifiers (topic-name-type name))
                                  (list (if (string= "N" (topic-name-value name)) +topic-name+ +name-type+))))
                         (topic-names a))))
      (check "import:cxtm-equal-to-source" (string= (cxtm source) (cxtm target))))))

(defun characterization-tests ()
  "What the library does today. Not a normative equivalence and not an interoperability rule."
  ;; An explicit merge of the two type Topics is a caller's own assertion that they have one subject.
  (let* ((map (read-ctm (format nil "a - \"N\" ; - <~A> : \"N\" ." +name-type+)))
         (a (local map "a")) (old (with-si map +name-type+)) (new (with-si map +topic-name+))
         (merged (merge-topics old new)))
    (check "characterization:explicit-merge-is-accepted"
           (and (eq merged (canonical-topic old)) (eq merged (canonical-topic new))))
    (check "characterization:merged-topic-carries-both-identifiers"
           (null (set-exclusive-or (list +name-type+ +topic-name+) (topic-subject-identifiers merged) :test #'string=)))
    (check "characterization:names-become-equal-and-merge" (= 1 (length (topic-names a)))))
  ;; The protected Core Subject set holds .../name-type and not .../topic-name; it is left as it is.
  (check "characterization:core-set-is-unchanged"
         (and (member +name-type+ (core-subject-identifiers) :test #'string=)
              (not (member +topic-name+ (core-subject-identifiers) :test #'string=))
              (= 8 (length (core-subject-identifiers)))))
  (let* ((map (make-topic-map)) (topic (intern-topic map :subject-identifier +name-type+)))
    (check "characterization:name-type-with-another-core-subject-is-rejected"
           (handler-case (progn (add-topic-identifier topic :subject-identifier +type+) nil)
             (core-subject-error (c) (eq :core-subject-conflict (core-subject-error-code c))))))
  (let* ((map (make-topic-map)) (topic (intern-topic map :subject-identifier +topic-name+))
         (result (add-topic-identifier topic :subject-identifier +type+)))
    (check "characterization:topic-name-with-another-core-subject-is-accepted-today"
           (= 2 (length (topic-subject-identifiers result))))))

(defun run-tests ()
  (let ((topic-maps.ctm.tests::*checks* nil))
    (implicit-tests) (explicit-tests) (coexistence-tests) (import-tests) (characterization-tests)
    (setf *last-checks* (reverse topic-maps.ctm.tests::*checks*))
    (format t "~&DEFAULT-NAME-TYPE-PASS: ~D checks; both identifiers kept apart; XTM path NOT-RUN in this suite.~%"
            (length *last-checks*))
    *last-checks*))
