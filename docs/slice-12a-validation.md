# Slice 12A — validation and acceptance evidence

Base: `6a2f8446afca0915882f0d4a06cb891ccfcdc96d`.
Branch: `codex/ctm-slice-12a`.

## Change

The public `topic-maps.tmdm:add-name` accepts an optional `:type` Topic.
`add-default-name` delegates without that keyword. The reader uses its existing
identity resolver for local, IRI, QName, explicit Item Identifier and Subject
Locator type references. No new identity model or information-item class.
The existing Name merging and CXTM implementation remain unchanged.

Normative references and actual inputs/properties are in
`docs/reading-typed-topic-names.md`: CTM 3.11 and its Topic-reference rules;
TMDM 5.4, 6.2 and 6.3; CXTM 3.6 and 4.7. TMDM 6.4 is reviewed but does not
apply to this no-Variants subset.

## Executed validation

The full existing Slice 0–11 suite plus the new typed-name tests ran offline,
in a fresh SBCL 2.5.4 process in the primary checkout. Network operations were
denied by `sandbox-exec`. No extra SBCL-version run, checkout relocation or
FASL-cache management was performed for this slice.

| Group | Passed assertions |
| --- | ---: |
| Infrastructure | 54 |
| Identity | 123 |
| Topic/Name merging | 646 |
| Associations/Roles | 657 |
| Retained CXTM | 445 |
| Occurrences | 1101 |
| Prefixes/datatypes | 150 |
| Integer | 665 |
| Decimal | 715 |
| Date | 1806 |
| DateTime | 217 |
| DateTime timezone | 1944 |
| Explicitly typed Names | 106 |
| **Total** | **8629** |

The 106 new assertions cover object identity, no unnecessary default Topic,
identity-category resolution, malformed input diagnostics/source positions,
undefined prefixes, different types for equal text, Type identity merging,
Parent/Type merge orders, retained Name and Topic handles, foreign/NIL types,
mutation-free refusal, self-typing, canonical sorting and pure serialization.
Previously valid-but-unsupported typed-name assertions were adapted; missing
name values remain specific CTM-REJECTIONs. The retained identity/prefix groups
keep their assertion counts and original model observations.

The Python checks independently decode all reports, verify original bytes,
model-property observations and XML reference integrity. Existing independent
numeric/calendar/Unicode checks also pass. The documented DESCRIBE example was
executed separately in a fresh, offline SBCL process and passed.

| Selected original contract | Byte-exact CXTM |
| --- | --- |
| `ctm/in/name.ctm` | PASS |
| `ctm/in/name2.ctm` | PASS |
| `ctm/in/name-type.ctm` | PASS |
| `ctm/in/name-duplicate.ctm` | PASS |

There are 56 positive byte-exact contracts, 8 specific negative PASS contracts,
2 known positive baseline-discrepancy FAILs, 0 UNSUPPORTED and 207 NOT-RUN.
Only `name-type.ctm` and `name2.ctm` transition from NOT-RUN to PASS. All 56
previously executed CXTM outputs are unchanged, including both FAIL outputs.
The protected corpus and reference files are byte-identical before/after.

`reports/slice-12a/execution.json` records runtime, UTC timestamps, exact
command, executed-source SHA256 values and artifact hashes. It identifies the
base plus the tested working source hashes; it does not pretend the precommit
execution took place at a future commit. `typed-names.json` contains actual
model observations; `cxtm.json` separately records actual/expected canonical
bytes and contract outcomes. `tests.log` and `describe.log` are execution logs.

## Reproduction

From the repository root, use the existing development SBCL:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-12a.py --sbcl "$(command -v sbcl)" --output /private/tmp/ctm-12a-review
```

The recorded execution used:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-12a.py --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

For only the existing full regression entry point and its independent checks:

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /usr/bin/env PYTHONDONTWRITEBYTECODE=1 SBCL="$(command -v sbcl)" TOPIC_MAPS_REPORT=/private/tmp/ctm-12a-report.json ./scripts/test.sh
```

## Limits

No Embedded Topics, Scope, Reification, Variants, Templates, cross-map merging
or HyperDoc integration. The two DateTime baseline conflicts are preserved,
not counted as successful canonical comparisons. No additional conformance
cases are promoted merely on the basis of earlier exploratory byte equality.
