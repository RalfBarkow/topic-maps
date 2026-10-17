# Slice 15 — Wildcards and Embedded Topics: validation

Branch `codex/ctm-slice-15`, base/parent
`4f7b4d26d40f8f5566594aa2e3ad6296d44fc4c3`. The starting index and working tree
were clean. Implementation, tests, documentation and execution evidence are
committed together. No HyperDoc repository or persistent Lisp image was changed.

## Reproduction and final result

```sh
python3 scripts/validate-slice-15.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

The validator runs `scripts/test.sh` in fresh SBCL 2.5.4 under
`/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)'`.
The exact subprocess command, runtime, times, source hashes and evidence hashes
are recorded in `reports/slice-15/execution.json`. Full output is `tests.log`.
The validated source is the base plus the recorded hashes, subsequently committed
together. No extra SBCL version, checkout relocation or cache-management work was
performed. No server or network access was used.

Final complete regression: **9,484 Lisp checks PASS, zero assertion failures**.

| Suite | Passed |
|---|---:|
| Foundation | 54 |
| Identity | 123 |
| Topic merging | 646 |
| Associations/Roles | 657 |
| Retained CXTM checks | 445 |
| Occurrences | 1,101 |
| Prefix/datatypes | 150 |
| Integers | 665 |
| Decimals | 715 |
| Dates | 1,806 |
| DateTime | 217 |
| Timezone | 1,944 |
| Typed Names | 106 |
| Scope | 293 |
| Variants | 324 |
| Topic references | 238 |

The two Python infrastructure fixtures, complete pinned corpus integrity check,
all retained independent report checkers, the new reference graph checker and
16,294 independent NFC oracle comparisons passed. The documented Lisp inspection
example passed in a separate fresh offline SBCL process.

## Imported contracts

Twenty-one new positive original inputs match unchanged CXTM baseline bytes.
Their exact list, source text, final counter and object graphs are in
`references.json`; actual XML bytes are saved under `actual/`. The four wildcard
cases and seventeen Embedded Topic cases cover recursive Name/Occurrence/
Association/Role Types, Role Players, Scopes, Variants and identity-triggered
merging. See `docs/reading-topic-references.md` for the complete list and clauses.

`ctm/invalid/embedded-topic-global-scope.ctm` is specifically rejected as
`CTM-REJECTION`, `:EMBEDDED-TOPIC-AT-TOP-LEVEL`, at source EOF. The diagnostic
retains the original case identity and character/line/column position.

Exactly those 22 contracts changed from NOT-RUN to PASS. Full corpus:
**93 PASS = 83 byte-exact positive contracts + 10 specific rejections;
2 FAIL; 0 recorded UNSUPPORTED; 178 NOT-RUN**.

Both DateTime baseline discrepancies remain FAIL: `occurrence-datetime2.ctm`
and `occurrence-datetime-timezone2.ctm`. Previous 64 executed CXTM outputs and
outcomes compare exactly with Slice 14. All retained case model observations
and timezone probes are unchanged. Corpus and references remain byte-identical.
The 40 independent earlier positive probes were not registered by this slice.

## Object and boundary evidence

Direct Lisp checks establish:

- Per-parse named wildcard reuse and anonymous uniqueness; exact `#$__N[.name]`
  Item Identifiers, preserved case/Unicode, 100-digit counters and independent
  Document/Wildcard IRIs. The file API forwards the same environment and returns
  its final counter; invalid environment arguments fail before file I/O.
- Named wildcard lookup after Topic replacement, using cached locator strings
  and the existing TMDM interner rather than cached obsolete object handles.
- Named Wildcards at all supported Type/Player/Scope positions share one
  environment. Explicit Name Types do not create an unnecessary default Type.
- Embedded Topic nesting to depth 40, preorder counter allocation and actual
  Type chains. Numeric/date/dateTime tokens stop correctly before `]`.
- Shared SI merging during Embedded Tails unions generated identifiers and
  updates stored Parent/Type/Player/Scope references. All live references point
  to actual current same-map Topics.
- Subsequent Topic/Name/Variant merging preserves retained canonical handles
  and Role references. Theme merges can reduce scope cardinality; loss of a
  Variant's additional scope still fails atomically.
- Deterministic, mutation-free CXTM, including retained forward links; specific
  malformed-Embedded/invalid-position diagnostics and preserved Role whitespace
  rules. Empty Embedded Topics are rejected because their Tail is required.

The independent Python checker compares full observed Topic identity-property
sets and all Name/Variant/Occurrence/Association/Role relationships with original
baselines. It also verifies complete generated identifier/counter sequences.
Observation ordinals are local evidence references, not persistent Subjects.

Old assertions that excluded newly supported references now use still-excluded
reified forms; their suite sizes and existing model/baseline results are retained.
Variant-scope Embedded probes now expect deserialization while leaving their
imported status NOT-RUN until the reference suite executes the full contracts.

## Scope retained

No TMDM source or canonicalization algorithm changed. The CXTM docstring was
corrected to acknowledge existing Variants. CTM's public reader gains optional
`:wildcard-iri` and `:wildcard-counter` and a secondary return value; existing
primary-value callers continue to receive the same Topic Map representation.

Reification, Templates, Include/Mergemap, `isa`/`ako`, more than two CTM Roles,
CTM `*`, cross-document merging and excluded datatype contexts remain outside
this slice. Template-dependent negatives remain NOT-RUN rather than being
promoted for an unrelated parser failure. No Slice 16 was started.
