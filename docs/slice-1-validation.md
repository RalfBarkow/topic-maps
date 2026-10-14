# Slice 1 validation

Implemented on `codex/ctm-slice-1` in `/Users/rgb/workspace/topic-maps`, from the
observed clean Slice 0 commit `9c83db34eb1ba8091b004433f088056717dbaa7e`.
The delivery commit is obtained with `git rev-parse HEAD` and reported in the
handoff; implementation and its tests are committed together after passing.

**100 semantic checks pass; zero fail.** The five selected original files yield
actual Topic Map, Topic and Topic Name objects. The required negative original
file is rejected specifically for its undefined prefix. The retained 54
foundation checks and two Python integrity fixture tests pass. The obsolete
foundation assumption that no reader/model system exists is adapted to verify
the still-absent canonicalizer; its other tests are retained.

The immutable corpus remains at `cd165b150176c1d6842b37be9cc9051b40d4996b`.
All 2,006 upstream hashes match. **It targets CTM draft 2010-03-31; passing it
alone cannot establish full ISO/IEC 13250-6:2010 conformity.** Published ISO
standards remain authoritative. No conflict was found blocking a selected case.

## Separate results

| Result class | Observed result |
| --- | --- |
| Five imported semantic cases | PASS, actual model properties and cardinalities checked |
| Independent semantic regressions | PASS: Document IRI, separate identifier kinds, duplicate references, default type reuse, parent/type object identity, Unicode, UTF-8, errors and unsupported constructs |
| Original positive `CXTM-EQUAL` contracts | All five remain NOT-RUN |
| Original `prefix-undefined.ctm` rejection contract | PASS: typed undefined-prefix condition at character 1, line 2, column 1 |
| All imported statuses | PASS 1; FAIL 0; UNSUPPORTED 0; NOT-RUN 272 |
| Selected baseline evidence | Expected properties checked against five frozen XML baselines; no XML generated and no canonical equality claimed |
| OS-enforced offline runs | PASS with fresh SBCL 2.5.4 and 2.4.10 |
| Relocation | Both imported and semantic JSON reports reproduce byte-for-byte |
| Standard DESCRIBE inspection | PASS in a fresh SBCL process |
| HyperDoc / services | Both observed checkouts clean; no server, deployment or running-image changes |

[Imported contracts](../reports/slice-1/validation.json),
[separate semantic observations](../reports/slice-1/semantics.json),
[successful 2.5.4 log](../reports/slice-1/tests-2.5.4.log),
[relocated 2.4.10 log](../reports/slice-1/tests-2.4.10-relocated.log), and
[execution record with digests](../reports/slice-1/execution.json) are retained.
The semantic report's Topic ordinals describe creation/inspection order; they
are not CXTM numbering or a canonicalization implementation.

## Exact reproduction commands

From `/Users/rgb/workspace/topic-maps`:

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /usr/bin/env \
  SBCL=/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-1-final.json \
  scripts/test.sh
```

A copy of the final implementation checkout excluding `.git` and Python caches
was made at `/private/tmp/ctm-slice-1-relocated`, then:

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /usr/bin/env \
  SBCL=/nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl \
  TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-1-relocated.json \
  /private/tmp/ctm-slice-1-relocated/scripts/test.sh

cmp /private/tmp/ctm-slice-1-final.json /private/tmp/ctm-slice-1-relocated.json
cmp /private/tmp/ctm-slice-1-final.json.semantics.json \
    /private/tmp/ctm-slice-1-relocated.json.semantics.json
```

Both commands and comparisons exited zero. `scripts/test.sh` runs corpus hashes,
Python integrity fixtures, `asdf:test-system "topic-maps/tests"`,
`asdf:test-system "topic-maps/ctm/tests"`, independent JSON validation and
selected baseline-property checks. On another machine substitute installed SBCL
paths and an appropriate network-denial executor. The library itself has no
macOS dependency; SBCL launch flags remain outside the ANSI reader/model.

For a simple installed-runtime reproduction:

```sh
SBCL=/path/to/sbcl TOPIC_MAPS_REPORT=/tmp/slice-1.json ./scripts/test.sh
```

Implemented clauses and precise subset boundaries are in
[API and boundaries](slice-1-api-and-boundaries.md) and the
[consulted-source record](../references/slice-1-sources.json).
[Reading the First Five CTM Documents](reading-first-five-ctm-documents.md)
provides original sources, actual observations and exercised inspection forms.
Remaining unsupported functionality includes the full merge model, CXTM,
associations/roles, occurrences, variants, scope/reification, templates,
directives, typed names, topic-tail identity assignments and other encodings.
Full IRI/scheme validation is also outside this slice.

**Ready for Slice 2: Yes.** Slice 2 is not started. Await review of this reader,
minimal model and the distinct test/report contracts before continuing.
