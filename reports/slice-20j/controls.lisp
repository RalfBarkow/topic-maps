;; Explorative inputs only; original sources, Case Records and reader stay unchanged.
(in-package :cl-user)
(defvar *rows* nil)
(defun control (label text &optional original)
  (let* ((doc (if original (concatenate 'string "https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/" original)
                  "https://example.invalid/slice20i/control.ctm"))
         (baseline (when original (merge-pathnames (concatenate 'string "vendor/cxtm/ctm/baseline/" (file-namestring original) ".cxtm") "/Users/rgb/workspace/topic-maps/"))))
    (multiple-value-bind (map condition)
        (topic-maps.registered-original.tests::captured-read
          (lambda () (topic-maps.ctm:deserialize-string text :document-iri doc :source-name label)))
      (let* ((held (when map (topic-maps.import.tests::handles map)))
             (state (when map (topic-maps.import.tests::state map held)))
             (actual (when map (topic-maps.cxtm:canonicalize-octets map :base-locator doc)))
             (expected (when baseline (topic-maps.registered-original.tests::binary baseline))))
        (push (topic-maps.test-foundation::fields
          "label" label "originalControlOnly" original "sourceText" text "documentIRI" doc
          "condition" (topic-maps.registered-original.tests::condition-data condition)
          "model" (when map (topic-maps.template.tests::observe map))
          "associations" (when map (coerce (loop for a in (topic-maps.tmdm:topic-map-associations map) collect
            (topic-maps.test-foundation::fields
              "typeSI" (coerce (topic-maps.tmdm:topic-subject-identifiers (topic-maps.tmdm:association-type a)) 'vector)
              "roles" (coerce (loop for r in (topic-maps.tmdm:association-roles a) collect
                (topic-maps.test-foundation::fields
                  "typeSI" (coerce (topic-maps.tmdm:topic-subject-identifiers (topic-maps.tmdm:association-role-type r)) 'vector)
                  "playerSI" (coerce (topic-maps.tmdm:topic-subject-identifiers (topic-maps.tmdm:association-role-player r)) 'vector))) 'vector))) 'vector))
          "referencesCurrent" (if (and map (topic-maps.reference.tests::references-current-p map)) :true :false)
          "canonicalizationPreservesMap" (if (and map (equal state (topic-maps.import.tests::state map held))) :true :false)
          "actualCXTM" (when actual (topic-maps.ctm::decode-utf8 actual)) "actualBytes" (when actual (length actual))
          "expectedBytes" (when expected (length expected))
          "byteExact" (if (and actual expected (equalp actual expected)) :true :false)) *rows*)))))
(control "expanded-ambiguous5" "topic <http://www.example.org/something/>; =<http://www.example.org/something/>; ^<http://www.example.org/something/>." "ctm/in/template-ambiguous-parameter5.ctm")
(control "expanded-ambiguous6" "%prefix ex <http://www.example.org/> topic ex:something; =ex:something; ^ex:something; occ: ex:something." "ctm/in/template-ambiguous-parameter6.ctm")
(control "expanded-subject-identifier2" "topic <http://psi.example.org/fake>." "ctm/in/template-subject-identifier2.ctm")
(control "head-variable-IRI" "def t($v) $v. end t(<http://www.example.org/entity>)")
(control "head-variable-item-identifier" "def t($v) $v. end t(^<http://www.example.org/entity>)")
(control "head-variable-subject-locator" "def t($v) $v. end t(=<http://www.example.org/entity>)")
(control "IRI-variable-in-explicit-identities-type-player-and-literal" "def t($v) $v. holder =$v; ^$v; occ: $v. $v($v : $v) end t(<http://www.example.org/entity>)")
(control "unmarked-tail-even-without-invocation" "def t($v) topic $v. end")
(control "item-identifier-cannot-be-literal" "def t($v) topic occ: $v. end t(^<http://www.example.org/entity>)")
(control "subject-locator-cannot-be-literal" "def t($v) topic occ: $v. end t(=<http://www.example.org/entity>)")
(control "second-item-identifier-in-IRI-slot" "def t($a,$b) topic1 ^$a. topic2 ^$b. end t(<http://www.example.org/>,^<http://www.example.org/>)")
(control "second-subject-locator-in-IRI-slot" "def t($a,$b) topic1 =$a. topic2 =$b. end t(<http://www.example.org/>,=<http://www.example.org/>)")
(with-open-file (out (concatenate 'string (uiop:getenv "TOPIC_MAPS_20J_OUTPUT") "/controls.json") :direction :output :if-exists :supersede)
  (topic-maps.test-foundation::emit-json-value (coerce (nreverse *rows*) 'vector) out) (terpri out))
