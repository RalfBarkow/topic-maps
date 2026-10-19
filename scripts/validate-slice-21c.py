#!/usr/bin/env python3
"""Validate cause-qualified negative originals through the existing XTM harness.

Use a fresh temporary output directory. No alternate parser/model/classifier is
introduced; all results come from ASDF and the existing foundation Case Records.
"""
import argparse
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
EVIDENCE = ROOT / 'reports/slice-21c'
BASE = 'd498716b1e30ca1ef2b5c124038b372851ccb731'
POLICY = '(version 1)(allow default)(deny network*)(deny file-write* (subpath "' + str(ROOT) + '"))'
ALLOWED_TRACKED = {'tests/xtm-identity.lisp', 'topic-maps.asd'}
EXCLUDED = ['reifier-collision.xtm', 'role-duplicate-reified.xtm', 'topicref-no-fragment-id.xtm', 'variant-missing-scope-duplicate.xtm']


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def prepare_pinned(target):
    # Reuse the existing local Store verifier and patcher, without a Nix daemon
    # evaluation or dependency download. The historical driver stays unchanged.
    spec = importlib.util.spec_from_file_location('slice21b', ROOT / 'scripts/validate-slice-21b.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.prepare_pinned(target)


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
    output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='topic-maps-21c-'))
    assert not output.is_relative_to(ROOT), 'Choose a temporary output directory outside the repository.'
    output.mkdir(parents=True, exist_ok=True)
    assert not (output / 'execution.json').exists(), 'Choose an unused output directory.'
    tracked = command(['git', 'ls-tree', '-r', '--name-only', BASE]).splitlines()
    assert set(command(['git', 'diff', '--name-only', BASE]).splitlines()) & set(tracked) <= ALLOWED_TRACKED
    protected = {p: sha(ROOT / p) for p in tracked if p not in ALLOWED_TRACKED}
    historical = {p: h for p, h in protected.items() if p.startswith('reports/')}
    sources = {p: sha(ROOT / p) for p in [*sorted(ALLOWED_TRACKED), 'tests/xtm-negative-originals.lisp',
        'scripts/validate-slice-21c.py', 'reports/slice-21c/candidate-inventory.json', 'reports/slice-21c/failure-controls.lisp']}
    candidates = read(EVIDENCE / 'candidate-inventory.json')['cases']
    ids = [c['id'] for c in candidates]
    assert len(ids) == len(set(ids)) == 7
    assert ids == ['xtm2/invalid/' + name + '.xtm' for name in ['id-invalid', 'itemid-collision', 'no-version',
        'reifier-elem-in-2.0', 'subjid-ref-in-2.0', 'subjloc-ref-in-2.0', 'topic-no-id']]
    prior = ROOT / 'reports/slice-21b'
    previous_xtm = read(prior / 'xtm.json')
    assert previous_xtm['statuses'] == {'pass': 26, 'fail': 0, 'unsupported': 0, 'not-run': 0}
    assert previous_xtm['otherCorpusInputs'] == {'positiveUnexecuted': 87, 'negativeUnregisteredUnexecuted': 11}
    ctm_statuses = {'pass': 262, 'fail': 4, 'unsupported': 0, 'not-run': 7}
    assert read(prior / 'ctm.validation.json')['statuses'] == ctm_statuses
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
    with tempfile.TemporaryDirectory(prefix='topic-maps-21c-sources-') as temp_name:
        provenance = json.loads(run('source-preparation', ['python3', str(Path(__file__)), '--prepare', temp_name + '/sources'], env))
        save(output / 'source-preparation.json', provenance)
        env.update(CL_SOURCE_REGISTRY=provenance['sourceRegistry'], TOPIC_MAPS_REPORT=str(retained / 'core.json'),
            TOPIC_MAPS_XTM_REPORT=str(output / 'xtm.json'), TOPIC_MAPS_XTM_MERGEMAP_REPORT=str(retained / 'xtm-mergemap'),
            TOPIC_MAPS_REGISTERED_ORIGINALS_REPORT=str(retained / 'slice20a'), TOPIC_MAPS_REGISTERED_NEGATIVES_REPORT=str(retained / 'slice20b'),
            TOPIC_MAPS_PROLOG_REPORT=str(retained / 'slice20c'), TOPIC_MAPS_EMPTY2_REPORT=str(retained / 'slice20e'),
            TOPIC_MAPS_CTM_INTEGER_REPORT=str(retained / 'slice20f'), TOPIC_MAPS_TRIPLE_REPORT=str(retained / 'slice20g'),
            TOPIC_MAPS_ENCODING_REPORT=str(output / 'ctm'))
        prefix = [runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script']
        xml = run('xml', prefix + ['tests/cxml-probe.lisp'], env)
        xml_labels = re.findall(r'^CXML-CHECK-PASS (.+)$', xml, re.M)
        assert len(xml_labels) == len(set(xml_labels)) == 146 and 'CXML-SUMMARY 146 PASS 0 FAIL' in xml
        xtm_log = run('xtm', prefix + ['scripts/fresh-xtm.lisp'], env)
        xtm = read(output / 'xtm.json')
        labels = re.findall(r'^XTM-CHECK-PASS (.+)$', xtm_log, re.M)
        assert labels == xtm['checks'] and len(labels) == len(set(labels)) and set(previous_xtm['checks']) <= set(labels)
        assert f'XTM-SUMMARY {len(labels)} PASS 0 FAIL; 26 original CXTM PASS; 7 negative originals PASS' in xtm_log
        assert xtm['statuses'] == {'pass': 33, 'fail': 0, 'unsupported': 0, 'not-run': 0}
        assert xtm['otherCorpusInputs'] == {'positiveUnexecuted': 87, 'negativeUnregisteredUnexecuted': 4}
        assert xtm['cases'][:26] == previous_xtm['cases']
        assert xtm['actualAndExpected'] == previous_xtm['actualAndExpected']
        assert xtm['helperSource'] == previous_xtm['helperSource']
        assert len(xtm['cases']) == len({c['id'] for c in xtm['cases']}) == 33
        assert [c['id'] for c in xtm['cases'][26:]] == ids
        assert all(c['status'] == 'pass' and c['actualOutcome'] == 'ctm-rejection' for c in xtm['cases'][26:])
        assert len(xtm['negativeOriginals']) == 7 and len(xtm['negativeControls']) == 13
        regression = run('regression', [str(ROOT / 'scripts/test.sh')], env)
        fault_controls = []
        # Preserve all five previously established positive-executor guards.
        for mode, outcome in [('mismatch', 'cxtm-mismatch'), ('xml', 'execution-error'), ('xtm', 'execution-error'),
                              ('tmdm', 'execution-error'), ('unsupported', 'unsupported')]:
            control_env = dict(env, TOPIC_MAPS_XTM_REPORT=str(output / ('retained-control-' + mode + '.json')), TOPIC_MAPS_21B_FAULT=mode)
            run('retained-control-' + mode, prefix + [str(prior / 'failure-controls.lisp')], control_env, expected_exit=1)
            result = read(output / ('retained-control-' + mode + '.json'))
            assert result['statuses']['pass'] == 0 and result['cases'][0]['actualOutcome'] == outcome
        for mode, outcome, condition_class in [('accepted', 'ctm-acceptance', None), ('xml', 'execution-error', 'XTM-XML-ERROR'),
                ('unsupported', 'unsupported', 'XTM-UNSUPPORTED'), ('wrong-cause', 'execution-error', 'XTM-REJECTION')]:
            control_env = dict(env, TOPIC_MAPS_XTM_REPORT=str(output / ('negative-control-' + mode + '.json')), TOPIC_MAPS_21C_FAULT=mode)
            run('negative-control-' + mode, prefix + [str(EVIDENCE / 'failure-controls.lisp')], control_env, expected_exit=1)
            result = read(output / ('negative-control-' + mode + '.json'))
            assert result['statuses']['pass'] == 26 and result['cases'][:26] == previous_xtm['cases']
            assert len(result['cases']) == 27 and result['cases'][-1]['actualOutcome'] == outcome
            negative = result['negativeOriginals'][0]
            assert not negative['intendedCauseReached'] and negative['status'] != 'pass'
            condition = negative['condition']
            assert (condition['class'] if condition else None) == condition_class
            fault_controls.append({'mode': mode, 'actualOutcome': outcome, 'condition': condition,
                'expectedASDFFailureObserved': True, 'positiveOriginalPassesPreserved': 26, 'negativeOriginalCountedAsPass': False})

    verified = []
    for old in sorted((prior / 'retained').glob('*.json')):
        assert read(old) == read(retained / old.name), str(old)
        verified.append(str(old.relative_to(ROOT)))
    for suffix in ['validation', 'cxtm', 'encoding']:
        old = prior / f'ctm.{suffix}.json'
        assert read(old) == read(output / f'ctm.{suffix}.json'), str(old)
        verified.append(str(old.relative_to(ROOT)))
    totals = read(ROOT / 'reports/slice-19d1/regression-execution.json')['regressionChecks']
    assert sum(totals.values()) == 12100
    stages = read(prior / 'execution.json')['stageChecks']
    for marker, count in dict(totals, **stages).items():
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', regression).group(1)) == count
    assert 'Ran 2 tests' in regression and 'NFC-ORACLE-PASS: 16294' in regression
    assert read(output / 'ctm.validation.json')['statuses'] == ctm_statuses
    for old, result in zip(candidates, xtm['negativeOriginals']):
        assert old['id'] == result['id'] and old['condition'] == result['condition']
        source = ROOT / 'vendor/cxtm' / old['id']
        raw = source.read_bytes()
        assert raw == bytes.fromhex(result['sourceHex']) == result['sourceText'].encode('utf-8')
        assert sha(source) == old['sourceSHA256'] and len(raw) == result['sourceBytes'] == old['sourceBytes']
        assert result['xmlWellFormed'] and result['intendedCauseReached'] and result['status'] == 'pass'
        assert not result['unsupported'] and result['condition']['cause'] is None
        result['sourceSHA256'] = sha(source)
    for positive in xtm['actualAndExpected']:
        p = ROOT / 'vendor/cxtm/xtm2/baseline' / (Path(positive['id']).name + '.cxtm')
        assert positive['actual'].encode('utf-8') == positive['expected'].encode('utf-8') == p.read_bytes()
    pending_negative = sorted('xtm2/invalid/' + p.name for p in (ROOT / 'vendor/cxtm/xtm2/invalid').glob('*.xtm') if 'xtm2/invalid/' + p.name not in ids)
    assert pending_negative == ['xtm2/invalid/' + name for name in EXCLUDED]
    assert not set(pending_negative) & {c['id'] for c in xtm['cases']}
    lock = read(ROOT / 'references/corpus-lock.json')
    for entry in lock['files']:
        p = ROOT / 'vendor/cxtm' / entry['path']
        assert p.stat().st_size == entry['size'] and sha(p) == entry['sha256']
    for snapshot in [protected, historical, sources]:
        assert snapshot == {p: sha(ROOT / p) for p in snapshot}
    assert set(command(['git', 'diff', '--name-only', BASE]).splitlines()) & set(tracked) <= ALLOWED_TRACKED
    save(output / 'negative-originals.json', {'kind': 'executed-cause-qualified-negative-originals', 'cases': xtm['negativeOriginals'],
        'excludedOriginals': [{'id': p, 'registeredStatus': 'not-run', 'executedInThisSlice': False} for p in pending_negative],
        'outcomeVocabulary': 'ctm-rejection is the existing foundation negative-outcome token; actual deserialization is XTM/TMDM.'})
    save(output / 'failure-controls.json', {'kind': 'negative-executor-fault-controls-not-corpus-results', 'controls': fault_controls})
    save(output / 'integrity.json', {'protectedBaseFilesSHA256': protected, 'historicalReportsSHA256': historical, 'executionSourcesSHA256': sources})
    statuses = dict(xtm['statuses'], **{'not-run': sum(xtm['otherCorpusInputs'].values())})
    save(output / 'execution.json', {'kind': 'xtm-negative-original-registration-validation', 'baseCommit': BASE,
        'branch': command(['git', 'branch', '--show-current']), 'runtime': 'SBCL 2.5.4', 'startedAtUTC': started,
        'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'runs': runs, 'sourcePreparation': 'source-preparation.json',
        'retainedLispChecks': 12100, 'retainedChecks': totals, 'stageChecks': stages, 'xmlQualificationChecks': 146,
        'standaloneXTMChecks': len(labels), 'retainedXTMCheckNamesPreserved': len(previous_xtm['checks']),
        'positiveOriginalComparisons': 26, 'positiveOriginalResultsUnchanged': True, 'newNegativeOriginals': 7,
        'validNegativeCounterexamples': 7, 'negativeClassificationControls': 6, 'positiveFaultControlsRetained': 5, 'negativeFaultControls': 4,
        'xtmStatusesBefore': {'pass': 26, 'fail': 0, 'unsupported': 0, 'not-run': 98}, 'xtmStatusesAfter': statuses,
        'xtmStatusChanges': [{'id': p, 'before': 'not-run', 'after': 'pass', 'actualOutcome': 'ctm-rejection'} for p in ids],
        'ctmStatusesBefore': ctm_statuses, 'ctmStatusesAfter': ctm_statuses, 'ctmStatusChanges': [],
        'knownFailuresUnchanged': [c['id'] for c in read(output / 'ctm.validation.json')['cases'] if c['status'] == 'fail'],
        'pythonUnitTests': 2, 'nfcOracleComparisons': 16294, 'allRetainedNonXTMReportsEqualToSlice21B': verified,
        'historicalReportFilesVerified': len(historical), 'protectedBaseFilesVerified': len(protected),
        'pinnedCorpusFilesVerified': len(lock['files']), 'historicalReportsUnchanged': True, 'originalSourcesAndBaselinesUnchanged': True,
        'productionCodeUnchanged': True, 'newDependencyDownloads': 0, 'persistentLispImagesTouched': False,
        'executionAuthorization': 'Regular require_escalated approval; all tests additionally deny network and repository writes; no symlink/configuration changes.',
        'fullOfflineNixRebuild': 'NOT-RUN; fresh SBCL loads with verified pinned local sources and existing XML patches.', 'acceptancePassed': True})
    print(json.dumps({'acceptancePassed': True, 'xtm': statuses, 'ctm': ctm_statuses, 'checks': len(labels), 'output': str(output)}))


if __name__ == '__main__':
    main()
