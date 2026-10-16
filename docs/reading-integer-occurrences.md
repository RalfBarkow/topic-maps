# Reading Integer Occurrences

Slice 7 extends the accepted Slice 6 commit
`3924d1eac5a070fe5a6a26683e23ac338793f544`. The original corpus remains pinned to
`cd165b150176c1d6842b37be9cc9051b40d4996b`. Its CTM tests target draft 2010-03-31;
the published standards remain authoritative.

## Representation, equality and canonicalization

These are three separate operations, not a single numeric-equality rule.

[CTM §3.4.1](https://www.isotopicmaps.org/ctm/ctm.html) defines the integer form
as an optional sign plus digits, assigns xsd:integer, and puts the literal's
value into the Occurrence. A quoted string can explicitly name that datatype.
This implementation maps an **unquoted numeric literal's value** to its canonical
integer string during deserialization: `+001` becomes `"1"`, `-000` becomes
`"0"`. This is the reader's documented value-representation policy, not a claim
that §3.4.1 explicitly mandates early lexical canonicalization. The lexer retains
the original token spelling; the unmodified CTM source remains separate.
**Explicitly quoted values retain their escape-decoded strings**, including
leading zeros and XML whitespace. The two source forms are not a promise to
preserve identical lexical histories in the model.

[TMDM §§4.3–4.4, 5.6, 6.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
require a string [value], a separate datatype locator, and equality by the
Occurrence's value/datatype/type/scope/parent. String equality compares Unicode
scalar sequences; mathematical value-space equivalence alone does not make
unequal strings equal. The existing model/API **does not normalize stored integer
strings**. Identical strings with equal remaining properties merge; differing
strings stay distinct. A datatype locator does not synthesize a Topic.

[CXTM §§3.16, 4.2–4.3, 4.9](https://www.isotopicmaps.org/cxtm/cxtm.html)
require integer canonical lexical output and Occurrence ordering by the model's
value, datatype, type, scope, parent. The integer's stored value is still a string:
comparison uses the stored string under the string rules, rather than a numeric
comparison or the reformatted output. Serialization computes the canonical
string without modifying the model or removing items that serialize alike.

[XML Schema Part 2, §§3.3.13.1–3.3.13.2 and 4.3.6](https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/#integer)
provide ASCII sign/digits, canonical representation and the XML-whitespace
collapse facet. The canonical output has no plus sign or leading zeros, and
zero is `0` (also consistent with §3.3.14.2). Internal whitespace is invalid;
XML whitespace at the ends of qualified values is accepted for interpreting
this datatype. It is retained in TMDM, removed only in canonical output.
No fixed-width numeric representation is needed: pure character processing
handles arbitrary finite-length integer strings.

Examples of the resulting contract, with the same Parent and Type:

| CTM forms | Stored values/datatype | Equality/result |
| --- | --- | --- |
| `001`, `+1`, `1` | all `"1"`, xsd:integer | duplicate Occurrences merge |
| `1`, `"1"^^xsd:integer` | both `"1"`, xsd:integer | merge |
| `"001"^^xsd:integer`, `"1"^^xsd:integer` | `"001"`, `"1"` | remain two Occurrences; both output `1` |
| `1`, `"1"` | same string, different datatypes | remain two Occurrences |

A map with one `"001"` integer Occurrence and one with one `"1"` integer
Occurrence can have identical canonical XML while their stored values differ.
The tests explicitly establish this counterexample; XML equality does not drive
TMDM merging.

The string order for `-2`, `-10`, `2`, `10` is `-10`, `-2`, `10`, `2`.
For **explicit** stored strings `+002`, `-10`, `001`, `2`, the string order is
`+002`, `-10`, `001`, `2`, while the output values are `2`, `-10`, `1`, `2`.
This is intentional: ordering uses §4.9's properties, output uses §3.16.

## Original cases and expected information items

The six original sources and baselines were read before implementation. All use
Document IRI `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
followed by their full `ctm/in/...ctm` ID; CXTM uses the same Base Locator.
Their baseline `#topic` and type identifiers follow the existing §3.18 policy.
Stored identifiers remain absolute, and datatype output remains a full locator.

Each input creates one Topic Map. The first four and the explicit-datatype case
create two Topics: owner `topic`, Type `occtype`. Each Topic has only its local
Item Identifier `DocumentIRI#identifier`. One Occurrence has Parent EQ owner,
Type EQ occtype, datatype `http://www.w3.org/2001/XMLSchema#integer`, and NIL
Item Identifiers. The actual stored values are `"1"`, `"1"`, `"1"`, `"-1"`, and
`"42"`, respectively. SI/SL/Names/Associations are empty. No datatype Topic exists.
CXTM numbers type=1, owner=2 and Occurrence=1.

The leading-zero case creates eight Topics: owner `topic` and seven Type Topics
`o1` through `o7`. The seven Occurrences' stored values in source order are
`"1"`, `"1"`, `"-1"`, `"100"`, `"0"`, `"0"`, `"0"`. All have Parent EQ owner
and distinct corresponding Type references, so they are not duplicates.
CXTM numbers o1–o7 as Topics 1–7 and owner as Topic 8. Its Occurrence order is
o3, o5, o6, o7, o1, o2, o4: value-string order followed by Type order on ties.

### ctm/in/occurrence-integer.ctm

```ctm
topic
occtype: 1;.
```

Original has no final LF; the display fence adds only a visual line break. Original CXTM: 351 bytes. **Byte-exact PASS**.

### ctm/in/occurrence-integer2.ctm

```ctm

# In a previous CTM draft 1. was a valid decimal.
# This is not the case anymore, the "1." must be interpreted as 
# integer "1" followed by the end of the topic block

topic
occtype: 1.
```

Original has no final LF; the display fence adds only a visual line break. Original CXTM: 351 bytes. **Byte-exact PASS**.

### ctm/in/occurrence-integer-plus-sign.ctm

```ctm
topic
occtype: +1;.
```

Original has no final LF; the display fence adds only a visual line break. Original CXTM: 351 bytes. **Byte-exact PASS**.

### ctm/in/occurrence-integer-minus-sign.ctm

```ctm
topic
occtype: -1;.
```

Original has no final LF; the display fence adds only a visual line break. Original CXTM: 352 bytes. **Byte-exact PASS**.

### ctm/in/occurrence-integer-leading-zeros.ctm

```ctm

#
# Various integer with leading zeros tests
# 

topic
  o1: 001;
  o2: +001;
  o3: -001;
  o4: 000100;
  o5: 000000;
  o6: +000000;
  o7: -000000.
```

Original final LF present. Original CXTM: 1741 bytes. **Byte-exact PASS**.

### ctm/in/occurrence-explicit-datatype2.ctm

```ctm
%prefix xsd http://www.w3.org/2001/XMLSchema#

topic
occtype: "42"^^xsd:integer.
```

Original has no final LF; the display fence adds only a visual line break. Original CXTM: 352 bytes. **Byte-exact PASS**.

## Public API and executable inspection

The existing `deserialize-string`, `deserialize-file`, `add-occurrence`,
`occurrence-value`, `occurrence-datatype`, Parent/Type readers,
`canonical-occurrence` and CXTM API signatures remain unchanged.
New pure helpers in `topic-maps.tmdm`:

- `(integer-datatype)` returns the exact xsd:integer locator string.
- `(integer-lexical-p string)` checks the supported XSD integer lexical space.
- `(canonical-integer-lexical-form string)` returns a canonical string, or NIL
  for invalid input. It performs no model normalization or merging.

The reader signals `CTM-REJECTION :INVALID-INTEGER-VALUE` for invalid explicitly
integer-typed strings, with the quoted token's source position. The model API
rejects them atomically via `OCCURRENCE-ERROR :INVALID-INTEGER-VALUE`; CXTM rejects
a private invalid model via `CXTM-ERROR :INVALID-INTEGER-VALUE`. These are distinct
from undefined-prefix rejection and unsupported Decimal/date/* forms.

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps/cxtm")
(let* ((doc "https://example.invalid/integers.ctm")
       (map (topic-maps.ctm:deserialize-string
             "%prefix xsd <http://www.w3.org/2001/XMLSchema#> topic occtype: +001; occtype: \"001\"^^xsd:integer."
             :document-iri doc))
       (owner (first (topic-maps.tmdm:topic-map-topics map)))
       (items (topic-maps.tmdm:topic-occurrences owner)))
  (assert (= 2 (length items)))
  (assert (equal '("1" "001") (mapcar #'topic-maps.tmdm:occurrence-value items)))
  (assert (eq (topic-maps.tmdm:occurrence-type (first items))
              (topic-maps.tmdm:occurrence-type (second items))))
  (describe (second items))
  (describe (topic-maps.tmdm:occurrence-type (second items)))
  (write-string (topic-maps.cxtm:canonicalize map :base-locator doc)))
```

## Local observations and limits

`reports/slice-7/integers.json` contains the six original sources, absolute
Document IRIs and actual object properties/reference ordinals. Its 143 additional
probes record both implicit/explicit model strings and complete canonical XML.
An independent Python big-integer oracle checks each output, including positive
and negative 10,000-digit values. The tests also permute construction order,
check lexical duplicate removal/late merges and verify model/retained-handle
purity. All prior 33 positive and three negative contracts retain their results.

The literal lexer recognizes `1.` as an integer followed by a terminator;
`1.5` remains an excluded Decimal. Preserve the QName grammar: `t:1` is a QName,
so use `t: 1` (or `t :1`) for a local Occurrence Type followed by an integer.
The selected originals already use the unambiguous syntax. Integer source text
is handled by the same dedicated CTM lexer/reader, never Common Lisp READ/EVAL.

Decimal, Date, DateTime, Variants, nonempty Scope, Reification, Templates,
cross-document merging and HyperDoc integration remain outside the slice.
The `*` literal/ctm-integer counter semantics are not implemented and are not a
dependency of any selected case. The existing generic explicit-datatype path
can carry an opaque ctm-integer locator; that adds no special semantics.
No derived XSD integer subtype coercion is introduced: only the exact xsd:integer
locator receives the new treatment. Existing locator-validation, Unicode and
root-LF boundaries are unchanged. No selected draft/published-standard conflict
was found; the early bare-literal representation policy is explicitly qualified
above rather than asserted as a new TMDM equality rule.
