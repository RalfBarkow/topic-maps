#!/usr/bin/env python3
"""Register one existing XTM Variant Merge original through the existing ASDF/Case Record harness.

The driver checks and retains execution evidence; Lisp performs all parsing,
model construction and conformance classification. Historical reports are inputs.
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
EVIDENCE = ROOT / 'reports/slice-21h'
PRIOR = ROOT / 'reports/slice-21g'
BASE = '39c125bf9d462f538403aa633c56054511c210da'
POLICY = '(version 1)(allow default)(deny network*)(deny file-write* (subpath "' + str(ROOT) + '"))'
ALLOWED = {'tests/xtm-identity.lisp', 'tests/xtm-variants.lisp', 'topic-maps.asd'}
CTM = {'pass': 262, 'fail': 4, 'unsupported': 0, 'not-run': 7}
TARGET = 'xtm2/in/merge-itemid-with-variants.xtm'


def read(p):
    return json.loads(p.read_text())


def save(p, v):
    p.write_text(json.dumps(v, indent=2, ensure_ascii=False) + '\n')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def command(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def prepare_pinned(target):
    spec = importlib.util.spec_from_file_location('slice21g', ROOT / 'scripts/validate-slice-21g.py')
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
    output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='topic-maps-21h-'))
    assert not output.is_relative_to(ROOT)
    output.mkdir(parents=True, exist_ok=True)
    assert not (output / 'execution.json').exists(), 'Choose an unused output directory.'
    tracked = command(['git', 'ls-tree', '-r', '--name-only', BASE]).splitlines()
    assert set(command(['git', 'diff', '--name-only', BASE]).splitlines()) & set(tracked) <= ALLOWED
    protected = {p: sha(ROOT / p) for p in tracked if p not in ALLOWED}
    historical = {p: h for p, h in protected.items() if p.startswith('reports/')}
    sources = {p: sha(ROOT / p) for p in [*sorted(ALLOWED), 'scripts/validate-slice-21h.py',
        *['reports/slice-21h/' + p for p in ['candidate-inventory.json', 'failure-controls.lisp', 'diagnostics.lisp',
                                          'before-diagnostics.json', 'baseline-xtm.json']]]}
    previous = read(PRIOR / 'xtm.json')
    assert read(EVIDENCE / 'baseline-xtm.json') == previous
    assert previous['statuses'] == {'pass': 56, 'fail': 0, 'unsupported': 0, 'not-run': 0}
    assert previous['otherCorpusInputs'] == {'positiveUnexecuted': 65, 'negativeUnregisteredUnexecuted': 3}
    assert read(PRIOR / 'ctm.validation.json')['statuses'] == CTM
    candidate = read(EVIDENCE / 'candidate-inventory.json')
    assert candidate['id'] == TARGET and candidate['sourceBytes'] == 641 and candidate['baselineBytes'] == 919
    assert TARGET not in {c['id'] for c in previous['cases']}
    assert read(EVIDENCE / 'before-diagnostics.json') == read(PRIOR / 'after-diagnostics.json')
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
    with tempfile.TemporaryDirectory(prefix='topic-maps-21h-sources-') as temp_name:
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
        assert labels == xtm['checks'] and len(labels) == len(set(labels))
        assert set(previous['checks']) <= set(labels)
        assert [label for label in labels if label in set(previous['checks'])] == previous['checks']
        assert f'XTM-SUMMARY {len(labels)} PASS 0 FAIL; 49 original CXTM PASS; 8 negative originals PASS' in xtm_log
        assert xtm['statuses'] == {'pass': 57, 'fail': 0, 'unsupported': 0, 'not-run': 0}
        assert xtm['otherCorpusInputs'] == {'positiveUnexecuted': 64, 'negativeUnregisteredUnexecuted': 3}
        assert xtm['cases'][:56] == previous['cases']
        for field, value in previous.items():
            if field not in ['scope', 'statuses', 'otherCorpusInputs', 'checks', 'cases']:
                assert xtm[field] == value, field
        assert len(xtm['cases']) == len({c['id'] for c in xtm['cases']}) == 57
        assert xtm['cases'][56]['id'] == TARGET and xtm['cases'][56]['status'] == 'pass'
        assert xtm['cases'][56]['actualOutcome'] == 'cxtm-match' and len(xtm['variantMergeOriginals']) == 1
        regression = run('regression', [str(ROOT / 'scripts/test.sh')], env)
        run('diagnostics', prefix + [str(EVIDENCE / 'diagnostics.lisp')],
            dict(env, TOPIC_MAPS_21H_ROOT=str(ROOT), TOPIC_MAPS_21H_DIAGNOSTICS=str(output / 'after-diagnostics.json')))
        fault_controls = []
        positive_modes = [('mismatch', 'cxtm-mismatch'), ('xml', 'execution-error'), ('unsupported', 'unsupported'), ('tmdm', 'execution-error')]
        negative_modes = [('accepted', 'ctm-acceptance'), ('xml', 'execution-error'), ('unsupported', 'unsupported'), ('wrong-cause', 'execution-error')]
        families = {'positive': positive_modes + [('xtm', 'execution-error')], 'negative': negative_modes,
                    'name': positive_modes, 'scope': positive_modes, 'iid': positive_modes, 'variant': positive_modes,
                    'variant-negative': negative_modes + [('tmdm', 'execution-error')],
                    'merge-variant': positive_modes + [('xtm', 'execution-error')]}
        for family, modes in families.items():
            for mode, outcome in modes:
                label = family + '-control-' + mode
                run(label, prefix + [str(EVIDENCE / 'failure-controls.lisp')],
                    dict(env, TOPIC_MAPS_XTM_REPORT=str(output / (label + '.json')), TOPIC_MAPS_21H_FAMILY=family, TOPIC_MAPS_21H_FAULT=mode), expected_exit=1)
                result = read(output / (label + '.json'))
                retained_count = {'positive': 0, 'negative': 26, 'name': 33, 'scope': 43, 'iid': 48, 'variant': 50, 'variant-negative': 55, 'merge-variant': 56}[family]
                assert result['statuses']['pass'] == retained_count
                assert len(result['cases']) == retained_count + 1 and result['cases'][-1]['actualOutcome'] == outcome
                assert result['cases'][:retained_count] == xtm['cases'][:retained_count]
                fault_controls.append({'family': family, 'mode': mode, 'actualOutcome': outcome,
                    'expectedASDFFailureObserved': True, 'retainedOriginalPasses': retained_count, 'faultCountedAsPass': False})

    verified = []
    for old in sorted((PRIOR / 'retained').glob('*.json')):
        assert read(old) == read(retained / old.name), str(old)
        verified.append(str(old.relative_to(ROOT)))
    for suffix in ['validation', 'cxtm', 'encoding']:
        old = PRIOR / f'ctm.{suffix}.json'
        assert read(old) == read(output / f'ctm.{suffix}.json'), str(old)
        verified.append(str(old.relative_to(ROOT)))
    totals = read(ROOT / 'reports/slice-19d1/regression-execution.json')['regressionChecks']
    stages = read(PRIOR / 'execution.json')['stageChecks']
    assert sum(totals.values()) == 12100
    for marker, count in dict(totals, **stages).items():
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', regression).group(1)) == count
    assert 'Ran 2 tests' in regression and 'NFC-ORACLE-PASS: 16294' in regression
    assert read(output / 'ctm.validation.json')['statuses'] == CTM
    result = xtm['variantMergeOriginals'][0]
    assert result['id'] == TARGET and result['condition'] is None and result['status'] == 'pass'
    source = ROOT / 'vendor/cxtm' / TARGET
    baseline = ROOT / 'vendor/cxtm/xtm2/baseline/merge-itemid-with-variants.xtm.cxtm'
    raw, actual = source.read_bytes(), result['actualCXTM'].encode('utf-8')
    assert raw == bytes.fromhex(result['sourceHex']) == result['sourceText'].encode('utf-8')
    assert sha(source) == candidate['sourceSHA256'] and len(raw) == result['sourceBytes'] == 641
    assert actual == result['expectedCXTM'].encode('utf-8') == baseline.read_bytes()
    assert len(actual) == result['actualBytes'] == result['expectedBytes'] == 919
    assert sha(baseline) == candidate['baselineSHA256'] and result['firstDifferentByte'] is None
    assert result['model']['canonicalVariantReferences'] and result['documentIRI'] == candidate['documentIRI'] and result['sourceKey'] == TARGET
    assert len(result['originalReaderStages']) == 2
    assert result['originalReaderStages'][1]['model'] == result['model']
    (output / 'actual').mkdir()
    (output / 'actual' / baseline.name).write_bytes(actual)
    comparison = dict(result, sourceSHA256=sha(source), baselineSHA256=sha(baseline),
                      actualSHA256=hashlib.sha256(actual).hexdigest(), executedInASDFTestOp=True)
    before, after = read(EVIDENCE / 'before-diagnostics.json'), read(output / 'after-diagnostics.json')
    assert len(before) == len(after) == 124 and before == after
    observation = next(c for c in after if c['id'] == TARGET)
    assert observation == candidate['priorEvidence']['observation']
    assert observation['byteExact'] and observation['actualCXTM'].encode('utf-8') == actual
    lock = read(ROOT / 'references/corpus-lock.json')
    for entry in lock['files']:
        p = ROOT / 'vendor/cxtm' / entry['path']
        assert p.stat().st_size == entry['size'] and sha(p) == entry['sha256']
    for snapshot in [protected, historical, sources]:
        assert snapshot == {p: sha(ROOT / p) for p in snapshot}
    assert set(command(['git', 'diff', '--name-only', BASE]).splitlines()) & set(tracked) <= ALLOWED
    save(output / 'variant-merge-original.json', {'kind': 'executed-original-variant-merge-registration', 'case': comparison})
    save(output / 'diagnostics.json', {'kind': 'read-only-observations-no-extra-registration',
        'originalObservations': 124, 'unchangedOriginalObservations': 124, 'diagnosticChanges': [],
        'priorSlice21GObservationReproduced': True, 'newlyRegisteredCase': TARGET})
    save(output / 'failure-controls.json', {'kind': 'executor-fault-controls-not-corpus-results', 'controls': fault_controls})
    save(output / 'integrity.json', {'protectedBaseFilesSHA256': protected, 'historicalReportsSHA256': historical, 'executionSourcesSHA256': sources})
    statuses = dict(xtm['statuses'], **{'not-run': sum(xtm['otherCorpusInputs'].values())})
    save(output / 'execution.json', {'kind': 'xtm-variant-merge-original-registration-validation', 'baseCommit': BASE,
        'branch': command(['git', 'branch', '--show-current']), 'runtime': 'SBCL 2.5.4', 'startedAtUTC': started,
        'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'runs': runs,
        'sourcePreparation': 'source-preparation.json', 'retainedLispChecks': 12100, 'retainedChecks': totals,
        'stageChecks': stages, 'xmlQualificationChecks': 146, 'standaloneXTMChecks': len(labels),
        'retainedXTMCheckNamesPreserved': len(previous['checks']), 'newXTMChecks': len(labels) - len(previous['checks']),
        'retainedOriginals': 56, 'retainedOriginalResultsUnchanged': True, 'newPositiveOriginals': 1,
        'originalByteComparison': {'actual': len(actual), 'baseline': 919, 'firstDifferentByte': None},
        'originalReaderStageCount': len(result['originalReaderStages']), 'faultControls': len(fault_controls),
        'diagnosticOriginalObservations': 124, 'diagnosticChanges': [],
        'xtmStatusesBefore': {'pass': 56, 'fail': 0, 'unsupported': 0, 'not-run': 68}, 'xtmStatusesAfter': statuses,
        'xtmStatusChanges': [{'id': TARGET, 'before': 'not-run', 'after': 'pass', 'actualOutcome': 'cxtm-match'}],
        'ctmStatusesBefore': CTM, 'ctmStatusesAfter': CTM, 'ctmStatusChanges': [],
        'knownFailuresUnchanged': [c['id'] for c in read(output / 'ctm.validation.json')['cases'] if c['status'] == 'fail'],
        'pythonUnitTests': 2, 'nfcOracleComparisons': 16294, 'allRetainedNonXTMReportsIdenticalToSlice21G': verified,
        'historicalReportFilesVerified': len(historical), 'protectedBaseFilesVerified': len(protected), 'pinnedCorpusFilesVerified': len(lock['files']),
        'historicalReportsUnchanged': True, 'originalSourcesAndBaselinesUnchanged': True, 'productionCodeUnchanged': True,
        'newDependencyDownloads': 0, 'persistentLispImagesTouched': False,
        'executionAuthorization': 'Regular require_escalated approval; tests additionally deny network and repository writes; no symlink/configuration changes.',
        'fullOfflineNixRebuild': 'NOT-RUN; fresh SBCL loads with verified pinned local sources and existing XML patches.', 'acceptancePassed': True})
    print(json.dumps({'acceptancePassed': True, 'xtm': statuses, 'ctm': CTM, 'checks': len(labels), 'output': str(output)}))


if __name__ == '__main__':
    main()
