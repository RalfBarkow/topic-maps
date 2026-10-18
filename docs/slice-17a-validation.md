# Slice 17A — Association arity validation

Base: `f1270a43720ab1454bebfb3d0a9e3555554a7ab9`; local branch
`codex/ctm-slice-17a`. Runtime, UTC interval, source hashes and artifact hashes
are recorded in `reports/slice-17a/execution.json`.

From the repository root:

```sh
python3 scripts/validate-slice-17a.py --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

The complete retained suite runs in a fresh SBCL process with user startup and
user ASDF registries excluded, under `sandbox-exec` denying network access.
No extra runtime versions, relocation, or cache-management changes are involved.

## Acceptance and evidence

- **10,301 Lisp checks pass: 9,964 retained and 337 new arity checks.**
  All retained assertions remain, including adapted feature-boundary
  assertions for now-supported n-ary Associations. Additional arity checks cover
  1/2/3/4/32/64 declarations, all 24 permutations of four Roles, repeated
  declarations, and declarations that normalize to only one or two Role items.
- Player, Role Type, Association Type and Scope-theme merging are exercised
  through both explicit merges and shared Topic identifiers, in both orders.
  Role and Association Item Identifiers, Reifiers, inverse references and old
  handles survive, including further replacement steps and scope collapse.
- QNames, explicit Item Identifiers, Subject Locators, Wildcards, Embedded Topics,
  nonempty Scope and source Role/Association Reifiers retain their existing
  semantics. Syntax errors and undefined prefixes have exact class/code/position
  assertions. `isa`/`ako` remain unsupported.
- Exactly one imported contract transitions: `association-duplicate-role.ctm`,
  NOT-RUN → PASS after real deserialization and 1,157 byte-equal CXTM bytes.
- Corpus: **107 PASS, 2 FAIL, 0 UNSUPPORTED, 164 NOT-RUN**.
  The FAILs remain `occurrence-datetime2.ctm` and
  `occurrence-datetime-timezone2.ctm` with unchanged outputs and diagnostics.
- The validator compares all prior 94 successful and two failing CXTM outputs,
  every retained model observation, all unchanged imported case records and
  prior suite counts. TMDM/CXTM source, references and corpus match the base.
- `arity.json` contains per-check labels, original source and actual EQ-reference
  observations; twelve additional XML witnesses are checked independently for
  canonical serialization, numbering and complete Role/Topic references.
- `original-reader-control.log` demonstrates the original reader's
  CTM-UNSUPPORTED/:ASSOCIATION-ARITY at position 48 in another disposable process.
  The documented inspection forms run independently and produce `describe.log`.

Both Python unit tests, the 16,294 independent NFC comparisons and every
independent report checker pass. The recorded full-run total and individual suite counts are in `execution.json`;
`tests.log` includes Python, NFC, Lisp and independent report-checker outcomes.
The open Core-Subject identity requirement for 17B is documented in
`reading-association-arity.md`. No change to that model behavior is claimed.
