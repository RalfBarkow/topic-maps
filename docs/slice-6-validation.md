# Slice 6 — Validation and acceptance evidence

Base commit: `437ad53ea7539d36db3fa871d0931650b7a6a03e`.
Observed initial branch: `codex/ctm-slice-5`; HEAD matched the base and
`git status --short --branch` contained no changed/untracked files. Created
`codex/ctm-slice-6` at that commit. The corpus remains pinned at
`cd165b150176c1d6842b37be9cc9051b40d4996b`; all corpus/reference bytes are unchanged.

## Scope and normative basis

[CTM](https://www.isotopicmaps.org/ctm/ctm.html) §§3.2, 3.3.3–3.3.5, 3.4.1–3.4.2,
3.10, 3.16.1; [TMDM](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
§§4.3–4.4, 5.6, 6.5; [CXTM](https://www.isotopicmaps.org/cxtm/cxtm.html)
§§3.8, 3.14, 3.16, 3.18–3.20, 4.2–4.5, 4.9.
The detailed interpretation, original source texts, expected/actual objects,
public API and an executed DESCRIBE example appear in
`reading-prefixes-and-datatypes.md`. The published standards were consulted
before implementation; no conflict with the selected draft-era cases was found.
This remains a bounded implementation, not a claim of complete ISO conformance.

The parser owns its prefix environment; bindings are processed in source order,
with exact locator comparison on rebinding. QName identity and literal locator
contexts share resolution but only identity contexts intern Topics. Quoted
Occurrence qualifiers retain the escape-decoded string and resolved datatype
locator. No datatype Topic is synthesized. The ordinary TMDM model is retained.

CXTM now permits arbitrary datatype locators under §3.16's Other rule, retaining
existing escaping/NFC, datatype ordering and non-base-stripped datatype output.
The four special integer/decimal/date/dateTime canonicalizations remain explicit
CXTM-UNSUPPORTED cases. There are no filename-dependent serialization rules.
Canonicalization does not mutate maps or retained replacement-object handles.

## Original contracts and local observations

Each source is deserialized from `vendor/cxtm` with the Slice 0 deterministic
Document IRI, also used as CXTM Base Locator. Binary output is compared directly
with the unchanged original binary baseline; neither side is preprocessed.

| Original file | Actual relevant properties | Contract/result |
| --- | --- | --- |
| `ctm/in/occurrence-explicit-datatype.ctm` | Two Topics (local topic/occtype); one Occurrence, Parent EQ topic, Type EQ occtype, Value `Occurrence`, Datatype `http://www.w3.org/2001/XMLSchema#string` | CXTM-EQUAL PASS; 359 bytes |
| `ctm/in/occurrence-datatype-unknown.ctm` | Two Topics (local topic/occtype); one Occurrence, Parent EQ topic, Type EQ occtype, Value `BOGUS`, Datatype `http://example.com/bogus` | CXTM-EQUAL PASS; 339 bytes |
| `ctm/in/prefix-duplicate.ctm` | One Topic, SI `http://psi.example.org/fake`, no II/SL | CXTM-EQUAL PASS; 141 bytes |
| `ctm/in/prefix-duplicate2.ctm` | Two Topics, SIs `http://psi.example.org/fake`, `http://psi.example.org/fake2`, no II/SL | CXTM-EQUAL PASS; 260 bytes |
| `ctm/in/prefix-multiline.ctm` | One Topic, SI `http://psi.example.org/fake`, no II/SL | CXTM-EQUAL PASS; 141 bytes |
| `ctm/invalid/prefix-collision.ctm` | PREFIX-COLLISION subclass of CTM-REJECTION, code :PREFIX-COLLISION, offset 43, line 2, column 9 | CTM-REJECTION PASS |
| `ctm/invalid/prefix-undefined2.ctm` | UNDEFINED-PREFIX subclass of CTM-REJECTION, code :UNDEFINED-PREFIX, offset 136, line 6, column 15 | CTM-REJECTION PASS |

All five positive maps have no Names/Associations; Occurrence identifier sets are
empty. The first two maps use only the absolute local Item Identifiers
`DocumentIRI#topic` and `DocumentIRI#occtype`, with no SI/SL. Datatypes are locator
strings, never extra Topics. Canonical Topics are type=1/owner=2 in the first
two cases and fake=1/fake2=2 in prefix-only cases. Relative baseline locators
follow the existing CXTM §3.18 base policy; datatype locators remain full IRIs.

| Imported status | PASS | FAIL | UNSUPPORTED | NOT-RUN |
| --- | ---: | ---: | ---: | ---: |
| All 273 cases | 36 | 0 | 0 | 237 |
| Positive CXTM contracts (231) | 33 | 0 | 0 | 198 |
| Negative CTM contracts (42) | 3 | 0 | 0 | 39 |

Only these seven new contracts changed status: all NOT-RUN → PASS. The old
`prefix-undefined.ctm` remains PASS. No unexecuted imported contract is inferred
to pass or to be unsupported from semantic tests. `reports/slice-6/cxtm.json`
contains all 33 executed IDs, full actual/expected XML and byte counts;
`reports/slice-6/actual/` contains their actual octets. All preceding 28 case
records and canonical outputs match Slice 5 exactly. The prior five identity,
11 merge, eight Association and four Occurrence object-observation records are
also unchanged; these separate semantic records do not assert CXTM equality.

## Fresh-process, network-denied regression results

All entries below were executed again for this slice. Each SBCL process starts
without user/system initialization and without inherited ASDF registry settings.
`/usr/bin/sandbox-exec` denies network operations. The 2.4.10 run uses a copied
checkout under a new `/private/tmp/ctm-slice-6-validation-.../checkout` directory.

| Suite | SBCL 2.5.4 | SBCL 2.4.10, relocated |
| --- | ---: | ---: |
| Foundation | 54 PASS | 54 PASS |
| Retained identity | 123 PASS | 123 PASS |
| Retained merging | 646 PASS | 646 PASS |
| Retained Associations/Roles | 657 PASS | 657 PASS |
| Retained CXTM checks | 445 PASS | 445 PASS |
| Retained Occurrences | 1,101 PASS | 1,101 PASS |
| Prefix/explicit datatype checks | 150 PASS | 150 PASS |
| Total Lisp checks | 3,176 PASS / 0 FAIL | 3,176 PASS / 0 FAIL |
| Python integrity tests | 2 PASS | 2 PASS |
| Independent NFC oracle comparisons | 16,294 PASS | 16,294 PASS |
| Byte-exact original CXTM contracts | 33 PASS | 33 PASS |

The 150 new checks cover order/scope/rebinding, case/Unicode/numeric QName local
parts, all three Topic identity categories, Association/Role references, datatype
versus Type identity, arbitrary datatype lexical preservation, explicit/default
string equality, duplication, Parent/Type merge replacement, stored references,
construction-order independence, canonicalizer purity and specific errors/positions.
Ad hoc integer/decimal/date/dateTime canonicalization checks verify explicit
unsupported outcomes; these do not change imported corpus statuses.

Obsolete expectations were adapted one-for-one: the identity exclusion fixture
now checks `%include` rather than supported `%prefix`; the Occurrence explicit
xsd:string diagnostic becomes a successful datatype assertion; the API invalid
fixture now checks a relative datatype locator rather than forbidding integer
storage. Their suite totals remain 123 and 1,101. The original 445 canonical
check labels/results are retained unchanged.

All seven report pairs (main, semantics, merging, Associations, CXTM, Occurrences,
prefixes) are byte-identical between runtimes/locations. Independent Python
checks verify original CTM source bytes, actual object-reference ordinals,
datatypes/values, negative positions, UTF-8 baseline equality, XML canonical form
and reference integrity. The public inspection example was separately executed
under network denial and passed. There were no compiler warnings/test failures
in either final run. The inherited NFC compiler note is harmless unreachable-code
elimination, not a warning.

`reports/slice-6/execution.json` records exact commands, runtime paths, exit codes,
totals, qualification and SHA-256 of every evidence artifact. The two complete
raw test logs and `describe.log` are included. The final runs supersede development
runs used to correct fixture parentheses/offsets; no failed final run is hidden
or counted as passing.

## Reproduction

From any working directory, using the installed runtimes on this host:

```sh
python3 /Users/rgb/workspace/topic-maps/scripts/validate-slice-6.py \
  --sbcl-254 /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --sbcl-2410 /nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl \
  --output /private/tmp/topic-maps-slice-6-reproduction
```

The script checks runtime versions, runs both complete suites offline, relocates
the second checkout, compares all reports and retained observations, executes
the documented inspection and writes logs/evidence to the given output. It
provisions no software and does not commit or alter the corpus. Python needs
UCD 15.0/15.1 for the inherited oracle; observed Python was 3.13.2, UCD 15.1.0.
macOS `sandbox-exec` is required for this network-denial workflow.

For one fresh offline run, the exact test invocation shape is:

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /usr/bin/env PYTHONDONTWRITEBYTECODE=1 \
  SBCL=/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  TOPIC_MAPS_REPORT=/private/tmp/topic-maps-slice-6.json \
  /Users/rgb/workspace/topic-maps/scripts/test.sh
```

## Changed implementation locations and limits

- `src/ctm/lexer.lisp:115`: QName local-part grammar; `:128`: prefix terminal.
- `src/ctm/reader.lisp:3`: parser-local environment; `:14`: QName resolution;
  `:25`: directives/rebinding; `:109`: qualified values; `:245`: top-level dispatch.
- `src/ctm/conditions.lisp:19`, `src/ctm/package.lisp`: exported PREFIX-COLLISION.
- `src/tmdm/occurrences.lisp:55`: absolute datatype locators without whitelisting.
- `src/cxtm/canonicalizer.lisp:121`: datatype validation and explicit special-rule
  exclusions; existing value/ordering/serialization paths implement Other.
- `tests/ctm-prefixes.lisp:10`, `:95`, `:149`, `:193`: original contracts, semantic,
  datatype, and merge/order tests; `scripts/check-prefixes.py`: independent checker.
- `topic-maps.asd`, `scripts/fresh-sbcl.lisp`, `scripts/test.sh`, report checkers:
  new test system and accurate 33-positive/3-negative reporting.
- `scripts/validate-slice-6.py`: reproducible dual-runtime/relocation evidence.

Remaining scope limits are not test failures: special numeric/date canonicalization,
nonempty Scope, Reification, Variants, Templates, include/mergemap/cross-document
merging, typed Names, triple-quoted strings and HyperDoc integration. Datatype
value spaces are not generally validated/interpreted. Model locator arguments
must be validated/resolved by the caller; the inherited scheme predicate is not
a complete RFC 3987 validator. Unicode bounds/ambiguous normalized Topic-key
rejection and the documented root-LF interpretation remain unchanged.
No selected case depends on an excluded feature. No server/deployment was used.

Acceptance recommendation: **PASS for Slice 6's selected subset**. Stop and
await review; Slice 7 is not started.
