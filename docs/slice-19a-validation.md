# Slice 19A validation

Base: `0573c4f710982dab1c3f2c9284adf459caaf73e9`.
Branch: `codex/tmdm-slice-19a`.

Run the complete retained suite and new Map-content-import model tests in a
fresh SBCL 2.5.4 process, offline, with the established development runtime:

```sh
cd /Users/rgb/workspace/topic-maps
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-19a.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

The validator runs `scripts/test.sh` under macOS sandbox-exec with network
access denied, preserving all Slice 0–18 regression phases. It independently
checks the JSON reports, executes the documented inspection forms and reproduces
the old normalizer's Reifier-first rejection in a separate process.
No persistent Lisp image is involved. No cache configuration, checkout relocation
or additional SBCL version is part of this validation.

Execution evidence: `reports/slice-19a/execution.json` contains exact commands,
UTC timestamps, runtime, exit code, per-phase totals, protected-source hashes
and artifact hashes. `tests.log` is the actual full regression output.
`map-import.json` records new model checks, 50 rejection witnesses and two model
transfer/merge witnesses with actual CXTM output.

Expected imported statuses remain **187 PASS, 2 FAIL, 0 UNSUPPORTED, 84 NOT-RUN**.
The 187 PASS comprise 165 byte-exact positive CTM/CXTM contracts and 22 specific
negative CTM contracts. The two DateTime FAILs are pre-existing published-standard
versus upstream-baseline discrepancies. All 273 imported case records, all 167
executed CXTM result records, and all retained model-observation reports must
match the saved Slice 18 evidence. No CTM import contract becomes PASS here.

`src/ctm`, `src/cxtm`, `vendor` and `references` must have no changes from BASE.
Source files are hashed before and after validation. Source and target immutability
on semantic rejection, source preservation on success, and retained canonical
handles are tested through raw object slots as well as CXTM comparisons.

Results are recorded by execution, not inferred from this document. A validator
failure aborts before delivery; the local commit is made only after a successful
complete run. See [Reading Map Content Import](reading-map-content-import.md) for
the public API, normative basis, exact transaction boundary and inspection forms.
