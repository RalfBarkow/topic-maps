# Reading the First CTM Associations

Slice 3 starts from accepted commit `66664dbff6275d60dab1bc6a232fa70f7b916b8c`.
It adds actual Association and Association Role information items to the
existing same-map identity model. It reads one or two Role declarations.

## The original unary source

The unmodified `ctm/in/association.ctm` contains, without a final newline:

```ctm
assoctype(roletype: topic)
```

Its Document IRI is:

```text
https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/association.ctm
```

Writing that IRI as D, the actual model has:

```text
M : TOPIC-MAP; TOPICS=(T-A T-R T-P); ASSOCIATIONS=(A)
T-A : TOPIC; ITEM-IDENTIFIERS={D#assoctype}; PARENT=M
T-R : TOPIC; ITEM-IDENTIFIERS={D#roletype}; PARENT=M
T-P : TOPIC; ITEM-IDENTIFIERS={D#topic}; PARENT=M
A : ASSOCIATION; TYPE=T-A; ROLES=(R); PARENT=M
R : ASSOCIATION-ROLE; TYPE=T-R; PLAYER=T-P; PARENT=A
T-P.ROLES-PLAYED=(R)  [computed]
```

All three Topics have empty Subject Identifier, Subject Locator and Name sets.
The other Topics' computed roles-played sets are empty. No default-name-type
Topic is created. Braces denote sets, not CTM or canonical syntax.

There are **five items apart from the container: three Topics, one Association
and one Role**. Including the Topic Map, there are six. The Role is an
independent inspectable object. The unchanged CXTM baseline explicitly contains
its `role` element, type/player references and the player's `rolePlayed` link.

## The original binary source

The unmodified `ctm/in/association-binary.ctm`, also without a final newline:

```ctm
assoctype(roletype1: topic1, roletype2 :topic2)
```

Document IRI:

```text
https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/association-binary.ctm
```

The model contains five Topics identified by D plus `#assoctype`, `#roletype1`,
`#topic1`, `#roletype2`, `#topic2`; one Association; and two Roles. The
Association's type is the first Topic. The Role pairs are `(roletype1, topic1)`
and `(roletype2, topic2)`, with the Association as their shared parent. Each
player's roles-played set contains its corresponding Role. All Topic parent
links point to the same map. Including the map, these are nine information
items. Baseline numbering differs from creation order and is not reused as
local object identity.

## Normative interpretation

[CTM ISO/IEC 13250-6:2010](https://www.isotopicmaps.org/ctm/ctm.html) §§3.3.7,
3.3.11 and 3.13 govern Topic references, types and Association/Role creation.
The Role separator needs layout on at least one side of `:`; both source
forms above meet the grammar. Existing comment handling also supplies layout.

[TMDM ISO/IEC 13250-2:2006](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
§§5.2, 5.3.5, 5.7 and 5.8 govern containment, roles played, Associations and
Roles. Topic merges replace Association type, Role type and Role player
references under §6.2. Equal Roles and Associations are normalized under
§§6.7 and 6.6 for the implemented empty/null properties.

Association equality compares type and the unordered structural Role set.
Within one Association, a Role is equal by type/player and its shared parent.
Roles in different unequal Associations do not coalesce just because their
type/player pairs match. Comparing Association Role sets uses those signatures
under the compared parents, avoiding the parent/equality cycle. When equal
Associations merge, the replacement receives one equal Role set, whose parent
references are updated; discarded equivalent Role handles resolve to that set.

## The required late-merge investigation

Construct the Association before merging its participating Topics:

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm")
(defparameter *map*
  (topic-maps.ctm:deserialize-string "a(a: b)"
    :document-iri "https://example.invalid/association-merge.ctm"))
(defparameter *association* (first (topic-maps.tmdm:topic-map-associations *map*)))
(defparameter *role* (first (topic-maps.tmdm:association-roles *association*)))
(defparameter *old-a* (topic-maps.tmdm:association-type *association*))
(defparameter *old-b* (topic-maps.tmdm:association-role-player *role*))
(topic-maps.tmdm:add-topic-identifier *old-a* :subject-identifier "urn:shared")
(defparameter *merged*
  (topic-maps.tmdm:add-topic-identifier *old-b* :subject-identifier "urn:shared"))
(list (eq *merged* (topic-maps.tmdm:association-type *association*))
      (eq *merged* (topic-maps.tmdm:association-role-type *role*))
      (eq *merged* (topic-maps.tmdm:association-role-player *role*)))
;; => (T T T)
(eq *old-a* *merged*) ; => NIL
(eq (topic-maps.tmdm:canonical-topic *old-a*) *merged*) ; => T
(describe *map*)
(describe *association*)
(describe *role*)
(topic-maps.tmdm:topic-roles-played *old-b*) ; => the one live Role
```

Stored live references are rewritten, not repaired only by getters. Tests
inspect the raw fields as well as the public API. Seven affected-reference
combinations, transitive replacements and combined Name/Association references
are checked. Duplicate Role and Association removal has its own retained-handle
tests. Another 128 graph/order variants construct a binary Association first
and then perform all possible four-Topic identity connections.

## Public API and scope

`make-association map type roles` takes a Topic and a nonempty list of
`(role-type player)` Topic pairs. It resolves obsolete Topic handles, checks
that all references belong to the map before mutation, constructs Role items,
normalizes duplicates and returns the live Association. The model operation
accepts a nonempty Role set; the CTM reader is limited to at most two Role
declarations before duplicate removal. Larger CTM arities signal UNSUPPORTED.

Accessors: `topic-map-associations`, `association-parent`, `association-type`,
`association-roles`, `association-role-parent`, `association-role-type`,
`association-role-player`, and computed `topic-roles-played`. Set readers return
copies. `canonical-association` and `canonical-association-role` resolve retained
handles after duplicate merging; use them before inspecting obsolete objects
with DESCRIBE. None of these functions performs CXTM canonicalization.

An Association's unmaterialized scope is implicitly empty. On Associations and
Roles, unmaterialized item identifiers are empty and reifier is null; Roles
have no separate scope property. Scope/reification syntax, larger arities, embedded
Topics, prefix directives, Templates, typed Names, Occurrences, Variants,
cross-map merging and full IRI grammar validation remain outside this slice.
No type-instance or supertype-subtype special Associations are introduced.

## Evidence boundary

Eight unchanged originals are exercised: `association.ctm`,
`association-binary.ctm`, `association-binary-duplicate.ctm`,
`association-type-sid.ctm` and `association-with-comment{,2,3,4}.ctm`.
The property oracle matches Topics by separate identifier sets, Associations
by type and Role signatures, and checks Role parent/player/type and roles-played
links under that mapping. It does not generate or canonicalize XML.

All previous 16 positive records are unchanged. All 24 inspected positive
CXTM-EQUAL contracts remain NOT-RUN; the sole imported PASS remains the specific
undefined-prefix rejection. All 272 other imported contracts stay NOT-RUN.
The pinned corpus targets draft 2010-03-31; property agreement does not establish
full ISO conformity. Consult `slice-3-validation.md` for exact test evidence.
