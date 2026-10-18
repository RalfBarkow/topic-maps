# General Item Identifiers — Slice 16A

An Item Identifier addresses an information item, not automatically its subject.
All seven existing TMDM item kinds now store their own identifier set. There is
no separate identity registry, no Scope class, and no Reification implementation.

## Normative contract and implementation choices

The published [TMDM](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
is authoritative: §5.1 defines identifier uniqueness; §§5.2–5.8 assign the
property to all seven item kinds. §§4.2–4.3 determine locator equality, and
§5.3.5 retains the distinct Topic II/SI/SL identity rules. §§6.2–6.7 require
identifier unions when the respective items merge. Non-Topic identifier equality
is not an additional structural equality rule.

The implementation compares stored resolved locator strings with `STRING=`.
It does not use CXTM base-relative or NFC-normalized output as identity keys.
Identifier collisions across distinct live items are rejected before mutation;
Topic–Topic collisions follow the existing Topic merge/preflight operation.
Equal Names, Variants, Occurrences, Associations and Roles retain their existing
structural equality rules and union their identifier metadata during replacement.

Returning replacement handles, rejecting invalid operations atomically and
copying locator strings are Lisp API choices. They preserve the existing API's
model invariants; they are not additional TMDM axioms.

## Public API

```lisp
(topic-maps.tmdm:item-identifiers item)
(topic-maps.tmdm:add-item-identifier item "urn:example:item")
```

The first form returns a fresh list containing fresh strings. The second adds
one already validated, resolved absolute locator and returns the current
representative. Repeated assignment is idempotent. It accepts retained handles;
for Topics it delegates to `add-topic-identifier`. The model checks the absolute
scheme shape; full source IRI processing remains the CTM reader's responsibility.

`topic-map-item-identifiers`, `topic-item-identifiers`,
`topic-name-item-identifiers`, `variant-item-identifiers`,
`occurrence-item-identifiers`, `association-item-identifiers` and
`association-role-item-identifiers` expose the same defensive-copy contract.

Existing constructors are reused. Assign identifiers through the common API
after constructing the item. The existing `add-occurrence :item-identifiers`
option remains supported, including validation before construction and copying
the supplied list and strings. Two separate public calls are not one transaction.

Identifier problems have `item-identifier-error` and `item-identifier-error-code`.
Codes include `:invalid-item-identifiers`, `:duplicate-item-identifier` and
`:invalid-item`. Historical Occurrence/Topic routes also retain compatibility
with `occurrence-error` through a shared condition subclass.

## Retained boundary for Slice 16B

The historical Topic-SI / Occurrence-II overlap guard remains explicitly
`:unsupported-reification-identity`, in both insertion directions. It is a
temporary implementation restriction, not a normative inference of Reification.
It is not extended to other item kinds. No `[reifier]`, `[reified]` or CTM `~`
support is introduced here. Its treatment requires the separate Slice 16B review.

## CXTM and external examples

[CXTM](https://www.isotopicmaps.org/cxtm/cxtm.html) §§3.4–3.10 determine
placement: Map identifiers precede Topics; Topic identifiers precede Names;
Name identifiers follow Variants; Variant/Occurrence identifiers follow Scope;
Association identifiers follow Scope; Role identifiers follow Type. §3.13
defines `itemIdentifiers`, §§3.17–3.20 locator representation, and §§4.3–4.5
ordering. Existing information-item sort keys (§§4.6–4.11) are unchanged.
Serialization validates global uniqueness and never repairs or mutates the model.

Seven original `xtm2/in/itemid*.xtm` examples are manually constructed as TMDM
objects and compared byte-for-byte against their untouched CXTM baselines:
`itemid-tm`, `itemid`, `itemid-name`, `itemid-variant`, `itemid-occurrence`,
`itemid-association`, `itemid-role`.
These are **manual model/baseline comparisons, not XTM deserialization contracts**.
The 273 CTM imported contracts and their statuses are unchanged.

## Inspect in a fresh Lisp process

Run these forms with this checkout as the working directory:

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/cxtm")
(let* ((map (topic-maps.tmdm:make-topic-map))
       (owner (topic-maps.tmdm:intern-topic map :subject-identifier "urn:example:owner"))
       (name (topic-maps.tmdm:add-name owner "Example")))
  (topic-maps.tmdm:add-item-identifier map "urn:example:map")
  (topic-maps.tmdm:add-item-identifier name "urn:example:name")
  (assert (equal '("urn:example:name") (topic-maps.tmdm:item-identifiers name)))
  (assert (eq owner (topic-maps.tmdm:topic-name-parent name)))
  (describe name)
  (describe (topic-maps.tmdm:topic-name-type name))
  (format t "~A" (topic-maps.cxtm:canonicalize map :base-locator "https://example.invalid/demo.ctm")))
```
