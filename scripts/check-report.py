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
slice19c = len(sys.argv) > 2 and sys.argv[2] == '--slice-19c'
slice19b = slice19c or len(sys.argv) > 2 and sys.argv[2] == '--slice-19b'
slice18 = slice19b or len(sys.argv) > 2 and sys.argv[2] == '--slice-18'
slice17b = slice18 or len(sys.argv) > 2 and sys.argv[2] == '--slice-17b'
slice17a = slice17b or len(sys.argv) > 2 and sys.argv[2] == '--slice-17a'
slice16b = slice17a or len(sys.argv) > 2 and sys.argv[2] == '--slice-16b'
slice15 = slice16b or len(sys.argv) > 2 and sys.argv[2] == '--slice-15'
slice14 = slice15 or len(sys.argv) > 2 and sys.argv[2] == '--slice-14'
slice13 = slice14 or len(sys.argv) > 2 and sys.argv[2] == '--slice-13'
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
passes = 204 if slice19c else 194 if slice19b else 187 if slice18 else 120 if slice17b else 107 if slice17a else 106 if slice16b else 93 if slice15 else 71 if slice14 else 67 if slice13 else 64 if slice12a else 62 if slice10 else 59 if slice9 else 49 if slice8 else 42 if slice7 else 36 if slice6 else 29 if slice5 else 25 if slice4 else int(slice1)
assert report['statuses'] == {'pass': passes, 'fail': (4 if slice19c else 2 if slice11 else int(slice10)), 'unsupported': 0, 'not-run': len(cases)-passes-(4 if slice19c else 2 if slice11 else int(slice10))}
assert [c['id'] for c in cases] == sorted(c['id'] for c in cases)
assert len({c['id'] for c in cases}) == len(cases)
tested = [c for c in cases if c['status'] == 'pass']
if slice4:
    positives = [c for c in tested if c['category'] == 'valid']
    assert len(positives) == (176 if slice19c else 169 if slice19b else 165 if slice18 else 108 if slice17b else 95 if slice17a else 94 if slice16b else 83 if slice15 else 62 if slice14 else 59 if slice13 else 56 if slice12a else 54 if slice10 else 51 if slice9 else 46 if slice8 else 39 if slice7 else 33 if slice6 else 28 if slice5 else 24) and all(c['actualOutcome'] == 'cxtm-match' for c in positives)
failed = [c for c in cases if c['status'] == 'fail']
if slice10:
    expected_failed = {'ctm/in/occurrence-datetime2.ctm'}
    if slice11:
        expected_failed.add('ctm/in/occurrence-datetime-timezone2.ctm')
    if slice19c:
        expected_failed.update({'ctm/in/include-template.ctm', 'ctm/in/include-wildcard2.ctm'})
    assert {c['id'] for c in failed} == expected_failed
    assert all(c['actualOutcome'] == 'cxtm-mismatch' and 'normative discrepancy' in c['diagnostics'][0] for c in failed)
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

if slice14:
    c = next(c for c in cases if c['id'] == 'ctm/invalid/variant-no-scope.ctm')
    assert c['status'] == 'pass' and c['actualOutcome'] == 'ctm-rejection'
    assert len(c['diagnostics']) == 1 and 'EXPECTED-VARIANT-SCOPE' in c['diagnostics'][0]

if slice15:
    c = next(c for c in cases if c['id'] == 'ctm/invalid/embedded-topic-global-scope.ctm')
    assert c['status'] == 'pass' and c['actualOutcome'] == 'ctm-rejection'
    assert len(c['diagnostics']) == 1 and 'EMBEDDED-TOPIC-AT-TOP-LEVEL' in c['diagnostics'][0]
    c = next(c for c in cases if c['id'] == 'ctm/invalid/embedded-topic-template.ctm')
    assert (c['status'] == 'pass' and c['actualOutcome'] == 'ctm-rejection') if slice18 else (c['status'] == 'not-run' and c['actualOutcome'] is None)
