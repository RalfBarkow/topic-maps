# Reading DateTime Occurrences

## Normative investigation before implementation

Base `2ad41cd1a945a4ce97824464de40646bb899259e`; clean
`codex/ctm-slice-9`; created `codex/ctm-slice-10`. All five original CTM inputs
and CXTM baselines were read unchanged before implementation.

Authorities:
- [Published CTM 3.4.1, printed p.5](https://cdn.standards.iteh.ai/samples/43940/6663ee28c1604551ac6adc02e22c6bb6/ISO-IEC-13250-6-2010.pdf#page=11): direct literals must be XSDT-valid; dateTime datatype is the XSD locator. CTM 3.2 removes a leading UTF-8 BOM. The HTML grammar has the previously documented day 01–09 omission; use the published XSDT-validity requirement.
- [TMDM 4.3–4.4, 5.6, 6.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/): stored values are Unicode strings, datatypes are separate locators; equality/duplicate removal use stored properties. Parent and Type remain Topics. Canonical handles retain the replacement-object contract.
- [CXTM 3.16, 4.9](https://www.isotopicmaps.org/cxtm/cxtm.html): dateTime output uses XSD canonical lexical form; Occurrences sort by stored value, datatype, type, scope, parent. Equal XML does not establish equal TMDM items.
- [XSD Part 2 Second Edition 3.2.7.1–3.2.7.3](https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/#dateTime): year rules inherited from Date, time component bounds; 24:00:00 denotes next-day midnight; trim fractional trailing zeroes; every timezoned canonical value uses Z, converting the instant to UTC. Zero offsets +00:00/-00:00 both map to Z. No timezone is distinct from UTC.

### A — leap seconds: a second baseline problem

[XSD 1.0 Appendix D.1](https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/#isoformats)
permits whole seconds 00–60 and arbitrary fractional precision. It explicitly
says a leap second used with inappropriate month/day is interpreted in the
following minute. Therefore `1976-09-19T12:01:60` is accepted lexical input,
but its value interpretation is `1976-09-19T12:02:00`; unchanged `:60` is not
justified by the XSD 3.2.7.2 one-to-one canonical mapping. September 19 cannot
be a D.1 candidate day even under the permitted timezone range.
This is not an actual IERS leap-second-history validation.

The pinned `occurrence-datetime2.ctm` baseline retains `:60`. Execute the
canonical comparison and record the resulting **FAIL / known normative baseline
discrepancy**, separately from successful implementation assertions. Do not
rewrite the baseline or count it PASS. Genuine candidate-day UTC leap seconds
at 23:59:60 retain 60 (fractional trailing zeroes removed). Candidate local
leap seconds without a known zone, and candidate-day wrong-time cases, are
explicitly unsupported in canonicalization: the implementation does not guess
an absent zone or silently introduce a historical leap-second database.
XSD 1.1/XPath's exclusion of leap seconds does not replace the selected XSD 1.0.

### B — nonzero timezone

XSD 3.2.7.2–3.2.7.3 and CXTM 3.16 require
`2011-01-01T00:00:00+02:00` → `2010-12-31T22:00:00Z`.
The unchanged upstream `occurrence-datetime-timezone2.ctm` baseline retains
`2011-01-01T00:00:00+02:00`. Preserve this documented discrepancy separately.
Validate/store offset-bearing qualified/API strings but do not implement
nonzero-offset canonicalization. Bare literals needing that conversion report
CTM-UNSUPPORTED; CXTM reports CXTM-UNSUPPORTED. The imported contract is NOT-RUN.
No filename-specific parsing/canonicalization rule is introduced.

## Representation policy

Reuse the existing Occurrence class. Bare supported literals use canonical
strings, as in Slices 7–9; lexer tokens retain spelling. Qualified quoted strings
and direct API strings preserve valid lexical values, including whitespace,
fractions and offset spelling. Validation precedes mutation. Datatype is never
a synthesized Topic. CXTM is pure: it trims surrounding XML whitespace and
fractional trailing zeroes, handles next-day midnight and the supported leap
interpretations without changing model strings, references or retained handles.
Date validation is reused; no system calendar, timezone or floating point.
Year rollover uses character arithmetic, including arbitrary-length years and
-0001 → 0001 with no year zero. Slice 9's documented BCE leap interpretation
remains unchanged. Date timezone canonicalization is not extended.

## Executable inspection

Run from the repository root in either supported SBCL:

```lisp
(require :asdf)
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps/cxtm")
(let* ((map (topic-maps.ctm:deserialize-file
             #p"vendor/cxtm/ctm/in/occurrence-datetime-fractional.ctm"
             :document-iri "https://example.invalid/occurrence-datetime-fractional.ctm"))
       (owner (find-if #'topic-maps.tmdm:topic-occurrences
                      (topic-maps.tmdm:topic-map-topics map)))
       (item (first (topic-maps.tmdm:topic-occurrences owner))))
  (describe item)
  (describe (topic-maps.tmdm:occurrence-type item))
  (list (eq owner (topic-maps.tmdm:occurrence-parent item))
        (topic-maps.tmdm:occurrence-value item)
        (topic-maps.tmdm:occurrence-datatype item)
        (topic-maps.cxtm:canonicalize map
          :base-locator "https://example.invalid/occurrence-datetime-fractional.ctm")))
```

Public helpers in `topic-maps.tmdm`: `datetime-datatype`, `datetime-lexical-p`,
`canonical-datetime-lexical-form`. The last returns a canonical string plus
`:CANONICAL`, or NIL with a specific invalid/unsupported reason. No DateTime
information-item class or alternative equality/merge logic is introduced.

## Original documents and observed results

The deterministic Document IRI / CXTM Base Locator remains
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
plus the corpus-relative path. Datatype is always the locator
`http://www.w3.org/2001/XMLSchema#dateTime`, never a Topic.

| Original | Stored bare value | Items | Original CXTM comparison |
|---|---|---|---|
| occurrence-datetime.ctm | `1976-09-19T12:01:01` | 2 Topics, 1 Occurrence | PASS, 370 bytes |
| occurrence-datetime2.ctm | `1976-09-19T12:02:00` | 2 Topics, 1 Occurrence | FAIL, known D.1 discrepancy; baseline `12:01:60` |
| occurrence-datetime-fractional.ctm | `2011-01-01T00:00:00.001` | 3 Topics, 2 Names, 1 Occurrence | PASS, 677 bytes |
| occurrence-datetime-timezone.ctm | `2011-01-01T00:00:00Z` | 3 Topics, 2 Names, 1 Occurrence | PASS, 674 bytes |
| occurrence-datetime-timezone2.ctm | No returned bare model; specific CTM-UNSUPPORTED | original contract NOT-RUN | documented required value `2010-12-31T22:00:00Z`; conversion unimplemented |

The first two owners have local item identifier `DocumentIRI#topic`; Type is
`DocumentIRI#occtype`. The named documents use `#some-topic` and `#datetime`
and reuse the standard default-name-type Topic. No Association or datatype Topic
is introduced. Raw Parent/Type references point to the actual canonical Topics.
Qualified/API offset values are valid stored strings, but CXTM refuses conversion.
`datetimes.json` separates actual model observations, local semantic assertions,
unsupported partial reads and normative discrepancies. `cxtm.json` contains full
actual/expected XML with separate imported `contractCounts`. Its passed/failed
check counters count assertions, not imported case outcomes.

Untouched original sources follow. The datetime2 file begins with UTF-8 BOM;
readable fences preserve U+FEFF, while the report/source bytes remain authoritative.

### occurrence-datetime.ctm

```text
topic
occtype: 1976-09-19T12:01:01 .
```

### occurrence-datetime2.ctm

```text
﻿#
# Test for leap seconds, 
# c.f. <http://projects.topicmapslab.de/issues/2563>
#
topic
occtype: 1976-09-19T12:01:60 .
```

### occurrence-datetime-fractional.ctm

```text
datetime - "datetime" .

some-topic - "some topic" ;
  datetime: 2011-01-01T00:00:00.001
.
```

### occurrence-datetime-timezone.ctm

```text
datetime - "datetime" .

some-topic - "some topic" ;
  datetime: 2011-01-01T00:00:00Z
.
```

### occurrence-datetime-timezone2.ctm

```text
datetime - "datetime" .

some-topic - "some topic" ;
  datetime: 2011-01-01T00:00:00+02:00
.
```
