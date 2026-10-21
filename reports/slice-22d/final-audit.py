#!/usr/bin/env python3
"""Audit saved Slice-22D evidence and the exact Git change scope, without tests.
This is artifact/integrity verification; it does not claim a fresh execution.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'reports/slice-22d'
BASE='b5c5ea5cc84dd31104045d032c25880b8bd62839'

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a,cwd=ROOT):return subprocess.check_output(['git',*a],cwd=cwd,text=True).strip()

initial=read(D/'initial-state.json');assert initial['baseCommit']==BASE
assert initial['indexClean'] and initial['worktreeClean']
assert set(initial['trackedFileSHA256'])==set(git('ls-tree','-r','--name-only',BASE).splitlines())
retarget=read(D/'retargetings.json')
expected_tests={'tests/xtm-name-reification.lisp','tests/xtm-names.lisp','tests/xtm-name-item-identities.lisp',
 'tests/xtm-negative-originals.lisp','tests/xtm-variant-uri-data.lisp','tests/xtm-variant-item-identities.lisp',
 'tests/xtm-identity.lisp','tests/xtm-map-reification.lisp','tests/xtm-name-scopes.lisp',
 'tests/xtm-variants.lisp','tests/ctm-xtm-mergemap.lisp'}
assert len(retarget)==11 and {r['file'] for r in retarget}==expected_tests
assert sum(len(r['changedLines']) for r in retarget)==21
allowed=expected_tests|{'src/xtm/reader.lisp','topic-maps.asd'}
protected={p:h for p,h in initial['trackedFileSHA256'].items() if p not in allowed}
assert protected=={p:sha(ROOT/p) for p in protected}
for row in retarget:
 original=subprocess.check_output(['git','show',BASE+':'+row['file']],cwd=ROOT)
 assert hashlib.sha256(original).hexdigest()==row['beforeSHA256']
 assert sha(ROOT/row['file'])==row['finalFileSHA256']
 for line in row['changedLines']:
  assert line['before'] in original.decode() and line['after'] in (ROOT/row['file']).read_text()
changed=set(git('diff','--name-only',BASE).splitlines())
untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
new_allowed={'tests/xtm-resource-datatypes.lisp','scripts/validate-slice-22d.py','docs/slice-22d-xtm-resource-datatypes.md'}
assert all(p in allowed or p in new_allowed or p.startswith('reports/slice-22d/') for p in changed|untracked)
assert {p for p in changed if p.startswith('src/')}=={'src/xtm/reader.lisp'}
ex=read(D/'after/execution.json');runs=read(D/'after/runs.json')
assert ex['acceptancePassed'] and ex['statusesAfter']=={'XTM':{'pass':72,'fail':0,'not-run':52},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':334,'fail':4,'not-run':59}}
assert ex['auditToolSHA256']==sha(ROOT/'scripts/validate-slice-22d.py')
assert len(runs['runs'])==119 and len(ex['runs'])==119
assert all(r['exitCode']==r['expectedExitCode'] and sha(D/'after'/(r['label']+'.log'))==r['logSHA256'] for r in runs['runs'])
assert runs['executionSourcesSHA256']=={p:sha(ROOT/p) for p in runs['executionSourcesSHA256']}
assert runs['rawReportSHA256']=={p:sha(D/'after'/p) for p in runs['rawReportSHA256']}
assert ex['retainedLispChecks']==12100 and ex['standaloneXTMChecks']==2522
assert ex['faultControls']==113 and ex['retainedFaultControls']==108 and ex['newFaultControls']==5
faults=read(D/'after/failure-controls.json');assert len(faults['controls'])==113
assert all(x['expectedASDFFailureObserved'] and not x['faultCountedAsPass'] for x in faults['controls'])
assert all(x['retainedOriginalPASS']==71 for x in faults['controls'] if not x['retained'])
assert all(x['conditionClassesUnchanged'] and x['conditionCodesUnchangedExceptDocumentedEmbeddedXMLRetargeting'] for x in faults['controls'] if x['retained'])
assert ex['retainedNonXTMReportsByteIdentical']==48
for row in read(D/'after/retained-reports.json'):
 assert sha(D/'baseline'/row['report'])==sha(D/'after'/row['report'])==row['sha256']
pre=read(D/'native-preflight.json');prov=read(D/'native-preflight-provenance.json')
assert pre['passed'] and len(pre['checks'])==11 and pre['registeredCases']==0
assert prov['exitCode']==0 and prov['readerUnchangedFromBase'] and not prov['productionChanged']
assert prov['readerSHA256']==initial['trackedFileSHA256']['src/xtm/reader.lisp']
assert datetime.datetime.fromisoformat(prov['finishedAtUTC'])<datetime.datetime.fromisoformat(ex['startedAtUTC'])
xtm=read(D/'after/xtm.json');assert all(c in xtm['checks'] for c in pre['checks'])
assert len(xtm['cases'])==len({c['id'] for c in xtm['cases']})==72
assert xtm['cases'][:71]==read(D/'baseline/xtm.json')['cases']
delta=read(D/'after/diagnostic-changes.json');assert delta['readerObservations']==124 and delta['changed']==1 and delta['unchanged']==123
assert delta['changes'][0]['id']=='xtm2/in/variant-datatype-unknown.xtm'
contract=read(D/'after/original-contract.json');src=ROOT/'vendor/cxtm'/contract['id']
baseline=ROOT/'vendor/cxtm/xtm2/baseline/variant-datatype-unknown.xtm.cxtm';actual=D/'after/actual/variant-datatype-unknown.xtm.cxtm'
assert contract['sourceSHA256']==sha(src) and contract['baselineSHA256']==sha(baseline)==sha(actual)==contract['actualSHA256']
assert src.stat().st_size==contract['sourceBytes']==340 and baseline.stat().st_size==actual.stat().st_size==579
assert contract['condition'] is None and contract['firstDifferentByte'] is None and contract['byteExact']
gap=read(D/'anytype-capability-gap.json');assert gap['validDatatype'] and not gap['implementedInSlice22D'] and gap['plannedSlice']=='22I'
assert gap['actualConditionClass']=='XTM-UNSUPPORTED'
lock=read(ROOT/'references/corpus-lock.json')
for entry in lock['files']:
 p=ROOT/'vendor/cxtm'/entry['path'];assert p.stat().st_size==entry['size'] and sha(p)==entry['sha256']
assert len(lock['files'])==2006 and sum(p.startswith('reports/') for p in protected)==4929
hyperdoc=Path('/Users/rgb/workspace/hyperdoc-dreyeck-ch')
assert git('rev-parse','HEAD',cwd=hyperdoc)==initial['hyperdocHead']
assert git('status','--porcelain=v1',cwd=hyperdoc)==initial['hyperdocStatus']
# Verify that all local Markdown links resolve; external norm URLs were reviewed
# separately and are not fetched by this integrity audit.
doc=ROOT/'docs/slice-22d-xtm-resource-datatypes.md'
links=re.findall(r'\]\(([^)]+)\)',doc.read_text())
for link in links:
 if '://' not in link:
  target=(doc.parent/link).resolve()
  assert target.exists() or target==D/'final-audit.json',link
artifacts={str(p.relative_to(ROOT)):sha(p) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='final-audit.json'}
artifacts.update({p:sha(ROOT/p) for p in sorted(allowed|new_allowed)})
report={'kind':'final-slice-22d-artifact-integrity-audit-not-new-test-run','auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'baseCommit':BASE,'observedHEAD':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),
 'initialIndexAndWorktreeClean':True,'allowedTrackedChanges':sorted(allowed),'changedPathsObserved':sorted(changed),
 'productionChanges':['src/xtm/reader.lisp'],'retargetedTestFiles':11,'retargetedSourceLines':21,
 'nativePreflightBeforeReaderChangeVerified':True,'acceptedExecutionUnmodified':True,'executorControlsVerified':113,
 'originalDiagnosticsVerified':124,'originalDiagnosticChanges':1,'statuses':ex['statusesAfter'],
 'allPrevious71XTMOriginalPASSUnchanged':True,'pinnedCorpusFilesVerified':2006,'historicalReportFilesVerified':4929,
 'protectedBaseFileCount':len(protected),'historicalReportsOriginalsBaselinesLockUnchanged':True,
 'slice22CThirteenDecisionsUnchanged':True,'slice22CTwelveOpenCDecisionsUnchanged':True,
 'anyTypeValidUnimplementedCapabilityPlannedFor':'22I','hyperdocHEAD':initial['hyperdocHead'],'hyperdocStatusUnchanged':True,
 'newDependencyDownloads':0,'persistentImagesTouched':False,'pushOrDeployment':False,
 'artifactSHA256':artifacts,'selfExcludedFromArtifactManifest':True,'acceptancePassed':True}
(D/'final-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['artifactSHA256','changedPathsObserved','allowedTrackedChanges']}))
