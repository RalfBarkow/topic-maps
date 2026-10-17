# Slice 14 — Variants: acceptance evidence

Branch: `codex/ctm-slice-14`. Parent/base:
`aeb017e4f4846f2e6a701e581d20eef84a8b83d9` (Slice 13).
The checkout and index were clean before creating the branch. No HyperDoc
repository, image, View or Work Topic was modified.

## Executed final validation

```sh
python3 scripts/validate-slice-14.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

The script invokes the existing `scripts/test.sh` in a new SBCL 2.5.4 process
under `/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)'`.
No network, server, HyperDoc, relocation, alternate SBCL or cache-management
work was used. Output files are execution evidence, not new upstream baselines.

Final result: **9,246 Lisp checks PASS**, zero assertion failures:

| Suite | Passed |
|---|---:|
| Foundation | 54 |
| Identity | 123 |
| Topic merging | 646 |
| Associations/Roles | 657 |
| Retained CXTM checks | 445 |
| Occurrences | 1,101 |
| Prefixes/datatypes | 150 |
| Integers | 665 |
| Decimals | 715 |
| Dates | 1,806 |
| DateTime | 217 |
| Timezone | 1,944 |
| Typed Names | 106 |
| Scope | 293 |
| Variants | 324 |

The two retained Python infrastructure fixtures, corpus integrity verification,
all existing independent report checkers, the new Variant JSON/XML checker and
16,294 independent NFC oracle comparisons also passed. The reading document's
Lisp inspection example ran successfully in a separate fresh offline process.

Machine-readable execution context, exact commands/times, source hashes, suite
totals, protected-corpus checks and artifact hashes are in
`reports/slice-14/execution.json`; full output is `tests.log` in that directory.
The tested revision is the stated base plus the hashed source changes, later
committed together with this evidence. No permanent Lisp object addresses are
claimed by the report ordinals.

## Actual new original contracts

| Case | Result | Actual CXTM bytes |
|---|---|---:|
| `ctm/in/variant.ctm` | PASS, byte-exact | 592 |
| `ctm/in/variants.ctm` | PASS, byte-exact | 857 |
| `ctm/in/variant-duplicate.ctm` | PASS, byte-exact | 592 |
| `ctm/invalid/variant-no-scope.ctm` | PASS, specific CTM rejection | — |

The negative condition is exactly `CTM-REJECTION`, code
`:EXPECTED-VARIANT-SCOPE`, character offset 28, line 3, column 22.

Only those four imported statuses changed from NOT-RUN to PASS. Full corpus:
**71 PASS = 62 exact positive CXTM contracts + 9 specific rejections;
2 FAIL; 0 recorded UNSUPPORTED; 200 NOT-RUN**. Unsupported diagnostic probes do
not promote the unexecuted contracts. The previous 61 executed CXTM outputs and
outcomes compare exactly to Slice 13's evidence. Corpus/reference files remain
byte-identical; the pin is `cd165b150176c1d6842b37be9cc9051b40d4996b`.

The two FAILs remain `occurrence-datetime2.ctm` (leap-second baseline) and
`occurrence-datetime-timezone2.ctm` (timezone baseline). A green regression suite
does not convert those documented normative discrepancies into PASS.

## Model and merge evidence

`variants.json` records source text, Document IRI, actual Topic identity
properties, Name Parent/Type/Scope references and Variant Value/Datatype/Scope
with direct and stored Parent checks. Python independently compares these
objects, by their identity-property sets, with the unchanged baselines.

Direct Lisp tests prove:

- Name-to-Variant containment, actual same-map Theme objects, unordered Scope
  equality and defensive copies; invalid arguments leave the model unchanged.
- Explicit CTM Scope is unioned with nonempty Parent Scope; a nonempty written
  Scope that contributes no additional theme is rejected.
- Value/Datatype/Scope/Parent equality, duplicate replacement and retained
  canonical Variant handles. Qualified lexical values remain stored unchanged.
- Parent-Topic, Name-Type and Name-Scope merges union Name children and replace
  stored Variant Parent references. Subsequent Variant duplicates merge.
- Theme merges update actual Scope references and can merge Variants. Scope
  cardinality may shrink while proper containment remains true.
- Explicit, II-, SI- and SL-triggered merges that would destroy proper
  containment are refused before changing identifiers, objects or forward links.
  A separate transitive normalization test checks full-closure preflight.
- 120 Variant construction orders produce the same CXTM, with independent XML
  checks of Value/Datatype/Scope ordering, numbering and reference integrity.
  Serialization leaves current objects and retained handles unchanged.

## Boundaries

Normative sources and exact clauses are in `docs/reading-variants.md`: TMDM
§§5.4–5.5/6.1–6.4; CTM §§3.4.1/3.11–3.12; CXTM §§3.6–3.7/3.12–3.21/4.2–4.8.
Atomic rejection of an incompatible merge is the documented local API policy
preserving the proper-superset invariant, not a normative recovery algorithm.

Variant Reification and explicit Variant Item Identifiers are not implemented.
Reifier remains null and identifiers empty. Embedded Topics, Templates, CTM `*`,
cross-document merging and previously excluded datatype/calendar contexts remain
unsupported. The reifier/embedded/template original contracts stay NOT-RUN.
No extra features were added to improve imported counts. No Slice 15 was started.
