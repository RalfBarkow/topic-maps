#!/usr/bin/env python3
"""Validate seven intended original CTM rejections and every retained suite offline."""
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

ROOT = Path(__file__).resolve().parent.parent
BASE = '9044114749dedc72f190f4aa9ba0443dfe7860b5'
POLICY = '(version 1)(allow default)(deny network*)'
EXPECTED = {
    'occurrence-double-positive-infinity': ('expected-occurrence-value', 15, 2, 10, 'I'),
    'occurrence-double-negative-infinity': ('expected-occurrence-value', 15, 2, 10, '-'),
    'qname-hyphen': ('unexpected-token', 38, 3, 3, ':'),
    'string-unbalanced': ('unterminated-string', 8, 1, 9, '"'),
    'string-unicode': ('invalid-unicode-escape', 11, 1, 12, '"'),
    'string-unicode2': ('invalid-unicode-escape', 15, 1, 16, 'G'),
    'topic-id-illegal': ('unexpected-character', 0, 1, 1, '\u0361'),
}


def main():
    # Reuse the existing validation utilities and full 20A/19D2 chain.
    spec = importlib.util.spec_from_file_location('slice20a', ROOT / 'scripts/validate-slice-20a.py')
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    read, save, sha, command, snapshot = previous.read, previous.save, previous.sha, previous.command, previous.snapshot
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/slice-20b')
    args = parser.parse_args()
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    test_path = 'tests/ctm-registered-originals.lisp'
    tracked_tests = command(['git', 'ls-tree', '-r', '--name-only', BASE, '--', 'tests']).splitlines()
    protected_paths = ['src', 'vendor', 'references', 'patches', 'flake.nix', 'flake.lock',
                       'scripts/test.sh', 'scripts/prepare-cxml.py', 'scripts/validate-slice-19d2.py',
                       'scripts/validate-slice-20a.py', 'docs/slice-20a-registration.md'] + [
                           p for p in tracked_tests if p != test_path]
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    # Existing positive tests and execution order are retained verbatim; only
    # the exports of new entry points and appended negative suite are allowed.
    prior_test = subprocess.check_output(['git', 'show', BASE + ':' + test_path], cwd=ROOT, text=True)
    prior_test = prior_test.replace('(:export #:run-tests #:write-reports #:candidate-groups))',
        '(:export #:run-tests #:write-reports #:candidate-groups\n           #:run-negative-tests #:write-negative-reports))', 1)
    assert (ROOT / test_path).read_text().startswith(prior_test)
    for name in ['topic-maps.asd', 'scripts/fresh-sbcl.lisp']:
        prior = subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT, text=True)
        assert (ROOT / name).read_text().startswith(prior)
    protected = snapshot(p for directory in ['src', 'vendor', 'references', 'patches']
                         for p in (ROOT / directory).rglob('*'))
    historical = snapshot(p for p in (ROOT / 'reports').rglob('*') if output not in p.parents)
    sources = snapshot(p for directory in ['src', 'tests', 'scripts', 'docs']
                       for p in (ROOT / directory).rglob('*')
                       if p.suffix in ['.lisp', '.py', '.sh', '.md'])
    sources.update(snapshot(ROOT / p for p in ['topic-maps.asd', 'flake.nix', 'flake.lock', 'README.md']))
    prefix = output / 'current'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TOPIC_MAPS_REGISTERED_NEGATIVES_REPORT=str(prefix))
    invocation = ['python3', 'scripts/validate-slice-20a.py', '--sbcl', runtime,
                  '--output', str(output / 'retained-20a')]
    result = subprocess.run(invocation, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=600)
    (output / 'retained-driver.log').write_bytes(result.stdout)
    assert result.returncode == 0, 'Retained regression failed; see retained-driver.log and retained-20a/retained/*.log'
    retained = read(output / 'retained-20a/execution.json')
    before = read(output / 'retained-20a/current.validation.json')
    assert before == read(ROOT / 'reports/slice-20a/current.validation.json')
    for suffix in ['cxtm', 'registration']:
        assert read(output / f'retained-20a/current.{suffix}.json') == read(ROOT / f'reports/slice-20a/current.{suffix}.json')
    final = read(Path(str(prefix) + '.validation.json'))
    cxtm = read(Path(str(prefix) + '.cxtm.json'))
    negative = read(Path(str(prefix) + '.negative.json'))
    assert negative['entryStatuses'] == before['statuses'] == {
        'pass': 245, 'fail': 4, 'unsupported': 0, 'not-run': 24}
    ids = ['ctm/invalid/' + name + '.ctm' for name in EXPECTED]
    assert [c['id'] for c in negative['cases']] == ids
    assert negative['failed'] == 0
    assert negative['passed'] == len(negative['checks']) == len(set(negative['checks']))
    log = (output / 'retained-20a/retained/regression.log').read_text()
    marker = re.search(r'(?m)^REGISTERED-NEGATIVES-PASS: (\d+) checks; (\d+) intended original rejections registered; (\d+) remain NOT-RUN', log)
    assert marker and int(marker.group(1)) == negative['passed']
    observed = re.findall(r'^REGISTERED-NEGATIVE (ctm/invalid/[^:]+): (PASS|NOT-RUN);', log, re.M)
    assert [i for i, _ in observed] == ids
    assert len(final['cases']) == len(before['cases']) == 273
    assert [c['id'] for c in final['cases']] == [c['id'] for c in before['cases']]
    assert {k: v for k, v in final.items() if k not in ['cases', 'statuses', 'implementationScope']} == {
        k: v for k, v in before.items() if k not in ['cases', 'statuses', 'implementationScope']}
    old_cxtm = read(output / 'retained-20a/current.cxtm.json')
    assert cxtm['cases'] == old_cxtm['cases']
    assert cxtm['contractCounts'] == old_cxtm['contractCounts'] == {'pass': 217, 'fail': 4}
    rows = {c['id']: c for c in negative['cases']}
    candidates, changes = [], []
    for a, b in zip(before['cases'], final['cases']):
        if a['id'] not in rows:
            assert a == b, a['id']
            continue
        row = rows[a['id']]
        name = Path(a['id']).stem
        code, position, line, column, character = EXPECTED[name]
        source = ROOT / 'vendor/cxtm' / a['sourcePathname']
        text = source.read_bytes().decode('utf-8')
        assert a['status'] == 'not-run' and a['actualOutcome'] is None
        assert a['category'] == 'invalid' and a['expectedOutcome'] == 'ctm-rejection' and a['expectedCXTM'] is None
        assert row['sourcePathname'] == a['sourcePathname'] and row['documentIRI'] == a['documentIRI']
        assert a['documentIRI'] == 'https://ctm-tests.example.invalid/' + before['commit'] + '/' + a['id']
        condition = row['condition']
        qualified = row['normativeValidated']
        if qualified:
            assert condition == row['repeatCondition']
            assert condition['condition'] == 'CTM-REJECTION'
            assert (condition['code'], condition['position'], condition['line'], condition['column']) == (code, position, line, column)
            assert condition['source'] == a['id'] and condition['positionUnit'] == 'character'
            assert condition['cause'] is condition['context'] is None
            assert text[position] == character
            # Independent character-index/line/column calculation from original bytes.
            assert text[:position].count('\n') + 1 == line
            assert len(text[:position].rsplit('\n', 1)[-1]) + 1 == column
            assert row['sourceWitness'] and row['lexicalWitness'] and row['reproducibleCondition']
            assert row['control']['inMemoryOnly'] and row['control']['accepted'] and row['control']['condition'] is None
            assert row['notRegisteredReason'] is None and row['clauses']
            control = row['control']['source']
            model = row['control']['model']
            assert control != text and model['associationCount'] == 0
            if name.startswith('occurrence-double-'):
                value = '-1' if 'negative' in name else '1'
                assert control == text.replace('-INF' if 'negative' in name else 'INF', value)
                occurrences = [o for t in model['topics'] for o in t['occurrences']]
                assert model['topicCount'] == 2 and len(occurrences) == 1
                assert occurrences[0]['value'] == value and occurrences[0]['datatype'] == 'http://www.w3.org/2001/XMLSchema#integer'
                assert occurrences[0]['parent'] == 1 and occurrences[0]['type'] == 2
            elif name == 'qname-hyphen':
                assert control == text.replace('ex:-issue', 'ex:issue')
                assert [(t['kind'], t['value'], t['position']) for t in row['tokens'][3:6]] == [
                    ('identifier', 'ex', 36), ('punctuation', ':', 38), ('punctuation', '-', 39)]
                assert model['topicCount'] == 1 and model['topics'][0]['subjectIdentifiers'] == ['http://psi.example.org/issue']
            elif name == 'topic-id-illegal':
                assert control == 'a\u0361' + text[2:]
                assert model['topicCount'] == 1 and model['topics'][0]['itemIdentifiers'] == [a['documentIRI'] + '#a\u0361']
            else:
                expected_control = {
                    'string-unbalanced': text[:-1] + '".',
                    'string-unicode': text.replace('\\U0041', '\\u0041'),
                    'string-unicode2': text.replace('\\U00GG00', '\\U000041'),
                }[name]
                assert control == expected_control
                names = [n for t in model['topics'] for n in t['names']]
                assert model['topicCount'] == 2 and len(names) == 1
                assert names[0]['value'] == ('Foo"' if name == 'string-unbalanced' else 'A')
                assert names[0]['parent'] == 1 and names[0]['type'] == 2
                assert row['lexicalCondition'] == condition
            if name == 'string-unicode2':
                assert 'Printed production [43]' in row['qualification']
            assert b == dict(a, status='pass', actualOutcome='ctm-rejection', diagnostics=[condition['message']])
            changes.append({'id': a['id'], 'before': a['status'], 'after': b['status']})
        else:
            assert b == a and row['status'] == 'not-run' and row['actualOutcome'] is None
            assert row['notRegisteredReason']
        candidates.append({'id': a['id'], 'status': b['status'], 'sourceSHA256': sha(source),
                           'documentIRI': a['documentIRI'], 'normativeReason': row['normativeReason'],
                           'clauses': row['clauses'], 'condition': condition,
                           'normativeValidated': qualified, 'qualification': row['qualification']})
    qualified = len(changes)
    assert int(marker.group(2)) == qualified and int(marker.group(3)) == 7 - qualified
    assert final['statuses'] == {'pass': 245 + qualified, 'fail': 4, 'unsupported': 0, 'not-run': 24 - qualified}
    xtm = read(output / 'retained-20a/retained/xtm.json')
    assert xtm == read(ROOT / 'reports/slice-20a/retained/xtm.json')
    assert xtm['statuses'] == {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 0}
    assert xtm['otherCorpusInputs'] == {'positiveUnexecuted': 107, 'negativeUnregisteredUnexecuted': 11}
    save(output / 'candidates.json', candidates)
    save(output / 'remaining.json', [c for c in final['cases'] if c['status'] == 'not-run'])
    (output / 'contracts.md').write_text(
        '# Slice 20B: actual original rejections\n\n'
        'Positions count Unicode characters from zero; lines and columns start at one.\n\n'
        '| Original CTM | Status | Condition | Code | Position | Line:column |\n'
        '| --- | --- | --- | --- | ---: | --- |\n' +
        ''.join(f"| `{Path(c['id']).name}` | {c['status'].upper()} | `{c['condition']['condition']}` | "
                f"`{c['condition']['code']}` | {c['condition']['position']} | "
                f"{c['condition']['line']}:{c['condition']['column']} |\n" for c in candidates) +
        '\nReviewed causes, the QName diagnostic trace and the Unicode printed-class qualification '
        'are documented in `../../docs/slice-20b-negative-registration.md`. Full actual conditions, '
        'repeated calls and accepted in-memory control models are in `current.negative.json`.\n')
    assert protected == {p: sha(ROOT / p) for p in protected}
    assert historical == {p: sha(ROOT / p) for p in historical}
    assert sources == {p: sha(ROOT / p) for p in sources}
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    save(output / 'integrity.json', {'protectedFilesSHA256': protected, 'historicalReportsSHA256': historical})
    evidence = {
        'baseCommit': BASE, 'branch': command(['git', 'branch', '--show-current']),
        'startedAtUTC': started, 'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'runtime': 'SBCL 2.5.4', 'sourceSHA256': sources, 'newDependencyDownloads': 0,
        'retainedValidationCommand': invocation, 'retainedExecutionEvidence': 'retained-20a/execution.json',
        'retainedLispChecks': retained['retainedLispChecks'], 'xmlQualificationChecks': retained['xmlQualificationChecks'],
        'standaloneXTMChecks': retained['standaloneXTMChecks'], 'xtmMergemapChecks': retained['xtmMergemapChecks'],
        'slice20aChecks': retained['registeredOriginalChecks'], 'slice20aActualByteExactContracts': 40,
        'registeredNegativeChecks': negative['passed'], 'newIntendedOriginalRejections': qualified,
        'pythonUnitTests': retained['pythonUnitTests'], 'nfcOracleComparisons': retained['nfcOracleComparisons'],
        'network': retained['network'], 'ctmStatusesBefore': before['statuses'], 'ctmStatusesAfter': final['statuses'],
        'ctmStatusChanges': changes, 'xtmCorpusStatuses': retained['xtmCorpusStatuses'],
        'knownFailuresUnchanged': [c['id'] for c in final['cases'] if c['status'] == 'fail'],
        'oldOriginalCXTMComparisonsUnchanged': len(old_cxtm['cases']),
        'allHistoricalReportBytesUnchanged': True, 'allProtectedFileBytesUnchanged': True,
        'positiveRegistrationImplementationRetained': True,
        'normativeReview': {'source': 'https://www.isotopicmaps.org/ctm/ctm.html',
                            'consultedDate': '2026-10-19', 'description': 'docs/slice-20b-negative-registration.md',
                            'qualification': 'Printed [43] permits more letters than hexadecimal decoding prose; string-unicode2 is justified by the latter.'},
        'persistentLispImagesTouched': False, 'fullOfflineNixRebuild': retained['fullOfflineNixRebuild'],
        'acceptancePassed': qualified == 7,
    }
    save(output / 'execution.json', evidence)
    print(json.dumps({k: evidence[k] for k in ['runtime', 'retainedLispChecks', 'xmlQualificationChecks',
        'standaloneXTMChecks', 'xtmMergemapChecks', 'slice20aChecks', 'registeredNegativeChecks',
        'newIntendedOriginalRejections', 'ctmStatusesAfter', 'xtmCorpusStatuses', 'acceptancePassed']}, indent=2))
    assert evidence['acceptancePassed'], 'Some intended causes remain unproved; those records stay NOT-RUN. See current.negative.json.'


if __name__ == '__main__':
    main()
