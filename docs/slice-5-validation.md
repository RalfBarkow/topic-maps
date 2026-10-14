# Slice 5 — Validation and acceptance evidence

Base commit: `8036a2b1ce009218f33d300edcc5f715ec1d1124`.
Branch: `codex/ctm-slice-5`. Initial branch was `codex/ctm-slice-4`, HEAD matched
that base, and the working tree was clean before branch creation.
The original corpus/locks remain unchanged at
`cd165b150176c1d6842b37be9cc9051b40d4996b` (CTM draft 2010-03-31).

## Implemented and observed

Occurrences belong to the existing TMDM Topic, with Parent/Type Topic object
references, lexical Value, Datatype locator and Item Identifiers. Supported
Scope is empty and Reifier null. Equal Occurrences are replaced according to
TMDM 5.6/6.5, their identifiers unioned, and retained handles resolve through
`canonical-occurrence`. Topic merges update actual stored Parent/Type references.

The dedicated CTM reader uses string/IRI literal kinds. Quoted content is not
IRI-resolved; IRI-form literals are formed/resolved under CTM 3.3.3. Datatype
locators are not interned as Topics. Explicit datatype-qualified strings and
numeric/date literals remain unsupported. Malformed inputs and unbound prefixes
retain specific rejection classes and source diagnostics.

CXTM represents Occurrences using §§3.5, 3.8, 3.13–3.23, 4.2–4.6 and 4.9.
Datatype output is not base-stripped; anyURI value output is locator-normalized.
String values sort before locator values under 4.2. Per-Topic Occurrence numbering
is separate from Name numbering. Canonicalization does not normalize/merge the
input model or compress retained forwarding chains.

The source texts, normative clause map, expected and actual items, public API,
limits and executable inspection are printed in
`docs/reading-first-occurrences.md`. The initial expectation table and original
sources were recorded before implementation, rather than inferred from generated XML.

## Actual end-to-end comparisons

Each source was read directly from the original corpus with its deterministic
absolute Document IRI; CXTM used that IRI as Base Locator. Actual binary output
was compared with the untouched upstream binary baseline. Neither side is trimmed,
reparsed, rewritten or normalized before this comparison.

| Selected original source | Result | UTF-8 bytes, actual = expected |
| --- | --- | ---: |
| `ctm/in/occurrence-string.ctm` | PASS | 359 |
| `ctm/in/occurrence-string2.ctm` | PASS | 359 |
| `ctm/in/occurrence-uri-relative.ctm` | PASS | 358 |
| `ctm/in/occurrence-two.ctm` | PASS | 730 |

`occurrence-string.ctm` and `occurrence-string2.ctm` each produce two Topics and
one string Occurrence with value `Occurrence`. The relative URI case produces
two Topics and one anyURI Occurrence whose stored value is the absolute logical
corpus locator ending `/ctm/in/file.html`; only CXTM renders `file.html`.
The two-occurrence case produces three Topics and two Occurrences: a multiline
xsd:string and the original absolute TMCL HTTP resource locator as xsd:anyURI.
All four maps contain no Names/Associations, and all Occurrence identifier sets
are empty. No datatype Topics are synthesized.

The combined canonical report retains the original 24 cases unchanged and adds
these four. Other cases are not inferred from newly available syntax.

| Imported contracts | PASS | FAIL | UNSUPPORTED | NOT-RUN |
| --- | ---: | ---: | ---: | ---: |
| 28 selected positive CXTM contracts | 28 | 0 | 0 | 0 |
| All 273 imported CTM contracts | 29 | 0 | 0 | 244 |

The additional PASS is the retained `prefix-undefined.ctm` negative contract,
verified as UNDEFINED-PREFIX, not a generic exception. Remaining 203 positive and
41 negative contracts were not executed.

## Fresh offline validation

Both complete suites used network-denying `sandbox-exec`, fresh SBCL processes,
no system/user init, no inherited ASDF source registry, and FASLs outside the repo.
The second suite ran in a newly copied checkout without `.git`/Python cache files.

| Executed checks, per runtime | SBCL 2.5.4 PASS | SBCL 2.4.10 PASS | FAIL |
| --- | ---: | ---: | ---: |
| Retained foundation | 54 | 54 | 0 |
| Retained identity semantics | 123 | 123 | 0 |
| Retained merge semantics | 646 | 646 | 0 |
| Retained Association/Role semantics | 657 | 657 | 0 |
| Retained CXTM checks | 445 | 445 | 0 |
| New Occurrence checks | 1,101 | 1,101 | 0 |
| Independent NFC oracle | 16,294 | 16,294 | 0 |
| Python integrity fixtures | 2 | 2 | 0 |

The new tests include actual references/values/datatypes for four original
sources, 144 construction permutations, 128 graph/order variants with an
independent connectivity oracle, duplicate and late merge identifier unions,
raw canonical Parent/Type references, old handles, Unicode/escaping, explicit
error classes/codes/positions, foreign map rejection and mutation-free failure paths.
The retained 445 CXTM check labels are exactly unchanged.

All six JSON report pairs are byte-identical across runtime versions/relocation:
validation, semantics, merging, associations, CXTM and Occurrences. The previous
24 semantic case records and canonical outputs equal committed Slice 4 records.
Python independently verifies raw CXTM bytes against the original baselines,
XML reference integrity and the actual Occurrence object-property observations.
The last Lisp block from the reading document was executed as printed, with its
Parent/Type EQ assertions and DESCRIBE output, in another fresh offline process.

## Reproduction and evidence

The exact two complete validation commands were:

```sh
cd /Users/rgb/workspace/topic-maps
'/usr/bin/sandbox-exec' '-p' '(version 1)(allow default)(deny network*)' '/usr/bin/env' 'PYTHONDONTWRITEBYTECODE=1' 'SBCL=/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl' 'TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-5-validation-tln5nucc/validation-2.5.4.json' '/Users/rgb/workspace/topic-maps/scripts/test.sh'
```

```sh
cd /private/tmp/ctm-slice-5-validation-tln5nucc/checkout
'/usr/bin/sandbox-exec' '-p' '(version 1)(allow default)(deny network*)' '/usr/bin/env' 'PYTHONDONTWRITEBYTECODE=1' 'SBCL=/nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl' 'TOPIC_MAPS_REPORT=/private/tmp/ctm-slice-5-validation-tln5nucc/validation-2.4.10.json' '/private/tmp/ctm-slice-5-validation-tln5nucc/checkout/scripts/test.sh'
```

The temporary relocated checkout was created by copying the repository while
excluding `.git`, `__pycache__` and `*.pyc`. Substitute another copied checkout
for future relocation runs; the logical Document IRIs do not change. Python's
NFC oracle requires UCD 15.0/15.1; recorded runs used 15.1.0.

`reports/slice-5/execution.json` records exact arguments, directories, exit codes,
Python version, counts and SHA-256 hashes. `occurrences.json` contains original
CTM source and actual object properties/references. `cxtm.json` contains complete
actual/expected XML for all 28 cases; `actual/` preserves the generated UTF-8 files.
Logs preserve raw process output; `describe.log` contains actual inspection output.
The combined CXTM report's 1,546 checks are 445 retained plus 1,101 new; they are
not counted a second time in the totals above.

## Limits and decision

No excluded feature was needed by the selected four cases. No normative/corpus
conflict was observed for them. The inherited explicit CXTM root-LF interpretation
is unchanged; this is bounded evidence, not full ISO conformity.
Nonempty Scope, Reification, Variants, arbitrary XSD numeric/date datatypes,
Templates, cross-document merging and HyperDoc integration are not implemented.
The existing prefix/triple-quote and URI grammar limits remain documented.
Explicit `^^` CTM datatype qualifiers are recognized but unsupported, including
string/anyURI qualifiers. The model API expects already validated absolute
locators; it is not a complete IRI grammar validator. Reification identity
conflicts are rejected rather than implemented implicitly. Unicode is bounded
to the existing 15.1.0 tables, with explicit unsupported results for newer characters.

**Acceptance evidence: PASS for the requested Slice 5 subset.** Implementation,
regressions, direct object observations and genuine baseline comparisons agree.
No server, deployment or HyperDoc change was made. Stop after this slice and
await review before extending CTM or TMDM.
