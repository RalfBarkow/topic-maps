# Reading Wildcards and Embedded Topics — Slice 15

Base commit: `4f7b4d26d40f8f5566594aa2e3ad6296d44fc4c3`.
This slice completes Topic references for the already supported CTM statements.
It adds no TMDM class, HyperDoc integration, Template engine or import mechanism.

## Normative requirements

[CTM §3.2](https://www.isotopicmaps.org/ctm/ctm.html) supplies the Document IRI,
a Wildcard IRI defaulting to it, and a non-negative Wildcard Counter defaulting
to zero. §§3.3.6–3.3.8 map topic identities and references to actual Topics.
For an anonymous `?`, increment the counter, then append `#$__` and the decimal
counter to Wildcard IRI. First use of `?name` also increments it and appends
`.name`; repeated uses reuse the locator. An Embedded Topic's `[` is handled
as an anonymous wildcard; its nonempty Topic Tail is processed before `]`.
The existing Topic-Tail implementation (§3.9) is reused recursively.

[TMDM §§5.1/5.3.5 and 6.1–6.7](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
govern Item Identifiers, Topic equality and reference replacement. Wildcard
locators are Item Identifiers, never Subject Identifiers or separate model items.
Explicit identities within an Embedded Tail can merge its Topic with an existing
Topic. Callers must receive the current canonical Topic after that Tail.

[CXTM §§3.4–3.21 and 4.3–4.11](https://www.isotopicmaps.org/cxtm/cxtm.html)
apply to the resulting existing model. Embedded Topics have no special CXTM
element. Topic numbering, locators, Parent/Type/Player references, Scopes and
Variants use the unchanged canonicalizer. Canonicalization never mutates objects.

The corpus remains pinned to `cd165b150176c1d6842b37be9cc9051b40d4996b`, with
its original 2010-03-31 draft qualification. Its sources and XML baselines are
unchanged evidence, not the source of the implementation rules.

## Public API and environment

Both `deserialize-string` and `deserialize-file` now accept:

```text
:document-iri    required absolute, fragment-free IRI
:source-name     optional diagnostic identity
:wildcard-iri    optional absolute, fragment-free IRI; defaults to Document IRI
:wildcard-counter optional non-negative integer; defaults to 0
```

They return two values: the TMDM Topic Map and the final counter. Existing callers
using just the first value retain their behavior. Environment arguments are
validated before parsing or file I/O. No global counter or name registry is used.
Named wildcard bindings cache locator strings; existing identity resolution finds
the current Topic even after replacement merging. Counter arithmetic is arbitrary
precision. Wildcard names preserve case and Unicode.

Document IRI continues to resolve local `identifier`s, relative IRIs and prefix
bindings. Wildcard IRI controls only generated Item Identifiers. It is not a
new document base. Separate parses have independent environments and objects;
no cross-document merging is implied by this API.

The shared `topic-reference` path handles identity forms and Embedded Topics at
Name/Occurrence/Association Type, Role Type/Player and Scope positions. Identity
statements in a Tail still add identifiers directly to the owner without an
unnecessary intermediate Topic. Nonempty Embedded Tails may have a trailing
semicolon; a period does not replace their closing bracket. A bare Embedded
Topic is not a top-level Topic declaration, but can be an Association Type.

## Original contracts

The following unmodified original sources execute against their original CXTM
baselines. Their Document IRI is the established
`https://ctm-tests.example.invalid/<pin>/ctm/in/<filename>.ctm`; Wildcard IRI
defaults to it and Counter starts at zero. The same Document IRI is supplied as
CXTM Base Locator. Stored generated identifiers are absolute, while baseline
`#$__...` strings are their canonical locator representation.

| Original positive case | Final counter |
|---|---:|
| wildcard | 1 |
| wildcard-named | 1 |
| wildcard-named2 | 3 |
| wildcard-named-merge | 1 |
| association-scope-embedded | 2 |
| association-scope-embedded2 | 3 |
| association-type-embedded | 1 |
| association-type-embedded-merge | 2 |
| embedded-semicolon | 1 |
| name-scope-embedded | 2 |
| name-scope-embedded2 | 3 |
| name-type-embedded | 1 |
| nested-twice | 2 |
| occurrence-scope-embedded | 2 |
| occurrence-scope-embedded2 | 3 |
| occurrence-type-embedded | 1 |
| role-player-embedded | 1 |
| role-type-embedded | 1 |
| subject-identifier-embedded | 1 |
| variant-scope-embedded | 3 |
| variant-scope-embedded2 | 4 |

For example, original `wildcard-named-merge.ctm` is `\n?foo.?foo.`. It creates
one Topic with Item Identifier `DocumentIRI#$__1.foo`, not two Topics or a Subject
Identifier. Original `association-type-embedded-merge.ctm` creates two generated
locators, then its shared SI merges their Topics and the duplicate Associations.
Both Item Identifiers remain on the canonical Topic.

Original `nested-twice.ctm`:

```text

topic
  [-[-"name"]: "occ-type"]: "Occurrence".
```

It creates four Topics: the owner, two generated Types and the default Name Type.
There are two Names and one Occurrence. The outer Occurrence Type is the first
generated Topic; its Name Type is the second generated Topic, whose Name has
the default Type. These are actual object references, not label-based links.

`variant-scope-embedded.ctm` creates seven Topics, five Names and one Variant.
The Parent Name has one Theme; the Variant has three actual Themes after union
with that Parent Scope. The second case exercises further nesting and identity
merging. Explicit Scope remains distinct from resulting TMDM Scope.

Original negative `ctm/invalid/embedded-topic-global-scope.ctm` is:

```text
[-"This is not allowed"]
```

It receives `CTM-REJECTION / :EMBEDDED-TOPIC-AT-TOP-LEVEL` at the end of the
source: the complete Embedded Topic is not followed by Association Roles.
The Template-dependent `embedded-topic-template.ctm` remains NOT-RUN. A failure
at `def` would not establish the required invalid Template-body semantics.

The reference report contains every full original source, Document IRI, counter
and observed graph. Independent Python checks compare identifier-property sets,
all Names/Variants/Occurrences/Associations/Roles, Scopes and generated locators
with the baselines. Observation ordinals are local references, not persistent IDs.

## Executable Lisp inspection

From the repository root, in a fresh process:

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps/cxtm")
(defparameter *result*
  (multiple-value-list
    (topic-maps.ctm:deserialize-string
      "owner - [-\"Type\"]: \"Name\" @?view (\"variant\" @[-\"extra\"]). ?view."
      :document-iri "https://example.invalid/doc.ctm"
      :wildcard-iri "https://identity.example.invalid/run"
      :wildcard-counter 40)))
(defparameter *map* (first *result*))
(assert (= 43 (second *result*)))
(defparameter *owner*
  (find-if (lambda (topic)
             (member "https://example.invalid/doc.ctm#owner"
                     (topic-maps.tmdm:topic-item-identifiers topic) :test #'string=))
           (topic-maps.tmdm:topic-map-topics *map*)))
(defparameter *name* (first (topic-maps.tmdm:topic-names *owner*)))
(assert (eq *owner* (topic-maps.tmdm:topic-name-parent *name*)))
(assert (equal '("https://identity.example.invalid/run#$__41")
               (topic-maps.tmdm:topic-item-identifiers
                 (topic-maps.tmdm:topic-name-type *name*))))
(describe (topic-maps.tmdm:topic-name-type *name*))
(mapc #'describe (topic-maps.tmdm:topic-name-scope *name*))
(describe (first (topic-maps.tmdm:topic-name-variants *name*)))
(write-string (topic-maps.cxtm:canonicalize *map* :base-locator "https://example.invalid/doc.ctm"))
```

## Preserved boundaries

Reification, Templates, Include/Mergemap, `isa`/`ako`, CTM `*`, additional
Association arity and previously excluded datatype contexts are not implemented.
All same-map identity, Scope/Variant invariants and canonical retained-handle
contracts remain in the existing TMDM. No TMDM source changes are necessary.
The two known DateTime baseline FAILs remain visible. The independent previously
unregistered positive probes are not promoted by this slice.
