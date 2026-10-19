#!/usr/bin/env python3
"""Execute the existing ASDF harness and offline regressions; retain byte evidence.

No alternate deserializer, model builder, or conformance classifier lives here.
Reports are produced by the existing Lisp harness. Use a new temporary output
folder; copy accepted evidence into version control only after this exits zero.
"""
import argparse
import collections
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'reports/slice-21b'
BASE = '1a2808b2d123184b2494f93b19738a31fc27fd52'
POLICY = '(version 1)(allow default)(deny network*)(deny file-write* (subpath "' + str(ROOT) + '"))'
ALLOWED_TRACKED = {'tests/xtm-identity.lisp', 'topic-maps.asd'}


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def prepare_pinned(target):
    prior = read(ROOT / 'reports/slice-20h/source-preparation.json')
    spec = importlib.util.spec_from_file_location('prepare_cxml', ROOT / 'scripts/prepare-cxml.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.prepare({'manifest': prior['sources'],
        'localPatches': [{'package': p['package'], 'sha256': p['sha256']} for p in prior['patches']]}, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare', type=Path)
    args = parser.parse_args()
    if args.prepare:
        print(json.dumps(prepare_pinned(args.prepare)))
        return
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT, check=True)
    output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='topic-maps-21b-'))
    assert not output.is_relative_to(ROOT), 'Run tests with repository writes denied; choose a temporary output directory.'
    output.mkdir(parents=True, exist_ok=True)
    assert not (output / 'execution.json').exists(), 'Choose an unused output directory.'
    tracked = command(['git', 'ls-tree', '-r', '--name-only', BASE]).splitlines()
    changed = set(command(['git', 'diff', '--name-only', BASE]).splitlines()) & set(tracked)
    assert changed <= ALLOWED_TRACKED
    protected = {p: sha(ROOT / p) for p in tracked if p not in ALLOWED_TRACKED}
    historical = {p: h for p, h in protected.items() if p.startswith('reports/')}
    sources = {p: sha(ROOT / p) for p in [*sorted(ALLOWED_TRACKED), 'scripts/validate-slice-21b.py',
               'reports/slice-21b/candidate-inventory.json', 'reports/slice-21b/failure-controls.lisp']}
    candidates = read(EVIDENCE / 'candidate-inventory.json')['candidates']
    assert len(candidates) == len({c['id'] for c in candidates}) == 20
    assert collections.Counter(c['group'] for c in candidates) == {
        'item-identifier': 4, 'merging': 4, 'subject-identifier': 7, 'subject-locator': 5}
    prior = ROOT / 'reports/slice-20j'
    baseline = read(EVIDENCE / 'baseline-xtm.json')
    assert baseline == read(prior / 'retained/xtm.json')
    assert baseline['statuses'] == {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 0}
    assert baseline['otherCorpusInputs'] == {'positiveUnexecuted': 107, 'negativeUnregisteredUnexecuted': 11}
    expected_ctm = {'pass': 262, 'fail': 4, 'unsupported': 0, 'not-run': 7}
    assert read(prior / 'current.validation.json')['statuses'] == expected_ctm
    assert not {c['id'] for c in baseline['cases']} & {c['id'] for c in candidates}
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    runs = []

    def run(label, invocation, env, expected_exit=0):
        invocation = ['/usr/bin/sandbox-exec', '-p', POLICY] + invocation
        entry = {'label': label, 'command': invocation, 'network': 'denied', 'repositoryWrites': 'denied',
                 'freshProcess': True, 'startedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        result = subprocess.run(invocation, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
        (output / (label + '.log')).write_bytes(result.stdout)
        entry.update(exitCode=result.returncode, expectedExitCode=expected_exit,
                     finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
        runs.append(entry)
        assert result.returncode == expected_exit, f'{label}: see {output / (label + ".log")}'
        return result.stdout.decode()

    retained = output / 'retained'
    retained.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith('TOPIC_MAPS_')}
    env.update(PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0', SBCL=runtime)
    with tempfile.TemporaryDirectory(prefix='topic-maps-21b-sources-') as temp_name:
        provenance = json.loads(run('source-preparation', ['python3', str(Path(__file__)), '--prepare', temp_name + '/sources'], env))
        save(output / 'source-preparation.json', provenance)
        env.update(CL_SOURCE_REGISTRY=provenance['sourceRegistry'],
                   TOPIC_MAPS_REPORT=str(retained / 'core.json'), TOPIC_MAPS_XTM_REPORT=str(output / 'xtm.json'),
                   TOPIC_MAPS_XTM_MERGEMAP_REPORT=str(retained / 'xtm-mergemap'),
                   TOPIC_MAPS_REGISTERED_ORIGINALS_REPORT=str(retained / 'slice20a'),
                   TOPIC_MAPS_REGISTERED_NEGATIVES_REPORT=str(retained / 'slice20b'),
                   TOPIC_MAPS_PROLOG_REPORT=str(retained / 'slice20c'), TOPIC_MAPS_EMPTY2_REPORT=str(retained / 'slice20e'),
                   TOPIC_MAPS_CTM_INTEGER_REPORT=str(retained / 'slice20f'), TOPIC_MAPS_TRIPLE_REPORT=str(retained / 'slice20g'),
                   TOPIC_MAPS_ENCODING_REPORT=str(output / 'ctm'))
        prefix = [runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script']
        xml = run('xml', prefix + ['tests/cxml-probe.lisp'], env)
        labels = re.findall(r'^CXML-CHECK-PASS (.+)$', xml, re.M)
        assert len(labels) == len(set(labels)) == 146 and 'CXML-SUMMARY 146 PASS 0 FAIL' in xml
        xtm_log = run('xtm', prefix + ['scripts/fresh-xtm.lisp'], env)
        xtm = read(output / 'xtm.json')
        labels = re.findall(r'^XTM-CHECK-PASS (.+)$', xtm_log, re.M)
        assert labels == xtm['checks'] and len(labels) == len(set(labels))
        assert set(baseline['checks']) <= set(labels), 'A retained XTM check disappeared'
        assert f'XTM-SUMMARY {len(labels)} PASS 0 FAIL; 26 original CXTM PASS' in xtm_log
        assert xtm['statuses'] == {'pass': 26, 'fail': 0, 'unsupported': 0, 'not-run': 0}
        assert xtm['otherCorpusInputs'] == {'positiveUnexecuted': 87, 'negativeUnregisteredUnexecuted': 11}
        assert xtm['cases'][:6] == baseline['cases']
        assert len({c['id'] for c in xtm['cases']}) == len(xtm['cases']) == 26
        assert [c['id'] for c in xtm['cases'][6:]] == [c['id'] for c in candidates]
        assert all(c['status'] == 'pass' and c['actualOutcome'] == 'cxtm-match' for c in xtm['cases'])
        assert xtm['helperSource'] == baseline['helperSource']
        regression = run('regression', [str(ROOT / 'scripts/test.sh')], env)
        controls = []
        for mode, outcome, condition_class in [('mismatch', 'cxtm-mismatch', None),
                ('xml', 'execution-error', 'XTM-XML-ERROR'), ('xtm', 'execution-error', 'XTM-REJECTION'),
                ('tmdm', 'execution-error', 'OCCURRENCE-IDENTIFIER-ERROR'), ('unsupported', 'unsupported', 'XTM-UNSUPPORTED')]:
            control_env = dict(env, TOPIC_MAPS_XTM_REPORT=str(output / ('control-' + mode + '.json')), TOPIC_MAPS_21B_FAULT=mode)
            run('control-' + mode, prefix + [str(EVIDENCE / 'failure-controls.lisp')], control_env, expected_exit=1)
            report = read(output / ('control-' + mode + '.json'))
            assert report['statuses']['pass'] == 0 and len(report['cases']) == 1
            assert report['cases'][0]['actualOutcome'] == outcome
            condition = report['actualAndExpected'][0]['condition']
            assert (condition['class'] if condition else None) == condition_class
            controls.append({'mode': mode, 'expectedASDFFailureObserved': True, 'actualOutcome': outcome,
                             'condition': condition, 'countedAsOriginalPass': False})

    verified = []
    for old in sorted((prior / 'retained').glob('*.json')):
        if old.name == 'xtm.json':
            continue
        assert read(old) == read(retained / old.name), str(old)
        verified.append(str(old.relative_to(ROOT)))
    for suffix in ['validation', 'cxtm', 'encoding']:
        old = prior / f'current.{suffix}.json'
        assert read(old) == read(output / f'ctm.{suffix}.json'), str(old)
        verified.append(str(old.relative_to(ROOT)))
    assert read(output / 'ctm.validation.json')['statuses'] == expected_ctm
    totals = read(ROOT / 'reports/slice-19d1/regression-execution.json')['regressionChecks']
    assert sum(totals.values()) == 12100
    for marker, count in totals.items():
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', regression).group(1)) == count
    stages = {'XTM-MERGEMAP': 217, 'REGISTERED-ORIGINALS': 286, 'REGISTERED-NEGATIVES': 25,
              'PROLOG': 171, 'EMPTY2': 13, 'CTM-INTEGER': 112, 'TRIPLE': 226, 'ENCODING': 722}
    for marker, count in stages.items():
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', regression).group(1)) == count
    assert 'Ran 2 tests' in regression and 'NFC-ORACLE-PASS: 16294' in regression
    comparisons = []
    (output / 'actual').mkdir()
    for record, result in zip(xtm['cases'], xtm['actualAndExpected']):
        assert record['id'] == result['id'] and result['condition'] is None
        source = ROOT / 'vendor/cxtm' / record['id']
        baseline_path = ROOT / 'vendor/cxtm/xtm2/baseline' / (source.name + '.cxtm')
        actual = result['actual'].encode('utf-8')
        assert actual == result['expected'].encode('utf-8') == baseline_path.read_bytes()
        assert result['byteLength'] == result['expectedByteLength'] == len(actual)
        assert result['sourceByteLength'] == source.stat().st_size and result['firstDifferentByte'] is None
        assert result['model']['canonicalParentsAndInverseReferences']
        (output / 'actual' / baseline_path.name).write_bytes(actual)
        comparison = {'id': record['id'], 'documentIRI': record['documentIRI'], 'sourceKey': record['id'],
            'sourceBytes': source.stat().st_size, 'sourceSHA256': sha(source),
            'baseline': str(baseline_path.relative_to(ROOT / 'vendor/cxtm')), 'baselineSHA256': sha(baseline_path),
            'expectedBytes': len(actual), 'actualBytes': len(actual), 'actualSHA256': hashlib.sha256(actual).hexdigest(),
            'firstDifferentByte': None, 'byteExact': True, 'condition': None, 'status': record['status'],
            'model': result['model'], 'executedInASDFTestOp': True,
            'checks': [c for c in labels if c.startswith(source.stem + ':')]}
        if record['id'] in {c['id'] for c in candidates}:
            candidate = next(c for c in candidates if c['id'] == record['id'])
            assert candidate['sourceSHA256'] == comparison['sourceSHA256'] and candidate['sourceBytes'] == comparison['sourceBytes']
            assert candidate['baselineSHA256'] == comparison['baselineSHA256'] and candidate['baselineBytes'] == len(actual)
            assert candidate['documentIRI'] == comparison['documentIRI']
        comparisons.append(comparison)
    lock = read(ROOT / 'references/corpus-lock.json')
    for entry in lock['files']:
        p = ROOT / 'vendor/cxtm' / entry['path']
        assert p.stat().st_size == entry['size'] and sha(p) == entry['sha256']
    for snapshot in [protected, historical, sources]:
        assert snapshot == {p: sha(ROOT / p) for p in snapshot}
    assert set(command(['git', 'diff', '--name-only', BASE]).splitlines()) & set(tracked) <= ALLOWED_TRACKED
    save(output / 'comparisons.json', {'kind': 'actual-original-cxtm-comparisons', 'cases': comparisons})
    save(output / 'failure-controls.json', {'kind': 'executor-fault-injection-controls-not-corpus-results', 'controls': controls})
    save(output / 'integrity.json', {'protectedBaseFilesSHA256': protected, 'historicalReportsSHA256': historical,
                                    'executionSourcesSHA256': sources})
    save(output / 'execution.json', {'kind': 'xtm-original-registration-validation', 'baseCommit': BASE,
        'branch': command(['git', 'branch', '--show-current']), 'runtime': 'SBCL 2.5.4', 'startedAtUTC': started,
        'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'runs': runs,
        'sourcePreparation': 'source-preparation.json', 'retainedLispChecks': 12100, 'retainedChecks': totals,
        'stageChecks': stages, 'xmlQualificationChecks': 146, 'standaloneXTMChecks': len(labels),
        'retainedXTMCheckNamesPreserved': len(baseline['checks']), 'originalComparisons': 26, 'newOriginalComparisons': 20,
        'xtmStatusesBefore': {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 118},
        'xtmStatusesAfter': {'pass': 26, 'fail': 0, 'unsupported': 0, 'not-run': 98},
        'xtmStatusChanges': [{'id': c['id'], 'before': 'not-run', 'after': 'pass', 'actualOutcome': 'cxtm-match'} for c in candidates],
        'ctmStatusesBefore': expected_ctm, 'ctmStatusesAfter': expected_ctm, 'ctmStatusChanges': [],
        'knownFailuresUnchanged': [c['id'] for c in read(output / 'ctm.validation.json')['cases'] if c['status'] == 'fail'],
        'negativeXTMOriginalsRegistered': 0, 'pythonUnitTests': 2, 'nfcOracleComparisons': 16294,
        'faultInjectionControls': controls, 'allRetainedNonXTMReportsEqualToSlice20J': verified,
        'historicalReportFilesVerified': len(historical), 'protectedBaseFilesVerified': len(protected),
        'pinnedCorpusFilesVerified': len(lock['files']), 'historicalReportsUnchanged': True,
        'originalSourcesAndBaselinesUnchanged': True, 'languageImplementationUnchanged': True,
        'newDependencyDownloads': 0, 'persistentLispImagesTouched': False,
        'fullOfflineNixRebuild': 'NOT-RUN; verified local pinned Store sources and existing qualified XML patches.',
        'executionAuthorization': 'Regular require_escalated approval after managed sandbox symlink launch error; no symlink or configuration changes.',
        'acceptancePassed': True})
    print(json.dumps({'acceptancePassed': True, 'xtm': {'pass': 26, 'fail': 0, 'not-run': 98},
        'ctm': expected_ctm, 'checks': len(labels), 'output': str(output)}))


if __name__ == '__main__':
    main()
