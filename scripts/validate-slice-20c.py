#!/usr/bin/env python3
"""Validate the minimal CTM prolog implementation and every retained suite offline."""
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
BASE = 'd024dc96ce091db06b9d09ea7c1ccb5f90b2886d'
POLICY = '(version 1)(allow default)(deny network*)'
EXPECTED = {
    'BOM-contradicts-encoding': ('encoding-conflict', 14, 'byte', None, None),
    'unknown-directive': ('unknown-directive', 0, 'character', 1, 1),
    'wrong-version': ('invalid-version', 9, 'character', 1, 10),
}
# Five prior 19D2 labels plus the one obsolete version-unimplemented assertion.
RENAMED = {
    'diagnostic:known-XTM-unimplemented:specific-condition': 'diagnostic:XTM-explicit-resolver-required:specific-condition',
    'diagnostic:known-XTM-unimplemented:source-position': 'diagnostic:XTM-explicit-resolver-required:source-position',
    'policy:XTM-recognized-without-retrieval:specific-condition': 'policy:XTM-explicit-resolver-before-retrieval:specific-condition',
    'policy:XTM-recognized-without-retrieval:source-position': 'policy:XTM-explicit-resolver-before-retrieval:source-position',
    'policy:XTM-does-not-call-resolver': 'policy:XTM-without-resolver-does-not-fetch',
    'remaining-construct-unsupported:%version 1.0': 'prefix:version-1.0-prolog-supported',
}


def main():
    spec = importlib.util.spec_from_file_location('slice20a', ROOT / 'scripts/validate-slice-20a.py')
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    read, save, sha, command, snapshot = common.read, common.save, common.sha, common.command, common.snapshot
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/slice-20c')
    parser.add_argument('--preimplementation-log', type=Path)
    args = parser.parse_args()
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    retained_dir = output / 'retained'
    retained_dir.mkdir()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    protected_paths = ['src/tmdm', 'src/cxtm', 'src/xml', 'src/xtm', 'patches', 'vendor', 'references',
                       'flake.nix', 'flake.lock', 'scripts/test.sh', 'scripts/prepare-cxml.py',
                       'scripts/validate-slice-19d2.py', 'scripts/validate-slice-20a.py', 'scripts/validate-slice-20b.py']
    tracked_tests = command(['git', 'ls-tree', '-r', '--name-only', BASE, '--', 'tests']).splitlines()
    protected_paths += [p for p in tracked_tests if p != 'tests/ctm-prefixes.lisp']
    protected_paths += ['src/ctm/' + p.name for p in (ROOT / 'src/ctm').glob('*.lisp')
                        if p.name not in ['unicode.lisp', 'lexer.lisp', 'reader.lisp', 'resources.lisp']]
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    protected = snapshot(p for directory in ['src/tmdm', 'src/cxtm', 'src/xml', 'src/xtm', 'vendor', 'references', 'patches']
                         for p in (ROOT / directory).rglob('*'))
    historical = snapshot(p for p in (ROOT / 'reports').rglob('*') if output not in p.parents)
    sources = snapshot(p for directory in ['src', 'tests', 'scripts', 'docs']
                       for p in (ROOT / directory).rglob('*') if p.suffix in ['.lisp', '.py', '.sh', '.md'])
    sources.update(snapshot(ROOT / p for p in ['topic-maps.asd', 'flake.nix', 'flake.lock', 'README.md']))
    if args.preimplementation_log:
        preimplementation = [json.loads(line) for line in args.preimplementation_log.read_text().splitlines() if line.startswith('{')]
        assert [Path(r['id']).stem for r in preimplementation] == list(EXPECTED)
        assert all(r['condition']['condition'] == 'CTM-UNSUPPORTED' and r['condition']['code'] == 'unsupported-directive'
                   for r in preimplementation)
        save(output / 'preimplementation.json', {'baseCommit': BASE, 'runtime': 'SBCL 2.5.4',
                                               'freshProcess': True, 'network': 'denied by sandbox-exec', 'cases': preimplementation})
    runs = []
    with tempfile.TemporaryDirectory(prefix='topic-maps-20c-') as tmp_name:
        tmp = Path(tmp_name)
        preparation = ['python3', 'scripts/prepare-cxml.py', '--directory', str(tmp / 'sources')]
        provenance = json.loads(command(preparation))
        save(output / 'source-preparation.json', provenance)
        env = dict(os.environ, SBCL=runtime, PYTHONDONTWRITEBYTECODE='1', CL_SOURCE_REGISTRY=provenance['sourceRegistry'])
        env.update(TOPIC_MAPS_REPORT=str(retained_dir / 'core.json'),
                   TOPIC_MAPS_XTM_REPORT=str(retained_dir / 'xtm.json'),
                   TOPIC_MAPS_XTM_MERGEMAP_REPORT=str(retained_dir / 'xtm-mergemap'),
                   TOPIC_MAPS_REGISTERED_ORIGINALS_REPORT=str(retained_dir / 'slice20a'),
                   TOPIC_MAPS_REGISTERED_NEGATIVES_REPORT=str(retained_dir / 'slice20b'),
                   TOPIC_MAPS_PROLOG_REPORT=str(output / 'current'))
        invocations = [
            ('xml', [runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script', 'tests/cxml-probe.lisp']),
            ('xtm', [runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script', 'scripts/fresh-xtm.lisp']),
            ('regression', [str(ROOT / 'scripts/test.sh')]),
        ]
        for label, invocation in invocations:
            invocation = ['/usr/bin/sandbox-exec', '-p', POLICY] + invocation
            context = {'label': label, 'command': invocation, 'freshProcess': True, 'network': 'denied by sandbox-exec',
                       'startedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
            result = subprocess.run(invocation, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
            (output / (label + '.log')).write_bytes(result.stdout)
            context.update(exitCode=result.returncode, finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
            runs.append(context)
            assert result.returncode == 0, f'{label} failed; see {label}.log'
            if label in ['xml', 'xtm']:
                marker = 'CXML' if label == 'xml' else 'XTM'
                labels = re.findall(r'^' + marker + r'-CHECK-PASS (.+)$', result.stdout.decode(), re.M)
                assert len(labels) == len(set(labels)) == (146 if label == 'xml' else 327)
                assert f'{marker}-SUMMARY {len(labels)} PASS 0 FAIL' in result.stdout.decode()
                context['passedChecks'] = len(labels)
        # Keep the two retained documented inspection examples executable too.
        for label, document in [('xtm-inspection', 'docs/slice-19d2-xtm-mergemap.md'),
                                ('ctm-inspection', 'docs/slice-20a-registration.md')]:
            forms = (ROOT / document).read_text().split('```lisp\n')[-1].split('\n```', 1)[0]
            invocation = ['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script', '/dev/stdin']
            result = subprocess.run(invocation, cwd=ROOT, env=env, input=forms.encode(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
            (output / (label + '.log')).write_bytes(result.stdout)
            assert result.returncode == 0, label
    def retained_equal(prior, current):
        if prior == current:
            return
        assert 'checks' in prior and 'checks' in current
        assert current['checks'] == [RENAMED.get(c, c) for c in prior['checks']]
        assert {k: v for k, v in prior.items() if k != 'checks'} == {k: v for k, v in current.items() if k != 'checks'}
    baseline = ROOT / 'reports/slice-19c'
    verified_reports = []
    for old in sorted(baseline.glob('*.json')):
        if old.name == 'execution.json':
            continue
        current = retained_dir / ('core.json' if old.name == 'validation.json' else 'core.json.' + old.name)
        retained_equal(read(old), read(current))
        verified_reports.append(str(old.relative_to(ROOT)))
    for suffix in ['validation', 'cxtm', 'integration']:
        retained_equal(read(ROOT / f'reports/slice-19d2/{suffix}.json'), read(retained_dir / f'xtm-mergemap.{suffix}.json'))
    for stage, directory, suffixes in [('slice20a', 'slice-20a', ['validation', 'cxtm', 'registration']),
                                       ('slice20b', 'slice-20b', ['validation', 'cxtm', 'negative'])]:
        for suffix in suffixes:
            retained_equal(read(ROOT / f'reports/{directory}/current.{suffix}.json'), read(retained_dir / f'{stage}.{suffix}.json'))
    before = read(retained_dir / 'slice20b.validation.json')
    final = read(output / 'current.validation.json')
    cxtm = read(output / 'current.cxtm.json')
    prolog = read(output / 'current.prolog.json')
    assert prolog['entryStatuses'] == before['statuses'] == {'pass': 252, 'fail': 4, 'unsupported': 0, 'not-run': 17}
    assert final['statuses'] == {'pass': 255, 'fail': 4, 'unsupported': 0, 'not-run': 14}
    assert prolog['failed'] == 0 and prolog['passed'] == len(prolog['checks']) == len(set(prolog['checks']))
    rows = {r['id']: r for r in prolog['originals']}
    assert list(rows) == ['ctm/invalid/' + name + '.ctm' for name in EXPECTED]
    assert len(before['cases']) == len(final['cases']) == 273
    changes, candidates = [], []
    for a, b in zip(before['cases'], final['cases']):
        assert a['id'] == b['id']
        if a['id'] not in rows:
            assert a == b, a['id']
            continue
        row = rows[a['id']]
        assert row['qualified'] and row['status'] == 'pass' and row['control']['accepted'] and row['control']['condition'] is None
        assert row['documentIRI'] == a['documentIRI']
        assert a['documentIRI'] == 'https://ctm-tests.example.invalid/' + before['commit'] + '/' + a['id']
        assert row['condition'] == row['repeatCondition']
        c = row['condition']
        expected = EXPECTED[Path(a['id']).stem]
        assert c['condition'] == 'CTM-REJECTION' and (c['code'], c['position'], c['positionUnit'], c['line'], c['column']) == expected
        assert c['source'] == a['id'] and c['cause'] is c['context'] is None
        data = (ROOT / 'vendor/cxtm' / a['sourcePathname']).read_bytes()
        assert row['sourceHex'] == data.hex(' ').upper()
        assert row['sourceTextAfterBOM'] == data.decode('utf-8-sig')
        if c['positionUnit'] == 'byte':
            assert data[:3] == bytes.fromhex('ef bb bf') and data[c['position']:].startswith(b'iso-8859-1')
        else:
            text = data.decode()
            assert text[c['position']:].startswith('10.0' if Path(a['id']).stem == 'wrong-version' else '%ctm')
            assert text[:c['position']].count('\n') + 1 == c['line']
            assert len(text[:c['position']].rsplit('\n', 1)[-1]) + 1 == c['column']
        assert a['status'] == 'not-run' and a['actualOutcome'] is None
        assert b == dict(a, status='pass', actualOutcome='ctm-rejection', diagnostics=[c['message']])
        changes.append({'id': a['id'], 'before': a['status'], 'after': b['status']})
        candidates.append({'id': a['id'], 'status': b['status'], 'sourceSHA256': sha(ROOT / 'vendor/cxtm' / a['id']),
                           'documentIRI': a['documentIRI'], 'clauses': row['clauses'], 'condition': c})
    assert {k: v for k, v in before.items() if k not in ['cases', 'statuses', 'implementationScope']} == {
        k: v for k, v in final.items() if k not in ['cases', 'statuses', 'implementationScope']}
    assert cxtm['cases'] == read(retained_dir / 'slice20b.cxtm.json')['cases']
    assert cxtm['contractCounts'] == {'pass': 217, 'fail': 4}
    # Independently recheck every actual positive CXTM stream against its pin.
    for case in cxtm['cases']:
        name = Path(case['id']).name
        baseline_bytes = (ROOT / 'vendor/cxtm/ctm/baseline' / (name + '.cxtm')).read_bytes()
        actual = case['actualCXTM'].encode('utf-8')
        assert (actual == baseline_bytes) == (case['status'] == 'pass')
        assert case['expectedCXTM'].encode('utf-8') == baseline_bytes
    positives = prolog['positives']
    assert len([p for p in positives if p['label'].startswith('utf8:provided=')]) == 18
    assert all(p['accepted'] for p in positives)
    assert 'encoding-selection-precedes-decoder:zero-calls' in prolog['checks']
    negative_labels = {r['label']: r['condition'] for r in prolog['negativeControls']}
    for label, c in negative_labels.items():
        assert c['condition'] in ['CTM-REJECTION', 'CTM-UNSUPPORTED']
        if c['positionUnit'] == 'byte':
            assert c['line'] is c['column'] is None
    assert negative_labels['conflict-before-invalid-body-decoding']['code'] == 'encoding-conflict'
    assert negative_labels['unsupported-before-invalid-body-decoding']['condition'] == 'CTM-UNSUPPORTED'
    assert negative_labels['known-literal-unsupported']['code'] == 'occurrence-literal-datatype'
    log = (output / 'regression.log').read_text()
    previous_totals = read(ROOT / 'reports/slice-19d1/regression-execution.json')['regressionChecks']
    totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) for marker in previous_totals}
    assert totals == previous_totals and sum(totals.values()) == 12100
    for marker, expected in [('XTM-MERGEMAP', 217), ('REGISTERED-ORIGINALS', 286), ('REGISTERED-NEGATIVES', 25), ('PROLOG', prolog['passed'])]:
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) == expected
    assert len(re.findall(r'^PROLOG-ORIGINAL ctm/invalid/[^:]+: PASS;', log, re.M)) == 3
    assert 'Ran 2 tests' in log and 'NFC-ORACLE-PASS: 16294' in log and 'XTM-ADAPTER-BOUNDARY-PASS:' in log
    xtm = read(retained_dir / 'xtm.json')
    assert xtm == read(ROOT / 'reports/slice-19d2/xtm.json')
    assert xtm['statuses'] == {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 0}
    assert xtm['otherCorpusInputs'] == {'positiveUnexecuted': 107, 'negativeUnregisteredUnexecuted': 11}
    assert protected == {p: sha(ROOT / p) for p in protected}
    assert historical == {p: sha(ROOT / p) for p in historical}
    assert sources == {p: sha(ROOT / p) for p in sources}
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    save(output / 'candidates.json', candidates)
    save(output / 'remaining.json', [c for c in final['cases'] if c['status'] == 'not-run'])
    save(output / 'integrity.json', {'protectedFilesSHA256': protected, 'historicalReportsSHA256': historical})
    evidence = {
        'baseCommit': BASE, 'branch': command(['git', 'branch', '--show-current']),
        'startedAtUTC': started, 'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'runtime': 'SBCL 2.5.4', 'sourceSHA256': sources, 'newDependencyDownloads': 0,
        'sourcePreparationCommand': preparation, 'qualifiedSourceProvenance': provenance, 'runs': runs,
        'retainedLispChecks': sum(totals.values()), 'retainedChecks': totals,
        'xmlQualificationChecks': 146, 'standaloneXTMChecks': 327, 'xtmMergemapChecks': 217,
        'slice20aChecks': 286, 'slice20bChecks': 25, 'prologChecks': prolog['passed'],
        'positivePrologAndResourceControls': len(positives), 'negativeControls': len(prolog['negativeControls']),
        'pythonUnitTests': 2, 'nfcOracleComparisons': 16294,
        'ctmStatusesBefore': before['statuses'], 'ctmStatusesAfter': final['statuses'], 'ctmStatusChanges': changes,
        'xtmCorpusStatuses': {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 118},
        'knownFailuresUnchanged': [c['id'] for c in final['cases'] if c['status'] == 'fail'],
        'retainedReportsVerified': verified_reports, 'retainedReportLabelChanges': RENAMED,
        'retainedPositiveCXTMComparisons': len(cxtm['cases']),
        'allHistoricalReportBytesUnchanged': True, 'allProtectedFileBytesUnchanged': True,
        'encodingConflictBeforeDecoderCalls': 0, 'optionalEncodingAPI': 'deserialize-file :encoding',
        'encodingScope': 'UTF-8 only; existing strict decoder unchanged; no aliases or new charset decoder; resolver protocol unchanged.',
        'persistentLispImagesTouched': False, 'documentedRetainedInspectionsPassed': True,
        'fullOfflineNixRebuild': 'NOT-RUN; fresh offline SBCL loads from verified local Store sources and unchanged XML patches.',
        'acceptancePassed': True,
    }
    save(output / 'execution.json', evidence)
    print(json.dumps({k: evidence[k] for k in ['runtime', 'retainedLispChecks', 'xmlQualificationChecks', 'standaloneXTMChecks',
        'xtmMergemapChecks', 'slice20aChecks', 'slice20bChecks', 'prologChecks', 'ctmStatusesAfter', 'xtmCorpusStatuses', 'acceptancePassed']}, indent=2))


if __name__ == '__main__':
    main()
