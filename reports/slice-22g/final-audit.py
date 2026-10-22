#!/usr/bin/env python3
"""Audit committed-candidate Slice 22G scope and saved execution; starts no tests."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import re
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'reports/slice-22g';A=D/'after';P=ROOT/'reports/slice-22f/after'
BASE='b50a9d7950c5407b2ec02e1caccd76f73018b45f'
ALLOWED={'src/xtm/reader.lisp','topic-maps.asd','tests/xtm-identity.lisp','tests/xtm-name-scopes.lisp','tests/xtm-resource-datatypes.lisp','tests/xtm-mergemap.lisp'}
NEW={'tests/xtm-occurrences.lisp','scripts/validate-slice-22g.py','docs/slice-22g-xtm-occurrence-core.md'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
s=read(D/'initial-state.json');assert s['baseCommit']==BASE and s['initialIndexAndWorktreeClean']
assert set(s['trackedFileSHA256'])==set(git('ls-tree','-r','--name-only',BASE).splitlines())
protected={p:h for p,h in s['trackedFileSHA256'].items() if p not in ALLOWED}
assert protected=={p:sha(ROOT/p) for p in protected}
changed=set(git('diff','--name-only',BASE).splitlines());untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
assert all(p in ALLOWED|NEW or p.startswith('reports/slice-22g/') for p in changed|untracked)
assert {p for p in changed if p.startswith('src/')}=={'src/xtm/reader.lisp'}
e=read(A/'execution.json');runs=read(A/'runs.json');assert e['acceptancePassed'] and e['auditToolSHA256']==sha(ROOT/'scripts/validate-slice-22g.py')
assert len(runs['runs'])==119 and all(r['exitCode']==r['expectedExitCode'] and r['freshProcess'] and r['network']==r['repositoryWrites']==r['hyperdocWrites']=='denied' and sha(A/(r['label']+'.log'))==r['logSHA256'] for r in runs['runs'])
assert runs['executionSourcesSHA256']=={p:sha(ROOT/p) for p in runs['executionSourcesSHA256']}
assert runs['rawReportSHA256']=={p:sha(A/p) for p in runs['rawReportSHA256']}
assert e['standaloneXTMChecks']==2869 and e['newXTMChecks']==165 and e['retainedStandaloneXTMChecks']==2704 and e['retainedLispChecks']==12100
assert e['statusesAfter']=={'XTM':{'pass':83,'fail':0,'not-run':41},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':345,'fail':4,'not-run':48}}
old=read(P/'xtm.json');new=read(A/'xtm.json');assert old['cases']==new['cases'][:72]
assert len(new['cases'])==len({r['id'] for r in new['cases']})==83
assert [c for c in new['checks'] if c in set(old['checks'])]==old['checks']
assert len(new['checks'])==len(set(new['checks']))==2869
assert re.findall(r'^XTM-CHECK-PASS (.+)$',(A/'xtm.log').read_text(),re.M)==new['checks']
originals=read(A/'original-contracts.json');inputs=read(D/'originals-before.json');assert len(originals)==len(inputs)==11
assert {r['id'] for r in originals}=={r['id'] for r in new['cases'][72:]}=={r['id'] for r in inputs}
for o in originals:
 p=ROOT/'vendor/cxtm'/o['id'];b=ROOT/'vendor/cxtm/xtm2/baseline'/(p.name+'.cxtm');actual=A/'actual'/(p.name+'.cxtm')
 assert sha(p)==o['sourceSHA256'] and p.read_bytes()==bytes.fromhex(o['sourceHex'])
 assert actual.read_bytes()==b.read_bytes()==o['actualCXTM'].encode()==o['expectedCXTM'].encode()
 assert sha(actual)==sha(b)==o['actualSHA256']==o['baselineSHA256']
 assert o['status']=='pass' and o['condition'] is None and o['firstDifferentByte'] is None and o['completeByteExact']
 assert o['qualifiedParserCalls']==1 and o['originalOctetsEQ'] and o['oldHandlesCanonicalAndLive'] and o['model']['canonicalOccurrenceReferencesEQ']
 assert o['actualBytes']==o['expectedBytes']==actual.stat().st_size
controls=read(A/'native-and-negative-controls.json');assert controls['positiveControls']==19 and controls['negativeControls']==27
for c in controls['controls']:
 if c.get('model'):assert c['model']['canonicalOccurrenceReferencesEQ']
 if c['label'].startswith('merge-'):
  h=c['retainedHandleEvidence'];assert h['distinctReadHandles']==2 and h['canonicalGroupsInFinalMap']==[1,1] and h['replacedReadHandles']==[True,True] and c['occurrenceCountsAfterEachRead']==[1,2]
delta=read(A/'diagnostic-changes.json');assert delta['originalDiagnoses']==124 and delta['changed']==17 and delta['unchanged']==107
assert len({r['id'] for r in delta['changes']}&{r['id'] for r in originals})==11
faults=read(A/'failure-controls.json');assert faults['retained']==113 and faults['new']==0 and faults['noFaultCountedAsPASS'] and len(faults['controls'])==113
for f in faults['controls']:
 assert f['exitCode']==1 and f['caseRecordsAndOutcomesIdentical'] and f['checkCoveragePreserved'] and f['expectedASDFFailureObserved']
 assert read(A/(f['label']+'.json'))['cases']==read(P/(f['label']+'.json'))['cases']
retained=read(A/'retained-reports.json');assert len(retained)==48
for f in retained:assert sha(A/f['report'])==f['sha256'] and (A/f['report']).read_bytes()==(P/f['report']).read_bytes()
eq=read(A/'equivalence-preservation.json');assert eq['checks']==487 and eq['readerPairs']==27 and eq['originalPairSourcesModelsAndFullCXTMUnchanged']
assert read(A/'retained/xtm-mergemap.equivalence.json')['pairs'][:30]==read(P/'retained/xtm-mergemap.equivalence.json')['pairs'][:30]
ret=read(D/'retargetings.json');assert len(ret)==4
for x in ret:
 assert x['baseFileSHA256']==s['trackedFileSHA256'][x['file']] and x['finalFileSHA256']==sha(ROOT/x['file'])
 assert x['before'] in subprocess.check_output(['git','show',BASE+':'+x['file']],cwd=ROOT,text=True)
 assert x['after'] in (ROOT/x['file']).read_text() and x['expectedClass']=='XTM-UNSUPPORTED' and x['expectedCode']=='unsupported-construct'
lock=read(ROOT/'references/corpus-lock.json');assert len(lock['files'])==2006
for x in lock['files']:
 p=ROOT/'vendor/cxtm'/x['path'];assert p.stat().st_size==x['size'] and sha(p)==x['sha256']
assert len(protected)==8459 and sum(p.startswith('reports/') for p in protected)==6178
for p in ['scripts/validate-slice-22g.py','reports/slice-22g/final-audit.py']:ast.parse((ROOT/p).read_text(),filename=p)
doc=ROOT/'docs/slice-22g-xtm-occurrence-core.md'
for link in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
 if '://' not in link:assert (doc.parent/link).resolve().exists() or (doc.parent/link).resolve()==D/'final-audit.json',link
manifest={str(p.relative_to(ROOT)):sha(p) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='final-audit.json'}
manifest.update({p:sha(ROOT/p) for p in ALLOWED|NEW})
audit={'kind':'final-slice-22g-saved-execution-and-scope-audit-not-new-test-run','baseCommit':BASE,'observedHEAD':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),
 'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'initialIndexAndWorktreeClean':True,'allowedTrackedChanges':sorted(ALLOWED),
 'productionChanges':['src/xtm/reader.lisp'],'newOriginalPASS':11,'retainedOriginalPASS':72,'standaloneXTMChecks':2869,'newXTMChecks':165,
 'nativePositiveControls':19,'negativeControls':27,'nativeLateMergeProbes':9,'executorControls':113,'originalDiagnosesChanged':17,'originalDiagnosesUnchanged':107,
 'retainedEquivalenceChecks':487,'retainedEquivalenceReaderPairs':27,'statuses':e['statusesAfter'],'pinnedCorpusFilesVerified':2006,'historicalReportFilesVerified':6178,
 'protectedBaseFilesVerified':len(protected),'originalSourcesBaselinesHistoricalReportsAndCorpusLockUnchanged':True,'TMDMCTMCXTMXMLUnchanged':True,
 'hyperdocOrOtherWorkspaceChanges':False,'newDependencyDownloads':0,'persistentImagesTouched':False,'pushOrDeployment':False,
 'artifactSHA256':manifest,'selfExcludedFromManifest':True,'acceptancePassed':True}
(D/'final-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in audit.items() if k not in ['artifactSHA256','allowedTrackedChanges']}))
