# Slice 19B validation

Base: `9ce2a2b5116edfd921a5240efcb2f604f9523693`.
Branch: `codex/ctm-slice-19b`.
Pinned corpus: `cd165b150176c1d6842b37be9cc9051b40d4996b`.

Reproduce the full retained regression and new CTM Mergemap tests:

```sh
cd /Users/rgb/workspace/topic-maps
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-19b.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

The validator runs `scripts/test.sh` in a fresh SBCL 2.5.4 process under macOS
sandbox-exec with network access denied. It retains the established source
registry/output translation settings without cache, relocation or additional
runtime work. The documented Lisp inspection is executed separately, and a
base lexer counterprobe verifies its former unsupported-directive response.

`reports/slice-19b/execution.json` records UTC execution times, exact commands,
exit status, all phase totals and source/artifact hashes. `tests.log` is the
actual complete run; `mergemap.json` separates original positives/negatives from
its focused checks. Four actual CXTM documents are preserved in `actual/`.
An independent Python checker compares original inputs, model identifier sets,
resource keys/IRIs and negative source positions. The existing CXTM checker
compares every executed positive baseline byte-for-byte and retains the two
DateTime mismatch records.

Only seven imported statuses may change: the four requested positive Mergemap
cases and three requested invalid cases. Expected aggregate:
**194 PASS (169 positives, 25 negatives), 2 known FAIL, 0 UNSUPPORTED, 77 NOT-RUN**.
Every other imported case record, the previous 167 CXTM records and all retained
model observations must match Slice 19A. All pinned sources, baselines,
references, TMDM and CXTM source files must remain unchanged.

Two older tests used unknown notation `urn:ctm` but expected all Mergemap syntax
to be unsupported. They now assert the specific unknown-notation rejection.
The Reference boundary label remains unchanged; the Template check is renamed
to `diagnostic:unknown-mergemap-notation`. Their phase totals and original corpus
contracts remain intact. The validator allows exactly this one report-label
replacement and no other retained-report drift.

Identity tests cover shared SIs, Topic IIs, SI/II overlap, SLs, dependent item
merging and retained target handles. Observations use the actual import's object
references. Additional tests cover resource resolution, namespace isolation,
Wildcard counters, repeated/nested imports, execution order, strict bytes/BOM,
resolver policy, diagnostic chains, metadata and deterministic pure CXTM.
Core, Reifier, Variant and identifier conflicts leave both graphs and their
CXTM unchanged at the import boundary. Non-Topic identifiers in synthetic model
tests are explicit TMDM API additions, not extra CTM syntax or corpus passes.

Results derive from execution evidence, not these expected counts. No persistent
Lisp image, HyperDoc, network resolver or server is used. Include and XTM
Mergemap contracts remain NOT-RUN, and no Slice 19C/19D work is included.
