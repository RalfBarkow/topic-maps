#!/usr/bin/env python3
"""Record one full offline fresh-SBCL run. No relocation or cache management."""
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
BASE = '6a2f8446afca0915882f0d4a06cb891ccfcdc96d'
POLICY = '(version 1)(allow default)(deny network*)'
NAMES = ['validation', 'semantics', 'merging', 'associations', 'cxtm', 'occurrences',
         'prefixes', 'integers', 'decimals', 'dates', 'datetimes', 'timezones', 'typed-names']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl', default=os.environ.get('SBCL', 'sbcl'))
    parser.add_argument('--output', default=str(ROOT / 'reports/slice-12a'))
    args = parser.parse_args()
    runtime = shutil.which(args.sbcl)
    if runtime is None:
        raise RuntimeError('SBCL executable not found: ' + args.sbcl)
    output = pathlib.Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    protected = {str(p.relative_to(ROOT)): sha(p) for directory in ['vendor/cxtm', 'references']
                 for p in (ROOT / directory).rglob('*') if p.is_file()}
    sources = {str(p.relative_to(ROOT)): sha(p) for directory in ['src', 'tests', 'scripts']
               for p in (ROOT / directory).rglob('*') if p.is_file() and
               '__pycache__' not in p.parts and p.suffix in ['.lisp', '.py', '.sh']}
    sources['topic-maps.asd'] = sha(ROOT / 'topic-maps.asd')
    version = subprocess.check_output([runtime, '--version'], text=True).strip()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix='ctm-slice-12a-validation-') as temp:
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
    old = ROOT / 'reports/slice-11'
    for name in ['semantics', 'merging', 'associations', 'occurrences', 'prefixes', 'integers', 'decimals', 'dates', 'datetimes']:
        assert json.loads((old / (name + '.json')).read_text())['cases'] == json.loads((output / (name + '.json')).read_text())['cases'], name
    previous = json.loads((old / 'cxtm.json').read_text())
    current = json.loads((output / 'cxtm.json').read_text())
    assert previous['cases'] == current['cases'][:56]
    original = json.loads((old / 'validation.json').read_text())
    now = json.loads((output / 'validation.json').read_text())
    transitions = [(a['id'], a['status'], b['status']) for a, b in zip(original['cases'], now['cases']) if a['status'] != b['status']]
    assert transitions == [('ctm/in/name-type.ctm', 'not-run', 'pass'), ('ctm/in/name2.ctm', 'not-run', 'pass')], transitions
    assert now['statuses'] == {'pass': 64, 'fail': 2, 'unsupported': 0, 'not-run': 207}
    assert current['contractCounts'] == {'pass': 56, 'fail': 2}
    actual_dir = output / 'actual'
    actual_dir.mkdir(exist_ok=True)
    for case in current['cases']:
        if case['id'] in ['ctm/in/' + n + '.ctm' for n in ['name', 'name2', 'name-type', 'name-duplicate']]:
            (actual_dir / (pathlib.Path(case['id']).name + '.cxtm')).write_bytes(case['actualCXTM'].encode('utf-8'))
    document = (ROOT / 'docs/reading-typed-topic-names.md').read_text()
    example = document.split('```lisp\n', 1)[1].split('\n```', 1)[0]
    inspection = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--noinform', '--no-sysinit',
                                 '--no-userinit', '--script', '/dev/stdin'], input=example.encode(), cwd=ROOT,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'describe.log').write_bytes(inspection.stdout)
    assert inspection.returncode == 0
    for path, value in protected.items():
        assert sha(ROOT / path) == value, path
    for path, value in sources.items():
        assert sha(ROOT / path) == value, path
    markers = ['FOUNDATION', 'CTM-IDENTITY-SEMANTICS', 'CTM-MERGING-SEMANTICS', 'CTM-ASSOCIATIONS-SEMANTICS',
               'CXTM', 'OCCURRENCES', 'PREFIX-DATATYPES', 'INTEGERS', 'DECIMALS', 'DATES', 'DATETIMES', 'TIMEZONES', 'TYPED-NAMES']
    totals = {marker: int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) for marker in markers}
    evidence = dict(baseCommit=BASE, branch='codex/ctm-slice-12a', runtime=version,
                    startedAtUTC=started, finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    command=command, exitCode=result.returncode, freshSBCL=True, network='denied by sandbox-exec',
                    regressionChecks=totals, totalLispChecks=sum(totals.values()), importedStatuses=now['statuses'],
                    transitions=transitions, previous56CXTMOutputsUnchanged=True, originalCorpusAndReferencesUnchanged=True,
                    sourceSHA256=sources, documentedInspectionPassed=True,
                    qualification='Pinned CTM draft-era corpus; regression assertion PASS does not erase the two normative baseline FAILs.',
                    artifactsSHA256={str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*'))
                                     if p.is_file() and p.name != 'execution.json'})
    (output / 'execution.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: evidence[k] for k in ['runtime', 'regressionChecks', 'totalLispChecks', 'importedStatuses', 'transitions']}, sort_keys=True))
    print('SLICE-12A-VALIDATION-PASS: fresh offline SBCL; retained outputs unchanged; four original Name comparisons')


if __name__ == '__main__':
    main()
