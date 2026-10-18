# Slice 18 — Templates: validation and boundaries

Base: `963f2a09444100d37e49cccbd6634879bd6742b5`; branch
`codex/ctm-slice-18`. Runtime, UTC execution interval, exact command, source and
artifact hashes are recorded in `reports/slice-18/execution.json`.

Reproduce from the repository root:

```sh
python3 scripts/validate-slice-18.py --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

The complete retained suite and the Template suite execute in a fresh SBCL 2.5.4
process under `sandbox-exec` with network denied and user/system init disabled.
No additional version, relocation or cache-policy work is performed.

Expected validated results:

- 11,317 retained + 297 new = **11,614 Lisp assertions**, zero assertion failures.
- Both Python unit tests, 16,294 independent NFC comparisons and all independent
  report/model checkers pass.
- **57** additional unchanged positive originals pass byte-for-byte;
  **10** additional negative originals pass their specific rejection contracts.
- Imported status: **187 PASS, 2 known DateTime FAIL, 0 UNSUPPORTED, 84 NOT-RUN**.
  The passing contracts comprise 165 positive comparisons and 22 rejections.
- All prior 108 positive outputs, both known discrepancy outputs, earlier model
  observations and all unrelated imported records are unchanged.
- Corpus/reference hashes and TMDM/CXTM sources are unchanged from the base.
- Original-baseline byte equality is separate from direct Lisp reference tests
  and from the independent Python relation between observed model and XML.

The replacement of old feature-boundary assumptions is deliberate: definitions
now have no model effects, and supported Template-dependent Variant sources now
parse. `a()` is an Invocation with no definition, rather than an empty
Association; `a(r p)` has malformed Invocation arguments. Their diagnostic tests
now follow the extended grammar. Existing assertion totals are retained.

The connected Merge witness retains Topic, Name, Variant, Occurrence,
Association, Role and Reifier handles; verifies Identifier unions and inverse
references; and checks continued Tail ownership. Core-Subject and Variant-scope
conflicts retain the existing atomic operation policy. Serialization preserves
all held slots and forwarding links. Body-definition tests instrument interning
and inspect stored CTM statement/token objects and the untouched Counter.

`base-control.log` loads the committed old CTM definitions in another disposable
process and confirms that definitions, Tail Invocations and variables were
unsupported there. `describe.log` executes the published inspection forms;
object addresses are observations of that process only.

The seven explicit grammar cases and four Import-dependent cases remain
NOT-RUN; see `reading-ctm-templates.md` for the exact distinction. The two
DateTime FAILs remain normative baseline discrepancies, not regression errors.
The expansion depth limit is resource policy. Duplicate parameter names are
rejected as an API binding policy. There is no whole-invocation transaction
promise. Include/Mergemap, cross-document merging, additional literal forms,
encodings and HyperDoc changes remain excluded.
