# Slice 20H: ISO-8859-5

Base: 7f0e40d1558255773357c5ed4fa44bb5184d85e0 (Slice 20G).
This slice adds ISO-8859-5 byte decoding to the existing CTM path.

The existing SBCL 2.5.4 external format was qualified before implementation:
every byte from 00 through FF decodes without replacement, encodes back to the
original byte, and agrees with the independent local Python standard-library
codec. runtime-qualification.json preserves that result. Permanent Lisp tests
check the 256 decoded codepoints against identity mappings for 00–9F and an
explicit expected table for A0–FF. Production code uses SBCL's existing codec;
there are no downloaded tables or new runtime dependencies.

The normative basis is ISO/IEC 13250-6:2010 §§3.2 and 3.6, as published in the
[CTM specification](https://www.isotopicmaps.org/ctm/ctm.html).
Charset identities come from the
[IANA registry](https://www.iana.org/assignments/character-sets);
the expected high-byte table agrees with the
[Unicode ISO-8859-5 mapping](https://www.unicode.org/Public/MAPPINGS/ISO8859/8859-5.TXT).

## Byte and prolog operations

ctm-encoding-kind recognizes only the two supported identities.
Names are case-insensitive; punctuation is significant.

| Identity | Accepted registered names |
| --- | --- |
| UTF-8 | UTF-8, csUTF8 |
| ISO-8859-5 | ISO-8859-5, ISO_8859-5:1988, ISO_8859-5, iso-ir-144, cyrillic, csISOLatinCyrillic |

compatible-ctm-encoding compares these identities, retaining the supplied names
in conflict diagnostics. decode-ctm-octets retains the selection order: external
argument, UTF-8 BOM, initial ASCII encoding declaration, conflict checks, UTF-8
default, then decoding. The strict UTF-8 decoder and IRI unescaping remain byte
identical to the base. The new ISO-8859-5 helper accepts specialized and generic
octet vectors without mutating them. read-prolog accepts the same supported
identity set after byte decoding. Unknown or unsupported charsets still signal
CTM-UNSUPPORTED / unsupported-encoding.

deserialize-file still reads binary data with an explicit Document IRI.
Include and CTM Mergemap still accept only explicitly resolved resource bytes;
the resource implementation, retrieval policy and identifier operations are
unchanged. Tests observe the actual byte-vector object reaching the shared
resource decoder. An externally supplied parent encoding is not inherited by a
resource with no declaration.

## Original and controls

The existing Case Record for ctm/in/encoding-8859-5.ctm remains the registration
unit. The test checks all 42 original bytes and the pinned Document IRI.
The name bytes C0 DE E1 E1 D8 EF decode to Россия.
The original is actually read, checked semantically, canonicalized and compared
byte for byte before PASS is recorded. The expected byte count is read from the
pinned baseline. Topic handles, identifiers and map state remain unchanged by
canonicalization. A Unicode-string control produces the same baseline.

Permanent tests cover the six ISO names against all compatible external
arguments, mixed case, external-only input, ASCII, every A0–FF character in a
Name, all combinations of the two UTF-8 aliases with/without a BOM, and already
decoded Unicode strings. Include and Mergemap check both byte-vector forms,
child/parent Document IRIs and their different existing wildcard-counter rules.

The negative matrix checks conflicting declarations/BOM/external arguments,
unsupported ISO-8859-1, unknown and unregistered names, strict UTF-8 default,
misplaced/repeated/unquoted declarations, invalid versions, and child-resource
diagnostic context. Decoder spies prove conflicts and unsupported selections
fail before either codec is called.

Positions remain explicit: encoding preflight and UTF-8 failures use zero-based
byte offsets with no character line/column; lexer/prolog errors use zero-based
Unicode character offsets and one-based line/column. Paired ISO/UTF-8 fixtures
with Cyrillic text before an illegal character preserve the original byte
offset separately; only the ISO single-byte offsets coincide. Examples include
encoding-conflict at byte 14 (BOM/declaration), byte 0 (external/BOM), and byte
11 (external/declaration); invalid-utf8 at byte 10 for undeclared ISO input;
misplaced-encoding at character 23 for the repeated declaration.
current.encoding.json records every actual Condition, code, source, position,
unit and resource context.

Seven old Unsupported assertions now use still-unsupported ISO-8859-1 in newly
generated reports. They retain their Condition class, code and positions.
The validator permits only those exact fixture/message changes and one renamed
check label when comparing previous report contents; archived bytes remain
untouched. The original negative BOM-conflict contract still uses ISO-8859-1
and is unchanged.

## Reproduction and acceptance

Run the existing complete offline driver, with an unused report output directory:

    python3 scripts/validate-slice-20h.py \
      --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
      --output reports/slice-20h-rerun

The validator reuses pinned local XML sources, existing patches and the existing
test harness. Fresh SBCL processes disable user/system init files; XML, XTM and
the full regression execute under sandbox-exec with deny network*.
It checks retained TMDM/CTM/CXTM, Include, Mergemap, XTM identity/Mergemap,
Slices 20A–20G, Python tests and the NFC oracle. The encoding ASDF test system is
actually called by scripts/fresh-sbcl.lisp; its report is written only after
the tests finish.

Acceptance requires only this one NOT-RUN-to-PASS transition:
CTM 261 PASS / 4 FAIL / 8 NOT-RUN to 262 PASS / 4 FAIL / 7 NOT-RUN.
The separate XTM corpus must remain 6 PASS / 0 FAIL / 118 NOT-RUN.
All four existing CTM failure records and their actual CXTM must remain exact.
The validator verifies every pinned corpus size/hash, every prior report hash,
and all protected base files. It saves complete logs, stage reports,
actual/encoding-8859-5.ctm.cxtm, integrity hashes and execution.json.
It does not rebuild a Nix closure or load persistent Lisp images.

The managed sandbox initially fails before command execution because its
configured writable root /Users/rgb/.nix-profile is a symlink:
“writable root /Users/rgb/.nix-profile contains symlink component
/Users/rgb/.nix-profile; symlinked writable roots are not supported.”
Execution uses regular approved require_escalated calls with canonical Store
runtime paths. The symlink and sandbox configuration are unchanged; regression
subprocesses enforce the explicit network denial.
