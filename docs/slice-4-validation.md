# Slice 4 — Validation and acceptance evidence

Base: `35648c4dcc71e8dc6448b64abcacb438e53d64a2`.
Branch: `codex/ctm-slice-4`. The initial Slice 3 branch/HEAD were verified and the
working tree was clean before creating the branch.

The core addition is `topic-maps/cxtm`, depending only on `topic-maps/tmdm`.
No CTM reader/model source, original corpus file, baseline or lock changed.
No server, deployment or HyperDoc integration was performed.

## Executed evidence

Both complete launches used fresh SBCL processes, ignored system/user init,
and denied network access with `sandbox-exec`. One used SBCL 2.5.4 at the original
checkout; the other used SBCL 2.4.10 in an independent relocated copy. The NFC
oracle launches an additional fresh SBCL process and verifies that neither the
CTM nor foundation package is loaded when only the canonicalizer is requested.
Python UCD version in both recorded runs: 15.1.0.

| Executable checks, per runtime | PASS | FAIL |
| --- | ---: | ---: |
| Retained infrastructure | 54 | 0 |
| Retained identity semantics | 123 | 0 |
| Retained Topic/Name merge semantics | 646 | 0 |
| Retained Association/Role semantics | 657 | 0 |
| New CXTM checks | 445 | 0 |
| Independent Python NFC oracle comparisons | 16,294 | 0 |
| Python corpus-integrity fixtures | 2 | 0 |

The 445 checks include 24 literal byte comparisons/purity observations, 48
construction permutations, 128 graph/edge-order variants, current/retained
reference checks after Topic/Name/Association/Role replacement, canonical set
ordering/numbering, file output, NFC/UTF-8/escaping and explicit error contracts.
The 16,294 oracle comparisons cover 4,122 canonical mapping/decomposition inputs,
all 11,172 Hangul decompositions and 1,000 seeded combining sequences. This is
an independent algorithm comparison, not a claim that every Unicode string
or the complete UAX conformance suite was exercised.

All five report pairs are byte-identical across runtimes and relocation:
validation, semantics, merging, associations and CXTM. The 24 original semantic
case observation records equal the committed Slice 3 records. The copied
DESCRIBE/serialization example from the reading document was independently
executed, including assertions for the two Topics, one Name and 328 bytes.

## Imported contracts

| Corpus scope | PASS | FAIL | UNSUPPORTED | NOT-RUN |
| --- | ---: | ---: | ---: | ---: |
| 24 selected positive `:CXTM-EQUAL` contracts | 24 | 0 | 0 | 0 |
| All 273 imported CTM contracts | 25 | 0 | 0 | 248 |

The additional PASS remains the specific `undefined-prefix` rejection of
`ctm/invalid/prefix-undefined.ctm`. The remaining 207 positive and 41 negative
contracts were not executed. They have no inferred acceptance/conformity status.

| Original input | CXTM result | UTF-8 bytes, actual = expected |
| --- | --- | ---: |
| `ctm/in/simple.ctm` | PASS | 114 |
| `ctm/in/subject-identifier.ctm` | PASS | 141 |
| `ctm/in/subject-locator.ctm` | PASS | 139 |
| `ctm/in/item-identifier.ctm` | PASS | 137 |
| `ctm/in/name.ctm` | PASS | 328 |
| `ctm/in/topic-subject-identifier.ctm` | PASS | 207 |
| `ctm/in/topic-subject-identifier-wrapped.ctm` | PASS | 207 |
| `ctm/in/topic-subject-identifier-duplicate.ctm` | PASS | 146 |
| `ctm/in/topic-subject-locator.ctm` | PASS | 201 |
| `ctm/in/topic-subject-locator-wrapped.ctm` | PASS | 201 |
| `ctm/in/topic-subject-locator-semi.ctm` | PASS | 201 |
| `ctm/in/topic-subject-locator-duplicate.ctm` | PASS | 112 |
| `ctm/in/topic-item-identifier.ctm` | PASS | 159 |
| `ctm/in/topic-item-identifier-wrapped.ctm` | PASS | 159 |
| `ctm/in/topic-item-identifier-duplicate.ctm` | PASS | 114 |
| `ctm/in/name-duplicate.ctm` | PASS | 328 |
| `ctm/in/association.ctm` | PASS | 507 |
| `ctm/in/association-binary.ctm` | PASS | 833 |
| `ctm/in/association-binary-duplicate.ctm` | PASS | 833 |
| `ctm/in/association-type-sid.ctm` | PASS | 535 |
| `ctm/in/association-with-comment.ctm` | PASS | 507 |
| `ctm/in/association-with-comment2.ctm` | PASS | 507 |
| `ctm/in/association-with-comment3.ctm` | PASS | 507 |
| `ctm/in/association-with-comment4.ctm` | PASS | 507 |

Every case was deserialized from its original source with the recorded absolute
Document IRI, canonicalized with that IRI as explicit base, then compared against
the original binary baseline. Mismatches report the first differing byte and
both lengths. Unsupported CTM/CXTM conditions map to UNSUPPORTED; unrelated
failures map to FAIL. No XML whitespace trimming, locator rewriting of baselines
or incomplete serialization comparison is used to award PASS.

`reports/slice-4/cxtm.json` contains the complete actual and expected XML for all
24 cases, logical bases and byte counts. `reports/slice-4/actual/` preserves the
actual generated UTF-8 files, independently checked against the unchanged
baselines. `execution.json` records exact launches, checkout locations, exits,
Python version, result counts and artifact SHA-256 values. Logs retain raw output.

## Normative interpretation and limits

The exact clause map, API, base-locator reasoning and representative Name XML
are in `docs/reading-canonical-topic-maps.md`. CXTM's explicit §3.1 root LF is
retained; generic XML-C14N after reparsing discards it. This interpretation is
recorded, and the byte oracle uses neither reparsing nor normalization.
No other discrepancy was observed for the selected 24 cases. These results
establish this bounded implementation against the pinned draft-era suite, not
full CTM, TMDM or CXTM conformity. Occurrences, Variants, nonempty Scope,
Reification, non-Topic identifiers and datatype canonicalization are unsupported.
Unicode is explicitly bounded to assigned UCD 15.1.0 characters; ambiguous
normalized Topic identity keys are rejected rather than silently merged.

## Exact reproduction commands

Run with installed runtimes and Python UCD 15.0/15.1; no acquisition/network is
required. These are the two commands actually executed:

```sh
cd /Users/rgb/workspace/topic-maps
'/usr/bin/sandbox-exec' '-p' '(version 1)(allow default)(deny network*)' '/usr/bin/env' 'PYTHONDONTWRITEBYTECODE=1' 'SBCL=/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl' 'TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-4-validation-5tf9f583/validation-2.5.4.json' '/Users/rgb/workspace/topic-maps/scripts/test.sh'
```

```sh
cd /private/tmp/ctm-slice-4-validation-5tf9f583/checkout
'/usr/bin/sandbox-exec' '-p' '(version 1)(allow default)(deny network*)' '/usr/bin/env' 'PYTHONDONTWRITEBYTECODE=1' 'SBCL=/nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl' 'TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-4-validation-5tf9f583/validation-2.4.10.json' '/private/tmp/ctm-slice-4-validation-5tf9f583/checkout/scripts/test.sh'
```

The temporary relocated checkout was made by copying the checkout while excluding
`.git`, `__pycache__` and `*.pyc`. A new relocated directory can be substituted
for a later reproduction; logical Document IRIs remain the same. Reports from
the two commands must compare byte-for-byte, including `.cxtm.json`.

The documented inspection forms are printed in the reading document and their
actual output is retained in `reports/slice-4/describe.log`.

**Decision:** PASS for the requested Slice 4 subset, with the explicit LF
interpretation and unsupported boundaries above available for review. Stop here;
do not extend the CTM/TMDM model or begin another slice before review.
