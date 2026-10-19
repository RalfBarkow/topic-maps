# Slice 20E: register the original empty2 contract

This slice registers only ctm/in/empty2.ctm after all retained 20A/20B/20C
stages, reusing the Slice 20A exercise-case function and the same discovered
Case Record. No CTM reader, TMDM or CXTM implementation changes are required.

The original source is exactly "%version 1.0" followed by LF (13 bytes).
Its baseline is "<topicMap>" LF "</topicMap>" LF (23 bytes).
CTM 3.5 [44]/[45] and 3.7 [48] permit this prolog without later constructs:
https://www.isotopicmaps.org/ctm/ctm.html .
The pinned corpus retains its historical 2010-03-31 draft qualification.

The existing original-execution function deserializes the unchanged file with
the discovered Document IRI. Its shared empty-map witness checks zero Topics
and Associations. It compares canonical octets with the original baseline,
checks raw model state and retained handles across canonicalization, checks
determinism and unchanged source bytes, and records PASS only for an actual
byte match. The new stage additionally checks the precise 13/23-byte vectors,
Case Record identity, stable previous observations and exactly one status
transition. ASDF topic-maps/ctm/empty2-tests is invoked unconditionally by
scripts/fresh-sbcl.lisp, after the historical stage reports are written.

Reproduce the complete offline acceptance run with an existing SBCL 2.5.4:

    python3 scripts/validate-slice-20e.py --sbcl /absolute/path/to/sbcl --output /private/tmp/new-slice-20e-report

The output directory must be new. The validator uses verified local Store
sources and the existing XML patches without downloads. Fresh SBCL processes
run with network denied. It runs TMDM/CTM/CXTM, XML qualification, standalone
XTM, XTM Mergemap, Slice 20A/20B/20C and the new original registration, plus the
existing Python tests and NFC oracle. It verifies the pinned corpus and hashes
every historical report and all protected repository files. Historical stage
reports are regenerated separately and checked against their prior provenance.

The run's actual results, the original comparison, source hashes and commands
are in reports/slice-20e/execution.json; full process output is retained in
the adjacent logs. current.registration.json records the executed checks,
current.cxtm.json contains actual and expected streams, and
current.validation.json records the final corpus statuses. These files are
written only by the successful execution; this document does not predeclare
the expected 256 PASS / 4 FAIL / 13 NOT-RUN as an observed result.

The default tool sandbox could not start because the configured writable root
/Users/rgb/.nix-profile is a symlink. Execution used the regular approved
require_escalated path; neither that symlink nor sandbox configuration was
changed. No persistent Lisp image, HyperDoc content, original corpus source,
baseline or historical report is modified. No push or deployment is performed.
