# Slice 16B — Reification validation

Base: `f24ac27e1e1cc0118411b058d40af3c1c87f3ffb`; local branch
`codex/ctm-slice-16b`. Source and artifact hashes, runtime and UTC interval are
recorded in `reports/slice-16b/execution.json`.

## Reproduction

From this checkout's root:

```sh
python3 scripts/validate-slice-16b.py --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

The complete retained suite executes in fresh SBCL 2.5.4 with user startup and
user ASDF registry excluded, under `/usr/bin/sandbox-exec` denying network access.
No additional SBCL versions, relocation or cache-management changes are involved.
The documented Lisp inspection forms run in a second isolated process.

## Results and evidence

- 9,964 passing Lisp checks: 9,728 retained checks and 236 Reification checks.
- Retained Python unit tests, 16,294 independent NFC comparisons and all
  independent report checkers pass.
- Eleven new original CTM/CXTM byte-exact comparisons and two original specific
  CTM rejections. Exactly these thirteen imported contracts transition to PASS.
- Full corpus: **106 PASS, 2 FAIL, 0 UNSUPPORTED, 165 NOT-RUN**.
- The FAILs remain `occurrence-datetime2.ctm` and
  `occurrence-datetime-timezone2.ctm`, with their existing normative discrepancies.

`reification.json` contains per-check labels, original sources, current model
properties, actual Reifier Topic ordinals and EQ/inverse assertions.
`reification-actual/` contains actual CXTM bytes; the original baselines remain
unmodified. `tests.log` records full execution and independent checks.
`describe.log` contains real objects from the documented inspection process;
its addresses are historical observations in that process, not durable identity.

The validator compares all prior 83 successful CTM/CXTM outputs and both known
discrepancy outputs, every retained model observation, all prior suite totals and
the seven manual XTM2-model comparisons with Slice 16A. Corpus and reference
checksums are checked before/after; the pinned upstream material is unchanged.

## Model and failure coverage

All six attachments are checked with actual EQ references in both directions.
Tests cover null, idempotent, different-Reifier merging, explicit clearing,
all directed cross-kind Reifier conflicts, foreign/invalid arguments and Topic
as an invalid reified target. Each structural item kind is merged with separate
Reifiers and Item Identifiers; retained handles and original Map membership are
checked after further assertions. Role/Association metadata is retained.

A four-level Name → Occurrence → Association/Role cascade reaches a fixed point.
Scope-collapse fixtures reject at each of those four levels through three
Topic-merge entry routes and preserve the complete original graph/handles.
Additional tests cover setter-induced collapse, identifier-triggered Reifier
conflicts, Reifiers also serving as Parent/Type Topics, construction order,
serialization purity and explicitly rejecting corrupted Reifier references.

Tests formerly asserting unsupported Reification now assert successful reading.
The old Topic-SI/Occurrence-II restriction tests now assert acceptance without
automatic Reification. Their prior assertion counts are retained; these are
consumed feature boundaries, not removed coverage. XTM2 models remain manually
constructed comparisons; no XTM deserialization contracts are claimed.

Atomic semantic rejection is the local API policy, implemented by disposable
copies of the same TMDM structures using the same merge operations. It does not
claim a general transaction engine or recovery from resource exhaustion.
See `reading-reification.md` for exact normative clauses, API and exclusions.
