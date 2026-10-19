# Slice 20A: actual original comparisons

| Original CTM | Group | Status | CXTM bytes |
| --- | --- | --- | ---: |
| `comment-ml.ctm` | comments | PASS | 207 |
| `comment-ml-nested.ctm` | comments | PASS | 207 |
| `comment-ml-nested2.ctm` | comments | PASS | 207 |
| `comment-sl.ctm` | comments | PASS | 114 |
| `comment-sl2.ctm` | comments | PASS | 207 |
| `comment-sl3.ctm` | comments | PASS | 23 |
| `comment-sl4.ctm` | comments | PASS | 114 |
| `comment-sl5.ctm` | comments | PASS | 114 |
| `comment-sl6.ctm` | comments | PASS | 206 |
| `empty.ctm` | comments | PASS | 23 |
| `association-qname-iid.ctm` | identity | PASS | 594 |
| `item-identifier-INF.ctm` | identity | PASS | 112 |
| `item-identifier-relative.ctm` | identity | PASS | 114 |
| `qname-date.ctm` | identity | PASS | 155 |
| `qname-digits.ctm` | identity | PASS | 140 |
| `rootless-uri.ctm` | identity | PASS | 159 |
| `subject-identifier-dot.ctm` | identity | PASS | 141 |
| `subject-identifier-non-http.ctm` | identity | PASS | 145 |
| `subject-identifier-relative.ctm` | identity | PASS | 119 |
| `subject-locator-dot.ctm` | identity | PASS | 131 |
| `subject-locator-relative.ctm` | identity | PASS | 113 |
| `topic-identifier-INF.ctm` | identity | PASS | 112 |
| `topic-identifier-unicode.ctm` | identity | PASS | 122 |
| `occurrence-decimal-dot-neg2.ctm` | occurrences | PASS | 355 |
| `occurrence-decimal-dot-pos.ctm` | occurrences | PASS | 353 |
| `occurrence-decimal-leading-zeros2.ctm` | occurrences | PASS | 353 |
| `occurrence-duplicate-string.ctm` | occurrences | PASS | 359 |
| `occurrence-duplicate-uri.ctm` | occurrences | PASS | 380 |
| `occurrence-qname-value.ctm` | occurrences | PASS | 390 |
| `occurrence-string-multiline.ctm` | occurrences | PASS | 365 |
| `occurrence-string-multiline2.ctm` | occurrences | PASS | 370 |
| `occurrence-uri-semicolon.ctm` | occurrences | PASS | 393 |
| `prefix-multiline2.ctm` | prefixes | PASS | 141 |
| `prefix-multiline3.ctm` | prefixes | PASS | 141 |
| `prefix-multiline4.ctm` | prefixes | PASS | 141 |
| `prefix-with-qm.ctm` | prefixes | PASS | 150 |
| `string-escape.ctm` | escapes | PASS | 505 |
| `string-escape2.ctm` | escapes | PASS | 325 |
| `unicode-escape-u4.ctm` | escapes | PASS | 330 |
| `unicode-escape-u6.ctm` | escapes | PASS | 330 |

All forty actual outputs equal the unchanged pinned baselines byte for byte. Individual source, baseline and actual SHA-256 digests are in `candidates.json`.
