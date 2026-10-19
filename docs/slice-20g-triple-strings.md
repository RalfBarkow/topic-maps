# Slice 20G: Triple-Quoted Strings

CTM 3.4.1 [37]/[39]/[40] and 3.4.2 [41]-[43] define the delimiters and shared
String escapes: https://www.isotopicmaps.org/ctm/ctm.html .
The pinned corpus retains its historical 2010-03-31 draft qualification.

Only src/ctm/lexer.lisp changes production behavior. next-token consumes the
first quote, and read-ctm-string detects and consumes two more opening quotes.
In Triple mode, one or two raw quotes are content; three consecutive raw
quotes close the token. Escaped quotes and quotes produced by Unicode escapes
remain content. The lexer consumes exactly the three closing quotes, leaving
any extra characters for the existing token/parser diagnostics. There is no
dedenting, whitespace trimming, line-ending conversion or new Unicode policy.

The same existing escape branch handles backslash, quote, n/r/t, four-digit
lowercase-u and six-digit uppercase-U escapes, including scalar validation.
Missing delimiters use ctm-rejection / unterminated-string at the opening
quote. Invalid escapes retain the existing error codes and character positions.
Occurrences, Names, Variants, qualified literals and existing Template
arguments/body strings already consume the same String token. Neither Reader
operations, TMDM/CXTM nor the Template grammar require changes.

The new ASDF test stage runs unconditionally after Slice 20F. It reuses the
Slice 20A exercise-case function and the same discovered Case Records for
exactly four originals: occurrence-string-triple, occurrence-string-triple2,
unicode-escape-u4-triple-string and unicode-escape-u6-triple-string.
Their baselines contain 367, 370, 331 and 331 bytes. Each actual Original
comparison is accompanied by a separately parsed ordinary-string control,
plus explicit model properties, stable Document IRI, raw map/handle state
and source immutability checks.

Counterprobes cover empty strings, quote runs, escaped terminal quotes,
Unicode, LF/CR/CRLF, whitespace and syntax-looking content in all three
value contexts. CR fixtures construct Return explicitly so source editing
cannot normalize them. Other controls cover typed values, the existing
Template String path, exact closing-token boundaries, malformed/unclosed
Triple Strings and unchanged ordinary-string diagnostics captured before
implementation in a fresh offline SBCL.

Only obsolete Unsupported assertions are updated in retained tests: the
identity and existing Template String paths now assert their actual Name
values; the prolog and CTM-integer boundary controls now reject unclosed
Triple Strings. Regenerated reports allow only these named label/control
substitutions. All archived report bytes remain unchanged.

Reproduce with an existing SBCL 2.5.4 and a new output directory:

    python3 scripts/validate-slice-20g.py --sbcl /absolute/path/to/sbcl --output /private/tmp/new-slice-20g-report

The committed preimplementation.json is the default diagnostic reference.
For the initial run, pass --preimplementation with the pre-change capture.
The validator uses verified local Store sources and unchanged XML patches
without downloads. Fresh SBCL processes have network denied. The complete
suite covers TMDM, CTM/CXTM, Include, XML qualification, standalone XTM,
CTM/XTM Mergemap, prior Slice 20 stages, Python tests and the NFC oracle.
Every pinned source/baseline and every historical report hash is rechecked.
execution.json records observed results; current.triple.json stores controls
and Conditions, current.cxtm.json actual/baseline streams and
current.validation.json the final shared Case Records.

The normal tool sandbox previously failed on the writable-root symlink
/Users/rgb/.nix-profile. Regular require_escalated approval is used without
changing that symlink or the sandbox configuration. No persistent Lisp image,
HyperDoc content, original source, baseline, push or deployment is involved.
