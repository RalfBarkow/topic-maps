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
slice1 = len(sys.argv) > 2 and sys.argv[2] == '--slice-1'
assert report['implemented'] == dict(ctmParsing=slice1, tmdmDeserialization=slice1, cxtmCanonicalization=False)
assert report['countsMatchPin'] is True
assert report['correspondence'] == dict(ok=True, missingInputs=[], missingBaselines=[], unmatchedBaselines=[], duplicateIDs=[])
cases = report['cases']
assert len(cases) == report['counts']['valid'] + report['counts']['invalid']
assert report['statuses'] == {'pass': int(slice1), 'fail': 0, 'unsupported': 0, 'not-run': len(cases)-int(slice1)}
assert [c['id'] for c in cases] == sorted(c['id'] for c in cases)
assert len({c['id'] for c in cases}) == len(cases)
untested = [c for c in cases if not (slice1 and c['id'] == 'ctm/invalid/prefix-undefined.ctm')]
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
