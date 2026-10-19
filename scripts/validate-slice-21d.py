#!/usr/bin/env python3
"""Validate basic Name originals through the existing XTM harness.

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
EVIDENCE = ROOT / 'reports/slice-21d'
BASE = '0eed7189a0cdd535c980c2160ae2065de21f5d93'
POLICY = '(version 1)(allow default)(deny network*)(deny file-write* (subpath "' + str(ROOT) + '"))'
ALLOWED_TRACKED = {'src/xtm/reader.lisp', 'tests/xtm-identity.lisp', 'tests/xtm-negative-originals.lisp', 'tests/ctm-xtm-mergemap.lisp', 'topic-maps.asd'}
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


def qualify_name_scope(value):
    if isinstance(value, dict):
        return {k: qualify_name_scope(v) for k, v in value.items()}
    if isinstance(value, list):
        return [qualify_name_scope(v) for v in value]
    if isinstance(value, str) and (value == 'unsupported-name' or value.startswith('unsupported-name:')):
        return value.replace('unsupported-name', 'unsupported-name-scope', 1)
    return value


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
    output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='topic-maps-21d-'))
    assert not output.is_relative_to(ROOT), 'Choose a temporary output directory outside the repository.'
    output.mkdir(parents=True, exist_ok=True)
    assert not (output / 'execution.json').exists(), 'Choose an unused output directory.'
    tracked = command(['git', 'ls-tree', '-r', '--name-only', BASE]).splitlines()
    assert set(command(['git', 'diff', '--name-only', BASE]).splitlines()) & set(tracked) <= ALLOWED_TRACKED
    protected = {p: sha(ROOT / p) for p in tracked if p not in ALLOWED_TRACKED}
    historical = {p: h for p, h in protected.items() if p.startswith('reports/')}
    sources = {p: sha(ROOT / p) for p in [*sorted(ALLOWED_TRACKED), 'tests/xtm-names.lisp',
        'scripts/validate-slice-21d.py', 'reports/slice-21d/candidate-inventory.json', 'reports/slice-21d/failure-controls.lisp',
        'reports/slice-21d/diagnostics.lisp', 'reports/slice-21d/before-diagnostics.json']}
    candidates = read(EVIDENCE / 'candidate-inventory.json')['candidates']
    ids = [c['id'] for c in candidates]
    assert len(ids) == len(set(ids)) == 10
    expected_names = ['name', 'name-unicode', 'name-escaping', 'name-duplicate', 'name-duplicate-merge',
        'merge-itemid-with-names', 'name-type', 'name-type-before', 'name-type-after', 'name-type-after-bad']
    assert ids == ['xtm2/in/' + n + '.xtm' for n in expected_names]
    prior = ROOT / 'reports/slice-21c'
    previous_xtm = read(prior / 'xtm.json')
    assert previous_xtm['statuses'] == {'pass': 33, 'fail': 0, 'unsupported': 0, 'not-run': 0}
    assert previous_xtm['otherCorpusInputs'] == {'positiveUnexecuted': 87, 'negativeUnregisteredUnexecuted': 4}
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
    with tempfile.TemporaryDirectory(prefix='topic-maps-21d-sources-') as temp_name:
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
        assert {x.replace('unsupported-name:', 'unsupported-name-scope:') for x in previous_xtm['checks']} <= set(labels)
        assert f'XTM-SUMMARY {len(labels)} PASS 0 FAIL; 36 original CXTM PASS; 7 negative originals PASS' in xtm_log
        assert xtm['statuses'] == {'pass': 43, 'fail': 0, 'unsupported': 0, 'not-run': 0}
        assert xtm['otherCorpusInputs'] == {'positiveUnexecuted': 77, 'negativeUnregisteredUnexecuted': 4}
        assert xtm['cases'][:33] == previous_xtm['cases']
        assert xtm['actualAndExpected'] == previous_xtm['actualAndExpected']
        assert xtm['negativeOriginals'] == previous_xtm['negativeOriginals']
        assert xtm['helperSource'] == previous_xtm['helperSource']
        assert len(xtm['cases']) == len({c['id'] for c in xtm['cases']}) == 43
        assert [c['id'] for c in xtm['cases'][33:]] == ids
        assert len(xtm['nameOriginals']) == 10 and len(xtm['nameControls']) == 50
        assert all(c['status'] == 'pass' and c['actualOutcome'] == 'cxtm-match' for c in xtm['cases'][33:])
        for old, current in zip(previous_xtm['negativeControls'], xtm['negativeControls']):
            if old['label'] != 'unsupported-is-not-pass':
                assert old == current
                continue
            assert old['label'] == current['label'] and old['status'] == current['status'] == 'unsupported'
            a, b = old['condition'], current['condition']
            assert a['class'] == b['class'] == 'XTM-UNSUPPORTED' and a['code'] == b['code'] == 'unsupported-construct'
            assert a['detail'] == 'XTM name is not implemented in this subset.'
            assert b['detail'] == 'XTM scope is not implemented in this subset.'
            assert b['column'] == a['column'] + 7
            assert {k: v for k, v in a.items() if k not in ['detail', 'column', 'message']} == {k: v for k, v in b.items() if k not in ['detail', 'column', 'message']}
        regression = run('regression', [str(ROOT / 'scripts/test.sh')], env)
        diag_env = dict(env, TOPIC_MAPS_21D_ROOT=str(ROOT), TOPIC_MAPS_21D_DIAGNOSTICS=str(output / 'after-diagnostics.json'))
        run('diagnostics', prefix + [str(EVIDENCE / 'diagnostics.lisp')], diag_env)
        fault_controls = []
        families = {'positive': [('mismatch', 'cxtm-mismatch'), ('xml', 'execution-error'), ('xtm', 'execution-error'), ('tmdm', 'execution-error'), ('unsupported', 'unsupported')],
                    'negative': [('accepted', 'ctm-acceptance'), ('xml', 'execution-error'), ('unsupported', 'unsupported'), ('wrong-cause', 'execution-error')],
                    'name': [('mismatch', 'cxtm-mismatch'), ('xml', 'execution-error'), ('unsupported', 'unsupported'), ('tmdm', 'execution-error')]}
        for family, modes in families.items():
            for mode, outcome in modes:
                label = family + '-control-' + mode
                control_env = dict(env, TOPIC_MAPS_XTM_REPORT=str(output / (label + '.json')),
                    TOPIC_MAPS_21D_FAMILY=family, TOPIC_MAPS_21D_FAULT=mode)
                run(label, prefix + [str(EVIDENCE / 'failure-controls.lisp')], control_env, expected_exit=1)
                result = read(output / (label + '.json'))
                retained_count = {'positive': 0, 'negative': 26, 'name': 33}[family]
                assert result['statuses']['pass'] == retained_count
                assert len(result['cases']) == retained_count + 1 and result['cases'][-1]['actualOutcome'] == outcome
                assert result['cases'][:retained_count] == previous_xtm['cases'][:retained_count]
                fault_controls.append({'family': family, 'mode': mode, 'actualOutcome': outcome,
                    'expectedASDFFailureObserved': True, 'retainedOriginalPasses': retained_count,
                    'faultCountedAsPass': False})

    verified = []
    for old in sorted((prior / 'retained').glob('*.json')):
        assert qualify_name_scope(read(old)) == read(retained / old.name), str(old)
        verified.append(str(old.relative_to(ROOT)))
    for suffix in ['validation', 'cxtm', 'encoding']:
        old = prior / f'ctm.{suffix}.json'
        assert qualify_name_scope(read(old)) == read(output / f'ctm.{suffix}.json'), str(old)
        verified.append(str(old.relative_to(ROOT)))
    totals = read(ROOT / 'reports/slice-19d1/regression-execution.json')['regressionChecks']
    assert sum(totals.values()) == 12100
    stages = read(prior / 'execution.json')['stageChecks']
    for marker, count in dict(totals, **stages).items():
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', regression).group(1)) == count
    assert 'Ran 2 tests' in regression and 'NFC-ORACLE-PASS: 16294' in regression
    assert read(output / 'ctm.validation.json')['statuses'] == ctm_statuses
    comparisons = []
    (output / 'actual').mkdir()
    for old, result in zip(candidates, xtm['nameOriginals']):
        assert old['id'] == result['id'] and result['condition'] is None and result['status'] == 'pass'
        source = ROOT / 'vendor/cxtm' / old['id']
        baseline = ROOT / 'vendor/cxtm/xtm2/baseline' / (source.name + '.cxtm')
        raw = source.read_bytes()
        assert raw == bytes.fromhex(result['sourceHex']) == result['sourceText'].encode('utf-8')
        assert sha(source) == old['sourceSHA256'] and len(raw) == result['sourceBytes'] == old['sourceBytes']
        actual = result['actualCXTM'].encode('utf-8')
        assert actual == result['expectedCXTM'].encode('utf-8') == baseline.read_bytes()
        assert len(actual) == result['actualBytes'] == result['expectedBytes'] == old['baselineBytes']
        assert sha(baseline) == old['baselineSHA256'] and result['firstDifferentByte'] is None
        assert result['model']['canonicalNameParentTypeReferences'] and result['documentIRI'] == old['documentIRI']
        (output / 'actual' / baseline.name).write_bytes(actual)
        comparisons.append(dict(result, sourceSHA256=sha(source), baselineSHA256=sha(baseline),
            actualSHA256=hashlib.sha256(actual).hexdigest(), executedInASDFTestOp=True))
    before_diag = read(EVIDENCE / 'before-diagnostics.json')
    after_diag = read(output / 'after-diagnostics.json')
    assert len(before_diag) == len(after_diag) == 124
    changes = []
    for a, b in zip(before_diag, after_diag):
        assert a['id'] == b['id'] and a['documentIRI'] == b['documentIRI']
        if a == b:
            continue
        assert a['condition']['class'] == 'XTM-UNSUPPORTED'
        assert a['condition']['detail'] == 'XTM name is not implemented in this subset.'
        if b['status'] == 'deserialized':
            assert b['id'] in ids and b['byteExact']
        else:
            assert b['condition']['class'] == 'XTM-UNSUPPORTED'
            assert b['condition']['code'] in ['unsupported-construct', 'reification']
        changes.append({'id': a['id'], 'before': a, 'after': b,
            'warrant': 'The formerly unsupported Name is now processed; any remaining excluded Name feature stays Unsupported.'})
    assert {b['id'] for a, b in zip(before_diag, after_diag) if a['status'] != 'deserialized' and b['status'] == 'deserialized'} == set(ids)
    save(output / 'diagnostic-changes.json', {'kind': 'read-only-diagnostic-observations-no-additional-registration', 'changes': changes,
        'unchangedOriginalObservations': 124 - len(changes), 'newByteExactOriginals': ids})
    for positive in xtm['actualAndExpected']:
        p = ROOT / 'vendor/cxtm/xtm2/baseline' / (Path(positive['id']).name + '.cxtm')
        assert positive['actual'].encode('utf-8') == positive['expected'].encode('utf-8') == p.read_bytes()
    pending_negative = sorted('xtm2/invalid/' + p.name for p in (ROOT / 'vendor/cxtm/xtm2/invalid').glob('*.xtm') if 'xtm2/invalid/' + p.name not in {c['id'] for c in xtm['negativeOriginals']})
    assert pending_negative == ['xtm2/invalid/' + name for name in EXCLUDED]
    assert not set(pending_negative) & {c['id'] for c in xtm['cases']}
    lock = read(ROOT / 'references/corpus-lock.json')
    for entry in lock['files']:
        p = ROOT / 'vendor/cxtm' / entry['path']
        assert p.stat().st_size == entry['size'] and sha(p) == entry['sha256']
    for snapshot in [protected, historical, sources]:
        assert snapshot == {p: sha(ROOT / p) for p in snapshot}
    assert set(command(['git', 'diff', '--name-only', BASE]).splitlines()) & set(tracked) <= ALLOWED_TRACKED
    save(output / 'name-originals.json', {'kind': 'executed-basic-name-originals', 'cases': comparisons,
        'excludedNegativeOriginals': pending_negative})
    save(output / 'failure-controls.json', {'kind': 'executor-fault-controls-not-corpus-results', 'controls': fault_controls})
    save(output / 'integrity.json', {'protectedBaseFilesSHA256': protected, 'historicalReportsSHA256': historical, 'executionSourcesSHA256': sources})
    statuses = dict(xtm['statuses'], **{'not-run': sum(xtm['otherCorpusInputs'].values())})
    save(output / 'execution.json', {'kind': 'xtm-basic-name-registration-validation', 'baseCommit': BASE,
        'branch': command(['git', 'branch', '--show-current']), 'runtime': 'SBCL 2.5.4', 'startedAtUTC': started,
        'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'runs': runs, 'sourcePreparation': 'source-preparation.json',
        'retainedLispChecks': 12100, 'retainedChecks': totals, 'stageChecks': stages, 'xmlQualificationChecks': 146,
        'standaloneXTMChecks': len(labels), 'retainedXTMCheckNamesPreserved': len(set(previous_xtm['checks']) & set(labels)),
        'retainedXTMChecksQualified': len(previous_xtm['checks']),
        'renamedXTMChecks': [{'before': x, 'after': x.replace('unsupported-name:', 'unsupported-name-scope:')}
                            for x in previous_xtm['checks'] if x.startswith('unsupported-name:')],
        'retainedOriginals': 33, 'retainedOriginalResultsUnchanged': True, 'newNameOriginals': 10,
        'nameCounterprobes': len(xtm['nameControls']), 'nameCounterprobeKinds': {k: sum(c['kind'] == k for c in xtm['nameControls']) for k in sorted({c['kind'] for c in xtm['nameControls']})},
        'faultControls': len(fault_controls), 'diagnosticOriginalObservations': 124, 'nameRelatedDiagnosticChanges': len(changes),
        'xtmStatusesBefore': {'pass': 33, 'fail': 0, 'unsupported': 0, 'not-run': 91}, 'xtmStatusesAfter': statuses,
        'xtmStatusChanges': [{'id': p, 'before': 'not-run', 'after': 'pass', 'actualOutcome': 'cxtm-match'} for p in ids],
        'ctmStatusesBefore': ctm_statuses, 'ctmStatusesAfter': ctm_statuses, 'ctmStatusChanges': [],
        'knownFailuresUnchanged': [c['id'] for c in read(output / 'ctm.validation.json')['cases'] if c['status'] == 'fail'],
        'pythonUnitTests': 2, 'nfcOracleComparisons': 16294, 'allRetainedNonXTMReportsQualifiedAgainstSlice21C': verified, 'retainedReportQualification': 'Only unsupported-name -> unsupported-name-scope fixture/check labels change.',
        'historicalReportFilesVerified': len(historical), 'protectedBaseFilesVerified': len(protected),
        'pinnedCorpusFilesVerified': len(lock['files']), 'historicalReportsUnchanged': True, 'originalSourcesAndBaselinesUnchanged': True,
        'productionChangesLimitedToXTMReader': True, 'TMDM_CTM_CXTM_XML_Unchanged': True, 'newDependencyDownloads': 0, 'persistentLispImagesTouched': False,
        'executionAuthorization': 'Regular require_escalated approval; all tests additionally deny network and repository writes; no symlink/configuration changes.',
        'fullOfflineNixRebuild': 'NOT-RUN; fresh SBCL loads with verified pinned local sources and existing XML patches.', 'acceptancePassed': True})
    print(json.dumps({'acceptancePassed': True, 'xtm': statuses, 'ctm': ctm_statuses, 'checks': len(labels), 'output': str(output)}))


if __name__ == '__main__':
    main()
