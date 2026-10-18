# Reification within one Topic Map — Slice 16B

Reification connects an existing non-Topic construct with a Topic representing
its subject. It adds neither a second model nor another identity registry.
Source declarations, current Lisp objects and canonical XML remain separate.

## Normative requirements

The published [TMDM](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
§§5.2–5.8 supply Reifier on Map, Name, Variant, Occurrence, Association and Role.
§§5.3.4–5.3.5 exclude Topic reification and define the computed Reified inverse
and Topic equality. §§5.4–5.8 retain structural item equality; Reifier and Item
Identifiers are metadata, not new non-Topic equality keys. §6.2 prohibits merging
Topics with different non-null Reified targets and replaces Reifier references.
§§6.3–6.7 merge Reifiers when their items merge, preserving identifier unions;
§6.1 requires subsequent duplicate removal. Variant Scope still obeys §5.5.

[CTM](https://www.isotopicmaps.org/ctm/ctm.html) §3.3.10 resolves `~ topic-ref`
through §§3.3.6–3.3.8, including Wildcards and Embedded Topics. Attachment points
are §3.5 (Map), §3.10 (Occurrence), §3.11 (Name, before Variants), §3.12 (Variant,
inside its parentheses) and §3.13 (individual Role and Association). Map Reifier
follows leading directives and precedes body declarations.

[CXTM](https://www.isotopicmaps.org/cxtm/cxtm.html) §§3.4–3.11 encode Reifier as
an attribute referencing the canonical Topic number; null is omitted. Existing
sort keys (§§4.6–4.11) remain unchanged. Reifier is not an ordering tie breaker.

## API and object contracts

```lisp
(topic-maps.tmdm:item-reifier item)       ; actual current Topic or NIL
(topic-maps.tmdm:topic-reified topic)     ; computed current item or NIL
(topic-maps.tmdm:set-item-reifier item topic)
```

`set-item-reifier` returns the canonical item. As a local API choice, it asserts
Reification: an existing different Reifier Topic is merged with the supplied one.
It never silently discards that Topic's identity. Passing NIL explicitly clears
the relation. A foreign Topic, non-Topic argument, Topic as target, or a Topic
already reifying a different current item is rejected with `reification-error`.
Inspect `reification-error-code` for `:foreign-reifier`, `:invalid-reifier`,
`:not-reifiable`, `:invalid-item`, `:foreign-item` or `:reifier-conflict`.

Old Topic/item handles resolve through the existing canonical functions. Topic
has no Reifier slot. Its Reified property is computed by scanning actual live
Reifier properties; there is no independently maintained inverse identity store.
All stored Reifier references point to current Topics of the same Map.

## Merge cascades and atomic API policy

Item replacement redirects old handles and child ownership before combining
Reifiers, so the Topic merge sees the new target, not two discarded items.
Normalizers rescan current owners after each replacement. This matters when a
Reifier is also a Parent, Type, Theme or Player. Normalization continues to a
fixed point. Association replacement retains both Role sets and merges matching
Roles, preserving both their Item Identifiers and Reifiers.

When a public Topic identity/merge operation or Reification assertion can affect
an existing relation, the same operation runs first on a disposable copy of the
current seven TMDM structures. It uses the same merge functions, not simulated
identity rules. Only after a successful full cascade does it run on original
objects. Nested steps do not repeat the outer copy. Tests cover scope collapse
at four cascade levels, through direct merge and both identifier APIs.

This is a bounded semantic preflight policy, not a general transaction engine
or a normative TMDM transaction requirement. It does not promise recovery from
resource exhaustion or interruption. Cost includes copying the current Map.
Two separately invoked public operations are not one transaction.

The historical Topic-SI/Occurrence-II overlap restriction is removed. Equal
locator strings alone establish no automatic Reification between a Topic and a
non-Topic item. TMDM §5.3.5's SI/II cross-identity rule concerns two Topics.
All general Item Identifier uniqueness rules from Slice 16A remain active.

## Current evidence and boundaries

The eleven original positive Reifier CTM cases execute end-to-end and are
compared as UTF-8 bytes with unchanged upstream CXTM baselines. The two original
negative cases test `:reifier-conflict` and `:topic-map-reifier-position`, including
marker positions. Object snapshots and EQ assertions are separate from XML tests.
The independent Python checker connects observed Reifier Topic identities and
inverse assertions to the source and baseline. Execution context and source
hashes are recorded in `reports/slice-16b/execution.json`; object addresses in
`describe.log` belong only to that isolated process.

Templates, Include/Mergemap, cross-document merging, XTM deserialization, CTM
Associations above two roles, new datatypes and HyperDoc remain outside scope.
The two known DateTime baseline conflicts are unchanged.

## Inspect actual objects in a fresh process

Run these forms from the checkout root:

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/cxtm")
(let* ((map (topic-maps.tmdm:make-topic-map))
       (a (topic-maps.tmdm:intern-topic map :subject-identifier "urn:owner:a"))
       (b (topic-maps.tmdm:intern-topic map :subject-identifier "urn:owner:b"))
       (r (topic-maps.tmdm:intern-topic map :subject-identifier "urn:reifier:r"))
       (s (topic-maps.tmdm:intern-topic map :subject-identifier "urn:reifier:s"))
       (n (topic-maps.tmdm:add-name a "N"))
       (other (topic-maps.tmdm:add-name b "N")))
  (topic-maps.tmdm:add-item-identifier n "urn:name:a")
  (topic-maps.tmdm:add-item-identifier other "urn:name:b")
  (topic-maps.tmdm:set-item-reifier n r)
  (topic-maps.tmdm:set-item-reifier other s)
  (topic-maps.tmdm:merge-topics a b)
  (assert (eq (topic-maps.tmdm:canonical-topic-name n)
              (topic-maps.tmdm:canonical-topic-name other)))
  (assert (eq (topic-maps.tmdm:item-reifier n) (topic-maps.tmdm:canonical-topic s)))
  (assert (eq (topic-maps.tmdm:canonical-topic-name n) (topic-maps.tmdm:topic-reified r)))
  (describe (topic-maps.tmdm:canonical-topic-name n))
  (describe (topic-maps.tmdm:item-reifier n))
  (format t "~A" (topic-maps.cxtm:canonicalize map :base-locator "https://example.invalid/reification.ctm")))
```
