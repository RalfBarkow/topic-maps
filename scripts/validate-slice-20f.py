#!/usr/bin/env python3
"""Validate the CTM-integer literal, original contract and all retained suites offline."""
import argparse
import datetime
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
BASE = '341cfa2306788e2943bdf11ced5ee32a8ba74894'
ID = 'ctm/in/occurrence-ctm-integer.ctm'
POLICY = '(version 1)(allow default)(deny network*)'
SOURCE = b'topic\nocctype: *;.'
EXPECTED = (ROOT / 'vendor/cxtm/ctm/baseline/occurrence-ctm-integer.ctm.cxtm').read_bytes()


def main():
    # Reuse existing report/hash utilities and historical label qualification.
    def previous(name):
        spec = importlib.util.spec_from_file_location(name, ROOT / ('scripts/validate-' + name + '.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    common = previous('slice-20a')
    read, save, sha, command, snapshot = common.read, common.save, common.sha, common.command, common.snapshot
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/slice-20f')
    parser.add_argument('--preimplementation', type=Path, default=ROOT / 'reports/slice-20f/preimplementation.json')
    args = parser.parse_args()
    preimplementation = read(args.preimplementation)
    assert preimplementation['baseCommit'] == BASE and len(preimplementation['cases']) == 24
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT, check=True)
    mutable = {'src/ctm/lexer.lisp', 'src/ctm/reader.lisp', 'src/ctm/templates.lisp',
               'tests/ctm-registered-originals.lisp', 'tests/ctm-occurrences.lisp', 'tests/ctm-integers.lisp',
               'tests/ctm-prolog.lisp', 'topic-maps.asd', 'scripts/fresh-sbcl.lisp'}
    tracked = command(['git', 'ls-tree', '-r', '--name-only', BASE]).splitlines()
    protected_paths = [p for p in tracked if p not in mutable]
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    retained = output / 'retained'
    retained.mkdir()
    save(output / 'preimplementation.json', preimplementation)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    protected = snapshot(ROOT / p for p in protected_paths)
    historical = snapshot(p for p in (ROOT / 'reports').rglob('*') if output not in p.parents)
    sources = snapshot(p for directory in ['src', 'tests', 'scripts', 'docs']
                       for p in (ROOT / directory).rglob('*') if p.suffix in ['.lisp', '.py', '.sh', '.md'])
    sources.update(snapshot(ROOT / p for p in ['topic-maps.asd', 'flake.nix', 'flake.lock', 'README.md']))
    source = ROOT / 'vendor/cxtm' / ID
    baseline = ROOT / 'vendor/cxtm/ctm/baseline/occurrence-ctm-integer.ctm.cxtm'
    assert source.read_bytes() == SOURCE and baseline.read_bytes() == EXPECTED
    assert len(EXPECTED) == 356 and common.digest(EXPECTED) == '51c024274bb50d36bd583998ee26dd120a177fa010bbf5259dc1bc18f045c190'
    runs = []
    with tempfile.TemporaryDirectory(prefix='topic-maps-20f-') as temp_name:
        temp = Path(temp_name)
        preparation = ['python3', 'scripts/prepare-cxml.py', '--directory', str(temp / 'sources')]
        provenance = json.loads(command(preparation))  # nix eval --offline; verifies local Store source hashes.
        save(output / 'source-preparation.json', provenance)
        env = dict(os.environ, SBCL=runtime, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1',
                   CL_SOURCE_REGISTRY=provenance['sourceRegistry'],
                   TOPIC_MAPS_REPORT=str(retained / 'core.json'),
                   TOPIC_MAPS_XTM_REPORT=str(retained / 'xtm.json'),
                   TOPIC_MAPS_XTM_MERGEMAP_REPORT=str(retained / 'xtm-mergemap'),
                   TOPIC_MAPS_REGISTERED_ORIGINALS_REPORT=str(retained / 'slice20a'),
                   TOPIC_MAPS_REGISTERED_NEGATIVES_REPORT=str(retained / 'slice20b'),
                   TOPIC_MAPS_PROLOG_REPORT=str(retained / 'slice20c'),
                   TOPIC_MAPS_EMPTY2_REPORT=str(retained / 'slice20e'),
                   TOPIC_MAPS_CTM_INTEGER_REPORT=str(output / 'current'))
        invocations = [
            ('xml', [runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script', 'tests/cxml-probe.lisp']),
            ('xtm', [runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script', 'scripts/fresh-xtm.lisp']),
            ('regression', [str(ROOT / 'scripts/test.sh')]),
        ]
        for label, invocation in invocations:
            invocation = ['/usr/bin/sandbox-exec', '-p', POLICY] + invocation
            run = {'label': label, 'command': invocation, 'freshProcess': True,
                   'network': 'denied by sandbox-exec',
                   'startedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
            result = subprocess.run(invocation, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=300)
            (output / (label + '.log')).write_bytes(result.stdout)
            run.update(exitCode=result.returncode, finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
            runs.append(run)
            assert result.returncode == 0, f'{label} failed; see {label}.log'
            if label in ['xml', 'xtm']:
                marker = 'CXML' if label == 'xml' else 'XTM'
                labels = re.findall(r'^' + marker + r'-CHECK-PASS (.+)$', result.stdout.decode(), re.M)
                assert len(labels) == len(set(labels)) == (146 if label == 'xml' else 327)
                assert f'{marker}-SUMMARY {len(labels)} PASS 0 FAIL' in result.stdout.decode()
                run['passedChecks'] = len(labels)
    # Historical report bytes remain immutable. Regenerated reports permit only
    # explicitly reviewed replacements of obsolete '*' unsupported assertions.
    label_changes = {
        'occurrence-diagnostic:a t:*.': 'occurrence-diagnostic:a t:*x.',
        'excluded-numeric-sugar:*': 'integer-slice-now-allows-ctm-integer',
        'known-literal-unsupported:specific-condition-code-position-source':
            'known-triple-string-unsupported:specific-condition-code-position-source',
        'known-literal-unsupported:position-units': 'known-triple-string-unsupported:position-units',
    }
    old_prolog = read(ROOT / 'reports/slice-20e/retained/slice20c.prolog.json')
    old_literal = next(r for r in old_prolog['negativeControls'] if r['label'] == 'known-literal-unsupported')
    new_condition = dict(old_literal['condition'],
        code='triple-quoted-string', source='known-triple-string-unsupported',
        message='TRIPLE-QUOTED-STRING in known-triple-string-unsupported at CHARACTER 11 (line 1, column 12): Triple quoted literals are outside Slice 1.')
    def qualified_retained(value):
        if isinstance(value, dict):
            if value.get('label') == 'known-literal-unsupported':
                assert value == old_literal
                return {'label': 'known-triple-string-unsupported', 'condition': new_condition}
            return {k: qualified_retained(v) for k, v in value.items()}
        if isinstance(value, list):
            return [qualified_retained(v) for v in value]
        if isinstance(value, str):
            return label_changes.get(value, value)
        return value
    verified = []
    for old in sorted((ROOT / 'reports/slice-20e/retained').glob('*.json')):
        assert qualified_retained(read(old)) == read(retained / old.name), str(old)
        verified.append(str(old.relative_to(ROOT)))
    for suffix in ['validation', 'cxtm', 'registration']:
        old = ROOT / f'reports/slice-20e/current.{suffix}.json'
        assert qualified_retained(read(old)) == read(retained / f'slice20e.{suffix}.json'), str(old)
        verified.append(str(old.relative_to(ROOT)))
    before = read(retained / 'slice20e.validation.json')
    final = read(output / 'current.validation.json')
    literal = read(output / 'current.literal.json')
    cxtm = read(output / 'current.cxtm.json')
    assert before['statuses'] == literal['entryStatuses'] == {
        'pass': 256, 'fail': 4, 'unsupported': 0, 'not-run': 13}
    assert final['statuses'] == {'pass': 257, 'fail': 4, 'unsupported': 0, 'not-run': 12}
    assert literal['passed'] == len(literal['checks']) == len(set(literal['checks']))
    assert literal['failed'] == 0
    row = literal['original']
    assert row['id'] == ID and row['sourceBytes'] == 18
    assert row['status'] == 'pass' and row['actualOutcome'] == 'cxtm-match' and row['diagnostics'] == []
    assert row['comparison']['actualBytes'] == row['comparison']['expectedBytes'] == 356
    assert row['comparison']['firstDifferentByte'] is None
    assert row['comparison']['model']['topicCount'] == 2 and row['comparison']['model']['associationCount'] == 0
    model_occurrences = [o for t in row['comparison']['model']['topics'] for o in t['occurrences']]
    assert len(model_occurrences) == 1
    assert model_occurrences[0]['value'] == '*' and model_occurrences[0]['datatype'] == 'http://psi.topicmaps.org/iso13250/ctm-integer'
    changes = []
    assert len(before['cases']) == len(final['cases']) == 273
    for a, b in zip(before['cases'], final['cases']):
        assert a['id'] == b['id']
        if a['id'] != ID:
            assert a == b, a['id']
            continue
        assert a['category'] == 'valid' and a['expectedOutcome'] == 'cxtm-equal'
        assert a['status'] == 'not-run' and a['actualOutcome'] is None
        assert a['documentIRI'] == row['documentIRI'] == (
            'https://ctm-tests.example.invalid/' + before['commit'] + '/' + ID)
        assert b == dict(a, status='pass', actualOutcome='cxtm-match')
        changes.append({'id': ID, 'before': a['status'], 'after': b['status']})
    assert len(changes) == 1
    assert {k: v for k, v in before.items() if k not in ['cases', 'statuses', 'implementationScope', 'infrastructureChecks']} == {
        k: v for k, v in final.items() if k not in ['cases', 'statuses', 'implementationScope', 'infrastructureChecks']}
    old_cxtm = read(retained / 'slice20e.cxtm.json')
    assert [c for c in cxtm['cases'] if c['id'] != ID] == old_cxtm['cases']
    assert cxtm['contractCounts'] == {'pass': 219, 'fail': 4}
    for case in cxtm['cases']:
        pinned = ROOT / 'vendor/cxtm/ctm/baseline' / (Path(case['id']).name + '.cxtm')
        actual = case['actualCXTM'].encode('utf-8')
        assert (actual == pinned.read_bytes()) == (case['status'] == 'pass')
        assert case['expectedCXTM'].encode('utf-8') == pinned.read_bytes()
    comparison = next(c for c in cxtm['cases'] if c['id'] == ID)
    assert comparison['actualCXTM'].encode() == comparison['expectedCXTM'].encode() == EXPECTED
    positives = {p['label']: p for p in literal['positives']}
    assert len(positives) == len(literal['positives']) == 31
    qualified = positives['original:qualified-control']
    assert qualified['actualCXTM'].encode() == EXPECTED
    for label, positive in positives.items():
        assert positive['finalCounter'] == (44 if label.startswith('counter:interleaved') else positive['initialCounter'])
    assert positives['equivalence:bare']['actualCXTM'] == positives['equivalence:qualified']['actualCXTM']
    assert positives['equivalence:bare']['actualCXTM'] != positives['distinction:string']['actualCXTM']
    assert positives['variant:bare']['actualCXTM'] == positives['variant:qualified']['actualCXTM']
    negatives = {r['label']: r for r in literal['negativeControls']}
    assert len(negatives) == len(literal['negativeControls']) == 26
    diagnostic_changes = []
    for prior in preimplementation['cases']:
        current = negatives[prior['label']]
        assert current['sourceText'] == prior['sourceText']
        old, new = prior['result'], current['condition']
        keys = ['condition', 'code', 'position', 'positionUnit', 'line', 'column', 'source']
        if prior['label'] in ['qualified-bare', 'missing-separator']:
            expected_position = 16 if prior['label'] == 'qualified-bare' else 17
            assert old['condition'] == 'CTM-UNSUPPORTED' and old['code'] == 'occurrence-literal-datatype'
            assert new['condition'] == 'CTM-REJECTION' and new['code'] == 'expected-separator'
            assert new['position'] == expected_position and new['line'] == 2 and new['column'] == expected_position - 5
            diagnostic_changes.append({'label': prior['label'], 'before': old, 'after': new,
                                       'reason': "The now-valid isolated '*' reaches the following forbidden token."})
        else:
            assert {k: old[k] for k in keys} == {k: new[k] for k in keys}, prior['label']
    assert len(diagnostic_changes) == 2
    log = (output / 'regression.log').read_text()
    prior_totals = read(ROOT / 'reports/slice-19d1/regression-execution.json')['regressionChecks']
    totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) for marker in prior_totals}
    assert totals == prior_totals and sum(totals.values()) == 12100
    for marker, count in [('XTM-MERGEMAP', 217), ('REGISTERED-ORIGINALS', 286),
                          ('REGISTERED-NEGATIVES', 25), ('PROLOG', 171), ('EMPTY2', 13), ('CTM-INTEGER', literal['passed'])]:
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) == count
    assert log.count('CTM-INTEGER-ORIGINAL ctm/in/occurrence-ctm-integer.ctm: PASS; 356 byte-exact CXTM bytes') == 1
    assert 'Ran 2 tests' in log and 'NFC-ORACLE-PASS: 16294' in log and 'XTM-ADAPTER-BOUNDARY-PASS:' in log
    xtm = read(retained / 'xtm.json')
    assert xtm == read(ROOT / 'reports/slice-19d2/xtm.json')
    assert xtm['statuses'] == {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 0}
    assert xtm['otherCorpusInputs'] == {'positiveUnexecuted': 107, 'negativeUnregisteredUnexecuted': 11}
    lock = read(ROOT / 'references/corpus-lock.json')
    for entry in lock['files']:
        path = ROOT / 'vendor/cxtm' / entry['path']
        assert path.stat().st_size == entry['size'] and sha(path) == entry['sha256'], str(path)
    assert protected == {p: sha(ROOT / p) for p in protected}
    assert historical == {p: sha(ROOT / p) for p in historical}
    assert sources == {p: sha(ROOT / p) for p in sources}
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    save(output / 'remaining.json', [c for c in final['cases'] if c['status'] == 'not-run'])
    save(output / 'integrity.json', {'protectedFilesSHA256': protected, 'historicalReportsSHA256': historical})
    evidence = {
        'baseCommit': BASE, 'branch': command(['git', 'branch', '--show-current']),
        'startedAtUTC': started, 'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'runtime': 'SBCL 2.5.4', 'sourceSHA256': sources, 'newDependencyDownloads': 0,
        'sourcePreparationCommand': preparation, 'qualifiedSourceProvenance': provenance, 'runs': runs,
        'retainedLispChecks': sum(totals.values()), 'retainedChecks': totals,
        'xmlQualificationChecks': 146, 'standaloneXTMChecks': 327, 'xtmMergemapChecks': 217,
        'slice20aChecks': 286, 'slice20bChecks': 25, 'prologChecks': 171, 'empty2Checks': 13, 'ctmIntegerChecks': literal['passed'],
        'positiveControls': len(positives), 'negativeControls': len(negatives),
        'unchangedDiagnosticSignatures': 22, 'newlyReachedDiagnostics': diagnostic_changes,
        'retainedReportLabelChanges': label_changes,
        'updatedBoundaryAssertion': 'occurrence-feature-boundary:a t:* . now checks acceptance',
        'pythonUnitTests': 2, 'nfcOracleComparisons': 16294,
        'ctmStatusesBefore': before['statuses'], 'ctmStatusesAfter': final['statuses'], 'ctmStatusChanges': changes,
        'xtmCorpusStatuses': {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 118},
        'knownFailuresUnchanged': [c['id'] for c in final['cases'] if c['status'] == 'fail'],
        'retainedReportsVerified': verified, 'allHistoricalReportBytesUnchanged': True,
        'allProtectedFileBytesUnchanged': True, 'pinnedCorpusFilesVerified': len(lock['files']),
        'originalComparison': {
            'id': ID, 'documentIRI': row['documentIRI'], 'sourceBytes': len(SOURCE), 'sourceSHA256': sha(source),
            'expectedBytes': len(EXPECTED), 'expectedSHA256': sha(baseline),
            'actualBytes': len(EXPECTED), 'actualSHA256': common.digest(comparison['actualCXTM'].encode()),
            'firstDifferentByte': None, 'topics': 2, 'associations': 0,
            'value': '*', 'datatype': 'http://psi.topicmaps.org/iso13250/ctm-integer',
            'qualifiedControlBytes': len(qualified['actualCXTM'].encode()),
            'qualifiedControlSHA256': common.digest(qualified['actualCXTM'].encode()),
            'canonicalizationPreservesMap': True, 'executedInFullRegression': True,
        },
        'persistentLispImagesTouched': False,
        'fullOfflineNixRebuild': 'NOT-RUN; fresh offline SBCL loads from verified local Store sources and unchanged XML patches.',
        'sandboxStartError': 'writable root /Users/rgb/.nix-profile contains symlink component /Users/rgb/.nix-profile; symlinked writable roots are not supported.',
        'executionAuthorization': 'Regular require_escalated auto-review approval; no symlink or sandbox configuration changes.',
        'acceptancePassed': True,
    }
    save(output / 'execution.json', evidence)
    print(json.dumps({k: evidence[k] for k in [
        'runtime', 'retainedLispChecks', 'xmlQualificationChecks', 'standaloneXTMChecks', 'xtmMergemapChecks',
        'slice20aChecks', 'slice20bChecks', 'prologChecks', 'empty2Checks', 'ctmIntegerChecks', 'positiveControls', 'negativeControls', 'ctmStatusesAfter',
        'xtmCorpusStatuses', 'originalComparison', 'pinnedCorpusFilesVerified', 'acceptancePassed']}, indent=2))


if __name__ == '__main__':
    main()
