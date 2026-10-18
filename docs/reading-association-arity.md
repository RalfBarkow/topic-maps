# Reading Associations with Arbitrarily Many Roles

Slice 17A builds on `f1270a43720ab1454bebfb3d0a9e3555554a7ab9`.
It removes a CTM reader restriction; it introduces no TMDM information items,
public model API, identity rules or canonicalization rules.

## Normative requirements

- [CTM §3.13](https://www.isotopicmaps.org/ctm/ctm.html), productions 59–62:
  an Association has one or more Role declarations, without an upper bound.
  Type/Player references, optional Association Scope and Association/Role
  Reifiers continue to use the existing shared deserialization mechanisms.
- [TMDM §§5.7–5.8, 6.6–6.7](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/):
  Association equality considers Type, Scope and its Role set. Roles sharing
  Parent, Type and Player merge; their Item Identifiers are united and their
  Reifiers handled by the existing merge rules. Declaration order is not a
  further identity property.
- [CXTM §§3.9–3.10, 3.19, 4.4, 4.10–4.11](https://www.isotopicmaps.org/cxtm/cxtm.html):
  number sorted Associations/Roles and emit complete rolePlayed references.
  Association ordering uses Type/Roles/Scope/Parent; Role ordering uses
  Player/Type/Parent. The existing implementation already handles these sets.

## Original source, expected model and current observation

The untouched pinned `ctm/in/association-duplicate-role.ctm` contains:

```text
assoctype(roletype1: topic1, roletype2: topic2, roletype3: topic3, roletype1: topic1)
```

Document IRI:
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/association-duplicate-role.ctm`.

The expected result has seven Topics identified by Document-IRI-relative Item
Identifiers, one Association typed by the `#assoctype` Topic, and three Roles:
`#roletype1 → #topic1`, `#roletype2 → #topic2`, `#roletype3 → #topic3`.
Each Role's Parent is the actual Association object; `topic-roles-played`
returns that same Role. Scope is empty and Reifiers are null. No Names or
Occurrences are required. The repeated first Role declaration does not add a
fourth distinct Role. The original CXTM baseline is 1,157 bytes.

`reports/slice-17a/arity.json` records observations of these actual references;
`association-duplicate-role.ctm.cxtm` records actual serialized bytes. The
imported contract is executed through CTM deserialization, not manual model
construction. The independent JSON/XML checker verifies the observed Type,
Player and Parent relations against the original baseline.

## Inspect actual Lisp objects

These forms load only the independent reader into the calling process. For a
fresh inspection use SBCL with `--no-sysinit --no-userinit`. The recorded
`describe.log` belongs to its isolated execution context; printed addresses are
not persistent Topic identity.

```lisp
(require :asdf)
(asdf:load-asd #P"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm")
(let* ((base "https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/association-duplicate-role.ctm")
       (map (topic-maps.ctm:deserialize-file
              #P"/Users/rgb/workspace/topic-maps/vendor/cxtm/ctm/in/association-duplicate-role.ctm"
              :document-iri base))
       (association (first (topic-maps.tmdm:topic-map-associations map))))
  (assert (= 3 (length (topic-maps.tmdm:association-roles association))))
  (describe association)
  (dolist (role (topic-maps.tmdm:association-roles association))
    (assert (eq association (topic-maps.tmdm:association-role-parent role)))
    (describe role)
    (format t "~&Type ~S -> Player ~S~%"
      (topic-maps.tmdm:topic-item-identifiers (topic-maps.tmdm:association-role-type role))
      (topic-maps.tmdm:topic-item-identifiers (topic-maps.tmdm:association-role-player role)))))
```

## Explicit boundary: Slice 17B

`isa`/`ako` remain unsupported. TMDM §7.1 requires the distinct Core Subjects
defined in §7 to remain distinct. Read-only probes at the accepted base showed
that merging the Topics identified by `.../type` and `.../instance`, or adding
both Subject Identifiers to one Topic, was accepted. This is an open normative
requirement for Slice 17B. Slice 17A does not change those identity operations
or claim to correct that discrepancy. General n-ary Associations must not be
confused with the exactly binary standardized relationships of §§7.2–7.3.

Templates, Include/Mergemap and HyperDoc changes are excluded. The two existing
DateTime baseline discrepancies remain FAIL, not implementation successes.
