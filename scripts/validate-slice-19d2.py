#!/usr/bin/env python3
"""Validate controlled XTM Mergemap and all retained suites, offline and fresh."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
BASE = 'f6a86668fce782a2e77d3bd763d58b0489079d75'
POLICY = '(version 1)(allow default)(deny network*)'


def command(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/slice-19d2')
    args = parser.parse_args()
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    protected_paths = ['src/tmdm', 'src/cxtm', 'src/xtm', 'src/xml', 'patches', 'flake.nix',
                       'flake.lock', 'vendor', 'references', 'scripts/prepare-cxml.py',
                       'tests/cxml-probe.lisp', 'tests/cxml-encoding-regressions.lisp', 'tests/xtm-identity.lisp', 'scripts/test.sh']
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    protected = {str(p.relative_to(ROOT)): sha(p) for directory in ['vendor/cxtm', 'references', 'patches']
                 for p in (ROOT / directory).rglob('*') if p.is_file()}
    sources = {str(p.relative_to(ROOT)): sha(p) for directory in ['src', 'tests', 'scripts', 'docs']
               for p in (ROOT / directory).rglob('*') if p.is_file() and p.suffix in ['.lisp', '.py', '.sh', '.md']}
    sources.update({p: sha(ROOT / p) for p in ['topic-maps.asd', 'README.md', 'flake.nix', 'flake.lock']})
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    xtm_source = '\n'.join(p.read_text() for p in sorted((ROOT / 'src/xtm').glob('*.lisp')))
    assert xtm_source.count('(topic-maps.xml:parse-octets ') == 1
    assert not re.search(r'\(cxml:parse[-\w]*\s', xtm_source, re.I)
    runs = []
    with tempfile.TemporaryDirectory(prefix='topic-maps-19d2-') as tmp:
        tmp = Path(tmp)
        preparation = ['python3', 'scripts/prepare-cxml.py', '--directory', str(tmp / 'sources')]
        provenance = json.loads(command(preparation))
        environment = dict(os.environ, CL_SOURCE_REGISTRY=provenance['sourceRegistry'], PYTHONDONTWRITEBYTECODE='1')
        base_report = tmp / 'core.json'
        final_prefix = tmp / 'xtm-mergemap'
        for label, invocation in [
            ('xml', [runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script', 'tests/cxml-probe.lisp']),
            ('xtm', [runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script', 'scripts/fresh-xtm.lisp']),
            ('regression', [str(ROOT / 'scripts/test.sh')])]:
            env = dict(environment, SBCL=runtime)
            if label == 'xtm':
                env['TOPIC_MAPS_XTM_REPORT'] = str(output / 'xtm.json')
            if label == 'regression':
                env['TOPIC_MAPS_REPORT'] = str(base_report)
                env['TOPIC_MAPS_XTM_MERGEMAP_REPORT'] = str(final_prefix)
            invocation = ['/usr/bin/sandbox-exec', '-p', POLICY] + invocation
            context = {'label': label, 'command': invocation, 'freshProcess': True,
                       'network': 'denied by sandbox-exec', 'startedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
            result = subprocess.run(invocation, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=240)
            (output / (label + '.log')).write_bytes(result.stdout)
            context.update(exitCode=result.returncode, finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
            assert result.returncode == 0, label + ' failed; see saved log'
            if label in ['xml', 'xtm']:
                prefix = 'CXML' if label == 'xml' else 'XTM'
                passed = re.findall(r'^' + prefix + r'-CHECK-PASS (.+)$', result.stdout.decode(), re.M)
                assert len(passed) == len(set(passed))
                assert prefix + '-SUMMARY ' + str(len(passed)) + ' PASS 0 FAIL' in result.stdout.decode()
                context['passedChecks'] = len(passed)
                assert len(passed) == (146 if label == 'xml' else 327)
            runs.append(context)
        base = read(base_report)
        baseline = ROOT / 'reports/slice-19c'
        assert base['statuses'] == {'pass': 204, 'fail': 4, 'unsupported': 0, 'not-run': 65}
        assert base == read(baseline / 'validation.json')
        retained = []
        for old in sorted(baseline.glob('*.json')):
            if old.name == 'execution.json':
                continue
            path = base_report if old.name == 'validation.json' else Path(str(base_report) + '.' + old.name)
            prior, current = read(old), read(path)
            if old.name in ['mergemap.json', 'cxtm.json']:
                renamed = {'diagnostic:known-XTM-unimplemented:specific-condition': 'diagnostic:XTM-explicit-resolver-required:specific-condition',
                           'diagnostic:known-XTM-unimplemented:source-position': 'diagnostic:XTM-explicit-resolver-required:source-position',
                           'policy:XTM-recognized-without-retrieval:specific-condition': 'policy:XTM-explicit-resolver-before-retrieval:specific-condition',
                           'policy:XTM-recognized-without-retrieval:source-position': 'policy:XTM-explicit-resolver-before-retrieval:source-position',
                           'policy:XTM-does-not-call-resolver': 'policy:XTM-without-resolver-does-not-fetch'}
                assert current['checks'] == [renamed.get(c, c) for c in prior['checks']]
                assert {k: v for k, v in prior.items() if k != 'checks'} == {k: v for k, v in current.items() if k != 'checks'}
            else:
                assert old.read_bytes() == path.read_bytes(), old.name
            retained.append(old.name)
        final = read(Path(str(final_prefix) + '.validation.json'))
        cxtm = read(Path(str(final_prefix) + '.cxtm.json'))
        integration = read(Path(str(final_prefix) + '.integration.json'))
        assert final['statuses'] == {'pass': 205, 'fail': 4, 'unsupported': 0, 'not-run': 64}
        changes = [(a['id'], a['status'], b['status']) for a, b in zip(base['cases'], final['cases']) if a != b]
        assert changes == [('ctm/in/mergemap-xtm.ctm', 'not-run', 'pass')]
        assert len(final['cases']) == len(base['cases']) == 273
        old_cxtm = read(Path(str(base_report) + '.cxtm.json'))
        assert cxtm['cases'][:-1] == old_cxtm['cases']
        assert cxtm['contractCounts'] == {'pass': 177, 'fail': 4}
        original = cxtm['cases'][-1]
        expected = (ROOT / 'vendor/cxtm/ctm/baseline/mergemap-xtm.ctm.cxtm').read_bytes()
        actual = original['actualCXTM'].encode()
        assert len(actual) == len(expected) == 1519
        assert actual == expected == original['expectedCXTM'].encode()
        (output / 'mergemap-xtm.actual.cxtm').write_bytes(actual)
        for name in ['validation', 'cxtm', 'integration']:
            shutil.copyfile(Path(str(final_prefix) + '.' + name + '.json'), output / (name + '.json'))
        assert integration['failed'] == 0 and integration['passed'] == len(integration['checks']) == len(set(integration['checks']))
        log = (output / 'regression.log').read_text()
        previous_totals = read(ROOT / 'reports/slice-19d1/regression-execution.json')['regressionChecks']
        totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) for marker in previous_totals}
        assert totals == previous_totals and sum(totals.values()) == 12100
        assert int(re.search(r'XTM-MERGEMAP-PASS: (\d+)', log).group(1)) == integration['passed']
        assert 'Ran 2 tests' in log and 'NFC-ORACLE-PASS: 16294' in log
        assert 'XTM-ADAPTER-BOUNDARY-PASS:' in log
        xtm = read(output / 'xtm.json')
        assert xtm == read(ROOT / 'reports/slice-19d1/xtm-1.json')
        assert xtm['statuses'] == {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 0}
        assert xtm['otherCorpusInputs'] == {'positiveUnexecuted': 107, 'negativeUnregisteredUnexecuted': 11}
        forms = (ROOT / 'docs/slice-19d2-xtm-mergemap.md').read_text().split('```lisp\n')[-1].split('\n```', 1)[0]
        invocation = ['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit', '--no-userinit', '--script', '/dev/stdin']
        inspection = subprocess.run(invocation, cwd=ROOT, env=environment, input=forms.encode(),
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        (output / 'inspection.log').write_bytes(inspection.stdout)
        assert inspection.returncode == 0, 'Documented inspection forms failed'
    assert protected == {p: sha(ROOT / p) for p in protected}
    assert sources == {p: sha(ROOT / p) for p in sources}
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    evidence = {'baseCommit': BASE, 'branch': command(['git', 'branch', '--show-current']),
                'startedAtUTC': started, 'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'runtime': 'SBCL 2.5.4', 'newDependencyDownloads': 0, 'sourcePreparationCommand': preparation,
                'qualifiedSourceProvenance': provenance, 'sourceSHA256': sources,
                'pinnedCorpusXMLPatchesAndTMDMUnchanged': True, 'runs': runs,
                'retainedLispChecks': sum(totals.values()), 'retainedChecks': totals,
                'newXTMIntegrationChecks': integration['passed'], 'retainedReportsVerified': retained,
                'retainedReportChange': 'Five obsolete XTM-unimplemented check labels now test missing explicit resolver, in mergemap.json and its checks embedded in cxtm.json; original cases/observations unchanged',
                'ctmStatuses': final['statuses'], 'ctmStatusChanges': changes,
                'xtmCorpusStatuses': {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 118},
                'xtmPositiveAndNegativeRegistration': 'Six original positives executed; 107 other positives and 11 negative inputs remain unexecuted.',
                'allFourKnownDiscrepanciesUnchanged': True, 'originalBaselineByteCount': 1519,
                'documentedInspectionPassed': True, 'rawUTF16AtXMLBoundaryEQ': True, 'unchangedChildModelAndEQImportReferences': True,
                'persistentLispImagesTouched': False,
                'fullOfflineNixRebuild': 'NOT-RUN; existing verified Store sources and unchanged local patches, fresh offline ASDF loads.'}
    (output / 'execution.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({k: evidence[k] for k in ['runtime', 'retainedLispChecks', 'newXTMIntegrationChecks', 'ctmStatuses', 'xtmCorpusStatuses']}, indent=2))


if __name__ == '__main__':
    main()
