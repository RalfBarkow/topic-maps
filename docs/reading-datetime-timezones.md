# Reading DateTime Timezone Canonicalization

## Normative decisions before implementation

Slice 11 starts at `8741d155d948c7317945eee423a977940cad995e`.
The original timezone2 source and baseline were read unchanged. Reuse the
existing Date/DateTime validators, Occurrence model and canonicalizer.

- [CXTM 3.16](https://www.isotopicmaps.org/cxtm/cxtm.html):
  serialize dateTime using the XML Schema canonical lexical representation.
  CXTM 4.3/4.9 compare the stored string properties in their specified order;
  this is not dateTime instant ordering or sorting the rendered XML values.
- [XML Schema Part 2, Second Edition 3.2.7.1–3.2.7.4](https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/#dateTime):
  validate lexical syntax and calendar first; offsets have magnitude at most
  14:00, with minute 00 at hour 14. Subtract the signed offset to obtain UTC,
  with calendar carry, then write Z. +00:00 and -00:00 both become Z.
  An absent zone stays absent. Normalize 24:00:00 to next-day midnight;
  remove trailing fractional zeroes without losing other digits. XSD instant
  comparison in 3.2.7.4 does not redefine TMDM string equality.
- [TMDM 4.3–4.4, 5.6, 6.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/):
  Value is a Unicode string; Datatype is a separate locator; Parent and Type
  are Topic references. Equal stored properties trigger duplicate removal,
  preserving the existing replacement-object/canonical-occurrence contract.
  Equal canonical XML alone does not establish equal Occurrence items.

Keep the established deserialization policy: bare literals store their derived
canonical string. Datatype-qualified quoted strings and direct API values
retain their valid lexical spelling, including offset and XML whitespace.
CXTM computes a separate representation without model or handle mutation.

## Deliberate calendar limits

Reuse the accepted Slice 9/10 calendar interpretation; do not silently import
XSD 1.1 astronomical year zero. Newly supported nonzero-offset conversions
requiring a day change in/into BCE are explicitly unsupported: the pre-existing
XSD 1.0 BCE leap-calendar qualification is not resolved here. BCE conversions
within one day need no calendar assumption. Existing zero/absent-zone behavior,
including its documented year rollover, is retained.

Nonzero-offset second-60 conversion is explicitly unsupported, without guessing
a UTC leap-second context. Existing absent/zero-zone leap handling is unchanged,
including the published D.1 qualification and original datetime2 FAIL.
Date timezone canonicalization is outside this slice.

## Original timezone2 contract

Input: `2011-01-01T00:00:00+02:00`.
Required UTC value: `2010-12-31T22:00:00Z`.
The pinned upstream baseline retains the input offset. Run the complete
CTM → TMDM → CXTM contract and record its actual mismatch as FAIL; never alter
the baseline or use a filename-specific canonicalization rule.

## Executable inspection

Run from the repository root in a fresh SBCL:

```lisp
(require :asdf)
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps/cxtm")
(let* ((map (topic-maps.ctm:deserialize-string
             "a t: \"2011-01-01T00:00:00+02:00\"^^<http://www.w3.org/2001/XMLSchema#dateTime>."
             :document-iri "https://example.invalid/timezone.ctm"))
       (owner (find-if #'topic-maps.tmdm:topic-occurrences
                       (topic-maps.tmdm:topic-map-topics map)))
       (item (first (topic-maps.tmdm:topic-occurrences owner))))
  (describe item)
  (describe (topic-maps.tmdm:occurrence-type item))
  (format t "~&Stored: ~A~%Datatype: ~A~%~A"
          (topic-maps.tmdm:occurrence-value item)
          (topic-maps.tmdm:occurrence-datatype item)
          (topic-maps.cxtm:canonicalize map
            :base-locator "https://example.invalid/timezone.ctm")))
```

The stored string remains `2011-01-01T00:00:00+02:00`; CXTM emits
`<value>2010-12-31T22:00:00Z</value>`. Replacing the quoted qualified value
with the bare literal stores the canonical UTC string, retaining Slice 10's
deserialization policy. Both examples have two Topics and one Occurrence;
the datatype locator does not create another Topic.
