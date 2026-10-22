#!/usr/bin/env python3
"""Register five already supported XTM mergeMap originals via the existing offline collector.
--audit-only verifies saved executions and starts no tests. Output is outside the repository.
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
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'reports/slice-22h';PRIOR=ROOT/'reports/slice-22g/after'
BASE='7f4aa941293e555ccb9d96f0c05c651b0549a866'
ALLOWED={'topic-maps.asd','tests/xtm-identity.lisp','tests/xtm-mergemap.lisp'}
SOURCES=ALLOWED|{'tests/xtm-mergemap-originals.lisp','scripts/validate-slice-22d.py','reports/slice-22d/failure-controls.lisp'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def diff(a,b,path=''):
 if a==b:return []
 if isinstance(a,dict) and isinstance(b,dict):return [d for k in sorted(a.keys()|b.keys()) for d in diff(a.get(k),b.get(k),path+'/'+k)]
 if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):return [d for i,(x,y) in enumerate(zip(a,b)) for d in diff(x,y,path+'/'+str(i))]
 return [{'path':path,'before':a,'after':b}]
def audit(out):
 initial=read(D/'initial-state.json');assert initial['baseCommit']==BASE and initial['initialIndexAndWorktreeClean']
 assert set(git('diff','--name-only',BASE).splitlines())&set(initial['trackedFileSHA256'])<=ALLOWED
 protected={p:h for p,h in initial['trackedFileSHA256'].items() if p not in ALLOWED}
 assert protected=={p:sha(ROOT/p) for p in protected}
 run=read(out/'runs.json');assert len(run['runs'])==119
 assert all(x['exitCode']==x['expectedExitCode'] and x['network']==x['repositoryWrites']=='denied' and sha(out/(x['label']+'.log'))==x['logSHA256'] for x in run['runs'])
 assert run['executionSourcesSHA256']=={p:sha(ROOT/p) for p in run['executionSourcesSHA256']}
 assert run['rawReportSHA256']=={p:sha(out/p) for p in run['rawReportSHA256']}
 old=read(PRIOR/'xtm.json');new=read(out/'xtm.json');before={x['id']:x for x in old['cases']};after={x['id']:x for x in new['cases']}
 inputs={x['id']:x for x in read(D/'originals-before.json')};targets=set(inputs)
 assert new['statuses']=={'pass':88,'fail':0,'unsupported':0,'not-run':0} and new['otherCorpusInputs']=={'positiveUnexecuted':33,'negativeUnregisteredUnexecuted':3}
 assert old['cases']==new['cases'][:len(old['cases'])] and set(after)-set(before)==targets
 assert len(after)==len(new['cases']) and all(after[id]['status']=='pass' and after[id]['actualOutcome']=='cxtm-match' for id in targets)
 assert [c for c in new['checks'] if c in set(old['checks'])]==old['checks']
 labels=re.findall(r'^XTM-CHECK-PASS (.+)$',(out/'xtm.log').read_text(),re.M)
 assert labels==new['checks'] and len(labels)==len(set(labels))==2965
 for key in old:
  if key not in {'scope','statuses','otherCorpusInputs','checks','cases'}:assert old[key]==new[key],key
 originals=[];(out/'actual').mkdir(exist_ok=True)
 assert {x['id'] for x in new['registeredMergemapOriginals']}==targets
 for row in new['registeredMergemapOriginals']:
  source=inputs[row['id']];assert row['condition'] is None and row['status']=='pass' and row['firstDifferentByte'] is None
  raw=bytes.fromhex(row['sourceHex']);childraw=bytes.fromhex(row['childHex'])
  assert raw==(ROOT/'vendor/cxtm'/row['id']).read_bytes() and childraw==(ROOT/'vendor/cxtm'/source['resourceID']).read_bytes()
  assert hashlib.sha256(raw).hexdigest()==source['sourceSHA256'] and hashlib.sha256(childraw).hexdigest()==source['resourceSHA256']
  actual=row['actualCXTM'].encode();expected=(ROOT/'vendor/cxtm/xtm2/baseline'/(Path(row['id']).name+'.cxtm')).read_bytes()
  assert actual==expected==row['expectedCXTM'].encode() and len(actual)==row['actualBytes']==row['expectedBytes']==source['baselineBytes']
  assert hashlib.sha256(expected).hexdigest()==source['baselineSHA256']
  traces=row['qualifiedParserTrace'];assert len(traces)==2
  assert traces[0]['documentIRI']==row['documentIRI'] and traces[0]['sourceKey']==row['sourceKey'] and traces[0]['originalRootOctetsEQ']
  assert traces[1]['documentIRI']==row['childDocumentIRI'] and traces[1]['sourceKey']==row['childSourceKey'] and traces[1]['originalChildOctetsEQ']
  assert traces[0]['bytes']==len(raw) and traces[1]['bytes']==len(childraw)
  trace=row['importTrace'];assert trace['sourceMapsPreserved'] and trace['qualifiedParserCalls']==2 and trace['model']==row['targetModel'] and trace['model']['canonicalNativeReferencesEQ']
  assert trace['resolverCalls']==[{'resourceIRI':row['childDocumentIRI'],'purpose':'mergemap','fromDocumentIRI':row['documentIRI'],'notation':'http://psi.topicmaps.org/iso13250/xtm'}]
  p=out/'actual'/(Path(row['id']).name+'.cxtm');p.write_bytes(actual)
  originals.append(dict(row,sourceSHA256=source['sourceSHA256'],childSHA256=source['resourceSHA256'],baselineSHA256=source['baselineSHA256'],actualSHA256=sha(p),completeByteExact=True))
 save(out/'original-contracts.json',originals)
 # Existing no-resolver exploratory diagnoses are unchanged. They are not the new original executions.
 assert (out/'after-diagnostics.json').read_bytes()==(PRIOR/'after-diagnostics.json').read_bytes()
 diagnoses={x['id']:x for x in read(out/'after-diagnostics.json')};assert len(diagnoses)==124
 inventory=sorted('xtm2/'+sub+'/'+p.name for sub in ['in','invalid'] for p in (ROOT/'vendor/cxtm/xtm2'/sub).glob('*.xtm'))
 assert len(inventory)==124 and set(inventory)==set(diagnoses)
 matrix=[]
 for id in inventory:
  b=before.get(id,{}).get('status','not-run');a=after.get(id,{}).get('status','not-run')
  assert (b!=a)==(id in targets)
  matrix.append({'id':id,'before':b,'after':a,'changed':b!=a,'beforeCaseRecord':before.get(id),'afterCaseRecord':after.get(id),
    'readerDiagnosisWithoutResolverUnchanged':True,'noResolverCondition':diagnoses[id]['condition'],
    'newOriginalWithPinnedResolver':next((o for o in originals if o['id']==id),None)})
 assert sum(x['after']=='pass' for x in matrix)==88 and sum(x['after']=='not-run' for x in matrix)==36
 save(out/'all-124-original-statuses.json',{'cases':matrix,'registeredChanges':5,'allOtherRegisteredStatusesUnchanged':True,'noResolverDiagnosticChanges':0})
 save(out/'diagnostic-changes.json',{'originalDiagnoses':124,'changed':0,'unchanged':124,'byteIdenticalToSlice22G':True,'note':'The legacy diagnostic driver omits a resolver. Five new original executions explicitly configure the pinned resolver and are recorded separately.'})
 faults=[]
 for x in run['runs']:
  if '-control-' not in x['label']:continue
  a=read(PRIOR/(x['label']+'.json'));b=read(out/(x['label']+'.json'));changes=diff(a,b)
  assert a['cases']==b['cases'] and a['statuses']==b['statuses'] and a['checks']==b['checks'] and x['exitCode']==1
  assert all(d['path'] in {'/scope','/registeredMergemapOriginals'} for d in changes)
  assert not b['registeredMergemapOriginals']
  faults.append({'label':x['label'],'expectedASDFFailureObserved':True,'exitCode':1,'caseRecordsOutcomesAndChecksIdentical':True,'faultCountedAsOriginalPASS':False,'reportDifferences':changes})
 assert len(faults)==113
 save(out/'failure-controls.json',{'retained':113,'new':0,'controls':faults,'allTargetCasesAndChecksUnchanged':True})
 retained=[]
 for p in sorted((PRIOR/'retained').glob('*.json')):
  rel=p.relative_to(PRIOR);assert p.read_bytes()==(out/rel).read_bytes(),str(rel)
  retained.append({'report':str(rel),'sha256':sha(p),'byteIdentical':True})
 for name in ['ctm.validation.json','ctm.cxtm.json','ctm.encoding.json']:
  assert (out/name).read_bytes()==(PRIOR/name).read_bytes();retained.append({'report':name,'sha256':sha(out/name),'byteIdentical':True})
 assert len(retained)==49;save(out/'retained-reports.json',retained)
 prior=read(PRIOR/'execution.json');log=(out/'regression.log').read_text()
 for marker,count in dict(prior['retainedChecks'],**prior['stageChecks']).items():assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',log).group(1))==count
 assert 'CTM-XTM-EQUIVALENCE-PASS: 487 checks; 27 actual reader pairs;' in log
 assert 'Ran 2 tests' in log and 'NFC-ORACLE-PASS: 16294' in log and 'CXML-SUMMARY 146 PASS 0 FAIL' in (out/'xml.log').read_text()
 lock=read(ROOT/'references/corpus-lock.json')
 for f in lock['files']:
  p=ROOT/'vendor/cxtm'/f['path'];assert p.stat().st_size==f['size'] and sha(p)==f['sha256']
 assert protected=={p:sha(ROOT/p) for p in protected}
 save(out/'integrity.json',{'protectedBaseFilesSHA256':protected,'pinnedCorpusFilesVerified':len(lock['files']),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
  'productionSourcesOriginalsBaselinesHistoricalReportsAndCorpusLockUnchanged':True,'productionChanges':[]})
 save(out/'execution.json',{'kind':'slice-22h-five-existing-XTM-mergeMap-originals','baseCommit':BASE,'branch':git('branch','--show-current'),'runtime':'SBCL 2.5.4',
  'startedAtUTC':run['startedAtUTC'],'finishedAtUTC':run['finishedAtUTC'],'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runs':run['runs'],
  'collector':'scripts/validate-slice-22d.py::collect (unchanged)','auditToolSHA256':sha(Path(__file__)),'standaloneXTMChecks':len(labels),'retainedStandaloneXTMChecks':len(old['checks']),
  'newXTMChecks':len(labels)-len(old['checks']),'retainedLispChecks':12100,'retainedChecks':prior['retainedChecks'],'stageChecks':prior['stageChecks'],
  'equivalenceChecks':487,'equivalenceReaderPairs':27,'faultControls':113,'allOriginalStatusesCompared':124,'diagnosticChanges':0,'registeredStatusChanges':5,
  'statusesBefore':prior['statusesAfter'],'statusesAfter':{'XTM':{'pass':88,'fail':0,'not-run':36},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':350,'fail':4,'not-run':43}},
  'originalRegistrationsAdded':5,'xmlQualificationChecks':146,'pythonUnitTests':2,'nfcOracleComparisons':16294,'pinnedCorpusFilesVerified':len(lock['files']),
  'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),'knownCTMFailuresUnchanged':prior['knownCTMFailuresUnchanged'],
  'productionChanges':[],'newDependencyDownloads':0,'persistentImagesTouched':False,'acceptancePassed':True})
 print(json.dumps({'acceptancePassed':True,'XTMChecks':len(labels),'newOriginalPASS':5,'allOriginalStatusesCompared':124,'faultControls':113}))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--audit-only',action='store_true');a=ap.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=True)
 if not a.audit_only:
  spec=importlib.util.spec_from_file_location('v22d',ROOT/'scripts/validate-slice-22d.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);v.EXECUTION_FILES=SOURCES;v.collect(out,ROOT/'reports/slice-22d/baseline')
 audit(out)
if __name__=='__main__':main()
