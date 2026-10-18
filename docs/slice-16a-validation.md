# Slice 16A — General Item Identifiers: validation

Base: `8c13acc6e96ced1b14d8ec733f701ac788911720`; local branch
`codex/ctm-slice-16a`. The source hashes in `reports/slice-16a/execution.json`
identify the actual implementation, tests and documentation used by the run.

## Reproduce

From the repository root, using the existing development SBCL:

```sh
python3 scripts/validate-slice-16a.py --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

The validator executes `scripts/test.sh` in a fresh SBCL 2.5.4 process, with no
user initialization or user ASDF registry, under an OS sandbox denying network
access. It retains every existing suite and independent report checker, adds
the Item Identifier suite and independent XML checker, then executes the
documented inspection example in a second isolated process. No version switching,
checkout relocation, FASL-cache changes or HyperDoc loading are part of this slice.

`execution.json` records exact commands, UTC execution interval, individual
suite totals, total Lisp checks, source/artifact SHA-256 values and exit status.
`tests.log` retains the complete output. `identifiers.json` contains individual
check labels and seven manual model/baseline observations. `manual-model-actual/`
contains their actual CXTM bytes. `describe.log` is the inspection output.

The recorded SBCL 2.5.4 run passes **9,728 Lisp checks**, comprising the retained
9,484 checks and 244 new Item Identifier checks, with zero assertion failures.
The Python unit tests, 16,294 NFC oracle comparisons and all independent report
checkers pass. The two known imported DateTime baseline FAILs remain separate.

## Acceptance evidence

- Empty and nonempty sets for all seven kinds; idempotence; copied input/output
  strings and list storage.
- Every directed cross-kind collision, distinct non-Topic items of the same
  kind, legacy constructor routes, and unchanged model snapshots on rejection.
- Topic identity merging; Name/Variant/Occurrence/Association/Role identifier
  unions; old handles used again after replacement; stored Parent/Type/Player
  references and Scope invariants.
- Role-type and Theme merges, Association merging with Role metadata, existing
  equal Names, and atomic rejection of identifier-induced Variant Scope collapse.
- Identifier insertion order and object construction order independence; pure
  serialization, including retained forward links; no use of CXTM NFC output
  for TMDM identifier equality.
- Seven hand-built TMDM models match the unchanged original XTM2 CXTM baselines.
  The independent Python checker also verifies all seven XML positions,
  identifier ordering and Topic references. This does not claim an XTM reader.

The validator checks every retained suite total against Slice 15, compares all
83 successful original CTM/CXTM outputs and the known discrepancy outputs, and
compares retained semantic observations. The complete 273-contract statuses
remain **93 PASS, 2 FAIL, 0 UNSUPPORTED, 178 NOT-RUN**. The FAILs are the existing
`occurrence-datetime2.ctm` and `occurrence-datetime-timezone2.ctm` normative
baseline discrepancies. No newly implemented CTM syntax or imported contracts
are claimed. All pinned corpus/reference bytes are protected by checksum checks.

## Boundaries

No Reifier/Reified properties, CTM `~`, Reification-induced merging, XTM reader,
Templates, Include/Mergemap, cross-document merging or HyperDoc integration.
The historical Topic-SI/Occurrence-II guard remains an explicitly tested,
documented restriction until Slice 16B; no lexical coincidence is presented as
automatic Reification. See `reading-item-identifiers.md` for API and clauses.
