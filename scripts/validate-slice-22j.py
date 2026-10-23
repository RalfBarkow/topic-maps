#!/usr/bin/env python3
"""Slice 22J acceptance audit over the existing offline collector and case records.
--audit-only checks saved executions without rerunning tests. Output is outside Git.
"""
import argparse,datetime,hashlib,importlib.util,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'reports/slice-22j';PRIOR=ROOT/'reports/slice-22h/after'
BASE='f27f0af85e49cf25948bc4f2325fb02e77698de9'
ALLOWED={'src/xtm/reader.lisp','topic-maps.asd','tests/xtm-identity.lisp','tests/xtm-name-scopes.lisp','tests/ctm-xtm-equivalence.lisp'}
SOURCES=ALLOWED|{'tests/xtm-associations.lisp','scripts/validate-slice-22d.py','reports/slice-22d/failure-controls.lisp'}
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
 assert old['statuses']=={'pass':88,'fail':0,'unsupported':0,'not-run':0}
 assert new['statuses']=={'pass':98,'fail':0,'unsupported':0,'not-run':0} and new['otherCorpusInputs']=={'positiveUnexecuted':24,'negativeUnregisteredUnexecuted':2}
 assert old['cases']==new['cases'][:len(old['cases'])] and set(after)-set(before)==targets
 assert len(after)==len(new['cases']) and all(after[id]['status']=='pass' for id in targets)
 assert [c for c in new['checks'] if c in set(old['checks'])]==old['checks']
 labels=re.findall(r'^XTM-CHECK-PASS (.+)$',(out/'xtm.log').read_text(),re.M)
 assert labels==new['checks'] and len(labels)==len(set(labels))==3130
 permitted={'scope','statuses','otherCorpusInputs','checks','cases','scopeControls','mapReifierControls','mergemapControls'}
 for key in old:
  if key not in permitted:assert old[key]==new[key],key
 retargets=[]
 for key in ['scopeControls','mapReifierControls']:
  assert len(old[key])==len(new[key])
  changed=[(a,b) for a,b in zip(old[key],new[key]) if a!=b];assert len(changed)==1
  for a,b in changed:
   assert a['label']==b['label'] and b['condition']['class']=='XTM-UNSUPPORTED' and b['condition']['code']=='unsupported-construct'
   retargets.append({'reportKey':key,'label':a['label'],'before':a,'after':b,'differences':diff(a,b)})
 assert new['mergemapControls'][1:]==old['mergemapControls']
 imported=new['mergemapControls'][0];assert imported['label']=='association-native-nested-import' and imported['sourceMapsPreserved'] and imported['qualifiedParserCalls']==3
 assert len(imported['resolverCalls'])==2 and imported['model']['canonicalNativeReferencesEQ']
 save(out/'retargeted-control-observations.json',retargets)
 originals=[];(out/'actual').mkdir(exist_ok=True)
 assert {x['id'] for x in new['associationOriginals']}==targets
 for row in new['associationOriginals']:
  source=inputs[row['id']];raw=bytes.fromhex(row['sourceHex'])
  assert raw==(ROOT/'vendor/cxtm'/row['id']).read_bytes() and hashlib.sha256(raw).hexdigest()==source['sourceSHA256']
  assert row['status']=='pass'
  if '/invalid/' in row['id']:
   c=row['condition'];assert row['intendedCauseReached'] and c['class']=='XTM-REJECTION' and c['code']=='invalid-topic-ref'
   assert c['line']==7 and c['column']==38 and c['documentIRI']==row['documentIRI'] and c['sourceKey']==row['id']
   assert after[row['id']]['actualOutcome']=='ctm-rejection'
  else:
   assert row['condition'] is None and row['firstDifferentByte'] is None and row['originalOctetsEQ'] and row['qualifiedParserCalls']==1 and row['oldHandlesCanonicalAndLive']
   assert row['model']['canonicalAssociationRoleReferencesEQ'] and row['model']['associationCount']==1
   actual=row['actualCXTM'].encode();expected=(ROOT/'vendor/cxtm/xtm2/baseline'/(Path(row['id']).name+'.cxtm')).read_bytes()
   assert actual==expected==row['expectedCXTM'].encode() and len(actual)==row['actualBytes']==row['expectedBytes']==source['baselineBytes']
   assert hashlib.sha256(expected).hexdigest()==source['baselineSHA256'] and after[row['id']]['actualOutcome']=='cxtm-match'
   p=out/'actual'/(Path(row['id']).name+'.cxtm');p.write_bytes(actual)
   row=dict(row,actualSHA256=sha(p),completeByteExact=True)
  originals.append(dict(row,sourceSHA256=source['sourceSHA256'],baselineSHA256=source['baselineSHA256']))
 save(out/'original-contracts.json',originals)
 # Compare all original reader diagnoses, not only successful registrations.
 oldd={x['id']:x for x in read(PRIOR/'after-diagnostics.json')};newd={x['id']:x for x in read(out/'after-diagnostics.json')}
 inventory=sorted('xtm2/'+sub+'/'+p.name for sub in ['in','invalid'] for p in (ROOT/'vendor/cxtm/xtm2'/sub).glob('*.xtm'))
 assert len(inventory)==124 and set(inventory)==set(oldd)==set(newd)
 changed=[];matrix=[]
 for id in inventory:
  a,b=oldd[id],newd[id];ds=diff(a,b)
  if ds:
   if id in targets:
    if '/in/' in id:assert b['byteExact'] and b['condition'] is None
    else:assert b['condition']['class']=='XTM-REJECTION' and b['condition']['code']=='invalid-topic-ref'
    reason='new core Association/Role original execution reaches intended result'
   else:
    c=b['condition'];assert a['condition']['class']==c['class']=='XTM-UNSUPPORTED' and a['condition']['code']==c['code']=='unsupported-construct'
    assert re.fullmatch(r'XTM (association|role) (reification|item identifiers) (is|are) not implemented in this subset\.',c['detail'])
    assert b['status']==a['status'] and b['actualCXTM'] is None and not b['byteExact']
    reason='new core path exposes the specifically excluded metadata capability; still Unsupported, not registered'
   changed.append({'id':id,'reason':reason,'differences':ds})
  elif id in targets:raise AssertionError(id)
  bs=before.get(id,{}).get('status','not-run');ns=after.get(id,{}).get('status','not-run');assert (bs!=ns)==(id in targets)
  matrix.append({'id':id,'before':bs,'after':ns,'registeredStatusChanged':bs!=ns,'diagnosisChanged':bool(ds),'beforeDiagnosis':a,'afterDiagnosis':b})
 assert all(newd[id]==oldd[id] for id in before)
 save(out/'diagnostic-changes.json',{'originalDiagnoses':124,'changed':len(changed),'unchanged':124-len(changed),'changes':changed})
 save(out/'all-124-original-statuses.json',{'cases':matrix,'registeredChanges':10,'previous88OriginalPASSUnchanged':True})
 faults=[]
 for x in run['runs']:
  if '-control-' not in x['label']:continue
  a=read(PRIOR/(x['label']+'.json'));b=read(out/(x['label']+'.json'));changes=diff(a,b)
  assert a['cases']==b['cases'] and a['statuses']==b['statuses'] and a['checks']==b['checks'] and x['exitCode']==1
  aa=dict(a);bb=dict(b)
  for k in ['scope','associationOriginals','associationControls']:aa.pop(k,None);bb.pop(k,None)
  for rt in retargets:
   key=rt['reportKey'];aa[key]=[rt['after'] if row==rt['before'] else row for row in aa[key]]
  assert aa==bb,(x['label'],diff(aa,bb))
  assert not b['associationOriginals'] and not b['associationControls']
  faults.append({'label':x['label'],'expectedASDFFailureObserved':True,'exitCode':1,'caseRecordsOutcomesAndChecksIdentical':True,'faultCountedAsOriginalPASS':False,'reportDifferences':changes})
 assert len(faults)==113
 save(out/'failure-controls.json',{'retained':113,'new':0,'controls':faults,'allTargetCasesAndChecksUnchanged':True,'failureDriverUnchanged':True})
 retained=[]
 for p in sorted((PRIOR/'retained').glob('*.json')):
  rel=p.relative_to(PRIOR)
  if p.name.endswith('.equivalence.json'):continue
  assert p.read_bytes()==(out/rel).read_bytes(),str(rel)
  retained.append({'report':str(rel),'sha256':sha(p),'byteIdentical':True})
 for name in ['ctm.validation.json','ctm.cxtm.json','ctm.encoding.json']:
  assert (out/name).read_bytes()==(PRIOR/name).read_bytes();retained.append({'report':name,'sha256':sha(out/name),'byteIdentical':True})
 assert len(retained)==48;save(out/'retained-reports.json',retained)
 eqpath=next((out/'retained').glob('*.equivalence.json'));eqa=read(PRIOR/eqpath.relative_to(out));eqb=read(eqpath)
 oldpairs={x['id']:x for x in eqa['pairs']};pairs={x['id']:x for x in eqb['pairs']}
 assert oldpairs.keys()==pairs.keys()
 assert all(oldpairs[id]==pairs[id] for id in oldpairs if id not in {'explicit-association','association-role-scope-reifiers'})
 gapdiff=diff(oldpairs['association-role-scope-reifiers'],pairs['association-role-scope-reifiers'])
 assert len(gapdiff)==1 and gapdiff[0]['path']=='/xtmCondition/message'
 assert gapdiff[0]['after']==gapdiff[0]['before'].replace('XTM association is not implemented','XTM association reification is not implemented')
 pair=pairs['explicit-association'];assert pair['byteExact'] and pair['nativePropertiesEqual'] and pair['ctmCanonicalEQ'] and pair['xtmCanonicalEQ']
 assert pair['ctmBytes']==pair['xtmBytes'] and pair['firstDifferentByte'] is None and pair['ctmCondition'] is pair['xtmCondition'] is None
 assert sum(x['kind']=='direct-reader-equivalence-pair' for x in eqb['pairs'])==28
 assert sum(x['kind']=='reader-capability-gap-not-equivalence-PASS' for x in eqb['pairs'])==2
 save(out/'equivalence-progress.json',{'previous27PairsAnd3ContrastsUnchanged':True,'remaining2GapSourcesAndUnsupportedClassCodePositionUnchanged':True,'remainingReificationGapMessageRefined':gapdiff,'resolvedCapabilityGap':pair,'checks':len(eqb['checks']),'pairs':28,'remainingGaps':2})
 prior=read(PRIOR/'execution.json');log=(out/'regression.log').read_text()
 for marker,count in dict(prior['retainedChecks'],**prior['stageChecks']).items():assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',log).group(1))==count
 assert f"CTM-XTM-EQUIVALENCE-PASS: {len(eqb['checks'])} checks; 28 actual reader pairs;" in log
 assert 'Ran 2 tests' in log and 'NFC-ORACLE-PASS: 16294' in log and 'CXML-SUMMARY 146 PASS 0 FAIL' in (out/'xml.log').read_text()
 lock=read(ROOT/'references/corpus-lock.json')
 for f in lock['files']:
  p=ROOT/'vendor/cxtm'/f['path'];assert p.stat().st_size==f['size'] and sha(p)==f['sha256']
 assert protected=={p:sha(ROOT/p) for p in protected}
 save(out/'integrity.json',{'protectedBaseFilesSHA256':protected,'pinnedCorpusFilesVerified':len(lock['files']),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
  'originalsBaselinesHistoricalReportsAndCorpusLockUnchanged':True,'productionChanges':['src/xtm/reader.lisp'],'TMDM_CTM_CXTM_XMLUnchanged':True})
 save(out/'execution.json',{'kind':'slice-22j-XTM-association-role-core','baseCommit':BASE,'branch':git('branch','--show-current'),'runtime':'SBCL 2.5.4',
  'startedAtUTC':run['startedAtUTC'],'finishedAtUTC':run['finishedAtUTC'],'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runs':run['runs'],
  'collector':'scripts/validate-slice-22d.py::collect (unchanged)','auditToolSHA256':sha(Path(__file__)),'standaloneXTMChecks':len(labels),'retainedStandaloneXTMChecks':len(old['checks']),
  'newXTMChecks':len(labels)-len(old['checks']),'retainedLispChecks':12100,'retainedChecks':prior['retainedChecks'],'stageChecks':prior['stageChecks'],
  'equivalenceChecks':len(eqb['checks']),'equivalenceReaderPairs':28,'faultControls':113,'allOriginalStatusesCompared':124,'diagnosticChanges':len(changed),'registeredStatusChanges':10,
  'statusesBefore':prior['statusesAfter'],'statusesAfter':{'XTM':{'pass':98,'fail':0,'not-run':26},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':360,'fail':4,'not-run':33}},
  'originalRegistrationsAdded':10,'xmlQualificationChecks':146,'pythonUnitTests':2,'nfcOracleComparisons':16294,'pinnedCorpusFilesVerified':len(lock['files']),
  'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),'knownCTMFailuresUnchanged':prior['knownCTMFailuresUnchanged'],
  'productionChanges':['src/xtm/reader.lisp'],'newDependencyDownloads':0,'persistentImagesTouched':False,'acceptancePassed':True})
 print(json.dumps({'acceptancePassed':True,'XTMChecks':len(labels),'newOriginalPASS':10,'allOriginalStatusesCompared':124,'diagnosticChanges':len(changed),'faultControls':113}))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--audit-only',action='store_true');a=ap.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=True)
 if not a.audit_only:
  spec=importlib.util.spec_from_file_location('v22d',ROOT/'scripts/validate-slice-22d.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);v.EXECUTION_FILES=SOURCES;v.collect(out,ROOT/'reports/slice-22d/baseline')
 audit(out)
if __name__=='__main__':main()
