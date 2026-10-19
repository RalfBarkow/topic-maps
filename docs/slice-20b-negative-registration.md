# Slice 20B: seven negative original CTM contracts

Parent: `9044114749dedc72f190f4aa9ba0443dfe7860b5`.
Branch: `codex/ctm-slice-20b`. The initial branch, HEAD, empty index and clean
worktree were observed before any edit. The initial registered CTM result is
**245 PASS, 4 FAIL, 24 NOT-RUN**. All seven candidates initially have NOT-RUN
status, no actual outcome and no CXTM baseline, as expected for invalid inputs.

## Sources and normative review

Original files come unchanged from `vendor/cxtm/ctm/invalid/`. The pinned
`vendor/cxtm/README` defines invalid inputs as rejection contracts;
`ctm/STATUS.txt` dates the corpus to the 2010-03-31 CTM draft. There are no
individual prose descriptions for these seven beyond their source text and
the identifier comment. No historical exploratory rejection is counted here.

The consulted reference is
[ISO/IEC 13250-6:2010 CTM text](https://www.isotopicmaps.org/ctm/ctm.html),
reviewed on 2026-10-19; published ISO standards remain the normative authority.

| Original filename | Applicable clause / productions | Reviewed cause |
| --- | --- | --- |
| `occurrence-double-positive-infinity.ctm` | 3.4.1 [28]–[34]; 3.10 [56] | Bare `INF` is not a literal. |
| `occurrence-double-negative-infinity.ctm` | 3.4.1 [28]–[34]; 3.10 [56] | Bare `-INF` is not a literal. |
| `qname-hyphen.ctm` | 3.3.4 [9]–[11]; 3.3.6 [14]–[16] | Hyphen cannot start the local part. |
| `string-unbalanced.ctm` | 3.4.1 [37]–[40]; 3.4.2 [41] | Escaped quote leaves the string unclosed. |
| `string-unicode.ctm` | 3.4.2 [42] | Uppercase `U` requires six digits, not four. |
| `string-unicode2.ctm` | 3.4.2 [42]–[43] and decoding prose | `G` is not hexadecimal. |
| `topic-id-illegal.ctm` | 3.3.6 [14]–[16] | U+0361 is a continuation character, not a start. |

The printed [43] class includes all letters. For `string-unicode2`, this review
relies on 3.4.2's hexadecimal decoding requirement; the printed class alone
would not reject `G`. This qualification is retained in each result.

## Actual cause evidence

The reader reports `ctm-rejection`, not `ctm-unsupported`, for every candidate in
the preliminary fresh-process investigation. The durable execution must repeat
those observations through public `deserialize-file`, with each existing Case
Record's Document IRI and original source name. Positions are zero-based Unicode
character offsets; lines and columns are one-based. The
[actual result table](../reports/slice-20b/contracts.md) records every condition,
code, offset, line and column. `current.negative.json` preserves full messages,
two repeated original calls, token observations and actual control models.

The QName error is generic: `unexpected-token` at the colon, offset 38, rather
than a dedicated invalid-QName condition. Actual tokens are identifier `ex`,
colon, hyphen. The valid `ex:issue` sibling resolves the declared prefix. This
establishes the malformed local-part boundary rather than an undefined prefix
or unavailable IRI resource. The test requires that token evidence as well as
the exact reader condition.

Each candidate also has an explicit valid sibling generated only in memory:

- `INF` / `-INF` become `1` / `-1`, with actual integer Occurrence values,
  datatypes, Parent and Type references checked.
- `ex:-issue` becomes `ex:issue`, with the resolved Subject Identifier checked.
- The unclosed string receives its missing closing quote; the Name value is
  checked as `Foo` followed by a quotation mark.
- The four-digit uppercase escape uses lowercase `u`; the malformed six-digit
  escape becomes `\U000041`. Both actual Name values must be `A`.
- The leading U+0361 moves after `a`; the accepted local Item Identifier is checked.

These controls are separate calls to `deserialize-string`; original bytes are
never corrected, replaced or fed through a workaround. Exact source spelling,
source/baseline hashes and all existing contract identities are checked.

## Registration and execution

The same `tests/ctm-registered-originals.lisp` package, `check`, `binary`,
`identity-fields`, `case-state`, model helpers and shared corpus from 20A are
reused. The existing positive implementation remains unchanged except for two
new exported entry points. The ASDF secondary system
`topic-maps/ctm/registered-negative-tests` depends on the existing original-test
system and invokes `run-negative-tests`. `scripts/fresh-sbcl.lisp` calls it after
the 20A snapshot; tests are executed, not merely loaded.

Only an exact intended syntax condition, exact location and source, absent
nested cause/context, reproducible original rejection, source witness and
accepted control can register `ctm-rejection` through existing `record-result`.
Other outcomes are documented separately and leave the original Case Record
NOT-RUN. The validator writes that evidence before failing acceptance if any
candidate lacks the required cause. It does not correct the reader.

All prior Case Records, specification-clause identities, positive CXTM
observations and the four known DateTime/Include FAILs remain unchanged.
Normative review metadata is attached to the new execution evidence rather
than retrospectively changing historical case metadata.

## Full offline validation

Run from the repository with an unused output directory:

```sh
python3 scripts/validate-slice-20b.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /tmp/topic-maps-20b-review
```

The unchanged 20A validator invokes the unchanged 19D2 qualification/regression
chain. Network is denied for fresh SBCL 2.5.4 XML, XTM, full CTM/TMDM/CXTM and
inspection processes. Preparation uses offline Nix evaluation, verified existing
Store sources and unchanged XML patches. No dependency downloads occur.
The new negative suite runs in the same fresh regression process after the forty
20A comparisons. Independent Python checks verify actual codes, character
locations, control model observations, exact status changes, corpus integrity
and byte-identical historical reports. A full Nix rebuild remains NOT-RUN.

[Execution evidence](../reports/slice-20b/execution.json) records actual totals;
**252 PASS, 4 FAIL, 17 NOT-RUN** is accepted only if all seven intended causes
were proved during that run. Separate XTM remains **6 PASS, 0 FAIL, 118 NOT-RUN**.

Evidence includes:

- `current.validation.json`: final existing Case Records and totals.
- `current.negative.json`: actual conditions, causes, positions, controls and checks.
- `current.cxtm.json`: retained positive comparisons, with no invented negative baselines.
- `candidates.json` and `contracts.md`: all seven actual statuses and source hashes.
- `remaining.json`: unexecuted original records.
- `retained-20a/`: complete fresh 20A and earlier regression evidence.
- `integrity.json`: protected source/baseline and historical-report SHA-256 hashes.

No CTM/TMDM/XTM/CXTM semantics, original sources, baselines or historical reports
are changed. No HyperDoc changes, push, deployment or later slice are included.
