#!/usr/bin/env python3
"""Qualify pinned CXML sources in fresh, network-denied SBCL 2.5.4 processes."""
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
BASE = 'bc4fcf0f126bab6567b37a21fc8c8eab2944c152'
PIN = '50ab793786d9de88ee30ec4e4c24fb4236fc2674'
POLICY = '(version 1)(allow default)(deny network*)'
# Avoid a local Nix evaluator-cache dynamic-derivations error; no cache or
# global Nix setting is changed, and no derivation is built here.
NIX_EVAL = ['nix', 'eval', '--offline', '--option', 'eval-cache', 'false']


def command(args, **kwargs):
    return subprocess.check_output(args, cwd=ROOT, text=True, **kwargs).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/slice-19d0')
    args = parser.parse_args()
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    lock = json.loads((ROOT / 'flake.lock').read_text())
    assert lock['nodes']['nixpkgs']['locked']['rev'] == PIN
    system = command(NIX_EVAL + ['--impure', '--raw',
                      '--expr', 'builtins.currentSystem'])
    # Evaluate the same source registry exported by the DevShell. This does
    # not realize the (separate, not fully cached) default toolchain shell.
    environment = json.loads(command(NIX_EVAL + [
        '--json', '.#lib.cxmlEnvironment',
        '--apply', 'f: f "' + system + '"']))
    registry = command(NIX_EVAL + ['--raw',
                        '.#devShells.' + system + '.default.CL_SOURCE_REGISTRY'])
    assert registry == environment['sourceRegistry']
    expected = {'cxml': '20200610-git', 'closure-common': '20181018-git',
                'babel': '20241012-git', 'alexandria': '20241012-git',
                'trivial-features': '20230618-git',
                'trivial-gray-streams': '20241012-git', 'puri': '20201016-git'}
    assert {p['name']: p['version'] for p in environment['manifest']} == expected
    for package in environment['manifest']:
        assert Path(package['source']).is_dir(), 'Source not provisioned: ' + package['name']
        actual = command(['nix', 'hash', 'path', '--type', 'sha256', '--base32', package['source']])
        assert actual == package['sha256'], 'SOURCE HASH MISMATCH: ' + package['name']
        package['verifiedNarSHA256'] = actual
    protected = {str(p.relative_to(ROOT)): sha(p)
                 for directory in ['vendor/cxtm', 'references']
                 for p in (ROOT / directory).rglob('*') if p.is_file()}
    files = ['flake.nix', 'flake.lock', 'tests/cxml-probe.lisp', 'scripts/validate-cxml.py']
    source_hashes = {p: sha(ROOT / p) for p in files}
    env = dict(os.environ, CL_SOURCE_REGISTRY=registry, PYTHONDONTWRITEBYTECODE='1')
    runs = []
    for number in [1, 2]:
        invocation = ['/usr/bin/sandbox-exec', '-p', POLICY, runtime,
                      '--noinform', '--no-sysinit', '--no-userinit', '--script',
                      str(ROOT / 'tests/cxml-probe.lisp')]
        result = subprocess.run(invocation, cwd=ROOT, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        log_name = 'cxml-run-' + str(number) + '.log'
        (output / log_name).write_bytes(result.stdout)
        log = result.stdout.decode('utf-8')
        checks = re.findall(r'^CXML-CHECK-PASS (.+)$', log, re.M)
        failed = re.findall(r'^CXML-CHECK-FAIL (.+)$', log, re.M)
        assert checks and len(checks + failed) == len(set(checks + failed))
        assert 'CXML-SUMMARY ' + str(len(checks)) + ' PASS ' + str(len(failed)) + ' FAIL' in log
        assert (result.returncode == 0) == (not failed), 'Unclassified probe execution failure'
        runs.append({'run': number, 'exitCode': result.returncode,
                     'freshProcess': True, 'network': 'denied by sandbox-exec',
                     'checks': checks, 'failedChecks': failed,
                     'command': invocation, 'log': log_name})
    assert runs[0]['checks'] == runs[1]['checks']
    assert runs[0]['failedChecks'] == runs[1]['failedChecks']
    # Retain the established full regression command/harness unchanged.
    with tempfile.TemporaryDirectory(prefix='topic-maps-19d0-regression-') as temp:
        invocation = ['python3', str(ROOT / 'scripts/validate-slice-19c.py'),
                      '--sbcl', runtime, '--output', temp]
        result = subprocess.run(invocation, cwd=ROOT, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output / 'regression-driver.log').write_bytes(result.stdout)
        assert result.returncode == 0, 'Retained regression failed'
        temporary = Path(temp)
        regression = json.loads((temporary / 'execution.json').read_text())
        assert regression['importedStatuses'] == {
            'pass': 204, 'fail': 4, 'unsupported': 0, 'not-run': 65}
        assert regression['totalLispChecks'] == 12100
        identical_reports = []
        for previous in sorted((ROOT / 'reports/slice-19c').glob('*.json')):
            if previous.name == 'execution.json':
                continue
            assert (temporary / previous.name).read_bytes() == previous.read_bytes(), previous.name
            identical_reports.append(previous.name)
        for name in ['execution.json', 'tests.log']:
            shutil.copyfile(temporary / name, output / ('regression-' + name))
    assert not command(['git', 'diff', BASE, '--', 'src', 'topic-maps.asd',
                        'vendor', 'references', 'flake.lock', 'scripts/test.sh'])
    assert protected == {p: sha(ROOT / p) for p in protected}
    assert source_hashes == {p: sha(ROOT / p) for p in source_hashes}
    evidence = {
        'baseCommit': BASE, 'branch': command(['git', 'branch', '--show-current']),
        'startedAtUTC': started,
        'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'runtime': 'SBCL 2.5.4', 'nixSystem': system, 'nixpkgsCommit': PIN,
        'sourceEnvironment': environment, 'sourceSHA256': source_hashes,
        'sourceHashesVerified': True, 'devShellRegistryEqualsTestRegistry': True,
        'xmlRuns': runs,
        'xmlChecksPerRun': len(runs[0]['checks']) + len(runs[0]['failedChecks']),
        'xmlPassedChecksPerRun': len(runs[0]['checks']),
        'xmlFailedChecksPerRun': len(runs[0]['failedChecks']),
        'xmlQualification': 'FAIL' if runs[0]['failedChecks'] else 'PASS',
        'encodingCounterexamples': {
            'utf16leAstral': {'character': '\U0001f98a', 'bytesHex': '\U0001f98a'.encode('utf-16le').hex(),
                             'strictPythonRoundTrip': bytes.fromhex('3ed88add').decode('utf-16le') == '\U0001f98a'},
            'invalidUtf8': {'bytesHex': 'c328', 'strictPythonRejection': False},
        },
        'securityPolicy': 'Reject every DOCTYPE; disallow internal subsets; '
                          'resolver signals external-resource-forbidden; no NIL fallback. '
                          'Catalog disabled and DTD cache fresh for each parse.',
        'securityCounterprobe': 'NIL resolver reaches trapped CXML file-opening fallback; '
                               'rejecting resolver never reaches it.',
        'sourceProvisioning': 'Only CXML and closure-common downloaded with authorized '
                              'hash-checked nix store prefetch-file; five sources already present.',
        'defaultDevShellBuild': 'NOT-RUN: existing pinned toolchain not fully provisioned',
        'fullOfflineRebuild': 'NOT-RUN: existing Nix SBCL and source artifacts used',
        'regressionChecks': regression['regressionChecks'],
        'totalLispChecks': regression['totalLispChecks'],
        'importedStatuses': regression['importedStatuses'],
        'byteIdenticalRetainedReports': identical_reports,
        'newXTMContracts': 0, 'pinnedCorpusAndNormativeReferencesUnchanged': True,
        'tmdmCtmCxtmAndExistingHarnessUnchanged': True,
    }
    try:
        bytes.fromhex('c328').decode('utf-8')
    except UnicodeDecodeError:
        evidence['encodingCounterexamples']['invalidUtf8']['strictPythonRejection'] = True
    assert evidence['encodingCounterexamples']['utf16leAstral']['strictPythonRoundTrip']
    assert evidence['encodingCounterexamples']['invalidUtf8']['strictPythonRejection']
    (output / 'execution.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({k: evidence[k] for k in ['runtime', 'xmlChecksPerRun', 'xmlPassedChecksPerRun',
          'xmlFailedChecksPerRun', 'xmlQualification', 'totalLispChecks', 'importedStatuses',
          'defaultDevShellBuild', 'fullOfflineRebuild']}, indent=2))
    # A successful regression/provisioning must never conceal failed parser
    # qualification. Preserve all evidence first, then report failure to CI.
    if evidence['xmlQualification'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
