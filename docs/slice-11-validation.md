# Slice 11 — DateTime Timezone Canonicalization: validation

Base `8741d155d948c7317945eee423a977940cad995e`, verified clean on
`codex/ctm-slice-10`; branch `codex/ctm-slice-11` created directly from it.
No HyperDoc change, push, server, deployment or Slice 12 work.

## Normative decisions and implementation

See [Reading DateTime Timezone Canonicalization](reading-datetime-timezones.md)
for the preimplementation normative decisions and executed inspection example.
CXTM 3.16, XSD Second Edition 3.2.7.1–3.2.7.4, TMDM 4.3–4.4/5.6/6.5 apply;
CXTM 4.3/4.9 ordering remains comparison of stored property strings.
No XSD instant-order API or different TMDM equality is introduced.

`canonical-datetime-lexical-form` reuses `datetime-parts`/Date validation;
`datetime-offset-minutes` parses only an already validated short offset.
`previous-datetime-date` reuses the Date validator for month length, and
`previous-datetime-year` inverts the existing character-based next-year helper.
Only hour/minute arithmetic uses small integers. Years and fractional digits
remain character sequences. The public canonical helper returns a derived
string and status; reader/CXTM retain specific invalid/unsupported conditions.

All offsets from -14:00 through +14:00 are tested minute by minute. Z, +00:00,
-00:00 and absence are tested separately. Calendar probes cover leap centuries,
28/29/30/31-day months, 24:00:00, year changes, 10000-digit years and fractions.
Nonzero-offset BCE day rollover and second-60 contexts remain explicitly
unsupported; inherited zero/absent-zone leap handling is unchanged.

Qualified strings/API values retain spelling. Bare CTM literals retain the
accepted canonical stored-string policy. Type/Parent stay Topic references;
the datatype is the locator `http://www.w3.org/2001/XMLSchema#dateTime`.
Pure CXTM generation changes neither live objects nor retained merge handles.
Distinct stored strings can produce equal CXTM without becoming equal TMDM
Occurrences. Actual duplicate merging still uses the stored properties.

## Original timezone2 evidence

The original source is unchanged:

```ctm
datetime - "datetime" .

some-topic - "some topic" ;
  datetime: 2011-01-01T00:00:00+02:00
.
```

Document IRI / Base Locator:
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/occurrence-datetime-timezone2.ctm`.

Actual model: three Topics (local datetime, local some-topic, standard name-type
Topic), two Names, one Occurrence, no Associations. The Occurrence's Parent is
the some-topic object and Type is the datetime object. Stored bare Value:
`2010-12-31T22:00:00Z`; Datatype: xsd:dateTime locator; Item Identifiers: empty.

Actual CXTM contains `<value>2010-12-31T22:00:00Z</value>` (674 UTF-8 bytes).
Unmodified expected CXTM contains `<value>2011-01-01T00:00:00+02:00</value>`
(679 bytes). First differing zero-based byte: 382. Imported result: **FAIL**.
The independent UTC/model assertions pass. The comparison is genuinely run;
there is no filename-specific implementation or changed baseline.

The original datetime2 result remains 370 actual/expected bytes, differing at
byte 232: actual `1976-09-19T12:02:00`, baseline `1976-09-19T12:01:60`.
The Slice 10 D.1 interpretation and normative qualification are retained.

## Full execution results

Both runtimes ran fresh, with `--no-sysinit --no-userinit`, no inherited ASDF
registry and macOS sandbox network denial. The 2.4.10 run used a relocated
checkout without .git. Every group below passed in both runs.

| Group | Checks per runtime |
|---|---:|
| Foundation | 54 |
| Topic identity | 123 |
| Topic merging | 646 |
| Associations and Roles | 657 |
| Retained CXTM assertions | 445 |
| Occurrences | 1101 |
| Prefix/datatype | 150 |
| Integer | 665 |
| Decimal | 715 |
| Date | 1806 |
| DateTime | 217 |
| DateTime timezones | 1944 |
| **Total Lisp assertions** | **8523** |

Additionally per run: two Python integrity tests, 16294 Unicode NFC oracle
comparisons; 143 Integer, 157 Decimal, 396 Date, 45 DateTime and 1774 timezone
oracle probes. The timezone oracle uses arbitrary Python integers/calendar
arithmetic and an additional fixed-UTC datetime cross-check in its CE range;
no implicit local timezone or floating-point fractions.

All twelve JSON report pairs are byte-identical. All 55 previous canonical
outputs and all four previous DateTime object observations remain unchanged;
all previous 54 positive matches and eight negative passes remain PASS.
Original corpus and reference bytes are unchanged. The documented Lisp example
was executed successfully offline; its output is in `describe.log`.

Imported statuses: **62 PASS, 2 FAIL, 0 UNSUPPORTED, 209 NOT-RUN** (273 total).
Of 56 executed positive CXTM contracts, 54 match byte-for-byte and two have the
documented normative discrepancy. The only imported status transition from
Slice 10 is timezone2: NOT-RUN → FAIL. Unsupported helper probes are independent
semantic tests and do not change unexecuted imported statuses.

Existing assertions expecting ordinary offsets to be unsupported were adapted
to supported-offset tests and remaining leap-context rejection fixtures.
Initial development runs caught two missing form delimiters and those obsolete
unsupported expectations; the final complete runs have no assertion failures.

## Reproduction and evidence

```sh
python3 scripts/validate-slice-11.py \
  --sbcl-254 /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --sbcl-2410 /nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl \
  --output /private/tmp/topic-maps-slice-11-reproduction
```

Committed evidence: `reports/slice-11/execution.json` records commands, exit
codes, runtime versions, counts and artifact hashes; the directory also contains
both logs, twelve deterministic reports, actual XML for all 56 comparisons and
the inspection output. The validator's PASS means successful implementation
assertions with two explicitly retained imported FAILs, not full ISO conformity.

Remaining exclusions: Date timezone canonicalization, nonzero-offset BCE day
rollover and leap-second canonicalization, CTM *, Variants, nonempty Scope,
Reification, Templates, cross-document merging and HyperDoc integration.
