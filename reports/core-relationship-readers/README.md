# Core relationship readers and default name types — execution report

Base revision: `88994c1b9e1edbf13e665e984a5c9c3b2cdf7575` (branch `dreyeck.ch`).
Runtime: SBCL 2.4.10, Python 3.13, Linux. All runs used the unchanged offline
launcher `scripts/test.sh` in a fresh process, with `TOPIC_MAPS_REPORT` set.

## What was changed

- `src/tmdm/core-relationships.lisp`: six read-only functions that recognize
  the type-instance (TMDM 7.2) and supertype-subtype (TMDM 7.3) Associations.
  They are added API over stored items, not a repair of a conformance defect.
- `tests/core-relationships.lisp`, `tests/default-name-types.lisp`, their two
  ASDF systems, two launcher lines and `scripts/check-core-relationships.py`.
- Documentation: `docs/tmdm-coverage-matrix.md` (new),
  `docs/reading-type-relationships.md`, `docs/reading-typed-topic-names.md` and
  one pointer in `README.md`.

No existing source file under `src/` was changed except the export list in
`src/tmdm/package.lisp`. Identity, merging, scope, canonicalization, the Core
Subject set and the CTM, XTM and CXTM code are untouched. Sort names (TMDM 7.4)
are deferred.

## Runs

| Run | State of the tree | Exit code | Log |
|---|---|---|---|
| before | unchanged `88994c1b` | 0 | [before/run.log](before/run.log) |
| default name types alone | tests added, no production change | 0 | 21 checks |
| core relationships alone | readers and tests added | 0 | 50 checks |
| after | all changes | 0 | [after/run.log](after/run.log) |

## Results

**Passed.**

- The baseline run on the unchanged tree.
- `DEFAULT-NAME-TYPE-PASS`: 21 checks. They passed against the unchanged
  production code, so the two default name type Subject Identifiers needed no
  code change.
- `CORE-RELATIONSHIP-PASS`: 50 checks over TMDM 7.2 and 7.3, including the
  eleven original `isa`/`ako` inputs.
- `CORE-RELATIONSHIPS-SERIALIZED-DATA-PASS`: the Python evaluation of the
  eleven unchanged CXTM baselines agrees with the counts the readers report.
  This evaluates serialized data; it is not a proof of conformance.
- Regression: the 25 report files the launcher wrote before the changes are
  byte-identical after them, the CXTM report included
  ([before/report-sha256.txt](before/report-sha256.txt),
  [after/report-sha256.txt](after/report-sha256.txt)). The after run has the
  316 PASS lines of the before run plus the three new ones.

**Failed.** Nothing new. The launcher reports the same known baseline
discrepancies before and after (the DateTime and Include cases documented in
`docs/slice-22c-normative-decisions.md`); they are retained FAIL contracts of
the corpus, not regressions.

**Not run.**

- The XTM suites (`topic-maps/xtm/tests`, `topic-maps/ctm/xtm-tests`): they
  require SBCL 2.5.4 and the patched CXML sources, which were not available.
  The XTM reader path for name types and `instanceOf` is therefore not
  exercised by this report.
- Inference over supertype-subtype relationships and sort names: not
  implemented, hence not tested.

## Open points

- The editions published by ISO were not consulted; clause numbers refer to the
  public texts listed in `docs/tmdm-coverage-matrix.md`.
- Both default name type identifiers are supported as different identifiers.
  The explicit merge of the two type Topics is recorded as current behaviour
  only.
- The next smallest integration task is on the client side: use
  `type-instance-relationship` instead of a local derivation of Topic types.
