#!/usr/bin/env python3
"""Reproduce the eight original failures; qualify local patches fully offline."""
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
BASE = 'ec3f21e45c46849a6bb674194b6f7cc75b67bba1'
PIN = '50ab793786d9de88ee30ec4e4c24fb4236fc2674'
POLICY = '(version 1)(allow default)(deny network*)'
NIX_EVAL = ['nix', 'eval', '--offline', '--option', 'eval-cache', 'false']


def command(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def failures():
    cases = []
    for name, encoding, bom, label in [
        ('utf16le-bom', 'utf-16le', b'\xff\xfe', 'UTF-16'),
        ('utf16be-bom', 'utf-16be', b'\xfe\xff', 'UTF-16'),
        ('utf16le-explicit-no-bom', 'utf-16le', b'', 'UTF-16LE'),
        ('utf16be-explicit-no-bom', 'utf-16be', b'', 'UTF-16BE')]:
        for content, suffix in [('Grüße 水', 'bmp'), ('Grüße 水 🦊', 'astral')]:
            if bom and suffix == 'bmp':
                continue
            source = "<?xml version='1.0' encoding='" + label + "'?><r>" + content + '</r>'
            cases.append({'name': name + ':' + suffix, 'source': source,
                          'octets': bom + source.encode(encoding), 'expectedText': content,
                          'declaredEncoding': label,
                          'cause': 'closure-common: UTF-16 second-unit check uses x instead of y'
                          if bom else 'closure-common: missing provisional XML signature; CXML: missing LE/BE declaration handling',
                          'functions': ['closure-common/encodings.lisp:decode-sequence'] if bom else
                          ['closure-common/xstream.lisp:figure-encoding', 'cxml/xml/xml-parse.lisp:setup-encoding'],
                          'normative': ['XML 1.0 §2.2, §4.3.3', 'Unicode §3.9.2, §3.10', 'RFC 2781 §2.2, §3.3']})
    cases.append({'name': 'utf16-bom-without-declaration:astral', 'source': '<r>水🦊</r>',
                  'octets': b'\xff\xfe' + '<r>水🦊</r>'.encode('utf-16le'), 'expectedText': '水🦊',
                  'declaredEncoding': None, 'cause': 'closure-common: UTF-16 second-unit check uses x instead of y',
                  'functions': ['closure-common/encodings.lisp:decode-sequence'],
                  'normative': ['XML 1.0 §2.2, §4.3.3', 'Unicode §3.9.2', 'RFC 2781 §2.2']})
    cases.append({'name': 'invalid-utf8', 'source': None, 'octets': b'<r>\xc3\x28</r>',
                  'expectedText': None, 'declaredEncoding': None,
                  'cause': 'closure-common: UTF-8 continuation bytes masked without validation',
                  'functions': ['closure-common/encodings.lisp:decode-sequence'],
                  'normative': ['XML 1.0 §4.3.3', 'Unicode §3.9.3 / Table 3-7', 'RFC 3629 §3–4']})
    return cases


def run_lisp(runtime, registry, output, label, *, source=None, script=None):
    invocation = ['/usr/bin/sandbox-exec', '-p', POLICY, runtime,
                  '--noinform', '--no-sysinit', '--no-userinit', '--script',
                  str(script) if script else '/dev/stdin']
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(invocation, cwd=ROOT,
                            env=dict(os.environ, CL_SOURCE_REGISTRY=registry, PYTHONDONTWRITEBYTECODE='1'),
                            input=source.encode() if source else None,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    (output / (label + '.log')).write_bytes(result.stdout)
    return result, {'label': label, 'command': invocation, 'exitCode': result.returncode,
                    'freshProcess': True, 'network': 'denied by sandbox-exec',
                    'startedAtUTC': started,
                    'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}


def checks(result, context):
    log = result.stdout.decode()
    passed = re.findall(r'^CXML-CHECK-PASS (.+)$', log, re.M)
    failed = re.findall(r'^CXML-CHECK-FAIL (.+)$', log, re.M)
    assert len(set(passed + failed)) == len(passed + failed)
    assert 'CXML-SUMMARY ' + str(len(passed)) + ' PASS ' + str(len(failed)) + ' FAIL' in log
    assert (result.returncode == 0) == (not failed)
    return dict(context, passedChecks=passed, failedChecks=failed)


def diagnostic_source(cases):
    source = '''(require :asdf)
(setf *compile-verbose* nil *load-verbose* nil)
(asdf:load-system "cxml")
(defun diagnose (id bytes)
 (format t "DIAG-ENCODING ~A ~A~%" id
  (runes::figure-encoding (cxml::make-octet-input-stream bytes)))
 (handler-case
  (let* ((node (cxml:parse-octets bytes (cxml-xmls:make-xmls-builder)
                 :disallow-internal-subset t
                 :entity-resolver (lambda (p s) (declare (ignore p s)) (error "External resource forbidden"))))
         (text (apply #'concatenate 'string (cxml-xmls:node-children node))))
   (format t "DIAG-ACCEPTED ~A ~{~X~^,~}~%" id (map 'list #'char-code text)))
  (error (c) (format t "DIAG-REJECTED ~A ~A ~A~%" id (type-of c)
              (substitute #\\Space #\\Newline (princ-to-string c))))))
'''
    for c in cases:
        source += '(diagnose ' + json.dumps(c['name']) + ' (make-array ' + str(len(c['octets']))
        source += " :element-type '(unsigned-byte 8) :initial-contents '(" + ' '.join(map(str, c['octets'])) + ')))\n'
    return source


def read_diagnostics(result, cases):
    assert result.returncode == 0
    lines = result.stdout.decode().splitlines()
    observations = {}
    for c in cases:
        name = c['name']
        encoding = next(l.split(' ', 2)[2] for l in lines if l.startswith('DIAG-ENCODING ' + name + ' '))
        accepted = next((l for l in lines if l.startswith('DIAG-ACCEPTED ' + name + ' ')), None)
        if accepted:
            codes = accepted.split(' ', 2)[2]
            observations[name] = {'recognizedEncoding': encoding, 'outcome': 'accepted',
                                  'text': ''.join(chr(int(n, 16)) for n in codes.split(','))}
        else:
            rejected = next(l.split(' ', 3) for l in lines if l.startswith('DIAG-REJECTED ' + name + ' '))
            observations[name] = {'recognizedEncoding': encoding, 'outcome': 'rejected',
                                  'condition': rejected[2], 'diagnostic': rejected[3]}
    return observations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/slice-19d0b')
    args = parser.parse_args()
    runtime = shutil.which(args.sbcl)
    assert runtime and command([runtime, '--version']) == 'SBCL 2.5.4'
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    system = command(NIX_EVAL + ['--impure', '--raw', '--expr', 'builtins.currentSystem'])
    environment = json.loads(command(NIX_EVAL + ['--json', '.#lib.cxmlEnvironment',
                                                '--apply', 'f: f "' + system + '"']))
    assert json.loads((ROOT / 'flake.lock').read_text())['nodes']['nixpkgs']['locked']['rev'] == PIN
    snapshot = subprocess.check_output(['git', 'show', BASE + ':tests/cxml-probe.lisp'], cwd=ROOT).decode()
    original_evidence = json.loads(command(['git', 'show', BASE + ':reports/slice-19d0/execution.json']))
    expected_checks = set(original_evidence['xmlRuns'][0]['checks'] + original_evidence['xmlRuns'][0]['failedChecks'])
    protected = {str(p.relative_to(ROOT)): sha(p)
                 for directory in ['vendor/cxtm', 'references', 'reports/slice-19d0']
                 for p in (ROOT / directory).rglob('*') if p.is_file()}
    files = ['flake.nix', 'flake.lock', 'topic-maps.asd', 'scripts/prepare-cxml.py',
             'scripts/validate-cxml-19d0b.py', 'tests/cxml-probe.lisp',
             'tests/cxml-encoding-regressions.lisp', 'src/xml/package.lisp', 'src/xml/parser.lisp',
             'patches/cxml-19d0b.patch', 'patches/closure-common-19d0b.patch',
             'README.md', 'docs/slice-19d0b-cxml-encoding.md']
    source_hashes = {p: sha(ROOT / p) for p in files}
    cases = failures()
    with tempfile.TemporaryDirectory(prefix='topic-maps-19d0b-') as temp:
        temp = Path(temp)
        patched = []
        for number in [1, 2]:
            patched.append(json.loads(command(['python3', str(ROOT / 'scripts/prepare-cxml.py'),
                                               '--directory', str(temp / ('sources-' + str(number)))])))
        assert patched[0]['patches'] == patched[1]['patches']
        pristine, context = run_lisp(runtime, environment['sourceRegistry'], output, 'original-58', source=snapshot)
        baseline = checks(pristine, context)
        assert len(baseline['passedChecks']) == 50 and len(baseline['failedChecks']) == 8
        assert set(baseline['failedChecks']) == {c['name'] for c in cases}
        before_result, before_context = run_lisp(runtime, environment['sourceRegistry'], output,
                                                'original-diagnostics', source=diagnostic_source(cases))
        before = read_diagnostics(before_result, cases)
        unqualified_source = '''(require :asdf)
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/xml")
(handler-case
 (progn (topic-maps.xml:parse-octets
          (make-array 4 :element-type '(unsigned-byte 8) :initial-contents '(60 114 47 62)) nil)
        (error "Unpatched dependency unexpectedly accepted"))
 (topic-maps.xml:unqualified-parser () (format t "UNPATCHED-BOUNDARY-PASS~%")))
'''
        unqualified_result, unqualified_context = run_lisp(
            runtime, environment['sourceRegistry'], output, 'unqualified-boundary', source=unqualified_source)
        assert unqualified_result.returncode == 0 and b'UNPATCHED-BOUNDARY-PASS' in unqualified_result.stdout
        raw_result, context = run_lisp(runtime, patched[0]['sourceRegistry'], output,
                                       'patched-original-58', source=snapshot)
        raw = checks(raw_result, context)
        assert not raw['failedChecks'] and set(raw['passedChecks']) == expected_checks
        xml_runs = []
        for number, provenance in enumerate(patched, 1):
            result, context = run_lisp(runtime, provenance['sourceRegistry'], output,
                                       'qualified-' + str(number), script=ROOT / 'tests/cxml-probe.lisp')
            run = checks(result, context)
            assert not run['failedChecks'] and expected_checks <= set(run['passedChecks'])
            xml_runs.append(run)
        assert xml_runs[0]['passedChecks'] == xml_runs[1]['passedChecks']
        after_result, after_context = run_lisp(runtime, patched[0]['sourceRegistry'], output,
                                              'patched-diagnostics', source=diagnostic_source(cases))
        after = read_diagnostics(after_result, cases)
        failure_report = []
        for c in cases:
            observation = after[c['name']]
            assert (observation['outcome'] == 'accepted') == (c['expectedText'] is not None)
            if c['expectedText'] is not None:
                assert observation['text'] == c['expectedText']
            else:
                assert observation['condition'] == 'WELL-FORMEDNESS-VIOLATION'
            failure_report.append({k: v for k, v in c.items() if k != 'octets'} | {
                'inputOctetsHex': c['octets'].hex(), 'inputLength': len(c['octets']),
                'inputSHA256': hashlib.sha256(c['octets']).hexdigest(),
                'before': before[c['name']], 'after': observation})
        (output / 'original-failures.json').write_text(json.dumps(failure_report, ensure_ascii=False, indent=2) + '\n')
        invocation = ['python3', str(ROOT / 'scripts/validate-slice-19c.py'), '--sbcl', runtime,
                      '--output', str(temp / 'regression')]
        result = subprocess.run(invocation, cwd=ROOT,
                                env=dict(os.environ, CL_SOURCE_REGISTRY=patched[0]['sourceRegistry'], PYTHONDONTWRITEBYTECODE='1'),
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
        (output / 'regression-driver.log').write_bytes(result.stdout)
        assert result.returncode == 0, 'Retained regression failed'
        regression = json.loads((temp / 'regression/execution.json').read_text())
        assert regression['importedStatuses'] == {'pass': 204, 'fail': 4, 'unsupported': 0, 'not-run': 65}
        assert regression['totalLispChecks'] == 12100
        identical_reports = []
        for previous in sorted((ROOT / 'reports/slice-19c').glob('*.json')):
            if previous.name != 'execution.json':
                assert (temp / 'regression' / previous.name).read_bytes() == previous.read_bytes(), previous.name
                identical_reports.append(previous.name)
        for name in ['execution.json', 'tests.log']:
            shutil.copyfile(temp / 'regression' / name, output / ('regression-' + name))
    assert not command(['git', 'diff', BASE, '--', 'src/tmdm', 'src/ctm', 'src/cxtm',
                        'vendor', 'references', 'flake.lock', 'scripts/test.sh'])
    assert protected == {p: sha(ROOT / p) for p in protected}
    assert source_hashes == {p: sha(ROOT / p) for p in source_hashes}
    for package in environment['manifest']:
        assert command(['nix', 'hash', 'path', '--type', 'sha256', '--base32', package['source']]) == package['sha256']
    evidence = {'baseCommit': BASE, 'branch': command(['git', 'branch', '--show-current']),
                'startedAtUTC': started, 'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'runtime': 'SBCL 2.5.4', 'nixpkgsCommit': PIN, 'nixSystem': system,
                'sourceEnvironment': environment, 'sourceSHA256': source_hashes,
                'sourceHashesVerifiedBeforeAndAfter': True, 'newDependencyNetworkAcquisitions': 0,
                'patchReproducibleAcrossTwoCopies': True, 'patchProvenance': patched,
                'temporarySourceContext': 'Effective source copies existed only during these recorded processes; reproduce with prepare-cxml.py.',
                'originalQualification': baseline, 'patchedUnmodifiedOriginalQualification': raw,
                'originalProbeSHA256': hashlib.sha256(snapshot.encode()).hexdigest(),
                'unpatchedBoundaryRefusal': unqualified_context,
                'original58ExpectationsChanged': False, 'xmlRuns': xml_runs,
                'originalDiagnosticContext': before_context, 'patchedDiagnosticContext': after_context,
                'xmlQualification': 'PASS', 'xmlChecksPerRun': len(xml_runs[0]['passedChecks']), 'xmlFailedChecks': 0,
                'bindingPublicContract': 'topic-maps.xml:parse-octets; verified patched dependencies; raw octets; mandatory namespace processing and DOCTYPE/entity denial; no caller overrides.',
                'regressionChecks': regression['regressionChecks'], 'totalLispChecks': regression['totalLispChecks'],
                'importedStatuses': regression['importedStatuses'], 'byteIdenticalRetainedReports': identical_reports,
                'newXTMContracts': 0, 'pinnedCorpusAndOriginalArchivesUnchanged': True,
                'fullOfflineNixRebuild': 'NOT-RUN; existing Nix artifacts plus offline source patching/ASDF compilation.'}
    (output / 'execution.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({k: evidence[k] for k in ['runtime', 'xmlQualification', 'xmlChecksPerRun',
          'xmlFailedChecks', 'original58ExpectationsChanged', 'totalLispChecks', 'importedStatuses']}, indent=2))


if __name__ == '__main__':
    main()
