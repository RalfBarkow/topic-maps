# Slice 19C validation and evidence

Base: `5e716c078b885e97ebe858230ce7d8578e65ae4b`.
Branch: `codex/ctm-slice-19c`.
Corpus pin: `cd165b150176c1d6842b37be9cc9051b40d4996b`.

```sh
cd /Users/rgb/workspace/topic-maps
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-19c.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

The validator executes all retained suites and the Include suite in one fresh
SBCL process under macOS `sandbox-exec` with network access denied. The normal
source registry/output settings remain unchanged. No additional runtime,
relocation, cache redesign, persistent image or HyperDoc system is involved.
The existing Python infrastructure tests and independent NFC oracle also run.

`reports/slice-19c/execution.json` records exact commands, UTC times, runtime,
phase totals, status changes and source/artifact hashes. `tests.log` is the
actual full execution. All previous phase totals and every pre-existing corpus
case must remain unchanged. Original positive outputs and observed model graphs
are compared with Slice 19B. Four old unsupported-Include labels are replaced
with precise missing-resolver assertions, without changing phase counts.
Original Template error classes/codes/sources/positions remain unchanged;
Template context strings gain definition/invocation source metadata.

All twelve original Include contracts now execute. Seven positive comparisons
match unmodified bytes and three negatives reject for their intended reasons.
`include-template.ctm` and `include-wildcard2.ctm` have their real comparison
results registered as **FAIL**, separately from passing semantic assertions.
See `reading-ctm-include.md` for the derivation and exact identifier differences.
The expected aggregate is **204 PASS, 4 FAIL, 0 UNSUPPORTED, 65 NOT-RUN**,
including the two retained DateTime FAILs. This is not an all-green conformance
claim. A successful regression means those discrepancies remain visible and no
unexpected result occurs.

`include.json` contains the original sources, actual model properties, resource
requests, every successful processor's Document/Wildcard IRI and Counter, and
Topic identifiers before/after each actual alias pass. The fresh test process
instruments the real functions, delegates to them, captures observations, and
restores the functions afterward. It supplies no alternative import or identity
model. `check-include.py` independently checks these traces and model identities.
`cxtm.json` plus `actual/` preserve all nine actual canonical results, including
the two mismatches. `check-cxtm.py` compares original expected bytes independently,
checks canonical XML and reference integrity, and never converts mismatch to PASS.

Focused assertions cover preserved identifier categories/values, literal-prefix
aliasing and percent handling, resolver identity, counter/cache locality,
Template arguments/forward references/overloads, correct nested source positions,
canonical handles for six content kinds, root metadata exclusion, Scope/Variant/
Reifier integrity, pure serialization and rejection before caller Map/Counter/
registry mutation. Resource errors and cycle/depth policy remain distinct from
malformed CTM. Invalid XTM-as-Include is rejected by the CTM reader at the child
source, not by an unrelated I/O failure or later undefined prefix.

The documented inspection runs separately in a fresh offline process. A base
lexer counterprobe reloads the committed pre-Include lexer in a disposable
process and confirms its former unsupported-directive response. Corpus/reference
hashes and TMDM/CXTM source trees must remain unchanged. No original baseline is
rewritten and no XTM-deserialization contract is promoted.
