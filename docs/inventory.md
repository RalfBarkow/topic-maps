# Pinned corpus and consulted references

## Location and base evidence

The user approved a new independent Git repository at
`/Users/rgb/workspace/topic-maps`, branch `codex/ctm-slice-0`.
The directory was checked twice and did not exist; no existing contents were
overwritten. The chosen implementation base is an **empty new repository**,
with no parent/base commit. The Slice 0 delivery is its root commit, obtained
with `git rev-parse HEAD`. No HyperDoc code or commit is the implementation base.

Before creating it, Git inspection established:

| Observed checkout | Branch | HEAD | State |
| --- | --- | --- | --- |
| `/Users/rgb/workspace/hyperdoc-dreyeck-ch` | `dreyeck.ch` | `9a1764250f31013a50965aad324dd72c0662b9cc` | Clean |
| `/Users/rgb/workspace/hyperdoc-querying-topicmaps` | `codex/querying-topicmaps` | `ca3c46b6e37b8e5e253c4faabc4819ff36bc64e8` | Clean |

The actual repository is the shared HyperDoc Git repository whose primary
worktree is `/Users/rgb/workspace/hyperdoc`. `git worktree list --porcelain`
identified the above worktrees. HyperDoc's ASDF source/test component conventions,
`nix/catalog-check.nix` fresh-process flags, and `flake.nix`/`flake.lock` were
inspected read-only. The independent project uses ASDF test-op and its own
source registry; only the existing nixpkgs revision was reused for a minimal
dev shell. No HyperDoc runtime dependencies or authoring systems were imported.
No running SBCL image, server, browser application, SSH session or deployment
was used for this slice.

## Exact versions

Published ISO standards are the normative authority. These are the consulted
web references, not redistributed standard documents:

| Reference | Edition/revision |
| --- | --- |
| [CTM](https://www.isotopicmaps.org/ctm/ctm.html) | ISO/IEC 13250-6:2010; consulted web bytes SHA-256 recorded |
| [TMDM](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) | ISO/IEC 13250-2:2006, dated SC34 text 2006-06-18; consulted bytes SHA-256 recorded |
| [Heuer CXTM](https://github.com/heuer/cxtm/tree/cd165b150176c1d6842b37be9cc9051b40d4996b) | `cd165b150176c1d6842b37be9cc9051b40d4996b` |
| [Ontopia](https://github.com/ontopia/ontopia/tree/49071fea60243540b5581b78702a77ba8064235d) | `49071fea60243540b5581b78702a77ba8064235d` |
| [Ontopia externals](https://github.com/ontopia/externals/tree/acba0660303cf9a3bfcb0c0df81319f1e1065bef) | `acba0660303cf9a3bfcb0c0df81319f1e1065bef` |
| nixpkgs | `50ab793786d9de88ee30ec4e4c24fb4236fc2674`; independent flake lock |

[Sources metadata](../references/sources.json) records consultation date,
exact immutable source URLs, file digests, web snapshot digests, licenses and
distribution comparisons. For Ontopia, the consulted files are its license,
`CTMTestCase.java`, `CTMInvalidTestCase.java`, `CTMTopicMapReader.java`, and `ctm.g`.
The Java tests use separate valid/invalid directories, compare valid canonical
results against baselines and distinguish invalid-topic-map rejection from
unexpected exceptions. Ontopia is implementation evidence, not normative
authority; none of its implementation is copied or run in this project.

The externals distribution has **201 valid CTM files, 27 invalid CTM files and
201 CXTM baselines**, according to its pinned recursive Git tree. Its own
`STATUS.txt` refers to the **CTM and CXTM drafts of 2009-03-xx**. It is not the
same revision of the suite used here. The pinned tree and Git-blob comparison
are recorded in references; differing files are listed, without assuming test
equivalence. The distribution's README describes a Maven repackaging of CXTM
inputs. It is not used as a replacement corpus.

## Acquisition and byte preservation

The complete Heuer Git tree was acquired with:

```sh
git clone https://github.com/heuer/cxtm.git /private/tmp/ctm-slice-0-cxtm
git -C /private/tmp/ctm-slice-0-cxtm rev-parse HEAD
git -C /private/tmp/ctm-slice-0-cxtm archive --format=tar \
  cd165b150176c1d6842b37be9cc9051b40d4996b
```

The archive was extracted under `vendor/cxtm`, without edits, conversion of
encodings or nested Git metadata. Its SHA-256 is
`19d88764908426ca1971213ef36063a72994a4a199bb3d46ac8b63aa435198d2`.
[corpus-lock.json](../references/corpus-lock.json) inventories **all 2,006
upstream files** by original path, size and SHA-256. The Lisp lock's expected
counts were generated from the recounted CTM subtree. They are observations
at this revision, not assumptions imported from a previous GitHub inspection.

`python3 scripts/corpus.py acquire` reproduces the acquisition when the vendor
directory is absent; existing content is verified and never overwritten.
`python3 scripts/corpus.py verify` checks the complete manifest, including
missing, additional and changed bytes, with no network access.
Independent fixtures test those failure modes. The upstream public-domain
notice and no-warranty statement remain in `vendor/cxtm/LICENSE.txt`.

## Original structure and CTM inventory

The full upstream root structure is retained:

```
.gitattributes  CHANGES.txt  LICENSE.txt  README  release.py
ctm/  jtm/  jtm11/  ltm/  rdf/  snello/  tmcl/  tmxml/
web/  xtm1/  xtm2/  xtm21/
```

Only the CTM subtree supplies this project's initial cases:

| Original directory/file | Observed count | Classification |
| --- | ---: | --- |
| `ctm/in/*.ctm` | 231 | Valid-category CTM test inputs |
| `ctm/invalid/*.ctm` | 42 | Invalid-category CTM test inputs |
| `ctm/baseline/*.ctm.cxtm` | 231 | Expected canonical baselines |
| `ctm/in/*.sub` | 13 | Include/mergemap resources |
| `ctm/in/*.sub2` | 1 | Additional include resource |
| `ctm/invalid/*.sub` | 5 | Invalid-case include/mergemap resources |
| `ctm/baseline/name-type.ctm` | 1 | XML-shaped upstream artifact; not a CTM input or a `.cxtm` baseline |
| `ctm/STATUS.txt`, `ctm/MISSING.txt` | 2 | Draft qualification and upstream gap notes |

There are **526 files** in this subtree: 273 inputs, 231 baselines and 22
auxiliaries. Every valid input corresponds to `baseline/<input-name>.cxtm`.
Missing baselines: **0**. Unmatched baselines: **0**. Invalid cases have no
expected CXTM baseline. The JSON report lists every case, baseline and auxiliary
resource. Auxiliary contents can be CTM fragments or XML; no decoder is applied
by discovery, including to the ISO-8859-5 encoded CTM test.

## Limitations retained from upstream

**The imported CTM tests target the draft dated 2010-03-31. Passing them alone
would not establish full ISO/IEC 13250-6:2010 conformity.** They are independent
testing evidence; all imported cases remain NOT-RUN in Slice 0.

The upstream README describes the CTM collection as incomplete. `MISSING.txt`
asks for more nested-topic, non-HTTP IRI and template tests, plus invalid
duplicate-template and possible infinite-template-loop cases. Those notes are
preserved as historical gap statements, not treated as proof of current total
absence: the pinned tree already includes `subject-identifier-non-http.ctm`
and `invalid/template-name-collision.ctm`. Complete edge-case coverage and a
published-edition-versus-draft audit still require review. No filename-based
inventory can establish semantic completeness or baseline correctness.
