# Slice 20A: register forty existing CTM original contracts

This slice registers exactly the forty positive originals authorized for Slice
20A. It adds no reader, model, XML, XTM or canonicalization semantics. Work resumed
on `codex/ctm-slice-20a`, parent
`9c196ddc16cf5cd727fcde81ad7835edefa0f787`, with the existing ASDF addition and
153-line test draft preserved and completed. Their observed starting SHA-256
digests are recorded in the new execution evidence.

The previous Slice 19D2 result is **205 PASS, 4 FAIL, 64 NOT-RUN**. The expected
result after forty successful new comparisons is **245 PASS, 4 FAIL, 24 NOT-RUN**.
The actual result and every candidate's status are recorded in
[execution evidence](../reports/slice-20a/execution.json) and the
[forty-contract table](../reports/slice-20a/contracts.md). Prior exploratory
matches are not counted as executed contracts. No separate complete historical
Slice-19 exploration inventory was found in the repository; the approved explicit
forty-case list determines this selection.

## Registration and evidence

`tests/ctm-registered-originals.lisp` selects the existing discovered Case Records:
10 comments/empty Map, 13 identities/IRIs/QNames, 9 occurrences, 4 prefixes and 4
escapes. It checks source/baseline identity and the existing pinned Document IRI
before deserializing each original file through the public CTM API. It verifies
concrete TMDM properties and EQ references, canonicalizer purity, deterministic
octets, original source preservation and unchanged contract identities. Only an
actual byte comparison can produce `cxtm-match`; errors and unsupported features
retain their own outcomes. No failure becomes an empty Map or a successful test.

The new test runs permanently at the end of `scripts/fresh-sbcl.lisp`, after the
retained suites and optional XTM adapter. Its ASDF system can also run directly;
without XTM integration, only the already loaded core contracts contribute to
its entry totals. It does not reset or rediscover the shared corpus. All forty
selected cases must enter as NOT-RUN. Nonselected records and all earlier CXTM
observations must remain unchanged.

Historical reports keep their original bytes. The existing 19D2 validator is
reused without modification; it validates XML, standalone XTM, all retained
suites and XTM Mergemap, writing its stage snapshots before registration. The
new validator independently compares all forty emitted outputs against the
pinned baseline bytes and verifies that only those forty records changed.
The four known FAILs remain the same actual CXTM mismatches:
`include-template`, `include-wildcard2`, `occurrence-datetime2` and
`occurrence-datetime-timezone2`. Their complete old case records and actual
outputs must remain unchanged. The separate XTM corpus remains **6 PASS,
0 FAIL, 118 NOT-RUN** (107 positive and 11 negative unexecuted inputs).

## Reproduce the full offline validation

Use a new output directory; existing evidence is never overwritten:

```sh
cd /Users/rgb/workspace/topic-maps
python3 scripts/validate-slice-20a.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /tmp/topic-maps-20a-review
```

All Lisp execution uses fresh SBCL 2.5.4 with network denied by `sandbox-exec`.
Source preparation reuses hash-verified Store sources and the existing XML
patches, using offline Nix evaluation. No dependencies are downloaded. Retained
checks are 12,100 Lisp checks, 146 XML qualification checks, 327 standalone XTM
checks, 217 XTM-Mergemap checks, two Python unit tests and 16,294 NFC comparisons.
The new registration assertions and all actual byte counts are recorded in the
new reports. A complete Nix rebuild remains NOT-RUN.

Evidence files:

- `reports/slice-20a/current.validation.json`: current Case Records and totals.
- `reports/slice-20a/current.cxtm.json`: all old and forty new actual comparisons.
- `reports/slice-20a/current.registration.json`: model observations and checks.
- `reports/slice-20a/candidates.json`: per-case source, baseline and actual SHA-256.
- `reports/slice-20a/actual/`: forty actual CXTM byte streams.
- `reports/slice-20a/retained/`: full fresh qualification and regression evidence.
- `reports/slice-20a/integrity.json`: unchanged protected and historical file hashes.

## Remaining cases

The 24 remaining cases are **NOT-RUN**, not failures or inferred unsupported
results. Their original records are listed in
[remaining.json](../reports/slice-20a/remaining.json). They were not in the
approved forty-positive registration selection; no language or negative-contract
extension is authorized in this slice.

| Unexecuted family | Cases | Reason to retain NOT-RUN in 20A |
| --- | ---: | --- |
| `empty2` | 1 positive | Version directive contract is outside the selected empty-map case. |
| `encoding-8859-5` | 1 positive | Legacy encoding contract; further encoding support is excluded. |
| `occurrence-ctm-integer` | 1 positive | CTM integer `*` value contract; additional literal forms are excluded. |
| `occurrence-string-triple`, `occurrence-string-triple2`, `unicode-escape-u4-triple-string`, `unicode-escape-u6-triple-string` | 4 positive | Triple-string contracts are outside the selected escapes and strings. |
| `template-ambiguous-parameter5`, `template-ambiguous-parameter6`, `template-subject-identifier2` | 3 positive | Contextual template argument contracts remain outside this registration slice. |
| `BOM-contradicts-encoding` | 1 negative | Encoding rejection contract is unregistered and unexecuted. |
| `occurrence-double-negative-infinity`, `occurrence-double-positive-infinity` | 2 negative | Infinity literal rejection contracts are unregistered and unexecuted. |
| `qname-hyphen`, `topic-id-illegal` | 2 negative | Identifier boundary rejection contracts are unregistered and unexecuted. |
| `string-unbalanced`, `string-unicode`, `string-unicode2` | 3 negative | String/escape rejection contracts are unregistered and unexecuted. |
| `template-item-identifier-2nd-arg`, `template-item-identifier3`, `template-subject-locator-2nd-arg`, `template-subject-locator3` | 4 negative | Template argument rejection contracts are unregistered and unexecuted. |
| `unknown-directive`, `wrong-version` | 2 negative | Directive/version rejection contracts are unregistered and unexecuted. |

## Inspect selected new comparisons

These forms run from the repository in a fresh SBCL process. They load only the
existing foundation, CTM and CXTM systems and expose actual model objects. The
validation driver executes these same forms with network denied.

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (merge-pathnames "topic-maps.asd" (truename ".")))
(asdf:load-system "topic-maps")
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps/cxtm")
(defun inspect-original (name)
  (let* ((corpus (topic-maps.test-foundation:discover-corpus))
         (case (first (topic-maps.test-foundation:select-cases
                       corpus :id (format nil "ctm/in/~A.ctm" name))))
         (doc (topic-maps.test-foundation:test-case-document-iri case))
         (map (topic-maps.ctm:deserialize-file
               (topic-maps.test-foundation:test-case-source-pathname case)
               :document-iri doc))
         (actual (topic-maps.cxtm:canonicalize-octets map :base-locator doc)))
    (with-open-file (in (topic-maps.test-foundation:test-case-expected-baseline case)
                        :element-type '(unsigned-byte 8))
      (let ((expected (make-array (file-length in) :element-type '(unsigned-byte 8))))
        (read-sequence expected in)
        (assert (equalp actual expected))))
    (format t "~&~A: ~D byte-equal CXTM bytes~%" name (length actual))
    (describe map)
    (dolist (topic (topic-maps.tmdm:topic-map-topics map)) (describe topic))
    map))
(inspect-original "comment-ml-nested2")
(inspect-original "topic-identifier-unicode")
(inspect-original "occurrence-string-multiline2")
```

No HyperDoc changes, persistent Lisp image changes, push, deployment or next
slice are part of this work.
