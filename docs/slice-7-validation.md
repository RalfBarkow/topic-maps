# Slice 7 — Integer Occurrences: validation evidence

Repository: `/Users/rgb/workspace/topic-maps`.
Observed initial branch: `codex/ctm-slice-6`, clean working tree, HEAD
`3924d1eac5a070fe5a6a26683e23ac338793f544` (the requested base).
Created `codex/ctm-slice-7` from that verified commit. Corpus and reference files
remain unchanged at pin `cd165b150176c1d6842b37be9cc9051b40d4996b`.

## Normative interpretation and implemented boundary

Consulted the published [CTM §3.4.1](https://www.isotopicmaps.org/ctm/ctm.html),
[TMDM §§4.3–4.4, 5.6, 6.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/),
[CXTM §§3.16, 4.2–4.3, 4.9](https://www.isotopicmaps.org/cxtm/cxtm.html) and
[XML Schema Part 2 §§3.3.13.1–3.3.13.2, 4.3.6](https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/#integer).
The full interpretation, original sources, actual object graph and inspection
example are in `reading-integer-occurrences.md`.

Three different contracts are retained:

1. The reader represents an **unquoted integer value** with a canonical lexical
   string. Its lexer token and original CTM source retain the source spelling.
   This early representation is a documented implementation policy under CTM's
   value mapping, not a claim that CTM explicitly requires early canonicalization.
   A qualified **quoted string** retains its escape-decoded value instead.
2. TMDM stores a string plus a separate datatype locator. Its API does not
   normalize integer strings. Occurrence equality/merging uses stored string
   equality and the other §5.6 properties; numeric equivalence or equal XML
   does not replace those rules.
3. CXTM formats xsd:integer output canonically, without changing those model
   values or retained merge handles. Occurrence sorting compares the original
   stored strings (§§4.3/4.9), not numeric values or reformatted output strings.

Canonical formatting is character-based, removing plus signs/leading zeros and
using `0` for positive/negative zero. It has no machine-word overflow boundary.
XML whitespace at the ends of a qualified integer is accepted for XSD datatype
interpretation, retained in TMDM, and removed in canonical output. Internal
whitespace and non-ASCII decimal digits are rejected for xsd:integer.

This explicitly distinguishes cases where bare `001`/`+1`/`1` already have the
same stored string from quoted `"001"`/`"1"`, whose strings remain different.
The latter produce equal canonical value elements but remain separate items.
A dedicated test also shows two separate maps with equal CXTM and different
stored integer strings. No XML-based equality or generic numeric merging exists.

## Selected original CTM/CXTM contracts

All sources and original baselines were read before implementation. All six
use the existing deterministic absolute Document IRI, also as CXTM Base Locator.
Actual UTF-8 bytes are compared directly against original baseline bytes, with
no trimming, XML reparsing, baseline rewriting or numeric preprocessing.

All cases produce one Topic Map, no Names/Associations and no datatype Topic.
Local Topic identities are only `DocumentIRI#identifier` Item Identifiers;
SI/SL sets and Occurrence Item Identifiers are empty. The datatype is always
`http://www.w3.org/2001/XMLSchema#integer`, never a Type Topic.

| Original source | Actual stored values, source order | Items/references | Byte-exact result |
| --- | --- | --- | --- |
| `ctm/in/occurrence-integer.ctm` | `"1"` | 2 Topics, 1 Occurrence; Parent EQ topic, Type EQ occtype | PASS, 351 bytes |
| `ctm/in/occurrence-integer2.ctm` | `"1"` | same; `1.` leaves the topic terminator | PASS, 351 bytes |
| `ctm/in/occurrence-integer-plus-sign.ctm` | `"1"` | same; original `+1` | PASS, 351 bytes |
| `ctm/in/occurrence-integer-minus-sign.ctm` | `"-1"` | same | PASS, 352 bytes |
| `ctm/in/occurrence-integer-leading-zeros.ctm` | `"1", "1", "-1", "100", "0", "0", "0"` | 8 Topics, 7 Occurrences; same Parent, Types EQ o1…o7 | PASS, 1,741 bytes |
| `ctm/in/occurrence-explicit-datatype2.ctm` | `"42"` | 2 Topics, 1 Occurrence; Parent EQ topic, Type EQ occtype | PASS, 352 bytes |

The leading-zero case's canonical occurrence order is o3, o5, o6, o7, o1, o2,
o4. The equal value strings are separated by Type, with canonical Type Topics
1–7 and owner Topic 8. The five simpler maps use Type Topic 1 and owner Topic 2.

| Imported contracts | PASS | FAIL | UNSUPPORTED | NOT-RUN |
| --- | ---: | ---: | ---: | ---: |
| All 273 cases | 42 | 0 | 0 | 231 |
| Positive CXTM contracts | 39 | 0 | 0 | 192 |
| Negative CTM contracts | 3 | 0 | 0 | 39 |

Only the six selected contracts changed NOT-RUN → PASS. The previous 33 positive
case records/outputs and all three specific prefix rejections are unchanged.
The existing identity, merge, Association, Occurrence and prefix object-observation
records match Slice 6 exactly. No unexecuted imported contract is inferred to
pass or to be unsupported from other tests.

## Fresh offline regression evidence

Each suite ran again in a fresh SBCL process, ignoring user/system initialization
and inherited ASDF source configuration. `sandbox-exec` denied network access.
The 2.4.10 run used an independently copied checkout under `/private/tmp`.

| Suite | SBCL 2.5.4 PASS | SBCL 2.4.10, relocated PASS |
| --- | ---: | ---: |
| Foundation | 54 | 54 |
| Topic Identity | 123 | 123 |
| Topic Merging | 646 | 646 |
| Associations/Roles | 657 | 657 |
| Retained CXTM | 445 | 445 |
| Occurrences | 1,101 | 1,101 |
| Prefix/explicit datatypes | 150 | 150 |
| Integer checks | 665 | 665 |
| Total Lisp checks | 3,841 | 3,841 |
| Python infrastructure tests | 2 | 2 |
| Independent NFC oracle comparisons | 16,294 | 16,294 |
| Independent integer arithmetic probes | 143 | 143 |
| Original positive CXTM byte comparisons | 39 | 39 |

Final failures: **0**. All eight report pairs are byte-identical across runtimes
and relocation. Public DESCRIBE/serialization inspection was independently
executed under network denial and passed. The 143 numeric probes include
positive/negative 10,000-digit integers and XML whitespace. Python arithmetic
provides an independent implementation of the numeric-to-string result.
The new integer tests also exercise malformed values, source diagnostics,
explicit/implicit datatypes, lexical equality, retained handles after Parent/Type
merging, datatype/type distinctions, ordering permutations and nonmutation.

Previously unsupported expectations were adapted one-for-one: the `42.`
unsupported fixture now uses excluded `42.5.`; the private unsupported integer
fixture now uses Decimal; the qualified integer CXTM assertion now requires
successful canonical output instead of an unsupported condition. Retained suite
totals remain 1,101 and 150. The original 445 canonical check labels/results are
unchanged. No original CTM source or expected XML was altered.

Evidence in `reports/slice-7/`: raw process logs, `execution.json` with commands,
runtime versions/paths, exit codes and artifact SHA-256 hashes; eight reports;
all 39 actual CXTM byte files; and `describe.log`. The combined CXTM report's
2,361 checks are retained CXTM + Occurrence + prefix + integer checks, not an
additional suite to add to the Lisp total. Development fixture syntax/layout
corrections precede these final successful runs.

## Reproduction

With the installed runtimes and Python UCD 15.0/15.1:

```sh
python3 /Users/rgb/workspace/topic-maps/scripts/validate-slice-7.py \
  --sbcl-254 /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --sbcl-2410 /nix/store/y96nx8571mpdvjd40krkdim2av0in972-sbcl-2.4.10/bin/sbcl \
  --output /private/tmp/topic-maps-slice-7-reproduction
```

The script verifies runtime versions, applies OS network denial, runs both fresh
suites, relocates the second checkout, compares reports and previous records,
checks original baseline bytes, executes the documented inspection and records
the evidence. It provisions no software, changes no corpus and makes no commit.

Single fresh offline run:

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /usr/bin/env PYTHONDONTWRITEBYTECODE=1 \
  SBCL=/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  TOPIC_MAPS_REPORT=/private/tmp/topic-maps-slice-7.json \
  /Users/rgb/workspace/topic-maps/scripts/test.sh
```

## Implementation and remaining limits

`src/ctm/lexer.lisp` contains the single numeric token path and the relocated
existing excluded-literal recognizer. `src/ctm/reader.lisp` maps integer token
values and qualified strings to the existing model. `src/tmdm/integers.lisp`
provides pure lexical helpers; `occurrences.lisp` validates integer input before
mutation without rewriting it. CXTM adds integer validation/output but keeps
its existing stored-string comparator. `tests/ctm-integers.lisp` and independent
Python checking cover the six selected contracts and direct semantics.

Decimal, Date, DateTime, Variants, nonempty Scope, Reification, Templates,
cross-document merging and HyperDoc integration remain excluded. No `*` literal
counter semantics or derived-integer subtype conversion was introduced; none
is required by the six selected cases. General locator/Unicode/root-LF limits
remain as documented in preceding slices. No server was started or deployed.

No blocking standard/corpus conflict was observed for this slice. The reader's
early bare-integer value-representation policy is explicitly documented, while
qualified string equality and normative string-based sort rules are retained.
Recommendation: **PASS for Slice 7's bounded scope**, await review before any
further slice.
