#!/usr/bin/env python3
"""Validate XTM Topic Name Reification originals through the existing ASDF/Case Record harness.

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
EVIDENCE = ROOT / 'reports/slice-21m'
PRIOR = ROOT / 'reports/slice-21l'
BASE = '6e7c8fc9f247a3e4419299caa7836366573c8c63'
POLICY = '(version 1)(allow default)(deny network*)(deny file-write* (subpath "' + str(ROOT) + '"))'
ALLOWED = {'src/xtm/reader.lisp', 'tests/xtm-identity.lisp', 'tests/ctm-xtm-mergemap.lisp', 'topic-maps.asd',
           'tests/xtm-names.lisp', 'tests/xtm-name-scopes.lisp', 'tests/xtm-name-item-identities.lisp', 'tests/xtm-map-reification.lisp'}
CTM = {'pass': 262, 'fail': 4, 'unsupported': 0, 'not-run': 7}
TARGETS = ['xtm2/in/name-reifier.xtm', 'xtm2/in/name-duplicate-reified.xtm']
EXPLORATORY = ['xtm2/in/name-duplicate-reified' + n + '.xtm' for n in ['2', '3', '4']]


def read(p):
    return json.loads(p.read_text())


def save(p, v):
    p.write_text(json.dumps(v, indent=2, ensure_ascii=False) + '\n')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def command(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def prepare_pinned(target):
    spec = importlib.util.spec_from_file_location('slice21g', ROOT / 'scripts/validate-slice-21l.py')
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
    output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='topic-maps-21m-'))
    assert not output.is_relative_to(ROOT)
    output.mkdir(parents=True, exist_ok=True)
    assert not (output / 'execution.json').exists(), 'Choose an unused output directory.'
    tracked = command(['git', 'ls-tree', '-r', '--name-only', BASE]).splitlines()
    assert set(command(['git', 'diff', '--name-only', BASE]).splitlines()) & set(tracked) <= ALLOWED
    protected = {p: sha(ROOT / p) for p in tracked if p not in ALLOWED}
    historical = {p: h for p, h in protected.items() if p.startswith('reports/')}
    sources = {p: sha(ROOT / p) for p in [*sorted(ALLOWED), 'tests/xtm-name-reification.lisp', 'scripts/validate-slice-21m.py',
        *['reports/slice-21m/' + p for p in ['candidate-inventory.json', 'api-preflight.lisp', 'failure-controls.lisp', 'diagnostics.lisp',
                                          'before-diagnostics.json', 'baseline-xtm.json', 'retargeted-controls.json']]]}
    previous = read(PRIOR / 'xtm.json')
    assert read(EVIDENCE / 'baseline-xtm.json') == previous
    assert previous['statuses'] == {'pass': 63, 'fail': 0, 'unsupported': 0, 'not-run': 0}
    assert previous['otherCorpusInputs'] == {'positiveUnexecuted': 58, 'negativeUnregisteredUnexecuted': 3}
    assert read(PRIOR / 'ctm.validation.json')['statuses'] == CTM
    candidate = read(EVIDENCE / 'candidate-inventory.json')
    assert [c['id'] for c in candidate['candidates']] == TARGETS
    assert [c['sourceBytes'] for c in candidate['candidates']] == [180, 251]
    assert [c['baselineBytes'] for c in candidate['candidates']] == [434, 435]
    assert not set(TARGETS) & {c['id'] for c in previous['cases']}
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
    with tempfile.TemporaryDirectory(prefix='topic-maps-21m-sources-') as temp_name:
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
        api_probe = run('name-reifier-api-preflight', prefix + [str(EVIDENCE / 'api-preflight.lisp')], env)
        assert 'NAME-REIFIER-API-PREFLIGHT-PASS:' in api_probe
        xtm_log = run('xtm', prefix + ['scripts/fresh-xtm.lisp'], env)
        xtm = read(output / 'xtm.json')
        labels = re.findall(r'^XTM-CHECK-PASS (.+)$', xtm_log, re.M)
        assert labels == xtm['checks'] and len(labels) == len(set(labels))
        substitutions = {'name-syntax:unsupported-reifier:': 'name-syntax:unsupported-variant-reifier:',
            'name-syntax:scope:name-reifier-stays-unsupported:': 'name-syntax:scope:variant-reifier-stays-unsupported:',
            'name-syntax:iid:reifier-stays-unsupported:': 'name-syntax:iid:variant-reifier-stays-unsupported:',
            'map-reifier-error:name-reification:': 'map-reifier-error:name-with-variant-reification:'}
        rename = {label: label.replace(old, new) for label in previous['checks'] for old, new in substitutions.items() if label.startswith(old)}
        assert len(rename) == 8
        retained_labels = [rename.get(label, label) for label in previous['checks']]
        assert set(retained_labels) <= set(labels)
        assert [label for label in labels if label in set(retained_labels)] == retained_labels
        assert f'XTM-SUMMARY {len(labels)} PASS 0 FAIL; 57 original CXTM PASS; 8 negative originals PASS' in xtm_log
        assert xtm['statuses'] == {'pass': 65, 'fail': 0, 'unsupported': 0, 'not-run': 0}
        assert xtm['otherCorpusInputs'] == {'positiveUnexecuted': 56, 'negativeUnregisteredUnexecuted': 3}
        assert xtm['cases'][:63] == previous['cases']
        control_retargets = read(EVIDENCE / 'retargeted-controls.json')['controls']
        expected_fields = {'nameControls', 'scopeControls', 'nameItemIdentityControls', 'mapReifierControls'}
        assert {row['field'] for row in control_retargets} == expected_fields and len(control_retargets) == 4
        for field, value in previous.items():
            if field in expected_fields:
                assert len(xtm[field]) == len(value)
                changed = [(a, b) for a, b in zip(value, xtm[field]) if a != b]
                approved = [(row['before'], row['after']) for row in control_retargets if row['field'] == field]
                assert changed == approved
                a, b = changed[0]
                assert a['condition']['class'] == b['condition']['class'] == 'XTM-UNSUPPORTED'
                assert a['condition']['code'] == b['condition']['code'] == 'reification'
                assert '<name reifier=' in a['sourceText'] and '<variant reifier=' in b['sourceText']
            elif field not in ['scope', 'statuses', 'otherCorpusInputs', 'checks', 'cases']:
                assert xtm[field] == value, field
        assert len(xtm['cases']) == len({c['id'] for c in xtm['cases']}) == 65
        assert [c['id'] for c in xtm['cases'][63:]] == TARGETS
        assert all(c['status'] == 'pass' and c['actualOutcome'] == 'cxtm-match' for c in xtm['cases'][63:])
        assert len(xtm['nameReifierOriginals']) == 2
        regression = run('regression', [str(ROOT / 'scripts/test.sh')], env)
        run('diagnostics', prefix + [str(EVIDENCE / 'diagnostics.lisp')],
            dict(env, TOPIC_MAPS_21M_ROOT=str(ROOT), TOPIC_MAPS_21M_DIAGNOSTICS=str(output / 'after-diagnostics.json')))
        fault_controls = []
        positive_modes = [('mismatch', 'cxtm-mismatch'), ('xml', 'execution-error'), ('unsupported', 'unsupported'), ('tmdm', 'execution-error')]
        negative_modes = [('accepted', 'ctm-acceptance'), ('xml', 'execution-error'), ('unsupported', 'unsupported'), ('wrong-cause', 'execution-error')]
        families = {'positive': positive_modes + [('xtm', 'execution-error')], 'negative': negative_modes,
                    'name': positive_modes, 'scope': positive_modes, 'iid': positive_modes, 'variant': positive_modes,
                    'variant-negative': negative_modes + [('tmdm', 'execution-error')],
                    'merge-variant': positive_modes + [('xtm', 'execution-error')],
                    'resource-ref': positive_modes + [('xtm', 'execution-error')],
                    'resource-ref-relative': positive_modes + [('xtm', 'execution-error')],
                    'uri-data': positive_modes + [('xtm', 'execution-error')],
                    'variant-iid': positive_modes + [('xtm', 'execution-error')],
                    'variant-iid-duplicate': positive_modes + [('xtm', 'execution-error')],
                    'map-reifier': positive_modes + [('xtm', 'execution-error')],
                    'map-reifier-condition': [('wrong-cause', 'foreign-reifier-rejected-as-wrong-condition')],
                    'name-reifier': positive_modes + [('xtm', 'execution-error')],
                    'name-reifier-duplicate': positive_modes + [('xtm', 'execution-error')],
                    'name-reifier-condition': [('wrong-cause', 'foreign-reifier-rejected-as-wrong-condition')]}
        for family, modes in families.items():
            for mode, outcome in modes:
                label = family + '-control-' + mode
                run(label, prefix + [str(EVIDENCE / 'failure-controls.lisp')],
                    dict(env, TOPIC_MAPS_XTM_REPORT=str(output / (label + '.json')), TOPIC_MAPS_21M_FAMILY=family, TOPIC_MAPS_21M_FAULT=mode), expected_exit=1)
                result = read(output / (label + '.json'))
                retained_count = {'positive': 0, 'negative': 26, 'name': 33, 'scope': 43, 'iid': 48, 'variant': 50, 'variant-negative': 55, 'merge-variant': 56, 'resource-ref': 57, 'resource-ref-relative': 58, 'uri-data': 59, 'variant-iid': 60, 'variant-iid-duplicate': 61, 'map-reifier': 62, 'map-reifier-condition': 63, 'name-reifier': 63, 'name-reifier-duplicate': 64, 'name-reifier-condition': 65}[family]
                assert result['statuses']['pass'] == retained_count
                if family in ['map-reifier-condition', 'name-reifier-condition']:
                    assert len(result['cases']) == retained_count
                    is_name = family == 'name-reifier-condition'
                    wrong_label = 'name:native-reuse-reifier' if is_name else 'reuse-reifier'
                    wrong = next(row for row in result['nameReifierControls' if is_name else 'mapReifierControls'] if row['label'] == wrong_label)
                    assert wrong['expectedCode'] == 'reifier-conflict'
                    assert wrong['condition']['class'] == 'REIFICATION-ERROR' and wrong['condition']['code'] == 'foreign-reifier'
                    assert wrong['atomicNativeOperation']
                    assert result['checks'][-1] == 'map-reifier-error:' + wrong_label + ':specific-class-code'
                else:
                    assert len(result['cases']) == retained_count + 1 and result['cases'][-1]['actualOutcome'] == outcome
                assert result['cases'][:retained_count] == xtm['cases'][:retained_count]
                if family in ['map-reifier', 'name-reifier', 'name-reifier-duplicate'] and mode == 'tmdm':
                    outputs = result['mapReifierOriginals'] if family == 'map-reifier' else result['nameReifierOriginals']
                    actual_condition = next(row for row in outputs if row['id'] == result['cases'][-1]['id'])['condition']
                    assert actual_condition['class'] == 'REIFICATION-ERROR' and actual_condition['code'] == 'reifier-conflict'
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
    comparisons = []
    (output / 'actual').mkdir()
    for candidate_case, result in zip(candidate['candidates'], xtm['nameReifierOriginals']):
        assert result['id'] == candidate_case['id'] and result['condition'] is None and result['status'] == 'pass'
        source = ROOT / 'vendor/cxtm' / result['id']
        baseline = ROOT / 'vendor/cxtm/xtm2/baseline' / (source.name + '.cxtm')
        raw, actual = source.read_bytes(), result['actualCXTM'].encode('utf-8')
        assert raw == bytes.fromhex(result['sourceHex']) == result['sourceText'].encode('utf-8')
        assert sha(source) == candidate_case['sourceSHA256'] and len(raw) == result['sourceBytes'] == candidate_case['sourceBytes']
        assert actual == result['expectedCXTM'].encode('utf-8') == baseline.read_bytes()
        assert len(actual) == result['actualBytes'] == result['expectedBytes'] == candidate_case['baselineBytes']
        assert sha(baseline) == candidate_case['baselineSHA256'] and result['firstDifferentByte'] is None
        assert result['documentIRI'] == candidate_case['documentIRI'] and result['sourceKey'] == result['id']
        model = result['model']
        identity = model['identity']['nameModel']['identity']
        assert model['canonicalNameReifierInverseEQ'] and model['mapReifierTopic'] is None
        assert model['nameReifierTopics'] == [3] and model['topicReifiedNames'] == [None, None, 1]
        assert identity['topicCount'] == 3 and identity['associationCount'] == 0
        assert identity['topics'] == [
            {'ordinal': 1, 'itemIdentifiers': [result['documentIRI'] + '#topic'], 'subjectIdentifiers': [], 'subjectLocators': []},
            {'ordinal': 2, 'itemIdentifiers': [], 'subjectIdentifiers': ['http://psi.topicmaps.org/iso13250/model/topic-name'], 'subjectLocators': []},
            {'ordinal': 3, 'itemIdentifiers': [result['reifierLocator']], 'subjectIdentifiers': [], 'subjectLocators': []}]
        assert model['identity']['nameModel']['mapItemIdentifiers'] == []
        assert model['identity']['nameModel']['names'] == [{'value': 'Topic', 'parent': 1, 'type': 2, 'scope': [], 'itemIdentifiers': [], 'variantCount': 0}]
        assert model['identity']['variants'] == []
        expected_r = '#reifier' if result['id'] == TARGETS[0] else '#reifier1'
        assert result['reifierLocator'] == result['documentIRI'] + expected_r
        assert result['sourceNameCount'] == (1 if result['id'] == TARGETS[0] else 2)
        (output / 'actual' / baseline.name).write_bytes(actual)
        comparisons.append(dict(result, sourceSHA256=sha(source), baselineSHA256=sha(baseline),
            actualSHA256=hashlib.sha256(actual).hexdigest(), executedInASDFTestOp=True))
    before, after = read(EVIDENCE / 'before-diagnostics.json'), read(output / 'after-diagnostics.json')
    assert len(before) == len(after) == 124
    assert [c['id'] for c in before] == [c['id'] for c in after]
    changes = [{'id': a['id'], 'before': b, 'after': a,
                'reason': ('Name Reification is assigned to the canonical add-name result using the shared II lookup; original registered after complete byte comparison.'
                           if a['id'] in TARGETS else 'Read-only diagnostic: existing Variant/Name-identifier support also permits this source after Name Reification. Deliberately unregistered.')}
               for b, a in zip(before, after) if b != a]
    assert {c['id'] for c in changes} == set(TARGETS + EXPLORATORY)
    for change in changes:
        assert change['before']['condition']['class'] == 'XTM-UNSUPPORTED'
        assert change['before']['condition']['code'] == 'reification'
        assert change['after']['condition'] is None and change['after']['byteExact']
        if change['id'] in TARGETS:
            assert next(c for c in comparisons if c['id'] == change['id'])['actualCXTM'] == change['after']['actualCXTM']
    assert not set(EXPLORATORY) & {case['id'] for case in xtm['cases']}
    further = []
    for id in EXPLORATORY:
        source = ROOT / 'vendor/cxtm' / id
        baseline = ROOT / 'vendor/cxtm/xtm2/baseline' / (source.name + '.cxtm')
        observed = next(row for row in after if row['id'] == id)
        assert observed['actualCXTM'].encode('utf-8') == baseline.read_bytes()
        further.append({'id': id, 'registered': False, 'registeredStatus': 'not-run', 'sourceBytes': source.stat().st_size,
            'sourceHex': source.read_bytes().hex(), 'sourceText': source.read_text(), 'sourceSHA256': sha(source),
            'baselineBytes': baseline.stat().st_size, 'baselineSHA256': sha(baseline), 'observation': observed})
    save(output / 'further-name-reification-observations.json', {'kind': 'read-only-original-observations-no-registration', 'cases': further})
    pending_negative = ['xtm2/invalid/' + stem + '.xtm' for stem in
                        ['reifier-collision', 'role-duplicate-reified', 'topicref-no-fragment-id']]
    assert not set(pending_negative) & {case['id'] for case in xtm['cases']}
    save(output / 'diagnostic-changes.json', changes)
    lock = read(ROOT / 'references/corpus-lock.json')
    for entry in lock['files']:
        p = ROOT / 'vendor/cxtm' / entry['path']
        assert p.stat().st_size == entry['size'] and sha(p) == entry['sha256']
    for snapshot in [protected, historical, sources]:
        assert snapshot == {p: sha(ROOT / p) for p in snapshot}
    assert set(command(['git', 'diff', '--name-only', BASE]).splitlines()) & set(tracked) <= ALLOWED
    save(output / 'name-reifier-originals.json', {'kind': 'executed-original-name-reifier-registration', 'cases': comparisons})
    save(output / 'diagnostics.json', {'kind': 'read-only-observations-no-extra-registration',
        'originalObservations': 124, 'unchangedOriginalObservations': 124 - len(changes),
        'diagnosticChanges': changes, 'registeredCases': TARGETS, 'negativeOriginalsRemainingNotRun': pending_negative,
        'other119ObservationsUnchanged': True, 'additionalSuccessfulOriginalsRemainingNotRun': EXPLORATORY})
    save(output / 'failure-controls.json', {'kind': 'executor-fault-controls-not-corpus-results', 'controls': fault_controls})
    save(output / 'integrity.json', {'protectedBaseFilesSHA256': protected, 'historicalReportsSHA256': historical, 'executionSourcesSHA256': sources})
    statuses = dict(xtm['statuses'], **{'not-run': sum(xtm['otherCorpusInputs'].values())})
    save(output / 'execution.json', {'kind': 'xtm-name-reifier-original-registration-validation', 'baseCommit': BASE,
        'branch': command(['git', 'branch', '--show-current']), 'runtime': 'SBCL 2.5.4', 'startedAtUTC': started,
        'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'runs': runs,
        'sourcePreparation': 'source-preparation.json', 'retainedLispChecks': 12100, 'retainedChecks': totals,
        'stageChecks': stages, 'xmlQualificationChecks': 146, 'nativeNameReifierAPIPreflightPassed': True, 'standaloneXTMChecks': len(labels),
        'retainedXTMChecks': len(previous['checks']), 'retargetedUnsupportedCheckNames': rename,
        'newXTMChecks': len(labels) - len(previous['checks']), 'retargetedUnsupportedControlRows': control_retargets,
        'retainedOriginals': 63, 'retainedOriginalResultsUnchanged': True, 'newPositiveOriginals': 2,
        'originalByteComparisons': [{'id': c['id'], 'actual': c['actualBytes'], 'baseline': c['expectedBytes'], 'firstDifferentByte': None} for c in comparisons], 'faultControls': len(fault_controls),
        'diagnosticOriginalObservations': 124, 'diagnosticChangedOriginals': [c['id'] for c in changes],
        'xtmStatusesBefore': {'pass': 63, 'fail': 0, 'unsupported': 0, 'not-run': 61}, 'xtmStatusesAfter': statuses,
        'xtmStatusChanges': [{'id': id, 'before': 'not-run', 'after': 'pass', 'actualOutcome': 'cxtm-match'} for id in TARGETS],
        'ctmStatusesBefore': CTM, 'ctmStatusesAfter': CTM, 'ctmStatusChanges': [],
        'knownFailuresUnchanged': [c['id'] for c in read(output / 'ctm.validation.json')['cases'] if c['status'] == 'fail'],
        'pythonUnitTests': 2, 'nfcOracleComparisons': 16294, 'allRetainedNonXTMReportsIdenticalToSlice21L': verified,
        'historicalReportFilesVerified': len(historical), 'protectedBaseFilesVerified': len(protected), 'pinnedCorpusFilesVerified': len(lock['files']),
        'historicalReportsUnchanged': True, 'originalSourcesAndBaselinesUnchanged': True, 'productionChangeLimitedToXTMReader': True, 'protectedSubsystemsUnchanged': ['TMDM', 'CTM', 'CXTM', 'XML'],
        'newDependencyDownloads': 0, 'persistentLispImagesTouched': False,
        'executionAuthorization': 'Regular require_escalated approval; tests additionally deny network and repository writes; no symlink/configuration changes.',
        'fullOfflineNixRebuild': 'NOT-RUN; fresh SBCL loads with verified pinned local sources and existing XML patches.', 'acceptancePassed': True})
    print(json.dumps({'acceptancePassed': True, 'xtm': statuses, 'ctm': CTM, 'checks': len(labels), 'output': str(output)}))


if __name__ == '__main__':
    main()
