#!/usr/bin/env python3
"""Slice 22G: reuse the existing 119-process offline collector; audit saved evidence.
--audit-only starts no tests. Output must be outside the repository.
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
D=ROOT/'reports/slice-22g';PRIOR=ROOT/'reports/slice-22f/after'
BASE='b50a9d7950c5407b2ec02e1caccd76f73018b45f'
ALLOWED={'src/xtm/reader.lisp','topic-maps.asd','tests/xtm-identity.lisp','tests/xtm-name-scopes.lisp','tests/xtm-resource-datatypes.lisp','tests/xtm-mergemap.lisp'}
SOURCES=ALLOWED|{'tests/xtm-occurrences.lisp','scripts/validate-slice-22d.py','reports/slice-22d/failure-controls.lisp'}
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
 runs=read(out/'runs.json');assert len(runs['runs'])==119
 assert all(x['exitCode']==x['expectedExitCode'] and sha(out/(x['label']+'.log'))==x['logSHA256'] for x in runs['runs'])
 assert runs['executionSourcesSHA256']=={p:sha(ROOT/p) for p in runs['executionSourcesSHA256']}
 assert runs['rawReportSHA256']=={p:sha(out/p) for p in runs['rawReportSHA256']}
 old=read(PRIOR/'xtm.json');new=read(out/'xtm.json');targets={x['id'] for x in read(D/'originals-before.json')}
 assert new['statuses']=={'pass':83,'fail':0,'unsupported':0,'not-run':0} and len(new['cases'])==83
 assert new['otherCorpusInputs']=={'positiveUnexecuted':38,'negativeUnregisteredUnexecuted':3}
 assert new['cases'][:72]==old['cases'] and {x['id'] for x in new['cases'][72:]}==targets
 assert len({x['id'] for x in new['cases']})==83 and all(x['status']=='pass' and x['actualOutcome']=='cxtm-match' for x in new['cases'][72:])
 assert new['checks'][:len(old['checks'])]!=[]
 assert [x for x in new['checks'] if x in set(old['checks'])]==old['checks']
 labels=re.findall(r'^XTM-CHECK-PASS (.+)$',(out/'xtm.log').read_text(),re.M)
 assert labels==new['checks'] and len(labels)==len(set(labels))
 actualdir=out/'actual';actualdir.mkdir(exist_ok=True);originals=[]
 sourceinfo={x['id']:x for x in read(D/'originals-before.json')}
 assert len(new['occurrenceOriginals'])==11
 for row in new['occurrenceOriginals']:
  source=sourceinfo[row['id']];assert row['condition'] is None and row['status']=='pass'
  assert row['qualifiedParserCalls']==1 and row['originalOctetsEQ'] and row['oldHandlesCanonicalAndLive']
  assert row['model']['canonicalOccurrenceReferencesEQ'] and row['firstDifferentByte'] is None
  raw=bytes.fromhex(row['sourceHex']);ac=row['actualCXTM'].encode();expected=(ROOT/'vendor/cxtm/xtm2/baseline'/(Path(row['id']).name+'.cxtm')).read_bytes()
  assert raw==(ROOT/'vendor/cxtm'/row['id']).read_bytes() and hashlib.sha256(raw).hexdigest()==source['sourceSHA256']
  assert ac==expected==row['expectedCXTM'].encode() and len(ac)==row['actualBytes']==row['expectedBytes']==source['baselineBytes']
  p=actualdir/(Path(row['id']).name+'.cxtm');p.write_bytes(ac)
  originals.append(dict(row,sourceSHA256=source['sourceSHA256'],baselineSHA256=sha(p),actualSHA256=sha(p),completeByteExact=True))
 save(out/'original-contracts.json',originals)
 controls=new['occurrenceControls'];positive=[c for c in controls if c.get('model')];negative=[c for c in controls if c.get('condition')]
 assert len(positive)==19 and len(negative)==27 and len(controls)==46
 assert all(c['model']['canonicalOccurrenceReferencesEQ'] for c in positive)
 merges=[c for c in positive if c['label'].startswith('merge-')]
 assert len(merges)==9
 for c in merges:
  h=c['retainedHandleEvidence'];assert c['occurrenceCountsAfterEachRead']==[1,2] and c['model']['occurrenceCount']==1
  assert h['readHandleCount']==h['distinctReadHandles']==2 and h['canonicalGroupsInFinalMap']==[1,1] and h['replacedReadHandles']==[True,True]
 assert {c['condition']['class'] for c in negative}=={'XTM-REJECTION','XTM-UNSUPPORTED','XTM-XML-ERROR','OCCURRENCE-ERROR','OCCURRENCE-IDENTIFIER-ERROR'}
 save(out/'native-and-negative-controls.json',{'positiveControls':19,'negativeControls':27,'mergingDimensions':['parent','type','scope'],'identityKinds':['SI','SL','II'],'controls':controls})
 # Compare all original diagnostics, including unregistered capability-boundary effects.
 before={x['id']:x for x in read(PRIOR/'after-diagnostics.json')};after={x['id']:x for x in read(out/'after-diagnostics.json')};assert len(before)==len(after)==124
 changes=[]
 for id in sorted(before):
  if before[id]==after[id]:continue
  if id in targets:
   assert after[id]['condition'] is None and after[id]['byteExact'];reason='Newly implemented supported occurrence core; full original baseline match.'
  else:
   assert id in {'xtm2/in/itemid-occurrence.xtm','xtm2/in/occurrence-duplicate-iid.xtm','xtm2/in/occurrence-duplicate-iid2.xtm','xtm2/in/occurrence-reifier.xtm','xtm2/in/occurrence-duplicate-reifier.xtm','xtm2/invalid/reifier-collision.xtm'}
   assert after[id]['condition']['class']=='XTM-UNSUPPORTED' and after[id]['condition']['code']=='unsupported-construct'
   assert 'occurrence' in after[id]['condition']['detail'];reason='Precise excluded occurrence II/reification boundary, not a registered PASS.'
  changes.append({'id':id,'reason':reason,'before':before[id],'after':after[id],'differences':diff(before[id],after[id])})
 assert {x['id'] for x in changes}==targets|{'xtm2/in/itemid-occurrence.xtm','xtm2/in/occurrence-duplicate-iid.xtm','xtm2/in/occurrence-duplicate-iid2.xtm','xtm2/in/occurrence-reifier.xtm','xtm2/in/occurrence-duplicate-reifier.xtm','xtm2/invalid/reifier-collision.xtm'}
 save(out/'diagnostic-changes.json',{'originalDiagnoses':124,'changed':len(changes),'unchanged':124-len(changes),'changes':changes})
 faults=[]
 for x in runs['runs']:
  if '-control-' not in x['label']:continue
  a=read(PRIOR/(x['label']+'.json'));b=read(out/(x['label']+'.json'))
  assert a['cases']==b['cases'] and a['statuses']==b['statuses'],x['label']
  assert x['exitCode']==1 and len(a['checks'])==len(b['checks'])
  differences=diff(a,b)
  permitted={'/scope','/occurrenceControls','/occurrenceOriginals','/scopeControls/35/sourceText',
    '/scopeControls/35/condition/column','/scopeControls/35/condition/detail','/scopeControls/35/condition/message',
    '/mapReifierControls/31/condition/detail','/mapReifierControls/31/condition/message',
    '/variantReifierControls/35/condition/detail','/variantReifierControls/35/condition/message'}
  assert all(d['path'] in permitted for d in differences),x['label']
  faults.append({'label':x['label'],'exitCode':1,'expectedASDFFailureObserved':True,'caseRecordsAndOutcomesIdentical':True,'checkCoveragePreserved':True,'behavioralDifferences':differences})
 assert len(faults)==113
 save(out/'failure-controls.json',{'retained':113,'new':0,'controls':faults,'noFaultCountedAsPASS':True})
 # Preserve all non-XTM reports. The old equivalence gap has a more precise message.
 retained=[]
 for p in sorted((PRIOR/'retained').glob('*.json')):
  rel=p.relative_to(PRIOR)
  if p.name=='xtm-mergemap.equivalence.json':continue
  assert p.read_bytes()==(out/rel).read_bytes(),str(rel)
  retained.append({'report':str(rel),'sha256':sha(p),'byteIdentical':True})
 for name in ['ctm.validation.json','ctm.cxtm.json','ctm.encoding.json']:
  assert (PRIOR/name).read_bytes()==(out/name).read_bytes();retained.append({'report':name,'sha256':sha(out/name),'byteIdentical':True})
 assert len(retained)==48
 save(out/'retained-reports.json',retained)
 eqold=read(PRIOR/'retained/xtm-mergemap.equivalence.json');eq=read(out/'retained/xtm-mergemap.equivalence.json')
 assert eq['condition'] is None and eq['checks']==eqold['checks'] and len(eq['checks'])==487
 assert eq['pairs'][:30]==eqold['pairs'][:30] and len(eq['pairs'])==33
 eqdiff=diff(eqold,eq)
 assert all(x['path'].startswith('/pairs/30/xtmCondition/') and x['path'].split('/')[-1] in {'message','detail'} for x in eqdiff)
 save(out/'equivalence-preservation.json',{'checks':487,'readerPairs':27,'originalPairSourcesModelsAndFullCXTMUnchanged':True,'differences':eqdiff,'scope':'Only the existing unsupported occurrence-reification gap message is refined.'})
 prior=read(PRIOR/'execution.json');log=(out/'regression.log').read_text()
 for marker,count in dict(prior['retainedChecks'],**prior['stageChecks']).items():assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',log).group(1))==count
 assert 'Ran 2 tests' in log and 'NFC-ORACLE-PASS: 16294' in log
 assert 'CXML-SUMMARY 146 PASS 0 FAIL' in (out/'xml.log').read_text()
 lock=read(ROOT/'references/corpus-lock.json')
 for x in lock['files']:
  p=ROOT/'vendor/cxtm'/x['path'];assert p.stat().st_size==x['size'] and sha(p)==x['sha256']
 assert protected=={p:sha(ROOT/p) for p in protected}
 save(out/'integrity.json',{'protectedBaseFilesSHA256':protected,'pinnedCorpusFilesVerified':len(lock['files']),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),'originalSourcesBaselinesHistoricalReportsUnchanged':True,'onlyProductionChange':'src/xtm/reader.lisp'})
 save(out/'retargeted-observations.json',{'retargetings':read(D/'retargetings.json'),'existingTestReportDifferences':diff(old,{k:v for k,v in new.items() if k not in {'occurrenceOriginals','occurrenceControls'}})})
 save(out/'execution.json',{'kind':'slice-22g-XTM-occurrence-core','baseCommit':BASE,'branch':git('branch','--show-current'),'runtime':'SBCL 2.5.4',
  'startedAtUTC':runs['startedAtUTC'],'finishedAtUTC':runs['finishedAtUTC'],'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runs':runs['runs'],
  'collector':'scripts/validate-slice-22d.py::collect (unchanged)','auditToolSHA256':sha(Path(__file__)),'standaloneXTMChecks':len(labels),'retainedStandaloneXTMChecks':len(old['checks']),
  'newXTMChecks':len(labels)-len(old['checks']),'retainedLispChecks':12100,'retainedChecks':prior['retainedChecks'],'stageChecks':prior['stageChecks'],
  'equivalenceChecks':487,'equivalenceReaderPairs':27,'faultControls':113,'originalDiagnoses':124,'diagnosticChanges':len(changes),
  'statusesBefore':prior['statusesAfter'],'statusesAfter':{'XTM':{'pass':83,'fail':0,'not-run':41},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':345,'fail':4,'not-run':48}},
  'originalRegistrationsAdded':11,'xmlQualificationChecks':146,'pythonUnitTests':2,'nfcOracleComparisons':16294,'pinnedCorpusFilesVerified':len(lock['files']),
  'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),'knownCTMFailuresUnchanged':prior['knownCTMFailuresUnchanged'],
  'productionChanges':['src/xtm/reader.lisp'],'newDependencyDownloads':0,'persistentImagesTouched':False,'acceptancePassed':True})
 print(json.dumps({'acceptancePassed':True,'XTMChecks':len(labels),'newOriginalPASS':11,'diagnosticChanges':len(changes),'faultControls':113}))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--audit-only',action='store_true');a=ap.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=True)
 if not a.audit_only:
  spec=importlib.util.spec_from_file_location('v22d',ROOT/'scripts/validate-slice-22d.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);v.EXECUTION_FILES=SOURCES;v.collect(out,ROOT/'reports/slice-22d/baseline')
 audit(out)
if __name__=='__main__':main()
