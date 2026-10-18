#!/usr/bin/env python3
"""Fresh offline XTM identity checks plus the unchanged XML and CTM regressions."""
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
BASE = '1691c8e0712e30666de2e667a5050eccb0086f71'
POLICY = '(version 1)(allow default)(deny network*)'


def command(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/slice-19d1')
    args = parser.parse_args()
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    protected_paths = ['src/tmdm', 'src/ctm', 'src/cxtm', 'src/xml', 'patches', 'flake.nix',
                       'flake.lock', 'vendor', 'references', 'scripts/prepare-cxml.py',
                       'tests/cxml-probe.lisp', 'tests/cxml-encoding-regressions.lisp', 'scripts/test.sh']
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    protected = {str(p.relative_to(ROOT)): sha(p) for directory in ['vendor/cxtm', 'references', 'patches']
                 for p in (ROOT / directory).rglob('*') if p.is_file()}
    sources = {str(p.relative_to(ROOT)): sha(p) for directory in ['src', 'tests', 'scripts', 'docs']
               for p in (ROOT / directory).rglob('*') if p.is_file() and p.suffix in ['.lisp', '.py', '.sh', '.md']}
    sources.update({p: sha(ROOT / p) for p in ['topic-maps.asd', 'README.md', 'flake.nix', 'flake.lock']})
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # The XTM source must have exactly one XML parse entry, the qualified boundary.
    xtm_source = '\n'.join(p.read_text() for p in sorted((ROOT / 'src/xtm').glob('*.lisp')))
    assert xtm_source.count('(topic-maps.xml:parse-octets ') == 1
    assert not re.search(r'\(cxml:parse[-\w]*\s', xtm_source, re.I)
    runs = []
    with tempfile.TemporaryDirectory(prefix='topic-maps-19d1-') as tmp:
        tmp = Path(tmp)
        preparation = ['python3', 'scripts/prepare-cxml.py', '--directory', str(tmp / 'sources')]
        provenance = json.loads(command(preparation))
        environment = dict(os.environ, CL_SOURCE_REGISTRY=provenance['sourceRegistry'], PYTHONDONTWRITEBYTECODE='1')
        for label, script in [('xml', 'tests/cxml-probe.lisp'), ('xtm-1', 'scripts/fresh-xtm.lisp'),
                              ('xtm-2', 'scripts/fresh-xtm.lisp')]:
            env = dict(environment)
            if label.startswith('xtm'):
                env['TOPIC_MAPS_XTM_REPORT'] = str(output / (label + '.json'))
            invocation = ['/usr/bin/sandbox-exec', '-p', POLICY, runtime,
                          '--noinform', '--no-sysinit', '--no-userinit', '--script', script]
            context = {'label': label, 'command': invocation, 'freshProcess': True,
                       'network': 'denied by sandbox-exec',
                       'startedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
            result = subprocess.run(invocation, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=120)
            (output / (label + '.log')).write_bytes(result.stdout)
            context.update(exitCode=result.returncode, finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
            assert result.returncode == 0, label + ' failed; see saved log'
            prefix = 'CXML' if label == 'xml' else 'XTM'
            passed = re.findall(r'^' + prefix + r'-CHECK-PASS (.+)$', result.stdout.decode(), re.M)
            assert len(passed) == len(set(passed))
            assert prefix + '-SUMMARY ' + str(len(passed)) + ' PASS 0 FAIL' in result.stdout.decode()
            context['passedChecks'] = len(passed)
            if label == 'xml':
                assert len(passed) == 146
            else:
                report = json.loads((output / (label + '.json')).read_text())
                assert report['checks'] == passed
                assert report['statuses'] == {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 0}
                assert report['helperSource']['status'] == 'pass'
                assert len(report['cases']) == 6
                for case in report['actualAndExpected']:
                    assert case['actual'].encode() == case['expected'].encode()
                assert report['otherCorpusInputs'] == {'positiveUnexecuted': 107, 'negativeUnregisteredUnexecuted': 11}
            runs.append(context)
        assert (output / 'xtm-1.json').read_bytes() == (output / 'xtm-2.json').read_bytes()
        regression_dir = tmp / 'regression'
        invocation = ['python3', 'scripts/validate-slice-19c.py', '--sbcl', runtime, '--output', str(regression_dir)]
        result = subprocess.run(invocation, cwd=ROOT, env=environment, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=180)
        (output / 'regression-driver.log').write_bytes(result.stdout)
        assert result.returncode == 0, 'Retained regression failed'
        regression = json.loads((regression_dir / 'execution.json').read_text())
        assert regression['totalLispChecks'] == 12100
        assert regression['importedStatuses'] == {'pass': 204, 'fail': 4, 'unsupported': 0, 'not-run': 65}
        identical = []
        for previous in sorted((ROOT / 'reports/slice-19c').glob('*.json')):
            if previous.name != 'execution.json':
                assert (regression_dir / previous.name).read_bytes() == previous.read_bytes(), previous.name
                identical.append(previous.name)
        for name in ['tests.log', 'execution.json']:
            shutil.copyfile(regression_dir / name, output / ('regression-' + name))
    assert protected == {p: sha(ROOT / p) for p in protected}
    assert sources == {p: sha(ROOT / p) for p in sources}
    assert not command(['git', 'diff', BASE, '--'] + protected_paths)
    evidence = {'baseCommit': BASE, 'branch': command(['git', 'branch', '--show-current']),
                'startedAtUTC': started, 'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'runtime': 'SBCL 2.5.4', 'newDependencyDownloads': 0, 'sourcePreparationCommand': preparation,
                'qualifiedSourceProvenance': provenance, 'sourceSHA256': sources,
                'protectedCorpusAndDecoderPatchesUnchanged': True, 'xmlBoundaryStaticAndRuntimeChecks': 'PASS',
                'runs': runs, 'ctmStatuses': regression['importedStatuses'],
                'retainedLispChecks': regression['totalLispChecks'], 'retainedChecks': regression['regressionChecks'],
                'retainedRegressionCommand': invocation, 'retainedReportsByteIdentical': identical,
                'xtmStatuses': {'pass': 6, 'fail': 0, 'unsupported': 0, 'not-run': 0},
                'unexecutedOtherXTMInputs': {'positive': 107, 'negative': 11},
                'directXTMHelperSource': 'PASS; 5 Topics, 1 Association, 2 Roles; not a CTM Mergemap PASS',
                'deterministicXTMReports': True, 'persistentLispImagesTouched': False,
                'fullOfflineNixRebuild': 'NOT-RUN; original Store sources, verified existing local patches and fresh offline ASDF loads.'}
    (output / 'execution.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({k: evidence[k] for k in ['runtime', 'runs', 'ctmStatuses', 'retainedLispChecks', 'xtmStatuses']}, indent=2))


if __name__ == '__main__':
    main()
