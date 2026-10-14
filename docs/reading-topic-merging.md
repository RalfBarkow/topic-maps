# Reading Topic Identity and Merging

Slice 2 starts at the accepted `fb60afd548d679d83fd8ec76bc5ff384c1e23e5f`.
It adds same-map Topic merging to the existing Topic/Name model. It does not
implement associations, cross-document merging or CXTM canonicalization.

## A late identity changes earlier references

```ctm
a - "Same".
b - "Same".
a <urn:shared>.
b <urn:shared>; - "Later".
```

Document IRI: `https://example.invalid/merging.ctm`.
Before the last declaration there are three live Topics: `a`, the default
name type, and `b`. The two named Topics have separate Name objects.
After the last declaration, this implementation observes:

```text
M.TOPICS = (C TYPE)
C.PARENT = M
C.ITEM-IDENTIFIERS = {https://example.invalid/merging.ctm#a,
                      https://example.invalid/merging.ctm#b}
C.SUBJECT-IDENTIFIERS = {urn:shared}
C.SUBJECT-LOCATORS = {}
C.NAMES = (N-SAME N-LATER)
N-SAME.VALUE = "Same";  N-SAME.PARENT = C;  N-SAME.TYPE = TYPE
N-LATER.VALUE = "Later"; N-LATER.PARENT = C; N-LATER.TYPE = TYPE
TYPE.SUBJECT-IDENTIFIERS = {http://psi.topicmaps.org/iso13250/model/topic-name}
TYPE.ITEM-IDENTIFIERS = {}; TYPE.SUBJECT-LOCATORS = {}; TYPE.NAMES = {}
TYPE.PARENT = M
```

These braces denote sets, not a new CTM notation or canonical ordering.
The two identical Names coalesce after their parents become the same Topic.
No additional Subject Identifier is invented, and no identity across maps is
asserted. This is a local model observation, not a CXTM comparison result.

## Normative basis and representation

[ISO/IEC 13250-2:2006](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
§5.3.5 supplies the identity equality rules; §§6.1–6.2 require merging and
replacement of references. §5.4 defines Name equality and the computed parent;
§6.3 covers equal Name merging. The implementation creates replacement Topic
and Name items, preserves identifier unions and rewrites stored Name parent
and type references. It repeats Topic equality merging to a fixed point.

[ISO/IEC 13250-6:2010](https://www.isotopicmaps.org/ctm/ctm.html) §3.3.6
maps topic identities; §3.9 adds tail identities to the current Topic and
requires applicable merges. §3.11 supplies the existing default name type.
Semicolons separate tail statements. Topic-tail assignments create locators,
not extra Topics. The original Document-IRI resolution policy is retained.

Only implemented Topic and unscoped Name properties are materialized.
Unimplemented set properties remain implicitly empty and nullable properties
implicitly null. Reification, scope, variants, occurrences, associations and
roles cannot carry references in this model; their merging is not claimed.
Both inspected editions remain authoritative over the draft-era test corpus.

## Public model API and retained Lisp handles

| Function | Contract |
| --- | --- |
| `intern-topic map kind iri` | Lookup/create using the same identity rule as merging |
| `add-topic-identifier topic kind iri` | Add a distinct-category locator, merge as required, return the current Topic |
| `merge-topics a b` | Explicit same-map merge, return the current Topic; reject different maps before mutation |
| `normalize-topic-map map` | Merge equal Topics to a fixed point and remove equal Names; return the map |
| `canonical-topic topic` | Resolve a retained reference to a replaced Topic |
| `canonical-topic-name name` | Resolve a retained reference to a replaced Name |

Identifier kinds are `:ITEM-IDENTIFIER`, `:SUBJECT-IDENTIFIER` and
`:SUBJECT-LOCATOR`. The model accepts already resolved nonempty absolute
locator strings; CTM performs decoding, validation and resolution. Full IRI
grammar validation remains outside this slice.

`merge-topics` explicitly asserts a shared subject even without identifier
equality. The CTM reader does not use that discretionary operation: it adds
identifiers and lets the shared equality rule decide required merging.

The old objects A and B remain ordinary Lisp objects, but are removed from the
map's live Topic set. Their `EQ` identity cannot change. An internal `FORWARD`
slot records their replacement; it is bookkeeping, not a TMDM property.
Resolve retained handles before comparing them with `EQ` or using `DESCRIBE`.
These representative-resolution functions do not perform CXTM canonicalization.
Public property readers also resolve obsolete handles. Live model references
are actually rewritten, not merely concealed by those readers.

Version 0.2 makes public set readers return copies. Generated `SETF` writers
for Topic/Name properties are no longer the mutation interface. Use the above
model operations; private structure setters bypass invariants and are not API.
List ordering is observational and not normative. Pair scanning favors clarity
for small maps; this slice adds no identity index or cross-map registry.

## Load and inspect

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm")
(defparameter *map*
  (topic-maps.ctm:deserialize-string
   "a - \"Same\". b - \"Same\". a <urn:shared>. b <urn:shared>; - \"Later\"."
   :document-iri "https://example.invalid/merging.ctm"))
(describe *map*)
(describe (first (topic-maps.tmdm:topic-map-topics *map*)))
(dolist (name (topic-maps.tmdm:topic-names
               (first (topic-maps.tmdm:topic-map-topics *map*))))
  (describe name)
  (describe (topic-maps.tmdm:topic-name-type name)))
```

To inspect retained references explicitly:

```lisp
(defparameter *m* (topic-maps.tmdm:make-topic-map))
(defparameter *a* (topic-maps.tmdm:intern-topic *m* :item-identifier "urn:a"))
(defparameter *b* (topic-maps.tmdm:intern-topic *m* :item-identifier "urn:b"))
(topic-maps.tmdm:add-topic-identifier *a* :subject-identifier "urn:shared")
(defparameter *c*
  (topic-maps.tmdm:add-topic-identifier *b* :subject-identifier "urn:shared"))
(eq *a* *c*) ; => NIL: merging creates a replacement item
(eq (topic-maps.tmdm:canonical-topic *a*) *c*) ; => T
(eq (topic-maps.tmdm:canonical-topic *b*) *c*) ; => T
(describe *c*)
```

## Pinned cases and evidence boundary

Eleven additional original files are exercised: the plain/wrapped/duplicate
`topic-subject-identifier` cases; plain/wrapped/semi/duplicate
`topic-subject-locator` cases; plain/wrapped/duplicate `topic-item-identifier`
cases; and `name-duplicate.ctm`.

They use `https://ctm-tests.example.invalid/` plus pinned commit
`cd165b150176c1d6842b37be9cc9051b40d4996b`, `/`, and the original case ID.
Frozen baseline fragment locators are interpreted in that Document-IRI context.
The Python property oracle matches Topics by identifier sets and compares Name
references under that mapping. It does not rely on observation order matching
CXTM numbering and does not produce or canonicalize XML.

The original five case records remain unchanged. All 16 positive imported
CXTM-EQUAL contracts stay NOT-RUN. Only the existing undefined-prefix rejection
is an imported PASS; 272 imported contracts stay NOT-RUN. Unexecuted contracts
are unchanged. The corpus targets draft 2010-03-31 and cannot by itself prove
full ISO conformity. See `slice-2-validation.md` for execution evidence.
