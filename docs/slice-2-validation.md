# Slice 2 validation: Topic Identity and Merging

The base was clean on `codex/ctm-slice-1` at the accepted commit
`fb60afd548d679d83fd8ec76bc5ff384c1e23e5f`. Work is on `codex/ctm-slice-2`.
The final commit is reported in the handoff; tests and implementation are
committed together only after successful validation.

## Executed results

| Check | SBCL 2.5.4 | SBCL 2.4.10, relocated checkout |
| --- | --- | --- |
| Retained identity/name suite | 123 PASS | 123 PASS |
| Same-map merging suite | 646 PASS | 646 PASS |
| Foundation regressions | 54 PASS | 54 PASS |
| Python integrity fixtures | 2 PASS | 2 PASS |
| Imported report validation | PASS | PASS |
| Original five baseline property checks | PASS | PASS |
| Eleven additional baseline property checks | PASS | PASS |
| Failures | 0 | 0 |

Both runs used fresh processes, ignored SBCL user/system initialization, and
ran under OS-denied networking. The second checkout was copied excluding Git
metadata and Python caches. All three generated JSON report pairs are
byte-identical across runtimes and relocation. Full logs, reports, exact
commands and artifact digests are retained in `reports/slice-2/`.
Both documented Lisp inspection blocks also ran in a fresh offline process;
`describe.log` records their objects and successful reference assertions.

The 646 merge checks comprise 134 concrete corpus/API/parser assertions and
512 assertions over 128 graph/order variants. An independent reachability
oracle considers all 64 undirected graphs on four Topics, each in forward and
reverse edge order. It checks components, identifier unions, Name coalescence,
retained handles and raw stored references. This is semantic testing, not
canonicalization. One previous unsupported-tail assertion was adapted to
check the newly implemented identity assignment; other Slice 1/1a assertions
remain in place.

## Exact complete test commands

```sh
# Working directory: /Users/rgb/workspace/topic-maps
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /usr/bin/env PYTHONDONTWRITEBYTECODE=1 SBCL=/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-2-final-2.5.4.json /Users/rgb/workspace/topic-maps/scripts/test.sh

# Working directory: /private/tmp/ctm-slice-2-relocated-vwd_hic2/checkout
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /usr/bin/env PYTHONDONTWRITEBYTECODE=1 SBCL=/nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-2-final-2.4.10.json /private/tmp/ctm-slice-2-relocated-vwd_hic2/checkout/scripts/test.sh
```

Both exited zero. The execution recorder compared each byte stream directly
before copying it into the retained artifacts. The comparisons can also be
reproduced with:

```sh
cmp /private/tmp/ctm-slice-2-final-2.5.4.json /private/tmp/ctm-slice-2-final-2.4.10.json
cmp /private/tmp/ctm-slice-2-final-2.5.4.json.semantics.json /private/tmp/ctm-slice-2-final-2.4.10.json.semantics.json
cmp /private/tmp/ctm-slice-2-final-2.5.4.json.merging.json /private/tmp/ctm-slice-2-final-2.4.10.json.merging.json
```

For another installed SBCL, use `SBCL=/path/to/sbcl
TOPIC_MAPS_REPORT=/tmp/slice-2.json ./scripts/test.sh` from the checkout.
The launcher includes all retained and new ASDF test systems and Python
baseline-property checks. No network dependency is needed during execution.

## Scope and evidence

The original five semantic case records are exactly unchanged from the
committed Slice 1 report. Eleven additional original identity-tail/duplicate
cases are separately checked against unchanged CXTM baselines. Topic matching
uses identifier sets, without treating observation order as canonical numbering.
No XML is generated or canonical output compared.

Imported status counts remain **PASS 1, FAIL 0, UNSUPPORTED 0, NOT-RUN 272**.
All 16 positive CXTM-EQUAL contracts remain NOT-RUN. The only imported PASS is
the existing specifically verified undefined-prefix rejection. No status is
inferred from a successful semantic property check.

All 2,006 pinned files still match their original hashes and sizes; upstream
inputs, baselines and corpus locks are unchanged. The corpus targets draft
2010-03-31, so these results do not establish full ISO conformance. No blocking
published-standard/corpus conflict was found for the selected cases.

Implemented requirements are bounded to TMDM 5.3.5, 5.4, 6.1, 6.2 and 6.3 for
the existing Topic/Name model, and CTM 3.9 identity tails using existing 3.3.6
resolution. See `reading-topic-merging.md` and `references/slice-2-sources.json`.
Reification conflicts and references in unimplemented item types remain outside
this model. Cross-map merges are rejected before mutation. Full IRI validation,
Associations/Roles, typed-name deserialization, Templates, directives and CXTM
canonicalization remain unsupported. No HyperDoc, server, SSH or deployment
work occurred. Await review before starting the next slice.
