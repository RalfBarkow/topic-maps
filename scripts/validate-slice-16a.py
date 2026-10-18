#!/usr/bin/env python3
"""Record Slice 16A's complete offline fresh-SBCL regression and source evidence."""
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
BASE = '8c13acc6e96ced1b14d8ec733f701ac788911720'
POLICY = '(version 1)(allow default)(deny network*)'
NAMES = ['validation', 'semantics', 'merging', 'associations', 'cxtm', 'occurrences',
         'prefixes', 'integers', 'decimals', 'dates', 'datetimes', 'timezones',
         'typed-names', 'scopes', 'variants', 'references', 'identifiers']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', default=str(ROOT / 'reports/slice-16a'))
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
    with tempfile.TemporaryDirectory(prefix='ctm-slice-16a-validation-') as temp:
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
    old = ROOT / 'reports/slice-15'
    previous = json.loads((old / 'validation.json').read_text())
    now = json.loads((output / 'validation.json').read_text())
    assert now['statuses'] == previous['statuses'] == {'pass': 93, 'fail': 2, 'unsupported': 0, 'not-run': 178}
    assert [(c['id'], c['status'], c['actualOutcome']) for c in now['cases']] == [
        (c['id'], c['status'], c['actualOutcome']) for c in previous['cases']]
    for name in NAMES[1:-1]:
        key = 'lexicalProbes' if name == 'timezones' else 'cases'
        assert json.loads((old / (name + '.json')).read_text())[key] == json.loads(
            (output / (name + '.json')).read_text())[key], name
    identifiers = json.loads((output / 'identifiers.json').read_text())
    actual_dir = output / 'manual-model-actual'
    actual_dir.mkdir(exist_ok=True)
    for example in identifiers['examples']:
        actual = example['actualCXTM'].encode('utf-8')
        assert actual == (ROOT / 'vendor/cxtm' / example['baseline']).read_bytes()
        (actual_dir / (pathlib.Path(example['source']).name + '.cxtm')).write_bytes(actual)
    document = (ROOT / 'docs/reading-item-identifiers.md').read_text()
    example = document.split('```lisp\n', 2)[2].split('\n```', 1)[0]
    inspection = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit',
                                 '--no-userinit', '--script', '/dev/stdin'], input=example.encode(), cwd=ROOT,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'describe.log').write_bytes(inspection.stdout)
    assert inspection.returncode == 0, 'Documented inspection forms failed'
    for path, value in protected.items():
        assert sha(ROOT / path) == value, path
    for path, value in sources.items():
        assert sha(ROOT / path) == value, path
    previous_totals = json.loads((old / 'execution.json').read_text())['regressionChecks']
    totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1))
              for marker in [*previous_totals, 'ITEM-IDENTIFIERS']}
    assert {k: totals[k] for k in previous_totals} == previous_totals
    evidence = dict(baseCommit=BASE, branch='codex/ctm-slice-16a', runtime=version,
                    startedAtUTC=started, finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    command=command, exitCode=result.returncode, freshSBCL=True, network='denied by sandbox-exec',
                    regressionChecks=totals, totalLispChecks=sum(totals.values()), importedStatuses=now['statuses'],
                    importedStatusChanges=[], previous83CXTMOutputsAndAllModelObservationsUnchanged=True,
                    manualXTM2ModelBaselineComparisons=len(identifiers['examples']), xtmDeserializationImplemented=False,
                    originalCorpusAndReferencesUnchanged=True, sourceSHA256=sources, documentedInspectionPassed=True,
                    qualification='Manual TMDM models are not XTM deserialization contracts; the two known DateTime baseline FAILs remain visible.',
                    artifactsSHA256={str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*'))
                                     if p.is_file() and p.name != 'execution.json'})
    (output / 'execution.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: evidence[k] for k in ['runtime', 'regressionChecks', 'totalLispChecks', 'importedStatuses']}, sort_keys=True))
    print('SLICE-16A-VALIDATION-PASS: fresh offline SBCL; retained evidence unchanged; 7 manual model/baseline comparisons')


if __name__ == '__main__':
    main()
