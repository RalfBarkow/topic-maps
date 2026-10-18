> Historical Slice 0 inventory below. Current Slice 18 implementation and the
> explicit Template exclusions are documented in
> [Reading CTM Templates](reading-ctm-templates.md) and
> [Slice 18 validation](slice-18-validation.md). The historical “No” column below
> describes Slice 0, not the current reader.

# Coverage and standards traceability

Three independent questions are recorded separately: specification coverage,
corpus evidence and Common Lisp implementation. **CTM parsing/deserialization
is implemented for none of these features in Slice 0.** Corpus files provide
expected contracts; they are not executed and none is PASS.

Normative reference: [ISO/IEC 13250-6:2010, consulted CTM text](https://www.isotopicmaps.org/ctm/ctm.html).
TMDM semantics refer to the [2006 edition](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/).
The corpus targets the **CTM draft dated 2010-03-31**; passing it alone cannot
establish full published-edition conformity. Revisions are pinned in inventory.

## Reviewed Slice 1 subjects

Paths in this table are relative to `vendor/cxtm/ctm`; every listed file exists
and its contents were inspected. Clause associations were checked against the
consulted normative text and are recorded on the corresponding case records.
They identify applicable clauses, not exhaustive coverage of those clauses.

| Feature specified by CTM | Evidence in corpus | Verified normative clauses | Implemented in CL? |
| --- | --- | --- | --- |
| Local Topic Identifiers | `in/simple.ctm` | [3.3.6](https://www.isotopicmaps.org/ctm/ctm.html#sec-topic-identity), 3.8, 3.2 | No |
| Subject Identifiers | `in/subject-identifier.ctm`, `in/topic-subject-identifier.ctm` | 3.3.6; 3.8 or 3.9 respectively | No |
| Subject Locators | `in/subject-locator.ctm`, `in/topic-subject-locator.ctm` | 3.3.6; 3.8 or 3.9 respectively | No |
| Item Identifiers | `in/item-identifier.ctm`, `in/topic-item-identifier.ctm` | 3.3.6; 3.8 or 3.9 respectively | No |
| Simple Topic Names | `in/name.ctm`, `in/name2.ctm` | [3.11](https://www.isotopicmaps.org/ctm/ctm.html#sec-name), 3.8 | No |
| Prefix resolution | `in/prefix-duplicate.ctm`, `in/prefix-multiline.ctm`, `invalid/prefix-undefined.ctm` | [3.3.4](https://www.isotopicmaps.org/ctm/ctm.html#sec-creating-iris-from-qnames), [3.16.1](https://www.isotopicmaps.org/ctm/ctm.html#dir-prefix); multiline also 3.3.1 | No |
| Document IRI handling | `in/simple.ctm`, `in/subject-identifier-relative.ctm`, `in/subject-locator-relative.ctm`, `in/item-identifier-relative.ctm` | 3.2, [3.3.3](https://www.isotopicmaps.org/ctm/ctm.html#sec-creating-iris), 3.3.6 | No |

The foundation assigns explicit fixture Document IRIs; that metadata operation
is not an implementation of CTM's resolution/deserialization rules.

## Other represented features

Representative inputs were inspected to establish that the corpus includes
these constructs. The specification defines them in the indicated sections;
individual edge-case mappings and draft/final alignment still require review.
These cases keep empty clause lists until that review is done.

| Corpus feature | Representative input | Relevant section / mapping review | Implemented? |
| --- | --- | --- | --- |
| Associations and role notation | `in/association-binary.ctm` | [3.13](https://www.isotopicmaps.org/ctm/ctm.html#sec-assoc); detailed case mapping pending | No |
| Occurrences | `in/occurrence-string.ctm` | [3.10](https://www.isotopicmaps.org/ctm/ctm.html#sec-occurrence); detailed mapping pending | No |
| Variants | `in/variant.ctm` | [3.12](https://www.isotopicmaps.org/ctm/ctm.html#sec-variant); detailed mapping pending | No |
| Templates | `in/template-simple.ctm` | [3.14](https://www.isotopicmaps.org/ctm/ctm.html#sec-template), 3.15; detailed mapping pending | No |
| Include and mergemap resources | `in/include.ctm`, `in/mergemap.ctm` and their `.sub` files | 3.16.2–3; detailed mapping pending | No |
| Wildcards | `in/wildcard.ctm` | 3.3.8; detailed mapping pending | No |
| Encoding | `in/encoding-8859-5.ctm` | 3.6 and 3.2; detailed mapping pending | No |

Additional filename families cover scope, reification, type-instance/subtype
shortcuts, numeric/date values, escapes and nested topics. Their clause/case
correspondence is explicitly **unreviewed** in this slice. Nothing infers a
coverage claim from the prefix of a filename alone.

## Known gaps and what Slice 1 needs

The original `MISSING.txt` is retained; its historical notes overlap some later
additions (see inventory). A comprehensive boundary-value matrix, all invalid
paths, cross-construct interactions and the 2010 draft/final audit are pending.
A canonical baseline proves neither its own correctness nor exhaustive coverage.
No canonicalizer, lexer, parser, model or deserializer exists in this project.

Slice 1 needs an actual reader and the minimal semantic support warranted by
its chosen cases. It must address local identifiers, the three explicit identity
forms, simple names, prefix binding and explicit Document-IRI resolution.
Semantic baselines must not be replaced by success flags or mocked model data.
If only a reader exists initially, canonical comparison remains NOT-RUN or
UNSUPPORTED as appropriate until a warranted comparison path exists.

## First five proposed semantic cases

1. **`ctm/in/simple.ctm`** — a single local identifier. Establishes a Topic and
   its Document-IRI-relative item identity without adding names or relations.
2. **`ctm/in/subject-identifier.ctm`** — a Topic referenced directly by a
   Subject Identifier; distinguishes subject identification from local item identity.
3. **`ctm/in/subject-locator.ctm`** — the explicit Subject Locator form; keeps
   that property distinct from a Subject Identifier.
4. **`ctm/in/item-identifier.ctm`** — the explicit Item Identifier form; completes
   the three identity forms without extra topic-tail syntax.
5. **`ctm/in/name.ctm`** — a simple name and its canonical representation,
   extending the first local Topic case with one descriptive assertion.

Each has a matching original CXTM baseline. They form a small semantic set
rather than merely accepted strings. Next come `prefix-multiline.ctm`,
`prefix-duplicate.ctm`, `invalid/prefix-undefined.ctm` and the three relative
identifier cases. These proposed selections do not change their NOT-RUN status.

**Ready for Slice 1: Yes.** The reproducible test foundation is available for
review. Slice 1 is not started automatically.
