#!/usr/bin/env python3
"""Register forty original CTM contracts after the complete retained offline suite."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
BASE = '9c196ddc16cf5cd727fcde81ad7835edefa0f787'
POLICY = '(version 1)(allow default)(deny network*)'
GROUPS = {
    'comments': ['comment-ml', 'comment-ml-nested', 'comment-ml-nested2', 'comment-sl',
                 'comment-sl2', 'comment-sl3', 'comment-sl4', 'comment-sl5', 'comment-sl6', 'empty'],
    'identity': ['association-qname-iid', 'item-identifier-INF', 'item-identifier-relative',
                 'qname-date', 'qname-digits', 'rootless-uri', 'subject-identifier-dot',
                 'subject-identifier-non-http', 'subject-identifier-relative', 'subject-locator-dot',
                 'subject-locator-relative', 'topic-identifier-INF', 'topic-identifier-unicode'],
    'occurrences': ['occurrence-decimal-dot-neg2', 'occurrence-decimal-dot-pos',
                    'occurrence-decimal-leading-zeros2', 'occurrence-duplicate-string',
                    'occurrence-duplicate-uri', 'occurrence-qname-value', 'occurrence-string-multiline',
                    'occurrence-string-multiline2', 'occurrence-uri-semicolon'],
    'prefixes': ['prefix-multiline2', 'prefix-multiline3', 'prefix-multiline4', 'prefix-with-qm'],
    'escapes': ['string-escape', 'string-escape2', 'unicode-escape-u4', 'unicode-escape-u6'],
}
BEGUN = {
    'topic-maps.asd': '9013f4ace885dc049e98f674e8f59378d108b391b2aeac73fb54ee45119f8842',
    'tests/ctm-registered-originals.lisp': '13eb134dde1620114e838f7595d1b1a0cfbd06624b1a0d23f5971441648e42e4',
}


def read(path):
    return json.loads(path.read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def command(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def snapshot(paths):
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/slice-20a')
    args = parser.parse_args()
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    tracked_tests = command(['git', 'ls-tree', '-r', '--name-only', BASE, '--', 'tests']).splitlines()
    protected_paths = ['src', 'vendor', 'references', 'patches', 'flake.nix', 'flake.lock',
                       'scripts/test.sh', 'scripts/prepare-cxml.py', 'scripts/validate-slice-19d2.py'] + tracked_tests
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    protected = snapshot(p for directory in ['src', 'vendor', 'references', 'patches']
                         for p in (ROOT / directory).rglob('*'))
    historical = snapshot(p for p in (ROOT / 'reports').rglob('*') if output not in p.parents)
    sources = snapshot(p for directory in ['src', 'tests', 'scripts', 'docs']
                       for p in (ROOT / directory).rglob('*')
                       if p.suffix in ['.lisp', '.py', '.sh', '.md'])
    sources.update(snapshot(ROOT / p for p in ['topic-maps.asd', 'flake.nix', 'flake.lock', 'README.md']))
    prefix = output / 'current'
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                       TOPIC_MAPS_REGISTERED_ORIGINALS_REPORT=str(prefix))
    # Reuse the unchanged qualification/regression driver, including its byte
    # checks against historical reports. Its integration snapshot precedes 20A.
    invocation = ['python3', 'scripts/validate-slice-19d2.py', '--sbcl', runtime,
                  '--output', str(output / 'retained')]
    result = subprocess.run(invocation, cwd=ROOT, env=environment, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=600)
    (output / 'retained-driver.log').write_bytes(result.stdout)
    assert result.returncode == 0, 'Retained regression failed; see retained-driver.log and retained/*.log'
    retained = read(output / 'retained/execution.json')
    old = read(ROOT / 'reports/slice-19d2/validation.json')
    before = read(output / 'retained/validation.json')
    old_cxtm = read(ROOT / 'reports/slice-19d2/cxtm.json')
    before_cxtm = read(output / 'retained/cxtm.json')
    assert before == old
    assert before_cxtm == old_cxtm
    assert read(output / 'retained/integration.json') == read(ROOT / 'reports/slice-19d2/integration.json')
    final = read(Path(str(prefix) + '.validation.json'))
    cxtm = read(Path(str(prefix) + '.cxtm.json'))
    registration = read(Path(str(prefix) + '.registration.json'))
    ids = ['ctm/in/' + name + '.ctm' for names in GROUPS.values() for name in names]
    assert len(ids) == len(set(ids)) == 40
    assert registration['entryStatuses'] == before['statuses'] == {
        'pass': 205, 'fail': 4, 'unsupported': 0, 'not-run': 64}
    assert final['statuses'] == {'pass': 245, 'fail': 4, 'unsupported': 0, 'not-run': 24}
    assert len(before['cases']) == len(final['cases']) == 273
    assert [c['id'] for c in before['cases']] == [c['id'] for c in final['cases']]
    changes = []
    for a, b in zip(before['cases'], final['cases']):
        if a['id'] in ids:
            assert a['status'] == 'not-run' and a['actualOutcome'] is None
            expected = dict(a, status='pass', actualOutcome='cxtm-match', diagnostics=[])
            assert b == expected, a['id']
            changes.append({'id': a['id'], 'before': a['status'], 'after': b['status']})
        else:
            assert a == b, a['id']
    assert {c['id'] for c in changes} == set(ids)
    assert {k: v for k, v in before.items() if k not in ['cases', 'statuses', 'implementationScope']} == {
        k: v for k, v in final.items() if k not in ['cases', 'statuses', 'implementationScope']}
    assert cxtm['cases'][:len(before_cxtm['cases'])] == before_cxtm['cases']
    assert cxtm['contractCounts'] == {'pass': 217, 'fail': 4}
    added = cxtm['cases'][len(before_cxtm['cases']):]
    assert [c['id'] for c in added] == ids == [c['id'] for c in registration['cases']]
    assert registration['failed'] == 0
    assert registration['passed'] == len(registration['checks']) == len(set(registration['checks']))
    log = (output / 'retained/regression.log').read_text()
    assert int(re.search(r'(?m)^REGISTERED-ORIGINALS-PASS: (\d+)', log).group(1)) == registration['passed']
    candidates = []
    (output / 'actual').mkdir()
    for case, row in zip(added, registration['cases']):
        name = Path(case['id']).stem
        group = next(group for group, names in GROUPS.items() if name in names)
        source = ROOT / 'vendor/cxtm' / case['id']
        baseline = ROOT / 'vendor/cxtm/ctm/baseline' / (name + '.ctm.cxtm')
        expected = baseline.read_bytes()
        actual = case['actualCXTM'].encode('utf-8')
        assert case['status'] == row['status'] == 'pass'
        assert row['group'] == group and row['actualOutcome'] == 'cxtm-match' and row['diagnostics'] == []
        assert row['sourcePathname'] == case['id'] and row['documentIRI'] == case['baseLocator']
        assert row['baseline'] == str(baseline.relative_to(ROOT / 'vendor/cxtm'))
        assert actual == expected == case['expectedCXTM'].encode('utf-8'), case['id']
        assert case['byteCount'] == row['comparison']['actualBytes'] == row['comparison']['expectedBytes'] == len(expected)
        assert row['comparison']['firstDifferentByte'] is None and row['sourceBytes'] == len(source.read_bytes())
        (output / 'actual' / (name + '.ctm.cxtm')).write_bytes(actual)
        candidates.append({'id': case['id'], 'group': group, 'status': 'pass',
                           'documentIRI': case['baseLocator'], 'bytes': len(actual),
                           'sourceSHA256': sha(source), 'baselineSHA256': sha(baseline),
                           'actualSHA256': digest(actual), 'byteExact': True})
    save(output / 'candidates.json', candidates)
    (output / 'contracts.md').write_text(
        '# Slice 20A: actual original comparisons\n\n'
        '| Original CTM | Group | Status | CXTM bytes |\n| --- | --- | --- | ---: |\n' +
        ''.join(f"| `{Path(c['id']).name}` | {c['group']} | PASS | {c['bytes']} |\n" for c in candidates) +
        '\nAll forty actual outputs equal the unchanged pinned baselines byte for byte. '
        'Individual source, baseline and actual SHA-256 digests are in `candidates.json`.\n')
    xtm = read(output / 'retained/xtm.json')
    assert xtm == read(ROOT / 'reports/slice-19d2/xtm.json')
    assert xtm['statuses'] == {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 0}
    assert xtm['otherCorpusInputs'] == {'positiveUnexecuted': 107, 'negativeUnregisteredUnexecuted': 11}
    remaining = [c for c in final['cases'] if c['status'] == 'not-run']
    assert len(remaining) == 24
    assert sum(c['category'] == 'valid' for c in remaining) == 10
    save(output / 'remaining.json', remaining)
    forms = (ROOT / 'docs/slice-20a-registration.md').read_text().split('```lisp\n')[-1].split('\n```', 1)[0]
    inspection_env = dict(environment, CL_SOURCE_REGISTRY=retained['qualifiedSourceProvenance']['sourceRegistry'])
    inspection_command = ['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform',
                          '--no-sysinit', '--no-userinit', '--script', '/dev/stdin']
    inspection = subprocess.run(inspection_command, cwd=ROOT, env=inspection_env, input=forms.encode(),
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    (output / 'inspection.log').write_bytes(inspection.stdout)
    assert inspection.returncode == 0, 'Documented inspection failed; see inspection.log'
    assert protected == {p: sha(ROOT / p) for p in protected}
    assert historical == {p: sha(ROOT / p) for p in historical}
    assert sources == {p: sha(ROOT / p) for p in sources}
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    save(output / 'integrity.json', {'protectedFilesSHA256': protected, 'historicalReportsSHA256': historical})
    evidence = {
        'baseCommit': BASE, 'branch': command(['git', 'branch', '--show-current']),
        'startedAtUTC': started, 'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'resumedUncommittedFileSHA256': BEGUN, 'sourceSHA256': sources,
        'runtime': 'SBCL 2.5.4', 'newDependencyDownloads': 0,
        'retainedValidationCommand': invocation, 'retainedExecutionEvidence': 'retained/execution.json',
        'retainedLispChecks': retained['retainedLispChecks'],
        'xmlQualificationChecks': next(r['passedChecks'] for r in retained['runs'] if r['label'] == 'xml'),
        'standaloneXTMChecks': next(r['passedChecks'] for r in retained['runs'] if r['label'] == 'xtm'),
        'xtmMergemapChecks': retained['newXTMIntegrationChecks'],
        'registeredOriginalChecks': registration['passed'], 'newActualByteExactContracts': len(candidates),
        'pythonUnitTests': 2, 'nfcOracleComparisons': 16294,
        'network': 'All Lisp qualification, regression and inspection processes deny network* with sandbox-exec; Nix preparation uses --offline and verified existing Store sources.',
        'ctmStatusesBefore': before['statuses'], 'ctmStatusesAfter': final['statuses'],
        'ctmStatusChanges': changes,
        'xtmCorpusStatuses': {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 118},
        'remainingCases': 'remaining.json; ten positive and fourteen negative cases not selected or executed by Slice 20A',
        'knownFailuresUnchanged': [c['id'] for c in final['cases'] if c['status'] == 'fail'],
        'oldOriginalComparisonsUnchanged': len(before_cxtm['cases']),
        'allHistoricalReportBytesUnchanged': True, 'allProtectedFileBytesUnchanged': True,
        'documentedInspectionPassed': True, 'persistentLispImagesTouched': False,
        'fullOfflineNixRebuild': 'NOT-RUN; reused verified local Store sources, unchanged patches and fresh SBCL loads.',
    }
    save(output / 'execution.json', evidence)
    print(json.dumps({k: evidence[k] for k in ['runtime', 'retainedLispChecks', 'xmlQualificationChecks',
        'standaloneXTMChecks', 'xtmMergemapChecks', 'registeredOriginalChecks', 'newActualByteExactContracts',
        'ctmStatusesAfter', 'xtmCorpusStatuses']}, indent=2))


if __name__ == '__main__':
    main()
