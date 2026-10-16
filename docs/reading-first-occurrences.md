# Reading the First Four CTM Occurrences

Historical Slice 5 subset. Slice 6 supersedes the exclusions of prefixes and
explicit quoted-string datatype qualifiers below; see
[Reading Prefixes and Explicit Datatypes](reading-prefixes-and-datatypes.md).


Slice 5 starts from the clean, verified Slice 4 commit
`8036a2b1ce009218f33d300edcc5f715ec1d1124`, on `codex/ctm-slice-5`.
The upstream corpus remains pinned to
`cd165b150176c1d6842b37be9cc9051b40d4996b` (CTM draft 2010-03-31).

## Expectations established before implementation

The original sources and CXTM baselines were read before implementation.
The common document/base IRI is
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/`
followed by the input filename. Each local Topic has only Item Identifier
`Document-IRI#identifier`; Subject Identifiers/Locators are empty.
Occurrence item identifiers start empty. Each map contains no Names or Associations.
The XML datatypes are locators, not additional Topic items.

| Original case | Expected live items | Expected Occurrence properties | Baseline bytes |
| --- | --- | --- | ---: |
| `occurrence-string.ctm` | Topic Map; Topics `topic`, `occtype`; one Occurrence | Parent `topic`, Type `occtype`, Value `Occurrence`, Datatype `http://www.w3.org/2001/XMLSchema#string` | 359 |
| `occurrence-string2.ctm` | Same items/properties; no trailing semicolon | Same properties | 359 |
| `occurrence-uri-relative.ctm` | Topic Map; Topics `topic`, `occtype`; one Occurrence | Parent `topic`, Type `occtype`, Value absolute corpus IRI ending `/ctm/in/file.html`, Datatype `http://www.w3.org/2001/XMLSchema#anyURI` | 358 |
| `occurrence-two.ctm` | Topic Map; Topics `tmcl-schema`, `description`, `see-also`; two Occurrences | Parent `tmcl-schema`; Types `description`/`see-also`; multiline string and absolute HTTP locator | 730 |

The standard supplies these expectations; baseline XML independently supplies
relative locator spellings, canonical numbering and output bytes. The baseline
alone cannot tell whether a relative URI value was stored or an absolute value
was correctly normalized. Direct semantic tests must establish that distinction.

## Normative clauses

- [CTM](https://www.isotopicmaps.org/ctm/ctm.html): §§3.2, 3.3.3–3.3.7,
  3.3.11, 3.4.1–3.4.2, 3.8–3.10.
- [TMDM](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/): §§4.3,
  5.1, 5.3, 5.6, 6.2, 6.5.
- [CXTM](https://www.isotopicmaps.org/cxtm/cxtm.html): §§3.1, 3.5, 3.8,
  3.11–3.23 and 4.2–4.6, 4.9 (string/anyURI subset only).

CTM Type denotes a Topic. A literal assigns value/datatype; an IRI-form literal
uses IRI creation, including relative resolution. TMDM's IRI datatype requires
absolute locators. A quoted string is not passed through IRI resolution merely
because it resembles a URI. Explicit datatype qualifiers are recognized but
remain unsupported in this bounded reader.

An Occurrence is distinct from its Type Topic and its value. Its equality uses
value, datatype, type, scope and parent. Supported scope is empty and reifier
null. Merging equal Occurrences produces a replacement and unions item identifiers.
CXTM orders Occurrences by value, datatype, type, scope and parent; the value
is locator-normalized only for anyURI, while datatype output is not base-stripped.

## Original, unmodified sources

`occurrence-string.ctm` (no final newline):

```ctm
topic
occtype: "Occurrence";.
```

`occurrence-string2.ctm` (no final newline):

```ctm
topic
occtype: "Occurrence".
```

`occurrence-uri-relative.ctm` (initial/final newline):

```ctm

topic occtype: <file.html> .
```

`occurrence-two.ctm` (initial/final newline; indentation inside the string matters):

```ctm

tmcl-schema
  description: "A meta-schema for TMCL, describing the allowed structure
                    of TMCL schemas.";
  see-also: http://www.isotopicmaps.org/tmcl/tmcl.html .
```

## Actual objects and API contract

`occurrence` is an ordinary TMDM DEFSTRUCT. Its materialized slots are value,
datatype, type, parent, item-identifiers and the private forwarding link.
Datatype locators use the model's existing string locator representation.
Scope is implicitly empty; reifier is implicitly null. No source object or XML-only
Occurrence model is introduced.

```lisp
(topic-maps.tmdm:add-occurrence parent-topic type-topic value
  :datatype (topic-maps.tmdm:string-datatype) :item-identifiers nil)
(topic-maps.tmdm:topic-occurrences topic)
(topic-maps.tmdm:canonical-occurrence retained-handle)
(topic-maps.tmdm:occurrence-parent occurrence)
(topic-maps.tmdm:occurrence-type occurrence)
(topic-maps.tmdm:occurrence-value occurrence)
(topic-maps.tmdm:occurrence-datatype occurrence)
(topic-maps.tmdm:occurrence-item-identifiers occurrence)
```

`add-occurrence` validates before mutation, accepts string or already absolute
anyURI values, and performs duplicate replacement. It never resolves strings
against a Document IRI. Type and Parent must belong to the same map. Optional
nonempty item identifiers are supported through the model API and canonicalizer;
CTM does not assign them to Occurrences. Unequal items cannot share an Item
Identifier. Conflicts requiring Topic/Occurrence reification are explicitly
rejected; reification is not implemented as a side effect.

A replaced handle is not EQ to its replacement. Its canonical representative is:

```lisp
(eq old-occurrence new-occurrence) ; NIL after replacement
(eq (topic-maps.tmdm:canonical-occurrence old-occurrence)
    new-occurrence)               ; T
```

Public property readers resolve the Occurrence handle and return current stored
parent/type references. Topic merges rewrite those references in the live model;
readers do not hide stale Topic references by lazily canonicalizing them. Collection
readers return copies. CXTM neither merges nor compresses old handle chains.

The reported insertion ordinals are **not** CXTM numbers. In each of the first
three maps, actual Topic T1 is `topic`, T2 is `occtype`, and O1 has Parent EQ T1,
Type EQ T2. Its Item Identifiers are NIL. CXTM sorts T2 before T1, so the occurrence
appears in CXTM Topic 2 and references Topic 1 as its type.

In `occurrence-two.ctm`, actual T1 is `tmcl-schema`, T2 is `description`, T3 is
`see-also`. O1/O2 have Parent EQ T1; Types EQ T2/T3 respectively. O1's exact value
is `A meta-schema for TMCL, describing the allowed structure`, then LF, then
**20 spaces**, then `of TMCL schemas.`. O2's exact value is
`http://www.isotopicmaps.org/tmcl/tmcl.html`. Datatypes are xsd:string and xsd:anyURI;
both identifier sets are NIL. CXTM sorts Topics description=1, see-also=2,
tmcl-schema=3, and numbers the two Occurrences 1 and 2 within Topic 3.

For the relative URI case the actual O1 value is:

```
https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/file.html
```

That is a formed locator, not the raw source spelling `<file.html>`. The
original source spelling is retained separately in the evidence report. The
source has not been edited to force a baseline match. Different Document IRIs
still give local Topics different Item Identifiers; matching CXTM under different
bases is not a cross-document Subject Identity assertion.

## Executable inspection

In a fresh Common Lisp process:

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm")
(let* ((iri "https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/occurrence-string.ctm")
       (map (topic-maps.ctm:deserialize-file
             (asdf:system-relative-pathname "topic-maps/ctm" "vendor/cxtm/ctm/in/occurrence-string.ctm")
             :document-iri iri))
       (parent (first (topic-maps.tmdm:topic-map-topics map)))
       (item (first (topic-maps.tmdm:topic-occurrences parent))))
  (assert (eq parent (topic-maps.tmdm:occurrence-parent item)))
  (assert (eq (second (topic-maps.tmdm:topic-map-topics map))
              (topic-maps.tmdm:occurrence-type item)))
  (describe item)
  (describe (topic-maps.tmdm:occurrence-type item)))
```

## Implementation and limitations

- `src/tmdm/items.lisp`: Occurrence structure, canonical handle/readers.
- `src/tmdm/occurrences.lisp:41`: duplicate replacement and identifier union;
  `:55`: public construction and validation.
- `src/tmdm/merging.lisp`: property union and stored parent/type rewrites.
- `src/ctm/reader.lisp:47`: IRI locators without Topic creation;
  `:87`: literal semantics and errors; `:123`: Type Topic/reference mapping.
- `src/cxtm/canonicalizer.lisp:51`: value-kind and Occurrence comparison;
  serializer emits value, datatype, type and identifiers after Names, before roles-played.
- `tests/ctm-occurrences.lisp`: original sources, direct object/merge tests and
  independent construction-order variants. Python independently checks the
  actual properties and raw baseline bytes.

The existing URI lexer/QName rules are retained. Use layout where a colon would
otherwise form a QName (for example before an undelimited URI literal).
Prefix directives, triple-quoted strings, explicit `^^` datatype-qualified CTM
literals, numeric/date values, nonempty Scope, Reification, Variants, Templates,
cross-document merging and HyperDoc integration remain unsupported. A missing
Occurrence value is CTM-REJECTION; recognized excluded literals are CTM-UNSUPPORTED;
unbound QNames preserve the specific UNDEFINED-PREFIX rejection.

There is no full IRI grammar validator in the model API: locator arguments must
already be validated/resolved. CXTM's Unicode 15.1.0 bound and explicit rejection
of ambiguous normalized Topic keys remain unchanged. The documented Slice 4
root-LF interpretation is retained. All four selected cases avoid excluded features.
