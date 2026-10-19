#!/usr/bin/env python3
"""Validate XTM Variant ResourceRef originals through the existing ASDF/Case Record harness.

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
EVIDENCE = ROOT / 'reports/slice-21i'
PRIOR = ROOT / 'reports/slice-21h'
BASE = '034d2c14fbf6a58a062351e4b64680283d241d22'
POLICY = '(version 1)(allow default)(deny network*)(deny file-write* (subpath "' + str(ROOT) + '"))'
ALLOWED = {'src/xtm/reader.lisp', 'tests/xtm-identity.lisp', 'tests/xtm-variants.lisp', 'tests/xtm-negative-originals.lisp',
           'tests/ctm-xtm-mergemap.lisp', 'tests/xtm-names.lisp', 'tests/xtm-name-scopes.lisp', 'tests/xtm-name-item-identities.lisp', 'topic-maps.asd'}
CTM = {'pass': 262, 'fail': 4, 'unsupported': 0, 'not-run': 7}
TARGETS = ['xtm2/in/variant-resourceref.xtm', 'xtm2/in/variant-resourceref-relative.xtm']


def read(p):
    return json.loads(p.read_text())


def save(p, v):
    p.write_text(json.dumps(v, indent=2, ensure_ascii=False) + '\n')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def command(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def prepare_pinned(target):
    spec = importlib.util.spec_from_file_location('slice21g', ROOT / 'scripts/validate-slice-21h.py')
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
    output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='topic-maps-21i-'))
    assert not output.is_relative_to(ROOT)
    output.mkdir(parents=True, exist_ok=True)
    assert not (output / 'execution.json').exists(), 'Choose an unused output directory.'
    tracked = command(['git', 'ls-tree', '-r', '--name-only', BASE]).splitlines()
    assert set(command(['git', 'diff', '--name-only', BASE]).splitlines()) & set(tracked) <= ALLOWED
    protected = {p: sha(ROOT / p) for p in tracked if p not in ALLOWED}
    historical = {p: h for p, h in protected.items() if p.startswith('reports/')}
    sources = {p: sha(ROOT / p) for p in [*sorted(ALLOWED), 'tests/xtm-variant-resourcerefs.lisp', 'scripts/validate-slice-21i.py',
        *['reports/slice-21i/' + p for p in ['candidate-inventory.json', 'failure-controls.lisp', 'diagnostics.lisp',
                                          'before-diagnostics.json', 'baseline-xtm.json']]]}
    previous = read(PRIOR / 'xtm.json')
    assert read(EVIDENCE / 'baseline-xtm.json') == previous
    assert previous['statuses'] == {'pass': 57, 'fail': 0, 'unsupported': 0, 'not-run': 0}
    assert previous['otherCorpusInputs'] == {'positiveUnexecuted': 64, 'negativeUnregisteredUnexecuted': 3}
    assert read(PRIOR / 'ctm.validation.json')['statuses'] == CTM
    candidate = read(EVIDENCE / 'candidate-inventory.json')
    assert [c['id'] for c in candidate['candidates']] == TARGETS
    assert [c['sourceBytes'] for c in candidate['candidates']] == [324, 311]
    assert [c['baselineBytes'] for c in candidate['candidates']] == [621, 608]
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
    with tempfile.TemporaryDirectory(prefix='topic-maps-21i-sources-') as temp_name:
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
        rename = {}
        for label in previous['checks']:
            if label.startswith('variant-syntax:resourceRef:'):
                rename[label] = label.replace('resourceRef', 'resourceData-anyURI')
            elif 'variant-resourceRef' in label:
                rename[label] = label.replace('variant-resourceRef', 'variant-resourceData-datatype')
        assert len(rename) == 12
        retained_labels = [rename.get(label, label) for label in previous['checks']]
        assert set(retained_labels) <= set(labels)
        assert [label for label in labels if label in set(retained_labels)] == retained_labels
        assert f'XTM-SUMMARY {len(labels)} PASS 0 FAIL; 51 original CXTM PASS; 8 negative originals PASS' in xtm_log
        assert xtm['statuses'] == {'pass': 59, 'fail': 0, 'unsupported': 0, 'not-run': 0}
        assert xtm['otherCorpusInputs'] == {'positiveUnexecuted': 62, 'negativeUnregisteredUnexecuted': 3}
        assert xtm['cases'][:57] == previous['cases']
        control_retargets = {
            'negativeControls': ('unsupported-is-not-pass', 'unsupported-is-not-pass'),
            'nameControls': ('unsupported-variant-resourceRef', 'unsupported-variant-resourceData-datatype'),
            'scopeControls': ('scope:variant-resourceRef-stays-unsupported', 'scope:variant-resourceData-datatype-stays-unsupported'),
            'nameItemIdentityControls': ('iid:variant-resourceRef-stays-unsupported', 'iid:variant-resourceData-datatype-stays-unsupported'),
            'variantControls': ('resourceRef', 'resourceData-anyURI')}
        for field, value in previous.items():
            if field in control_retargets:
                assert len(xtm[field]) == len(value)
                changed = [(old, new) for old, new in zip(value, xtm[field]) if old != new]
                assert len(changed) == 1, field
                old, new = changed[0]
                assert (old['label'], new['label']) == control_retargets[field]
                assert new['condition']['class'] == 'XTM-UNSUPPORTED'
                assert new['condition']['code'] == 'resource-data-datatype'
            elif field not in ['scope', 'statuses', 'otherCorpusInputs', 'checks', 'cases']:
                assert xtm[field] == value, field
        assert len(xtm['cases']) == len({c['id'] for c in xtm['cases']}) == 59
        assert [c['id'] for c in xtm['cases'][57:]] == TARGETS
        assert all(c['status'] == 'pass' and c['actualOutcome'] == 'cxtm-match' for c in xtm['cases'][57:])
        assert len(xtm['variantResourceRefOriginals']) == 2
        regression = run('regression', [str(ROOT / 'scripts/test.sh')], env)
        run('diagnostics', prefix + [str(EVIDENCE / 'diagnostics.lisp')],
            dict(env, TOPIC_MAPS_21I_ROOT=str(ROOT), TOPIC_MAPS_21I_DIAGNOSTICS=str(output / 'after-diagnostics.json')))
        fault_controls = []
        positive_modes = [('mismatch', 'cxtm-mismatch'), ('xml', 'execution-error'), ('unsupported', 'unsupported'), ('tmdm', 'execution-error')]
        negative_modes = [('accepted', 'ctm-acceptance'), ('xml', 'execution-error'), ('unsupported', 'unsupported'), ('wrong-cause', 'execution-error')]
        families = {'positive': positive_modes + [('xtm', 'execution-error')], 'negative': negative_modes,
                    'name': positive_modes, 'scope': positive_modes, 'iid': positive_modes, 'variant': positive_modes,
                    'variant-negative': negative_modes + [('tmdm', 'execution-error')],
                    'merge-variant': positive_modes + [('xtm', 'execution-error')],
                    'resource-ref': positive_modes + [('xtm', 'execution-error')],
                    'resource-ref-relative': positive_modes + [('xtm', 'execution-error')]}
        for family, modes in families.items():
            for mode, outcome in modes:
                label = family + '-control-' + mode
                run(label, prefix + [str(EVIDENCE / 'failure-controls.lisp')],
                    dict(env, TOPIC_MAPS_XTM_REPORT=str(output / (label + '.json')), TOPIC_MAPS_21I_FAMILY=family, TOPIC_MAPS_21I_FAULT=mode), expected_exit=1)
                result = read(output / (label + '.json'))
                retained_count = {'positive': 0, 'negative': 26, 'name': 33, 'scope': 43, 'iid': 48, 'variant': 50, 'variant-negative': 55, 'merge-variant': 56, 'resource-ref': 57, 'resource-ref-relative': 58}[family]
                assert result['statuses']['pass'] == retained_count
                assert len(result['cases']) == retained_count + 1 and result['cases'][-1]['actualOutcome'] == outcome
                assert result['cases'][:retained_count] == xtm['cases'][:retained_count]
                fault_controls.append({'family': family, 'mode': mode, 'actualOutcome': outcome,
                    'expectedASDFFailureObserved': True, 'retainedOriginalPasses': retained_count, 'faultCountedAsPass': False})

    def retarget_mergemap(value):
        if isinstance(value, dict):
            changed = {k: retarget_mergemap(v) for k, v in value.items()}
            if value.get('label') == 'unsupported-name-variant-resourceRef':
                assert value['code'] == 'UNSUPPORTED-CONSTRUCT'
                changed['code'] = 'RESOURCE-DATA-DATATYPE'
            return changed
        if isinstance(value, list):
            return [retarget_mergemap(v) for v in value]
        if isinstance(value, str) and (value == 'unsupported-name-variant-resourceRef' or value.startswith('unsupported-name-variant-resourceRef:')):
            return value.replace('unsupported-name-variant-resourceRef', 'unsupported-name-variant-resourceData-datatype', 1)
        return value

    verified, retargeted_reports = [], []
    for old in sorted((PRIOR / 'retained').glob('*.json')):
        prior_value, actual_value = read(old), read(retained / old.name)
        expected_value = retarget_mergemap(prior_value) if old.name.startswith('xtm-mergemap.') else prior_value
        assert expected_value == actual_value, str(old)
        if prior_value != actual_value:
            retargeted_reports.append(str(old.relative_to(ROOT)))
        verified.append(str(old.relative_to(ROOT)))
    assert len(retargeted_reports) == 2
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
    for candidate_case, result in zip(candidate['candidates'], xtm['variantResourceRefOriginals']):
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
        assert result['model']['canonicalVariantReferences']
        assert len(result['model']['variants']) == 1
        variant = result['model']['variants'][0]
        assert variant['value'] == result['absoluteValue'] and variant['datatype'] == 'http://www.w3.org/2001/XMLSchema#anyURI'
        assert result['absoluteValue'].startswith(('http:', 'https:'))
        (output / 'actual' / baseline.name).write_bytes(actual)
        comparisons.append(dict(result, sourceSHA256=sha(source), baselineSHA256=sha(baseline),
            actualSHA256=hashlib.sha256(actual).hexdigest(), executedInASDFTestOp=True))
    before, after = read(EVIDENCE / 'before-diagnostics.json'), read(output / 'after-diagnostics.json')
    assert len(before) == len(after) == 124
    assert [c['id'] for c in before] == [c['id'] for c in after]
    changes = [{'id': a['id'], 'before': b, 'after': a,
                'reason': 'Variant resourceRef now resolves the resource locator and creates an anyURI Variant through add-variant.'}
               for b, a in zip(before, after) if b != a]
    assert {c['id'] for c in changes} == set(TARGETS)
    for change in changes:
        assert change['before']['condition']['class'] == 'XTM-UNSUPPORTED'
        assert change['before']['condition']['code'] == 'unsupported-construct'
        assert change['after']['condition'] is None and change['after']['byteExact']
        comparison = next(c for c in comparisons if c['id'] == change['id'])
        assert change['after']['actualCXTM'] == comparison['actualCXTM']
    excluded = next(c for c in after if c['id'] == 'xtm2/in/variant-resourcedata-uri.xtm')
    assert excluded['condition']['class'] == 'XTM-UNSUPPORTED' and excluded['condition']['code'] == 'resource-data-datatype'
    save(output / 'diagnostic-changes.json', changes)
    lock = read(ROOT / 'references/corpus-lock.json')
    for entry in lock['files']:
        p = ROOT / 'vendor/cxtm' / entry['path']
        assert p.stat().st_size == entry['size'] and sha(p) == entry['sha256']
    for snapshot in [protected, historical, sources]:
        assert snapshot == {p: sha(ROOT / p) for p in snapshot}
    assert set(command(['git', 'diff', '--name-only', BASE]).splitlines()) & set(tracked) <= ALLOWED
    save(output / 'variant-resource-ref-originals.json', {'kind': 'executed-original-variant-resource-ref-registration', 'cases': comparisons})
    save(output / 'diagnostics.json', {'kind': 'read-only-observations-no-extra-registration',
        'originalObservations': 124, 'unchangedOriginalObservations': 124 - len(changes),
        'diagnosticChanges': changes, 'registeredCases': TARGETS,
        'outOfScopeResourceDataURIStillUnsupported': True})
    save(output / 'failure-controls.json', {'kind': 'executor-fault-controls-not-corpus-results', 'controls': fault_controls})
    save(output / 'integrity.json', {'protectedBaseFilesSHA256': protected, 'historicalReportsSHA256': historical, 'executionSourcesSHA256': sources})
    statuses = dict(xtm['statuses'], **{'not-run': sum(xtm['otherCorpusInputs'].values())})
    save(output / 'execution.json', {'kind': 'xtm-variant-resource-ref-original-registration-validation', 'baseCommit': BASE,
        'branch': command(['git', 'branch', '--show-current']), 'runtime': 'SBCL 2.5.4', 'startedAtUTC': started,
        'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'runs': runs,
        'sourcePreparation': 'source-preparation.json', 'retainedLispChecks': 12100, 'retainedChecks': totals,
        'stageChecks': stages, 'xmlQualificationChecks': 146, 'standaloneXTMChecks': len(labels),
        'retainedXTMChecks': len(previous['checks']), 'retargetedUnsupportedCheckNames': rename,
        'newXTMChecks': len(labels) - len(previous['checks']), 'retargetedUnsupportedControlRows': control_retargets,
        'retainedOriginals': 57, 'retainedOriginalResultsUnchanged': True, 'newPositiveOriginals': 2,
        'originalByteComparisons': [{'id': c['id'], 'actual': c['actualBytes'], 'baseline': c['expectedBytes'], 'firstDifferentByte': None} for c in comparisons], 'faultControls': len(fault_controls),
        'diagnosticOriginalObservations': 124, 'diagnosticChangedOriginals': [c['id'] for c in changes],
        'xtmStatusesBefore': {'pass': 57, 'fail': 0, 'unsupported': 0, 'not-run': 67}, 'xtmStatusesAfter': statuses,
        'xtmStatusChanges': [{'id': id, 'before': 'not-run', 'after': 'pass', 'actualOutcome': 'cxtm-match'} for id in TARGETS],
        'ctmStatusesBefore': CTM, 'ctmStatusesAfter': CTM, 'ctmStatusChanges': [],
        'knownFailuresUnchanged': [c['id'] for c in read(output / 'ctm.validation.json')['cases'] if c['status'] == 'fail'],
        'pythonUnitTests': 2, 'nfcOracleComparisons': 16294, 'allRetainedNonXTMReportsVerifiedAgainstSlice21H': verified,
        'retargetedMergemapUnsupportedReports': retargeted_reports, 'unchangedNonXTMReports': len(verified) - len(retargeted_reports),
        'historicalReportFilesVerified': len(historical), 'protectedBaseFilesVerified': len(protected), 'pinnedCorpusFilesVerified': len(lock['files']),
        'historicalReportsUnchanged': True, 'originalSourcesAndBaselinesUnchanged': True, 'productionChangeLimitedToXTMReader': True, 'protectedSubsystemsUnchanged': ['TMDM', 'CTM', 'CXTM', 'XML'],
        'newDependencyDownloads': 0, 'persistentLispImagesTouched': False,
        'executionAuthorization': 'Regular require_escalated approval; tests additionally deny network and repository writes; no symlink/configuration changes.',
        'fullOfflineNixRebuild': 'NOT-RUN; fresh SBCL loads with verified pinned local sources and existing XML patches.', 'acceptancePassed': True})
    print(json.dumps({'acceptancePassed': True, 'xtm': statuses, 'ctm': CTM, 'checks': len(labels), 'output': str(output)}))


if __name__ == '__main__':
    main()
