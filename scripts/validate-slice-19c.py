#!/usr/bin/env python3
"""Validate Slice 19C in a fresh SBCL 2.5.4 process with network access denied."""
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
BASE = '5e716c078b885e97ebe858230ce7d8578e65ae4b'
POLICY = '(version 1)(allow default)(deny network*)'
NAMES = ['validation', 'semantics', 'merging', 'associations', 'cxtm', 'occurrences',
         'prefixes', 'integers', 'decimals', 'dates', 'datetimes', 'timezones',
         'typed-names', 'scopes', 'variants', 'references', 'identifiers', 'reification', 'arity',
         'relationships', 'templates', 'map-import', 'mergemap', 'include']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', default=str(ROOT / 'reports/slice-19c'))
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
    with tempfile.TemporaryDirectory(prefix='tmdm-slice-19c-validation-') as temp:
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
    old = ROOT / 'reports/slice-19b'
    previous = json.loads((old / 'validation.json').read_text())
    now = json.loads((output / 'validation.json').read_text())
    assert now['statuses'] == {'pass': 204, 'fail': 4, 'unsupported': 0, 'not-run': 65}
    selected = sorted('ctm/in/' + n + '.ctm' for n in [
        'include', 'include-prefix', 'include-prefix2', 'include-template',
        'include-template-wildcard', 'include-tm-reifier', 'include-topicref',
        'include-wildcard', 'include-wildcard2'])
    selected += sorted('ctm/invalid/' + n + '.ctm' for n in ['include-prefix', 'include-prefix2', 'include-xtm'])
    discrepancies = {'ctm/in/include-template.ctm', 'ctm/in/include-wildcard2.ctm'}
    changes = [(a['id'], a['status'], b['status']) for a, b in zip(previous['cases'], now['cases']) if a['status'] != b['status']]
    assert changes == [(id, 'not-run', 'fail' if id in discrepancies else 'pass') for id in selected]
    assert [c['id'] for c in previous['cases']] == [c['id'] for c in now['cases']]
    for a, b in zip(previous['cases'], now['cases']):
        if a['id'] not in selected:
            assert a == b, a['id']
    renamed = {
        'semantics': ('identity-feature-boundary:%include <other.ctm>', 'identity:Include-requires-explicit-resolver'),
        'prefixes': ('remaining-construct-unsupported:%include <other.ctm>', 'prefix:Include-requires-explicit-resolver'),
        'references': ('references:feature-boundary:%include <file.ctm>', 'references:Include-requires-explicit-resolver'),
        'templates': ('diagnostic:unchanged-excluded-feature:%include <other>', 'diagnostic:Include-requires-explicit-resolver')}
    for name in NAMES[1:-1]:
        prior = json.loads((old / (name + '.json')).read_text())
        current = json.loads((output / (name + '.json')).read_text())
        if name == 'cxtm':
            assert prior['cases'] == current['cases'][:len(prior['cases'])]
            assert current['contractCounts'] == {'pass': 176, 'fail': 4}
            actual = output / 'actual'
            actual.mkdir(exist_ok=True)
            for case in current['cases'][len(prior['cases']):]:
                baseline = ROOT / 'vendor/cxtm/ctm/baseline' / (pathlib.Path(case['id']).name + '.cxtm')
                raw = case['actualCXTM'].encode('utf-8')
                assert (raw == baseline.read_bytes()) == (case['id'] not in discrepancies)
                (actual / baseline.name).write_bytes(raw)
        elif name in renamed:
            old_check, new_check = renamed[name]
            assert [new_check if c == old_check else c for c in prior['checks']] == current['checks']
            for key in prior.keys() - {'checks', 'rejections'}:
                assert prior[key] == current[key], name + ':' + key
            if name == 'templates':
                # Original rejection class/code/source/positions stay identical.
                # Contexts now also preserve definition/invocation provenance.
                for a, b in zip(prior['rejections'], current['rejections']):
                    assert {k: v for k, v in a.items() if k != 'context'} == {k: v for k, v in b.items() if k != 'context'}
                    assert a['context'] == b['context'] or ':DEFINITION-SOURCE' in b['context']
        else:
            assert prior == current, name
    example = (ROOT / 'docs/reading-ctm-include.md').read_text().split('```lisp\n', 1)[1].split('\n```', 1)[0]
    inspection = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit',
                                 '--no-userinit', '--script', '/dev/stdin'], input=example.encode(), cwd=ROOT,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'describe.log').write_bytes(inspection.stdout)
    assert inspection.returncode == 0, 'Documented inspection forms failed'
    control = """(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd (truename "topic-maps.asd"))
(asdf:load-system "topic-maps/ctm")
(load (make-string-input-stream (uiop:run-program
 (list "git" "show" "BASE:src/ctm/lexer.lisp") :output :string)))
(handler-case
 (progn (topic-maps.ctm:deserialize-string
          "%include <child>"
          :document-iri "urn:base-control")
        (error "Base unexpectedly accepted Include"))
 (topic-maps.ctm:ctm-unsupported (c)
  (assert (eq :unsupported-directive (topic-maps.ctm:error-code c)))
  (format t "BASE-CONTROL-PASS: committed lexer rejected Include as ~A~%" c)))
""".replace('BASE:', BASE + ':')
    probe = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit',
                            '--no-userinit', '--script', '/dev/stdin'], input=control.encode(), cwd=ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'base-control.log').write_bytes(probe.stdout)
    assert probe.returncode == 0, 'Base lexer control failed'
    for path, value in protected.items():
        assert sha(ROOT / path) == value, path
    assert not subprocess.check_output(['git', 'diff', BASE, '--', 'vendor', 'references', 'src/tmdm', 'src/cxtm'], cwd=ROOT)
    for path, value in sources.items():
        assert sha(ROOT / path) == value, path
    previous_totals = json.loads((old / 'execution.json').read_text())['regressionChecks']
    totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1))
              for marker in [*previous_totals, 'INCLUDE']}
    assert {k: totals[k] for k in previous_totals} == previous_totals
    evidence = dict(baseCommit=BASE, branch='codex/ctm-slice-19c', runtime=version,
                    startedAtUTC=started, finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    command=command, exitCode=result.returncode, freshSBCL=True, network='denied by sandbox-exec',
                    regressionChecks=totals, totalLispChecks=sum(totals.values()), importedStatuses=now['statuses'],
                    importedStatusChanges=changes, retainedOriginalCXTMOutputsAndModelObservationsUnchanged=True,
                    originalCorpusAndReferencesUnchanged=True, tmdmAndCxtmSourcesUnchanged=True,
                    documentedInspectionPassed=True, baseLexerCounterprobePassed=True, sourceSHA256=sources,
                    qualification='CTM Include with immediate-parent Document/Wildcard environments, per-level aliases and source-preserving Templates. All twelve originals execute: seven byte-equal positives, three rejections, two explicit mismatches. Two retained DateTime FAILs unchanged; XTM remains NOT-RUN.',
                    artifactsSHA256={str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*'))
                                     if p.is_file() and p.name != 'execution.json'})
    (output / 'execution.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: evidence[k] for k in ['runtime', 'regressionChecks', 'totalLispChecks', 'importedStatuses']}, sort_keys=True))
    print('SLICE-19C-VALIDATION-PASS: fresh offline regression; seven byte-exact Include originals, three rejections, two original mismatches; retained contracts unchanged')


if __name__ == '__main__':
    main()
