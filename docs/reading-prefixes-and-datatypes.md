# Reading Prefixes and Explicit Datatypes

Slice 6 starts at `437ad53ea7539d36db3fa871d0931650b7a6a03e`. A prefix is a
source abbreviation for an IRI, not a Topic. An Occurrence datatype is a locator;
its Type is a Topic reference. These two properties remain different even if an
author deliberately uses the same IRI for both.

## Normative requirements

[ISO/IEC 13250-6:2010](https://www.isotopicmaps.org/ctm/ctm.html):
§3.2 processes components in document order. §§3.3.3–3.3.5 form IRIs and resolve
QNames by concatenation; undefined prefixes are errors. §3.16.1 binds an
identifier to an IRI and permits repeat binding only to the same reference.
Its reference production accepts an IRI, not another QName. §§3.4.1–3.4.2 and
3.10 assign the quoted/escape-decoded lexical value and the explicit datatype
to the Occurrence. A qualifier is `^^` followed by an IRI reference.

[TMDM 2006](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/):
§4.3 defines string/locator equality. §4.4 permits other datatypes and stores
value representations separately from datatype locators. A datatype Topic need
not exist. `xsd:anyURI` content must be absolute. §5.6 defines Occurrence
properties/equality; §6.5 merges equal Occurrences and unions their identifiers.
The existing empty-Scope/null-Reifier subset and replacement handles continue.

[ISO/IEC 13250-4:2009](https://www.isotopicmaps.org/cxtm/cxtm.html):
§3.14 writes the datatype locator without base stripping. §3.16 uses locator
normalization for anyURI, special lexical rules for integer/decimal/date/dateTime,
and the string rule for Other. §3.20 applies NFC to encoded string properties.
§§4.2–4.5 and 4.9 order Occurrences by value, datatype, Type, Scope, Parent.
The serializer's existing §§3.8, 3.18–3.19 numbering/base rules remain unchanged.

## Original inputs and expected items

The upstream corpus is unchanged at
`cd165b150176c1d6842b37be9cc9051b40d4996b`. It targets draft 2010-03-31;
the published standard is authoritative. No conflict blocks these seven cases.
The following expectations were established from those clauses and checked
against the original baselines before implementation.

Every case uses the absolute Document IRI formed by concatenating
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
and its full `ctm/in/...` or `ctm/invalid/...` case ID. This IRI is also the CXTM
Base Locator. It is independent of the physical checkout. Model Item Identifiers
remain absolute; the baselines' `#topic`/`#occtype` follow CXTM §3.18. Datatype
locators remain full IRIs under §3.14.

### ctm/in/occurrence-explicit-datatype.ctm

```ctm
%prefix xsd http://www.w3.org/2001/XMLSchema#

topic
occtype: "Occurrence"^^xsd:string;.
```

The original source has no final LF; the display fence adds only a visual line break.

Two Topics, `topic` and `occtype`, each with its document-local Item Identifier. One Occurrence O1: Parent EQ topic, Type EQ occtype, Value `Occurrence`, Datatype `http://www.w3.org/2001/XMLSchema#string`. No Topic for xsd or its datatype. Empty SI/SL and Occurrence identifiers. Original CXTM: 359 bytes.

### ctm/in/occurrence-datatype-unknown.ctm

```ctm
topic
occtype: "BOGUS"^^http://example.com/bogus.
```

The same two Topic identities. One Occurrence O1: Parent EQ topic, Type EQ occtype, Value `BOGUS`, Datatype `http://example.com/bogus`. The unknown datatype is a locator, not a third Topic. Original CXTM: 339 bytes.

### ctm/in/prefix-duplicate.ctm

```ctm
%prefix ex http://psi.example.org/

%prefix ex http://psi.example.org/

ex:fake.
```

One Topic with SI `http://psi.example.org/fake`, no II or SL. The identical rebinding is permitted and creates no information item. Original CXTM: 141 bytes.

### ctm/in/prefix-duplicate2.ctm

```ctm
%prefix ex http://psi.example.org/

ex:fake.

%prefix ex http://psi.example.org/

ex:fake2.
```

Two Topics with SIs `http://psi.example.org/fake` and `http://psi.example.org/fake2`; no II/SL. A binding persists across intervening Topic declarations. Original CXTM: 260 bytes.

### ctm/in/prefix-multiline.ctm

```ctm
%prefix 
ex 
http://psi.example.org/ ex:fake.
```

One Topic with SI `http://psi.example.org/fake`, no II/SL. The directive is token based and may span lines; the next Topic can follow its IRI on the same line. Original CXTM: 141 bytes.

### ctm/invalid/prefix-collision.ctm

```ctm
%prefix ex http://www.example.org/
%prefix ex http://www.example.net/

```

Reject the second binding: `PREFIX-COLLISION`, a `CTM-REJECTION`, code `:PREFIX-COLLISION`, zero-based offset 43, line 2, column 9 (the second prefix identifier). No map is returned.

### ctm/invalid/prefix-undefined2.ctm

```ctm
#
# In one of the CTM drafts, xsd was bound to <http://www.w3.org/2001/XMLSchema#>
# This binding was removed from CTM
#

foo occ: "1"^^xsd:int .
```

Reject `xsd:int`: `UNDEFINED-PREFIX`, a `CTM-REJECTION`, code `:UNDEFINED-PREFIX`, zero-based offset 136, line 6, column 15. There is no implicit xsd binding. The failure precedes any CXTM datatype processing. No map is returned.

## Observed Lisp objects and results

The two Occurrence examples each return a `TOPIC-MAP` with two `TOPIC` structures
in source order: T1 owner, T2 type. T1's `topic-occurrences` contains O1, an
`OCCURRENCE` structure. O1's raw stored parent/type references are EQ T1/T2.
Its value/datatype are exactly the strings stated above; its Item Identifiers
are NIL. The owner/type Topics have II `DocumentIRI#topic`/`DocumentIRI#occtype`,
SI/SL NIL. No Names or Associations occur. Canonical topic numbers are type=1,
owner=2, with Occurrence number 1 inside owner.

The three positive prefix-only examples return one/two Topics in source order,
with precisely the SI sets above and empty II/SL/Names/Occurrences. Their
canonical numbers are fake=1, fake2=2 where applicable. The two negative cases
produce the specific conditions above, never I/O/generic failures.

These local observations are separately recorded in `reports/slice-6/prefixes.json`;
the Python checker independently checks source bytes, ordinal references, values,
datatypes and negative source positions. The actual CXTM UTF-8 bytes are compared
without any preprocessing to the original upstream baselines. All five comparisons
and both rejections pass. The preceding 28 canonical outputs remain byte-identical.
See `slice-6-validation.md` for full regression counts and fresh-process commands.

## Public API and inspection

Load `topic-maps/ctm` for deserialization and `topic-maps/cxtm` for canonicalization.
No API signature changes:

- `deserialize-string text :document-iri absolute-iri :source-name optional-name`
- `deserialize-file pathname :document-iri absolute-iri :source-name optional-name`
- `add-occurrence parent-topic type-topic value :datatype absolute-locator :item-identifiers ids`
- `occurrence-value`, `occurrence-datatype`, `occurrence-parent`, `occurrence-type`,
  `occurrence-item-identifiers`, `canonical-occurrence`
- `canonicalize`, `canonicalize-octets`, `write-cxtm`, with explicit `:base-locator`.

The new exported `prefix-collision` condition subclasses `ctm-rejection`, as does
`undefined-prefix`. Both are distinct from `ctm-unsupported`. Errors expose code,
source name, zero-based character offset and one-based line/column.

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps/cxtm")
(let* ((doc "https://example.invalid/inspection.ctm")
       (map (topic-maps.ctm:deserialize-string
             "%prefix ex <urn:example:> owner ex:description: \"00042\"^^ex:custom."
             :document-iri doc))
       (owner (first (topic-maps.tmdm:topic-map-topics map)))
       (item (first (topic-maps.tmdm:topic-occurrences owner))))
  (assert (eq owner (topic-maps.tmdm:occurrence-parent item)))
  (assert (string= "00042" (topic-maps.tmdm:occurrence-value item)))
  (assert (string= "urn:example:custom" (topic-maps.tmdm:occurrence-datatype item)))
  (assert (equal '("urn:example:description")
                 (topic-maps.tmdm:topic-subject-identifiers
                  (topic-maps.tmdm:occurrence-type item))))
  (describe item)
  (describe (topic-maps.tmdm:occurrence-type item))
  (write-string (topic-maps.cxtm:canonicalize map :base-locator doc)))
```

## Implementation boundaries

Bindings are parser-local, case-sensitive and document-ordered. A successful or
failed read cannot export a prefix to another read. Prefix IRIs are formed once;
QName concatenation neither decodes nor resolves the bound IRI again.

Quoted strings preserve their escape-decoded lexical values in TMDM. Datatype
IRIs/QNames are resolved as locators and never automatically interned as Topics.
Unknown datatypes use CXTM's Other string rule, including normal XML escaping/NFC
at output. Their value spaces are not interpreted or validated. No implicit
numeric, whitespace, URI-content or date conversion is performed.

Explicit integer/decimal/date/dateTime datatype locators can be stored through
the general quoted-string qualifier/API, but CXTM reports
`CXTM-UNSUPPORTED :UNSUPPORTED-OCCURRENCE-DATATYPE` for these four exact IRIs;
§3.16 requires canonical lexical rules outside this slice. Numeric/date sugar
still reports `CTM-UNSUPPORTED`. A quoted relative anyURI value is specifically
rejected (`:RELATIVE-URI-VALUE`) under TMDM §4.4, never silently resolved; IRI-form
values retain the previously implemented CTM IRI-reference behavior.

Nonempty Scope, Reification, Variants, Templates, includes/mergemap, cross-document
merging, non-UTF-8 encoding declarations and HyperDoc integration remain unsupported.
Typed Names and triple-quoted strings remain unsupported. The inherited locator
API expects validated/resolved arguments; its scheme check is not a complete RFC
3987 validator. The established Unicode 15.1 and normalized Topic-key ambiguity
limits, and the previously documented CXTM root-LF interpretation, remain.
