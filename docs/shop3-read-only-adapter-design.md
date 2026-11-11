# A read-only SHOP3 adapter over TMDM objects — design draft

Status: design only. Nothing described here is implemented, and no planning
infrastructure is added. The `topic-maps` library stays the only implementation
authority for TMDM objects; SHOP3 stays responsible for planning.

Based on `topic-maps` at `88994c1b` plus the readers for TMDM 7.2/7.3, and on
HyperDoc at `2b86477` (read, not changed).

## 1. Place and direction

The adapter belongs in HyperDoc, next to the existing SHOP3 layer
(`dreyeck/shop3`), not in `topic-maps`: the library has no dependency on SHOP3
or HyperDoc and should not get one. The adapter

- takes one native `topic-maps.tmdm:topic-map`;
- reads it through the library's public readers only;
- returns a set of facts and, from them, a SHOP3 initial state;
- never writes to the map, and never creates TMDM items.

What exists in HyperDoc today:

- `dreyeck/shop3/plan-objects.lisp`: `hyperdoc-htn-plan-result`, with
  `:execution-mode :plan-only`.
- `dreyeck/work/planning.lisp`: a SHOP3 domain whose initial state is written by
  hand, e.g. `(source-known connections)`.
- `dreyeck/work/project`: the project CTM read into native TMDM objects, with
  local helpers that read Associations by type and Role.

## 2. Three layers that must stay distinguishable

Every fact the adapter produces belongs to exactly one layer.

1. **TMDM items as they are.** Topics, Topic Names, Occurrences, Associations
   and Roles of the map. A fact of this layer restates one item, for example an
   Occurrence of a given type on a Topic, or one Association with its Role
   players.
2. **Relationships recognized by the library readers.** The type-instance and
   supertype-subtype relationships of TMDM 7.2 and 7.3, as reported by
   `type-instance-relationship`, `supertype-subtype-relationship` and the four
   Topic readers. These are still stated in the map; the reader only recognizes
   the structure the clause defines. The adapter must not re-derive them itself.
3. **Facts derived by named rules.** Anything the adapter computes beyond
   layers 1 and 2: for example the transitive closure of supertype-subtype, or
   "instance of a subtype is an instance of the supertype" (TMDM 7.3). Each
   such fact names the rule that produced it and the facts it was produced from.

Layer 3 is optional. A first adapter can stop after layer 2.

## 3. Fact records and warrant

A fact is a record held by the adapter, not a TMDM item:

| Field | Content |
|---|---|
| atom | the SHOP3 state atom, e.g. `(instance-of a b)` |
| layer | 1, 2 or 3 |
| source items | the TMDM item or items it restates or was recognized from |
| rule | for layer 3: the name of the rule; premises: the facts used |
| warrant | `observed`, `derived`, `inferred` or `hypothesized` |
| snapshot | identity of the map state the fact was read from |

The warrant belongs to the statement or derivation in the adapter. It is not
added to the TMDM model as a property, Occurrence or Scope.

- `observed`: layers 1 and 2. The atom corresponds to items present in the
  snapshot.
- `derived`: layer 3. The atom follows from observed facts by a named rule.
- `inferred`, `hypothesized`: never produced by the adapter. If a caller
  supplies such facts, they carry that label and are kept apart from the
  exported TMDM facts.

If a map itself models provenance, for example by reifying an Association and
giving the Reifier Occurrences, that is ordinary TMDM content of layer 1. It is
read like any other content and is not the adapter's warrant.

## 4. From facts to a SHOP3 problem

- The initial state is the list of atoms of the chosen facts.
- Method and operator preconditions query that state only. SHOP3 does not call
  back into TMDM while planning, so a plan refers to one fixed snapshot.
- The result stays a plan-only object. Operators change the planner's state,
  not the map.

Which TMDM statements become which predicates is declared in an explicit
vocabulary mapping (Association type and Role types to predicate and argument
order; Occurrence type to predicate). Nothing is exported that the mapping does
not name.

## 5. Missing prerequisites for a plan over real TMDM objects

1. **Term names.** SHOP3 atoms need constants. A rule is needed that maps each
   Topic to one stable constant and back. "The first Subject Identifier" is not
   a rule: the order of a set is not significant. How SHOP3 unifies non-symbol
   constants such as strings has to be checked before choosing a representation.
2. **Scope.** TMDM leaves open how a Scope defines a context (5.3.3). The
   adapter needs a declared rule: for example, export only statements in the
   unconstrained scope, or export a statement when its scope is contained in an
   explicitly given set of themes. Layer 3 rules must say how they combine the
   scopes of their premises (TMDM 7.3 gives an example).
3. **Vocabulary mapping.** For the project map: which Association types mean
   dependency, which Occurrence type carries status, and what the planner's
   predicates are called.
4. **Snapshot identity.** A way to tell that facts are stale, for example the
   SHA-256 of the map's CXTM at export time.
5. **Derived closure.** A decision whether layer 3 is wanted at all, and if so
   which rules.
6. **A planning domain.** Operators and methods are written by a person. They
   cannot be read from the map.
7. **A library revision in HyperDoc that has the readers.** HyperDoc pins
   `topic-maps` at `88994c1b`; the readers are not in that revision.
8. **Both default name type identifiers.** If names are exported, a Name Type
   carrying `.../name-type` and one carrying `.../topic-name` are different
   Topics and must not be merged into one "default" by the adapter.

## 6. Smallest next integration task

Without any planning domain: a read-only function in HyperDoc that exports the
layer 2 facts of the existing project map, `instance-of` only, each with its
source Association, and a test that the number of exported facts equals the
number of Associations for which `type-instance-relationship` returns players.
That replaces the local type derivation in
`dreyeck/work/project/project-workspace.lisp` by the library reader and needs
only prerequisite 7 and a provisional answer to prerequisite 1.

## 7. Out of scope

Writing plans back into a map, executing operators, a second TMDM model inside
HyperDoc, a user interface, and any change to identity, merging or scope in the
library.
