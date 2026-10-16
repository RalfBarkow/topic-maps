# Slice 9 — Date Occurrences: validation evidence

Repository `/Users/rgb/workspace/topic-maps`; initial branch `codex/ctm-slice-8`,
HEAD `195d5f5444d776096b765d04c815c23c3db5f84c`, clean index/tree. Created
`codex/ctm-slice-9` from that exact commit. The corpus remains pinned at
`cd165b150176c1d6842b37be9cc9051b40d4996b`; upstream inputs, baselines and
existing references are unchanged.

## Normative interpretation

Rules were recorded before implementation in `reading-date-occurrences.md`:
published CTM §3.4.1 (XSDT validity), CTM §3.2 (BOM), TMDM §§4.3–4.4, 5.6,
6.5, CXTM §§3.16, 4.9, XSD Second Edition §§3.2.7.1, 3.2.9–3.2.9.2, 4.3.6,
D and E.1. The HTML mirror omits days 01–09 in production 35; the published
preview expressly requires XSDT-valid Dates. This slice admits those days in
accord with XSD and the selected tests, without claiming the mirror grammar
is correct or that the published Annex grammar was available in that preview.

Year zero, a leading plus, fewer than four year digits and extended years with
leading zeros are invalid. The calendar checks month lengths and Gregorian
4/100/400 divisibility with a bounded residue accumulator; no machine-sized
year, local timezone, platform calendar, floating point, or Lisp reader is used.
BCE leap validation applies E.1 directly to the signed lexical year. XSD 1.0's
BCE leap ambiguity is expressly qualified in the reading document, rather than
silently importing XSD 1.1 astronomical numbering or permitting year zero.

The existing Occurrence is the sole model: stored Value string, Datatype locator,
Parent Topic and Type Topic stay separate. Bare date literals use the existing
canonical-string policy; qualified strings/direct API values retain their
valid lexical strings. CXTM trims XML whitespace and renders the supported
canonical date without modifying values or handles. Equality/duplicate merging
remain lexical; matching canonical output does not imply TMDM equality.
Ordering compares stored strings, not chronology or formatted XML.

## Original contracts

Five selected positive files match original CXTM bytes: occurrence-date (357),
occurrence-date2 (357), occurrence-date3 (1066), occurrence-date-negative (358),
occurrence-date-another-century (359). All are PASS. The two UTF-8 BOMs are read
through the existing byte decoder and remain unchanged in the source evidence.

Five selected negative files are PASS under their rejection contracts:
date-invalid-day → INVALID-DATE-DAY; date-invalid-month → INVALID-DATE-MONTH;
date-invalid-year, year2, year3 → INVALID-DATE-YEAR. Each is CTM-REJECTION with
source/character/line/column diagnostics; unsupported or I/O errors cannot pass.
Full sources, actual information items/references, diagnostic coordinates and
XML are in `reports/slice-9/dates.json` and `cxtm.json` and the reading document.

| Imported contracts | PASS | FAIL | UNSUPPORTED | NOT-RUN |
|---|---:|---:|---:|---:|
| All 273 | 59 | 0 | 0 | 214 |
| Positive CXTM | 51 | 0 | 0 | 180 |
| Negative CTM | 8 | 0 | 0 | 34 |

All 46 previously passing positive cases have identical actual object
observations and canonical outputs. The three prefix rejections remain PASS.
Only the ten selected Date contracts change NOT-RUN → PASS.

## Complete fresh offline runs

Both runs disable user/system initialization and inherited ASDF configuration.
`sandbox-exec` denies network access. SBCL 2.4.10 runs in a separate relocated
checkout without `.git`; deterministic IRIs remain independent of file location.

| Suite | SBCL 2.5.4 | SBCL 2.4.10 relocated |
|---|---:|---:|
| Foundation | 54 | 54 |
| Topic Identity | 123 | 123 |
| Topic Merging | 646 | 646 |
| Associations/Roles | 657 | 657 |
| Retained CXTM | 445 | 445 |
| Occurrences | 1101 | 1101 |
| Prefix/explicit datatypes | 150 | 150 |
| Integers | 665 | 665 |
| Decimals | 715 | 715 |
| Dates | 1806 | 1806 |
| **Total Lisp checks** | **6362** | **6362** |
| Python infrastructure tests | 2 | 2 |
| Independent NFC comparisons | 16294 | 16294 |
| Independent Integer probes | 143 | 143 |
| Independent Decimal probes | 157 | 157 |
| Independent Date probes | 396 | 396 |
| Independent century decisions | 15 | 15 |
| Positive original CXTM byte comparisons | 51 | 51 |
| **Failures** | **0** | **0** |

All ten report pairs are byte-identical. The 4882 checks in the combined CXTM
report are already included above, not additional tests. Python's separate
calendar oracle uses arbitrary-precision integers and calendar.isleap, not
platform-local dates/timezones. Probes include 10,000-digit years, valid
month/year combinations, explicit XML whitespace, negative years and centuries.
Date tests also cover invalid year/month/day forms, lexical/grammar boundaries,
QName distinction, duplicate replacement, Topic merges, canonical raw reference
slots, retained handles, construction-order independence, lexical order rather
than chronology and mutation-free serialization.

Retained assertions formerly testing unsupported Dates were adapted one-for-one:
DateTime remains an excluded fixture; explicit Date now uses a valid date and
expects canonical output. All prior suite totals and original-case observations
are preserved. Initial development compilation/fixture corrections precede the
final successful full runs; the final logs contain no test failures.

The public Lisp inspection example was executed successfully under the same
network-denied policy. Exact commands, versions, exit codes, input digest and
64 artifact digests are in `reports/slice-9/execution.json`. Original reports and
baselines were neither rewritten nor substituted.

## Reproduction

```sh
python3 /Users/rgb/workspace/topic-maps/scripts/validate-slice-9.py \
  --sbcl-254 /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --sbcl-2410 /nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl \
  --output /private/tmp/topic-maps-slice-9-reproduction
```

Actual validation used `--output reports/slice-9`. It requires the already
installed runtimes, Python with UCD 15.0/15.1 and macOS sandbox-exec; it provisions
nothing. To run one fresh complete suite:

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /usr/bin/env PYTHONDONTWRITEBYTECODE=1 \
  SBCL=/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  TOPIC_MAPS_REPORT=/private/tmp/topic-maps-slice-9.json \
  /Users/rgb/workspace/topic-maps/scripts/test.sh
```

Valid explicitly qualified date zones are stored/validated but CXTM signals
`:DATE-TIMEZONE-CANONICALIZATION` as unsupported. Bare CTM date zones are not in
the date grammar. DateTime, zone conversion, Variants, nonempty Scope, Reification,
Templates, CTM `*`, cross-document merging and HyperDoc integration remain out of
scope. No server or deployment was used. Slice 10 is not begun.
