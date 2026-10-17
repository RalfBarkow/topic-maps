#!/usr/bin/env python3
"""Reproduce Slice 11: two fresh offline runtimes, relocation, report/retained-output checks.

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
BASE = '8741d155d948c7317945eee423a977940cad995e'
POLICY = '(version 1)(allow default)(deny network*)'
SUFFIXES = ['', '.semantics.json', '.merging.json', '.associations.json',
            '.cxtm.json', '.occurrences.json', '.prefixes.json', '.integers.json', '.decimals.json', '.dates.json', '.datetimes.json', '.timezones.json']
NAMES = ['validation', 'semantics', 'merging', 'associations', 'cxtm', 'occurrences', 'prefixes', 'integers', 'decimals', 'dates', 'datetimes', 'timezones']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sbcl-254', required=True)
    parser.add_argument('--sbcl-2410', required=True)
    parser.add_argument('--output', default=str(ROOT / 'reports/slice-11'))
    args = parser.parse_args()
    output = pathlib.Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    # The pin is verified inside each full suite. Snapshot all reference/corpus
    # bytes independently as a guard against any change during validation.
    protected = {str(p.relative_to(ROOT)): digest(p.read_bytes())
                 for directory in ['vendor/cxtm', 'references']
                 for p in (ROOT / directory).rglob('*') if p.is_file()}
    records = []
    temporary = pathlib.Path(tempfile.mkdtemp(prefix='ctm-slice-11-validation-', dir='/private/tmp'))
    relocated = temporary / 'checkout'
    # Historical reports are inputs for retained-result comparison, but the new
    # output directory is not copied into its own test checkout.
    shutil.copytree(ROOT, relocated, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'slice-11'))
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
    previous = ROOT / 'reports/slice-10'
    for name in ['semantics', 'merging', 'associations', 'occurrences', 'prefixes', 'integers', 'decimals', 'dates']:
        old = json.loads((previous / (name + '.json')).read_text())
        new = json.loads((output / (name + '.json')).read_text())
        # Checks change when previously unsupported syntax becomes implemented;
        # the original sources and actual object observations must not change.
        assert old['cases'] == new['cases'], 'Retained object observations changed: ' + name
    old_cxtm = json.loads((previous / 'cxtm.json').read_text())
    new_cxtm = json.loads((output / 'cxtm.json').read_text())
    assert old_cxtm['cases'] == new_cxtm['cases'][:55]
    old_datetime = json.loads((previous / 'datetimes.json').read_text())
    new_datetime = json.loads((output / 'datetimes.json').read_text())
    assert old_datetime['cases'] == new_datetime['cases'][:4]
    # Every previously passing imported contract remains PASS; the only status
    # transition is the newly executed timezone2 baseline mismatch.
    old_imported = json.loads((previous / 'validation.json').read_text())
    new_imported = json.loads((output / 'validation.json').read_text())
    transitions = []
    for old, new in zip(old_imported['cases'], new_imported['cases']):
        assert old['id'] == new['id']
        if old['status'] == 'pass': assert new['status'] == 'pass'
        if old['status'] != new['status']: transitions.append((old['id'], old['status'], new['status']))
    assert transitions == [('ctm/in/occurrence-datetime-timezone2.ctm', 'not-run', 'fail')]
    assert new_cxtm['contractCounts'] == {'pass': 54, 'fail': 2}
    assert old_cxtm['checks'][:445] == new_cxtm['checks'][:445]
    actual_dir = output / 'actual'
    actual_dir.mkdir(exist_ok=True)
    for case in new_cxtm['cases']:
        actual = case['actualCXTM'].encode('utf-8')
        baseline = ROOT / 'vendor/cxtm/ctm/baseline' / (pathlib.Path(case['id']).name + '.cxtm')
        if case['id'] in ['ctm/in/occurrence-datetime2.ctm', 'ctm/in/occurrence-datetime-timezone2.ctm']:
            assert actual != baseline.read_bytes() and case['status'] == 'fail'
        else:
            assert actual == baseline.read_bytes() and case['status'] == 'pass', case['id']
        (actual_dir / baseline.name).write_bytes(actual)
    # Execute the exact public inspection example, suppressing only environment-
    # dependent FASL location defaults. It uses no test-only API.
    document = (ROOT / 'docs/reading-datetime-timezones.md').read_text()
    example = document.split('```lisp\n', 1)[1].split('\n```', 1)[0]
    setup = '(require :asdf)\n(asdf:initialize-output-translations \'(:output-translations (t (:root "tmp" "topic-maps-fasls")) :ignore-inherited-configuration))\n'
    source = setup + example + '\n(format t "~&DOCUMENTED-INSPECTION-PASS~%")\n'
    command = ['/usr/bin/sandbox-exec', '-p', POLICY, args.sbcl_254, '--noinform', '--no-sysinit',
               '--no-userinit', '--script', '/dev/stdin']
    result = subprocess.run(command, cwd=ROOT, input=source.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'describe.log').write_bytes(result.stdout)
    records.append(dict(command=command, workdir=str(ROOT), exitCode=result.returncode, log='describe.log',
                        input='Lisp fence in docs/reading-datetime-timezones.md plus FASL setup/success marker',
                        inputSHA256=digest(source.encode('utf-8'))))
    assert result.returncode == 0 and b'DOCUMENTED-INSPECTION-PASS' in result.stdout
    for name, value in protected.items():
        assert digest((ROOT / name).read_bytes()) == value, 'Protected file changed: ' + name
    totals = {}
    for key, marker in [('foundationChecks', 'FOUNDATION'), ('identityChecks', 'CTM-IDENTITY-SEMANTICS'),
                        ('mergeChecks', 'CTM-MERGING-SEMANTICS'), ('associationChecks', 'CTM-ASSOCIATIONS-SEMANTICS'),
                        ('retainedCXTMChecks', 'CXTM'), ('occurrenceChecks', 'OCCURRENCES'), ('prefixDatatypeChecks', 'PREFIX-DATATYPES'), ('integerChecks', 'INTEGERS'), ('decimalChecks', 'DECIMALS'), ('dateChecks', 'DATES'), ('datetimeChecks', 'DATETIMES'), ('timezoneChecks', 'TIMEZONES')]:
        values = [int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', log).group(1)) for log in logs]
        assert values[0] == values[1]
        totals[key] = values[0]
    assert [totals[k] for k in ['foundationChecks', 'identityChecks', 'mergeChecks', 'associationChecks',
                              'retainedCXTMChecks', 'occurrenceChecks', 'prefixDatatypeChecks', 'integerChecks', 'decimalChecks', 'dateChecks']] == [54, 123, 646, 657, 445, 1101, 150, 665, 715, 1806]
    assert all('NFC-ORACLE-PASS: 16294' in log and 'Ran 2 tests' in log
               and 'INTEGER-INDEPENDENT-PASS:' in log and 'DECIMAL-INDEPENDENT-PASS:' in log and 'DATE-INDEPENDENT-PASS:' in log and 'DATETIME-INDEPENDENT-PASS:' in log and 'TIMEZONE-INDEPENDENT-PASS:' in log for log in logs)
    totals.update(totalLispChecks=sum(totals.values()), combinedCXTMReportChecks=new_cxtm['passed'],
                  unicodeOracleComparisons=16294, pythonIntegrityTests=2, regressionAssertionFailures=0, pinnedCanonicalCases=54, executedCanonicalCases=56, knownBaselineMismatches=2, documentedNormativeDiscrepancies=2, canonicalContractCounts=new_cxtm['contractCounts'],
                  newPositivePasses=0, newlyExecutedPositiveMismatches=1, newNegativeCases=0, independentIntegerOracleProbes=143, independentDecimalOracleProbes=157,
                  independentDateOracleProbes=len(json.loads((output / 'dates.json').read_text())['lexicalProbes']),
                  independentDateTimeOracleProbes=len(json.loads((output / 'datetimes.json').read_text())['lexicalProbes']),
                  importedStatuses=json.loads((output / 'validation.json').read_text())['statuses'],
                  independentTimezoneOracleProbes=len(json.loads((output / 'timezones.json').read_text())['lexicalProbes']),
                  allTwelveReportPairsByteIdentical=True, previous55CanonicalOutputsAnd54PassesUnchanged=True,
                  previousFourDatetimeObservationsUnchanged=True,
                  previous445CanonicalChecksUnchanged=True, originalCorpusAndReferencesUnchanged=True,
                  documentedInspectionPassed=True)
    artifacts = {str(p.relative_to(output)): digest(p.read_bytes()) for p in sorted(output.rglob('*'))
                 if p.is_file() and p.name != 'execution.json'}
    evidence = dict(baseCommit=BASE, branch='codex/ctm-slice-11', validatedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    pythonVersion=sys.version, unicodeOracleVersion=unicodedata.unidata_version, commands=records, results=totals,
                    qualification='Pinned corpus targets CTM draft 2010-03-31; published standards remain authoritative.',
                    normativeInterpretation='XSD UTC conversion implemented with exact calendar/fraction arithmetic. Original timezone2 now executes as a known normative baseline FAIL; datetime2 FAIL unchanged. TMDM values/equality/order remain lexical; qualified strings and retained handles unchanged. Nonzero-offset BCE day rollover and leap seconds are specific unsupported contexts; Date timezone canonicalization excluded.',
                    artifactsSHA256=artifacts)
    (output / 'execution.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(totals, sort_keys=True), flush=True)
    print('SLICE-11-VALIDATION-PASS: offline dual runtime, relocation, 12 identical report pairs; previous 55 outputs unchanged; two known normative baseline FAILs', flush=True)


if __name__ == '__main__':
    main()
