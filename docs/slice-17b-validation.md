# Slice 17B — isa/ako and Core Subject validation

Base: `bdc56a8236c6e6180df217d37e82846025026096`; branch
`codex/ctm-slice-17b`. Source/artifact hashes, runtime and UTC interval are in
`reports/slice-17b/execution.json`.

From the repository root:

```sh
python3 scripts/validate-slice-17b.py --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

The full retained suite runs in fresh SBCL 2.5.4 under `sandbox-exec` denying
network access, with user/system startup and inherited ASDF registry excluded.
There are no extra SBCL versions, checkout relocations or cache-policy changes.

## Results

- **11,317 Lisp assertions pass: 10,301 retained and 1,016 new.** Consumed
  unsupported-feature assertions now check actual isa/ako model semantics;
  all retained suite totals and model observations are preserved.
- Both Python unit tests, 16,294 independent NFC comparisons and all independent
  report checkers pass. No Quicklisp, external server or HyperDoc system is used.
- All 13 selected original CTM documents deserialize to actual TMDM objects and
  match their unchanged original CXTM baselines byte-for-byte. The complete list,
  byte counts, object relations and normative clauses are in
  `reading-type-relationships.md`; actual bytes are under `reports/slice-17b/actual/`.
- Exactly those 13 imported cases transition NOT-RUN → PASS. Corpus totals:
  **120 PASS, 2 FAIL, 0 UNSUPPORTED, 151 NOT-RUN**. This comprises 108 positive
  byte-exact contracts and 12 specific rejection contracts. Both existing
  DateTime normative baseline FAILs remain unchanged, including their outputs
  and diagnostic text. No unimplemented contract is promoted.
- All 95 prior passing CXTM outputs, both known discrepancy outputs, all other
  imported case records and every prior model observation are compared to 17A.
  Original corpus and reference hashes are checked before/after execution.

## Core Subject and failure evidence

The protected vocabulary is checked against all eight exact §7 locators in the
published TMDM 2006 text. Its six relationship Subjects are also checked as actual
Association/Role Type Topics. The §7.5 `name-type` versus CTM §3.11 `topic-name`
spelling distinction is explicit; no guessed alias or Name-Type rewrite occurs.

There are **304 executed atomic conflict observations**. They cover every
ordered pair of different Core Subjects via explicit merge, SI bridge, II bridge,
shared Subject Locator and interning a new Core SI on an existing II-bound Topic.
Additional tests cover retained alias chains, an entire prospective transitive
normalization, all five structurally mergeable item kinds, a direct Reifier
setter conflict, and a four-level Name→Occurrence→Association→Role cascade.
Interning before a late conflict does not leave a new empty Topic behind.

Each rejection asserts the condition class/code, equality of the complete
original graph state and held identifier/forward/Reifier slots, and preservation
of existing model invariants for initially valid graphs. White-box unnormalized
inputs are explicitly marked; their initial graphs are preserved on rejection.
This is the existing local preflight policy, not a normative transaction claim.

Positive tests cover same-Core idempotence, legal aliases, copied public
vocabulary strings, preserved locator categories, short/long Association equality,
all shared reference forms, replacement handles, cyclic ako, non-materialization
of inferred relationships, pure deterministic CXTM, and specific CTM positions.
The independent Python checker compares all 13 actual reference graphs against
the baseline XML separately from the raw byte checks.

`base-control.log` restores only the base definitions in a separate disposable
process: the former Core merge is accepted there and both keywords are rejected
as unsupported. `describe.log` records executable inspection forms in another
fresh process; its printed addresses are historical process-local observations.

Templates, Include/Mergemap, cross-document merging, XTM deserialization, further
datatypes and HyperDoc changes are excluded. No push or deployment is performed.
