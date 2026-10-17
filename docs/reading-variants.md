# Reading Variants — Slice 14

Base: `aeb017e4f4846f2e6a701e581d20eef84a8b83d9`. The independent model now
supports unreified Variant information items under Topic Names. HyperDoc is not
a dependency and no HyperDoc image is loaded by these tests.

## Normative requirements and local policy

[TMDM §5.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) specifies
Value, Datatype, Scope, Reifier, Item Identifiers and Parent Name. Scope is a
nonempty Topic set properly containing the Parent Name's Scope. A Variant has
no Type Topic. Equality uses Value, Datatype, Scope and Parent. §§6.1/6.4 remove
equal Variants; §6.3 unions Variants when Names merge; §6.2 replaces Theme references.
Reifier is null and Item Identifiers empty in this bounded implementation.

[CTM §§3.4.1, 3.11–3.12](https://www.isotopicmaps.org/ctm/ctm.html) specify
`'(' literal scope reifier? ')'` after a Name.
The shared literal reader supplies the same values/datatypes as for Occurrences.
The reader unions explicitly supplied themes E with current Parent Name Scope P.
Actual TMDM Scope V is P union E, and P must be a proper subset of V. Explicit
source Scope E is syntax, not another TMDM property. `@p` under Parent Scope
`{p}` is invalid even though the written Scope is nonempty.

[CXTM §§3.6–3.7, 3.12–3.21, 4.2–4.8](https://www.isotopicmaps.org/cxtm/cxtm.html)
nest Variants under their Names, numbered from 1 within that Name's sorted set.
Children are Value, Datatype, full Scope and, if any, Item Identifiers. Scope
references canonical Topic numbers. Variant keys are Value, Datatype, Scope,
Parent; sets sort by size then sorted members. String values precede locator
values. Value normalization reuses the existing datatype-specific CXTM code;
Datatype locators are not base-normalized. Serialization never mutates the model.

Local value policy is unchanged: bare supported CTM numeric/date literals use
their established value representation; qualified strings retain their lexical
values. The model does not infer equality from equal canonical XML values.
For example, quoted `"01"^^xsd:integer` and `"1"^^xsd:integer` remain distinct
stored strings, while CXTM renders both as `1`.

**Merge policy:** if a Theme merge would collapse Variant Scope to Parent Scope,
the API signals `variant-error` / `:variant-scope-collapse` before any mutation.
This is a local atomic failure contract preserving TMDM §5.5, not an error
recovery algorithm prescribed by the standard. The preflight computes the full
prospective identity closure, including automatic identifier-triggered merges.
It never deletes a Variant, manufactures a Theme, or changes a value to hide
the constraint violation. Valid reductions such as `{a,b,x}` to `{c,x}` with
Parent `{a,b}` to `{c}` remain supported.

## Unchanged corpus sources and baseline expectations

Pin: `cd165b150176c1d6842b37be9cc9051b40d4996b`; draft qualification 2010-03-31.
Each Document IRI is `https://ctm-tests.example.invalid/` + pin + `/` + case ID.
The same absolute IRI is used as CXTM Base Locator. Stored local item identifiers
are absolute; `#theme` in a baseline is the CXTM relative locator representation.

`ctm/in/variant.ctm`:
```text
topic - "Name" ("name" @theme).
```
Three Topics: owner, theme and default Name Type. One Name, Parent EQ owner,
Type EQ the Topic with SI `http://psi.topicmaps.org/iso13250/model/topic-name`.
One Variant, Value `name`, Datatype `http://www.w3.org/2001/XMLSchema#string`,
Parent EQ Name, Scope containing the actual theme Topic. Baseline Theme ref 1.

`ctm/in/variants.ctm`:
```text
topic - "Name" ("name" @theme)("nome" @theme2).
```
Four Topics, one Name, two Variants; Values `name` and `nome`, string Datatype,
Scopes containing theme and theme2 respectively. Baseline refs 1 and 2.

`ctm/in/variant-duplicate.ctm`:
```text
topic - "Name" ("name" @theme)("name" @theme).
```
Three Topics, one Name, one Variant after duplicate removal. No datatype Topic
or independent Variant Type is introduced.

`ctm/invalid/variant-no-scope.ctm` (including its initial blank line):
```text

topic
  - "name" ("variant").
```
Specific `ctm-rejection`, `:expected-variant-scope`, zero-based character 28,
line 3, column 22. An unsupported feature or unrelated exception is not a PASS.

The three positive outputs are compared to original baselines as raw UTF-8 bytes.
Direct EQ assertions and the independent JSON/XML checker additionally compare
actual information items and relationships. Report ordinals identify objects
within that observation only; they are not permanent Subject Identifiers.

`variant-reifier.ctm` additionally needs Reification; `variant-scope-embedded`
and `embedded2` need Embedded Topics; `embedded3` and `embedded4` also need
Templates. Their imported contracts remain NOT-RUN. Diagnostic probes verify
UNSUPPORTED without recording success. There is no selected Variant baseline
conflict; the two existing DateTime baseline FAILs remain visible.

## Public API and executable inspection

`add-variant name value :datatype locator :scope actual-themes` accepts an actual
Scope, not just the extra CTM themes. Datatype defaults to xsd:string. The Parent
Name and themes are resolved through existing canonical handles. All arguments
are checked before mutation. Public set readers return copies. Replaced objects
remain reachable through `canonical-variant` and `canonical-topic-name`; old EQ
identity does not change. Names retain their own independent Type Topics.

Run from the repository root in a fresh SBCL process:

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps/cxtm")
(defparameter *map*
  (topic-maps.ctm:deserialize-string
    "topic - kind:\"Name\" @parent-theme (\"variant\" @extra-theme)."
    :document-iri "https://example.invalid/variants.ctm"))
(defparameter *name*
  (first (loop for topic in (topic-maps.tmdm:topic-map-topics *map*)
               append (topic-maps.tmdm:topic-names topic))))
(defparameter *variant* (first (topic-maps.tmdm:topic-name-variants *name*)))
(assert (eq *name* (topic-maps.tmdm:variant-parent *variant*)))
(assert (= 1 (length (topic-maps.tmdm:topic-name-scope *name*))))
(assert (= 2 (length (topic-maps.tmdm:variant-scope *variant*))))
(describe *variant*)
(describe (topic-maps.tmdm:variant-parent *variant*))
(mapc #'describe (topic-maps.tmdm:variant-scope *variant*))
(write-string (topic-maps.cxtm:canonicalize *map*
               :base-locator "https://example.invalid/variants.ctm"))
```

No Source spans, persistent Inspector URLs or additional HyperDoc Views are
created. The independent model remains ordinary inspectable Lisp structures.
