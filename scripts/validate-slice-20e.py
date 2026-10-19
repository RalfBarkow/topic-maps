#!/usr/bin/env python3
"""Validate the empty2 original registration and all retained suites offline."""
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
BASE = '9866a0e94a2a43c6aa73025f1c8d06b0f093a34b'
ID = 'ctm/in/empty2.ctm'
POLICY = '(version 1)(allow default)(deny network*)'
SOURCE = b'%version 1.0\n'
EXPECTED = b'<topicMap>\n</topicMap>\n'


def main():
    # Reuse existing report/hash utilities and historical label qualification.
    def previous(name):
        spec = importlib.util.spec_from_file_location(name, ROOT / ('scripts/validate-' + name + '.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    common, prolog_driver = previous('slice-20a'), previous('slice-20c')
    read, save, sha, command, snapshot = common.read, common.save, common.sha, common.command, common.snapshot
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/slice-20e')
    args = parser.parse_args()
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT, check=True)
    mutable = {'tests/ctm-registered-originals.lisp', 'topic-maps.asd', 'scripts/fresh-sbcl.lisp'}
    tracked = command(['git', 'ls-tree', '-r', '--name-only', BASE]).splitlines()
    protected_paths = [p for p in tracked if p not in mutable]
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    retained = output / 'retained'
    retained.mkdir()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    protected = snapshot(ROOT / p for p in protected_paths)
    historical = snapshot(p for p in (ROOT / 'reports').rglob('*') if output not in p.parents)
    sources = snapshot(p for directory in ['src', 'tests', 'scripts', 'docs']
                       for p in (ROOT / directory).rglob('*') if p.suffix in ['.lisp', '.py', '.sh', '.md'])
    sources.update(snapshot(ROOT / p for p in ['topic-maps.asd', 'flake.nix', 'flake.lock', 'README.md']))
    source = ROOT / 'vendor/cxtm' / ID
    baseline = ROOT / 'vendor/cxtm/ctm/baseline/empty2.ctm.cxtm'
    assert source.read_bytes() == SOURCE and baseline.read_bytes() == EXPECTED
    runs = []
    with tempfile.TemporaryDirectory(prefix='topic-maps-20e-') as temp_name:
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
                   TOPIC_MAPS_EMPTY2_REPORT=str(output / 'current'))
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
    # Compare regenerated retained stages with their historical provenance.
    def retained_equal(prior, current):
        if prior == current:
            return
        assert current['checks'] == [prolog_driver.RENAMED.get(c, c) for c in prior['checks']]
        assert {k: v for k, v in prior.items() if k != 'checks'} == {
            k: v for k, v in current.items() if k != 'checks'}
    verified = []
    for old in sorted((ROOT / 'reports/slice-19c').glob('*.json')):
        if old.name == 'execution.json':
            continue
        current = retained / ('core.json' if old.name == 'validation.json' else 'core.json.' + old.name)
        retained_equal(read(old), read(current))
        verified.append(str(old.relative_to(ROOT)))
    for suffix in ['validation', 'cxtm', 'integration']:
        old = ROOT / f'reports/slice-19d2/{suffix}.json'
        retained_equal(read(old), read(retained / f'xtm-mergemap.{suffix}.json'))
        verified.append(str(old.relative_to(ROOT)))
    for stage, directory, suffixes in [
        ('slice20a', 'slice-20a', ['validation', 'cxtm', 'registration']),
        ('slice20b', 'slice-20b', ['validation', 'cxtm', 'negative']),
        ('slice20c', 'slice-20c', ['validation', 'cxtm', 'prolog']),
    ]:
        for suffix in suffixes:
            old = ROOT / f'reports/{directory}/current.{suffix}.json'
            assert read(old) == read(retained / f'{stage}.{suffix}.json'), str(old)
            verified.append(str(old.relative_to(ROOT)))
    before = read(retained / 'slice20c.validation.json')
    final = read(output / 'current.validation.json')
    registration = read(output / 'current.registration.json')
    cxtm = read(output / 'current.cxtm.json')
    assert before['statuses'] == registration['entryStatuses'] == {
        'pass': 255, 'fail': 4, 'unsupported': 0, 'not-run': 14}
    assert final['statuses'] == {'pass': 256, 'fail': 4, 'unsupported': 0, 'not-run': 13}
    assert registration['passed'] == len(registration['checks']) == len(set(registration['checks']))
    assert registration['failed'] == 0 and len(registration['cases']) == 1
    row = registration['cases'][0]
    assert row['id'] == ID and row['sourceBytes'] == 13
    assert row['status'] == 'pass' and row['actualOutcome'] == 'cxtm-match' and row['diagnostics'] == []
    assert row['comparison']['actualBytes'] == row['comparison']['expectedBytes'] == 23
    assert row['comparison']['firstDifferentByte'] is None
    assert row['comparison']['model'] == {'topicCount': 0, 'associationCount': 0, 'topics': []}
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
    old_cxtm = read(retained / 'slice20c.cxtm.json')
    assert [c for c in cxtm['cases'] if c['id'] != ID] == old_cxtm['cases']
    assert cxtm['contractCounts'] == {'pass': 218, 'fail': 4}
    for case in cxtm['cases']:
        pinned = ROOT / 'vendor/cxtm/ctm/baseline' / (Path(case['id']).name + '.cxtm')
        actual = case['actualCXTM'].encode('utf-8')
        assert (actual == pinned.read_bytes()) == (case['status'] == 'pass')
        assert case['expectedCXTM'].encode('utf-8') == pinned.read_bytes()
    comparison = next(c for c in cxtm['cases'] if c['id'] == ID)
    assert comparison['actualCXTM'].encode() == comparison['expectedCXTM'].encode() == EXPECTED
    log = (output / 'regression.log').read_text()
    prior_totals = read(ROOT / 'reports/slice-19d1/regression-execution.json')['regressionChecks']
    totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) for marker in prior_totals}
    assert totals == prior_totals and sum(totals.values()) == 12100
    for marker, count in [('XTM-MERGEMAP', 217), ('REGISTERED-ORIGINALS', 286),
                          ('REGISTERED-NEGATIVES', 25), ('PROLOG', 171), ('EMPTY2', registration['passed'])]:
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) == count
    assert log.count('EMPTY2-ORIGINAL ctm/in/empty2.ctm: PASS; 23 byte-exact CXTM bytes') == 1
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
        'slice20aChecks': 286, 'slice20bChecks': 25, 'prologChecks': 171, 'empty2Checks': registration['passed'],
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
            'firstDifferentByte': None, 'topics': 0, 'associations': 0,
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
        'slice20aChecks', 'slice20bChecks', 'prologChecks', 'empty2Checks', 'ctmStatusesAfter',
        'xtmCorpusStatuses', 'originalComparison', 'pinnedCorpusFilesVerified', 'acceptancePassed']}, indent=2))


if __name__ == '__main__':
    main()
