# Slice 20B: actual original rejections

Positions count Unicode characters from zero; lines and columns start at one.

| Original CTM | Status | Condition | Code | Position | Line:column |
| --- | --- | --- | --- | ---: | --- |
| `occurrence-double-negative-infinity.ctm` | PASS | `CTM-REJECTION` | `expected-occurrence-value` | 15 | 2:10 |
| `occurrence-double-positive-infinity.ctm` | PASS | `CTM-REJECTION` | `expected-occurrence-value` | 15 | 2:10 |
| `qname-hyphen.ctm` | PASS | `CTM-REJECTION` | `unexpected-token` | 38 | 3:3 |
| `string-unbalanced.ctm` | PASS | `CTM-REJECTION` | `unterminated-string` | 8 | 1:9 |
| `string-unicode.ctm` | PASS | `CTM-REJECTION` | `invalid-unicode-escape` | 11 | 1:12 |
| `string-unicode2.ctm` | PASS | `CTM-REJECTION` | `invalid-unicode-escape` | 15 | 1:16 |
| `topic-id-illegal.ctm` | PASS | `CTM-REJECTION` | `unexpected-character` | 0 | 1:1 |

Reviewed causes, the QName diagnostic trace and the Unicode printed-class qualification are documented in `../../docs/slice-20b-negative-registration.md`. Full actual conditions, repeated calls and accepted in-memory control models are in `current.negative.json`.
