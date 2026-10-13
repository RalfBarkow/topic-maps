# Boundaries and execution contracts

`topic-maps` currently contains file discovery, case records, correspondence
checks, result classification and JSON reporting. `topic-maps/tests` tests
those mechanisms. Neither system reads CTM tokens or constructs Topic Maps.
No test invokes a disguised or mock parser.

Future components have distinct responsibilities:

| Future system | Responsibility | Slice 0 state |
| --- | --- | --- |
| `topic-maps/ctm` | CTM syntax plus orchestration of deserialization, prefix/template context and resource resolution | Not defined |
| `topic-maps/tmdm` | Semantic information items, identity/merging and model invariants | Not defined |
| `topic-maps/cxtm` | Canonical representation of a model for comparison | Not defined |
| `topic-maps/tests` | Contracts and independent fixtures, later executor adapters | Implemented as infrastructure only |

CTM's syntax-to-model mapping is governed by ISO/IEC 13250-6:2010, and model
semantics by ISO/IEC 13250-2:2006. A later CXTM implementation must consult the
applicable canonicalization standard, ISO/IEC 13250-4; the current baselines
are testing evidence, not its normative definition. Future CTM tests will need
both a reader/model and a canonicalizer to establish semantic equality with a
baseline. A reader that merely accepts a valid file will not suffice.

No HyperDoc classes, Inspector, HyperBook, CLOG, TALA or SQLite dependency is
present. No live SBCL image is changed. SBCL-specific launch flags are isolated
in `scripts/test.sh`; the library uses ANSI Common Lisp plus ASDF/UIOP.
`src/filesystem.lisp` isolates UIOP directory/path utilities because ANSI Common
Lisp lacks a portable recursive filesystem traversal operation. ASDF locates
project resources. SHA-256 verification is an external maintenance operation
using Python's standard library, not a dependency loaded into Lisp.

## Document-IRI policy

Every imported case receives this explicit logical absolute Document IRI:

```
https://ctm-tests.example.invalid/<pinned-commit>/<case-id>
```

For example, `ctm/in/simple.ctm` gets
`https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/simple.ctm`.
These are test execution inputs, not productive Subject Identifiers or web
endpoints. No request is made to them. `.invalid` deliberately prevents any
assumption of a real host. Case IDs are upstream-relative pathnames; the
revision is carried by corpus metadata and by the Document IRI.

Source pathnames can change when the checkout moves; Document IRIs cannot.
JSON pathnames are relative to `vendor/cxtm`, avoiding machine-specific paths.
`discover-corpus :document-base ...` allows an explicit alternate absolute
HTTP(S) directory IRI. No base is silently constructed from a temporary path.
The narrow fixture-IRI assignment is not a CTM IRI resolver: it performs no
percent decoding, URI normalization or CTM identifier interpretation.

CTM §3.2 makes the Document IRI an input to deserialization; §§3.3.3 and 3.3.6
use it for references and local identifiers. The clause links are in coverage.
A future executor must pass the recorded IRI, not the input's file URL, to the
reader. Its resource adapter will map the reported logical resource IRIs to
local pinned `.sub`/`.sub2` resources, including XML where supplied. The adapter
must preserve relative-reference behavior and restrict acquisition to local
fixtures during conformance testing. None of that executor is implemented here.

Baselines contain relative locators such as `#topic`. A future canonicalizer
must apply the standard's rules with the same Document-IRI context; this slice
does not normalize baselines, turn them into models or claim that the chosen
policy already produces matching canonical output. Absolute/relative reference
cases are among the proposed Slice 1 tests.

## Outcomes are supplied, never inferred from missing implementation

Imported valid cases expect `:CXTM-EQUAL`; invalid cases expect
`:CTM-REJECTION`. At discovery, actual outcome is NIL and status is `:NOT-RUN`.
`record-result` classifies an executor-supplied result; it executes nothing.

| Supplied outcome | Expected CXTM equality | Expected CTM rejection |
| --- | --- | --- |
| `:CXTM-MATCH` | PASS | FAIL |
| `:CXTM-MISMATCH` | FAIL | FAIL |
| `:CTM-REJECTION` | FAIL | PASS |
| `:CTM-ACCEPTANCE` | FAIL | FAIL |
| `:UNSUPPORTED` | UNSUPPORTED | UNSUPPORTED |
| `:EXECUTION-ERROR` | FAIL | FAIL |
| No execution / `reset-result` | NOT-RUN | NOT-RUN |

An identified CTM syntax or semantic rejection is distinct from an unsupported
feature and from I/O/runtime failure. Exceptions must not automatically count
as successful invalid tests. A future adapter must classify them explicitly.
Recorded diagnostics survive until reset. Infrastructure fixtures exercise the
protocol using supplied outcomes without examining or recognizing CTM text.
Filesystem fixtures deliberately omit a baseline and include an orphan;
correspondence problems are reported without pretending any CTM was executed.

Reviewed specification clauses are stored in `references/reviewed-clauses.sexp`.
Other records have an empty clause list, meaning review pending. No mapping is
inferred from a filename alone. JSON encodes keywords as lowercase status
strings; the Lisp records retain the requested keyword statuses.
