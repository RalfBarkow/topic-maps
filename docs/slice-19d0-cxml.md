# Slice 19D0 — Pinned CXML provisioning and qualification

Source provisioning succeeds. **Unmodified parser qualification fails.**
This is not an XTM implementation, and it does not authorize proceeding to 19D1.

## Source identity

Base: `bc4fcf0f126bab6567b37a21fc8c8eab2944c152`.
The unchanged Nixpkgs pin is `50ab793786d9de88ee30ec4e4c24fb4236fc2674`.
`lib.cxmlEnvironment` follows the pinned CXML package's transitive `lispLibs`
and uses their **sources**, not Nixpkgs SBCL 2.4.10 FASLs.

All hashes below are recursive SHA-256 NAR hashes in Nix base32, not compressed
archive hashes. They come from the pinned package definitions and are checked
again against the materialized source directories by `validate-cxml.py`.

| Package | Version | SHA-256 |
|---|---|---|
| cxml | 20200610-git | `18fls3bx7vmnxfa6qara8fxp316d8kb3izar0kysvqg6l0a45a51` |
| closure-common | 20181018-git | `0k5r2qxn122pxi301ijir3nayi9sg4d7yiy276l36qmzwhp4mg5n` |
| babel | 20241012-git | `0359bj3yr6frybcmg8qr5vi4q8hzbsb7hmvxdc0jgkfz3c33q667` |
| alexandria | 20241012-git | `0jq0n59s0r9yl374f0zpdnaflb5g853yqvax7ka8rnypspyykwdw` |
| trivial-features | 20230618-git | `0r33ycg1wsmglbsychglzkd6fachnnqfzd0w9mhpwi6cz94hx7c3` |
| trivial-gray-streams | 20241012-git | `0iw6q5hx7x8sc5s7ikvsjccsksbm0rd13d54mkrg62sc56hjywrm` |
| puri | 20201016-git | `0gq2rsr0aihs0z20v4zqvmdl4szq53b52rh97pvnmwrlbn4mapmd` |

Dependency graph: CXML → closure-common, PURI, trivial-gray-streams;
closure-common → Babel, trivial-gray-streams; Babel → Alexandria, trivial-features.
Only CXML and closure-common required the separately authorized acquisition:

```sh
nix store prefetch-file --json --unpack --name source \
  --expected-hash sha256-oahCFKDm4a39BFn9ONZEzYRxu0MqK2yU67bu09fQ1KE= \
  http://beta.quicklisp.org/archive/cxml/2020-06-10/cxml-20200610-git.tgz
nix store prefetch-file --json --unpack --name source \
  --expected-hash sha256-trxKLuS/YjOoOcJHfxp5OkWv7MhRxgBG7FeIYDsWuUw= \
  http://beta.quicklisp.org/archive/closure-common/2018-10-18/closure-common-20181018-git.tgz
```

Both returned exactly the expected hashes and source paths. The other five
source directories already existed. No other package was fetched; there is
no Quicklisp installation, runtime download, upstream patch or new Nixpkgs pin.

## Offline loading and reproduction

The default DevShell exports the same `CL_SOURCE_REGISTRY` as the independently
evaluable source environment. It excludes inherited user registries; the project
itself can still be loaded explicitly with `asdf:load-asd` as before.

```sh
cd /Users/rgb/workspace/topic-maps
export CL_SOURCE_REGISTRY="$(nix eval --offline --option eval-cache false --raw \
  .#lib.cxmlEnvironment --apply 'f: (f "aarch64-darwin").sourceRegistry')"
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --noinform --no-sysinit --no-userinit --non-interactive \
  --eval '(require :asdf)' --eval '(asdf:load-system "cxml")'

python3 scripts/validate-cxml.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl
```

The first command loads CXML successfully. The validator deliberately exits
**1** when XML qualification fails, after saving both XML runs and the complete
retained regression. It never converts a failed qualification to PASS merely
because source provisioning or CTM regression succeeds.

The per-command `eval-cache false` avoids a local Nix evaluation-cache error
about `dynamic-derivations`; no Nix settings or cache contents are changed.
The Lisp runs receive the evaluated Nix source environment and use the existing
Nix-store SBCL 2.5.4. They do not run inside a newly built default DevShell.
The pinned default DevShell/toolchain is not fully provisioned: building it and
a complete offline rebuild are **NOT-RUN**, not implied by these tests.
No FASL cache policy, relocation or second SBCL version is introduced.

## Explicit external-resource policy

`tests/cxml-probe.lisp` contains a qualification-only SAX handler and parsing
configuration. It is not a production XML or XTM API and is not installed
globally by ASDF loading. Future callers must explicitly apply the policy:

* Raw octet input, namespace processing enabled, no DTD validation.
* Every DOCTYPE is rejected by `sax:start-dtd`, before subset processing.
* `:disallow-internal-subset t` is a second guard against internal subsets.
* `:entity-resolver` **signals** `external-resource-forbidden`; it never returns
  NIL. Catalog resolution is disabled and each parse has a fresh DTD cache.

The tests exercise local-file and HTTP external DTDs, general entities and
parameter entities. Resolver-only probes temporarily permit DOCTYPEs so they
test the resolver independently of the first guard. A test-only interception
of `cxml::uri-to-pathname` traps the exact fallback before OPEN; it is restored
in the disposable process. The rejecting resolver never reaches this fallback.
A NIL-resolver counterprobe does reach it and is intercepted before any I/O.
Thus filesystem/network denial is not mistaken for successful resolver refusal.
The complete probes run twice in fresh processes with all network access denied.

CXML documents the NIL fallback in `xml/xml-parse.lisp:3179`; the fallback OPEN
is at line 1064, and the DOCTYPE callback precedes subset processing at line 2578
in the unchanged CXML source. No external resource is fetched by these probes.

## Observed encoding defects — not normalized away

The repeated matrix records **50 PASS and 8 FAIL per process**. Namespaces,
expanded attribute names, duplicate-attribute rejection, nesting errors,
ordinary UTF-8, BMP UTF-16 with BOM, XML line/attribute normalization and the
external-resource policy pass. All eight failures remain visible:

1. **Valid UTF-16 supplementary characters rejected:** U+1F98A has surrogate
   code units D83E DD8A (LE bytes `3e d8 8a dd`). The LE/BE BOM inputs are
   rejected, as is the LE BOM input without an XML declaration. In the original
   `closure-common/encodings.lisp:172` and `:209`, the second-code-unit range
   check examines `x` again instead of `y`. These are three failed matrix cells.
2. **Invalid UTF-8 accepted:** the content bytes `c3 28` are not valid UTF-8.
   CXML accepts them and reports U+00E8. The UTF-8 decoder beginning at
   `closure-common/encodings.lisp:222` masks continuation bytes without checking
   their required prefix. This is one failed rejection test. Python's strict
   codecs independently confirm both this invalid sequence and the valid
   UTF-16 surrogate pair; they are byte-fixture checks, not a substitute parser.
3. **Additional encoding-support observations:** explicit `UTF-16LE`/`UTF-16BE`
   inputs without BOM fail for BMP and supplementary content (four cells).
   These additional encoding-name forms are reported separately from the
   decisive XML UTF-8/UTF-16 failures above. The pinned input stream recognizes
   UTF-16 by BOM only (`closure-common/xstream.lisp:366`). Generic `UTF-16`
   declarations also produce an unsupported-encoding warning even when BOM
   detection lets BMP input parse; `cxml/xml/xml-parse.lisp:2520` is involved.

The original libraries are not repaired, pre-decoded, filtered or replaced in
these tests. A dependency correction needs an explicit, reviewable follow-up:
repair/replace the encoding path with pinned, tested changes, retain upstream
source hashes, and re-run strict malformed-input and surrogate-boundary tests.
This is more than making the already pinned sources available. No new parser
implementation, unapproved source acquisition or XTM work was started.

## Retained regression and evidence

`reports/slice-19d0/execution.json` records the pinned manifest, actual NAR
hashes, source environment, both fresh XML runs, failed checks and observation
times. `cxml-run-1.log` and `cxml-run-2.log` contain conditions and SAX checks.
`regression-execution.json` and `regression-tests.log` preserve the complete
unchanged regression run. Every retained JSON report is compared byte-for-byte
with Slice 19C; original sources, baselines and normative references stay intact.

Retained results: **12,100 Lisp checks**, **2 Python tests**, **16,294 NFC oracle
comparisons** pass. CTM remains **204 PASS, 4 known FAIL, 65 NOT-RUN**.
No XTM contract is registered or marked PASS.

Conclusion: **source provisioning PASS; parser qualification FAIL; full offline
DevShell rebuild NOT-RUN.** The parser is not yet qualified for Slice 19D1.
