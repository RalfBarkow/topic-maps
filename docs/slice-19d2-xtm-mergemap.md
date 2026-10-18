# Slice 19D2 — CTM Mergemap with XTM 2.0

Base: `f6a86668fce782a2e77d3bd763d58b0489079d75`.
Load **`topic-maps/ctm/xtm`** explicitly, using the already qualified 19D0B
source environment. Plain `topic-maps/ctm` remains usable without CXML; an XTM
request without the adapter signals `:xtm-mergemap-reader-required` before retrieval.
This configuration limit does not assert that XTM is an unknown CTM notation.

## Normative requirements and local choices

[CTM 3.16.3](https://www.isotopicmaps.org/ctm/ctm.html) identifies the CTM and
XTM notations, requires immediate deserialization of the referenced resource,
and transfers its Topics and Associations. The Include-specific identifier
alias transformation from 3.16.2 does not apply to Mergemap.

The unchanged XTM reader follows [XTM 2.0 4.3–4.9 and 4.20](https://www.isotopicmaps.org/sam/sam-xtm/).
[TMDM 6.2, 6.6–6.7 and 7.2](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
remain responsible for identity, normalization and the type-instance Core Subjects.
The existing [CXTM 3.18 and clause 4](https://www.isotopicmaps.org/cxtm/cxtm.html)
handle locator representation and canonical ordering.

Local implementation choices are an opt-in ASDF adapter, explicit caller-provided
resource resolution, an unchanged source-preserving `import-map-content`, and
conditions which retain their original causes. These choices are not claimed as
normative API or transaction requirements. No TMDM or XTM language rules changed.

## Real processing path

1. CTM resolves the resource and notation IRI through its existing IRI/QName reader.
2. The finite caller resolver receives:

   ```lisp
   (funcall resolver absolute-resource-iri
     :purpose :mergemap :from-document-iri parent-document-iri
     :notation "http://psi.topicmaps.org/iso13250/xtm")
   ;; => raw-octet-vector, diagnostic-source-key
   ```

3. The shared resource path validates the resolver result without decoding it.
   `mergemap-reader` selects the notation-specific function. CTM resources alone
   use the existing UTF-8/BOM decoder; Include still uses that same CTM decoder.
4. The XTM adapter passes the bytes to `topic-maps.xtm:deserialize-octets`, with
   the absolute Resource IRI as its Document IRI. Source-Key has no identity role.
   Specialized unsigned-byte-8 vectors retain their EQ identity; accepted generic
   byte vectors are specialized without changing their byte values.
5. XTM XML processing still exclusively uses `topic-maps.xml:parse-octets`.
6. The actual child Map is passed to `topic-maps.tmdm:import-map-content`.
   That operation copies content and normalizes the target. The child is unchanged;
   its root Map identifiers and root Reifier edge are not transferred.

No callback can enable implicit filesystem/network retrieval. The qualified XML
policy still rejects DOCTYPE and external resources. All original archives,
source hashes, decoder patches and Nix configuration remain unchanged.

## Original contract and actual objects

Unmodified source `ctm/in/mergemap-xtm.ctm`:

```ctm
%mergemap <mergemap-xtm.sub> http://psi.topicmaps.org/iso13250/xtm

lars isa person.
```

Its Document IRI **D** is:
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/mergemap-xtm.ctm`.

Resource IRI and child Document IRI **R** are:
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/mergemap-xtm.sub`.

The resolver supplies Source-Key `ctm/in/mergemap-xtm.sub` and the unchanged
161 source bytes. The child reader produces five Topics, one Association and
two Roles. The final target has seven Topics, two Associations and four Roles:

| Actual TMDM Topic | Identifier property |
|---|---|
| CTM lars | II `D#lars` |
| CTM person | II `D#person` |
| imported XTM lars | II `R#lars` |
| imported XTM person | II `R#person` |
| Core type-instance | SI `http://psi.topicmaps.org/iso13250/model/type-instance` |
| Core instance | SI `http://psi.topicmaps.org/iso13250/model/instance` |
| Core type | SI `http://psi.topicmaps.org/iso13250/model/type` |

Both Associations have the same actual Core Type Topic. The CTM Association's
`instance`/`type` Players are its CTM-local Topics; the imported Association's
Players are its XTM-local Topics. Roles have the correct Association Parent,
Role Type and Player by EQ, including rolesPlayed. Locals retain one II each;
there are no Include aliases. Each source content object resolves to its actual
canonical target copy through the existing import resolver.

The generated CXTM is **byte-identical to the unchanged 1,519-byte baseline**.
The integration report contains both complete XML documents and observed model
properties. No hand-built substitute is counted as an original CTM contract.

## Tests and diagnostic contract

The tests cover full-IRI/QName notation and resources, relative/absolute resource
resolution, exact resolver arguments, Source-Key independence, repeated and mixed
CTM/XTM directives, nested CTM-to-XTM resolution, forward Players, Core merging,
retained handles and mutation-free serialization. All thirteen previous positive import sources and six negative sources are also repeated after loading the adapter. Child Maps and retained raw
slots are checked before/after actual imports. Root Reifier exclusion is tested
through explicit model-API instrumentation, not claimed as new XTM syntax.

A valid UTF-16LE XML document with BOM reaches the qualified XML boundary using
the same octet vector by EQ. The CTM decoder is observed zero times. The bytes
remain unchanged; a control confirms they cannot be decoded as CTM UTF-8.

| Failure | Condition / code |
|---|---|
| no resolver | `ctm-unsupported`, `:resource-resolver-required` |
| resource absent or declined with NIL | `ctm-resource-error`, `:resource-unavailable` |
| resolver signals refusal | `ctm-resource-error`, `:resource-resolver-failure`, original cause retained |
| invalid octets or Source-Key result | `ctm-resource-error`, `:invalid-resource-result` |
| unknown notation | `ctm-rejection`, `:unknown-mergemap-notation`, before retrieval |
| malformed XML / invalid encoding | `mergemap-source-error`, original `xtm-xml-error` retained |
| XTM structure/version/namespace/ID error | `mergemap-source-error`, original `xtm-rejection` retained |
| valid unsupported XTM feature | `mergemap-source-unsupported`, original `xtm-unsupported` retained |
| model conflict during child reading | `mergemap-source-error`, original TMDM condition retained |
| model conflict during content import | existing `ctm-rejection`, original TMDM condition retained |

The public `topic-maps.ctm:error-cause` reader exposes that exact cause object.
For XML failures its nested cause remains available through the XTM reader.
The wrapper retains the CTM directive position and resource context; the XTM
condition retains its child Document IRI, Source-Key and approximate XML position.
Unsupported XTM features are not classified as malformed CTM notation.

## Full offline validation

```sh
cd /Users/rgb/workspace/topic-maps
python3 scripts/validate-slice-19d2.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /tmp/topic-maps-19d2-review
```

Preparation uses offline Nix evaluation and the existing hash-verified sources
and patches. The driver runs XML qualification (146 checks), unchanged standalone
XTM tests (327 checks and six original byte comparisons), the complete retained
suite (12,100 Lisp checks, two Python tests and 16,294 NFC comparisons), then the
new adapter tests in that fresh process. Network is denied with `sandbox-exec`.
`TOPIC_MAPS_XTM_MERGEMAP_REPORT` explicitly enables adapter tests after the core
suites; core reports remain separate. The restored source registry is read as
safe configuration data from the qualified `CL_SOURCE_REGISTRY` environment.

Only `mergemap-xtm.ctm` moves from NOT-RUN to PASS: final CTM status is
**205 PASS, 4 known FAIL, 64 NOT-RUN**. Original DateTime and Include discrepancies
remain byte-for-byte unchanged. Five obsolete XTM-unimplemented check labels in
the retained Mergemap/CXTM reports now describe the explicit-resolver requirement;
the old original-case observations and all other retained report content remain
unchanged. The XTM report is separate: **6 PASS, 0 FAIL, 118 NOT-RUN** across the
124 XTM inputs, comprising six executed positives and 118 unexecuted inputs.
No new XTM reader contracts are registered by the CTM import.

A full offline Nix rebuild is NOT-RUN; existing Store sources plus fresh patched
ASDF loading are exercised. No additional dependency downloads are needed.

## Inspect the actual original result

First prepare and launch a fresh qualified process (the target must be new):

```sh
cd /Users/rgb/workspace/topic-maps
xtm_registry=$(python3 scripts/prepare-cxml.py --directory /tmp/xtm-mergemap-review-sources --registry)
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /usr/bin/env CL_SOURCE_REGISTRY="$xtm_registry" \
  /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --no-sysinit --no-userinit
```

```lisp
(require :asdf)
(asdf:load-asd #P"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm/xtm")
(defparameter *result*
  (topic-maps.ctm:deserialize-string
    "%mergemap <child.xtm> <http://psi.topicmaps.org/iso13250/xtm> lars isa person."
    :document-iri "https://example.invalid/main.ctm"
    :resource-resolver
    (lambda (iri &key purpose from-document-iri notation)
      (assert (equal iri "https://example.invalid/child.xtm"))
      (assert (eq purpose :mergemap))
      (assert (equal from-document-iri "https://example.invalid/main.ctm"))
      (assert (equal notation "http://psi.topicmaps.org/iso13250/xtm"))
      (with-open-file (in #P"/Users/rgb/workspace/topic-maps/vendor/cxtm/ctm/in/mergemap-xtm.sub"
                          :element-type '(unsigned-byte 8))
        (let ((octets (make-array (file-length in) :element-type '(unsigned-byte 8))))
          (read-sequence octets in)
          (values octets "pinned:ctm/in/mergemap-xtm.sub"))))))
(describe *result*)
(dolist (association (topic-maps.tmdm:topic-map-associations *result*))
  (describe association)
  (dolist (role (topic-maps.tmdm:association-roles association))
    (describe (topic-maps.tmdm:association-role-player role))))
```

No additional XTM features, XTM mergeMap, Include-rule changes, HyperDoc changes,
persistent-image loads or publication are part of this slice.
