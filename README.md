# Common Lisp Topic Maps — Slice 19C

Slice 19D0B qualifies local, versioned CXML/closure-common encoding corrections:
**58 original and 88 additional XML checks PASS** in fresh offline SBCL 2.5.4.
The required entry point is `topic-maps.xml:parse-octets` after offline source
patch preparation; it enforces external-resource denial. No XTM deserializer
is implemented. See [encoding qualification](docs/slice-19d0b-cxml-encoding.md).

Slice 19D0 made pinned CXML sources available to ASDF through the Nix source
environment. Its initial parser qualification failed on UTF-16 supplementary
characters and invalid UTF-8; those historical failures are retained. See
[CXML provisioning and qualification](docs/slice-19d0-cxml.md) for exact hashes,
offline loading, external-entity policy, the failing probes and retained regression.

Slice 19C adds `%include` with controlled resources, per-level Topic-II aliases,
immediate-parent Document/Wildcard environments, Counter propagation and
source-preserving Template import. Imported bodies execute in the caller's
identity/Prefix environment while errors preserve definition and invocation
sources. See [Reading CTM Include](docs/reading-ctm-include.md) and
[Slice 19C validation](docs/slice-19c-validation.md).
The registered corpus is **204 PASS, 4 FAIL, 65 NOT-RUN**. All twelve Include
contracts execute: seven byte-equal positives, three intended rejections, two
explicit normative/baseline mismatches. The two earlier DateTime FAILs remain.

Slice 19B adds CTM `%mergemap` with the CTM notation and an explicit
`:resource-resolver` on `deserialize-string` / `deserialize-file`. Resources are
supplied as bytes by the caller, deserialized with independent environments,
and transferred by Slice 19A's TMDM content import. No implicit file/network
retrieval or XTM deserialization is provided (Include is added by Slice 19C).
See [Reading CTM Mergemap](docs/reading-ctm-mergemap.md) and
[Slice 19B validation](docs/slice-19b-validation.md).
The registered corpus now has **194 PASS, 2 known DateTime FAIL, 77 NOT-RUN**:
four new byte-exact positive contracts and three intended negative rejections.

Slice 19A adds `topic-maps.tmdm:import-map-content`: source-preserving copying
of Topics, Associations and their children into a target Map, followed by the
existing same-map identity and structural merging. Both original graphs remain
unchanged on semantic rejection. The returned resolver tracks canonical target
representatives. Source Map identifiers/reifier are excluded.
See [Reading Map Content Import](docs/reading-map-content-import.md) for the API,
object references and inspection forms, and [Slice 19A validation](docs/slice-19a-validation.md)
for fresh offline execution evidence. This adds no CTM import contracts:
**187 PASS, 2 known DateTime FAIL, 84 NOT-RUN** remain unchanged.

A working ANSI Common Lisp reader for CTM identity/name syntax and
Associations with one or more Roles, with same-map merging of Topics, Names, Associations
and Roles, plus string/IRI-valued Occurrences, in a bounded TMDM model. HyperDoc remains a possible future client
and is neither the codebase nor a dependency. Slice 4 adds a pure, independent
CXTM canonicalizer for this model. Controlled Include/Mergemap and Map content import are described above. Slice 5 adds Occurrence items and replacement merging
without expanding Scope, Reification or Variants. Slice 6 adds document-local
prefixes, QName resolution and explicit datatype locators on quoted Occurrence
values. Unknown datatypes retain their lexical values; Date timezone CXTM rules
remain explicitly unsupported. Slice 7 adds integer literals, lexical validation
and pure xsd:integer canonical output; qualified strings retain their stored
lexical values. Slice 8 adds decimal literals, exact character-based xsd:decimal
canonicalization and lexical validation, with the same separation of stored
strings, TMDM equality and canonical serialization. Slice 9 adds timezone-free
xsd:date literals, Gregorian calendar validation and pure CXTM Date output.
Negative-year leap validation follows the documented XSD 1.0 E.1 interpretation.
Slice 10 adds xsd:dateTime with absent/zero zones, exact fractional precision and
midnight rollover. A noncandidate leap-second baseline disagrees with XSD D.1
following-minute interpretation and remains FAIL. Slice 11 adds exact nonzero-offset UTC canonicalization; the original timezone2
contract now executes and reports its known inconsistent baseline as FAIL.
Nonzero-offset BCE day rollover and leap-second contexts remain explicitly
unsupported; existing zero/absent-zone behavior is retained.
Slice 12A adds explicitly typed Topic Names. Slice 13 adds Scope Topic sets to
Names, Occurrences and Associations, including reference replacement, duplicate
merging and canonical output. Slice 14 adds unreified Variants with proper Scope
supersets, canonical merge handles and pure CXTM output. Slice 15 adds per-document
Wildcards and recursive Embedded Topics through the shared Topic reference reader.
Slice 16A adds general Item Identifiers for all seven existing information-item
kinds, including metadata-preserving replacement merges and pure CXTM output.
Slice 16B adds same-map Reification, full merge cascades, atomic semantic
preflight and all six CTM Reifier attachment positions.
Slice 17A removes the two-Role CTM limit, preserving the existing model and
canonicalizer. Slice 17B adds `isa`/`ako` using ordinary Associations and protects
the distinct Core Subjects defined by TMDM 2006 §7. Atomic merge preflight uses
the existing disposable TMDM graph. No inference engine is introduced.

Slice 18 adds grammar-checked Templates, contextual positional arguments,
global/Tail/nested Invocations, invocation-local Wildcards and canonical handles
through existing model operations. Seven explicitly documented grammar contracts
remain open; no extra TMDM item kind or Lisp evaluation is introduced.

Start with [CTM Templates and Invocations](docs/reading-ctm-templates.md) for
representation, diagnostics, open grammar cases and executable inspection forms.
See [Slice 18 validation](docs/slice-18-validation.md) for the full offline run,
57 additional byte-exact original contracts and ten specific rejection contracts.

Start with [isa/ako and Core Subject Consistency](docs/reading-type-relationships.md)
for the exact vocabulary, object relations, normative distinctions and inspection.
See [Slice 17B validation](docs/slice-17b-validation.md) for the complete offline
regression and thirteen new original byte-exact comparisons.

Start with [Associations with Arbitrarily Many Roles](docs/reading-association-arity.md)
for the actual seven-Topic/three-Role example and executable inspection forms.
See [Slice 17A validation](docs/slice-17a-validation.md) for the full offline run
and the single new byte-exact original contract.

Start with [Reification](docs/reading-reification.md) for actual Reifier/Reified
objects, normative clauses, cascade handling and inspection forms.
See [General Item Identifiers](docs/reading-item-identifiers.md) for the
uniform API, retained handles, exact boundaries and executable inspection forms.

Systems: `topic-maps` (the retained foundation), `topic-maps/tests`,
`topic-maps/tmdm`, `topic-maps/ctm`, `topic-maps/ctm/tests` and
`topic-maps/ctm/merging-tests` and `topic-maps/ctm/association-tests`, plus `topic-maps/cxtm` and
`topic-maps/cxtm/tests`, `topic-maps/ctm/occurrence-tests` and `topic-maps/ctm/prefix-tests` and `topic-maps/ctm/integer-tests`, plus `topic-maps/ctm/decimal-tests` and `topic-maps/ctm/date-tests` and `topic-maps/ctm/datetime-tests` and `topic-maps/ctm/timezone-tests`, `topic-maps/ctm/typed-name-tests` and `topic-maps/ctm/scope-tests`, plus `topic-maps/ctm/variant-tests` and `topic-maps/ctm/reference-tests`.
The core reader/model uses ANSI Common Lisp; the foundation/tooling uses
ASDF/UIOP and Python's standard library. No Quicklisp packages are required.
`topic-maps/tmdm/identifier-tests` and `topic-maps/tmdm/reification-tests` add the
general identifier and Reification regression suites.
`topic-maps/ctm/association-arity-tests` adds n-ary syntax, merge/handle checks
and the original `association-duplicate-role.ctm` comparison.
`topic-maps/ctm/type-relationship-tests` adds Core consistency, atomic failure
and isa/ako model/reference-graph checks.

Start with [Reading Topic References](docs/reading-topic-references.md) for Wildcard
IRIs/counters, recursive Embedded Topics and actual object relationships.
[Reading Variants](docs/reading-variants.md) for Parent Name relationships,
explicit/resulting Scope, merge preflight and the four original contracts.
[Reading Scope](docs/reading-scope.md) for Scope APIs, actual Topic
references, merge handles and the three original comparisons.
[Reading Typed Topic Names](docs/reading-typed-topic-names.md) covers Slice 12A.
[Reading DateTime Timezone Canonicalization](docs/reading-datetime-timezones.md)
for UTC conversion, calendar limits, actual stored strings and executable inspection.
[Reading DateTime Occurrences](docs/reading-datetime-occurrences.md)
for lexical/value/canonical distinctions and the two normative discrepancies.
[Reading Date Occurrences](docs/reading-date-occurrences.md)
for the ten original Date cases, calendar rules, stored values and inspection.
[Reading Decimal Occurrences](docs/reading-decimal-occurrences.md)
for the seven Decimal cases, string representation, equality and inspection.
[Reading Integer Occurrences](docs/reading-integer-occurrences.md)
for integer representation, lexical equality, canonicalization and inspection.
[Reading Prefixes and Explicit Datatypes](docs/reading-prefixes-and-datatypes.md)
for the seven original cases, current API, object properties and diagnostics.
[Reading the First Four CTM Occurrences](docs/reading-first-occurrences.md)
for actual parent/type references, literal values, datatypes and executable inspection.
[Reading Canonical Topic Maps](docs/reading-canonical-topic-maps.md)
for the CXTM API, normative clauses, base-locator policy and actual byte comparisons.
[Reading the First CTM Associations](docs/reading-first-ctm-associations.md)
for actual Association/Role items, late Topic merges and current subset boundaries.
[Reading Topic Identity and Merging](docs/reading-topic-merging.md)
for the current API, reference replacement, identifier tails and exact subset
boundaries. See [Reading the First Five CTM Documents](docs/reading-first-five-ctm-documents.md)
for original sources, actual objects, normative clauses, baseline evidence and
copy-pasteable DESCRIBE forms. [API and boundaries](docs/slice-1-api-and-boundaries.md)
document the accepted Slice 1 baseline; the Slice 2 document supersedes its
statements about absent identity tails, merging and immutable Name references.
The Slice 3 document supersedes historical statements about absent Associations/Roles.

The pinned suite targets the **CTM draft dated 2010-03-31**. Passing it alone
does not establish full ISO/IEC 13250-6:2010 conformity.

## Load and inspect

In a new Common Lisp process, with this checkout selected:

```lisp
(require :asdf)
(asdf:initialize-source-registry
 '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps")
(defparameter *corpus* (topic-maps.test-foundation:discover-corpus))
(topic-maps.test-foundation:summarize-corpus *corpus*)
(topic-maps.test-foundation:select-cases *corpus* :category :invalid)
(topic-maps.test-foundation:select-cases *corpus* :id "ctm/in/simple.ctm")
(asdf:test-system "topic-maps/tests")
(asdf:test-system "topic-maps/ctm/tests")
(asdf:test-system "topic-maps/ctm/merging-tests")
(asdf:test-system "topic-maps/ctm/association-tests")
(asdf:test-system "topic-maps/ctm/decimal-tests") ; includes retained Integer/Prefix/Occurrence/CXTM suites
(topic-maps.test-foundation:write-validation-report
 *corpus* #p"/tmp/topic-maps-inventory.json")
```

Change only the checkout pathname when using another machine. The case's
Document IRI remains independent of that pathname. Records are inspectable
Common Lisp structures, with actual source/baseline pathnames and explicit
contracts, results, statuses, diagnostics and reviewed clauses.

## Offline verification

```sh
# SBCL must already be installed. No network is used by this command.
TOPIC_MAPS_REPORT=/tmp/topic-maps-validation.json ./scripts/test.sh
```

Set `SBCL=/absolute/path/to/sbcl` if needed. The launcher starts a new process,
ignores system/user initialization, clears inherited ASDF source configuration
and writes FASLs outside the repository. It runs byte-integrity fixtures,
Common Lisp infrastructure checks and an independent JSON-schema/content check
when a report pathname is supplied. `nix develop path:.` supplies a minimal,
pinned SBCL/Python/Git environment; initial environment provisioning may need
network access, while test execution after provisioning does not.

The complete upstream corpus is already vendored, unchanged. If absent in a
source distribution, acquire it once:

```sh
python3 scripts/corpus.py acquire
python3 scripts/corpus.py verify
```

Acquisition uses the exact commit and archive digest in
[corpus-lock.json](references/corpus-lock.json), refuses to merge over existing
contents and verifies every file. Verification is offline. Valid CTM inputs
are selected only under `ctm/in`, invalid ones only under `ctm/invalid`, and
CXTM baselines only under `ctm/baseline`. Auxiliary files are reported separately.

## Current validation and historical foundation

The complete pinned corpus remains unchanged: 231 valid CTM inputs, 42 invalid
inputs, 231 CXTM baselines and 22 CTM auxiliary files. One hundred sixty-five selected positive
cases pass actual CXTM byte comparisons. Twenty-two specific rejection contracts pass.
Two executed DateTime contracts remain FAIL because of documented normative
baseline discrepancies; 84 contracts remain NOT-RUN. A green regression run
preserves those two FAILs and never changes an upstream baseline. Unsupported
constructs and I/O errors cannot count as the required CTM rejection.

The full launcher runs the retained 54 foundation checks, two Python integrity
fixtures, 123 retained identity checks, 646 merge checks, 657 Association checks,
imported-report validation and selected baseline
property evidence, 445 retained CXTM checks, 1,101 Occurrence checks, 150 prefix/datatype checks, 665 integer checks, 715 Decimal checks, 1,806 Date checks, 217 DateTime checks, 1,944 timezone checks, 106 typed-name checks, 293 Scope checks, 324 Variant checks and 238 Topic Reference checks, plus
244 general Item Identifier checks, 236 Reification checks, 337 n-ary Association
checks, 1,016 Core Subject/type-relationship checks, 297 Template checks and 16,294 independent Unicode NFC oracle
comparisons. The oracle needs Python UCD 15.0 or 15.1 (tables use UCD 15.1.0).
A report path also produces `<path>.semantics.json` with
separate model observations, plus `<path>.merging.json`, `<path>.associations.json`
and `<path>.cxtm.json` (complete actual/expected XML and byte counts),
plus `<path>.occurrences.json` with separate actual Occurrence objects/properties
and `<path>.prefixes.json` with all seven selected observations, plus `<path>.integers.json` for integer objects
and independently checked arithmetic probes, plus `<path>.decimals.json` with
seven Decimal object observations and 157 independent Decimal arithmetic probes,
plus `<path>.dates.json` with five original Date results, five original rejections,
396 independent date/calendar probes and 15 century decisions. `<path>.datetimes.json` records five actual DateTime
models, 45 independent lexical/canonical probes and two executed baseline
discrepancies. `<path>.timezones.json` adds exact UTC, fraction and model-purity
probes, including every one of the 1681 permitted signed offset minutes.
The merge checks include 128 graph/order variants with an independent reachability
oracle. Earlier slices recorded version/relocation comparisons; Slice 17A uses
the existing single-runtime environment. `<path>.typed-names.json` records Name value/Parent/Type relations;
`<path>.scopes.json` records Scope object relations and an ordering witness.
`<path>.variants.json` records Variant/Parent/Scope observations and XML ordering.
`<path>.references.json` records the new source/counter/model observations.
`<path>.identifiers.json` and `<path>.reification.json` retain their model evidence;
`<path>.arity.json` adds actual Role references and twelve canonical XML witnesses.
`<path>.relationships.json` records the thirteen original reference graphs and
atomic Core Subject conflict observations.
`<path>.templates.json` records the 57 model observations and ten specific
rejections, including original positions and invocation contexts.
See [Slice 19B validation](docs/slice-19b-validation.md) for current evidence.
[Slice 12A validation](docs/slice-12a-validation.md) records explicit Name types.
[Slice 11 validation](docs/slice-11-validation.md) preserves the prior timezone evidence.
[Slice 10 validation](docs/slice-10-validation.md) preserves the earlier DateTime baseline.
[Slice 9 validation](docs/slice-9-validation.md) records the accepted Date subset.
[Slice 8 validation](docs/slice-8-validation.md) records the accepted Decimal subset.
[Slice 7 validation](docs/slice-7-validation.md) records the accepted Integer subset.
[Slice 6 validation](docs/slice-6-validation.md) records the preceding accepted subset.
[Slice 5 validation](docs/slice-5-validation.md) records the preceding accepted subset.
[Slice 4 validation](docs/slice-4-validation.md) records the accepted baseline.
[Slice 3 validation](docs/slice-3-validation.md),
[imported contracts](reports/slice-1/validation.json) and
[semantic observations](reports/slice-1/semantics.json).

[Slice 0 inventory](docs/inventory.md), [architecture](docs/architecture.md),
[coverage](docs/coverage.md) and [validation](docs/validation.md) remain historical
foundation records. Their original report/logs are preserved. Their statements
about absent reader/model systems describe Slice 0, not the current branch.
Slice 1 is built from `9c83db34eb1ba8091b004433f088056717dbaa7e` on
`codex/ctm-slice-1`. Slice 2 starts from the accepted Slice 1a commit
`fb60afd548d679d83fd8ec76bc5ff384c1e23e5f` on `codex/ctm-slice-2`.
Slice 13 starts from `788899aea1a20b9cd8237c6106e6613e180d7362` on
`codex/ctm-slice-13`.
Slice 14 starts from `aeb017e4f4846f2e6a701e581d20eef84a8b83d9` on
`codex/ctm-slice-14`.
Slice 11 starts from `8741d155d948c7317945eee423a977940cad995e` on
`codex/ctm-slice-11`.
Slice 10 starts from `2ad41cd1a945a4ce97824464de40646bb899259e` on
`codex/ctm-slice-10`.
Slice 9 starts from `195d5f5444d776096b765d04c815c23c3db5f84c` on
`codex/ctm-slice-9`.
Slice 8 starts from `17dd58775e25ab495e3c83deb4b5a36f5e5a124b` on
`codex/ctm-slice-8`.
Slice 7 starts from `3924d1eac5a070fe5a6a26683e23ac338793f544` on
`codex/ctm-slice-7`.
Slice 6 starts from `437ad53ea7539d36db3fa871d0931650b7a6a03e` on
`codex/ctm-slice-6`.
Slice 5 starts from `8036a2b1ce009218f33d300edcc5f715ec1d1124` on
`codex/ctm-slice-5`.
Slice 4 starts from `35648c4dcc71e8dc6448b64abcacb438e53d64a2` on
`codex/ctm-slice-4`.
Slice 3 starts from accepted `66664dbff6275d60dab1bc6a232fa70f7b916b8c` on
`codex/ctm-slice-3`. Await review before continuing to the next slice.

Slice 15 starts from `4f7b4d26d40f8f5566594aa2e3ad6296d44fc4c3` on `codex/ctm-slice-15`.
