# Slice 19D1 — Reading XTM 2.0 identity

Base: `1691c8e0712e30666de2e667a5050eccb0086f71`. This is an independent
`topic-maps/xtm` ASDF system depending on `topic-maps/tmdm` and `topic-maps/xml`.
It neither depends on CTM nor changes the existing information-item model.

## Normative basis and implementation boundary

The [published-equivalent XTM 2.0 text](https://www.isotopicmaps.org/sam/sam-xtm/)
is ISO/IEC 13250-3:2007, not XTM 2.1. Clauses 4.1–4.2 establish the XML Infoset
input; 4.3.1 and Annex A specify namespaces and grammar. Clauses 4.3.3–4.3.4
require percent-UTF-8 decoding and Document-IRI resolution. Clauses 4.4–4.8
specify map creation, required topic IDs and the three identity properties.
Clause 4.9 maps `instanceOf` to type-instance Associations. Clause 4.20 searches
existing SI/II locators before creating a reference Topic; a hit adds no II.

[TMDM](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) 4.2, 5.1–5.3,
5.7–5.8, 6.2, 6.6–6.7 and 7.1–7.2 govern locator identity, canonical same-map
merging and Core Subjects. Existing public TMDM operations implement those
transformations. The XML ID-uniqueness set contains strings only, never Topics.

[CXTM](https://www.isotopicmaps.org/cxtm/cxtm.html) 3.2–3.4, 3.10–3.15, 3.18
and clause 4 supply the existing numbering, reference, locator and ordering
rules. Baselines contain relative locators because CXTM 3.18 removes the given
base-locator prefix; stored TMDM identifiers stay absolute. CXTM is not used to
infer TMDM identity.

Local choices: XML events form a temporary source tree, validated before model
construction. Deserialization then follows document order, including forward
references. Existing replacement handles remain authoritative. Unknown XTM
structure is rejected; excluded grammar extension points signal unsupported,
without claiming full validation of their unimplemented subgrammars. TMDM
conflicts propagate as their original specific conditions, rather than becoming
XML errors. No transaction policy or extra merging rule is attributed to XTM.

## Public API and diagnostics

```lisp
(topic-maps.xtm:deserialize-octets octets
  :document-iri "https://example.invalid/maps/example.xtm"
  :source-key "caller-supplied:source-label")
```

Returns a new actual `topic-maps.tmdm:topic-map`. Octets are an unsigned-byte-8
vector; no filenames or decoded strings are implicitly accepted. Document IRI
is required, absolute and fragment-free. Source-Key affects diagnostics only.
Source bytes and source-tree nodes are not mixed into the TMDM information items.

`xtm-rejection` carries `error-code`, `error-detail`, `error-document-iri`,
`error-source-key`, `error-line`, `error-column`. Positions are approximate SAX
positions at a start-tag boundary, never invented source spans. `xtm-unsupported`
is a separate condition. `xtm-xml-error` retains `error-cause` and distinguishes
`:xml-not-well-formed` from `:doctype-forbidden`. Existing TMDM
`item-identifier-error` and `core-subject-error` are preserved. API argument/type
errors and an unqualified XML runtime are configuration errors, not XTM rejects.

All actual XML parsing goes through `topic-maps.xml:parse-octets`. Its unchanged
19D0B ABI markers, mandatory namespaces, rejecting DOCTYPE/entity policy and
strict patched decoders remain required. There are no retrieval callbacks,
file opens or network retrieval in the XTM reader. External `topicRef` locators
create/reuse Topics without retrieving the referenced document. The pinned
CXML XML-1.0 name tables check ID/NCName characters; this helper does not bypass
the XML byte boundary. ID whitespace is collapsed and document uniqueness checked.

## Original contracts and actual model

The Document IRI for each input is:
`https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/<file>`.

| Unmodified original | Actual TMDM | CXTM bytes |
|---|---|---:|
| empty.xtm | empty Topic Map | 23 |
| topic.xtm | one Topic, II = Document IRI + `#topic` | 114 |
| itemid-tm.xtm | empty Map, Map II = Document IRI + `#the-topic-map` | 94 |
| topic-type.xtm | five Topics, one Association, two Roles | 963 |
| topic-type-duplicate.xtm | same normalized information items | 963 |
| merge-three-way.xtm | one Topic with the three absolute `#topic`, `#topic2`, `#topic3` IIs | 168 |

The separate XTM report records six genuine CTM-independent reader/CXTM
comparisons. The remaining 107 positive and 11 negative XTM inputs are unexecuted;
they are not imported as passing contracts. These six results do not establish
complete XTM conformance.

The unchanged `ctm/in/mergemap-xtm.sub` is also read directly with its own absolute
Document IRI under that same base. Its Topics are the `#lars` and `#person` II
Topics plus the three Core SI Topics `.../model/type-instance`, `.../model/type`,
`.../model/instance`. One Association has the type-instance Topic as its Type.
Its Roles have `(Type, Player)` = `(type, person)` and `(instance, lars)`.
All Parent, Type, Player, rolesPlayed and canonical-handle references are checked
by actual EQ. This direct fixture is **not** the CTM Mergemap contract.

Retained Topic, Association and Role handles are checked during later declaration
merges. Tests distinguish an SI hit (no new II) from a forward reference which
first creates an II and later merges; declaration order therefore can affect
identifier sets. Subject Locators are not used by topicRef lookup. Separate
Document IRIs preserve different local identities. CXTM leaves both current
objects and retained handles unchanged.

## Reproduce offline

No new dependency downloads. Use the already qualified original sources and
unchanged local decoder patches:

```sh
cd /Users/rgb/workspace/topic-maps
python3 scripts/validate-slice-19d1.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /tmp/topic-maps-19d1-review
```

The driver prepares sources with offline Nix evaluation and verified hashes,
then runs XML qualification, two independent XTM processes with byte-identical
reports, and the unchanged full regression. SBCL runs under `sandbox-exec` with
network denied; there are no loads into persistent images. `execution.json`
records commands, times, source hashes, temporary runtime provenance and results.
A full offline Nix rebuild is **NOT-RUN**; existing Store sources plus fresh
patched-source ASDF loading are tested. XML qualification is not an XTM PASS.

For inspection, prepare once (the target must not already exist):

```sh
cd /Users/rgb/workspace/topic-maps
xtm_registry=$(python3 scripts/prepare-cxml.py --directory /tmp/xtm-review-sources --registry)
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /usr/bin/env CL_SOURCE_REGISTRY="$xtm_registry" \
  /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --no-sysinit --no-userinit
```

In this fresh process:

```lisp
(require :asdf)
(asdf:load-asd #P"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/xtm")
(defparameter *map*
  (with-open-file (in #P"/Users/rgb/workspace/topic-maps/vendor/cxtm/ctm/in/mergemap-xtm.sub"
                      :element-type '(unsigned-byte 8))
    (let ((bytes (make-array (file-length in) :element-type '(unsigned-byte 8))))
      (read-sequence bytes in)
      (topic-maps.xtm:deserialize-octets bytes
        :document-iri "https://example.invalid/mergemap-xtm.sub"
        :source-key "pinned:ctm/in/mergemap-xtm.sub"))))
(describe *map*)
(defparameter *association* (first (topic-maps.tmdm:topic-map-associations *map*)))
(describe *association*)
(dolist (role (topic-maps.tmdm:association-roles *association*))
  (describe role)
  (describe (topic-maps.tmdm:association-role-player role)))
(eq *map* (topic-maps.tmdm:association-parent *association*)) ; T
```

Not implemented: CTM XTM-Mergemap dispatch, XTM mergeMap, Names, Variants,
Occurrences, explicit Associations, Reification and embedded XML values.
No HyperDoc changes or additional XTM features belong to this slice.
