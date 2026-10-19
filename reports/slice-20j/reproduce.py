#!/usr/bin/env python3
"""Reproduce documentary observations and the unchanged offline regression."""
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
import tempfile

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent
BASE = 'bc04a1657f0b548ec5cdf2862aeed6a1ad0630b8'
POLICY = '(version 1)(allow default)(deny network*)'
READ_ONLY = POLICY + '(deny file-write* (subpath "' + str(ROOT) + '"))'


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args, **kwargs):
    return subprocess.check_output(args, cwd=ROOT, text=True, **kwargs).strip()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare_pinned(target):
    # Reuse the existing verifier/patcher with the already recorded Store
    # manifest. No Nix evaluation or daemon/network connection is needed.
    prior = read(ROOT / 'reports/slice-20h/source-preparation.json')
    module = load_module('prepare_cxml', ROOT / 'scripts/prepare-cxml.py')
    environment = {'manifest': prior['sources'],
                   'localPatches': [{'package': p['package'], 'sha256': p['sha256']} for p in prior['patches']]}
    return module.prepare(environment, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path, default=EVIDENCE)
    parser.add_argument('--prepare', type=Path)
    args = parser.parse_args()
    if args.prepare:
        print(json.dumps(prepare_pinned(args.prepare)))
        return
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT, check=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    assert not (output / 'execution.json').exists(), 'Choose an unused output directory'
    tracked = command(['git', 'ls-tree', '-r', '--name-only', BASE]).splitlines()
    assert not command(['git', 'diff', BASE, '--'] + tracked)
    protected = {p: sha(ROOT / p) for p in tracked}
    historical = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'reports').rglob('*')
                  if p.is_file() and output not in p.parents}
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in [*EVIDENCE.glob('*.py'), *EVIDENCE.glob('*.lisp'),
              EVIDENCE / 'import.json', ROOT / 'docs/slice-20j-template-tail-grammar.md', *sorted((EVIDENCE / 'slice20i').glob('*'))]}
    imported = read(EVIDENCE / 'import.json')
    assert imported['baseCommit'] == BASE
    for name, record in imported['files'].items():
        path = EVIDENCE / 'slice20i' / name
        assert path.stat().st_size == record['bytes'] and sha(path) == record['sha256']
    old = read(EVIDENCE / 'slice20i/investigation.json')
    old_controls = read(EVIDENCE / 'slice20i/controls.json')
    detailed = read(EVIDENCE / 'slice20i/detailed-inventory.json')
    assert read(EVIDENCE / 'slice20i/before-sha256.json') == protected
    assert old['harnessCaseStatesUnchanged'] and len(old['cases']) == len(detailed['cases']) == 7
    retained = output / 'retained'
    retained.mkdir()
    runs = []
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def run(label, invocation, env, policy=POLICY):
        invocation = ['/usr/bin/sandbox-exec', '-p', policy] + invocation
        entry = {'label': label, 'command': invocation, 'network': 'denied',
                 'freshProcess': True, 'startedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        result = subprocess.run(invocation, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=300)
        (output / (label + '.log')).write_bytes(result.stdout)
        entry.update(exitCode=result.returncode, finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
        runs.append(entry)
        assert result.returncode == 0, f'{label}: see {label}.log'
        return result.stdout.decode()

    with tempfile.TemporaryDirectory(prefix='topic-maps-20j-') as temp_name:
        temp = Path(temp_name)
        env = {k: v for k, v in os.environ.items() if not k.startswith('TOPIC_MAPS_')}
        env.update(PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0', SBCL=runtime)
        provenance = json.loads(run('source-preparation',
            ['python3', str(Path(__file__)), '--prepare', str(temp / 'sources')], env, READ_ONLY))
        save(output / 'source-preparation.json', provenance)
        env.update(CL_SOURCE_REGISTRY=provenance['sourceRegistry'],
                   TOPIC_MAPS_REPORT=str(retained / 'core.json'), TOPIC_MAPS_XTM_REPORT=str(retained / 'xtm.json'),
                   TOPIC_MAPS_XTM_MERGEMAP_REPORT=str(retained / 'xtm-mergemap'),
                   TOPIC_MAPS_REGISTERED_ORIGINALS_REPORT=str(retained / 'slice20a'),
                   TOPIC_MAPS_REGISTERED_NEGATIVES_REPORT=str(retained / 'slice20b'),
                   TOPIC_MAPS_PROLOG_REPORT=str(retained / 'slice20c'), TOPIC_MAPS_EMPTY2_REPORT=str(retained / 'slice20e'),
                   TOPIC_MAPS_CTM_INTEGER_REPORT=str(retained / 'slice20f'), TOPIC_MAPS_TRIPLE_REPORT=str(retained / 'slice20g'),
                   TOPIC_MAPS_ENCODING_REPORT=str(output / 'current'))
        for label, script, marker, count in [('xml', 'tests/cxml-probe.lisp', 'CXML', 146),
                                              ('xtm', 'scripts/fresh-xtm.lisp', 'XTM', 327)]:
            log = run(label, [runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script', script], env)
            labels = re.findall(r'^' + marker + r'-CHECK-PASS (.+)$', log, re.M)
            assert len(labels) == len(set(labels)) == count
            assert f'{marker}-SUMMARY {count} PASS 0 FAIL' in log
        log = run('regression', [str(ROOT / 'scripts/test.sh')], env)
        obs_env = {k: v for k, v in env.items() if not k.startswith('TOPIC_MAPS_')}
        obs_env.update(TOPIC_MAPS_XTM_MERGEMAP_REPORT=str(temp / 'probe-xtm'),
                       TOPIC_MAPS_20J_ROOT=str(ROOT), TOPIC_MAPS_20J_OUTPUT=str(temp))
        driver = temp / 'observe.lisp'
        driver.write_text('(load ' + json.dumps(str(EVIDENCE / 'observations.lisp')) + ')\n'
                          '(load ' + json.dumps(str(EVIDENCE / 'controls.lisp')) + ')\n')
        run('observations', [runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script', str(driver)], obs_env, READ_ONLY)
        current = read(temp / 'investigation.json')
        controls = read(temp / 'controls.json')
        assert current == old, 'Original observations differ from verified Slice 20I'
        assert controls == old_controls, 'Explorative controls differ from verified Slice 20I'
        save(output / 'observed-originals.json', current)
        save(output / 'observed-controls.json', controls)

    verified_reports = []
    for prior in sorted((ROOT / 'reports/slice-20h/retained').glob('*.json')):
        assert read(prior) == read(retained / prior.name), str(prior)
        verified_reports.append(str(prior.relative_to(ROOT)))
    for suffix in ['validation', 'cxtm', 'encoding']:
        prior = ROOT / f'reports/slice-20h/current.{suffix}.json'
        assert read(prior) == read(output / f'current.{suffix}.json'), str(prior)
        verified_reports.append(str(prior.relative_to(ROOT)))
    final = read(output / 'current.validation.json')
    expected_statuses = {'pass': 262, 'fail': 4, 'unsupported': 0, 'not-run': 7}
    assert final['statuses'] == current['harnessStatuses'] == expected_statuses
    pending = [c for c in final['cases'] if c['status'] == 'not-run']
    assert [c['id'] for c in pending] == [c['id'] for c in current['cases']]
    cases = []
    for original, detail in zip(current['cases'], detailed['cases']):
        assert original['id'] == detail['id']
        path = ROOT / 'vendor/cxtm' / original['id']
        raw = path.read_bytes()
        assert raw == bytes.fromhex(original['sourceHex']) == original['sourceText'].encode('ascii')
        assert len(raw) == original['sourceBytes'] and sha(path) == detail['sourceSHA256']
        matches = list(re.finditer(r'\$[A-Za-z_][A-Za-z0-9_]*', original['sourceText']))
        assert len(matches) == len(detail['variables'])
        variables = []
        for match, variable in zip(matches, detail['variables']):
            pos = match.start()
            assert match.group() == variable['variable'] and pos == variable['position']
            assert variable['line'] == raw[:pos].count(b'\n') + 1
            assert variable['column'] == pos - raw.rfind(b'\n', 0, pos)
            variables.append(dict(variable, roleOrigin='observed' if variable['role'] == 'Parameterdeklaration' else 'inferred'))
        condition = original['condition']
        assert condition['condition'] == 'INVALID-TEMPLATE-BODY' and condition['code'] == 'template-identity-tail'
        assert condition['positionUnit'] == 'character' and condition['cause'] is None and condition['context'] is None
        assert original['model'] is None and original['actualCXTM'] is None
        case = dict(detail, status='not-run', variables=variables, observation=original,
                    originalComparisonPerformed=False, argumentCheckReached=False,
                    evidenceOrigins={'sourceAndCondition': 'observed', 'intendedRoles': 'inferred',
                                     'grammar': 'norm-derived', 'compatibilityRule': 'hypothesized'},
                    compatibilityRule='H-SI-tail', normativeReferences=['N-tail', 'N-variables', 'N-templates'])
        if original['baselineText']:
            baseline = Path(original['baselinePath'])
            assert baseline.read_bytes() == original['baselineText'].encode('utf-8') and sha(baseline) == detail['baselineSHA256']
            control = detail['expandedControl']
            assert control in controls and control['byteExact'] and control['condition'] is None
            actual = control['actualCXTM'].encode('utf-8')
            assert actual == baseline.read_bytes() and len(actual) == control['actualBytes'] == control['expectedBytes']
            case['expandedComparison'] = {'epistemicOrigin': 'observed', 'originalTemplateExecutedSuccessfully': False,
                'actualBytes': len(actual), 'expectedBytes': len(actual), 'actualSHA256': hashlib.sha256(actual).hexdigest(),
                'expectedSHA256': sha(baseline), 'firstDifferentByte': None}
        else:
            second = '2nd-arg' in original['id']
            case['intendedArgumentCheck'] = {'epistemicOrigin': 'inferred', 'argumentIndex': 2 if second else 1,
                'parameter': '$iri2' if second else '$iri', 'identityKind': 'item-identifier' if 'item-identifier' in original['id'] else 'subject-locator',
                'targetContext': 'unmarked Subject Identifier Tail slot',
                'basis': 'invalid corpus category, source argument marker and, for two arguments, original invalid comment'}
        cases.append(case)
    report = {'kind': 'ctm-template-tail-investigation', 'baseCommit': BASE, 'runtime': 'SBCL 2.5.4',
        'corpusCommit': final['commit'], 'statuses': expected_statuses, 'caseStatusChanges': [],
        'originalComparisonsPerformed': 0, 'expandedControlComparisons': 3,
        'normativeReference': detailed['normativeReference'],
        'normativeFindings': [
            {'id': 'N-tail', 'epistemicOrigin': 'norm-derived', 'sections': {'3.9': [50, 51, 52], '3.3.6': [17], '3.3.5': [12]},
             'derivation': '[50] -> [51] -> [52] -> [17] -> [12]', 'result': 'No variable alternative in this unmarked Tail slot.'},
            {'id': 'N-variables', 'epistemicOrigin': 'norm-derived', 'sections': {'3.3.6': [13, 18, 19], '3.3.7': [20], '3.4.1': [28]},
             'result': 'Explicit variable uses in Topic identity/reference, marked SL/II and literal contexts.'},
            {'id': 'N-templates', 'epistemicOrigin': 'norm-derived', 'sections': {'3.14': [63, 64, 65, 66, 67], '3.15': [68, 69, 70]},
             'result': 'Template-only variables, positional binding and use-context constraints.'}],
        'compatibilityHypothesis': {'id': 'H-SI-tail', 'epistemicOrigin': 'hypothesized', 'implemented': False,
            'scope': 'Only the Subject Identifier branch of [52] inside a Template Tail.',
            'additionalRule': 'template-tail-subject-identifier ::= iri-ref | variable',
            'bindingRequirement': 'Variable must denote an IRI reference (IRI or resolved QName), added as an SI of the owner.',
            'rejectedBindings': ['marked item identifier', 'marked subject locator', 'Topic-only argument', 'non-IRI literal'],
            'identityKindsMustBePreserved': True, 'textualMarkerStrippingAllowed': False,
            'doesNotChange': ['Topic-head variables', 'Type/Player Topic references', 'literal substitution'],
            'historicalIntentEstablished': False},
        'historicalQualification': detailed['historicalQualification'], 'cases': cases}
    save(output / 'current.investigation.json', report)
    totals = read(ROOT / 'reports/slice-19d1/regression-execution.json')['regressionChecks']
    assert sum(totals.values()) == 12100
    for marker, count in totals.items():
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) == count
    stage_counts = {'XTM-MERGEMAP': 217, 'REGISTERED-ORIGINALS': 286, 'REGISTERED-NEGATIVES': 25,
                    'PROLOG': 171, 'EMPTY2': 13, 'CTM-INTEGER': 112, 'TRIPLE': 226, 'ENCODING': 722}
    for marker, count in stage_counts.items():
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) == count
    assert 'Ran 2 tests' in log and 'NFC-ORACLE-PASS: 16294' in log
    xtm = read(retained / 'xtm.json')
    assert xtm['statuses'] == {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 0}
    assert xtm['otherCorpusInputs'] == {'positiveUnexecuted': 107, 'negativeUnregisteredUnexecuted': 11}
    lock = read(ROOT / 'references/corpus-lock.json')
    for entry in lock['files']:
        p = ROOT / 'vendor/cxtm' / entry['path']
        assert p.stat().st_size == entry['size'] and sha(p) == entry['sha256']
    for snapshot in [protected, historical, inputs]:
        assert snapshot == {p: sha(ROOT / p) for p in snapshot}
    assert not command(['git', 'diff', BASE, '--'] + tracked)
    save(output / 'integrity.json', {'baseTrackedFilesSHA256': protected, 'historicalReportsSHA256': historical,
                                    'documentaryInputsSHA256': inputs})
    save(output / 'execution.json', {'kind': 'ctm-template-tail-documentation-validation', 'baseCommit': BASE,
        'branch': command(['git', 'branch', '--show-current']), 'startedAtUTC': started,
        'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'runtime': 'SBCL 2.5.4',
        'runs': runs, 'sourcePreparation': provenance, 'retainedLispChecks': 12100, 'retainedChecks': totals,
        'stageChecks': stage_counts, 'xmlQualificationChecks': 146, 'standaloneXTMChecks': 327,
        'pythonUnitTests': 2, 'nfcOracleComparisons': 16294, 'originalObservationsReproduced': 7,
        'explorativeControlsReproduced': len(controls), 'expandedBaselineComparisons': 3,
        'ctmStatusesBefore': expected_statuses, 'ctmStatusesAfter': final['statuses'], 'ctmStatusChanges': [],
        'xtmCorpusStatuses': {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 118},
        'allRetainedReportsEqualToSlice20H': verified_reports, 'allBaseTrackedFileBytesUnchanged': True,
        'baseTrackedFilesVerified': len(protected), 'historicalReportsVerified': len(historical),
        'pinnedCorpusFilesVerified': len(lock['files']), 'newDependencyDownloads': 0,
        'languageOrRegistrationChanges': False, 'persistentLispImagesTouched': False,
        'fullOfflineNixRebuild': 'NOT-RUN; verified local pinned Store sources and unchanged XML patches.',
        'executionAuthorization': 'Regular require_escalated approval; no symlink or sandbox configuration changes.',
        'acceptancePassed': True})
    print(json.dumps({'acceptancePassed': True, 'ctm': final['statuses'], 'xtm': {'pass': 6, 'fail': 0, 'not-run': 118},
                      'originalObservations': 7, 'expandedComparisons': 3, 'protectedBaseFiles': len(protected)}))


if __name__ == '__main__':
    main()
