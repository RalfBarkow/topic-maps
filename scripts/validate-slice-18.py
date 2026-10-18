#!/usr/bin/env python3
"""Validate Slice 18 in a fresh offline process and preserve all prior evidence."""
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
BASE = '963f2a09444100d37e49cccbd6634879bd6742b5'
POLICY = '(version 1)(allow default)(deny network*)'
NAMES = ['validation', 'semantics', 'merging', 'associations', 'cxtm', 'occurrences',
         'prefixes', 'integers', 'decimals', 'dates', 'datetimes', 'timezones',
         'typed-names', 'scopes', 'variants', 'references', 'identifiers', 'reification', 'arity', 'relationships', 'templates']
OPEN = ['ctm/in/' + n + '.ctm' for n in ['template-subject-identifier2', 'template-ambiguous-parameter5', 'template-ambiguous-parameter6']]
OPEN += ['ctm/invalid/' + n + '.ctm' for n in ['template-item-identifier3', 'template-item-identifier-2nd-arg',
                                           'template-subject-locator3', 'template-subject-locator-2nd-arg']]
IMPORTS = ['ctm/in/include-template.ctm', 'ctm/in/include-template-wildcard.ctm',
           'ctm/in/mergemap-template.ctm', 'ctm/invalid/mergemap-template.ctm']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', default=str(ROOT / 'reports/slice-18'))
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
    assert version == 'SBCL 2.5.4', version
    with tempfile.TemporaryDirectory(prefix='ctm-slice-18-validation-') as temp:
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
    old = ROOT / 'reports/slice-17b'
    previous = json.loads((old / 'validation.json').read_text())
    now = json.loads((output / 'validation.json').read_text())
    templates = json.loads((output / 'templates.json').read_text())
    selected = sorted(c['id'] for c in templates['cases'] + templates['rejections'])
    assert len(selected) == len(set(selected)) == 67
    assert now['statuses'] == {'pass': 187, 'fail': 2, 'unsupported': 0, 'not-run': 84}
    assert [c['id'] for c in previous['cases']] == [c['id'] for c in now['cases']]
    changes = [(a['id'], a['status'], b['status']) for a, b in zip(previous['cases'], now['cases']) if a['status'] != b['status']]
    assert changes == [(id, 'not-run', 'pass') for id in selected]
    for a, b in zip(previous['cases'], now['cases']):
        if a['id'] not in selected:
            assert a == b, a['id']
        if b['id'] in OPEN + IMPORTS:
            assert b['status'] == 'not-run' and b['actualOutcome'] is None
    for name in NAMES[1:-1]:
        key = 'lexicalProbes' if name == 'timezones' else 'examples' if name == 'identifiers' else 'original' if name == 'arity' else 'cases'
        prior = json.loads((old / (name + '.json')).read_text())[key]
        current = json.loads((output / (name + '.json')).read_text())[key]
        assert prior == (current[:len(prior)] if name == 'cxtm' else current), name
        extra = 'negativeCases' if name == 'reification' else 'witnesses' if name == 'arity' else None
        if extra:
            assert json.loads((old / (name + '.json')).read_text())[extra] == json.loads((output / (name + '.json')).read_text())[extra], name
    cxtm = json.loads((output / 'cxtm.json').read_text())
    assert cxtm['contractCounts'] == {'pass': 165, 'fail': 2}
    actual_dir = output / 'actual'
    actual_dir.mkdir(exist_ok=True)
    for case in cxtm['cases']:
        if case['id'] in selected:
            actual = case['actualCXTM'].encode('utf-8')
            baseline = ROOT / 'vendor/cxtm/ctm/baseline' / (pathlib.Path(case['id']).name + '.cxtm')
            assert actual == baseline.read_bytes()
            (actual_dir / baseline.name).write_bytes(actual)
    example = (ROOT / 'docs/reading-ctm-templates.md').read_text().split('```lisp\n', 1)[1].split('\n```', 1)[0]
    inspection = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit',
                                 '--no-userinit', '--script', '/dev/stdin'], input=example.encode(), cwd=ROOT,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'describe.log').write_bytes(inspection.stdout)
    assert inspection.returncode == 0, 'Documented inspection forms failed'
    # Load committed BASE definitions in a separate process. No checkout/cache
    # changes, no second model and no persistent runtime are involved.
    control = '''(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/tmdm")
(dolist (path '("package" "conditions" "unicode" "iri" "lexer" "reader"))
  (load (make-string-input-stream
    (uiop:run-program (list "git" "show" (concatenate 'string "BASE:src/ctm/" path ".lisp")) :output :string))))
(dolist (text '("def f() a. end f()" "a f()." "$x."))
  (handler-case
    (progn (topic-maps.ctm:deserialize-string text :document-iri "https://example.invalid/base.ctm")
           (error "Base unexpectedly supports Templates"))
    (topic-maps.ctm:ctm-unsupported (condition)
      (format t "BASE-CONTROL-PASS: ~S => ~A~%" text (topic-maps.ctm:error-code condition)))))
'''.replace('BASE:', BASE + ':')
    probe = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit',
                            '--no-userinit', '--script', '/dev/stdin'], input=control.encode(), cwd=ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'base-control.log').write_bytes(probe.stdout)
    assert probe.returncode == 0, 'Base control failed'
    for path, value in protected.items():
        assert sha(ROOT / path) == value, path
    assert not subprocess.check_output(['git', 'diff', BASE, '--', 'vendor', 'references', 'src/tmdm', 'src/cxtm'], cwd=ROOT)
    for path, value in sources.items():
        assert sha(ROOT / path) == value, path
    previous_totals = json.loads((old / 'execution.json').read_text())['regressionChecks']
    totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1))
              for marker in [*previous_totals, 'TEMPLATES']}
    assert {k: totals[k] for k in previous_totals} == previous_totals
    evidence = dict(baseCommit=BASE, branch='codex/ctm-slice-18', runtime=version,
                    startedAtUTC=started, finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    command=command, exitCode=result.returncode, freshSBCL=True, network='denied by sandbox-exec',
                    regressionChecks=totals, totalLispChecks=sum(totals.values()), importedStatuses=now['statuses'],
                    importedStatusChanges=changes, prior108PassingCXTMAndTwoKnownFailuresUnchanged=True,
                    allRetainedModelObservationsUnchanged=True, originalCorpusAndReferencesUnchanged=True,
                    tmdmAndCxtmSourcesUnchanged=True, documentedInspectionPassed=True, baseControlPassed=True,
                    openGrammarContracts=OPEN, unimplementedImportContracts=IMPORTS, sourceSHA256=sources,
                    qualification='Templates expand supported CTM statements into the existing TMDM. Seven grammar cases and Import-dependent contracts remain NOT-RUN. The two DateTime baseline FAILs remain unchanged.',
                    artifactsSHA256={str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*'))
                                     if p.is_file() and p.name != 'execution.json'})
    (output / 'execution.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: evidence[k] for k in ['runtime', 'regressionChecks', 'totalLispChecks', 'importedStatuses']}, sort_keys=True))
    print('SLICE-18-VALIDATION-PASS: fresh offline regression, 57 original byte comparisons, 10 specific rejections; prior results unchanged')


if __name__ == '__main__':
    main()
