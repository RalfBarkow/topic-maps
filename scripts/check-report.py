#!/usr/bin/env python3
"""Check the Lisp-generated JSON with an independent standard-library decoder."""
import json
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
lock = json.loads((root / 'references/corpus-lock.json').read_text())
assert report['repository'] == lock['repository'] and report['commit'] == lock['commit']
assert report['qualification'] == lock['draftQualification']
assert report['counts'] == lock['ctmCounts']
slice13 = len(sys.argv) > 2 and sys.argv[2] == '--slice-13'
slice12a = slice13 or len(sys.argv) > 2 and sys.argv[2] == '--slice-12a'
slice11 = slice12a or len(sys.argv) > 2 and sys.argv[2] == '--slice-11'
slice10 = slice11 or len(sys.argv) > 2 and sys.argv[2] == '--slice-10'
slice9 = slice10 or len(sys.argv) > 2 and sys.argv[2] == '--slice-9'
slice8 = slice9 or len(sys.argv) > 2 and sys.argv[2] == '--slice-8'
slice7 = slice8 or len(sys.argv) > 2 and sys.argv[2] == '--slice-7'
slice6 = slice7 or len(sys.argv) > 2 and sys.argv[2] == '--slice-6'
slice5 = slice6 or len(sys.argv) > 2 and sys.argv[2] == '--slice-5'
slice4 = slice5 or len(sys.argv) > 2 and sys.argv[2] == '--slice-4'
slice1 = slice4 or (len(sys.argv) > 2 and sys.argv[2] == '--slice-1')
assert report['implemented'] == dict(ctmParsing=slice1, tmdmDeserialization=slice1, cxtmCanonicalization=slice4)
assert report['countsMatchPin'] is True
assert report['correspondence'] == dict(ok=True, missingInputs=[], missingBaselines=[], unmatchedBaselines=[], duplicateIDs=[])
cases = report['cases']
assert len(cases) == report['counts']['valid'] + report['counts']['invalid']
passes = 67 if slice13 else 64 if slice12a else 62 if slice10 else 59 if slice9 else 49 if slice8 else 42 if slice7 else 36 if slice6 else 29 if slice5 else 25 if slice4 else int(slice1)
assert report['statuses'] == {'pass': passes, 'fail': (2 if slice11 else int(slice10)), 'unsupported': 0, 'not-run': len(cases)-passes-(2 if slice11 else int(slice10))}
assert [c['id'] for c in cases] == sorted(c['id'] for c in cases)
assert len({c['id'] for c in cases}) == len(cases)
tested = [c for c in cases if c['status'] == 'pass']
if slice4:
    positives = [c for c in tested if c['category'] == 'valid']
    assert len(positives) == (59 if slice13 else 56 if slice12a else 54 if slice10 else 51 if slice9 else 46 if slice8 else 39 if slice7 else 33 if slice6 else 28 if slice5 else 24) and all(c['actualOutcome'] == 'cxtm-match' for c in positives)
failed = [c for c in cases if c['status'] == 'fail']
if slice10:
    assert len(failed) == (2 if slice11 else 1) and {c['id'] for c in failed} == ({'ctm/in/occurrence-datetime2.ctm', 'ctm/in/occurrence-datetime-timezone2.ctm'} if slice11 else {'ctm/in/occurrence-datetime2.ctm'})
    assert failed[0]['actualOutcome'] == 'cxtm-mismatch' and 'normative discrepancy' in failed[0]['diagnostics'][0]
    offset = next(c for c in cases if c['id'] == 'ctm/in/occurrence-datetime-timezone2.ctm')
    assert offset['status'] == ('fail' if slice11 else 'not-run')
else:
    assert not failed
untested = [c for c in cases if c['status'] == 'not-run']
assert all(c['status'] == 'not-run' and c['actualOutcome'] is None and c['diagnostics'] == [] for c in untested)
if slice1:
    negative = next(c for c in cases if c['id'] == 'ctm/invalid/prefix-undefined.ctm')
    assert negative['status'] == 'pass' and negative['actualOutcome'] == 'ctm-rejection'
    assert len(negative['diagnostics']) == 1 and 'UNDEFINED-PREFIX' in negative['diagnostics'][0]
assert all(c['documentIRI'] == 'https://ctm-tests.example.invalid/' + lock['commit'] + '/' + c['id'] for c in cases)
assert sum(c['category'] == 'valid' for c in cases) == report['counts']['valid']
assert sum(c['category'] == 'invalid' for c in cases) == report['counts']['invalid']
assert all(c['expectedOutcome'] == 'ctm-rejection' and c['expectedCXTM'] is None for c in cases if c['category'] == 'invalid')
assert all(c['expectedOutcome'] == 'cxtm-equal' and c['expectedCXTM'].endswith('.ctm.cxtm') for c in cases if c['category'] == 'valid')
assert all((root/'vendor/cxtm'/c['sourcePathname']).is_file() for c in cases)
assert all((root/'vendor/cxtm'/c['expectedCXTM']).is_file() for c in cases if c['expectedCXTM'])
assert len(report['auxiliaryResources']) == report['counts']['auxiliary']
assert len(report['baselines']) == report['counts']['baselines']
assert len(report['infrastructureChecks']) == len(set(report['infrastructureChecks'])) > 0
print('REPORT-JSON-PASS: deterministic schema, draft qualification, case contracts and only warranted imported status changes')

if slice6:
    for name, reason in [('prefix-collision', 'PREFIX-COLLISION'), ('prefix-undefined2', 'UNDEFINED-PREFIX')]:
        c = next(c for c in cases if c['id'] == f'ctm/invalid/{name}.ctm')
        assert c['status'] == 'pass' and c['actualOutcome'] == 'ctm-rejection'
        assert len(c['diagnostics']) == 1 and reason in c['diagnostics'][0]

if slice9:
    for name, reason in [('date-invalid-day', 'INVALID-DATE-DAY'), ('date-invalid-month', 'INVALID-DATE-MONTH'),
                         ('date-invalid-year', 'INVALID-DATE-YEAR'), ('date-invalid-year2', 'INVALID-DATE-YEAR'), ('date-invalid-year3', 'INVALID-DATE-YEAR')]:
        c = next(c for c in cases if c['id'] == f'ctm/invalid/{name}.ctm')
        assert c['status'] == 'pass' and c['actualOutcome'] == 'ctm-rejection'
        assert len(c['diagnostics']) == 1 and reason in c['diagnostics'][0]
