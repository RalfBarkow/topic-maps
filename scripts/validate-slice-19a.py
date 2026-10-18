#!/usr/bin/env python3
"""Validate Slice 19A in a fresh SBCL 2.5.4 process with network access denied."""
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
BASE = '0573c4f710982dab1c3f2c9284adf459caaf73e9'
POLICY = '(version 1)(allow default)(deny network*)'
NAMES = ['validation', 'semantics', 'merging', 'associations', 'cxtm', 'occurrences',
         'prefixes', 'integers', 'decimals', 'dates', 'datetimes', 'timezones',
         'typed-names', 'scopes', 'variants', 'references', 'identifiers', 'reification', 'arity',
         'relationships', 'templates', 'map-import']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', default=str(ROOT / 'reports/slice-19a'))
    args = parser.parse_args()
    runtime = shutil.which(args.sbcl)
    assert runtime is not None, 'SBCL executable not found'
    output = pathlib.Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    protected = {str(p.relative_to(ROOT)): sha(p) for directory in ['vendor/cxtm', 'references']
                 for p in (ROOT / directory).rglob('*') if p.is_file()}
    sources = {str(p.relative_to(ROOT)): sha(p) for directory in ['src', 'tests', 'scripts', 'docs']
               for p in (ROOT / directory).rglob('*') if p.is_file() and
               '__pycache__' not in p.parts and p.suffix in ['.lisp', '.py', '.sh', '.md']}
    sources.update({p: sha(ROOT / p) for p in ['topic-maps.asd', 'README.md']})
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    version = subprocess.check_output([runtime, '--version'], text=True).strip()
    assert version == 'SBCL 2.5.4', version
    with tempfile.TemporaryDirectory(prefix='tmdm-slice-19a-validation-') as temp:
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
    old = ROOT / 'reports/slice-18'
    previous = json.loads((old / 'validation.json').read_text())
    now = json.loads((output / 'validation.json').read_text())
    assert now['statuses'] == {'pass': 187, 'fail': 2, 'unsupported': 0, 'not-run': 84}
    assert now['cases'] == previous['cases'], 'Imported case records changed'
    # Every old report must retain its observations, checks and original outputs.
    # CXTM's scope and additional model-check summary are the only new fields.
    for name in NAMES[1:-1]:
        prior = json.loads((old / (name + '.json')).read_text())
        current = json.loads((output / (name + '.json')).read_text())
        if name == 'cxtm':
            for key in ['cases', 'contractCounts']:
                assert prior[key] == current[key], name + ':' + key
        else:
            assert prior == current, name
    example = (ROOT / 'docs/reading-map-content-import.md').read_text().split('```lisp\n', 1)[1].split('\n```', 1)[0]
    inspection = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit',
                                 '--no-userinit', '--script', '/dev/stdin'], input=example.encode(), cwd=ROOT,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'describe.log').write_bytes(inspection.stdout)
    assert inspection.returncode == 0, 'Documented inspection forms failed'
    # Regression counterprobe: the BASE normalizer rejects the valid Reifier-first
    # case before the equal reified Names can merge. No second checkout or runtime.
    control = '''(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/tmdm/import-tests")
(load (make-string-input-stream (uiop:run-program
 (list "git" "show" "BASE:src/tmdm/merging.lisp") :output :string)))
(handler-case
 (progn (topic-maps.import.tests::reifier-order-test) (error "Base control did not reproduce the defect"))
 (topic-maps.tmdm:reification-error (c)
  (assert (eq :reifier-conflict (topic-maps.tmdm:reification-error-code c)))
  (format t "BASE-NORMALIZER-CONTROL-PASS: valid Reifier-first import rejected as ~A~%" c)))
'''.replace('BASE:', BASE + ':')
    probe = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit',
                            '--no-userinit', '--script', '/dev/stdin'], input=control.encode(), cwd=ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'base-normalizer-control.log').write_bytes(probe.stdout)
    assert probe.returncode == 0, 'Base normalizer control failed'
    for path, value in protected.items():
        assert sha(ROOT / path) == value, path
    assert not subprocess.check_output(['git', 'diff', BASE, '--', 'vendor', 'references', 'src/ctm', 'src/cxtm'], cwd=ROOT)
    for path, value in sources.items():
        assert sha(ROOT / path) == value, path
    previous_totals = json.loads((old / 'execution.json').read_text())['regressionChecks']
    totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1))
              for marker in [*previous_totals, 'MAP-IMPORT']}
    assert {k: totals[k] for k in previous_totals} == previous_totals
    evidence = dict(baseCommit=BASE, branch='codex/tmdm-slice-19a', runtime=version,
                    startedAtUTC=started, finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    command=command, exitCode=result.returncode, freshSBCL=True, network='denied by sandbox-exec',
                    regressionChecks=totals, totalLispChecks=sum(totals.values()), importedStatuses=now['statuses'],
                    importedStatusChanges=[], allPriorModelReportsAndCXTMOutputsUnchanged=True,
                    originalCorpusAndReferencesUnchanged=True, ctmAndCxtmSourcesUnchanged=True,
                    documentedInspectionPassed=True, baseNormalizerCounterprobePassed=True, sourceSHA256=sources,
                    qualification='TMDM content import model tests only. No CTM import or XTM contract executed. Two DateTime baseline FAILs unchanged.',
                    artifactsSHA256={str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*'))
                                     if p.is_file() and p.name != 'execution.json'})
    (output / 'execution.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: evidence[k] for k in ['runtime', 'regressionChecks', 'totalLispChecks', 'importedStatuses']}, sort_keys=True))
    print('SLICE-19A-VALIDATION-PASS: fresh offline regression; all imported contracts and prior model evidence unchanged')


if __name__ == '__main__':
    main()
