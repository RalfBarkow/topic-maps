# Slice 19D0B — CXML encoding qualification

Base: `ec3f21e45c46849a6bb674194b6f7cc75b67bba1`.
Nixpkgs remains `50ab793786d9de88ee30ec4e4c24fb4236fc2674`.
Qualification is **PASS** with the local patches and mandatory byte boundary.
No XTM deserializer or XTM contract is introduced.

## Normative decisions

The checked sources are [XML 1.0 Fifth Edition §2.2, §2.11, §4.3.3](https://www.w3.org/TR/2008/REC-xml-20081126/),
[Unicode 16.0 §3.9.2–3, Table 3-7 and §3.10](https://www.unicode.org/versions/Unicode16.0.0/core-spec/chapter-3/),
[RFC 2781 §2.2, §3.3, §4](https://www.rfc-editor.org/rfc/rfc2781.html), and
[RFC 3629 §3–4](https://www.rfc-editor.org/rfc/rfc3629.html).

XML requires UTF-8 and UTF-16 support and accepts supplementary characters in
its Char range, including currently unassigned code points. Generic UTF-16
requires a BOM. UTF-16LE/BE are distinct encoding schemes: these original inputs
have an XML declaration that identifies their byte order. They are sufficiently
labeled. XML Appendix F.1 describes provisional signature detection; it is
informative, while declaration consistency and illegal-sequence rejection in
§4.3.3 are normative. Missing labels and contradictory declarations are errors.
XML line-end normalization also applies to UTF-16.

Unicode UTF-16 pairs a high surrogate with a low surrogate; isolated units are
invalid. UTF-8 must use its shortest form, valid continuation bytes and scalar
range, excluding encoded surrogates. Incomplete sequences require more input
until EOF, then fail. RFC 2781 distinguishes the explicit endian labels from
generic UTF-16; RFC 3629 corroborates the UTF-8 byte ranges. These encoding
rules do not change the project's Unicode NFC tables or add a Unicode library.

## All eight original failures

The exact Unicode source text, **complete input octets in hex**, byte count,
SHA-256, detected encoding, before/after result, condition, diagnostic and
applicable clauses for each case are in
`reports/slice-19d0b/original-failures.json`. The source bytes are reconstructed
independently with Python's standard codecs and passed directly to CXML.
Diagnostics are observed parser messages; line/column reports are not promoted
to exact byte offsets.

| Original test | Bytes | Originally detected | Original result | Required/patched result | Cause |
|---|---:|---|---|---|---|
| `utf16le-bom:astral` | 114 | UTF-16 LE | rejects D83E DD8A | accepts `Grüße 水 🦊` | A |
| `utf16be-bom:astral` | 114 | UTF-16 BE | rejects D83E DD8A | accepts `Grüße 水 🦊` | A |
| `utf16le-explicit-no-bom:bmp` | 110 | UTF-8 | malformed markup | accepts `Grüße 水` | B |
| `utf16le-explicit-no-bom:astral` | 116 | UTF-8 | malformed markup | accepts `Grüße 水 🦊` | B + A |
| `utf16be-explicit-no-bom:bmp` | 110 | UTF-8 | NUL in markup | accepts `Grüße 水` | B |
| `utf16be-explicit-no-bom:astral` | 116 | UTF-8 | NUL in markup | accepts `Grüße 水 🦊` | B + A |
| `utf16-bom-without-declaration:astral` | 22 | UTF-16 LE | rejects D83E DD8A | accepts `水🦊` | A |
| `invalid-utf8` | 9 | UTF-8 | accepts `C3 28` as U+00E8 | rejects invalid continuation | C |

**A — closure-common defect.** The endian-specific `decode-sequence` methods
in `encodings.lisp` check the first code unit `x` again where they must check
the second, `y` (original lines 172/209). Valid supplementary content therefore
fails. Fixing `x` to `y` preserves the existing code-point computation.

**B — two implementation gaps, not incorrect expectations.** In
`closure-common/xstream.lisp`, `figure-encoding` recognizes only BOM-based
UTF-16. It defaults the four correctly labeled inputs to UTF-8 before CXML can
read their declarations. CXML's `setup-encoding` additionally lacks explicit
LE/BE handling, warns for generic UTF-16 and does not fully check consistency.
The patch recognizes the four-byte XML signatures provisionally, preserves
preread bytes and records the detection reason in the existing stream plist.
`setup-encoding` then checks the actual declaration. A signature alone does not
authorize generic BOM-less UTF-16, a missing label or a mismatched label.
The existing `set-full-speed` transition also checks that a declaration was
actually processed, so a leading ordinary processing instruction cannot bypass it.

**C — closure-common defect.** The UTF-8 `decode-sequence` method masks tail
bytes without validating their prefix. The patch validates continuation bytes,
shortest forms, the maximum scalar and permitted leading bytes; obsolete
five/six-byte forms fail. Incomplete UTF-8/UTF-16 sequences fail at EOF rather
than being silently dropped or repeatedly retried. Both existing UTF-16
decoders also receive their protocol-required CR/CRLF handling.

The four endian-specific, BOM-less inputs are valid supported forms, though
XML's mandatory UTF-8/UTF-16 support alone does not require these related
schemes. **No original expectation was weakened or replaced.** In particular,
the BOM-less tests were not changed to expect rejection. Their data includes
`3c 00 3f 00` / `00 3c 00 3f` followed by the appropriate encoding declaration.

## Patch and source provenance

`patches/closure-common-19d0b.patch` changes only `encodings.lisp` and
`xstream.lisp`. `patches/cxml-19d0b.patch` changes only `xml/xml-parse.lisp`.
They modify the existing decoder and declaration paths; they do not introduce
a second parser, decoder framework or Unicode data set.

The original archives, seven Nix source directories and their recursive
source hashes remain unchanged. `flake.lock` and the corpus remain unchanged.
The Nix source environment now also records the local patch profile and
SHA-256 of both patch files. No further dependency was downloaded.

`scripts/prepare-cxml.py`:

1. Evaluates the existing pinned Nix source environment offline.
2. Verifies all seven original source hashes before writing outputs.
3. Copies only the two affected packages into a **new** caller-selected directory.
4. Checks local patch hashes against the Nix manifest and applies them with
   the existing `patch` tool, with zero fuzz and no offsets.
5. Checks the exact set of changed files; records original and resulting
   file hashes and the effective ASDF registry in `provenance.json`.

It never writes into `/nix/store`, overwrites an existing output directory or
retrieves a resource. Two independent copies produce identical patched file
hashes. Effective paths in recorded validation runs belonged to those temporary
execution contexts; they are not persistent addresses. Reproduce them with the
preparation command rather than reusing expired temporary paths.

## Binding public call contract

The optional ASDF system **`topic-maps/xml`** depends only on CXML, not on CTM,
TMDM or HyperDoc. Future XTM deserialization **must call
`topic-maps.xml:parse-octets`**, not bare `cxml:parse-octets`.

The function accepts a specialized octet vector and a SAX handler, and returns
the handler's SAX result without replacing its object identity. It:

* Refuses libraries without the required local patch ABI markers.
* Fixes namespace processing on and gives the caller no resolver/DTD overrides.
* Wraps the receiver in an existing CXML SAX proxy that rejects every DOCTYPE
  before forwarding it. Even a NIL/permissive receiver cannot bypass the guard.
* Disallows internal subsets and uses a resolver that **signals**
  `external-resource-forbidden`; returning NIL is forbidden.
* Disables catalog lookup and binds a fresh DTD cache for each parse.

The ABI markers protect against accidental loading of pristine dependencies;
they are not an integrity defense against arbitrary Lisp code rewriting loaded
functions. Source and patch integrity is checked during preparation.
The underlying library's unsafe entry points are not made globally safe.
The public boundary offers no already-decoded-string, filename, transport
encoding or arbitrary parser-option interface.

## Reproduction and inspection

```sh
cd /Users/rgb/workspace/topic-maps
xml_sources=$(mktemp -d /tmp/topic-maps-xml.XXXXXX)
export CL_SOURCE_REGISTRY="$(python3 scripts/prepare-cxml.py \
  --directory "$xml_sources/patched" --registry)"
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --noinform --no-sysinit --no-userinit --script tests/cxml-probe.lisp

python3 scripts/validate-cxml-19d0b.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

In a fresh Lisp process with that registry:

```lisp
(require :asdf)
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/xml")
(let ((bytes (make-array 4 :element-type '(unsigned-byte 8)
                          :initial-contents '(60 114 47 62)))) ; <r/>
  (describe (topic-maps.xml:parse-octets bytes (cxml-xmls:make-xmls-builder))))
```

The Nix manifest's `sourceRegistry` still denotes pristine upstream sources;
the preparation step is mandatory for this API. Merely entering the old
DevShell or loading unpatched CXML does not activate the patches. A fresh-process
counterprobe loads precisely that unpatched environment and proves that the
public boundary refuses it before parsing. This source-overlay workflow reuses
the existing Nix/ASDF provisioning without realizing an uncached toolchain.

## Validation evidence

`reports/slice-19d0b/execution.json` records source/patch hashes, runtime and
timestamps, independent source-copy reproduction, original and patched runs,
the fresh unpatched-boundary counterprobe and the complete retained regression.

* Original test program from the base commit, pristine sources: **50 PASS, 8 FAIL**.
* **Unmodified original program**, patched sources: **58 PASS, 0 FAIL**.
* Original 58 expectations through the binding public boundary, plus 88 focused
  regressions: **146 PASS, 0 FAIL**, repeated in two fresh SBCL 2.5.4 processes.
* Additional cases cover malformed/overlong/truncated UTF-8, invalid UTF-16
  units, Unicode scalar boundaries, partial-input/EOF behavior, large refills,
  line ends, missing/conflicting declarations, namespaces and the fixed API.
* All external DTD/entity rejection checks and the NIL-resolver fallback
  counterprobe remain. The fallback is intercepted before OPEN, so sandbox I/O
  denial is never misreported as successful resolver refusal.
* Full existing regression: **12,100 Lisp checks**, **2 Python tests** and
  **16,294 NFC oracle comparisons** pass. All 24 retained JSON reports are
  byte-identical to Slice 19C. CTM stays **204 PASS, 4 known FAIL, 65 NOT-RUN**.

All Lisp observations run with network access denied. Nix evaluation uses
`--offline`; patching consumes already materialized sources. The complete Nix
toolchain/DevShell offline rebuild remains **NOT-RUN**. This is an offline
source-patch/ASDF qualification using existing Nix runtime artifacts, not a claim
that every Nix artifact was rebuilt offline or that all of XML is conformant.
No XTM PASS, push, deployment, HyperDoc modification or persistent-image load.
