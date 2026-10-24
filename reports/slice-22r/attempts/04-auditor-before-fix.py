#!/usr/bin/env python3
"""Reproduce Slice 22R with the existing offline collector; audit against 22Q.
--output must be outside the repository. --audit-only verifies saved execution,
never claims a new test run. No downloads or changes to existing collectors.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'reports/slice-22r'
PRIOR = ROOT / 'reports/slice-22q/after'
BASE = '0cb182ebab1b90dd871048c031612acd9d302678'
ALLOWED = {'src/xml/package.lisp', 'topic-maps.asd', 'tests/xtm-identity.lisp'}
NEW_SOURCES = {'src/xml/resource-c14n.lisp', 'tests/xml-resource-c14n.lisp'}


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def audit(out):
    initial = read(D / 'initial-state.json')
    assert initial['baseCommit'] == BASE and initial['initialIndexAndWorktreeClean']
    protected = {p: h for p, h in initial['trackedFileSHA256'].items() if p not in ALLOWED}
    assert protected == {p: sha(ROOT / p) for p in protected}
    run = read(out / 'runs.json')
    assert len(run['runs']) == 119
    assert all(r['exitCode'] == r['expectedExitCode'] and
               r['network'] == r['repositoryWrites'] == r['hyperdocWrites'] == 'denied' and
               sha(out / (r['label'] + '.log')) == r['logSHA256'] for r in run['runs'])
    assert run['executionSourcesSHA256'] == {p: sha(ROOT / p) for p in run['executionSourcesSHA256']}
    assert run['rawReportSHA256'] == {p: sha(out / p) for p in run['rawReportSHA256']}
    old, new = read(PRIOR / 'xtm.json'), read(out / 'xtm.json')
    for key in old:
        if key != 'checks':
            assert old[key] == new[key], key
    assert [c for c in new['checks'] if c in set(old['checks'])] == old['checks']
    additions = [c for c in new['checks'] if c not in set(old['checks'])]
    assert additions and all(c.startswith(('resource-c14n:', 'resource-c14n-native:',
                                          'resource-c14n-security:', 'resource-c14n-api:')) for c in additions)
    labels = re.findall(r'^XTM-CHECK-PASS (.+)$', (out / 'xtm.log').read_text(), re.M)
    assert labels == new['checks'] and len(labels) == len(set(labels))
    x = new['resourceDataC14N']
    assert x['executed'] and x['qualifiedForClosedXTMNodeSet']
    assert not x['generalXPathC14N'] and not x['XTMReaderIntegration'] and x['corpusRegistrationsAdded'] == 0
    rows = {r['id']: r for r in x['probes']}
    assert len(rows) == len(x['probes'])
    # Every existing independent 22Q oracle and ORIGINAL input byte is reused.
    for r in old['c14nPreflight']['probes']:
        newrow = rows[r['id']]
        assert newrow['inputHex'] == r['inputHex'] and newrow['expectedHex'] == r['expectedHex']
    official = [r for r in rows.values() if r['id'].startswith('w3c-')]
    assert len(official) == 6
    assert sum(not r['publicXTMProjection'] for r in official) == 3
    for r in rows.values():
        actual, expected = bytes.fromhex(r['actualHex']), bytes.fromhex(r['expectedHex'])
        assert actual == expected == r['expectedXML'].encode('utf-8') == r['actualXML'].encode('utf-8')
        assert len(actual) == r['actualBytes'] == r['expectedBytes']
        assert r['firstDifferentByte'] is None and r['byteIdentical'] and r['repeatedPure']
    public = {r['id']: r for r in rows.values() if r['publicXTMProjection']}
    assert set(public) == {r['id'] for r in x['nativeValues']}
    for r in x['nativeValues']:
        assert r['value'] == r['occurrenceValue'] == r['variantValue'] == public[r['id']]['actualXML']
        assert r['datatype'] == 'http://www.w3.org/2001/XMLSchema#anyType' and r['topicCount'] == 5
        assert r['canonicalReferencesEQ'] and r['repeatedCXTMPure'] and not r['readerIntegration']
    assert x['controls'] and all(r['condition'] for r in x['controls'])
    # Historical candidate still has the same eight failures, not reclassified.
    assert new['c14nPreflight'] == old['c14nPreflight']
    assert sum(r['normativeComparison'] == 'BYTE-DIFFERENCE' for r in new['c14nPreflight']['probes']) == 8
    assert read(PRIOR / 'after-diagnostics.json') == read(out / 'after-diagnostics.json')
    assert len(read(out / 'after-diagnostics.json')) == 124
    retained = []
    for p in sorted((out / 'retained').rglob('*')):
        if p.is_file():
            rel = p.relative_to(out)
            assert p.read_bytes() == (PRIOR / rel).read_bytes(), str(rel)
            retained.append({'report': str(rel), 'SHA256': sha(p)})
    controls = []
    for r in run['runs']:
        if '-control-' not in r['label']:
            continue
        name = r['label'] + '.json'
        a, b = read(PRIOR / name), read(out / name)
        assert r['exitCode'] == 1
        for key in a:
            assert a[key] == b[key], (name, key)
        assert not b['resourceDataC14N']['executed'] and not b['resourceDataC14N']['qualifiedForClosedXTMNodeSet']
        assert not b['resourceDataC14N']['probes'] and not b['resourceDataC14N']['nativeValues']
        controls.append({'label': r['label'], 'expectedExitCode': 1, 'previousFieldsUnchanged': True,
                         'retargeted': False, 'newTestsNotClaimedExecuted': True})
    assert len(controls) == 113
    prior = read(PRIOR / 'execution.json')
    regression = (out / 'regression.log').read_text()
    for marker, count in prior['stageChecks'].items():
        assert int(re.search(r'(?m)^' + marker + r'-PASS: (\d+)', regression).group(1)) == count
    assert 'PASS: 12100' in regression and 'Ran 2 tests' in regression and 'NFC-ORACLE-PASS: 16294' in regression
    assert 'CXML-SUMMARY 146 PASS 0 FAIL' in (out / 'xml.log').read_text()
    assert read(out / 'ctm.validation.json')['statuses'] == {'pass': 262, 'fail': 4, 'unsupported': 0, 'not-run': 7}
    assert new['statuses'] == {'pass': 121, 'fail': 0, 'unsupported': 0, 'not-run': 0}
    assert new['otherCorpusInputs'] == {'positiveUnexecuted': 3, 'negativeUnregisteredUnexecuted': 0}
    assert new['cases'] == old['cases']
    assert protected == {p: sha(ROOT / p) for p in protected}
    summary = [{'id': r['id'], 'expectedBytes': r['expectedBytes'], 'actualBytes': r['actualBytes'],
                'firstDifferentByte': None, 'byteIdentical': True, 'origin': r['origin']} for r in rows.values()]
    save(out / 'comparison-summary.json', {'kind': 'XTM-node-set-C14N-1.0-closed-profile-qualification',
         'probes': summary, 'unchanged22QVectors': len(old['c14nPreflight']['probes']),
         'independentW3CVectors': 3, 'additionalPublicWrappersOfW3CVectors': 3,
         'publicValueAndNativeModelRows': len(public), 'oldCandidateDifferencesPreserved': 8})
    save(out / 'failure-controls-audit.json', controls)
    save(out / 'retained-reports.json', retained)
    save(out / 'diagnostic-changes.json', {'observations': 124, 'changed': 0, 'unchanged': 124,
         'changes': [], 'newOriginalRegistrations': 0, 'retargetings': []})
    save(out / 'integrity.json', {'protectedBaseFilesSHA256': protected,
         'protectedBaseFileCount': len(protected),
         'pinnedCorpusFilesVerified': sum(p.startswith('vendor/cxtm/') for p in protected),
         'historicalReportFilesVerified': sum(p.startswith('reports/') for p in protected),
         'allowedTrackedChanges': sorted(ALLOWED), 'newExecutionSources': sorted(NEW_SOURCES),
         'originalXMLByteBoundaryUnchanged': True, 'allTMDMCTMXTMCXTMSourcesUnchanged': True})
    save(out / 'execution.json', {'kind': 'slice-22r-closed-XTM-C14N-infrastructure-NOT-reader-integration',
         'baseCommit': BASE, 'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
         'runtime': 'SBCL 2.5.4', 'startedAtUTC': run['startedAtUTC'], 'finishedAtUTC': run['finishedAtUTC'],
         'auditedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'collector': 'scripts/validate-slice-22d.py::collect (unchanged)', 'auditToolSHA256': sha(Path(__file__)),
         'runs': run['runs'], 'standaloneXTMChecks': len(labels), 'retainedStandaloneXTMChecks': len(old['checks']),
         'newInfrastructureChecks': len(additions), 'retainedLispChecks': prior['retainedLispChecks'],
         'stageChecks': prior['stageChecks'], 'equivalenceChecks': prior['equivalenceChecks'],
         'equivalenceReaderPairs': prior['equivalenceReaderPairs'], 'faultControls': len(controls),
         'all124OriginalDiagnosesUnchanged': True, 'retainedReportsByteIdentical': len(retained),
         'statusesBefore': prior['statusesAfter'], 'statusesAfter': prior['statusesAfter'],
         'originalRegistrationsAdded': 0, 'xmlQualificationChecks': prior['xmlQualificationChecks'],
         'pythonUnitTests': prior['pythonUnitTests'], 'nfcOracleComparisons': prior['nfcOracleComparisons'],
         'qualifiedScope': 'XTM 4.16.3 descendant set; C14N 1.0; existing closed XML profile',
         'generalXPathC14N': False, 'XTMReaderIntegration': False, 'newDependencies': 0,
         'newNativeValueRows': len(public), 'acceptancePassed': True})
    print(json.dumps({'acceptancePassed': True, 'XTMChecks': len(labels), 'newChecks': len(additions),
          'positiveByteRows': len(rows), 'nativeValueRows': len(public), 'faultControls': len(controls),
          'statusesUnchanged': prior['statusesAfter']}), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--audit-only', action='store_true')
    a = ap.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=True)
    if not a.audit_only:
        spec = importlib.util.spec_from_file_location('oldcollector', ROOT / 'scripts/validate-slice-22d.py')
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        m.EXECUTION_FILES = {str(p.relative_to(ROOT)) for folder in ['src', 'tests']
                             for p in (ROOT / folder).rglob('*.lisp')} | {
                             'topic-maps.asd', 'scripts/validate-slice-22d.py',
                             'reports/slice-22d/failure-controls.lisp', 'reports/slice-22r/reproduce.py'}
        m.collect(out, ROOT / 'reports/slice-22d/baseline')
    audit(out)


if __name__ == '__main__':
    main()
