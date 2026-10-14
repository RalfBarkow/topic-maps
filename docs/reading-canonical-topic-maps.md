# Reading Canonical Topic Maps

This records Slice 4. [Slice 5](reading-first-occurrences.md) extends the model
with Occurrences and supersedes the corresponding limits below.

Slice 4 compares the existing model with the original CXTM, rather than using
only property observations. It adds no CTM syntax or TMDM properties. The pinned
CTM draft remains 2010-03-31 at `cd165b150176c1d6842b37be9cc9051b40d4996b`.

## Normative basis and implementation

Source: [published CXTM text](https://www.isotopicmaps.org/cxtm/cxtm.html),
identified as the published version by the [editors' index](https://www.isotopicmaps.org/cxtm/).
Its HTML header retains the editorial date 2009-01-27. The ISO edition is
[ISO/IEC 13250-4:2009](https://committee.iso.org/standard/52120.html).
Baselines are independent test evidence, not the definition of canonicalization.

| CXTM clauses | Implemented responsibility | Source |
| --- | --- | --- |
| 3.1, 3.3–3.5 | Document, map, topics, identifiers, roles-played | `src/cxtm/canonicalizer.lisp:125` |
| 3.6, 3.9–3.10 | Names, associations and roles | `src/cxtm/canonicalizer.lisp:165` |
| 3.11–3.12 | Current null reifiers / empty scopes have no representation | Model schema restriction; `validate-map:73` |
| 3.13, 3.15–3.17 | Identifiers, topic references, string values | `emit-locators:117`, serialization below |
| 3.18 | Locator rewriting with explicit base | `normalized-locator:11` |
| 3.19–3.23 | Numbering, NFC, Infoset defaults | Serializer; `src/cxtm/unicode.lisp:29` |
| 4.1, 4.3–4.7 | Set, locator, Topic and Name comparisons | `canonicalizer.lisp:27–50` |
| 4.10–4.11 | Association and Role comparisons | `canonicalizer.lisp:51–64` |
| XML-C14N 1.0 §2.3 | UTF-8, XML escaping, expanded empty elements | Serializer and `canonicalize-octets` |

Mixed-type comparison (§4.2), Variants (§§3.7, 4.8), Occurrences (§§3.8, 4.9)
and datatype canonicalization (§3.14, numeric/date parts of §3.16) are not
implemented. The existing properties being compared are homogeneous sets.
The model has no nonempty Scope, Reifier or non-Topic item identifier properties.
An extended item class is rejected, not projected onto a smaller schema.

## Document IRI and base locator

The reader keeps absolute locators. The executor supplies the **same explicit
Document IRI** as the CXTM Base Locator. For `simple.ctm`, this is:

```
https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/simple.ctm
```

Its Topic's Item Identifier ends in `simple.ctm#topic`; §3.18 rewrites it to
`#topic`. External locators retain their absolute spelling where no base prefix
matches. The comparison reads the original baseline bytes, without trimming,
XML reparsing, IRI resolution or XML normalization. Checkout paths never enter
the logical IRIs. Equality under different chosen bases does not establish
shared absolute Subject Identity or cross-document merging. Tests also cover sibling paths, upward prefix search, queries,
fragments, trailing slashes, opaque IRIs and the specified literal prefix match.

**Interpretation point:** §3.1 step 2 inserts LF after every element, including
the document element. This implementation retains that LF. Generic
[XML-C14N §2.1](https://www.w3.org/TR/2001/REC-xml-c14n-20010315)
discards whitespace outside the root when reparsing XML. Therefore reparsing
and generic XML canonicalization alone are not the CXTM byte oracle here.
The supplementary Python XML check restores the specifically required root LF;
the actual baseline comparison performs no such modification. This distinction
is explicit rather than an undisclosed whitespace tolerance.

## Public API and inspection

The independent `topic-maps/cxtm` system depends only on `topic-maps/tmdm`.
Its runtime uses ANSI Common Lisp, without Python, a CTM dependency or a
second model. The three public functions require an explicit absolute base:

```lisp
(topic-maps.cxtm:canonicalize map :base-locator iri) ; string
(topic-maps.cxtm:canonicalize-octets map :base-locator iri) ; UTF-8 byte vector
(topic-maps.cxtm:write-cxtm map pathname :base-locator iri) ; file, returns pathname
```

To inspect `name.ctm` in a fresh process:

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps/cxtm")
(asdf:load-system "topic-maps")
(defparameter *case*
  (first (topic-maps.test-foundation:select-cases
          (topic-maps.test-foundation:discover-corpus) :id "ctm/in/name.ctm")))
(defparameter *iri* (topic-maps.test-foundation:test-case-document-iri *case*))
(defparameter *map*
  (topic-maps.ctm:deserialize-file
   (topic-maps.test-foundation:test-case-source-pathname *case*) :document-iri *iri*))
(describe *map*)
(describe (first (topic-maps.tmdm:topic-names
                  (first (topic-maps.tmdm:topic-map-topics *map*)))))
(write-string (topic-maps.cxtm:canonicalize *map* :base-locator *iri*))
```

Actual output and original expected output are identical (328 UTF-8 bytes,
including the final LF):

```xml
<topicMap>
<topic number="1">
<itemIdentifiers>
<locator>#topic</locator>
</itemIdentifiers>
<name number="1">
<value>Name</value>
<type topicref="2"></type>
</name>
</topic>
<topic number="2">
<subjectIdentifiers>
<locator>http://psi.topicmaps.org/iso13250/model/topic-name</locator>
</subjectIdentifiers>
</topic>
</topicMap>
```

## Purity and boundaries

Canonicalization validates live membership/parents/references, sorts **copies**,
and assigns numbers in temporary EQ tables. It does not call `normalize-topic-map`,
merge items, modify identifiers, compress forward links or replace handles.
Retained pre-merge handles still resolve through the original canonical-* APIs.
Name numbers are local to their Topic; Role numbers are local to their Association.

Role comparison inside an Association's set uses player/type signatures: parent
is fixed within that context. Comparing Association signatures avoids recursively
comparing the same parents through their Roles. Global roles-played comparison
also compares parent Associations when player/type tie. Separate tests distinguish
Role type order from parent order.

Unicode data are pinned to 15.1.0. NFC includes recursive canonical decomposition,
stable combining-class ordering, blocked composition, exclusions and algorithmic
Hangul. `scripts/generate-nfc-data.py` regenerates the committed facts offline
with Python UCD 15.1.0; it is not invoked during deserialization/canonicalization.
Unassigned characters in that version yield `cxtm-unsupported` with
`:unsupported-unicode-version`. XML-inexpressible text yields `cxtm-error` with
`:xml-character`. Private-use characters are supported where XML permits them.

If distinct Topics have identical **normalized** identity keys, the canonicalizer
raises `cxtm-unsupported` / `:ambiguous-topic-order`. It does not invent an
address-based ordering or perform an additional merge. Unknown/extended model
classes raise `:unsupported-information-item`; stale/foreign live references
raise `:invalid-topic-reference`. Missing/relative base raises `:invalid-base-locator`.
No complete IRI validator, general XML canonicalizer, Occurrences, Variants,
nonempty Scope, Reification, additional identifier-bearing items, Templates,
cross-document merging or HyperDoc integration is supplied by this slice.
