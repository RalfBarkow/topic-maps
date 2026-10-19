# Slice 20C: CTM prolog and three negative original contracts

Parent: `d024dc96ce091db06b9d09ea7c1ccb5f90b2886d`.
Branch: `codex/ctm-slice-20c`. The initial index and worktree were clean; the
observed registered CTM state was **252 PASS, 4 FAIL, 17 NOT-RUN**.

## Normative cause review

Reference: [ISO/IEC 13250-6:2010 CTM text](https://www.isotopicmaps.org/ctm/ctm.html),
sections 3.2, 3.5, 3.6, 3.7 and 3.16, consulted 2026-10-19. Published ISO
standards remain normative; the pinned corpus targets the 2010-03-31 draft.

Encoding selection precedes decoding: supplied encoding, UTF-8 BOM, declaration,
then the UTF-8 default. Conflicting explicit selections are errors. The encoding
header belongs at the stream start; the optional version follows it, before
ordinary directives or body content. Only version `1.0` is valid. `%ctm` is not
one of the grammar's directive types.

| Original source | Actual original bytes / directive | Required cause |
| --- | --- | --- |
| `BOM-contradicts-encoding.ctm` | `EF BB BF` followed by `%encoding "iso-8859-1"`, LF LF, `topic.`, LF | UTF-8 BOM conflicts with the explicit declaration, before decoding. |
| `unknown-directive.ctm` | `%ctm 1.0` and LF | Unknown directive type; syntax rejection. |
| `wrong-version.ctm` | `%version 10.0` and LF | Recognized version directive with a prohibited version. |

All three previously raised `ctm-unsupported / unsupported-directive` at character
zero. That fresh-process preimplementation observation is preserved in
`reports/slice-20c/preimplementation.json` for the original implementation run.
Actual final conditions, byte/character offsets, line/column values and complete
original hex strings are in `current.prolog.json` and `candidates.json`.
Byte offsets count from the original input, including the BOM; byte errors have
no invented character line/column. Character positions exclude a removed BOM.

## Scope assessment and targeted implementation

A general encoding architecture is unnecessary. `decode-ctm-octets` checks a
small initial ASCII header and calls the existing unchanged strict UTF-8 decoder.
Only the four CTM files `unicode.lisp`, `lexer.lisp`, `reader.lisp` and
`resources.lisp` need implementation changes. No new dependencies are added.

The public file API adds the optional `:encoding` string, following the same
selection order. Matching registered UTF-8 names are compared case-insensitively;
there is no alias registry. Other charsets remain `ctm-unsupported /
unsupported-encoding` when no conflicting declaration exists. ISO-8859-5 is not
decoded. Supplied encoding metadata is per input stream, not inherited by
separate Include/Mergemap resources. Their existing resolver still returns only
untouched octets and the optional diagnostic source key.

The shared resource decoder uses the same preflight. XTM raw bytes continue
through the unchanged XTM adapter and qualified XML boundary. Unicode decoding,
BOM removal, malformed UTF-8 rejection, document identity, wildcard state,
Include aliases/templates and Mergemap content import retain their existing
behavior.

`read-prolog` handles the initial encoding header and exact version spelling
before ordinary directives. Misplaced or repeated encoding/version directives
receive distinct placement errors; invalid versions do not enter the numeric
Occurrence lexer. Unknown directives become `ctm-rejection / unknown-directive`.
Known invalid syntax, unsupported charsets/literals and explicit resolver policy
retain separate classifications.

## Durable tests and registration

`tests/ctm-prolog.lisp` reuses the existing Case Records, result recording,
condition and model helpers. ASDF system `topic-maps/ctm/prolog-tests` runs after
the unchanged Slice 20A/20B snapshots in `scripts/fresh-sbcl.lisp`.

Positive controls cover empty and nonempty version prologs, an immediately
adjacent Topic after the fixed `1.0` terminal, comments, encoding
before version, prefixes and map reification, plus all 18 combinations of
optional supplied UTF-8, BOM and UTF-8 declaration. Actual Unicode Name values
and byte-exact canonical models are compared. Both Include and CTM Mergemap
exercise BOM, declared UTF-8, version and multibyte content through real resource
calls; input bytes and actual object references are checked.

Negative controls distinguish encoding conflicts, unsupported charsets, invalid
UTF-8, unknown directives, known malformed directives, unsupported literals,
invalid version spellings and misplaced/repeated prologs. Test instrumentation
observes zero UTF-8 decoder calls for conflict and unsupported-charset preflight,
even with a malformed body. Resource failures retain the child source and
Include/Mergemap context. The UTF-8 decoder is always restored after observation.

Each original is read twice through the public file API with its existing
Document IRI. Exact condition/code/position/source, reproducibility, unchanged
source bytes, unchanged contract identity and an accepted file control are
required before `record-result` registers PASS. Only the three selected records
change. In particular `empty2`, the valid ISO-8859-5 input and all other open
literal/template cases remain NOT-RUN.

One obsolete historical assertion that `%version 1.0` is unsupported is replaced
by a positive empty-Map assertion with the same assertion count. Its current
label changes in the prefix report and the combined core CXTM report. Historical
report files keep their exact bytes; current comparisons allow only that label
change and the five previously documented 19D2 label changes. Prior original
observations and the four known DateTime/Include FAILs remain unchanged.

## Full offline validation and evidence

```sh
cd /Users/rgb/workspace/topic-maps
python3 scripts/validate-slice-20c.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /tmp/topic-maps-20c-review
```

Use a new output directory. The 20C driver reuses the existing offline source
preparation, qualification programs, `scripts/test.sh`, ASDF suites and report
format. Older 20A/20B validators intentionally prohibit reader changes, so the
20C driver runs their same suites and verifies the retained stage reports rather
than weakening those historical validators. All Lisp qualification, regression
and documented retained inspections run in fresh SBCL 2.5.4 with network denied.
Nix preparation is offline and hash-verifies existing Store sources and patches.
No dependency downloads or full Nix rebuild occur.

Expected CTM counts after three proved rejections are **255 PASS, 4 FAIL,
14 NOT-RUN**; [execution.json](../reports/slice-20c/execution.json) records actual
validated totals. Separate XTM remains **6 PASS, 0 FAIL, 118 NOT-RUN**.

- `current.prolog.json`: original conditions, positive models and negative controls.
- `current.validation.json`: final original Case Records and counts.
- `current.cxtm.json`: all retained positive comparisons and four known mismatches.
- `candidates.json`: original source SHA-256 values and exact diagnostics.
- `retained/`: core, XTM-Mergemap, Slice 20A and Slice 20B stage reports.
- `xml.log`, `xtm.log`, `regression.log`: complete actual execution output.
- `source-preparation.json`, `integrity.json`: verified dependency provenance,
  protected files and unchanged historical reports.

Implementation, tests and execution evidence are committed together only after
successful full validation. No HyperDoc changes, push, deployment or later slice
are included.
