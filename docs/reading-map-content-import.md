# Reading Map Content Import

Slice 19A builds on `0573c4f710982dab1c3f2c9284adf459caaf73e9`.
It changes the independent TMDM system; the CTM reader, CXTM canonicalizer and
pinned corpus (`cd165b150176c1d6842b37be9cc9051b40d4996b`) are unchanged.

## Normative basis and local API choices

[TMDM 2006](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/):
§4.3 requires exact locator-string equality. §5.1 constrains identifier uniqueness;
§5.3.5 supplies Topic identity. §§5.4–5.8 define the structural item equalities.
§5.5 requires the Variant scope to properly contain its Name scope.
§6.1 requires duplicate removal after changes; §§6.2–6.7 specify replacement,
reference rewriting and metadata union, including Reifier merging. §6.2 rejects
merging Topics that reify different items; §7.1 protects distinct Core Subjects.

These are model requirements. The two-return-value API, source-preserving copy,
source Map exclusion, self-import rejection and preflight transaction policy
below are explicit implementation choices for this content-import operation.
The operation does not merge two root Map items and is not a CTM directive.

## Public API and object lifetime

`(import-map-content target source)` returns `TARGET` and a resolver function.
Both arguments must be different valid Maps. Wrong argument types signal
`TYPE-ERROR`; self-import signals `MAP-IMPORT-ERROR`, code `:SAME-MAP`.

`(funcall resolve source-item)` returns the current canonical target object.
Several source objects can resolve to one target. The table contains original
source snapshot objects, never locator-to-subject identities. Existing source
aliases may resolve through their snapshot representative. A known snapshot
object still works if its source handle later forwards elsewhere. A newly
created source object is not automatically imported. Source Map, foreign objects
and objects outside the snapshot signal `MAP-IMPORT-ERROR :NOT-IMPORTED`.
No durable object IDs or URLs are manufactured. The resolver and source/target
object references belong to the calling Lisp process. Keep the resolver while
its mapping is needed; no global import registry is retained.

The target Map stays the parent. Source Map item identifiers and its Reifier
edge are excluded. The source's map-reifying Topic is still copied as an ordinary
content Topic; it does not thereby reify the target Map. Target root metadata
and its consistency constraints remain active.

## Transfer and normalization

`copy-map-graph` generalizes the existing disposable preflight graph copier.
It first allocates same-model Topic shells, then Names/Variants/Occurrences and
Associations/Roles, and finally assigns rewritten Scopes, Reifiers and identifier
sets. The copy table only maps actual objects. New locator/value/datatype strings
and collections are copied too. Parent, Type, Player, Theme and Reifier references
remain inside the target. No source object's forwarding link is changed.

`normalize-topic-map` performs ordinary same-map merging on the complete graph.
A Reifier-first construction-order regression exposed premature conflict
selection in the old normalizer. Normalization now selects an available
nonconflicting equal Topic pair first. Owner/Type merging can then make the
reified items equal and merge their Reifiers by the existing item rules. If no
such pair can proceed, the existing Reifier-conflict check still rejects. Explicit
`merge-topics` conflict rules and the cross-map restriction are unchanged.

`validate-import-map` checks current graph membership, parents, canonical
references, Scope sets, identifier uniqueness, Reification, Variant and Core
constraints. Identifier collisions between unequal items are checked after
normalization; equal structural items can therefore union their metadata first.

The complete operation is tried on a fresh target copy before actual target
changes. Both paths use the same seven structures and merge functions. Semantic
failures leave both maps, stored strings and held handles unchanged. This is a
single-threaded API guarantee; allocation failure, asynchronous interruption or
concurrent external slot mutation does not have a rollback guarantee.

Repeat imports are tested through actual Topic identity and item equality,
without an already-imported list. Fixtures with shared identifiers produce no
new items on repetition. Different document-relative identities remain distinct
without identity evidence. No general promise based solely on import repetition
is used, and CXTM-normalized strings never determine TMDM identity.

## Direct inspection in a fresh process

Run from the repository root. Only `topic-maps/tmdm` is required; no CTM, CXTM,
HyperDoc system or persistent image is loaded.

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/tmdm")
(let* ((source (topic-maps.tmdm:make-topic-map))
       (target (topic-maps.tmdm:make-topic-map))
       (owner (topic-maps.tmdm:intern-topic source :subject-identifier "urn:owner"))
       (type (topic-maps.tmdm:intern-topic source :subject-identifier "urn:type"))
       (theme (topic-maps.tmdm:intern-topic source :subject-identifier "urn:theme"))
       (name (topic-maps.tmdm:add-name owner "Name" :type type))
       (variant (topic-maps.tmdm:add-variant name "V" :scope (list theme)))
       (occ (topic-maps.tmdm:add-occurrence owner type "+0007"
               :datatype (topic-maps.tmdm:integer-datatype) :scope (list theme)))
       (association (topic-maps.tmdm:make-association source type (list (list type owner))))
       (reifier (topic-maps.tmdm:intern-topic source :subject-identifier "urn:reifier")))
  (topic-maps.tmdm:add-item-identifier source "urn:source-map-only")
  (topic-maps.tmdm:add-item-identifier name "urn:name")
  (topic-maps.tmdm:set-item-reifier name reifier)
  (multiple-value-bind (result resolve) (topic-maps.tmdm:import-map-content target source)
    (let* ((new-owner (funcall resolve owner)) (new-name (funcall resolve name))
           (new-occ (funcall resolve occ)) (new-association (funcall resolve association)))
      (assert (eq target result))
      (assert (not (eq owner new-owner)))
      (assert (eq source (topic-maps.tmdm:topic-parent owner)))
      (assert (eq target (topic-maps.tmdm:topic-parent new-owner)))
      (assert (eq new-owner (topic-maps.tmdm:topic-name-parent new-name)))
      (assert (eq (funcall resolve type) (topic-maps.tmdm:topic-name-type new-name)))
      (assert (eq new-name (topic-maps.tmdm:variant-parent (funcall resolve variant))))
      (assert (eq new-owner (topic-maps.tmdm:occurrence-parent new-occ)))
      (assert (eq new-owner (topic-maps.tmdm:association-role-player
                            (first (topic-maps.tmdm:association-roles new-association)))))
      (assert (eq new-name (topic-maps.tmdm:topic-reified (funcall resolve reifier))))
      (assert (null (topic-maps.tmdm:item-identifiers target)))
      (mapc #'describe (list source target name new-name new-occ new-association))
      (format t "~&IMPORT-INSPECTION-PASS: copied graph; actual EQ references; source unchanged.~%"))))
```

## Evidence and limits

`tests/map-import.lisp` checks six-kind transfers, all relevant references by EQ,
Topic identity categories, many-to-one mappings, all six imported kinds against
seven target kinds for identifier collisions, Reifier cascades, atomic conflicts,
source/target old handles, repeated import, construction order and CXTM purity.
It checks raw slots of live and retained objects plus source CXTM before/after.
`reports/slice-19a/map-import.json` records model witnesses and actual canonical
XML. Its independent Python checker verifies item counts, metadata and output
references. These are manually constructed model examples, not imported CTM/XTM
conformance contracts. `base-normalizer-control.log` reproduces the ordering
regression with the committed base normalizer in a separate disposable process.

No resource retrieval, `%include`, `%mergemap`, Include-local identifier aliases,
Template binding transport or XTM deserializer is provided. No new literal form
or HyperDoc integration is included. The two known DateTime baseline conflicts
remain visible. This slice does not claim complete CTM or TMDM conformance.
