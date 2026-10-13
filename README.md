# Common Lisp Topic Maps — Slice 0

An independent foundation for implementing ISO/IEC 13250-6:2010 (CTM) in
Common Lisp. **There is no CTM reader, TMDM model or CXTM canonicalizer yet.**
HyperDoc may become a client later; it is neither the codebase nor a dependency.

Only `topic-maps` (the actual test foundation) and `topic-maps/tests` exist.
The future `topic-maps/tmdm`, `topic-maps/ctm` and `topic-maps/cxtm` systems are
not defined. Loading the foundation does not pretend they are available.
Runtime dependencies: Common Lisp, ASDF/UIOP. Integrity/acquisition tooling
uses Python 3's standard library and Git. No Quicklisp packages are required.

## Load and inspect

In a new Common Lisp process, with this checkout selected:

```lisp
(require :asdf)
(asdf:initialize-source-registry
 '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps")
(defparameter *corpus* (topic-maps.test-foundation:discover-corpus))
(topic-maps.test-foundation:summarize-corpus *corpus*)
(topic-maps.test-foundation:select-cases *corpus* :category :invalid)
(topic-maps.test-foundation:select-cases *corpus* :id "ctm/in/simple.ctm")
(asdf:test-system "topic-maps/tests")
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

## Recorded result and authority

The pinned corpus has 231 valid CTM inputs, 42 invalid inputs, 231 CXTM baselines
and 22 auxiliary files in its CTM subtree, with no unmatched/missing baseline.
All 273 imported CTM cases are **NOT-RUN**; none passes a nonexistent reader.
Infrastructure fixtures exercise PASS, FAIL, UNSUPPORTED and NOT-RUN separately.

The upstream CTM suite targets the **draft dated 2010-03-31**. Passing that suite
alone would not establish full ISO/IEC 13250-6:2010 conformity. Published ISO
standards are normative; this corpus and Ontopia are independent evidence.

See [inventory and provenance](docs/inventory.md),
[coverage and the first five proposed Slice 1 cases](docs/coverage.md),
[architecture and Document-IRI policy](docs/architecture.md), and
[execution evidence](docs/validation.md).
The [machine-readable report](reports/validation.json) records actual imported
case contracts and the passing infrastructure check names, without claiming
CTM implementation. Nothing from Slice 1 is automatically started.
