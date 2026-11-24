# TMDM coverage matrix

Clause-by-clause coverage of the Topic Maps Data Model by `topic-maps/tmdm`,
established by reading the source at commit
`88994c1b9e1edbf13e665e984a5c9c3b2cdf7575` and extended by the readers for
TMDM 7.2 and 7.3 described below.

The matrix keeps two questions apart:

- **Norm coverage**: is the structure or rule of the clause represented and
  enforced by the model?
- **API**: does the library offer a function to read or state it?

A missing reader is a functional gap of the Common Lisp library. By itself it
is not evidence of a conformance defect.

## Sources

The texts consulted are the public HTML texts, not the editions sold by ISO.
Every clause number below refers to them.

| Document | URL | Dated | SHA-256 of the retrieved octets |
|---|---|---|---|
| TMDM (ISO/IEC 13250-2) | https://www.isotopicmaps.org/sam/sam-model/2006-06-18/ | 2006-06-18 | `7f2fd03605d93c4c4c7759da1bcd1024fb0204dd34b522eff59a2ebdfb2a133b` |
| TMDM, later text | https://www.isotopicmaps.org/sam/sam-model/ | 2008-06-03 | begins `82d492565d9cef8e` |
| TMDM errata | https://www.isotopicmaps.org/sam/errata.html | 2008-06-03 | `cb7705d6abf8fdd0351d3b9c2c9c2ec795a36ca08cc151c15b29c277f15631d2` |

The two TMDM texts differ in clause 7.5 (the default name type identifier) and
in the wording of clause 6.3, point 5. The clauses 7.2 and 7.3 are the same in
both. CTM and CXTM coverage is tracked case by case in
[the conformance matrix](slice-22a-conformance-matrix.md) and
[the normative decisions](slice-22c-normative-decisions.md).

## Matrix

"Tests" names the suites in `tests/` that exercise the row. File references are
to `src/tmdm/` unless a directory is given.

| Clause | Subject | Source | Tests | Norm coverage | API |
|---|---|---|---|---|---|
| 4.2–4.3 | Locators, strings, sets, null; equality by exact character sequence | `items.lisp`, `merging.lisp` | identity, merging | covered | — |
| 4.4 | Datatypes: any absolute datatype locator; string, IRI (absolute), integer, decimal, date and dateTime values validated | `occurrences.lisp`, `variants.lisp` | occurrence, integer, decimal, date, dateTime suites | covered; `anyType` values only through the XTM/XML path | readers and constructors |
| 5.1 | Item Identifiers on all seven item kinds; duplicate Item Identifiers on different items are an error | `item-identifiers.lisp` | `item-identifiers.lisp` | covered | `item-identifiers`, `add-item-identifier` |
| 5.2 | Topic Map item: topics, associations, reifier, item identifiers | `items.lisp` | reification, import | covered | readers |
| 5.3.2 | Subject Identifiers and Subject Locators as separate properties | `merging.lisp` | merging | covered | readers, `add-topic-identifier` |
| 5.3.3 | Scope as a set of Topics of the same map; the empty set is the unconstrained scope | `merging.lisp` | `ctm-scopes.lisp` | covered; how a scope defines a context is left open by the clause | scope readers |
| 5.3.4 | Reification within one map; a Topic cannot be reified | `reification.lisp` | `reification.lisp` | covered | `item-reifier`, `set-item-reifier`, `topic-reified` |
| 5.3.5 | Topic properties; computed roles played, reified and parent; the equality rule | `merging.lisp`, `items.lisp` | `merge-graphs.lisp`, `normalization-index.lisp` | covered | readers, `merge-topics` |
| 5.3.5 | Constraint "Topic identifier required" | `intern-topic` is the only constructor and always supplies a locator | not searched for a dedicated negative test | enforced by construction | `intern-topic` |
| 5.4 | Topic Name items and their equality | `merging.lisp` | `ctm-typed-names.lisp` | covered | `add-name`, readers |
| 5.5 | Variant items; scope a true superset of the Name's scope | `variants.lisp` | `ctm-variants.lisp` | covered | `add-variant`, readers |
| 5.6 | Occurrence items and their equality | `occurrences.lisp` | `ctm-occurrences.lisp` | covered | `add-occurrence`, readers |
| 5.7–5.8 | Association items (non-empty Role set) and Role items; equality | `associations.lisp` | `association-graphs.lisp`, `association-index.lisp`, arity | covered | `make-association`, readers |
| 6.1–6.7 | Merging of every item kind, including merging of Reifiers | `merging.lisp`, `associations.lisp`, `occurrences.lisp`, `variants.lisp`, `reification.lisp` | merging, reification | covered | `merge-topics`, `normalize-topic-map` |
| 6 | Taking over the content of another map | `import.lisp` | `map-import.lisp` | covered; the source map's own identifiers and reifier are not imported | `import-map-content` |
| 7.1 | Core Subjects cannot be merged with one another | `core-subjects.lisp` | `ctm-type-relationships.lisp` | covered for the eight identifiers of the 2006-06-18 text | `core-subject-identifiers` |
| 7.2 | The type-instance relationship | written by `ctm/reader.lisp` (`isa`) and `xtm/reader.lisp` (`instanceOf`) | 13 original inputs; `core-relationships.lisp` | covered: the Association is created and stored as the clause states | readers added: `type-instance-relationship`, `topic-type-associations`, `topic-instance-associations` |
| 7.3 | The supertype-subtype relationship | written by `ctm/reader.lisp` (`ako`) | as above | covered as stated; inferred relationships are not materialized, which the clause does not require | readers added: `supertype-subtype-relationship`, `topic-supertype-associations`, `topic-subtype-associations` |
| 7.4 | Sort names | the locator constant only | — | a sort Variant can be stored like any Variant | no reader; deferred |
| 7.5 | The default name type | implicit: `items.lisp`, `merging.lisp`; explicit: `ctm/reader.lisp`, `xtm/reader.lisp` | `ctm-typed-names.lisp`, `default-name-types.lisp` | both documented identifiers are handled as ordinary, different Subject Identifiers | `default-name-type-identifier` returns `.../topic-name` |

The XTM suites need SBCL 2.5.4 and the patched CXML sources. Where those are
absent they are not run; rows that depend on the XTM path say so.

## Findings

**N1 — two default name type identifiers.** The 2006-06-18 text names
`.../model/name-type` in clause 7.5; the 2008-06-03 text names
`.../model/topic-name`. Both are supported as different identifiers and are
never equated automatically. Which text is authoritative is not decided here.
See [Two documented default name type identifiers](reading-type-relationships.md#two-documented-default-name-type-identifiers).

**N2 — edition boundary.** The editions published by ISO were not consulted.

**N3 — relationship recognition belongs in the library.** Before the readers
existed, a client had to recognize type-instance Associations itself. A reading
that compares only a Topic's first Subject Identifier, or that does not require
exactly two Roles, departs from clause 7.2. The readers apply the clause as
written.

**N4 — clients that label default name types.** A client that recognizes the
default name type only by `default-name-type-identifier` does not recognize a
Name Type carrying `.../name-type`. The library offers no function listing both
identifiers; none was added.

## Not covered by this matrix

Inference over supertype-subtype relationships, evaluation of Scope as a
context, sort order of sort names, and any change to the Core Subject set.
