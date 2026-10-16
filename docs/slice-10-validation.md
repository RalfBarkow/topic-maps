# Slice 10 — DateTime Occurrences: validation

Base: `2ad41cd1a945a4ce97824464de40646bb899259e`, clean
`codex/ctm-slice-9`; created `codex/ctm-slice-10` directly from that commit.
No HyperDoc change, server, deployment or Slice 11 work.

The normative investigation was recorded before implementation in
`reading-datetime-occurrences.md`. CTM 3.4.1, TMDM 4.3–4.4/5.6/6.5,
CXTM 3.16/4.9, XSD Second Edition 3.2.7.1–3.2.7.3 and D.1 apply.
Two normative baseline discrepancies are retained explicitly:

| Original case | Actual normative-subset result | Contract status |
|---|---|---|
| occurrence-datetime.ctm | 1976-09-19T12:01:01; 370 exact CXTM bytes | PASS |
| occurrence-datetime2.ctm | 1976-09-19T12:02:00; baseline retains :60 | **FAIL**, documented D.1 following-minute interpretation |
| occurrence-datetime-fractional.ctm | 2011-01-01T00:00:00.001; 677 exact CXTM bytes | PASS |
| occurrence-datetime-timezone.ctm | 2011-01-01T00:00:00Z; 674 exact CXTM bytes | PASS |
| occurrence-datetime-timezone2.ctm | Conversion to 2010-12-31T22:00:00Z required; not implemented | NOT-RUN; specific unsupported partial-read probe is separate |

Seconds 60 are lexically allowed in XSD 1.0. D.1's noncandidate-day rule means
September 19 does not justify an unchanged canonical :60. The implementation
follows that value interpretation and exposes the mismatch, rather than altering
the baseline. Candidate-day UTC leap seconds at 23:59:60 are supported; ambiguous
local leap contexts remain explicitly unsupported. No actual IERS-history
validation is claimed. No XSD 1.1 leap-second prohibition is imported.

Bare supported literals use the established canonical stored-string policy.
Qualified/API strings retain their valid lexical strings. Same-map equality and
merging remain based on stored properties; equal canonical XML does not merge
distinct lexical values. Zero offsets and Z produce Z; absent timezone stays
absent. Fractions and year rollover use character arithmetic; Date validation
and its qualified BCE interpretation are reused. No floating point, OS calendar
or local timezone is used. Serialization never mutates objects or retained handles.

## Full regression results per runtime

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
| DateTimes | 215 | 215 |
| **Total assertions** | **6577** | **6577** |
| Regression assertion failures | 0 | 0 |
| Python infrastructure tests | 2 | 2 |
| Independent NFC comparisons | 16294 | 16294 |
| Independent Integer / Decimal / Date probes | 143 / 157 / 396 | 143 / 157 / 396 |
| Independent DateTime probes | 45 | 45 |

The known original CXTM contract FAIL is not erased by green regression
assertions. `validation.json` counts imported outcomes; `cxtm.json` additionally
has explicit contractCounts. Local assertion counters are separately identified.

| Imported contracts | PASS | FAIL | UNSUPPORTED | NOT-RUN |
|---|---:|---:|---:|---:|
| Positive CXTM, 231 total | 54 | 1 | 0 | 176 |
| Negative CTM, 42 total | 8 | 0 | 0 | 34 |
| **All 273** | **62** | **1** | **0** | **210** |

All previous 51 positive outputs and model observations, and eight negative
contracts are retained. One previous NOT-RUN contract is now FAIL, three become
PASS. Nonzero-offset original remains NOT-RUN, even though a separate partial
read confirms the specific unsupported condition. Recognized unsupported
constructs are distinct from unexecuted imported outcomes and baseline conflicts.

Both complete runs use fresh SBCL processes, ignore inherited ASDF configuration
and user/system initialization, and run under sandbox-exec deny-network policy.
The 2.4.10 run uses a copied checkout without .git. All eleven generated report
pairs are byte-identical. Corpus, baselines, locks and existing references are
unchanged. Original input bytes including the datetime2 BOM are preserved.
The public Lisp DESCRIBE example executes successfully under the same policy.

DateTime assertions cover malformed hours/minutes/seconds/fractions/zones,
24:00:00 and Gregorian rollover, no year zero, negative and extended years,
10,000-digit fractions/years, explicit/bare/API values, real Parent/Type object
references, datatype locators without new Topics, duplicate replacement and
identifier union, retained handles, construction order, lexical sorting and
purity. Old exclusion fixtures are adapted one-for-one to still-excluded offsets
or the now-specific invalid DateTime rejection; old suite counts are preserved.
Initial development failures (test-form delimiter, obsolete excluded fixture,
empty fraction validation, QName separator in a new fixture) were corrected
before the final full runs; they are not conflated with the known baseline FAIL.

## Reproduction

```sh
python3 scripts/validate-slice-10.py \
  --sbcl-254 /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --sbcl-2410 /nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl \
  --output /private/tmp/topic-maps-slice-10-reproduction
```

Final committed evidence is under `reports/slice-10`; execution.json records
versions, exact commands/exit codes, result totals, report and actual-XML hashes.
The driver verifies both retained outputs and the known mismatch explicitly;
its success means implementation checks PASS with one disclosed imported FAIL,
not complete upstream-suite or ISO conformity.

Nonzero DateTime offset conversion, Date timezone canonicalization, ambiguous
local leap contexts, CTM *, Variants, nonempty Scope, Reification, Templates,
cross-document merging and HyperDoc integration remain outside this slice.
