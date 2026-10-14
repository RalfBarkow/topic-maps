# Common Lisp Topic Maps — Slice 2

A working ANSI Common Lisp reader for the first CTM identity/default-name
subset, with same-map Topic/Name merging in a minimal TMDM model. HyperDoc
remains a possible future client and is neither the codebase nor a dependency. There is no CXTM
canonicalizer, association/template implementation or cross-document merge engine.

Systems: `topic-maps` (the retained foundation), `topic-maps/tests`,
`topic-maps/tmdm`, `topic-maps/ctm`, `topic-maps/ctm/tests` and
`topic-maps/ctm/merging-tests`.
The core reader/model uses ANSI Common Lisp; the foundation/tooling uses
ASDF/UIOP and Python's standard library. No Quicklisp packages are required.

Start with [Reading Topic Identity and Merging](docs/reading-topic-merging.md)
for the current API, reference replacement, identifier tails and exact subset
boundaries. See [Reading the First Five CTM Documents](docs/reading-first-five-ctm-documents.md)
for original sources, actual objects, normative clauses, baseline evidence and
copy-pasteable DESCRIBE forms. [API and boundaries](docs/slice-1-api-and-boundaries.md)
document the accepted Slice 1 baseline; the Slice 2 document supersedes its
statements about absent identity tails, merging and immutable Name references.

The pinned suite targets the **CTM draft dated 2010-03-31**. Passing it alone
does not establish full ISO/IEC 13250-6:2010 conformity.

## Load and inspect

In a new Common Lisp process, with this checkout selected:

```lisp
(require :asdf)
(asdf:initialize-source-registry
 '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps")
(defparameter *corpus* (topic-maps.test-foundation:discover-corpus))
(topic-maps.test-foundation:summarize-corpus *corpus*)
(topic-maps.test-foundation:select-cases *corpus* :category :invalid)
(topic-maps.test-foundation:select-cases *corpus* :id "ctm/in/simple.ctm")
(asdf:test-system "topic-maps/tests")
(asdf:test-system "topic-maps/ctm/tests")
(asdf:test-system "topic-maps/ctm/merging-tests")
(topic-maps.test-foundation:write-validation-report
 *corpus* #p"/tmp/topic-maps-inventory.json")
```

Change only the checkout pathname when using another machine. The case's
Document IRI remains independent of that pathname. Records are inspectable
Common Lisp structures, with actual source/baseline pathnames and explicit
contracts, results, statuses, diagnostics and reviewed clauses.

## Offline verification

```sh
# SBCL must already be installed. No network is used by this command.
TOPIC_MAPS_REPORT=/tmp/topic-maps-validation.json ./scripts/test.sh
```

Set `SBCL=/absolute/path/to/sbcl` if needed. The launcher starts a new process,
ignores system/user initialization, clears inherited ASDF source configuration
and writes FASLs outside the repository. It runs byte-integrity fixtures,
Common Lisp infrastructure checks and an independent JSON-schema/content check
when a report pathname is supplied. `nix develop path:.` supplies a minimal,
pinned SBCL/Python/Git environment; initial environment provisioning may need
network access, while test execution after provisioning does not.

The complete upstream corpus is already vendored, unchanged. If absent in a
source distribution, acquire it once:

```sh
python3 scripts/corpus.py acquire
python3 scripts/corpus.py verify
```

Acquisition uses the exact commit and archive digest in
[corpus-lock.json](references/corpus-lock.json), refuses to merge over existing
contents and verifies every file. Verification is offline. Valid CTM inputs
are selected only under `ctm/in`, invalid ones only under `ctm/invalid`, and
CXTM baselines only under `ctm/baseline`. Auxiliary files are reported separately.

## Current validation and historical foundation

The complete pinned corpus remains unchanged: 231 valid CTM inputs, 42 invalid
inputs, 231 CXTM baselines and 22 CTM auxiliary files. Sixteen selected semantic
cases pass; their imported canonical contracts remain NOT-RUN. Only
`ctm/invalid/prefix-undefined.ctm` is PASS under its CTM rejection contract;
272 imported contracts remain NOT-RUN. Unsupported constructs and I/O errors
cannot count as that required rejection.

The full launcher runs the retained 54 foundation checks, two Python integrity
fixtures, 123 retained identity checks, 646 merge checks, imported-report validation and selected baseline
property evidence. A report path also produces `<path>.semantics.json` with
separate model observations, plus `<path>.merging.json` for the new cases.
The merge checks include 128 graph/order variants with an independent reachability
oracle. Reports are deterministic across the tested SBCL versions and checkout
relocation. See [Slice 2 validation](docs/slice-2-validation.md),
[imported contracts](reports/slice-1/validation.json) and
[semantic observations](reports/slice-1/semantics.json).

[Slice 0 inventory](docs/inventory.md), [architecture](docs/architecture.md),
[coverage](docs/coverage.md) and [validation](docs/validation.md) remain historical
foundation records. Their original report/logs are preserved. Their statements
about absent reader/model systems describe Slice 0, not the current branch.
Slice 1 is built from `9c83db34eb1ba8091b004433f088056717dbaa7e` on
`codex/ctm-slice-1`. Slice 2 starts from the accepted Slice 1a commit
`fb60afd548d679d83fd8ec76bc5ff384c1e23e5f` on `codex/ctm-slice-2`.
Associations/Roles are not part of this slice; await review before continuing.
