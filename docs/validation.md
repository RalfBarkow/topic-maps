# Slice 0 validation and handoff

**Ready for Slice 1: Yes.** This confirms the foundation is ready for review,
not that CTM is implemented. Slice 1 has not started. No reader, semantic model
or canonicalizer is present; all imported CTM cases remain NOT-RUN.

The imported suite targets the **CTM draft dated 2010-03-31**. Passing it alone
would not establish full ISO/IEC 13250-6:2010 conformity. Published ISO standards
remain normative; the corpus and Ontopia are independent evidence.

## Observed results

| Check | Observed result |
| --- | --- |
| Complete vendored corpus integrity | All 2,006 original files match the pinned path/size/SHA-256 manifest |
| CTM inventory | 231 valid; 42 invalid; 231 baselines; 22 auxiliaries |
| Baseline correspondence | No missing input, missing baseline, unmatched baseline or duplicate case ID |
| Common Lisp infrastructure | 54 checks pass in fresh plain SBCL processes |
| Python integrity fixtures | 2 tests pass, including changed bytes, missing/extra files and incomplete correspondence |
| Independent report decoding | Standard-library JSON check passes, including all contracts and statuses |
| Imported CTM execution | 273 NOT-RUN; 0 PASS, 0 FAIL, 0 UNSUPPORTED |
| No implementation systems | `topic-maps/ctm`, `/tmdm` and `/cxtm` are not defined |
| Offline execution | OS sandbox denies network for the full test process |
| Relocated checkout | SBCL 2.4.10 reproduces the SBCL 2.5.4 report byte-for-byte at a different root |
| Primary ASDF test-op | `asdf:test-system "topic-maps"` routes to the passing infrastructure tests |
| Acquisition idempotence | Existing pinned corpus verified; nothing overwritten, no network |
| Nix shell | Pinned independent shell evaluates offline; no Nix build claimed |
| Existing HyperDoc checkouts | Both remain clean at their observed HEADs |

The successful final logs and exact environment/commands are stored in
[execution.json](../reports/execution.json), with SHA-256 digests.
[validation.json](../reports/validation.json) is the raw reproducible Lisp output,
including every case and the actual passing infrastructure-check names.
The checks test state transitions on independent fixtures; those outcomes are
not reported as upstream CTM conformance successes.

## Commands actually used

From `/Users/rgb/workspace/topic-maps`:

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /usr/bin/env \
  SBCL=/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-0-report-final.json \
  scripts/test.sh
```

A copy of the project, excluding `.git` and Python caches, was placed at
`/private/tmp/ctm-slice-0-relocated`. Its final standard package-import test
files were updated before the final relocated run:

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /usr/bin/env \
  SBCL=/nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl \
  TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-0-report-relocated.json \
  /private/tmp/ctm-slice-0-relocated/scripts/test.sh

cmp reports/validation.json /private/tmp/ctm-slice-0-report-relocated.json
```

Both test commands and `cmp` exited zero. The macOS sandbox restriction is an
acceptance executor, not a library dependency. On other platforms use an
appropriate network-denial executor if required; `scripts/test.sh` itself does
not use the network. SBCL and Python must already be installed.

Also verified:

```sh
python3 scripts/corpus.py acquire
python3 -m py_compile scripts/corpus.py scripts/check-report.py tests/test_corpus.py
nix eval --offline --raw \
  'path:/Users/rgb/workspace/topic-maps#devShells.x86_64-darwin.default.name'
```

The first command detects the already-present exact corpus and performs no
acquisition or write. The Nix command returned `nix-shell`. A separate fresh
SBCL process loaded `topic-maps.asd` with no inherited source registry and ran
`asdf:test-system "topic-maps"`; its complete command is recorded in execution.
No long-running Lisp image was modified, and no server, browser application,
SSH connection or deployment was started.

## Repository and commit

Worktree/repository: `/Users/rgb/workspace/topic-maps`.
Branch: `codex/ctm-slice-0`.
Base: empty independent repository, no parent commit. The delivery is the root
commit, created only after the infrastructure tests passed. Retrieve its exact
SHA with:

```sh
git -C /Users/rgb/workspace/topic-maps rev-parse HEAD
```

A commit cannot contain its own hash without circularity; the final handoff
reports the observed delivery SHA. Implementation, infrastructure tests,
reference locks, original corpus and reports are delivered in that one commit.
The five proposed semantic cases and their rationale are in
[coverage.md](coverage.md). Review this foundation before authorizing Slice 1.

The staged upstream tree was also compared with the original Git tree: all
2,006 Git blobs match exactly. Whole-tree whitespace checking flags original
upstream text and deliberately significant whitespace in baselines; those bytes
are retained. Whitespace checking of authored files passes separately.
