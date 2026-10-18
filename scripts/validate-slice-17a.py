#!/usr/bin/env python3
"""Record Slice 17A's full offline regression and unchanged retained evidence."""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'f1270a43720ab1454bebfb3d0a9e3555554a7ab9'
POLICY = '(version 1)(allow default)(deny network*)'
NAMES = ['validation', 'semantics', 'merging', 'associations', 'cxtm', 'occurrences',
         'prefixes', 'integers', 'decimals', 'dates', 'datetimes', 'timezones',
         'typed-names', 'scopes', 'variants', 'references', 'identifiers', 'reification', 'arity']
SELECTED = 'ctm/in/association-duplicate-role.ctm'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', default=str(ROOT / 'reports/slice-17a'))
    args = parser.parse_args()
    runtime = shutil.which(args.sbcl)
    if runtime is None:
        raise RuntimeError('SBCL executable not found: ' + args.sbcl)
    output = pathlib.Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    protected = {str(p.relative_to(ROOT)): sha(p) for directory in ['vendor/cxtm', 'references', 'src/tmdm', 'src/cxtm']
                 for p in (ROOT / directory).rglob('*') if p.is_file()}
    sources = {str(p.relative_to(ROOT)): sha(p) for directory in ['src', 'tests', 'scripts', 'docs']
               for p in (ROOT / directory).rglob('*') if p.is_file() and
               '__pycache__' not in p.parts and p.suffix in ['.lisp', '.py', '.sh', '.md']}
    sources.update({p: sha(ROOT / p) for p in ['topic-maps.asd', 'README.md']})
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    version = subprocess.check_output([runtime, '--version'], text=True).strip()
    with tempfile.TemporaryDirectory(prefix='ctm-slice-17a-validation-') as temp:
        report = pathlib.Path(temp) / 'validation.json'
        command = ['/usr/bin/sandbox-exec', '-p', POLICY, '/usr/bin/env', 'PYTHONDONTWRITEBYTECODE=1',
                   'SBCL=' + runtime, 'TOPIC_MAPS_REPORT=' + str(report), str(ROOT / 'scripts/test.sh')]
        result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output / 'tests.log').write_bytes(result.stdout)
        if result.returncode:
            raise RuntimeError('Full regression failed: see ' + str(output / 'tests.log'))
        log = result.stdout.decode('utf-8')
        for name in NAMES:
            source = report if name == 'validation' else pathlib.Path(str(report) + '.' + name + '.json')
            (output / (name + '.json')).write_bytes(source.read_bytes())
    old = ROOT / 'reports/slice-16b'
    previous = json.loads((old / 'validation.json').read_text())
    now = json.loads((output / 'validation.json').read_text())
    assert now['statuses'] == {'pass': 107, 'fail': 2, 'unsupported': 0, 'not-run': 164}
    assert [c['id'] for c in previous['cases']] == [c['id'] for c in now['cases']]
    changes = [(a['id'], a['status'], b['status']) for a, b in zip(previous['cases'], now['cases']) if a['status'] != b['status']]
    assert changes == [(SELECTED, 'not-run', 'pass')]
    for a, b in zip(previous['cases'], now['cases']):
        if a['id'] != SELECTED:
            assert a == b, a['id']
    for name in NAMES[1:-1]:
        key = 'lexicalProbes' if name == 'timezones' else 'examples' if name == 'identifiers' else 'cases'
        prior = json.loads((old / (name + '.json')).read_text())[key]
        current = json.loads((output / (name + '.json')).read_text())[key]
        assert prior == (current[:len(prior)] if name == 'cxtm' else current), name
        if name == 'reification':
            assert json.loads((old / (name + '.json')).read_text())['negativeCases'] == json.loads((output / (name + '.json')).read_text())['negativeCases']
    cxtm = json.loads((output / 'cxtm.json').read_text())
    assert cxtm['contractCounts'] == {'pass': 95, 'fail': 2}
    selected = [c for c in cxtm['cases'] if c['id'] == SELECTED]
    assert len(selected) == 1
    actual = selected[0]['actualCXTM'].encode('utf-8')
    baseline = ROOT / 'vendor/cxtm/ctm/baseline/association-duplicate-role.ctm.cxtm'
    assert actual == baseline.read_bytes() and len(actual) == 1157
    (output / 'association-duplicate-role.ctm.cxtm').write_bytes(actual)
    example = (ROOT / 'docs/reading-association-arity.md').read_text().split('```lisp\n', 1)[1].split('\n```', 1)[0]
    inspection = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit',
                                 '--no-userinit', '--script', '/dev/stdin'], input=example.encode(), cwd=ROOT,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'describe.log').write_bytes(inspection.stdout)
    assert inspection.returncode == 0, 'Documented inspection forms failed'
    # Demonstrate that the original reader rejects this exact source. It is
    # loaded only in another disposable process; the checkout is never reverted.
    control = '''(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/ctm")
(let ((source (uiop:run-program '("git" "show" "BASE:src/ctm/reader.lisp") :output :string)))
  (load (make-string-input-stream source)))
(handler-case
    (progn (topic-maps.ctm:deserialize-file "vendor/cxtm/ctm/in/association-duplicate-role.ctm"
             :document-iri "https://example.invalid/original.ctm")
           (error "Original reader unexpectedly accepted n-ary source"))
  (topic-maps.ctm:ctm-unsupported (c)
    (assert (eq :association-arity (topic-maps.ctm:error-code c)))
    (assert (= 48 (topic-maps.ctm:error-position c)))
    (format t "ORIGINAL-READER-CONTROL-PASS: CTM-UNSUPPORTED :ASSOCIATION-ARITY at 48~%")))
'''.replace('BASE:', BASE + ':')
    negative = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit',
                               '--no-userinit', '--script', '/dev/stdin'], input=control.encode(), cwd=ROOT,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'original-reader-control.log').write_bytes(negative.stdout)
    assert negative.returncode == 0, 'Original reader control failed'
    for path, value in protected.items():
        assert sha(ROOT / path) == value, path
    # The independent model and serializer must also match the accepted base.
    assert not subprocess.check_output(['git', 'diff', BASE, '--', 'src/tmdm', 'src/cxtm', 'vendor', 'references'], cwd=ROOT)
    for path, value in sources.items():
        assert sha(ROOT / path) == value, path
    previous_totals = json.loads((old / 'execution.json').read_text())['regressionChecks']
    totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1))
              for marker in [*previous_totals, 'ASSOCIATION-ARITY']}
    assert {k: totals[k] for k in previous_totals} == previous_totals
    evidence = dict(baseCommit=BASE, branch='codex/ctm-slice-17a', runtime=version,
                    startedAtUTC=started, finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    command=command, exitCode=result.returncode, freshSBCL=True, network='denied by sandbox-exec',
                    regressionChecks=totals, totalLispChecks=sum(totals.values()), importedStatuses=now['statuses'],
                    importedStatusChanges=changes, previous94PassingCXTMAndTwoKnownFailuresUnchanged=True,
                    allRetainedModelObservationsUnchanged=True, modelAndCanonicalizerUnchangedFromBase=True,
                    originalCorpusAndReferencesUnchanged=True, documentedInspectionPassed=True,
                    originalReaderControlPassed=True, sourceSHA256=sources,
                    qualification='Unbounded CTM Role declarations; core-subject identity protection and isa/ako remain open for 17B. The two DateTime baseline FAILs remain unchanged.',
                    artifactsSHA256={str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*'))
                                     if p.is_file() and p.name != 'execution.json'})
    (output / 'execution.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: evidence[k] for k in ['runtime', 'regressionChecks', 'totalLispChecks', 'importedStatuses', 'importedStatusChanges']}, sort_keys=True))
    print('SLICE-17A-VALIDATION-PASS: complete fresh offline SBCL regression; 1157 original bytes; all retained contracts unchanged')


if __name__ == '__main__':
    main()
