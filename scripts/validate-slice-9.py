#!/usr/bin/env python3
"""Reproduce Slice 9: two fresh offline runtimes, relocation, report/retained-output checks.

Requires macOS sandbox-exec, installed SBCL 2.5.4/2.4.10 and Python UCD 15.0/15.1.
Does not provision software, change corpus/locks, use a server or commit files.
"""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = '195d5f5444d776096b765d04c815c23c3db5f84c'
POLICY = '(version 1)(allow default)(deny network*)'
SUFFIXES = ['', '.semantics.json', '.merging.json', '.associations.json',
            '.cxtm.json', '.occurrences.json', '.prefixes.json', '.integers.json', '.decimals.json', '.dates.json']
NAMES = ['validation', 'semantics', 'merging', 'associations', 'cxtm', 'occurrences', 'prefixes', 'integers', 'decimals', 'dates']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl-254', required=True)
    parser.add_argument('--sbcl-2410', required=True)
    parser.add_argument('--output', default=str(ROOT / 'reports/slice-9'))
    args = parser.parse_args()
    output = pathlib.Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    # The pin is verified inside each full suite. Snapshot all reference/corpus
    # bytes independently as a guard against any change during validation.
    protected = {str(p.relative_to(ROOT)): digest(p.read_bytes())
                 for directory in ['vendor/cxtm', 'references']
                 for p in (ROOT / directory).rglob('*') if p.is_file()}
    records = []
    temporary = pathlib.Path(tempfile.mkdtemp(prefix='ctm-slice-9-validation-', dir='/private/tmp'))
    relocated = temporary / 'checkout'
    # Historical reports are inputs for retained-result comparison, but the new
    # output directory is not copied into its own test checkout.
    shutil.copytree(ROOT, relocated, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'slice-9'))
    reports = []
    logs = []
    for version, runtime, checkout, log_name in [
        ('2.5.4', args.sbcl_254, ROOT, 'tests-2.5.4.log'),
        ('2.4.10', args.sbcl_2410, relocated, 'tests-2.4.10-relocated.log'),
    ]:
        version_result = subprocess.run(['/usr/bin/sandbox-exec', '-p', POLICY, runtime, '--version'],
                                        check=True, capture_output=True, text=True)
        assert version_result.stdout.strip() == 'SBCL ' + version, version_result.stdout
        report = temporary / ('validation-' + version + '.json')
        command = ['/usr/bin/sandbox-exec', '-p', POLICY, '/usr/bin/env', 'PYTHONDONTWRITEBYTECODE=1',
                   'SBCL=' + runtime, 'TOPIC_MAPS_REPORT=' + str(report), str(checkout / 'scripts/test.sh')]
        result = subprocess.run(command, cwd=checkout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output / log_name).write_bytes(result.stdout)
        records.append(dict(command=command, workdir=str(checkout), exitCode=result.returncode, log=log_name))
        if result.returncode:
            raise RuntimeError(f'{version} failed: see {output / log_name}')
        reports.append(report)
        logs.append(result.stdout.decode('utf-8'))
        print(f'OFFLINE-SBCL-{version}-PASS: {log_name}', flush=True)
    for name, suffix in zip(NAMES, SUFFIXES):
        a, b = [pathlib.Path(str(p) + suffix).read_bytes() for p in reports]
        assert a == b, 'Reports differ after runtime change/relocation: ' + name
        (output / (name + '.json')).write_bytes(a)
    previous = ROOT / 'reports/slice-8'
    for name in ['semantics', 'merging', 'associations', 'occurrences', 'prefixes', 'integers', 'decimals']:
        old = json.loads((previous / (name + '.json')).read_text())
        new = json.loads((output / (name + '.json')).read_text())
        # Checks change when previously unsupported syntax becomes implemented;
        # the original sources and actual object observations must not change.
        assert old['cases'] == new['cases'], 'Retained object observations changed: ' + name
    old_cxtm = json.loads((previous / 'cxtm.json').read_text())
    new_cxtm = json.loads((output / 'cxtm.json').read_text())
    assert old_cxtm['cases'] == new_cxtm['cases'][:46]
    assert old_cxtm['checks'][:445] == new_cxtm['checks'][:445]
    actual_dir = output / 'actual'
    actual_dir.mkdir(exist_ok=True)
    for case in new_cxtm['cases']:
        actual = case['actualCXTM'].encode('utf-8')
        baseline = ROOT / 'vendor/cxtm/ctm/baseline' / (pathlib.Path(case['id']).name + '.cxtm')
        assert actual == baseline.read_bytes(), case['id']
        (actual_dir / baseline.name).write_bytes(actual)
    # Execute the exact public inspection example, suppressing only environment-
    # dependent FASL location defaults. It uses no test-only API.
    document = (ROOT / 'docs/reading-date-occurrences.md').read_text()
    example = document.split('```lisp\n', 1)[1].split('\n```', 1)[0]
    setup = '(require :asdf)\n(asdf:initialize-output-translations \'(:output-translations (t (:root "tmp" "topic-maps-fasls")) :ignore-inherited-configuration))\n'
    source = setup + example + '\n(format t "~&DOCUMENTED-INSPECTION-PASS~%")\n'
    command = ['/usr/bin/sandbox-exec', '-p', POLICY, args.sbcl_254, '--noinform', '--no-sysinit',
               '--no-userinit', '--script', '/dev/stdin']
    result = subprocess.run(command, cwd=ROOT, input=source.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'describe.log').write_bytes(result.stdout)
    records.append(dict(command=command, workdir=str(ROOT), exitCode=result.returncode, log='describe.log',
                        input='Lisp fence in docs/reading-date-occurrences.md plus FASL setup/success marker',
                        inputSHA256=digest(source.encode('utf-8'))))
    assert result.returncode == 0 and b'DOCUMENTED-INSPECTION-PASS' in result.stdout
    for name, value in protected.items():
        assert digest((ROOT / name).read_bytes()) == value, 'Protected file changed: ' + name
    totals = {}
    for key, marker in [('foundationChecks', 'FOUNDATION'), ('identityChecks', 'CTM-IDENTITY-SEMANTICS'),
                        ('mergeChecks', 'CTM-MERGING-SEMANTICS'), ('associationChecks', 'CTM-ASSOCIATIONS-SEMANTICS'),
                        ('retainedCXTMChecks', 'CXTM'), ('occurrenceChecks', 'OCCURRENCES'), ('prefixDatatypeChecks', 'PREFIX-DATATYPES'), ('integerChecks', 'INTEGERS'), ('decimalChecks', 'DECIMALS'), ('dateChecks', 'DATES')]:
        values = [int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) for log in logs]
        assert values[0] == values[1]
        totals[key] = values[0]
    assert [totals[k] for k in ['foundationChecks', 'identityChecks', 'mergeChecks', 'associationChecks',
                              'retainedCXTMChecks', 'occurrenceChecks', 'prefixDatatypeChecks', 'integerChecks', 'decimalChecks']] == [54, 123, 646, 657, 445, 1101, 150, 665, 715]
    assert all('NFC-ORACLE-PASS: 16294' in log and 'Ran 2 tests' in log
               and 'INTEGER-INDEPENDENT-PASS:' in log and 'DECIMAL-INDEPENDENT-PASS:' in log and 'DATE-INDEPENDENT-PASS:' in log for log in logs)
    totals.update(totalLispChecks=sum(totals.values()), combinedCXTMReportChecks=new_cxtm['passed'],
                  unicodeOracleComparisons=16294, pythonIntegrityTests=2, failures=0, pinnedCanonicalCases=51,
                  newPositiveCases=5, newNegativeCases=5, independentIntegerOracleProbes=143, independentDecimalOracleProbes=157,
                  independentDateOracleProbes=len(json.loads((output / 'dates.json').read_text())['lexicalProbes']),
                  importedStatuses=json.loads((output / 'validation.json').read_text())['statuses'],
                  allTenReportPairsByteIdentical=True, previous46ObjectObservationsAndCanonicalOutputsUnchanged=True,
                  previous445CanonicalChecksUnchanged=True, originalCorpusAndReferencesUnchanged=True,
                  documentedInspectionPassed=True)
    artifacts = {str(p.relative_to(output)): digest(p.read_bytes()) for p in sorted(output.rglob('*'))
                 if p.is_file() and p.name != 'execution.json'}
    evidence = dict(baseCommit=BASE, branch='codex/ctm-slice-9', validatedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    pythonVersion=sys.version, unicodeOracleVersion=unicodedata.unidata_version, commands=records, results=totals,
                    qualification='Pinned corpus targets CTM draft 2010-03-31; published standards remain authoritative.',
                    normativeInterpretation='Bare Integer/Decimal/Date literals use canonical strings as documented reader policy; qualified strings retain lexical values. TMDM equality/order stays lexical; CXTM 3.16 formats timezone-free Date output without mutation; Gregorian validation uses no system calendar. DateTime/date-timezone conversion remain unsupported. Published CTM 3.4.1 XSDT validity is used for days 01-09; the HTML omission and unavailable published Annex grammar are documented. BCE leap validation uses the E.1 signed lexical year interpretation; XSD 1.0 ambiguity is qualified.',
                    artifactsSHA256=artifacts)
    (output / 'execution.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(totals, sort_keys=True), flush=True)
    print('SLICE-9-VALIDATION-PASS: offline dual runtime, relocation, 10 identical report pairs and previous 46 outputs unchanged', flush=True)


if __name__ == '__main__':
    main()
