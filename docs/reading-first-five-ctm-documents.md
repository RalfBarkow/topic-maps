# Reading the First Five CTM Documents

These five documents are the original inputs from the pinned public-domain
CXTM corpus at `cd165b150176c1d6842b37be9cc9051b40d4996b`. It targets the
**CTM draft dated 2010-03-31**; successful tests alone do not establish full
ISO/IEC 13250-6:2010 conformity. The published standards remain authoritative.

CTM [§3.3.6](https://www.isotopicmaps.org/ctm/ctm.html#sec-topic-identity)
determines which identifier property receives each reference. The local form
uses the explicit Document IRI. TMDM [§5.3.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/#d0e1029)
keeps the three properties distinct and specifies identity. CTM
[§3.11](https://www.isotopicmaps.org/ctm/ctm.html#sec-name) supplies the default
name-type Subject Identifier; TMDM [§5.4](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/#sect-topic-name)
requires a Name item whose type is a Topic.

The model observations below come from the actual reader results and accessor
checks, not from fabricated XML. Ordinals label objects for inspection; they
are neither identities nor canonical ordering. Other set-valued properties
are implicitly empty and single-valued properties null (CTM §3.2). No scope,
variant, role or occurrence syntax is implemented.

## simple.ctm

Actual unmodified source ([original file](../vendor/cxtm/ctm/in/simple.ctm)):

```ctm
topic.
```

Original bytes: 6; no terminal newline. The newline before the Markdown closing fence is presentation only.

Document IRI:

```text
https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/simple.ctm
```

**Normative expectation:** One Topic with an Item Identifier formed from this Document IRI and `#topic`; no name or name-type Topic.

Applicable clauses: CTM 3.3.6, CTM 3.8, CTM 3.2, TMDM 5.1, TMDM 5.2, TMDM 5.3.5. TMDM §5.2 supplies the containing Topic Map.

**Upstream evidence:** [original CXTM baseline](../vendor/cxtm/ctm/baseline/simple.ctm.cxtm) contains the corresponding topics and identifier/name properties. The baseline is unchanged.

**Local observation:** 1 Topic object(s), 0 Topic Name object(s), inside one Topic Map.

| Object | Item Identifiers | Subject Identifiers | Subject Locators | Name item(s) |
| --- | --- | --- | --- | --- |
| Topic 1 | `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/simple.ctm#topic` | empty | empty | none |

Every Topic parent is the actual containing map. Name type/parent checks use `EQ`, not matching display labels.

**Result:** semantic assertions PASS; selected baseline-property evidence PASS. The imported `:CXTM-EQUAL` contract remains **NOT-RUN**, because no canonicalizer exists.

## subject-identifier.ctm

Actual unmodified source ([original file](../vendor/cxtm/ctm/in/subject-identifier.ctm)):

```ctm
<http://psi.example.org/fake>.
```

Original bytes: 30; no terminal newline. The newline before the Markdown closing fence is presentation only.

Document IRI:

```text
https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/subject-identifier.ctm
```

**Normative expectation:** One Topic with the given Subject Identifier; no Item Identifier or Subject Locator is implicitly added.

Applicable clauses: CTM 3.3.6, CTM 3.8, TMDM 5.1, TMDM 5.2, TMDM 5.3.5. TMDM §5.2 supplies the containing Topic Map.

**Upstream evidence:** [original CXTM baseline](../vendor/cxtm/ctm/baseline/subject-identifier.ctm.cxtm) contains the corresponding topics and identifier/name properties. The baseline is unchanged.

**Local observation:** 1 Topic object(s), 0 Topic Name object(s), inside one Topic Map.

| Object | Item Identifiers | Subject Identifiers | Subject Locators | Name item(s) |
| --- | --- | --- | --- | --- |
| Topic 1 | empty | `http://psi.example.org/fake` | empty | none |

Every Topic parent is the actual containing map. Name type/parent checks use `EQ`, not matching display labels.

**Result:** semantic assertions PASS; selected baseline-property evidence PASS. The imported `:CXTM-EQUAL` contract remains **NOT-RUN**, because no canonicalizer exists.

## subject-locator.ctm

Actual unmodified source ([original file](../vendor/cxtm/ctm/in/subject-locator.ctm)):

```ctm
=<http://www.example.org/resource>.
```

Original bytes: 35; no terminal newline. The newline before the Markdown closing fence is presentation only.

Document IRI:

```text
https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/subject-locator.ctm
```

**Normative expectation:** One Topic with the given Subject Locator; no Subject Identifier or Item Identifier is implicitly added.

Applicable clauses: CTM 3.3.6, CTM 3.8, TMDM 5.1, TMDM 5.2, TMDM 5.3.5. TMDM §5.2 supplies the containing Topic Map.

**Upstream evidence:** [original CXTM baseline](../vendor/cxtm/ctm/baseline/subject-locator.ctm.cxtm) contains the corresponding topics and identifier/name properties. The baseline is unchanged.

**Local observation:** 1 Topic object(s), 0 Topic Name object(s), inside one Topic Map.

| Object | Item Identifiers | Subject Identifiers | Subject Locators | Name item(s) |
| --- | --- | --- | --- | --- |
| Topic 1 | empty | empty | `http://www.example.org/resource` | none |

Every Topic parent is the actual containing map. Name type/parent checks use `EQ`, not matching display labels.

**Result:** semantic assertions PASS; selected baseline-property evidence PASS. The imported `:CXTM-EQUAL` contract remains **NOT-RUN**, because no canonicalizer exists.

## item-identifier.ctm

Actual unmodified source ([original file](../vendor/cxtm/ctm/in/item-identifier.ctm)):

```ctm
^<http://www.example.org/#topic>.
```

Original bytes: 33; no terminal newline. The newline before the Markdown closing fence is presentation only.

Document IRI:

```text
https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/item-identifier.ctm
```

**Normative expectation:** One Topic with the explicit Item Identifier; its locator is independent of the supplied Document IRI.

Applicable clauses: CTM 3.3.6, CTM 3.8, TMDM 5.1, TMDM 5.2, TMDM 5.3.5. TMDM §5.2 supplies the containing Topic Map.

**Upstream evidence:** [original CXTM baseline](../vendor/cxtm/ctm/baseline/item-identifier.ctm.cxtm) contains the corresponding topics and identifier/name properties. The baseline is unchanged.

**Local observation:** 1 Topic object(s), 0 Topic Name object(s), inside one Topic Map.

| Object | Item Identifiers | Subject Identifiers | Subject Locators | Name item(s) |
| --- | --- | --- | --- | --- |
| Topic 1 | `http://www.example.org/#topic` | empty | empty | none |

Every Topic parent is the actual containing map. Name type/parent checks use `EQ`, not matching display labels.

**Result:** semantic assertions PASS; selected baseline-property evidence PASS. The imported `:CXTM-EQUAL` contract remains **NOT-RUN**, because no canonicalizer exists.

## name.ctm

Actual unmodified source ([original file](../vendor/cxtm/ctm/in/name.ctm)):

```ctm
topic
- "Name";.
```

Original bytes: 16; no terminal newline. The newline before the Markdown closing fence is presentation only.

Document IRI:

```text
https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/name.ctm
```

**Normative expectation:** Two Topics and one Topic Name: the local Topic, its Name item with value `Name`, and the default type Topic identified by `http://psi.topicmaps.org/iso13250/model/topic-name`. The Name type is that actual Topic object; the Name parent is the local Topic.

Applicable clauses: CTM 3.8, CTM 3.11, TMDM 5.1, TMDM 5.2, TMDM 5.3.5, TMDM 5.4. The default-type rule is CTM §3.11, not an assumption inferred solely from the baseline. TMDM §5.2 supplies the containing Topic Map.

**Upstream evidence:** [original CXTM baseline](../vendor/cxtm/ctm/baseline/name.ctm.cxtm) contains the corresponding topics and identifier/name properties. The baseline is unchanged.

**Local observation:** 2 Topic object(s), 1 Topic Name object(s), inside one Topic Map.

| Object | Item Identifiers | Subject Identifiers | Subject Locators | Name item(s) |
| --- | --- | --- | --- | --- |
| Topic 1 | `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/name.ctm#topic` | empty | empty | value `Name`, type → Topic 2, parent → Topic 1 |
| Topic 2 | empty | `http://psi.topicmaps.org/iso13250/model/topic-name` | empty | none |

Every Topic parent is the actual containing map. Name type/parent checks use `EQ`, not matching display labels.

**Result:** semantic assertions PASS; selected baseline-property evidence PASS. The imported `:CXTM-EQUAL` contract remains **NOT-RUN**, because no canonicalizer exists.

## Relative locators in the baselines

For `simple.ctm` and `name.ctm`, the baseline's `#topic` is interpreted in the
recorded Document-IRI context. The actual Item Identifier is the full Document
IRI plus that fragment. This selected-property interpretation does not validate
a future canonicalizer's relativization or ordering. No XML is produced or
compared byte-for-byte by this slice.

## The negative case

`ctm/invalid/prefix-undefined.ctm` contains a leading newline, `ex:fake.`, then a
trailing newline. CTM §3.3.4 requires a prefix binding. The actual condition is
`TOPIC-MAPS.CTM:UNDEFINED-PREFIX`, code `:UNDEFINED-PREFIX`, character offset 1,
line 2, column 1. Its imported `:CTM-REJECTION` contract is PASS. I/O failures,
unsupported constructs and unrelated exceptions cannot satisfy this check.

## Standard Common Lisp inspection

Use a new SBCL process. These forms load only the independent project:

```lisp
(require :asdf)
(asdf:initialize-source-registry
 '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/ctm")
(defparameter *document-iri*
  "https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/name.ctm")
(defparameter *map*
  (topic-maps.ctm:deserialize-file
   (asdf:system-relative-pathname "topic-maps" "vendor/cxtm/ctm/in/name.ctm")
   :document-iri *document-iri*))
(describe *map*)
(defparameter *topic* (first (topic-maps.tmdm:topic-map-topics *map*)))
(describe *topic*)
(defparameter *name* (first (topic-maps.tmdm:topic-names *topic*)))
(describe *name*)
(describe (topic-maps.tmdm:topic-name-type *name*))
(eq *topic* (topic-maps.tmdm:topic-name-parent *name*)) ; => T
```

These forms were exercised in a fresh process; the captured
[DESCRIBE output](../reports/slice-1/describe.log) exposes the actual objects.
Memory addresses in that log are observations of one run, not stable identity.
The deterministic [semantic report](../reports/slice-1/semantics.json) exposes
properties separately from [imported contracts](../reports/slice-1/validation.json).
The test-only `topic-maps.ctm.tests:observations` operation also returns the
actual model objects after `asdf:test-system "topic-maps/ctm/tests"`.
