# Reading CTM Templates and Template Invocations

Slice 18 builds on `963f2a09444100d37e49cccbd6634879bd6742b5`.
The upstream corpus remains pinned at
`cd165b150176c1d6842b37be9cc9051b40d4996b` (draft 2010-03-31).
Its baselines are evidence, not a replacement for the published standard.

## Normative basis

[CTM](https://www.isotopicmaps.org/ctm/ctm.html) §§3.14–3.15,
productions 63–70, define the Template name/arity namespace, positional binding,
global and Topic-Tail invocation, deferred lookup of nested calls and fresh
invocation-local named Wildcards. §3.2 supplies document order, Document IRI,
Wildcard IRI and Counter; §§3.3.6–3.3.8 retain ordinary Topic identity.
§3.13 distinguishes Role declarations from argument lists using its colon/layout
rule. §3.4.1 production 29 requires an IRI reference after `^^`, not a variable.
The body grammar admits Topics, Associations and Invocations, not directives,
nested definitions, standalone Embedded Topics or a Topic Map Reifier.

[TMDM](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) §§5.3–5.8
supply the unchanged information items/equality rules; §§6.1–6.7 supply merging.
Templates add no TMDM item kind. [CXTM](https://www.isotopicmaps.org/cxtm/cxtm.html)
§§3.4–3.19 and 4.6–4.11 apply to the resulting ordinary information items.

## Concrete reader representation

`template-definition` stores name, ordered parameters, definition position and a
list of `ctm-statement` objects. Each statement has its parsed statement kind,
original character position and grammar-checked token sequence. Tokens retain
start/end offsets in the original source, including Unicode character offsets.
These are CTM concrete-syntax objects, not Topic Maps information items.

The definition traversal does not call TMDM constructors or intern identities.
It does not execute Wildcards. It checks the entire body even if never invoked.
Stored statements are replayed through the existing Topic/Name/Variant/
Occurrence/Association readers. There is no generated CTM string, Common Lisp
reader, EVAL, second literal-value parser or second Topic identity registry.

An invocation creates positional bindings and a fresh named-Wildcard table.
The same parser retains the shared Counter, Prefixes and Template registry.
Callers' arguments are evaluated in the caller environment: Wildcards and
Embedded Topics are resolved once and passed as actual canonical Topic handles.
IRIs/QNames retain their syntactic token and a locator resolved once in the
caller, without interning a Topic. Their Topic/literal use remains contextual;
an argument used only as an Occurrence value creates no SI Topic. Even an unused
QName requires a bound prefix; bound prefixes are never decoded a second time.
Explicit `=`/`^` arguments remain Topic references and cannot become literal
values or bare IRIs after an identity marker.
Bare and qualified literal values use the existing `read-literal` policy.
Qualified quoted lexical values are preserved. Datatype locators are not Topics.

The continued Topic Tail always retains its own canonical owner, independently
of the last Topic visited by a nested template. Retained argument handles are
resolved with `canonical-topic` when used after a Merge.

## Three equivalent/useful forms

Global and Tail calls produce equivalent models:

```text
def has-name($topic, $name)
  $topic - $name.
end
has-name(a, "Name")
```

```text
def has-name($topic, $name)
  $topic - $name.
end
a has-name("Name").
```

A nested callee may be declared after its caller, but before execution:

```text
def outer($topic)
  inner($topic)
end
def inner($topic)
  $topic - "Nested".
end
outer(a)
```

## Diagnostics and API policy

The public deserialization signatures and final Counter return value remain
unchanged. New exported CTM-REJECTION subclasses are `template-error`,
`duplicate-template`, `undefined-template`, `template-arity-error`,
`unbound-template-variable`, `invalid-template-argument` and
`invalid-template-body`. Existing Prefix conditions remain distinct.

`error-position`, `error-line`, `error-column` and `error-source` refer to the
original source. `error-context` holds an innermost-first list with Template
name, definition position and invocation position. These positions do not
identify objects outside that execution. Included-source provenance is not
implemented because Include is excluded.

Unbound variables are rejected during definition checking. Distinct parameter
names are required by this implementation's positional-binding policy. The
internal expansion-depth limit defaults to 256; reaching it reports
CTM-UNSUPPORTED / :TEMPLATE-DEPTH-LIMIT, not a normative syntax error.
There is no promise of a transaction covering an entire multi-statement
invocation. Existing per-operation conflict/preflight policies remain intact.

## Seven deliberately open grammar contracts

CTM §3.3.6 production 17 gives `subject-identifier -> iri-ref`; §3.9
production 52 uses that production for an unmarked identity in a Topic Tail.
§3.14's substitution prose does not explicitly add a variable there. The corpus
assumes `topic $iri.` is allowed with a bare IRI argument, and rejects it with an
explicitly marked II/SL argument. This Slice adds no such grammar extension.
An unmarked variable Tail identity is rejected with :TEMPLATE-IDENTITY-TAIL;
variables as an Occurrence Type before `:` and the explicit `^$iri`/`=$iri`
productions remain supported. The following imported contracts remain NOT-RUN:

- in/template-subject-identifier2.ctm
- in/template-ambiguous-parameter5.ctm
- in/template-ambiguous-parameter6.ctm
- invalid/template-item-identifier3.ctm
- invalid/template-item-identifier-2nd-arg.ctm
- invalid/template-subject-locator3.ctm
- invalid/template-subject-locator-2nd-arg.ctm

A rejection of an open contract is not recorded as a conformance PASS.
Separately, Include/Mergemap dependencies keep in/include-template.ctm,
in/include-template-wildcard.ctm, in/mergemap-template.ctm and
invalid/mergemap-template.ctm NOT-RUN. The last requires the fact that Mergemap
imports data, not template definitions (CTM §3.16.3); Include would import
Templates (§3.16.2). Neither directive is implemented here.

## Inspect actual Lisp objects in a fresh process

Run from the repository root. Printed addresses belong only to this process.

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/ctm")
(asdf:load-system "topic-maps/cxtm")
(let* ((source "def named($t,$n) $t - $n. end def outer($t) named($t,\"Name\") end a outer().")
       (iri "https://example.invalid/templates.ctm")
       (map (topic-maps.ctm:deserialize-string source :document-iri iri))
       (topic (find-if #'topic-maps.tmdm:topic-names (topic-maps.tmdm:topic-map-topics map)))
       (name (first (topic-maps.tmdm:topic-names topic))))
  (assert (eq topic (topic-maps.tmdm:topic-name-parent name)))
  (assert (member (topic-maps.tmdm:topic-name-type name)
                  (topic-maps.tmdm:topic-map-topics map) :test #'eq))
  (describe map)
  (describe topic)
  (describe name)
  (describe (topic-maps.tmdm:topic-name-type name))
  (write-string (topic-maps.cxtm:canonicalize map :base-locator iri)))
```

## Executed original contracts

The tables below list the explicit test selection, not inferred passes.
Execution evidence is in `reports/slice-18/`: original bytes, model observations,
specific rejection classes/codes/positions, runtime and source/artifact hashes.
The independent Python checker relates actual model references to original
baseline topics separately from byte equality. `tests/ctm-templates.lisp` also
asserts EQ relationships, retained handles and mutation-free serialization.

| Positive original | Baseline bytes | Principal exercised capability |
|---|---:|---|
| `association-scope-embedded3.ctm` | 2431 | definition / invocation, binding, Embedded Topics, Scope |
| `association-scope-embedded4.ctm` | 3613 | definition / invocation, binding, Embedded Topics, Scope |
| `name-scope-embedded3.ctm` | 2105 | definition / invocation, binding, Embedded Topics, Scope |
| `name-scope-embedded4.ctm` | 3284 | definition / invocation, binding, Embedded Topics, Scope |
| `occurrence-scope-embedded3.ctm` | 2277 | definition / invocation, binding, Embedded Topics, Scope |
| `occurrence-scope-embedded4.ctm` | 3457 | definition / invocation, binding, Embedded Topics, Scope |
| `prefix-template-scope.ctm` | 263 | definition / invocation |
| `template-ambiguous-parameter.ctm` | 376 | definition / invocation, binding |
| `template-ambiguous-parameter2.ctm` | 407 | definition / invocation, binding |
| `template-ambiguous-parameter3.ctm` | 399 | definition / invocation, binding |
| `template-ambiguous-parameter4.ctm` | 1506 | definition / invocation, binding, type relationships |
| `template-assoc-embedded-topic.ctm` | 23 | definition / invocation, Embedded Topics |
| `template-duplicate-name.ctm` | 438 | definition / invocation, binding |
| `template-forward-ref.ctm` | 825 | definition / invocation, binding |
| `template-invocation-embedded.ctm` | 401 | definition / invocation, binding, Embedded Topics |
| `template-invocation-embedded2.ctm` | 401 | definition / invocation, binding, Embedded Topics |
| `template-invocation-noargs-isa.ctm` | 963 | definition / invocation, type relationships |
| `template-invocation-noargs2.ctm` | 828 | definition / invocation, binding |
| `template-invocation-prefix-notation.ctm` | 328 | definition / invocation, binding |
| `template-invocation-twice.ctm` | 402 | definition / invocation, binding |
| `template-invocation-wildcard-named.ctm` | 331 | definition / invocation, binding, Wildcards |
| `template-invocation-wildcard-named2.ctm` | 331 | definition / invocation, binding, Wildcards |
| `template-invocation-wildcard-named3.ctm` | 646 | definition / invocation, binding, Wildcards |
| `template-invocation-wildcard-named4.ctm` | 331 | definition / invocation, Wildcards |
| `template-invocation-wildcard-named5.ctm` | 577 | definition / invocation, Wildcards |
| `template-invocation-wildcard-named6.ctm` | 581 | definition / invocation, binding, Wildcards |
| `template-invocation-wildcard.ctm` | 484 | definition / invocation, binding, Wildcards |
| `template-item-identifier.ctm` | 131 | definition / invocation, binding |
| `template-item-identifier2.ctm` | 131 | definition / invocation, binding |
| `template-item-identifier4.ctm` | 157 | definition / invocation, binding |
| `template-nested-occtype.ctm` | 576 | definition / invocation, Embedded Topics |
| `template-nested-occtype2.ctm` | 737 | definition / invocation, Embedded Topics |
| `template-noop.ctm` | 23 | definition / invocation |
| `template-noop2.ctm` | 23 | definition / invocation |
| `template-noop3.ctm` | 23 | definition / invocation, binding, type relationships |
| `template-references.ctm` | 23 | definition / invocation, type relationships |
| `template-simple.ctm` | 114 | definition / invocation |
| `template-subject-identifier.ctm` | 141 | definition / invocation, binding |
| `template-subject-locator.ctm` | 131 | definition / invocation, binding |
| `template-subject-locator2.ctm` | 131 | definition / invocation, binding |
| `template-subject-locator4.ctm` | 194 | definition / invocation, binding |
| `template-topic-nested.ctm` | 678 | definition / invocation, Embedded Topics, Reifier |
| `template-topic-nested2.ctm` | 596 | definition / invocation, Embedded Topics, Reifier |
| `template-typed-value.ctm` | 351 | definition / invocation, binding |
| `template-wildcard-named.ctm` | 211 | definition / invocation, Wildcards |
| `template-wildcard-named2.ctm` | 211 | definition / invocation, Wildcards |
| `template-wildcard-named3.ctm` | 211 | definition / invocation, Wildcards |
| `template-wildcard-named4.ctm` | 919 | definition / invocation, binding, Wildcards |
| `template-wildcard.ctm` | 203 | definition / invocation, Wildcards |
| `template-wildcard2.ctm` | 293 | definition / invocation, Wildcards |
| `tmlab-tmql-issue-48.ctm` | 2358 | definition / invocation, binding, Wildcards, type relationships |
| `topic-embedded-template-invocation.ctm` | 1357 | definition / invocation, binding, Embedded Topics, type relationships |
| `topic-identifier-eq-template-name.ctm` | 207 | definition / invocation |
| `topic-template-invocation-unary.ctm` | 328 | definition / invocation, binding |
| `topic-template-invocation.ctm` | 328 | definition / invocation, binding |
| `variant-scope-embedded3.ctm` | 2547 | definition / invocation, binding, Embedded Topics, Scope |
| `variant-scope-embedded4.ctm` | 3734 | definition / invocation, binding, Embedded Topics, Scope |

| Negative original | Required specific code |
|---|---|
| `embedded-topic-template.ctm` | `:INVALID-TEMPLATE-BODY` |
| `occurrence-explicit-datatype-as-parameter.ctm` | `:VARIABLE-DATATYPE` |
| `prefix-template-scope.ctm` | `:INVALID-TEMPLATE-BODY` |
| `template-bad-type.ctm` | `:INVALID-TEMPLATE-ARGUMENT` |
| `template-missing-args.ctm` | `:TEMPLATE-ARITY` |
| `template-missing-def.ctm` | `:UNDEFINED-TEMPLATE` |
| `template-name-collision.ctm` | `:DUPLICATE-TEMPLATE` |
| `tm-reifier-in-template.ctm` | `:INVALID-TEMPLATE-BODY` |
| `variable-undefined.ctm` | `:VARIABLE-OUTSIDE-TEMPLATE` |
| `variable-undefined2.ctm` | `:VARIABLE-OUTSIDE-TEMPLATE` |
