# Reading Decimal Occurrences

## Rules established before implementation

Base: accepted Slice 7 `17dd58775e25ab495e3c83deb4b5a36f5e5a124b`.
The original seven CTM files and CXTM baselines were read before implementation.
The unchanged corpus pin is `cd165b150176c1d6842b37be9cc9051b40d4996b`;
it targets draft 2010-03-31, while the published standards remain authoritative.

- [CTM §3.4.1, productions 28–34](https://www.isotopicmaps.org/ctm/ctm.html):
  a decimal has a fractional digit sequence, optionally an integer component
  and sign. Decimal and Integer have separate implicit datatype locators.
  Thus `1.0.`, `.3.` and `9.3.` contain a decimal then a topic terminator;
  `1.` contains an Integer then the terminator. A qualified quoted string uses
  its specified datatype. The existing reader policy maps bare numeric values
  to canonical strings; this is a representation choice, not a claim that CTM
  mandates early canonicalization. Quoted strings retain their decoded spelling.
- [TMDM §§4.3–4.4, 5.6, 6.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/):
  Occurrence [value] is a Unicode string; [datatype] is a separate locator,
  not a Topic. Equality compares the stored string, datatype, type, scope and
  parent. The model API preserves valid strings. Mathematical equivalence alone
  does not merge different stored strings. Duplicate replacement and retained
  handles keep their existing contract.
- [CXTM §§3.14, 3.16, 4.2–4.3, 4.9](https://www.isotopicmaps.org/cxtm/cxtm.html):
  output uses the decimal's canonical lexical representation without changing
  the model. Ordering compares stored [value] strings, followed by datatype,
  Type, Scope and Parent; it does not sort numeric values or reformatted output.
- [XML Schema Part 2 §§3.2.3–3.2.3.2, 4.3.6](https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/#decimal):
  decimal values have finite decimal expansions; precision is not a separate
  value-space distinction. Lexical forms use ASCII digits and an optional sign;
  XSD also permits `1` and `1.` in explicitly typed strings. Canonical form has
  no plus, no unnecessary leading/trailing zeros, and at least one digit on
  each side of the required decimal point. Zero becomes `0.0`, including
  negative zero. XML whitespace at the ends is collapsed for datatype
  interpretation; the stored qualified string retains it. Internal whitespace,
  exponent notation and Unicode lookalike digits are invalid for this datatype.

Implementation must use pure character processing: no binary floating point,
no Lisp reader/EVAL, no precision-dependent rounding, and no numeric-based
change to TMDM equality. The existing single numeric token path is extended.
Date, DateTime, CTM `*` semantics, Scope, Reification, Variants, Templates,
cross-document merging and HyperDoc integration remain outside this slice.

## Actual information items and original baseline results

Every selected document produces one Topic Map, two Topics (`topic`, `occtype`)
and one Occurrence. Each Topic has just its absolute local Item Identifier
`DocumentIRI#identifier`; SI/SL sets, Names and Associations are empty. The
Occurrence's stored Parent is EQ the owner Topic; Type is EQ `occtype`. Its
Item Identifiers are empty. Datatype is always the locator
`http://www.w3.org/2001/XMLSchema#decimal`; no datatype Topic is synthesized.

Document IRI and CXTM Base Locator use the existing deterministic policy:
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
plus the full `ctm/in/...ctm` ID. Stored identifiers remain absolute; baseline
`#topic` / `#occtype` output follows the retained CXTM §3.18 policy.
CXTM numbers Type Topic=1, owner Topic=2, Occurrence=1, type topicref=1.

| Original file | Actual stored [value] | Canonical value | Original CXTM bytes |
| --- | --- | --- | ---: |
| occurrence-decimal.ctm | `"9.3"` | `9.3` | 353 |
| occurrence-decimal-dot.ctm | `"0.3"` | `0.3` | 353 |
| occurrence-decimal-dot-neg.ctm | `"-0.3"` | `-0.3` | 354 |
| occurrence-decimal-leading-zeros.ctm | `"0.3"` | `0.3` | 353 |
| occurrence-decimal-minus-sign.ctm | `"-9.3"` | `-9.3` | 354 |
| occurrence-decimal-plus-sign.ctm | `"9.3"` | `9.3` | 353 |
| occurrence-decimal-1.0.ctm | `"1.0"` | `1.0` | 353 |

All seven original baselines match byte-for-byte; no XML reparse, trimming,
value rewriting or baseline adjustment is used for the comparison.
The following are the actual unchanged sources; display fences add a visual
line ending where the original has none. Exact sources and object observations
are also recorded in `reports/slice-8/decimals.json`.

### ctm/in/occurrence-decimal.ctm

```ctm
topic
occtype: 9.3.
```

Original final LF absent.

### ctm/in/occurrence-decimal-dot.ctm

```ctm
topic
occtype: .3.
```

Original final LF absent.

### ctm/in/occurrence-decimal-dot-neg.ctm

```ctm
topic
  occtype: -.3.
```

Original final LF present.

### ctm/in/occurrence-decimal-leading-zeros.ctm

```ctm
topic
occtype: 0000000000000.3.
```

Original final LF absent.

### ctm/in/occurrence-decimal-minus-sign.ctm

```ctm
topic
occtype: -9.3.
```

Original final LF absent.

### ctm/in/occurrence-decimal-plus-sign.ctm

```ctm
topic
occtype: +9.3.
```

Original final LF absent.

### ctm/in/occurrence-decimal-1.0.ctm

```ctm

topic
occtype: 1.0.
```

Original final LF absent.

## Independent semantic controls

Bare `01.00`, `+1.0` and `1.000` already share the stored string `"1.0"`
under the reader policy and merge when the other properties match.
Qualified `"01.00"^^xsd:decimal` and `"1.0"^^xsd:decimal` retain different
strings and remain two Occurrences even though both serialize as `1.0`.
Two separate maps with those strings can have the same XML while retaining
unequal stored values. Canonical XML is not used to define TMDM equality.

Qualified `"1"^^xsd:decimal` and `"1"^^xsd:integer` retain the exact same string
but remain different Occurrences solely because the Datatype Locators differ.
They output `1.0` and `1`. Stored strings `+002.00`, `-10.00`, `001.00`, `2.0`
sort in that order; output values are `2.0`, `-10.0`, `1.0`, `2.0`, demonstrating
why sorting formatted output or mathematical values would be wrong.

The suite checks all permutations of representative sets, lexical duplicates
and Item Identifier union after Parent/Type merges, raw stored canonical
references, retained replacement handles, malformed inputs and source positions,
negative zero, 10,000-digit integer/fraction components and tiny values with
10,000 fractional leading zeroes. Serializing never rewrites the model or its
retained handles. An independent Python Decimal arithmetic oracle checks 157
implicit/explicit probes with sufficient explicit precision and no binary float.

## API and executable inspection

Existing deserialization, model and CXTM APIs are unchanged. New pure helpers
in `topic-maps.tmdm` are `decimal-datatype`, `decimal-lexical-p` and
`canonical-decimal-lexical-form` (returns NIL for invalid forms). The model API
validates supported datatype lexical forms before mutation, retaining the string.
Malformed qualified values signal `CTM-REJECTION :INVALID-DECIMAL-VALUE` at the
string token's source position; model insertion uses
`OCCURRENCE-ERROR :INVALID-DECIMAL-VALUE`, and a private malformed item is refused
by `CXTM-ERROR :INVALID-DECIMAL-VALUE`. Undefined prefixes and unsupported
features remain separate conditions. The lexer retains raw decimal spelling.

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps/cxtm")
(let* ((doc "https://example.invalid/decimals.ctm")
       (map (topic-maps.ctm:deserialize-string
             "%prefix xsd <http://www.w3.org/2001/XMLSchema#> topic occtype: +001.2300; occtype: \"001.2300\"^^xsd:decimal."
             :document-iri doc))
       (owner (first (topic-maps.tmdm:topic-map-topics map)))
       (items (topic-maps.tmdm:topic-occurrences owner)))
  (assert (= 2 (length items)))
  (assert (equal '("1.23" "001.2300") (mapcar #'topic-maps.tmdm:occurrence-value items)))
  (assert (every (lambda (item)
                   (string= (topic-maps.tmdm:decimal-datatype)
                            (topic-maps.tmdm:occurrence-datatype item))) items))
  (assert (eq (topic-maps.tmdm:occurrence-type (first items))
              (topic-maps.tmdm:occurrence-type (second items))))
  (describe (second items))
  (describe (topic-maps.tmdm:occurrence-type (second items)))
  (write-string (topic-maps.cxtm:canonicalize map :base-locator doc)))
```

## Remaining limits

Only the exact xsd:decimal locator receives Decimal treatment; no derived-type
coercion, general numeric implementation, exponent syntax, or floating-point
conversion is introduced. Explicit XSD decimal strings may omit a fractional
component; bare CTM decimals may not. `1.` retains the Slice-7 Integer behavior.
No application-defined precision limit is introduced beyond finite Lisp strings
and available memory. Date/DateTime, CTM `*` semantics, nonempty Scope,
Reification, Variants, Templates, cross-document merging and HyperDoc integration
remain unimplemented. Unselected imported cases stay NOT-RUN even where the
new subset might happen to parse them. No selected draft/published-standard
conflict was found.
