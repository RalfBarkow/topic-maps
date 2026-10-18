# Reading CTM Include and Imported Templates

Slice 19C builds on `5e716c078b885e97ebe858230ce7d8578e65ae4b` and the unchanged
corpus `cd165b150176c1d6842b37be9cc9051b40d4996b` (draft 2010-03-31).
Published CTM remains authoritative. This slice implements Include; it does not
claim complete CTM/TMDM conformance or resolve the two original baseline conflicts.

## Requirements and chosen execution contract

[CTM 3.2, 3.3.6, 3.3.8, 3.14–3.16.2](https://www.isotopicmaps.org/ctm/ctm.html)
define the environments, identifier construction, Templates and Include.
Include processes a child immediately, using its resource IRI as Document IRI,
the immediate parent's **Document IRI** as child Wildcard IRI, and the current
Counter. Each level adds aliases for existing child Topic IIs starting with
that child's Document IRI; the suffix is resolved against the parent's Document
IRI. Existing identifiers are retained. The final child Counter is returned.
Templates are imported as declarations at the inclusion point; Prefix bindings
and named-Wildcard caches are not imported.

Body identifiers, relative IRIs and QNames in imported Templates execute in the
caller's active Document-IRI/Prefix environment. This is the explicit, reviewed
interpretation for this slice, not a lexical closure over the definition's
Prefix bindings. Definition-source identity and Document IRI are retained as
provenance. Arguments use the existing contextual binding rules; actual Topics
are canonical handles, not generated identity substitutes. Forward lookup uses
the current Template registry. Each invocation has fresh named-Wildcard bindings
and shares the active Counter.

[TMDM 4.3, 5.1–5.8 and 6.1–6.7](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
remain the identity/merge authority. Alias addition and Map content transfer
use the existing operations, including Scope, Variant, Reifier and Core Subject
invariants. Source Map identifiers/reifier are not transferred as root metadata.
[CXTM 3.13, 3.17–3.18 and 4](https://www.isotopicmaps.org/cxtm/cxtm.html)
preserve all identifier entries, with canonical locator representation/order.
No serializer rule or TMDM representation is changed in this slice.

## Public API and resource boundary

`deserialize-string` and `deserialize-file` keep their existing keyword interface
and exactly two return values: Map and final Counter. `:resource-resolver` is a
function called with the absolute resource IRI and these keywords:

```text
(:purpose :include :from-document-iri parent-document-iri :notation nil)
```

It returns an octet vector and optional string source key. Only the resource
IRI supplies the child's identity base; the source key is diagnostic. Existing
strict UTF-8/BOM decoding is reused. No implicit filesystem or network fallback
exists. Invalid CTM bytes/source are rejected, not accepted as arbitrary data.

Missing resources, resolver errors and malformed resolver results are resource
conditions. Missing resolver, active cycles and configured depth limits are
explicit unsupported/resource-policy conditions. Cycle/depth rejection is an
implementation policy, not a normative CTM grammar prohibition. Existing
Mergemap behavior remains independent: no Include aliasing, Template import or
Counter propagation is added to Mergemap.

Alias inputs are snapshotted once per Include level. Matching is a literal
string prefix, not a fragment-boundary test. Suffixes are already locator
strings and are **not percent-decoded a second time**. Only Topic IIs receive
aliases: SIs, SLs, Occurrence values and root identifiers do not.

Template-name/arity conflicts are checked before caller mutation. Alias work
uses the private child graph. Existing `import-map-content` preflight protects
the caller Map on semantic conflicts. Counter and Template-registry transfer
follow successful model transfer. This is a single-threaded semantic rejection
contract; it is not a new general transaction system.

## Source preservation

Definitions retain their name/arity, original tokens, original source text/key,
Document IRI and definition position. Template execution changes lexical
source/line context to the definition while keeping the caller's semantic
environment. Error frames separately retain definition source/position/Document
IRI and invocation source/position/active Document IRI. Nested invocations retain
the complete chain. No source text substitution or Lisp evaluation occurs.

## Two original baseline discrepancies

Let `P` be the fixed corpus Document-IRI prefix ending in `/ctm/in/`.

For `include-template.ctm`, `T=P+include-template.ctm`, `S=P+include-template.sub`.
The child contains only a definition and creates zero Topics. Its Include alias
pass therefore has no operands. Later `template(topic)` creates `{T#topic}` and
Type `{T#occtype}` with one string Occurrence `"Test"`. No rule in the reviewed
clauses supplies a future `S#occtype` alias. Actual CXTM: **353 bytes**; original:
**401 bytes**, with extra `include-template.sub#occtype`. Topic numbering also
changes. The registered original comparison is **FAIL**; model assertions pass.

For `include-wildcard2.ctm`, use A for the main source, B for `.sub`, C for `.sub2`:

| Processor | Document IRI | Wildcard IRI | Entry → exit Counter |
|---|---|---|---|
| C | C | B | 0 → 1 |
| B | B | A | 0 → 2 |
| A | A | A | 0 → 3 |

C creates `B#$__1.foo`. C→B adds no alias because that II does not start with C.
B creates `A#$__2.foo`. B→A adds `A#$__1.foo` while retaining `B#$__1.foo`.
A creates `A#$__3.foo`. The final three named subjects have these II sets:

- Sub Sub: `{A#$__1.foo, B#$__1.foo}`
- Sub: `{A#$__2.foo}`
- Master: `{A#$__3.foo}`

All three Names share the same actual default Type Topic. Actual CXTM:
**719 bytes**; original: **669 bytes**, omitting `include-wildcard2.sub#$__1.foo`.
Canonical Topic order changes because one identifier set is larger. This is a
missing baseline identifier, not merely a relative-locator spelling difference.
The registered comparison remains **FAIL**. The root Wildcard IRI is not silently
substituted for the immediate parent's Document IRI.

These findings distinguish published-rule interpretation, upstream baseline
evidence and locally executed observations. No upstream input/baseline is edited.

## Inspect actual objects

Run from the repository root in a fresh SBCL process. The resolver below supplies
only the one known fixture; it is not a general filesystem/network loader.

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps/cxtm")
(let* ((base "https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/")
       (doc (concatenate 'string base "include-template.ctm"))
       (child (concatenate 'string base "include-template.sub"))
       (root (asdf:system-source-directory "topic-maps"))
       (resolver
         (lambda (iri &key purpose from-document-iri notation)
           (assert (and (eq purpose :include) (null notation) (string= from-document-iri doc)))
           (when (string= iri child)
             (with-open-file (in (merge-pathnames "vendor/cxtm/ctm/in/include-template.sub" root)
                                 :element-type '(unsigned-byte 8))
               (let ((bytes (make-array (file-length in) :element-type '(unsigned-byte 8))))
                 (read-sequence bytes in) (values bytes "ctm/in/include-template.sub")))))))
  (multiple-value-bind (map counter)
      (topic-maps.ctm:deserialize-file
        (merge-pathnames "vendor/cxtm/ctm/in/include-template.ctm" root)
        :document-iri doc :source-name "ctm/in/include-template.ctm" :resource-resolver resolver)
    (let* ((owner (find-if (lambda (topic) (member (concatenate 'string doc "#topic")
                           (topic-maps.tmdm:item-identifiers topic) :test #'string=))
                         (topic-maps.tmdm:topic-map-topics map)))
           (occurrence (first (topic-maps.tmdm:topic-occurrences owner))))
      (assert (= counter 0))
      (assert (eq owner (topic-maps.tmdm:occurrence-parent occurrence)))
      (assert (equal (list (concatenate 'string doc "#occtype"))
                     (topic-maps.tmdm:item-identifiers (topic-maps.tmdm:occurrence-type occurrence))))
      (describe occurrence)
      (describe (topic-maps.tmdm:occurrence-type occurrence))
      (write-string (topic-maps.cxtm:canonicalize map :base-locator doc)))))
```

Use `reports/slice-19c/include.json` for actual original-source model observations,
resource requests, processor environments and every before/after alias pass.
Use `cxtm.json` and `actual/` for actual canonical outputs and unchanged expected
bytes. Model checks passing do not turn a mismatching original contract into PASS.
