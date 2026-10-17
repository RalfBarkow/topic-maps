# Slice 13 validation — Scope

Implemented on `codex/ctm-slice-13`, parent
`788899aea1a20b9cd8237c6106e6613e180d7362`. The initial checkout was clean on
`codex/ctm-slice-12a`, tree `ecfec2c84faa95352ea3ad012cec5a2bc72fa98f`.
The pinned corpus is unchanged at `cd165b150176c1d6842b37be9cc9051b40d4996b`.
No HyperDoc source or runtime was changed.

## Current evidence

`reports/slice-13/execution.json` records UTC start/finish, exact execution
command, runtime, source hashes, unchanged protected files, imported status
transitions and artifact hashes. It represents the current local execution,
not merely a historical PASS. `tests.log` retains the actual output;
`describe.log` records execution of the reading document's inspection forms.

One fresh SBCL 2.5.4 process ran the complete retained suite, offline under
`(deny network*)`, followed by independent Python report/model/CXTM checks.
A separate fresh offline process executed the documented inspection example.
No additional SBCL version, checkout relocation or cache-management work was used.
The existing fresh-process launcher and its unchanged output translations were reused.

| Regression family | Passed checks |
| --- | ---: |
| Foundation | 54 |
| Topic Identity | 123 |
| Topic Merging | 646 |
| Associations / Roles | 657 |
| Initial CXTM | 445 |
| Occurrences | 1,101 |
| Prefixes / explicit datatypes | 150 |
| Integers | 665 |
| Decimals | 715 |
| Dates | 1,806 |
| DateTimes | 217 |
| Timezone canonicalization | 1,944 |
| Explicitly typed Names | 106 |
| Scope | 293 |
| **Total Lisp checks** | **8,922** |

Zero assertion failures. Two Python infrastructure fixtures and 16,294
independent NFC comparisons also pass. Independent validators pass for all
retained report families and the new Scope model/ordering witness.

Historical assertions that Scope syntax was unsupported were adapted explicitly:
valid scoped Name/Occurrence/Association inputs now assert actual deserialization;
Scope directly on a bare Topic asserts CTM rejection. The previous check totals
are retained, and other excluded constructs still assert unsupported conditions.

## Original contracts

| Original source | Expected bytes = actual bytes | Result |
| --- | ---: | --- |
| `ctm/in/name-scope.ctm` | 615 | PASS |
| `ctm/in/occurrence-scope.ctm` | 646 | PASS |
| `ctm/in/association-scope.ctm` | 794 | PASS |

Only these three imported records transition from NOT-RUN to PASS.
All 58 previously executed CXTM records retain byte-identical actual/expected
outputs and outcomes. Those records comprise 56 matches and two known mismatches.
The independent check now verifies 59 matches and two documented DateTime
mismatches against original baselines. All eight prior negative CTM contracts pass.

Imported totals: **67 PASS, 2 FAIL, 0 UNSUPPORTED, 204 NOT-RUN**.
The two FAILs remain `occurrence-datetime2.ctm` and
`occurrence-datetime-timezone2.ctm`. No baseline was rewritten and no semantic
assertion was substituted for a CXTM comparison. Other Scope-related imported
contracts involving Embedded Topics, Templates, Variants or Reification remain
NOT-RUN; local unsupported probes do not promote their status.

`scopes.json` records actual source strings, Document IRIs, Topic identifier sets,
item properties and object-reference ordinals. Lisp assertions separately verify
EQ identity, Parent/Type/Player links and current raw Scope references.
`scripts/check-scopes.py` independently resolves those ordinals to identifier sets
and compares the relationships with the original XML. It also checks a separate
ordering witness without invoking the Lisp comparators as its oracle.

## Merge, boundary and mutation controls

- Empty, single-theme and multiple-theme Scopes; duplicate and reordered inputs.
- Different Scope sets keep otherwise equal items distinct.
- Theme merging reduces `{A,B}` to `{C}` and `{A,B,Z}` to `{C,Z}` for each item kind.
  Equal items then merge, and retained Name/Occurrence/Association/Role handles
  resolve to the current representatives. Distinct remaining Scopes stay distinct.
- All six orders of transitive merging of three themes leave one canonical
  Theme reference per Scope. Both directions of the two-theme merge are tested.
- Parent, Type, Role Type and Player may alias a Theme and remain current when
  that Theme merges. Binary Associations also retain their Roles/Scope.
- Occurrence duplicate merging unions Item Identifiers in their own category.
  Reusing an identifier with an unequal Scope is refused before mutation.
- Invalid finite/improper/circular lists, non-Topics and foreign-map Themes are
  refused without model changes. Invalid default-Name Scope creates no type Topic.
  Both caller-owned input lists and returned lists are detached from stored sets.
- Reader tests cover identifiers, QName/IRI references, Subject Locators and
  explicit Item Identifiers, comments, Unicode, adjacent `@`, numeric/date/string
  boundaries, and quoted explicit datatypes. Full Scope is known before creating
  the Name/Occurrence/Association and performing duplicate normalization.
- Specific diagnostics include missing themes, trailing/doubled commas, invalid
  Theme tokens, undefined prefixes and misplaced Scope, with offset/line/column.
  Excluded features still signal unsupported conditions.
- Twenty-four item-construction permutations produce identical CXTM. Scope-set
  cardinality and member ordering, all Topic references and RolePlayed references
  are checked. Serialization preserves both live model state and retained handles.
- Corrupt internal Scope references (retired, foreign or duplicate Themes) are
  explicitly rejected by the canonicalizer without normalizing the input.

Normative clauses, actual item relationships, API and executable inspection are
in [Reading Scope](reading-scope.md). No full CTM/TMDM conformity is claimed.

## Reproduction

From the repository, using the existing installed development SBCL:

```sh
PYTHONDONTWRITEBYTECODE=1 SBCL=/path/to/sbcl \
  TOPIC_MAPS_REPORT=/tmp/topic-maps-slice-13.json \
  sandbox-exec -p '(version 1)(allow default)(deny network*)' ./scripts/test.sh
```

To reproduce this slice's evidence and the documentation inspection:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-13.py \
  --sbcl /path/to/sbcl --output /tmp/topic-maps-slice-13-evidence
```

This command records a new execution in the selected output directory; it does
not import anything or change corpus baselines. Exact runtime and commands for
the delivered run are recorded in `reports/slice-13/execution.json`.

Scope support is complete only for the agreed identity-reference subset.
Embedded Topics, wildcards, Variants, Templates, Reification and cross-document
merging remain outside this slice. The HyperDoc Work-Topic representation question
remains separate. No next slice, server, push or deployment was started.
