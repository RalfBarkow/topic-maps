# Reading Date Occurrences

## Rules established before implementation

Base: accepted Slice 8 `195d5f5444d776096b765d04c815c23c3db5f84c`;
initial branch `codex/ctm-slice-8`, clean index/tree. The five original inputs,
five CXTM baselines and five original invalid inputs were read first.
Corpus pin remains `cd165b150176c1d6842b37be9cc9051b40d4996b`.

- [Published CTM §3.4.1, printed p.5](https://cdn.standards.iteh.ai/samples/43940/6663ee28c1604551ac6adc02e22c6bb6/ISO-IEC-13250-6-2010.pdf)
  requires directly supported date literals to be XSDT-valid and assigns xsd:date.
  Recognition remains in the existing numeric/date token path. Bare dates have
  no timezone; their final dot is CTM punctuation. §3.2 removes a leading UTF-8 BOM.
  The [HTML mirror](https://www.isotopicmaps.org/ctm/ctm.html) production 35
  omits days 01–09; the published preview's normative XSDT validity rule and
  the selected test inputs support them. `occurrence-date2` explicitly tests
  that draft error. This discrepancy is recorded, not silently copied into the
  reader or presented as a verified correction of the unavailable Annex grammar.
- [TMDM §§4.3–4.4, 5.6, 6.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/):
  the existing Occurrence stores a Unicode value string and a datatype locator.
  Parent and Type remain Topic references. Equality/merging compare stored
  properties, not mathematical equivalence or output XML. Canonical handles and
  identifier union retain their existing contract.
- [CXTM §§3.16, 4.9](https://www.isotopicmaps.org/cxtm/cxtm.html):
  render the canonical datatype lexical form, without mutation. Order by stored
  value string, then datatype, Type, Scope and Parent, not chronological order.
- [XML Schema Part 2 Second Edition §§3.2.7.1, 3.2.9–3.2.9.2, 4.3.6, D, E.1](https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/#date):
  years have at least four ASCII digits; no plus, no zero year, no leading zero
  on an extended year. Negative years use this edition's numbering. Month/day
  have two digits; calendar validity includes month lengths and Gregorian
  divisibility by 4, 100 and 400. Whitespace collapse affects interpretation,
  while qualified stored strings remain unchanged. Timezone-free valid dates
  are canonical once surrounding XML whitespace is removed.

Bare literal deserialization uses the established canonical-string policy;
qualified quoted strings and the model API retain their valid lexical strings.
This policy is distinct from TMDM equality. No local timezone/calendar API,
floating point, Lisp reader or EVAL is used. Extended years are validated with
character processing and a bounded modulo-400 accumulator, not a fixed-width year.

Valid timezone-qualified explicit xsd:date strings can be represented and
validated lexically; CXTM reports them explicitly unsupported. XSD date timezone
normalization (§3.2.9.2) needs recoverable-timezone/day adjustment, not simple
DateTime-to-UTC truncation. This slice implements neither conversion. Bare CTM
dates with timezone suffixes are rejected as outside the date grammar.

## Executable inspection

From the repository root, with the established SBCL runtime:

```lisp
(require :asdf)
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps/cxtm")
(let* ((map (topic-maps.ctm:deserialize-file
             #p"vendor/cxtm/ctm/in/occurrence-date.ctm"
             :document-iri "https://example.invalid/occurrence-date.ctm"))
       (owner (find-if #'topic-maps.tmdm:topic-occurrences
                      (topic-maps.tmdm:topic-map-topics map)))
       (item (first (topic-maps.tmdm:topic-occurrences owner))))
  (describe item)
  (describe (topic-maps.tmdm:occurrence-type item))
  (list (eq owner (topic-maps.tmdm:occurrence-parent item))
        (topic-maps.tmdm:occurrence-value item)
        (topic-maps.tmdm:occurrence-datatype item)
        (topic-maps.cxtm:canonicalize map
          :base-locator "https://example.invalid/occurrence-date.ctm")))
```

Public additions in `topic-maps.tmdm`: `date-datatype`, `date-lexical-p`,
`canonical-date-lexical-form`. The latter returns a string and `:CANONICAL`
for supported valid data, or NIL plus an invalid-date code / `:UNSUPPORTED-TIMEZONE`.
Existing deserializer, `add-occurrence`, `canonical-occurrence` and CXTM APIs
remain the entry points; no separate Date information-item class is introduced.

## BCE calendar qualification

XML Schema 1.0's year labels omit zero. For BCE leap validation this slice
applies the divisibility formula to the signed lexical year, following E.1's
`yearValue` arithmetic (thus `-0004-02-29` is accepted, `-0100-02-29` rejected).
No astronomical-year shift is silently introduced. This is an explicit 1.0
interpretation, not a claim that BCE leap-day semantics were unambiguous:
[W3C's later clarification](https://www.w3.org/TR/2012/REC-xmlschema11-2-20120405/#dateTime)
acknowledges the ambiguity of XSD 1.0 for BCE leap years. XSD 1.1 is not used to
permit year zero or change the selected edition. All five original positive
fixtures avoid BCE February 29, so this qualification does not affect their
conformance comparisons. Future date arithmetic must revisit this decision.

## Original sources and observed information items

All Dates use the locator `http://www.w3.org/2001/XMLSchema#date`.
No datatype Topic is synthesized. Each document creates one Topic Map and
one owner Topic with its local Item Identifier `DocumentIRI#topic`; its type
Topics have `DocumentIRI#occtype`, or `#o1` through `#o4` for date3. SI/SL,
Names, Associations and Occurrence Item Identifiers are empty. Parent/Type
are the actual stored canonical Topic objects, not copied labels.

The deterministic Document IRI is
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
plus `ctm/in/filename.ctm` (or `ctm/invalid/filename.ctm`). The same absolute
IRI is the CXTM Base Locator, preserving the accepted relative-locator policy.

| Original positive file | Stored value strings | Topics / Occurrences | Exact CXTM bytes | Result |
|---|---|---|---:|---|
| occurrence-date.ctm | `1976-09-19` | 2 / 1 | 357 | PASS |
| occurrence-date2.ctm | `1976-10-09` | 2 / 1 | 357 | PASS |
| occurrence-date3.ctm | `0001-12-02`, `0011-12-02`, `0111-12-02`, `1111-12-02` | 5 / 4 | 1066 | PASS |
| occurrence-date-negative.ctm | `-1976-09-19` | 2 / 1 | 358 | PASS |
| occurrence-date-another-century.ctm | `191976-09-19` | 2 / 1 | 359 | PASS |

In model construction order the owner has ordinal 1 and its Type Topics have
ordinals 2 onward. CXTM's independent numbering places the Type Topic(s) first,
owner last, and numbers each owner's Occurrences from 1. `dates.json` records
actual properties and references; `cxtm.json` separately records full actual and
expected XML. The source records in dates.json round-trip to unchanged input bytes.
The following readable code fences omit trailing whitespace; the report retains
it exactly, including BOMs.
The two BOM-bearing examples retain U+FEFF in the source records; only the
reader's byte-to-character deserialization removes the leading BOM.

### occurrence-date.ctm

```text
topic
occtype: 1976-09-19.
```

### occurrence-date2.ctm — starts with UTF-8 BOM EF BB BF

```text
﻿#
# Tests if implementations did not copy and paste the
# error from the CTM draft 2010-03-29
# <http://projects.topicmapslab.de/issues/2563>
#
topic
occtype: 1976-10-09.
```

### occurrence-date3.ctm — starts with UTF-8 BOM EF BB BF

```text
﻿#
# Different valid dates acc. to <http://www.w3.org/TR/xmlschema-2/#dateTime>
#
topic
  o1: 0001-12-02;
  o2: 0011-12-02;
  o3: 0111-12-02;
  o4: 1111-12-02
.
```

### occurrence-date-negative.ctm

```text
topic
occtype: -1976-09-19.
```

### occurrence-date-another-century.ctm

```text
topic
occtype: 191976-09-19.
```

| Original negative file | Specific rejection | Source position | Result |
|---|---|---|---|
| date-invalid-day.ctm | `INVALID-DATE-DAY` | line 2, column 14 | PASS |
| date-invalid-month.ctm | `INVALID-DATE-MONTH` | line 2, column 14 | PASS |
| date-invalid-year.ctm | `INVALID-DATE-YEAR` | line 2, column 14 | PASS |
| date-invalid-year2.ctm | `INVALID-DATE-YEAR` | line 6, column 14 | PASS |
| date-invalid-year3.ctm | `INVALID-DATE-YEAR` | line 6, column 14 | PASS |

All five conditions are `CTM-REJECTION`, with character position, source name,
line and column; none is `CTM-UNSUPPORTED` or an I/O failure. No successful
TMDM result is returned. Exact source strings are in `dates.json`; readable renderings follow below.

### date-invalid-day.ctm

```text
topic
    occtype: 2000-12-32.
```

### date-invalid-month.ctm

```text
topic
    occtype: 2000-13-02.
```

### date-invalid-year.ctm

```text
topic
    occtype: 0000-01-02.  # See <http://www.w3.org/TR/xmlschema-2/#dateTime> "[...] '0000' is prohibited [...]"
```

### date-invalid-year2.ctm

```text
#
# See <http://www.w3.org/TR/xmlschema-2/#dateTime>
# "[...] if more than four digits, leading zeros are prohibited [...]"
#
topic
    occtype: 00002000-01-02.
```

### date-invalid-year3.ctm

```text
#
# See <http://www.w3.org/TR/xmlschema-2/#dateTime>
# "[...] also note that a plus sign is not permitted [...]"
#
topic
    occtype: +2000-01-02.
```

## Remaining boundaries

DateTime, DateTime conversion, date recoverable-timezone normalization,
Variants, nonempty Scope, Reification, Templates, CTM `*`, cross-document merging
and HyperDoc integration remain unsupported. Unselected imported cases remain
NOT-RUN even if their syntax is incidentally accepted. Valid explicit date
zones are recognized as such, then CXTM signals `CXTM-UNSUPPORTED` with
`:DATE-TIMEZONE-CANONICALIZATION`; malformed dates remain specific rejections.
Date-like QNames retain QName semantics and do not become literal tokens.
See `slice-9-validation.md` for execution evidence and all reproduction commands.
