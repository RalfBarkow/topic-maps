# Reading CTM Mergemap

Slice 19B builds on `9ce2a2b5116edfd921a5240efcb2f604f9523693`.
The corpus remains pinned at `cd165b150176c1d6842b37be9cc9051b40d4996b`.

## Normative basis

[CTM §3.16.3](https://www.isotopicmaps.org/ctm/ctm.html) productions 74–75
require resource and notation IRI references, immediate deserialization into a
separate model instance and addition of its Topics/Associations. §§3.2,
3.3.3–3.3.5 govern document order, Document IRI, relative resolution and QNames.
Both CTM and XTM notation support are mandatory for a conforming processor;
this slice implements CTM only. Unsupported notations are errors.

[TMDM §§5–6](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
provide identity, item equality, reference replacement and merging; §7.1 protects
Core Subjects. [CXTM §3.18](https://www.isotopicmaps.org/cxtm/cxtm.html)
explains base-relative locators in the supplied baselines. TMDM/CXTM implementations
are unchanged in this slice. The published standards outrank draft-era baselines.

## Public resolver API

`deserialize-string` and `deserialize-file` accept two additional keywords:

- `:resource-resolver`: a function or NIL (default).
- `:max-resource-depth`: a nonnegative integer, default 32; zero disables imports.

The resolver is called as:

`(funcall resolver absolute-resource-iri :purpose :mergemap :from-document-iri parent-document-iri :notation notation-iri)`

Return two values: an octet vector and a string source key (or NIL). Any vector
of integer octets 0–255 is accepted, including an empty vector. NIL as first
value means unavailable/declined. NIL as second value defaults the diagnostic
source key to the resource IRI. The key never becomes the Document IRI. The
resource IRI, resolved by the existing IRI/QName reader, is the imported
Document IRI. A local filename used as a source key does not alter identity.

No implicit file or HTTP resolver exists. `deserialize-file` reads only the
explicit root file; imported bytes must still be supplied by the caller.
A finite IRI-to-bytes table suffices, and both original and synthetic tests use
one. The existing strict UTF-8 decoder/BOM handling is reused; other encodings
remain outside the reader subset. The existing absolute, fragment-free Document
IRI API boundary is retained.

## Executable public inspection

The following runs from the repository root in a fresh Lisp process. The bytes
`#(97 46)` are exactly the CTM document `a.`. URNs here are explicit example
Document IRIs, not retrievable addresses or persistent object handles.

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/ctm")
(let ((calls 0))
  (multiple-value-bind (map counter)
      (topic-maps.ctm:deserialize-string
       "%mergemap <urn:child> <http://psi.topicmaps.org/iso13250/ctm>"
       :document-iri "urn:parent" :source-name "memory:parent"
       :resource-resolver
       (lambda (iri &key purpose from-document-iri notation)
         (assert (string= iri "urn:child"))
         (assert (eq purpose :mergemap))
         (assert (string= from-document-iri "urn:parent"))
         (assert (string= notation "http://psi.topicmaps.org/iso13250/ctm"))
         (incf calls)
         (values #(97 46) "memory:child")))
    (let ((topic (first (topic-maps.tmdm:topic-map-topics map))))
      (assert (= calls 1))
      (assert (= counter 0))
      (assert (eq map (topic-maps.tmdm:topic-parent topic)))
      (assert (equal '("urn:child#a") (topic-maps.tmdm:topic-item-identifiers topic)))
      (describe map)
      (describe topic)
      (format t "~&MERGEMAP-INSPECTION-PASS: actual Topic with child Document IRI; parent is the caller Map.~%"))))
```

## Actual original contracts

Every original retains its deterministic Document IRI:
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/<case-id>`.
The finite resolver table maps the corpus auxiliary IRIs to their unchanged
binary files. Source keys are corpus IDs, e.g. `ctm/in/mergemap.sub`.

| Original positive contract | Resource relative to its Document IRI | Expected/observed model | CXTM bytes |
|---|---|---|---:|
| `ctm/in/mergemap.ctm` | `mergemap.sub` | 7 Topics, 2 Associations, 4 Roles | 1511 |
| `ctm/in/mergemap-syntax-qname.ctm` | `mergemap.sub` | Same graph; notation `syn:ctm` resolves to the CTM IRI | 1511 |
| `ctm/in/mergemap-template.ctm` | `mergemap-template.sub` | 7 Topics, 2 Associations, 4 Roles; independent same-named Templates | 1529 |
| `ctm/in/mergemap-tm-reifier.ctm` | `mergemap-tm-reifier.sub` | One ordinary Topic, no target Map Reifier | 134 |

For the first three cases, parent `#lars`/`#person` and resource-local
`mergemap*.sub#lars`/`mergemap*.sub#person` are four distinct actual Topics.
Three Core Subject Topics (type-instance, instance, type) are shared by the
Associations through canonical references. Each Association relates its own
lars/person pair. No Include identifier aliases are created. The last case
copies the Topic identified by `mergemap-tm-reifier.sub#tm`; its source Map's
Reifier edge does not become a target Map edge.

| Original negative contract | Actual required diagnostic | Resolver calls |
|---|---|---:|
| `ctm/invalid/mergemap-missing-syntax-iri.ctm` | `CTM-REJECTION :EXPECTED-MERGEMAP-NOTATION`, character 35 | 0 |
| `ctm/invalid/mergemap-template.ctm` | `UNDEFINED-TEMPLATE :UNDEFINED-TEMPLATE`, character 72 | 1 |
| `ctm/invalid/mergemap-unknown-syntax.ctm` | `CTM-REJECTION :UNKNOWN-MERGEMAP-NOTATION`, character 0 | 0 |

The invalid Template resource has key `ctm/invalid/mergemap-template.sub`, not
`ctm/in/mergemap-template.sub`. Its definition is parsed successfully into its
own register. Calling that Template in the parent fails because definitions are
not imported. Neither a missing file nor a premature unsupported-directive
error counts as this rejection.

The actual XML results are saved under `reports/slice-19b/actual/`; exact source,
resource arguments, observed model properties and diagnostics appear in
`mergemap.json`. The full CXTM report independently checks the unchanged baseline
bytes. These are executed original contracts, separate from synthetic model tests.

## Execution, namespaces and diagnostics

`read-directive` dispatches the existing Prefix reader and the new Mergemap
reader. The latter reads both IRI references, classifies the notation, requests
bytes, calls the existing CTM deserializer and then calls only
`topic-maps.tmdm:import-map-content`. It resumes the parent parser afterwards.

A fresh child parser has independent Prefixes, Templates, named Wildcards,
Document IRI and default Wildcard IRI/Counter. Parent overrides are not passed as
child wildcard state, and the child's final Counter is not assigned to the
parent. The same resolver and configured depth limit remain available for nested
resources. Each completed repeated directive calls the resolver and deserializes
again; there is no global imported-resource cache.

Cycle detection checks active Document IRIs. The maximum depth and cycle policy
signal `CTM-UNSUPPORTED :RESOURCE-DEPTH-LIMIT` / `:CYCLIC-MERGEMAP`; these are
resource policies, not additional normative CTM rejection rules.

A missing resolver signals `CTM-UNSUPPORTED :RESOURCE-RESOLVER-REQUIRED`.
Resolver exceptions, refusal/missing bytes and invalid results respectively
signal `CTM-RESOURCE-ERROR :RESOURCE-RESOLVER-FAILURE`, `:RESOURCE-UNAVAILABLE`
and `:INVALID-RESOURCE-RESULT`. Configuration errors use the same non-rejection
condition family. Malformed child CTM retains its specific rejection class/code,
source key and character/byte location. `error-context` adds Mergemap frames with
parent source, Document IRI, directive position, resource IRI, notation and child
source key. Printed diagnostics also show this chain. Imported TMDM conflicts
are reported at the parent directive with their existing specific codes.

Synthetic tests instrument the real public import in the fresh process to
observe Source/Target objects, held handles and EQ relations, then restore its
function binding. Metadata tests add non-Topic Item Identifiers through the
TMDM API before importing; they do not claim CTM syntax for those identifiers.
Both successful source preservation and atomic conflict rejection are checked
through raw slots/handles and CXTM. The transaction boundary is the individual
TMDM import, not arbitrary resolver side effects or the entire document parse.

## Remaining limits

The standard XTM IRI is recognized as `CTM-UNSUPPORTED :XTM-MERGEMAP-NOTATION`;
`mergemap-xtm.ctm` remains NOT-RUN. This is partial CTM support, not full processor
conformance. `%include`, Include aliases, Template transport and XTM parsing
remain unimplemented. The two Include norm/corpus questions recorded in the
Slice 19 investigation remain explicitly open; this slice makes no finding
that resolves either one. The two known DateTime baseline FAILs are unchanged.
