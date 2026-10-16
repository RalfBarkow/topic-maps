# Slice 8 — Decimal Occurrences: validation evidence

Repository `/Users/rgb/workspace/topic-maps`. Verified initial branch
`codex/ctm-slice-7`, HEAD `17dd58775e25ab495e3c83deb4b5a36f5e5a124b`, clean
working tree and index. Created `codex/ctm-slice-8` from that commit.
Corpus pin remains `cd165b150176c1d6842b37be9cc9051b40d4996b`. Original inputs,
baselines and reference files are unchanged.

## Normative contract

The rules were recorded before implementation in
[Reading Decimal Occurrences](reading-decimal-occurrences.md):
CTM §3.4.1 (productions 28–34), TMDM §§4.3–4.4, 5.6, 6.5,
CXTM §§3.8, 3.14, 3.16, 4.2–4.3, 4.9, and XML Schema Part 2
§§3.2.3–3.2.3.2, 4.3.6. Sources are linked there.

The existing TMDM model remains the only model. Decimal values are strings;
the exact Datatype Locator is `http://www.w3.org/2001/XMLSchema#decimal`.
The reader's existing bare-number policy uses canonical value strings;
this is explicitly a local representation policy, not a new normative mandate.
Qualified strings and direct model insertions retain their valid lexical strings.
TMDM equality stays lexical and datatype-sensitive. CXTM canonicalizes the
output without rewriting or merging the input, and sorts the stored strings
rather than numeric values or formatted XML. All new core operations use
character sequences; no binary floating point or precision-dependent arithmetic
is used. Unknown datatype treatment stays unchanged.

## Seven original end-to-end results

Each original creates one Topic Map, two Topics and one Occurrence, with the
stored Parent EQ `topic` and Type EQ `occtype`; datatype is a locator, not a Topic.
Local Item Identifiers are absolute DocumentIRI fragments. SI/SL, Names,
Associations and Occurrence Item Identifiers are empty. The existing absolute
Document-IRI/Base-Locator policy is retained. CXTM numbers Type=1, Parent=2,
Occurrence=1. All comparisons below use original UTF-8 bytes directly.

| File under `ctm/in/` | Stored string | CXTM bytes | Result |
| --- | --- | ---: | --- |
| occurrence-decimal.ctm | `"9.3"` | 353 | PASS |
| occurrence-decimal-dot.ctm | `"0.3"` | 353 | PASS |
| occurrence-decimal-dot-neg.ctm | `"-0.3"` | 354 | PASS |
| occurrence-decimal-leading-zeros.ctm | `"0.3"` | 353 | PASS |
| occurrence-decimal-minus-sign.ctm | `"-9.3"` | 354 | PASS |
| occurrence-decimal-plus-sign.ctm | `"9.3"` | 353 | PASS |
| occurrence-decimal-1.0.ctm | `"1.0"` | 353 | PASS |

The 39 preceding positive sources, model observations and actual canonical
outputs are unchanged. All three specific negative prefix results remain PASS.
Only the seven selected positive imported contracts change NOT-RUN → PASS.

| Imported contracts | PASS | FAIL | UNSUPPORTED | NOT-RUN |
| --- | ---: | ---: | ---: | ---: |
| All 273 | 49 | 0 | 0 | 224 |
| Positive CXTM contracts | 46 | 0 | 0 | 185 |
| Negative CTM contracts | 3 | 0 | 0 | 39 |

Unselected inputs are not counted as passing just because their syntax may
now happen to be accepted. Semantic assertions and actual byte comparisons
remain separate evidence.

## Full fresh offline regressions

Both runs disable system/user initialization and inherited ASDF configuration.
OS `sandbox-exec` denies network access. SBCL 2.4.10 runs from a separately
copied checkout under `/private/tmp`; its document IRIs do not depend on location.

| Suite | SBCL 2.5.4 | SBCL 2.4.10, relocated |
| --- | ---: | ---: |
| Foundation | 54 | 54 |
| Topic Identity | 123 | 123 |
| Topic Merging | 646 | 646 |
| Associations / Roles | 657 | 657 |
| Retained CXTM | 445 | 445 |
| Occurrences | 1,101 | 1,101 |
| Prefix / explicit datatypes | 150 | 150 |
| Integers | 665 | 665 |
| Decimals | 715 | 715 |
| **Total Lisp checks** | **4,556** | **4,556** |
| Python infrastructure tests | 2 | 2 |
| Independent Unicode NFC oracle | 16,294 | 16,294 |
| Independent Integer arithmetic oracle | 143 | 143 |
| Independent Decimal arithmetic oracle | 157 | 157 |
| Original positive CXTM byte comparisons | 46 | 46 |
| Failures | **0** | **0** |

All **nine report pairs are byte-identical** across runtime versions and checkout
relocation. The combined CXTM report's 3,076 checks comprise retained CXTM,
Occurrence, prefix, Integer and Decimal checks; they are not an additional suite.
The exact public Lisp inspection example was executed successfully offline.

The 715 Decimal checks cover sign/zero rules, integer/fractional components,
long values (10,000-digit components and tiny fractions), CTM boundaries
`1.0.`, `.3.`, `9.3.` and retained `1.`, XML-whitespace handling, errors and
source positions, datatype-only distinctions, lexical duplicate removal,
Parent/Type merging, identifier union, canonical reference slots, retained
Occurrence handles, all representative construction permutations and purity.
Python's independent Decimal arithmetic normalizes with explicitly sufficient
precision, never binary floats or an implicitly rounded context.

Old exclusions were adapted one-for-one: two formerly unsupported Decimal
syntax fixtures now exercise Date and `*`; the private unsupported-datatype
fixture now uses Date; explicit Decimal canonicalization is now expected to
succeed, and four formerly unsupported Decimal literals now assert their datatype.
Existing suite totals and original-case observations remain unchanged. No tests
are deleted, and no upstream input/baseline is changed. Initial development
compilation corrections precede these final successful runs.

## Reproduction and retained evidence

```sh
python3 /Users/rgb/workspace/topic-maps/scripts/validate-slice-8.py \
  --sbcl-254 /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --sbcl-2410 /nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl \
  --output /private/tmp/topic-maps-slice-8-reproduction
```

The actual validation used `--output reports/slice-8`. The script runs both
fresh offline suites, relocates the second checkout, compares all reports,
checks retained Slice-7 cases/outputs, checks original baseline bytes, executes
the documented example and records exact commands, versions, exit codes and
artifact hashes in `reports/slice-8/execution.json`. It provisions no software,
changes no source corpus, starts no server and makes no commit. It requires
already installed runtimes, macOS `sandbox-exec`, and Python UCD 15.0/15.1.

A single full fresh run:

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /usr/bin/env PYTHONDONTWRITEBYTECODE=1 \
  SBCL=/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  TOPIC_MAPS_REPORT=/private/tmp/topic-maps-slice-8.json \
  /Users/rgb/workspace/topic-maps/scripts/test.sh
```

`reports/slice-8/` retains raw logs, nine reports, all 46 actual CXTM byte files,
DESCRIBE output and the execution manifest. `decimals.json` includes unmodified
sources, absolute Document IRIs, actual model properties/reference ordinals and
157 probes. Full remaining limits and copy-pasteable inspection are in the
reading document. No selected normative/corpus conflict was found.

Date, DateTime, CTM `*` semantics, nonempty Scope, Reification, Variants,
Templates, cross-document merging and HyperDoc integration remain outside scope.
Only the exact xsd:decimal datatype receives these rules. No Slice 9 is begun.
