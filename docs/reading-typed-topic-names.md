# Reading Explicitly Typed Topic Names

Slice 12A builds on `6a2f8446afca0915882f0d4a06cb891ccfcdc96d`.
The CTM corpus remains pinned at `cd165b150176c1d6842b37be9cc9051b40d4996b`.
Original inputs and baselines are unchanged. The corpus targets the draft of
2010-03-31; published normative rules remain authoritative.

## Normative requirements

- [CTM 3.11](https://www.isotopicmaps.org/ctm/ctm.html): a Name's optional
  `type ':'` refers to a Topic. Without it, the default Type Topic is identified
  by `http://psi.topicmaps.org/iso13250/model/topic-name`. With an explicit
  different type, no default Type Topic is required. CTM 3.3.6–3.3.7 and 3.3.11
  supply the existing identity/reference procedure used for Name types.
- [TMDM 5.4](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/): a Name
  has a string Value, Topic Type and containing Topic Parent. Name equality
  compares Value, Type, Scope and Parent; equal text with different Types does
  not establish equality. There is no Name Datatype property.
- TMDM 6.2 replaces Topic references when Topics merge; 6.3 replaces equal
  Names with one Name. Existing forwarding handles implement this contract.
  TMDM 6.4 concerns Variants, which remain outside this slice; no partial
  Variant merge implementation has been added.
- [CXTM 3.6 and 4.7](https://www.isotopicmaps.org/cxtm/cxtm.html): emit the
  Name's Value and Type reference, sorting by Value, Type, Scope, Parent. Scope
  remains empty. The existing canonicalizer already implements these supported
  properties and is unchanged.

The default identifier above is taken specifically from CTM 3.11. The linked
2006-06-18 TMDM text's 7.5 spells its default identifier `.../name-type`;
this slice preserves the CTM-mandated `.../topic-name` and the original CTM
baselines rather than silently substituting the other spelling.
Both spellings are supported as different identifiers; see
[Two documented default name type identifiers](reading-type-relationships.md#two-documented-default-name-type-identifiers).

## Four unchanged original sources

`name.ctm`:
```ctm
topic
- "Name";.
```

`name2.ctm`:
```ctm
topic
- "Name".
```

`name-type.ctm`:
```ctm
topic
 - nametype : "Name" .
```

`name-duplicate.ctm`:
```ctm
topic
- "Name";
- "Name"
.
```

For each file the exact Document IRI is:
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/<filename>`.
This is a deserialization input, not a reachable Subject URL. Canonicalization
uses the same IRI as its Base Locator (CXTM 3.18); this explains the baseline's
`#topic` and `#nametype` locators without changing those baseline bytes.

## Expected items, baseline evidence and actual observations

All four documents yield one Map, two Topics, one Name, no Occurrences or
Associations. In the first, second and fourth document, the containing Topic
has Item Identifier `DocumentIRI#topic`; the other Topic has the default
Subject Identifier above. The Name has Value `"Name"`, its Parent is the
containing Topic and its Type is that default Topic. The duplicate declaration
in `name-duplicate.ctm` does not introduce a second live Name.

In `name-type.ctm`, the second Topic instead has Item Identifier
`DocumentIRI#nametype`, no Subject Identifier and no Subject Locator. The Name's
Type is EQ to that actual Topic; Parent is EQ to the `#topic` object. No default
Type Topic is present. The baseline numbers the Type Topic as 1 and Parent as
2; the generated Name therefore contains:
```xml
<value>Name</value>
<type topicref="1"></type>
```

These expectations follow from the cited rules. The upstream XML is separate
external evidence. Lisp assertions test actual object identity and raw stored
references, while an independent Python check compares identifier sets and
Name/Parent/Type relations with the baseline. CXTM byte comparisons are a
separate check. Execution results are recorded in `reports/slice-12a/`.

## Public API and inspection

`(topic-maps.tmdm:add-name topic value &key type)` returns a current Name.
Omitting `:type` uses the default. Supplying it requires an actual Topic from
the same Map; explicitly supplying NIL is an error. Retained Topic handles are
resolved before storage. Invalid types are refused before mutation. Equal
Value/Type/Parent reuses an existing Name. `add-default-name` remains compatible
and delegates to this API.

Run from the repository root in a fresh SBCL:
```lisp
(require :asdf)
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/ctm")
(let* ((map (topic-maps.ctm:deserialize-string
             "topic - nametype: \"Name\"."
             :document-iri "https://example.invalid/names.ctm"))
       (owner (find-if #'topic-maps.tmdm:topic-names
                       (topic-maps.tmdm:topic-map-topics map)))
       (name (first (topic-maps.tmdm:topic-names owner))))
  (assert (= 2 (length (topic-maps.tmdm:topic-map-topics map))))
  (assert (eq owner (topic-maps.tmdm:topic-name-parent name)))
  (describe name)
  (describe (topic-maps.tmdm:topic-name-type name)))
```

After Type or Parent merging, inspect `(canonical-topic-name retained-name)`;
EQ on an obsolete Name is not rewritten. Public Name readers resolve the
retained handle. Serialization does not compress forwarding chains or mutate
retained objects.

## Limits

Embedded Topics, Scope, Reification, Variants, Templates and cross-map merging
remain unsupported. No HyperDoc dependency or navigation code is introduced.
The two DateTime baseline discrepancies remain executed FAILs. The other
exploratively observed contracts are not promoted by this slice.
