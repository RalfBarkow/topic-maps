#!/usr/bin/env python3
"""Validate four Triple String originals and the complete retained offline suite."""
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
BASE = '1ef5768ce6913f0c04da111d5f525b6d50a27e0b'
POLICY = '(version 1)(allow default)(deny network*)'
CONTRACTS = {
    'occurrence-string-triple': (41, 367, 'Occurrence " Value'),
    'occurrence-string-triple2': (48, 370, 'Occurrence"" " Value"'),
    'unicode-escape-u4-triple-string': (33, 331, 'ZZ \nTop'),
    'unicode-escape-u6-triple-string': (37, 331, 'ZZ \nTop'),
}


def main():
    spec = importlib.util.spec_from_file_location('slice20a', ROOT / 'scripts/validate-slice-20a.py')
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    read, save, sha, command, snapshot = common.read, common.save, common.sha, common.command, common.snapshot
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/slice-20g')
    parser.add_argument('--preimplementation', type=Path, default=ROOT / 'reports/slice-20g/preimplementation.json')
    args = parser.parse_args()
    pre = read(args.preimplementation)
    assert pre['baseCommit'] == BASE and len(pre['cases']) == 12 and len(pre['originals']) == 4
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT, check=True)
    mutable = {'src/ctm/lexer.lisp', 'tests/ctm-identity.lisp', 'tests/ctm-templates.lisp',
               'tests/ctm-prolog.lisp', 'tests/ctm-integer-literal.lisp',
               'tests/ctm-registered-originals.lisp', 'topic-maps.asd', 'scripts/fresh-sbcl.lisp'}
    tracked = command(['git', 'ls-tree', '-r', '--name-only', BASE]).splitlines()
    protected_paths = [p for p in tracked if p not in mutable]
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    retained = output / 'retained'
    retained.mkdir()
    save(output / 'preimplementation.json', pre)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    protected = snapshot(ROOT / p for p in protected_paths)
    historical = snapshot(p for p in (ROOT / 'reports').rglob('*') if output not in p.parents)
    sources = snapshot(p for directory in ['src', 'tests', 'scripts', 'docs']
                       for p in (ROOT / directory).rglob('*') if p.suffix in ['.lisp', '.py', '.sh', '.md'])
    sources.update(snapshot(ROOT / p for p in ['topic-maps.asd', 'flake.nix', 'flake.lock', 'README.md']))
    runs = []
    with tempfile.TemporaryDirectory(prefix='topic-maps-20g-') as temp_name:
        preparation = ['python3', 'scripts/prepare-cxml.py', '--directory', str(Path(temp_name) / 'sources')]
        provenance = json.loads(command(preparation))  # Existing pinned local sources, nix --offline.
        save(output / 'source-preparation.json', provenance)
        env = dict(os.environ, SBCL=runtime, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1',
                   CL_SOURCE_REGISTRY=provenance['sourceRegistry'],
                   TOPIC_MAPS_REPORT=str(retained / 'core.json'),
                   TOPIC_MAPS_XTM_REPORT=str(retained / 'xtm.json'),
                   TOPIC_MAPS_XTM_MERGEMAP_REPORT=str(retained / 'xtm-mergemap'),
                   TOPIC_MAPS_REGISTERED_ORIGINALS_REPORT=str(retained / 'slice20a'),
                   TOPIC_MAPS_REGISTERED_NEGATIVES_REPORT=str(retained / 'slice20b'),
                   TOPIC_MAPS_PROLOG_REPORT=str(retained / 'slice20c'),
                   TOPIC_MAPS_EMPTY2_REPORT=str(retained / 'slice20e'),
                   TOPIC_MAPS_CTM_INTEGER_REPORT=str(retained / 'slice20f'),
                   TOPIC_MAPS_TRIPLE_REPORT=str(output / 'current'))
        for label, invocation in [
            ('xml', [runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script', 'tests/cxml-probe.lisp']),
            ('xtm', [runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script', 'scripts/fresh-xtm.lisp']),
            ('regression', [str(ROOT / 'scripts/test.sh')]),
        ]:
            invocation = ['/usr/bin/sandbox-exec', '-p', POLICY] + invocation
            run = {'label': label, 'command': invocation, 'freshProcess': True, 'network': 'denied by sandbox-exec',
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
    # Permit only named obsolete Unsupported assertions in regenerated reports.
    # Archived report bytes are independently hashed and remain unchanged.
    labels = {
        'diagnostic:unchanged-excluded-feature:def f() a - """N""". end': 'diagnostic:triple-string-body-supported',
        'known-triple-string-unsupported:specific-condition-code-position-source': 'known-string-unclosed:specific-condition-code-position-source',
        'known-triple-string-unsupported:position-units': 'known-string-unclosed:position-units',
        'negative:triple-still-unsupported:class-code-exact-position': 'negative:triple-unclosed:class-code-exact-position',
    }
    old_prolog = read(ROOT / 'reports/slice-20f/retained/slice20c.prolog.json')
    old_prolog_row = next(r for r in old_prolog['negativeControls'] if r['label'] == 'known-triple-string-unsupported')
    old_integer = read(ROOT / 'reports/slice-20f/current.literal.json')
    old_integer_row = next(r for r in old_integer['negativeControls'] if r['label'] == 'triple-still-unsupported')
    def updated_condition(prior, source):
        return dict(prior, condition='CTM-REJECTION', code='unterminated-string', source=source,
                    message=f'UNTERMINATED-STRING in {source} at CHARACTER {prior["position"]} (line {prior["line"]}, column {prior["column"]}): Unterminated triple-quoted string.')
    def qualified_retained(value):
        if isinstance(value, dict):
            if value.get('label') == 'known-triple-string-unsupported':
                assert value == old_prolog_row
                return dict(value, label='known-string-unclosed',
                            condition=updated_condition(value['condition'], 'known-string-unclosed'))
            if value.get('label') == 'triple-still-unsupported':
                assert value == old_integer_row
                return dict(value, label='triple-unclosed', sourceText='topic t: """x.',
                            condition=updated_condition(value['condition'], 'triple-unclosed'))
            return {k: qualified_retained(v) for k, v in value.items()}
        if isinstance(value, list):
            return [qualified_retained(v) for v in value]
        if isinstance(value, str):
            return labels.get(value, value)
        return value
    verified = []
    for old in sorted((ROOT / 'reports/slice-20f/retained').glob('*.json')):
        assert qualified_retained(read(old)) == read(retained / old.name), str(old)
        verified.append(str(old.relative_to(ROOT)))
    for suffix in ['validation', 'cxtm', 'literal']:
        old = ROOT / f'reports/slice-20f/current.{suffix}.json'
        assert qualified_retained(read(old)) == read(retained / f'slice20f.{suffix}.json'), str(old)
        verified.append(str(old.relative_to(ROOT)))
    before = read(retained / 'slice20f.validation.json')
    final = read(output / 'current.validation.json')
    triple = read(output / 'current.triple.json')
    cxtm = read(output / 'current.cxtm.json')
    assert before['statuses'] == triple['entryStatuses'] == {'pass': 257, 'fail': 4, 'unsupported': 0, 'not-run': 12}
    assert final['statuses'] == {'pass': 261, 'fail': 4, 'unsupported': 0, 'not-run': 8}
    assert triple['passed'] == len(triple['checks']) == len(set(triple['checks'])) and triple['failed'] == 0
    rows = {r['id']: r for r in triple['originals']}
    ids = ['ctm/in/' + n + '.ctm' for n in CONTRACTS]
    assert list(rows) == ids
    changes, comparisons = [], []
    positives = {p['label']: p for p in triple['positives']}
    assert len(positives) == len(triple['positives']) == 77
    assert all(p['initialCounter'] == p['finalCounter'] == 37 for p in positives.values())
    negatives = {r['label']: r for r in triple['negativeControls']}
    assert len(negatives) == len(triple['negativeControls']) == 31
    for prior in pre['cases']:
        current = negatives[prior['label']]
        assert prior['sourceText'] == current['sourceText']
        assert prior['result'] == {k: current['condition'][k] for k in prior['result']}, prior['label']
    assert len(before['cases']) == len(final['cases']) == 273
    for a, b in zip(before['cases'], final['cases']):
        assert a['id'] == b['id']
        if a['id'] not in rows:
            assert a == b, a['id']
            continue
        row = rows[a['id']]
        name = Path(a['id']).stem
        source_size, expected_size, expected_value = CONTRACTS[name]
        source = ROOT / 'vendor/cxtm' / a['id']
        baseline = ROOT / 'vendor/cxtm/ctm/baseline' / (name + '.ctm.cxtm')
        assert a['status'] == 'not-run' and a['actualOutcome'] is None and a['category'] == 'valid'
        assert a['documentIRI'] == row['documentIRI'] == 'https://ctm-tests.example.invalid/' + before['commit'] + '/' + a['id']
        assert b == dict(a, status='pass', actualOutcome='cxtm-match')
        assert row['status'] == 'pass' and row['actualOutcome'] == 'cxtm-match' and row['diagnostics'] == []
        assert source.stat().st_size == row['sourceBytes'] == source_size
        assert row['comparison']['actualBytes'] == row['comparison']['expectedBytes'] == expected_size
        assert row['comparison']['firstDifferentByte'] is None
        model = row['comparison']['model']
        assert model['topicCount'] == 2 and model['associationCount'] == 0
        constructs = [item for t in model['topics'] for item in t['occurrences' if name.startswith('occurrence-') else 'names']]
        assert len(constructs) == 1 and constructs[0]['value'] == expected_value
        if name.startswith('occurrence-'):
            assert constructs[0]['datatype'] == 'http://www.w3.org/2001/XMLSchema#string'
        actual_case = next(c for c in cxtm['cases'] if c['id'] == a['id'])
        actual = actual_case['actualCXTM'].encode('utf-8')
        assert actual == actual_case['expectedCXTM'].encode('utf-8') == baseline.read_bytes()
        control = positives[a['id'] + ':ordinary-control']['actualCXTM'].encode('utf-8')
        assert control == actual
        prior = next(r for r in pre['originals'] if r['original'] == a['id'])
        assert prior['documentIRI'] == row['documentIRI']
        assert prior['result']['condition'] == 'CTM-UNSUPPORTED' and prior['result']['code'] == 'triple-quoted-string'
        comparisons.append({'id': a['id'], 'documentIRI': row['documentIRI'], 'sourceBytes': source_size,
                            'sourceSHA256': sha(source), 'expectedBytes': expected_size, 'expectedSHA256': sha(baseline),
                            'actualBytes': len(actual), 'actualSHA256': common.digest(actual), 'firstDifferentByte': None,
                            'ordinaryControlBytes': len(control), 'ordinaryControlSHA256': common.digest(control),
                            'value': expected_value, 'datatype': 'http://www.w3.org/2001/XMLSchema#string',
                            'canonicalizationPreservesMap': True, 'executedInFullRegression': True})
        changes.append({'id': a['id'], 'before': a['status'], 'after': b['status']})
    assert len(changes) == 4
    assert {k: v for k, v in before.items() if k not in ['cases', 'statuses', 'implementationScope', 'infrastructureChecks']} == {
        k: v for k, v in final.items() if k not in ['cases', 'statuses', 'implementationScope', 'infrastructureChecks']}
    old_cxtm = read(retained / 'slice20f.cxtm.json')
    assert [c for c in cxtm['cases'] if c['id'] not in rows] == old_cxtm['cases']
    assert cxtm['contractCounts'] == {'pass': 223, 'fail': 4}
    for case in cxtm['cases']:
        baseline = ROOT / 'vendor/cxtm/ctm/baseline' / (Path(case['id']).name + '.cxtm')
        actual = case['actualCXTM'].encode('utf-8')
        assert (actual == baseline.read_bytes()) == (case['status'] == 'pass')
        assert case['expectedCXTM'].encode('utf-8') == baseline.read_bytes()
    log = (output / 'regression.log').read_text()
    prior_totals = read(ROOT / 'reports/slice-19d1/regression-execution.json')['regressionChecks']
    totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) for marker in prior_totals}
    assert totals == prior_totals and sum(totals.values()) == 12100
    for marker, count in [('XTM-MERGEMAP', 217), ('REGISTERED-ORIGINALS', 286), ('REGISTERED-NEGATIVES', 25),
                          ('PROLOG', 171), ('EMPTY2', 13), ('CTM-INTEGER', 112), ('TRIPLE', triple['passed'])]:
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) == count
    assert re.findall(r'^TRIPLE-ORIGINAL (ctm/in/[^:]+): PASS;', log, re.M) == ids
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
        'slice20aChecks': 286, 'slice20bChecks': 25, 'prologChecks': 171, 'empty2Checks': 13, 'ctmIntegerChecks': 112,
        'tripleChecks': triple['passed'], 'positiveControls': len(positives), 'negativeControls': len(negatives),
        'ordinaryStringDiagnosticSignaturesUnchanged': len(pre['cases']), 'originalComparisons': comparisons,
        'retainedReportLabelChanges': labels, 'updatedAssertions': [
            'Identity Triple String boundary now checks its actual Name value.',
            'Existing Template body String path checks Name N after invocation.',
            'Prolog and CTM-integer old valid-triple Unsupported probes now reject unclosed Triple Strings.'],
        'pythonUnitTests': 2, 'nfcOracleComparisons': 16294,
        'ctmStatusesBefore': before['statuses'], 'ctmStatusesAfter': final['statuses'], 'ctmStatusChanges': changes,
        'xtmCorpusStatuses': {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 118},
        'knownFailuresUnchanged': [c['id'] for c in final['cases'] if c['status'] == 'fail'],
        'retainedReportsVerified': verified, 'allHistoricalReportBytesUnchanged': True,
        'allProtectedFileBytesUnchanged': True, 'pinnedCorpusFilesVerified': len(lock['files']),
        'persistentLispImagesTouched': False,
        'fullOfflineNixRebuild': 'NOT-RUN; fresh offline SBCL loads from verified local Store sources and unchanged XML patches.',
        'executionAuthorization': 'Regular require_escalated approval; no symlink or sandbox configuration changes.',
        'acceptancePassed': True,
    }
    save(output / 'execution.json', evidence)
    print(json.dumps({k: evidence[k] for k in ['runtime', 'retainedLispChecks', 'xmlQualificationChecks',
        'standaloneXTMChecks', 'xtmMergemapChecks', 'tripleChecks', 'positiveControls', 'negativeControls',
        'ctmStatusesAfter', 'xtmCorpusStatuses', 'originalComparisons', 'pinnedCorpusFilesVerified', 'acceptancePassed']}, indent=2))


if __name__ == '__main__':
    main()
