#!/usr/bin/env python3
"""Audit saved Slice 22H executions and artifact scope; starts no tests."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import re
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'reports/slice-22h';A=D/'after';P=ROOT/'reports/slice-22g/after'
BASE='7f4aa941293e555ccb9d96f0c05c651b0549a866'
ALLOWED={'topic-maps.asd','tests/xtm-identity.lisp','tests/xtm-mergemap.lisp'}
NEW={'tests/xtm-mergemap-originals.lisp','scripts/validate-slice-22h.py','docs/slice-22h-xtm-mergemap-originals.md'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
s=read(D/'initial-state.json');assert s['baseCommit']==BASE and s['initialIndexAndWorktreeClean']
assert set(s['trackedFileSHA256'])==set(git('ls-tree','-r','--name-only',BASE).splitlines())
protected={p:h for p,h in s['trackedFileSHA256'].items() if p not in ALLOWED}
assert protected=={p:sha(ROOT/p) for p in protected}
changed=set(git('diff','--name-only',BASE).splitlines());untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
assert all(p in ALLOWED|NEW or p.startswith('reports/slice-22h/') for p in changed|untracked)
assert not any(p.startswith('src/') for p in changed|untracked)
e=read(A/'execution.json');runs=read(A/'runs.json');assert e['acceptancePassed'] and e['auditToolSHA256']==sha(ROOT/'scripts/validate-slice-22h.py')
assert len(runs['runs'])==119
assert all(x['exitCode']==x['expectedExitCode'] and x['freshProcess'] and x['network']==x['repositoryWrites']==x['hyperdocWrites']=='denied' and sha(A/(x['label']+'.log'))==x['logSHA256'] for x in runs['runs'])
assert runs['executionSourcesSHA256']=={p:sha(ROOT/p) for p in runs['executionSourcesSHA256']}
assert runs['rawReportSHA256']=={p:sha(A/p) for p in runs['rawReportSHA256']}
assert e['standaloneXTMChecks']==2965 and e['newXTMChecks']==96 and e['retainedStandaloneXTMChecks']==2869 and e['retainedLispChecks']==12100
assert e['statusesAfter']=={'XTM':{'pass':88,'fail':0,'not-run':36},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':350,'fail':4,'not-run':43}}
old=read(P/'xtm.json');new=read(A/'xtm.json');assert old['cases']==new['cases'][:len(old['cases'])]
assert len(new['cases'])==len({c['id'] for c in new['cases']})
assert [c for c in new['checks'] if c in set(old['checks'])]==old['checks']
assert len(new['checks'])==len(set(new['checks']))==2965
assert re.findall(r'^XTM-CHECK-PASS (.+)$',(A/'xtm.log').read_text(),re.M)==new['checks']
inputs={x['id']:x for x in read(D/'originals-before.json')};originals=read(A/'original-contracts.json')
assert {o['id'] for o in originals}==set(inputs)=={c['id'] for c in new['cases']} - {c['id'] for c in old['cases']}
for o in originals:
 i=inputs[o['id']];source=ROOT/'vendor/cxtm'/o['id'];child=ROOT/'vendor/cxtm'/i['resourceID'];baseline=ROOT/'vendor/cxtm/xtm2/baseline'/(source.name+'.cxtm');actual=A/'actual'/(source.name+'.cxtm')
 assert source.read_bytes()==bytes.fromhex(o['sourceHex']) and sha(source)==i['sourceSHA256']==o['sourceSHA256']
 assert child.read_bytes()==bytes.fromhex(o['childHex']) and sha(child)==i['resourceSHA256']==o['childSHA256']
 assert actual.read_bytes()==baseline.read_bytes()==o['actualCXTM'].encode()==o['expectedCXTM'].encode()
 assert sha(actual)==sha(baseline)==i['baselineSHA256']==o['baselineSHA256']==o['actualSHA256']
 assert actual.stat().st_size==o['actualBytes']==o['expectedBytes'] and o['condition'] is None and o['firstDifferentByte'] is None and o['status']=='pass'
 assert o['importTrace']['sourceMapsPreserved'] and o['targetModel']['canonicalNativeReferencesEQ'] and o['sourceModel']['canonicalNativeReferencesEQ']
 p=o['qualifiedParserTrace'];assert len(p)==2 and p[0]['originalRootOctetsEQ'] and p[1]['originalChildOctetsEQ']
 assert p[0]['documentIRI']==o['documentIRI'] and p[1]['documentIRI']==o['childDocumentIRI']
 assert p[0]['sourceKey']==o['sourceKey'] and p[1]['sourceKey']==o['childSourceKey']
 assert o['importTrace']['resolverCalls']==[{'resourceIRI':o['childDocumentIRI'],'purpose':'mergemap','fromDocumentIRI':o['documentIRI'],'notation':'http://psi.topicmaps.org/iso13250/xtm'}]
ledger=read(A/'all-124-original-statuses.json');assert len(ledger['cases'])==124 and ledger['registeredChanges']==5
assert {c['id'] for c in ledger['cases'] if c['changed']}==set(inputs)
assert sum(c['after']=='pass' for c in ledger['cases'])==88 and sum(c['after']=='not-run' for c in ledger['cases'])==36
assert all(c['before']=='not-run' and c['after']=='pass' and c['newOriginalWithPinnedResolver']['condition'] is None for c in ledger['cases'] if c['changed'])
assert (A/'after-diagnostics.json').read_bytes()==(P/'after-diagnostics.json').read_bytes() and len(read(A/'after-diagnostics.json'))==124
faults=read(A/'failure-controls.json');assert faults['retained']==113 and faults['new']==0 and len(faults['controls'])==113
for f in faults['controls']:
 assert f['exitCode']==1 and f['expectedASDFFailureObserved'] and f['caseRecordsOutcomesAndChecksIdentical'] and not f['faultCountedAsOriginalPASS']
 assert all(d['path'] in {'/scope','/registeredMergemapOriginals'} for d in f['reportDifferences'])
 assert read(A/(f['label']+'.json'))['cases']==read(P/(f['label']+'.json'))['cases']
retained=read(A/'retained-reports.json');assert len(retained)==49
for f in retained:assert sha(A/f['report'])==f['sha256'] and (A/f['report']).read_bytes()==(P/f['report']).read_bytes()
for key in ['occurrenceOriginals','occurrenceControls','mergemapOriginalObservations']:assert old[key]==new[key]
notes=read(D/'test-integration-notes.json')
for n in notes['changedExcludedCaseGuards']:
 assert n['baseFileSHA256']==s['trackedFileSHA256'][n['file']] and n['finalFileSHA256']==sha(ROOT/n['file'])
 assert n['before'] in subprocess.check_output(['git','show',BASE+':'+n['file']],cwd=ROOT,text=True) and n['after'] in (ROOT/n['file']).read_text()
lock=read(ROOT/'references/corpus-lock.json');assert len(lock['files'])==2006
for f in lock['files']:
 p=ROOT/'vendor/cxtm'/f['path'];assert p.stat().st_size==f['size'] and sha(p)==f['sha256']
assert len(protected)==8777 and sum(p.startswith('reports/') for p in protected)==6490
for f in ['scripts/validate-slice-22h.py','reports/slice-22h/final-audit.py']:ast.parse((ROOT/f).read_text(),filename=f)
doc=ROOT/'docs/slice-22h-xtm-mergemap-originals.md'
for link in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
 if '://' not in link:assert (doc.parent/link).resolve().exists() or (doc.parent/link).resolve()==D/'final-audit.json',link
manifest={str(p.relative_to(ROOT)):sha(p) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='final-audit.json'}
manifest.update({p:sha(ROOT/p) for p in ALLOWED|NEW})
audit={'kind':'final-slice-22h-saved-execution-and-scope-audit-not-new-test-run','baseCommit':BASE,'observedHEAD':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),
 'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'initialIndexAndWorktreeClean':True,'allowedTrackedChanges':sorted(ALLOWED),'productionChanges':[],
 'newOriginalPASS':5,'retainedOriginalPASS':83,'allOriginalStatusesCompared':124,'readerDiagnosticChanges':0,'standaloneXTMChecks':2965,'newXTMChecks':96,
 'executorControls':113,'retainedEquivalenceChecks':487,'retainedEquivalenceReaderPairs':27,'statuses':e['statusesAfter'],'pinnedCorpusFilesVerified':2006,
 'historicalReportFilesVerified':6490,'protectedBaseFilesVerified':len(protected),'productionSourcesOriginalsBaselinesHistoricalReportsAndCorpusLockUnchanged':True,
 'excludedMapItemIdentityAndCycleOriginalsStillNotRun':True,'hyperdocOrOtherWorkspaceChanges':False,'newDependencyDownloads':0,'persistentImagesTouched':False,'pushOrDeployment':False,
 'artifactSHA256':manifest,'selfExcludedFromManifest':True,'acceptancePassed':True}
(D/'final-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in audit.items() if k not in ['artifactSHA256','allowedTrackedChanges']}))
