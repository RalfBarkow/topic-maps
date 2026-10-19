#!/usr/bin/env python3
"""Validate ISO-8859-5 and the complete retained offline suite in fresh SBCL."""
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
BASE = '7f0e40d1558255773357c5ed4fa44bb5184d85e0'
POLICY = '(version 1)(allow default)(deny network*)'
ORIGINAL = 'ctm/in/encoding-8859-5.ctm'
ISO_NAMES = ['ISO-8859-5', 'ISO_8859-5:1988', 'ISO_8859-5', 'iso-ir-144',
             'cyrillic', 'csISOLatinCyrillic']


def main():
    spec = importlib.util.spec_from_file_location('slice20a', ROOT / 'scripts/validate-slice-20a.py')
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    read, save, sha, command, snapshot = common.read, common.save, common.sha, common.command, common.snapshot
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/slice-20h')
    parser.add_argument('--preimplementation', type=Path, default=ROOT / 'reports/slice-20h/preimplementation.json')
    parser.add_argument('--runtime-qualification', type=Path, default=ROOT / 'reports/slice-20h/runtime-qualification.json')
    args = parser.parse_args()
    pre, qualification = read(args.preimplementation), read(args.runtime_qualification)
    oracle = [ord(c) for c in bytes(range(256)).decode('iso8859_5')]
    assert pre['baseCommit'] == qualification['baseCommit'] == BASE
    assert pre['runtime'] == qualification['runtime'] == 'SBCL 2.5.4'
    assert pre['network'] == qualification['network'] == 'denied'
    assert pre['original']['id'] == ORIGINAL and pre['original']['code'] == 'unsupported-encoding'
    assert pre['original']['condition'] == 'CTM-UNSUPPORTED' and pre['original']['position'] == 11
    assert pre['original']['positionUnit'] == 'byte'
    assert qualification['all256DecodedWithoutReplacement'] and qualification['all256EncodeRoundTrip']
    assert qualification['pythonCodecOracleEqual'] and qualification['codepoints'] == oracle
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT, check=True)
    mutable = {'src/ctm/unicode.lisp', 'src/ctm/reader.lisp', 'tests/ctm-prolog.lisp',
               'tests/ctm-integer-literal.lisp', 'tests/ctm-registered-originals.lisp',
               'topic-maps.asd', 'scripts/fresh-sbcl.lisp'}
    tracked = command(['git', 'ls-tree', '-r', '--name-only', BASE]).splitlines()
    protected_paths = [p for p in tracked if p not in mutable]
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    old_unicode = subprocess.check_output(['git', 'show', BASE + ':src/ctm/unicode.lisp'], cwd=ROOT).decode()
    new_unicode = (ROOT / 'src/ctm/unicode.lisp').read_text()
    # Includes both strict UTF-8 and IRI unescaping, byte for byte.
    assert old_unicode[:old_unicode.index(';; Slice 20C:')] == new_unicode[:new_unicode.index(';; Inspect')]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    retained = output / 'retained'
    retained.mkdir()
    save(output / 'preimplementation.json', pre)
    save(output / 'runtime-qualification.json', qualification)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    protected = snapshot(ROOT / p for p in protected_paths)
    historical = snapshot(p for p in (ROOT / 'reports').rglob('*') if output not in p.parents)
    sources = snapshot(p for directory in ['src', 'tests', 'scripts', 'docs']
                       for p in (ROOT / directory).rglob('*') if p.suffix in ['.lisp', '.py', '.sh', '.md'])
    sources.update(snapshot(ROOT / p for p in ['topic-maps.asd', 'flake.nix', 'flake.lock', 'README.md']))
    runs = []
    with tempfile.TemporaryDirectory(prefix='topic-maps-20h-') as temp_name:
        preparation = ['python3', 'scripts/prepare-cxml.py', '--directory', str(Path(temp_name) / 'sources')]
        provenance = json.loads(command(preparation))  # Pinned local Store sources, nix --offline.
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
                   TOPIC_MAPS_TRIPLE_REPORT=str(retained / 'slice20g'),
                   TOPIC_MAPS_ENCODING_REPORT=str(output / 'current'))
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

    # Only the seven obsolete Unsupported fixtures and their check label may
    # change. Their complete prior rows are matched before this transformation.
    old_prolog = read(ROOT / 'reports/slice-20g/retained/slice20c.prolog.json')
    old_integer = read(ROOT / 'reports/slice-20g/retained/slice20f.literal.json')
    obsolete = {r['label']: r for r in old_prolog['negativeControls'] + old_integer['negativeControls']
                if r['condition']['code'] == 'unsupported-encoding'}
    assert len(obsolete) == 7
    def qualified_retained(value):
        if isinstance(value, dict):
            if value.get('label') in obsolete:
                assert value == obsolete[value['label']]
                current = dict(value)
                condition = dict(value['condition'])
                condition['message'] = condition['message'].replace(
                    'Only UTF-8 CTM input is implemented.',
                    'Only UTF-8 and ISO-8859-5 CTM input are implemented.').replace(
                    'Charset "iso-8859-5" is recognized but only UTF-8 decoding is implemented.',
                    'Charset "iso-8859-1" is not implemented; supported CTM encodings are UTF-8 and ISO-8859-5.')
                if value['label'] == 'iso88595-still-unsupported':
                    current.update(label='iso88591-still-unsupported',
                                   sourceText=value['sourceText'].replace('iso-8859-5', 'iso-8859-1'))
                    condition['source'] = current['label']
                    condition['message'] = condition['message'].replace(value['label'], current['label'])
                current['condition'] = condition
                return current
            return {k: qualified_retained(v) for k, v in value.items()}
        if isinstance(value, list):
            return [qualified_retained(v) for v in value]
        if value == 'negative:iso88595-still-unsupported:class-code-exact-position':
            return 'negative:iso88591-still-unsupported:class-code-exact-position'
        return value
    verified = []
    for old in sorted((ROOT / 'reports/slice-20g/retained').glob('*.json')):
        assert qualified_retained(read(old)) == read(retained / old.name), str(old)
        verified.append(str(old.relative_to(ROOT)))
    for suffix in ['validation', 'cxtm', 'triple']:
        old = ROOT / f'reports/slice-20g/current.{suffix}.json'
        assert qualified_retained(read(old)) == read(retained / f'slice20g.{suffix}.json'), str(old)
        verified.append(str(old.relative_to(ROOT)))
    before = read(retained / 'slice20g.validation.json')
    final, encoding, cxtm = [read(output / f'current.{name}.json') for name in ['validation', 'encoding', 'cxtm']]
    assert before['statuses'] == encoding['entryStatuses'] == {'pass': 261, 'fail': 4, 'unsupported': 0, 'not-run': 8}
    assert final['statuses'] == {'pass': 262, 'fail': 4, 'unsupported': 0, 'not-run': 7}
    assert encoding['passed'] == len(encoding['checks']) == len(set(encoding['checks'])) and encoding['failed'] == 0
    assert encoding['decoderCodepoints'] == oracle == qualification['codepoints']
    assert encoding['ISO88595Names'] == ISO_NAMES and encoding['UTF8Names'] == ['UTF-8', 'csUTF8']
    assert encoding['selectionEvidence'] == {'conflictAndUnsupportedUTF8Calls': 0, 'conflictAndUnsupportedISOCalls': 0}
    positives = {p['label']: p for p in encoding['positives']}
    negatives = {r['label']: r for r in encoding['negativeControls']}
    assert len(positives) == len(encoding['positives']) == 74
    assert len(negatives) == len(encoding['negativeControls']) == 33
    for charset in ['ISO-8859-5', 'csUTF8']:
        row = negatives['source-position:' + charset]
        condition = row['condition']
        assert condition['code'] == 'unexpected-character' and condition['positionUnit'] == 'character'
        assert condition['line'] == 3 and condition['column'] == 1
        assert (row['positionInOriginalBytes'] == condition['position']) == (charset == 'ISO-8859-5')
    for purpose in ['INCLUDE', 'MERGEMAP']:
        for generic in ['NIL', 'T']:
            row = positives[f'resource:{purpose}:generic={generic}']
            assert row['finalCounter'] == (20 if purpose == 'INCLUDE' else 18)
            assert 'C0 DE E1 E1 D8 EF' in row['inputHex']
    row = encoding['original']
    assert row['id'] == ORIGINAL and row['status'] == 'pass' and row['actualOutcome'] == 'cxtm-match'
    assert row['diagnostics'] == [] and row['sourceBytes'] == 42
    source = ROOT / 'vendor/cxtm' / ORIGINAL
    baseline = ROOT / 'vendor/cxtm/ctm/baseline/encoding-8859-5.ctm.cxtm'
    assert source.read_bytes() == b'%encoding "iso-8859-5"\nrussia - "\xc0\xde\xe1\xe1\xd8\xef" .'
    expected = baseline.read_bytes()  # Read the actual pinned byte count; never prescribe it.
    comparison = row['comparison']
    assert comparison['firstDifferentByte'] is None
    assert comparison['actualBytes'] == comparison['expectedBytes'] == len(expected)
    model = comparison['model']
    assert model['topicCount'] == 2 and model['associationCount'] == 0
    names = [n for topic in model['topics'] for n in topic['names']]
    assert len(names) == 1 and names[0]['value'] == 'Россия'
    assert len(before['cases']) == len(final['cases']) == 273
    changes = []
    for a, b in zip(before['cases'], final['cases']):
        assert a['id'] == b['id']
        if a['id'] != ORIGINAL:
            assert a == b, a['id']
            continue
        assert a['status'] == 'not-run' and a['actualOutcome'] is None and a['category'] == 'valid'
        assert a['documentIRI'] == row['documentIRI'] == pre['original']['documentIRI']
        assert a['documentIRI'] == 'https://ctm-tests.example.invalid/' + before['commit'] + '/' + ORIGINAL
        assert b == dict(a, status='pass', actualOutcome='cxtm-match')
        changes.append({'id': ORIGINAL, 'before': a['status'], 'after': b['status']})
    assert len(changes) == 1
    assert {k: v for k, v in before.items() if k not in ['cases', 'statuses', 'implementationScope', 'infrastructureChecks']} == {
        k: v for k, v in final.items() if k not in ['cases', 'statuses', 'implementationScope', 'infrastructureChecks']}
    old_cxtm = read(retained / 'slice20g.cxtm.json')
    assert [c for c in cxtm['cases'] if c['id'] != ORIGINAL] == old_cxtm['cases']
    assert cxtm['contractCounts'] == {'pass': 224, 'fail': 4}
    for case in cxtm['cases']:
        pinned = ROOT / 'vendor/cxtm/ctm/baseline' / (Path(case['id']).name + '.cxtm')
        actual = case['actualCXTM'].encode('utf-8')
        assert (actual == pinned.read_bytes()) == (case['status'] == 'pass')
        assert case['expectedCXTM'].encode('utf-8') == pinned.read_bytes()
    original_case = next(c for c in cxtm['cases'] if c['id'] == ORIGINAL)
    actual = original_case['actualCXTM'].encode('utf-8')
    assert actual == original_case['expectedCXTM'].encode('utf-8') == expected
    (output / 'actual').mkdir()
    (output / 'actual/encoding-8859-5.ctm.cxtm').write_bytes(actual)
    log = (output / 'regression.log').read_text()
    prior_totals = read(ROOT / 'reports/slice-19d1/regression-execution.json')['regressionChecks']
    totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) for marker in prior_totals}
    assert totals == prior_totals and sum(totals.values()) == 12100
    for marker, count in [('XTM-MERGEMAP', 217), ('REGISTERED-ORIGINALS', 286), ('REGISTERED-NEGATIVES', 25),
                          ('PROLOG', 171), ('EMPTY2', 13), ('CTM-INTEGER', 112), ('TRIPLE', 226),
                          ('ENCODING', encoding['passed'])]:
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) == count
    assert re.findall(r'^ENCODING-ORIGINAL (ctm/in/[^:]+): PASS;', log, re.M) == [ORIGINAL]
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
        'initialRepositoryState': {'head': BASE, 'branch': 'codex/ctm-slice-20g', 'indexClean': True, 'worktreeClean': True},
        'startedAtUTC': started, 'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'runtime': 'SBCL 2.5.4', 'sourceSHA256': sources, 'newDependencyDownloads': 0,
        'sourcePreparationCommand': preparation, 'qualifiedSourceProvenance': provenance, 'runs': runs,
        'retainedLispChecks': sum(totals.values()), 'retainedChecks': totals,
        'xmlQualificationChecks': 146, 'standaloneXTMChecks': 327, 'xtmMergemapChecks': 217,
        'slice20aChecks': 286, 'slice20bChecks': 25, 'prologChecks': 171, 'empty2Checks': 13,
        'ctmIntegerChecks': 112, 'tripleChecks': 226, 'encodingChecks': encoding['passed'],
        'positiveControls': len(positives), 'negativeControls': len(negatives),
        'all256ByteMappingsMatchIndependentOracle': True, 'runtimeQualificationBeforeImplementation': qualification,
        'supportedISO88595Names': ISO_NAMES, 'supportedUTF8Names': ['UTF-8', 'csUTF8'],
        'strictUTF8AndIRIUnescapingByteIdenticalToBase': True,
        'originalComparison': {'id': ORIGINAL, 'documentIRI': row['documentIRI'], 'sourceBytes': source.stat().st_size,
            'sourceSHA256': sha(source), 'expectedBytes': len(expected), 'expectedSHA256': sha(baseline),
            'actualBytes': len(actual), 'actualSHA256': common.digest(actual), 'firstDifferentByte': None,
            'originalNameBytesHex': 'C0 DE E1 E1 D8 EF', 'value': 'Россия',
            'canonicalizationPreservesMap': True, 'executedInFullRegression': True},
        'updatedUnsupportedAssertions': sorted(obsolete),
        'updatedAssertionReason': 'ISO-8859-5 is now supported; ISO-8859-1 remains unsupported. Only messages and one named fixture/check label change in regenerated reports.',
        'pythonUnitTests': 2, 'nfcOracleComparisons': 16294,
        'ctmStatusesBefore': before['statuses'], 'ctmStatusesAfter': final['statuses'], 'ctmStatusChanges': changes,
        'xtmCorpusStatuses': {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 118},
        'knownFailuresUnchanged': [c['id'] for c in final['cases'] if c['status'] == 'fail'],
        'retainedReportsVerified': verified, 'allHistoricalReportBytesUnchanged': True,
        'historicalReportFilesVerified': len(historical), 'allProtectedFileBytesUnchanged': True,
        'protectedFilesVerified': len(protected), 'pinnedCorpusFilesVerified': len(lock['files']),
        'persistentLispImagesTouched': False,
        'fullOfflineNixRebuild': 'NOT-RUN; fresh offline SBCL loads from verified local Store sources and unchanged XML patches.',
        'sandboxStartupError': 'writable root /Users/rgb/.nix-profile contains symlink component /Users/rgb/.nix-profile; symlinked writable roots are not supported.',
        'executionAuthorization': 'Regular require_escalated approval, canonical SBCL/Nix Store paths; no symlink or sandbox configuration changes. All regression subprocesses deny network.',
        'acceptancePassed': True,
    }
    save(output / 'execution.json', evidence)
    print(json.dumps({k: evidence[k] for k in ['runtime', 'retainedLispChecks', 'xmlQualificationChecks',
        'standaloneXTMChecks', 'xtmMergemapChecks', 'encodingChecks', 'positiveControls', 'negativeControls',
        'ctmStatusesAfter', 'xtmCorpusStatuses', 'originalComparison', 'pinnedCorpusFilesVerified', 'acceptancePassed']}, indent=2))


if __name__ == '__main__':
    main()
