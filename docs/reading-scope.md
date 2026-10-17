# Reading Scope in CTM and TMDM — Slice 13

This slice starts from Topic Maps commit
`788899aea1a20b9cd8237c6106e6613e180d7362`. It extends the existing information
items. It adds neither a Scope information-item class nor HyperDoc integration.

## Normative requirements

- [TMDM §§4.3, 5.3.3](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/):
  Scope is an unordered set of Topics whose subjects jointly qualify a statement.
  The empty set is unconstrained Scope. Topic Names (§5.4), Occurrences (§5.6)
  and Associations (§5.7) carry Scope; Roles have no separate Scope (§5.8).
- Scope participates in item equality (§§5.4, 5.6–5.7). Topic merging replaces
  Scope references (§6.2); newly equal items must then merge (§6.1). Name,
  Occurrence and Association replacement copies their equal Scope (§§6.3, 6.5–6.6).
  Different scopes are not unioned to force equality. No new Topic identity rule
  is introduced by Name/Occurrence/Association equality.
- [CTM §§3.3.7, 3.3.9, 3.10–3.13](https://www.isotopicmaps.org/ctm/ctm.html):
  `@ topic-ref (, topic-ref)*` assigns the resolved set after a Name string,
  Occurrence literal or Association roles. Each statement is constructed after
  its complete Scope is known. Identity resolution is the existing reader path.
- [CXTM §§3.6, 3.8–3.9, 3.12](https://www.isotopicmaps.org/cxtm/cxtm.html):
  empty Scope has no representation; nonempty Scope emits `scope/scopingTopic`
  references to canonical Topic numbers. Scope follows Type on Names/Occurrences
  and Roles on Associations. LF and explicit empty-element end tags follow §3.1.
- CXTM §§4.4, 4.6–4.11: Scope members sort as Topics; sets compare by cardinality,
  then sorted members. Name keys are Value, Type, Scope, Parent; Occurrence keys
  are Value, Datatype, Type, Scope, Parent; Association keys are Type, Roles,
  Scope, Parent. RolePlayed references use the resulting Association numbering.

The pinned corpus remains `cd165b150176c1d6842b37be9cc9051b40d4996b` and targets
the CTM draft dated 2010-03-31. Original baselines are evidence, not normative
rules. No Scope disagreement was found for these three selected contracts.

## Original inputs and expected information items

Each Document IRI is the existing deterministic
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
plus its complete case ID, for example `ctm/in/name-scope.ctm`.
Local Topic identifiers resolve to that Document IRI plus `#identifier`.
The same IRI is passed as CXTM Base Locator; baseline `#...` locators are its
canonical relative representation, not the stored identity in the TMDM object.

Original `ctm/in/name-scope.ctm`:

```text
topic
- "Name" @theme1, theme2.
```

Four Topics: owner, two themes and default Name Type. One Name with Value
`Name`, Parent EQ to the owner, Type EQ to the default-type Topic whose SI is
`http://psi.topicmaps.org/iso13250/model/topic-name`. Scope holds the two actual
Theme objects. Baseline canonical Theme references: 1, 2.

Original `ctm/in/occurrence-scope.ctm` (trailing source whitespace is retained
in the vendored file and observation report):

```text
topic
occtype: "Occurrence" @theme1, theme2.
```

Four Topics: owner, Type and two themes. One Occurrence, Value `Occurrence`,
Datatype `http://www.w3.org/2001/XMLSchema#string`, Parent/Type EQ to the owner/
`occtype` Topics, Scope EQ-member references to the two themes. Baseline Theme
references: 2, 3. The Datatype remains a locator, not a Topic.

Original `ctm/in/association-scope.ctm`:

```text
assoctype(roletype: topic)@theme1,theme2
```

Five Topics: Association Type, Role Type, Player and two themes. One Association
owned by the Map, with the two-theme Scope and one Role. Role Parent is EQ to
that Association; Role Type and Player are EQ to the corresponding Topics.
Baseline Theme references: 3, 4. No Role Scope is synthesized.

The executable report records full unmodified source strings, actual public
properties and reference ordinals. Ordinals identify objects within that one
observation; they are neither Subject Identifiers nor permanent object addresses.
Separate tests assert EQ directly. The independent Python checker maps ordinals
back to distinct identifier-property sets before comparing baseline relationships.

## Public API and merge contract

Existing creators now accept `:scope` (default NIL):

- `add-name topic value &key type scope`
- `add-default-name topic value &key scope`
- `add-occurrence topic type value &key datatype item-identifiers scope`
- `make-association map type roles &key scope`

`topic-name-scope`, `occurrence-scope` and `association-scope` resolve retained
item handles and return copies of the stored set lists. Arguments must be finite
proper lists of actual same-map Topics. Retired Topic arguments are resolved via
`canonical-topic`. Duplicate members are removed by canonical object identity.
Invalid lists, non-Topic members and foreign Themes signal `scope-error`, with
`scope-error-code` values `:invalid-scope`, `:invalid-theme`, `:foreign-theme`.
Validation occurs before mutation, including before automatic Name-Type creation.

Merging Theme A and Theme B rewrites all live Scope sets. Thus `{A,B}` becomes
`{C}`, while `{A,B,Z}` becomes `{C,Z}`. Formerly different items whose full equality
keys now match are replaced using the established canonical-handle contract.
Name/Occurrence/Association handles resolve through their existing canonical
readers; discarded Role handles also resolve to Roles of the current Association.
Occurrence item identifiers are unioned when equal Occurrences merge.

Stored values, datatypes and existing identity categories retain their earlier
semantics. Equal canonical XML is not used as a TMDM equality test.
Canonicalization validates current references and never normalizes the model or
compresses old handles. Tests compare live and retired states before/after output.

## Inspect with ordinary Common Lisp

Start a fresh process in this checkout. These forms execute no writes or server:

```lisp
(require :asdf)
(asdf:load-asd (merge-pathnames "topic-maps.asd" (uiop:getcwd)))
(asdf:load-system "topic-maps/ctm")
(let* ((document-iri "https://example.invalid/name-scope.ctm")
       (map (topic-maps.ctm:deserialize-file
             #p"vendor/cxtm/ctm/in/name-scope.ctm"
             :document-iri document-iri))
       (owner (find-if #'topic-maps.tmdm:topic-names
                      (topic-maps.tmdm:topic-map-topics map)))
       (name (first (topic-maps.tmdm:topic-names owner)))
       (themes (topic-maps.tmdm:topic-name-scope name)))
  (assert (eq owner (topic-maps.tmdm:topic-name-parent name)))
  (assert (= 2 (length themes)))
  (assert (every (lambda (theme)
                   (member theme (topic-maps.tmdm:topic-map-topics map) :test #'eq))
                 themes))
  (describe name)
  (mapc #'describe themes)
  (let ((merged (topic-maps.tmdm:merge-topics (first themes) (second themes))))
    (assert (equal (list merged) (topic-maps.tmdm:topic-name-scope name)))
    (assert (eq merged (topic-maps.tmdm:canonical-topic (first themes))))
    (describe (topic-maps.tmdm:canonical-topic-name name))))
```

The inspection deliberately uses its own absolute Document IRI. Imported byte
comparisons use each original contract's Document IRI/Base Locator instead.

## Explicit limits

Only identity references already supported by the reader are accepted as Themes:
local identifiers, IRIs/QNames, explicit Item Identifiers and Subject Locators.
Embedded Topics, wildcards, Templates, Reification and Variants remain unsupported;
full CTM `topic-ref` conformity is not claimed. Missing Themes and malformed
comma lists are syntax rejections, with offsets and line/column diagnostics.
Scope on a bare Topic or inside a Role is rejected as misplaced syntax.

For a later Variant slice, CTM §3.12 requires adding the Parent Name Scope to the
Variant's stated Scope; TMDM §5.5 then requires a true superset. Variant equality,
merging and that constraint are not implemented here.

The HyperDoc Work-Topic `TMDM model` example-reading view still does not establish
a TMDM representation of its Work Topic. That separate Slice 12B semantic question
is unchanged. No HyperDoc repository, view or running image is modified here.
