# Slice 20F: the CTM integer literal

CTM 3.4.1 [28]/[30]/[33] maps the exact bare "*" literal to lexical value "*"
and datatype http://psi.topicmaps.org/iso13250/ctm-integer:
https://www.isotopicmaps.org/ctm/ctm.html .
It does not generate a counter value or create a wildcard identity.

The existing number-token scanner and all its delimiters remain unchanged.
Only its exact-star token label changes from excluded-literal to ctm-integer.
The shared read-literal branch consumes that token and returns the literal
value and datatype. Existing Occurrence and Variant operations do the model
work. Existing Template argument dispatch and syntax-literal accept the same
literal token; no new Template productions, TMDM operations, datatype
conversions, counter changes, encodings or string syntax are introduced.

The durable suite uses the existing Slice 20A exercise-case function and the
same discovered original Case Record. It checks the original 18 bytes,
Document IRI, actual model properties, raw object preservation and exact
356-byte CXTM baseline. The explicitly qualified spelling is separately
deserialized and compared with that same original baseline. Other controls
cover plain strings, numeric literals, Variants, existing Template argument
and body paths, token delimiters, wildcard identifiers and nonzero counters.
The suite runs unconditionally after the retained Slice 20E report stage.

Before implementation, a fresh offline SBCL process captured 24 diagnostic
cases. The final suite preserves 22 signatures (class, code, offset, unit,
line, column and source). Two malformed inputs now reach their actual
following syntax errors: "*^^<urn:d>" and "* extra". They still reject, at
character offsets 16 and 17 (line 2, columns 11 and 12), rather than stopping
at the formerly unsupported "*" at offset 15. Two additional controls reject
using the CTM-integer argument as a Topic or as a Name string.

Obsolete Unsupported assertions are explicitly replaced: the old "*." syntax
rejection now tests "*x."; the integer boundary accepts the CTM-integer value;
the occurrence feature boundary permits "*"; the prolog boundary still tests
an unsupported literal, now a triple-quoted string. New regenerated reports
are compared with the previous reports using only the documented label/control
substitutions. Historical report bytes are never rewritten.

Reproduce with an existing SBCL 2.5.4 and a new output directory:

    python3 scripts/validate-slice-20f.py --sbcl /absolute/path/to/sbcl --output /private/tmp/new-slice-20f-report

The committed preimplementation.json is the default diagnostic reference.
For the first run, pass --preimplementation with the captured pre-change file.
The validator uses verified local Store sources and unchanged XML patches,
with no downloads. Fresh SBCL processes have network denied. The full suite
covers TMDM, CTM/CXTM, Include, XML qualification, standalone XTM, CTM/XTM
Mergemap, all retained Slice 20 stages, the new literal suite, Python tests
and the NFC oracle. It rechecks every pinned corpus file and all historical
report hashes. execution.json records actual results rather than predicted
conformance totals; current.literal.json contains controls and Conditions,
current.cxtm.json the actual/baseline streams and current.validation.json
the final shared Case Records.

The normal execution sandbox previously failed on the configured writable-root
symlink /Users/rgb/.nix-profile. These commands use regular require_escalated
approval, without changing that symlink or sandbox configuration. No persistent
Lisp image, HyperDoc content, original source or baseline is changed.
