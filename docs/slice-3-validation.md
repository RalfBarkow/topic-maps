# Slice 3 validation: Associations and Roles

Base was observed clean on `codex/ctm-slice-2` at accepted commit
`66664dbff6275d60dab1bc6a232fa70f7b916b8c`. Work is on `codex/ctm-slice-3`.
The final delivery commit is reported in the handoff after validation.

## Executed complete runs

| Check | SBCL 2.5.4 | SBCL 2.4.10, relocated checkout |
| --- | --- | --- |
| Identity/name suite | 123 PASS | 123 PASS |
| Topic/Name merging suite | 646 PASS | 646 PASS |
| Association/Role suite | 657 PASS | 657 PASS |
| Foundation regressions | 54 PASS | 54 PASS |
| Python integrity fixtures | 2 PASS | 2 PASS |
| Imported report validation | PASS | PASS |
| Original five baseline property checks | PASS | PASS |
| Eleven Slice 2 baseline property checks | PASS | PASS |
| Eight Association baseline property checks | PASS | PASS |
| Failures | 0 | 0 |

There are 1,426 semantic assertions per runtime. The 657 Association checks
include 145 concrete corpus/API/parser/reference assertions and 512 assertions
over 128 graph/order variants. Seven nonempty combinations of affected
Association type, Role type and Role player are tested after construction.
Stored fields, retained handles, transitive replacements, combined Name and
Association references, duplicate Roles/Associations, inverse roles played,
unordered Role sets and atomic rejection of foreign-map references are checked.
One former unsupported-Association assertion is adapted to successful parsing;
other prior suites retain their totals.

Both runs use fresh processes with user/system initialization disabled and
OS-denied networking. The relocated copy excludes `.git` and Python caches.
All four JSON report pairs are byte-identical across runtimes and relocation.
Full logs, reports, exact command vectors and artifact hashes are retained
under `reports/slice-3/`.

## Exact commands

```sh
# Working directory: /Users/rgb/workspace/topic-maps
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /usr/bin/env PYTHONDONTWRITEBYTECODE=1 SBCL=/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-3-final-2.5.4.json /Users/rgb/workspace/topic-maps/scripts/test.sh

# Working directory: /private/tmp/ctm-slice-3-relocated-f2q69ba3/checkout
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /usr/bin/env PYTHONDONTWRITEBYTECODE=1 SBCL=/nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-3-final-2.4.10.json /private/tmp/ctm-slice-3-relocated-f2q69ba3/checkout/scripts/test.sh
```

Both exited zero. The recorder compares complete byte streams before retaining
the reports. Equivalent comparison commands:

```sh
cmp /private/tmp/ctm-slice-3-final-2.5.4.json /private/tmp/ctm-slice-3-final-2.4.10.json
cmp /private/tmp/ctm-slice-3-final-2.5.4.json.semantics.json /private/tmp/ctm-slice-3-final-2.4.10.json.semantics.json
cmp /private/tmp/ctm-slice-3-final-2.5.4.json.merging.json /private/tmp/ctm-slice-3-final-2.4.10.json.merging.json
cmp /private/tmp/ctm-slice-3-final-2.5.4.json.associations.json /private/tmp/ctm-slice-3-final-2.4.10.json.associations.json
```

For another installed runtime, set `SBCL=/path/to/sbcl` and
`TOPIC_MAPS_REPORT=/tmp/slice-3.json` when invoking `./scripts/test.sh`.
The launcher runs all retained and new ASDF tests and the independent Python
property oracles. No network acquisition is required.

## Acceptance evidence and boundaries

`association.ctm` produces three Topics, an Association and a distinct Role:
five information items apart from the map, six including it. The binary case
produces five Topics, an Association and two Roles, nine including the map.
Role parent/type/player are actual references. The required late-merge matrix
inspects raw stored reference fields, so forwarding getters cannot hide stale
live references. Computed roles-played is checked against the live Role set.

The eight originals exercised are `association.ctm`, `association-binary.ctm`,
`association-binary-duplicate.ctm`, `association-type-sid.ctm` and the four
`association-with-comment` cases. The property oracle maps Topics by identifier
sets and Associations/Roles by structural signatures, and checks inverse links.
No observation order is treated as CXTM numbering; no XML is generated.

All prior 16 selected case observations are exactly unchanged from committed
Slice 2 reports. Imported statuses remain **PASS 1, FAIL 0, UNSUPPORTED 0,
NOT-RUN 272**. All 24 inspected positive CXTM-EQUAL contracts remain NOT-RUN;
only the existing specific undefined-prefix rejection is an imported PASS.

All 2,006 upstream files match pinned sizes and SHA-256 hashes. Inputs,
baselines and corpus locks are unchanged. The corpus targets draft 2010-03-31;
these selected properties do not prove full CTM/TMDM or CXTM conformity. No
blocking published-standard/corpus conflict was found for the selected cases.

Scope is limited to CTM one/two-role declarations and unscoped, unreified
Association/Role items. Empty/null properties are implicit. Larger CTM arities,
embedded Topics, scope/reification, prefix directives, Templates, typed Names,
Occurrences/Variants, special vocabulary relationships, full IRI validation,
cross-document merging and CXTM canonicalization remain outside this slice.
See `reading-first-ctm-associations.md` and `references/slice-3-sources.json`.
No HyperDoc, server, SSH or deployment work occurred. Await review before the
next slice.
