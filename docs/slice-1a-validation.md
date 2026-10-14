# Slice 1a: name error classification

Base: `1805023b5c5690f224a2bb556af46a4af7c36687`, observed clean on
`codex/ctm-slice-1`. This correction does not begin Slice 2.

CTM 3.11 requires a string after the optional name type and colon. CTM 3.3.1
allows whitespace between tokens. Both `a - type:"Name".` and
`a - type: "Name".` are valid typed-name syntax, whose deserialization remains
unsupported. References: ISO/IEC 13250-6:2010,
<https://www.isotopicmaps.org/ctm/ctm.html>, clauses 3.3.1, 3.3.4 and 3.11.

The lexer forms a QName only when a local part immediately follows its colon;
otherwise the colon remains a separate token. The reader checks for a name
string, or a type followed by colon and string, before classifying typed names
as unsupported. It does not resolve name types or add typed-name semantics.

Before/after observations were reproduced in fresh SBCL processes, loading
source from the base Git commit and the corrected checkout respectively:

| Source | Before | After | Character offset / line / column |
| --- | --- | --- | --- |
| `a - .` | CTM-UNSUPPORTED / :TYPED-NAME | CTM-REJECTION / :EXPECTED-NAME-VALUE | 4 / 1 / 5 |
| `a -` | CTM-UNSUPPORTED / :TYPED-NAME | CTM-REJECTION / :EXPECTED-NAME-VALUE | 3 / 1 / 4 |
| `a - type:"Name".` | CTM-UNSUPPORTED / :TYPED-NAME | CTM-UNSUPPORTED / :TYPED-NAME | 4 / 1 / 5 |
| `a - type: "Name".` | CTM-REJECTION / :INVALID-QNAME | CTM-UNSUPPORTED / :TYPED-NAME | 4 / 1 / 5 |

The regression suite asserts exact classes, codes, offsets, line/column,
character position units, source labels and meaningful diagnostics for all
four inputs. Further checks cover a missing type separator, a missing typed
name value, and newline/comment layout. All original 100 semantic check labels
remain; 23 checks were added.

## Validation executed

Both complete runs passed: **123 semantic checks, 54 foundation checks and 2
Python integrity tests**, zero failures. Each used a fresh SBCL process with
OS-denied networking. The second used a relocated copy excluding `.git` and
Python caches. Exact commands:

```sh
# Working directory: /Users/rgb/workspace/topic-maps
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /usr/bin/env PYTHONDONTWRITEBYTECODE=1 SBCL=/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-1a-2.5.4.json scripts/test.sh

# Working directory: /private/tmp/ctm-slice-1a-relocated-yfcaz7au/checkout
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /usr/bin/env PYTHONDONTWRITEBYTECODE=1 SBCL=/nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-1a-2.4.10.json /private/tmp/ctm-slice-1a-relocated-yfcaz7au/checkout/scripts/test.sh

cmp /private/tmp/ctm-slice-1a-2.5.4.json /private/tmp/ctm-slice-1a-2.4.10.json
cmp /private/tmp/ctm-slice-1a-2.5.4.json.semantics.json /private/tmp/ctm-slice-1a-2.4.10.json.semantics.json
```

All commands exited zero. Both report pairs are byte-identical. The five
positive semantic case records, including actual object properties and
parent/type reference observations, are unchanged from the committed Slice 1
semantic report. The selected frozen-baseline property checker also passes.

Imported statuses remain PASS 1, FAIL 0, UNSUPPORTED 0, NOT-RUN 272. All five
positive CXTM-EQUAL contracts remain NOT-RUN; only the specific undefined-prefix
rejection is PASS. No canonical output was produced.

All 2,006 pinned corpus files still match their original sizes and hashes;
inputs, baselines and pin files are unchanged. No TMDM source was changed.

No remaining discrepancy was observed for the four requested inputs. Existing
Slice 1 boundaries remain, including unsupported typed-name deserialization,
full IRI validation and general merging, and absent CXTM canonicalization.
The pinned corpus targets draft 2010-03-31 and does not establish full ISO
conformity. No HyperDoc integration, server, SSH or deployment was performed.
