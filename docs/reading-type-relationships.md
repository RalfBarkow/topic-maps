# Reading isa, ako and Core Subject Consistency

Slice 17B starts from `bdc56a8236c6e6180df217d37e82846025026096`.
It uses the same seven information-item structures, ordinary Topic references,
Association/Role constructors, replacement handles and canonical serializer.

## Normative requirements and the exact vocabulary

[CTM §3.9](https://www.isotopicmaps.org/ctm/ctm.html#sec-topic-tail),
productions 50–55, defines `isa topic-ref` and `ako topic-ref` as Topic Tail
elements. Each has one right-hand reference; repeated statements are separated
by semicolons. The common resolver also admits QNames, explicit SI/SL/II forms,
Wildcards and recursive Embedded Topics (§§3.3.6–3.3.8).

[TMDM §7.1](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
requires the Core Subjects defined in §7 to be distinct. Their published
Subject Identifiers use `http://psi.topicmaps.org/iso13250/model/` plus:

| Clause | Local parts |
|---|---|
| 7.2 | `type-instance`, `type`, `instance` |
| 7.3 | `supertype-subtype`, `supertype`, `subtype` |
| 7.4 | `sort` |
| 7.5 | `name-type` |

The protected set therefore has eight locators, including all six used by these
relationships. These constants are not Topic objects or another identity index.
`core-subject-identifiers` returns private copies of their strings.

The cited 2006 text spells §7.5's locator `.../name-type`. CTM §3.11 and the
accepted existing default Name mapping use `.../topic-name`. This slice does not
infer an alias between those two strings, rewrite existing Name Types, or extend
the protected set by guessing. All retained Name results stay unchanged.

The expansion mandated by TMDM §§7.2–7.3 is:

| Input | Association Type SI local part | Role Type SI → Player |
|---|---|---|
| `a isa b.` | `type-instance` | `instance → a`, `type → b` |
| `a ako b.` | `supertype-subtype` | `subtype → a`, `supertype → b` |

Each expansion has exactly two Role items, empty Scope and null Reifier.
Normal Associations remain n-ary. A differently structured Association using
these Subjects does not become a standardized relationship merely by its type.
No special Topic slots or another type hierarchy representation are introduced.

`isa` is not transitive. `ako` is transitive, but TMDM §7.3 does not require
materializing inferred Associations. Cycles do not imply Topic identity. Only
explicitly deserialized relationships are stored here. This is not a query or
inference engine.

## Identity, equality, merging and API policy

TMDM §§5.3.5, 5.7–5.8 and 6.2/6.6–6.7 remain the identity/equality/merge rules.
Short and long Association syntax normalize to the same canonical items.
Subject Identifiers of distinct Core Subjects must never occur on one Topic.
The guard compares actual locator strings in that property, not CXTM-normalized
strings or an IRI merely occurring in a Subject Locator/Item Identifier slot.
An Item Identifier can nevertheless cause a conflict through the existing
SI/II Topic identity rule; this is checked before committing the mutation.

The public failure is `core-subject-error`, code `:core-subject-conflict`.
The affected operations are `merge-topics`, `add-topic-identifier` (also reached
by Topic `add-item-identifier`), `intern-topic`, `normalize-topic-map`, and
Reifier-triggered merging via `set-item-reifier`. `intern-topic` preflights
before appending a new Topic. Old handles still resolve through the existing
canonical accessors. Valid alias merges of the same Core Subject remain legal.

**Normative invariant:** the contradictory Core Subject state is forbidden.
**Local API policy:** reject the whole semantic operation before changing any
original item, identifier list or forward link. The existing disposable copy
of the same TMDM graph now covers Core conflicts as well as Reifier cascades;
its internal entry points are `needs-merge-preflight-p` and
`preflight-merge-mutation`. It is not a second model or a rollback engine, and
does not promise recovery from resource exhaustion. White-box normalization
tests explicitly identify intentionally unnormalized initial graphs.

The CTM layer reports Core conflicts as `ctm-rejection/:core-subject-conflict`.
Missing relationship targets and comma lists have dedicated rejection codes
and source positions; undefined prefixes retain their own condition class.
The CXTM validator rejects a deliberately corrupted Core state without mutation.
CXTM §§3.9–3.10 and 4.10–4.11 still supply the unchanged representation/sort rules:
[published CXTM](https://www.isotopicmaps.org/cxtm/cxtm.html).

## Original contracts and current object observations

All sources/baselines are the untouched pinned corpus at
`cd165b150176c1d6842b37be9cc9051b40d4996b`. Its CTM tests target the draft of
2010-03-31; the published standards remain authoritative. For every row the
Document IRI is `https://ctm-tests.example.invalid/` + pin + `/ctm/in/` + filename.
Local Item Identifiers append `#identifier` to that absolute Document IRI.
The existing CXTM base-locator policy produces the relative locators in the
supplied baselines; no baseline or comparison normalization was changed.

| File | Topics | Associations | Actual/expected CXTM bytes |
|---|---:|---:|---:|
| `isa-relationship.ctm` | 5 | 1 | 963 / 963 |
| `isa-relationship-duplicate.ctm` | 5 | 1 | 963 / 963 |
| `isa-relationship-duplicate2.ctm` | 5 | 1 | 963 / 963 |
| `isa-relationship-embedded.ctm` | 6 | 1 | 1,181 / 1,181 |
| `isa-relationship-type-qname.ctm` | 5 | 1 | 991 / 991 |
| `ako-relationship.ctm` | 5 | 1 | 977 / 977 |
| `ako-relationship-duplicate.ctm` | 5 | 1 | 977 / 977 |
| `ako-relationship-duplicate2.ctm` | 5 | 1 | 977 / 977 |
| `ako-relationship-embedded.ctm` | 6 | 1 | 1,190 / 1,190 |
| `ako-relationship-supertype-qname.ctm` | 5 | 1 | 1,005 / 1,005 |
| `ako-merge-away.ctm` | 6 | 2 | 1,590 / 1,590 |
| `subject-identifier-topicref.ctm` | 5 | 1 | 989 / 989 |
| `item-identifier-topicref.ctm` | 5 | 1 | 985 / 985 |

All thirteen are real CTM→TMDM→CXTM byte-exact comparisons. Every Association has
two Roles. In `isa-relationship.ctm` the actual `type-instance` Topic is the
Association Type; Role Type `instance` points to the Topic with II `#ctm`, and
Role Type `type` points to II `#format`. Each Role's Parent is EQ to its actual
Association and the computed rolesPlayed inverse contains the same Role object.
`ako-relationship.ctm` analogously binds `subtype → #tm-syntax` and
`supertype → #syntax`. Embedded examples add an actual Name item and the existing
default Name-Type Topic. The QName and explicit identity cases preserve their
different SI/II bindings.

`ako-merge-away.ctm` binds local `haha`/`hehe`/`hoho` aliases to the standardized
Association/Role-Type Topics between two assertions. The resolver looks up the
Core locators anew and canonicalizes references; no stale Topic cache is used.
Both resulting Associations refer to the same current Type Topic.

`reports/slice-17b/relationships.json` records each unmodified source, absolute
Document IRI, actual Topic identities, Association Type, Scope, Role Type/Player,
and EQ/Parent/inverse observations. Its atomic-conflict records refer to executed
tests, not inferred runtime behavior. `execution.json` binds those observations
to source hashes, runtime and UTC interval. The independent Python checker
compares these reference graphs against the original XML separately from the
raw byte comparison. Norm interpretation, upstream evidence and current Lisp
observations are distinct evidence sources.

## Reading the relationships back (TMDM 7.2 and 7.3)

The reader and the model have always *stored* these relationships as ordinary
Associations. Six functions of `topic-maps.tmdm` now also *recognize* them.
They are added API over stored items, not a repair of a conformance defect:
storing a conforming Association was and is sufficient for the data model.

| Function | Returns |
|---|---|
| `type-instance-relationship association` | `(values type instance)`, the two player Topics, or `(values nil nil)` |
| `supertype-subtype-relationship association` | `(values supertype subtype)`, or `(values nil nil)` |
| `topic-type-associations topic` | the 7.2 Associations in which `topic` is the instance |
| `topic-instance-associations topic` | the 7.2 Associations in which `topic` is the type |
| `topic-supertype-associations topic` | the 7.3 Associations in which `topic` is the subtype |
| `topic-subtype-associations topic` | the 7.3 Associations in which `topic` is the supertype |

An Association is recognized exactly when it has the structure the clause
states: its Type has the relationship's Subject Identifier, it has exactly two
Roles, and one Role Type has each of the two role Subject Identifiers. The
clauses name the `[subject identifiers]` property, so the same locator as an
Item Identifier or Subject Locator does not count. An Association that uses the
identifiers with any other structure "is not considered to represent" the
relationship, and the readers return nothing for it.

The Topic readers return Associations, not player Topics, so that each
statement's Scope, Reifier and Item Identifiers stay reachable. TMDM 7.2 and 7.3
say that Scope applies to these Associations as to any other; the readers do not
evaluate it.

What the readers do not do: they intern no Topic, keep no index, change no item,
and infer nothing. `a isa b. b ako c.` yields `b` as the only stated type of
`a`; the transitive and instance-of-supertype consequences that TMDM 7.3
describes are not computed, and TMDM does not require Associations for them.
Sort names (TMDM 7.4) have no reader.

```lisp
(let* ((map (topic-maps.ctm:deserialize-string "a isa b." :document-iri "https://example.invalid/doc.ctm"))
       (association (first (topic-maps.tmdm:topic-map-associations map))))
  (multiple-value-bind (type instance) (topic-maps.tmdm:type-instance-relationship association)
    (list type instance (topic-maps.tmdm:topic-type-associations instance))))
```

`tests/core-relationships.lisp` argues each expectation from its clause.
`scripts/check-core-relationships.py` separately counts such Associations in
the eleven unchanged original CXTM baselines; that is an evaluation of
serialized data, not a proof of conformance.

## Two documented default name type identifiers

The TMDM text dated 2006-06-18 spells clause 7.5's identifier
`http://psi.topicmaps.org/iso13250/model/name-type`; the text dated 2008-06-03
spells it `http://psi.topicmaps.org/iso13250/model/topic-name`, as CTM 3.11 and
XTM 2.0 do. This library treats both as documented identifiers that a map may
contain, and does not decide which text is authoritative.

- They are different Subject Identifiers. Topics carrying one or the other are
  different Topics, and nothing equates them automatically.
- An explicitly stated Name Type is kept on import and in CXTM, whichever
  identifier it carries.
- A Name without a stated type gets `.../topic-name`, as CTM 3.11 and XTM 2.0
  specify for their syntaxes; `default-name-type-identifier` returns it.
- The protected Core Subject set of TMDM 7.1 is unchanged: it holds
  `.../name-type` and not `.../topic-name`.

`tests/default-name-types.lisp` shows preservation and coexistence. It also
records, as a characterization of current behaviour and not as a rule, that an
explicit `merge-topics` of the two type Topics is accepted and leaves one Topic
with both identifiers. See [the coverage matrix](tmdm-coverage-matrix.md).

## Fresh-process inspection

In a fresh SBCL process with `--no-sysinit --no-userinit`:

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #P"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm")
(let ((map (topic-maps.ctm:deserialize-string "a isa b; ako c."
             :document-iri "https://example.invalid/relationships.ctm")))
  (assert (= 2 (length (topic-maps.tmdm:topic-map-associations map))))
  (dolist (association (topic-maps.tmdm:topic-map-associations map))
    (describe association)
    (dolist (role (topic-maps.tmdm:association-roles association))
      (assert (eq association (topic-maps.tmdm:association-role-parent role)))
      (describe role)
      (format t "~&Role Type: ~S; Player II: ~S~%"
        (topic-maps.tmdm:topic-subject-identifiers (topic-maps.tmdm:association-role-type role))
        (topic-maps.tmdm:topic-item-identifiers (topic-maps.tmdm:association-role-player role))))))
```

`describe.log` records one disposable execution of these forms; printed addresses
are historical process-local observations, not durable Topic identity.

Templates, Include/Mergemap, cross-document merging, XTM deserialization, further
datatypes and HyperDoc integration remain excluded. The two known DateTime
baseline discrepancies remain FAIL. Full CTM/TMDM conformance is not claimed.
