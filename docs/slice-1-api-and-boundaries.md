# Slice 1 reader and model boundary

The repository was observed clean at
`9c83db34eb1ba8091b004433f088056717dbaa7e` on `codex/ctm-slice-0` before
`git switch -c codex/ctm-slice-1 9c83db34eb1ba8091b004433f088056717dbaa7e`.
Implementation is in `/Users/rgb/workspace/topic-maps`. HyperDoc is not a base,
dependency or integration target in this slice.

## Public reader API

```lisp
(topic-maps.ctm:deserialize-string
 "topic - \"Name\"."
 :document-iri "https://example.invalid/lesson.ctm"
 :source-name "lesson")

(topic-maps.ctm:deserialize-file
 #p"/path/to/document.ctm"
 :document-iri "https://example.invalid/lesson.ctm"
 :source-name "lesson")
```

Both return a new `topic-maps.tmdm:topic-map`. The Document IRI is required,
absolute and fragment-free (RFC 3987 absolute-IRI). File reading accepts UTF-8,
with an optional UTF-8 BOM. It uses ANSI binary I/O and a strict decoder,
including rejection of overlong sequences, surrogates and incomplete bytes.
A Common Lisp implementation unable to represent a needed Unicode scalar
signals UNSUPPORTED. The core reader/model depends on no third-party library.
ASDF is the loader, and UIOP is used only by the retained foundation/test tooling.

The dedicated lexer distinguishes identifiers, QNames, IRIs, strings and
punctuation. There is no use of Common Lisp READ, READ-FROM-STRING or EVAL on
CTM text. Character case is preserved. CTM identifier character ranges, quoted
string escapes, and single/nested multiline comments are handled explicitly.
IRI construction applies CTM's percent-octet UTF-8 decoding and relative
resolution from RFC 3986 §5.2. No fetching, host/scheme case normalization or
machine-path-derived Document IRI occurs. Full IRI grammar and scheme-specific
validation are not claimed; delimiter, character, relative-colon and fragment
checks cover the implemented path. No prefixes can be declared in this slice;
a QName produces a specific undefined-prefix rejection.

The syntax subset is Topic declarations with local, Subject Identifier,
Subject Locator or Item Identifier identity; quoted untyped names; required
periods; semicolon-separated names and optional trailing semicolon. Other
recognized CTM constructs signal `CTM-UNSUPPORTED`. Typed names, additional
identity assignments, associations, occurrences, scope, variants, reification,
templates, directives, wildcards and other encodings are outside this slice.
Unsupported input is not returned as an apparently valid partial map.
Each read creates its own private map; a failed read returns no model.

## Conditions and positions

- `CTM-REJECTION`: an identified CTM/decoding/input-contract error.
- `UNDEFINED-PREFIX`: a subclass of rejection, code `:UNDEFINED-PREFIX`.
- `CTM-UNSUPPORTED`: separate from rejection; a recognized unavailable feature.
- File I/O exceptions propagate as file errors, not CTM rejections.

Accessors: `error-code`, `error-position`, `error-position-unit`, `error-line`,
`error-column`, `error-source`. Offsets are zero-based; character line/column
numbers are one-based, with CR, LF and CRLF handled. Invalid UTF-8 uses byte
offsets when decoded character positions are unavailable. `source-name` is an
optional logical source label; the harness supplies the stable case ID.
The selected invalid case reports character offset 1, line 2, column 1 because
its original file begins with a newline.

## Model and identity

Ordinary ANSI Common Lisp structures represent a Topic Map, Topic and Topic
Name. Topics have separate Item Identifier, Subject Identifier and Subject
Locator sets (lists with unique locator strings), Name items and a map parent.
Names have value, a Topic as type and a Topic parent. Parent/type links are real
object references. Print methods avoid cycles; standard DESCRIBE works.
The remaining TMDM properties are implicitly initialized to empty sets or null
as appropriate for the supported inputs. This is a minimal representation,
not the complete TMDM information-item model.

The default type URI comes directly from CTM §3.11. Its Topic is interned in
the current map by Subject Identifier, reused if already present, and created
only when a name needs it. Reading an unnamed or empty document does not
create it. It receives no invented Item Identifier or name.

Same-map interning implements the applicable identity equality in TMDM §5.3.5:
same-category equal locators reuse a Topic, as does Item Identifier/Subject
Identifier overlap. Subject Locator equality is separate; equality of its
string with an Item or Subject Identifier does not conflate them. An unscoped
Name with the same value, type and parent is interned under TMDM §5.4 equality;
all supported names have implicitly empty scope/variants and null reifier.
Lists have deterministic observational order, not normative set ordering.
General merging procedures (§§6.2–6.3), cross-map/cross-document merging and
identities added by topic tails are not implemented. Interning avoids duplicate
items in this bounded subset rather than implementing an unrestricted merge
engine or global object registry.

Different Document IRIs produce different local Item Identifier strings.
Those local names alone add no Subject Identifier/Locator or evidence of a
shared Subject. Equal spelling does not establish cross-document identity.

## Harness and canonicalization boundary

`topic-maps` remains the independent Slice 0 foundation; `topic-maps/tests`
retains its regressions. `topic-maps/tmdm` and `topic-maps/ctm` are opt-in
systems. `topic-maps/ctm/tests` adds semantic assertions and a selected executor.
There is no `topic-maps/cxtm` system. The former foundation assertion that no
reader/model system exists is adapted to prohibit the absent canonicalizer;
all discovery, integrity, selection, status and reporting tests remain.

The report writer takes an optional implementation descriptor. An inventory-only
call retains the foundation-only metadata; the Slice 1 executor explicitly
reports the implemented identity/name subset. That descriptor does not change
contracts or infer a result from the existence of implementation code.

Five positive cases produce separate semantic observations of actual model
objects. Their imported `CXTM-EQUAL` results remain NOT-RUN. The required
negative case becomes PASS only after verifying the precise undefined-prefix
condition. Remaining imported cases are untouched. The two JSON reports keep
semantic assertions and canonical contracts separate. Five original baselines
are read as expected-property evidence by a Python standard-library checker;
no XML is produced, incompletely serialized or byte-compared by this slice.

[Reading the First Five CTM Documents](reading-first-five-ctm-documents.md)
explains the absolute Document IRIs versus relative baseline locators and
provides exercised inspection forms. Normative editions, exact consulted
snapshot hashes, corpus revision and bounded clauses are recorded in
[the Slice 1 source record](../references/slice-1-sources.json).
The pinned suite targets the **CTM draft dated 2010-03-31**; passing it alone
would not establish full ISO/IEC 13250-6:2010 conformity. Published ISO standards
remain authoritative. No blocking conflict was found for the selected cases.
