#!/usr/bin/env python3
"""Record Slice 17B's full fresh offline regression and unchanged prior contracts."""
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
BASE = 'bdc56a8236c6e6180df217d37e82846025026096'
POLICY = '(version 1)(allow default)(deny network*)'
NAMES = ['validation', 'semantics', 'merging', 'associations', 'cxtm', 'occurrences',
         'prefixes', 'integers', 'decimals', 'dates', 'datetimes', 'timezones',
         'typed-names', 'scopes', 'variants', 'references', 'identifiers', 'reification', 'arity', 'relationships']
SELECTED = ['ctm/in/' + name + '.ctm' for name in [
    'isa-relationship', 'isa-relationship-duplicate', 'isa-relationship-duplicate2',
    'isa-relationship-embedded', 'isa-relationship-type-qname', 'ako-relationship',
    'ako-relationship-duplicate', 'ako-relationship-duplicate2', 'ako-relationship-embedded',
    'ako-relationship-supertype-qname', 'ako-merge-away', 'subject-identifier-topicref', 'item-identifier-topicref']]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', default=str(ROOT / 'reports/slice-17b'))
    args = parser.parse_args()
    runtime = shutil.which(args.sbcl)
    if runtime is None:
        raise RuntimeError('SBCL executable not found: ' + args.sbcl)
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
    with tempfile.TemporaryDirectory(prefix='ctm-slice-17b-validation-') as temp:
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
    old = ROOT / 'reports/slice-17a'
    previous = json.loads((old / 'validation.json').read_text())
    now = json.loads((output / 'validation.json').read_text())
    assert now['statuses'] == {'pass': 120, 'fail': 2, 'unsupported': 0, 'not-run': 151}
    assert [c['id'] for c in previous['cases']] == [c['id'] for c in now['cases']]
    changes = [(a['id'], a['status'], b['status']) for a, b in zip(previous['cases'], now['cases']) if a['status'] != b['status']]
    assert changes == [(id, 'not-run', 'pass') for id in sorted(SELECTED)]
    for a, b in zip(previous['cases'], now['cases']):
        if a['id'] not in SELECTED:
            assert a == b, a['id']
    for name in NAMES[1:-1]:
        key = 'lexicalProbes' if name == 'timezones' else 'examples' if name == 'identifiers' else 'original' if name == 'arity' else 'cases'
        prior = json.loads((old / (name + '.json')).read_text())[key]
        current = json.loads((output / (name + '.json')).read_text())[key]
        assert prior == (current[:len(prior)] if name == 'cxtm' else current), name
        extra = 'negativeCases' if name == 'reification' else 'witnesses' if name == 'arity' else None
        if extra:
            assert json.loads((old / (name + '.json')).read_text())[extra] == json.loads((output / (name + '.json')).read_text())[extra], name
    cxtm = json.loads((output / 'cxtm.json').read_text())
    assert cxtm['contractCounts'] == {'pass': 108, 'fail': 2}
    actual_dir = output / 'actual'
    actual_dir.mkdir(exist_ok=True)
    selected = [c for c in cxtm['cases'] if c['id'] in SELECTED]
    assert len(selected) == len(SELECTED)
    for case in selected:
        actual = case['actualCXTM'].encode('utf-8')
        baseline = ROOT / 'vendor/cxtm/ctm/baseline' / (pathlib.Path(case['id']).name + '.cxtm')
        assert actual == baseline.read_bytes()
        (actual_dir / baseline.name).write_bytes(actual)
    example = (ROOT / 'docs/reading-type-relationships.md').read_text().split('```lisp\n', 1)[1].split('\n```', 1)[0]
    inspection = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit',
                                 '--no-userinit', '--script', '/dev/stdin'], input=example.encode(), cwd=ROOT,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'describe.log').write_bytes(inspection.stdout)
    assert inspection.returncode == 0, 'Documented inspection forms failed'
    # Restore definitions only inside another fresh disposable process. No
    # checkout reversal, persistent image changes or alternate object model.
    control = '''(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/ctm")
(dolist (path '("src/tmdm/reification.lisp" "src/tmdm/merging.lisp" "src/ctm/reader.lisp"))
  (load (make-string-input-stream
          (uiop:run-program (list "git" "show" (concatenate 'string "BASE:" path)) :output :string))))
(let* ((m (topic-maps.tmdm:make-topic-map))
       (a (topic-maps.tmdm:intern-topic m :subject-identifier "http://psi.topicmaps.org/iso13250/model/type"))
       (b (topic-maps.tmdm:intern-topic m :subject-identifier "http://psi.topicmaps.org/iso13250/model/instance"))
       (c (topic-maps.tmdm:merge-topics a b)))
  (assert (= 1 (length (topic-maps.tmdm:topic-map-topics m))))
  (assert (= 2 (length (topic-maps.tmdm:topic-subject-identifiers c))))
  (format t "BASE-CORE-GAP-CONFIRMED: different type/instance Core Subjects merged~%"))
(dolist (text '("a isa b." "a ako b."))
  (handler-case
      (progn (topic-maps.ctm:deserialize-string text :document-iri "https://example.invalid/base.ctm")
             (error "Base reader unexpectedly accepted relationship syntax"))
    (topic-maps.ctm:ctm-unsupported (c)
      (assert (eq :unsupported-keyword (topic-maps.ctm:error-code c)))
      (format t "BASE-READER-CONTROL-PASS: ~S rejected as ~A~%" text (topic-maps.ctm:error-code c)))))
'''.replace('BASE:', BASE + ':')
    negative = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit',
                               '--no-userinit', '--script', '/dev/stdin'], input=control.encode(), cwd=ROOT,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'base-control.log').write_bytes(negative.stdout)
    assert negative.returncode == 0, 'Base control failed'
    for path, value in protected.items():
        assert sha(ROOT / path) == value, path
    assert not subprocess.check_output(['git', 'diff', BASE, '--', 'vendor', 'references'], cwd=ROOT)
    for path, value in sources.items():
        assert sha(ROOT / path) == value, path
    previous_totals = json.loads((old / 'execution.json').read_text())['regressionChecks']
    totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1))
              for marker in [*previous_totals, 'TYPE-RELATIONSHIPS']}
    assert {k: totals[k] for k in previous_totals} == previous_totals
    relationships = json.loads((output / 'relationships.json').read_text())
    evidence = dict(baseCommit=BASE, branch='codex/ctm-slice-17b', runtime=version,
                    startedAtUTC=started, finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    command=command, exitCode=result.returncode, freshSBCL=True, network='denied by sandbox-exec',
                    regressionChecks=totals, totalLispChecks=sum(totals.values()), importedStatuses=now['statuses'],
                    importedStatusChanges=changes, previous95PassingCXTMAndTwoKnownFailuresUnchanged=True,
                    allRetainedModelObservationsUnchanged=True, originalCorpusAndReferencesUnchanged=True,
                    documentedInspectionPassed=True, baseControlPassed=True,
                    protectedCoreSubjectIdentifiers=relationships['coreSubjectIdentifiers'],
                    atomicConflictObservations=len(relationships['rejections']), sourceSHA256=sources,
                    qualification='CTM isa/ako and TMDM 2006 Core Subject locators. Atomic semantic rejection is API policy. No inferred Associations are materialized. The two DateTime baseline FAILs remain unchanged.',
                    artifactsSHA256={str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*'))
                                     if p.is_file() and p.name != 'execution.json'})
    (output / 'execution.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: evidence[k] for k in ['runtime', 'regressionChecks', 'totalLispChecks', 'importedStatuses', 'atomicConflictObservations']}, sort_keys=True))
    print('SLICE-17B-VALIDATION-PASS: complete fresh offline SBCL regression; 13 original byte comparisons; all retained contracts unchanged')


if __name__ == '__main__':
    main()
