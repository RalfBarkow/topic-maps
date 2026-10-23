#!/usr/bin/env python3
"""Slice 22M offline execution and acceptance audit using the existing collector.
Use an unused --output outside the repository; --audit-only rechecks saved runs.
"""
import argparse,datetime,hashlib,importlib.util,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'reports/slice-22m';PRIOR=ROOT/'reports/slice-22l/after'
BASE='27bf0dc4e2ab1e5afefcc616df8afdd73f815607'
ALLOWED={'src/xtm/reader.lisp','topic-maps.asd','tests/xtm-identity.lisp','tests/xtm-name-scopes.lisp','tests/xtm-associations.lisp','tests/xtm-occurrence-reification.lisp','tests/ctm-xtm-equivalence.lisp'}
SOURCES=ALLOWED|{'tests/xtm-association-reifier-native.lisp','tests/xtm-association-reification.lisp','reports/slice-22m/api-preflight.lisp','scripts/validate-slice-22d.py','reports/slice-22d/failure-controls.lisp'}
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
 assert old['statuses']=={'pass':110,'fail':0,'unsupported':0,'not-run':0}
 assert new['statuses']=={'pass':115,'fail':0,'unsupported':0,'not-run':0} and new['otherCorpusInputs']=={'positiveUnexecuted':8,'negativeUnregisteredUnexecuted':1}
 assert old['cases']==new['cases'][:len(old['cases'])] and set(after)-set(before)==targets
 assert len(after)==len(new['cases']) and all(after[id]['status']=='pass' for id in targets)
 assert [c for c in new['checks'] if c in set(old['checks'])]==old['checks']
 labels=re.findall(r'^XTM-CHECK-PASS (.+)$',(out/'xtm.log').read_text(),re.M)
 assert labels==new['checks'] and len(labels)==len(set(labels))==3587
 permitted={'scope','statuses','otherCorpusInputs','checks','cases','scopeControls','mapReifierControls','associationControls','occurrenceReifierControls','mergemapControls'}
 for key in old:
  if key not in permitted:assert old[key]==new[key],key
 retargets=[]
 for key,count in {'scopeControls':1,'mapReifierControls':1,'associationControls':2,'occurrenceReifierControls':1}.items():
  assert len(old[key])==len(new[key]);changed=[(a,b) for a,b in zip(old[key],new[key]) if a!=b];assert len(changed)==count,(key,changed)
  for a,b in changed:
   assert a['label']==b['label'] and a['condition']['class']==b['condition']['class']=='XTM-UNSUPPORTED'
   assert a['condition']['code']==b['condition']['code']=='unsupported-construct'
   assert a['condition']['detail']=='XTM association reification is not implemented in this subset.'
   assert b['condition']['detail']=='XTM role reification is not implemented in this subset.'
   assert '<role reifier=' in b['sourceText']
   assert b['sourceText']==a['sourceText'] or b['sourceText']==a['sourceText'].replace('<role>',"<role reifier='#excluded-role'>",1)
   for k in ['sourceKey','documentIRI','line']:assert a['condition'][k]==b['condition'][k]
   retargets.append({'reportKey':key,'label':a['label'],'before':a,'after':b,'differences':diff(a,b)})
 assert new['mergemapControls'][1:]==old['mergemapControls']
 imported=new['mergemapControls'][0];assert imported['label']=='Association-Reification-import' and imported['sourceMapsPreserved'] and imported['qualifiedParserCalls']==2
 assert len(imported['resolverCalls'])==1 and imported['model']['canonicalNativeReferencesEQ']
 for fixture in read(D/'retargetings.json'):
  if 'afterSource' in fixture:assert fixture['afterSource'] in (ROOT/fixture['file']).read_text()
 save(out/'retargeted-control-observations.json',retargets)
 originals=[];(out/'actual').mkdir(exist_ok=True)
 assert {x['id'] for x in new['associationReifierOriginals']}==targets
 for row in new['associationReifierOriginals']:
  source=inputs[row['id']];raw=bytes.fromhex(row['sourceHex'])
  assert raw==(ROOT/'vendor/cxtm'/row['id']).read_bytes() and hashlib.sha256(raw).hexdigest()==source['sourceSHA256']
  assert row['status']=='pass' and row['condition'] is None and row['firstDifferentByte'] is None
  assert row['originalOctetsEQ'] and row['qualifiedParserCalls']==1 and row['oldHandlesCanonicalAndLive']
  assert row['model']['canonicalAssociationReifierInverseEQ']
  actual=row['actualCXTM'].encode();expected=(ROOT/'vendor/cxtm/xtm2/baseline'/(Path(row['id']).name+'.cxtm')).read_bytes()
  assert actual==expected==row['expectedCXTM'].encode() and len(actual)==row['actualBytes']==row['expectedBytes']==source['baselineBytes']
  assert hashlib.sha256(expected).hexdigest()==source['baselineSHA256'] and after[row['id']]['actualOutcome']=='cxtm-match'
  p=out/'actual'/(Path(row['id']).name+'.cxtm');p.write_bytes(actual)
  originals.append(dict(row,actualSHA256=sha(p),completeByteExact=True,sourceSHA256=source['sourceSHA256'],baselineSHA256=source['baselineSHA256']))
 save(out/'original-contracts.json',originals)
 # All original reader diagnoses, including a later reached excluded Role boundary.
 oldd={x['id']:x for x in read(PRIOR/'after-diagnostics.json')};newd={x['id']:x for x in read(out/'after-diagnostics.json')}
 inventory=sorted('xtm2/'+sub+'/'+p.name for sub in ['in','invalid'] for p in (ROOT/'vendor/cxtm/xtm2'/sub).glob('*.xtm'))
 assert len(inventory)==124 and set(inventory)==set(oldd)==set(newd)
 changes=[];matrix=[];excluded='xtm2/invalid/role-duplicate-reified.xtm'
 for id in inventory:
  a,b=oldd[id],newd[id];ds=diff(a,b)
  if ds:
   assert id in targets,id
   if id in targets:assert b['byteExact'] and b['condition'] is None
   else:
    assert a['condition']['class']==b['condition']['class']=='XTM-UNSUPPORTED' and a['condition']['code']==b['condition']['code']=='unsupported-construct'
    assert 'association reification' in a['condition']['detail'] and 'role reification' in b['condition']['detail']
   changes.append({'id':id,'reason':'new Association Reification original result' if id in targets else 'Excluded Role-Reification reached after supported Association; remains NOT-RUN','differences':ds})
  elif id in targets:raise AssertionError(id)
  bs=before.get(id,{}).get('status','not-run');ns=after.get(id,{}).get('status','not-run');assert (bs!=ns)==(id in targets)
  matrix.append({'id':id,'before':bs,'after':ns,'registeredStatusChanged':bs!=ns,'diagnosisChanged':bool(ds),'beforeDiagnosis':a,'afterDiagnosis':b})
 assert all(newd[id]==oldd[id] for id in before)
 assert targets=={x['id'] for x in changes} and excluded not in after and oldd[excluded]==newd[excluded]
 save(out/'diagnostic-changes.json',{'originalDiagnoses':124,'changed':len(changes),'unchanged':124-len(changes),'changes':changes})
 save(out/'all-124-original-statuses.json',{'cases':matrix,'registeredChanges':5,'previous110OriginalPASSUnchanged':True})
 faults=[]
 for x in run['runs']:
  if '-control-' not in x['label']:continue
  a=read(PRIOR/(x['label']+'.json'));b=read(out/(x['label']+'.json'));ds=diff(a,b)
  assert a['cases']==b['cases'] and a['statuses']==b['statuses'] and a['checks']==b['checks'] and x['exitCode']==1
  aa=dict(a);bb=dict(b)
  for k in ['scope','associationReifierNative','associationReifierOriginals','associationReifierControls']:aa.pop(k,None);bb.pop(k,None)
  for rt in retargets:
   key=rt['reportKey'];aa[key]=[rt['after'] if row==rt['before'] else row for row in aa[key]]
  assert aa==bb,(x['label'],diff(aa,bb))
  assert not b['associationReifierNative'] and not b['associationReifierOriginals'] and not b['associationReifierControls']
  faults.append({'label':x['label'],'expectedASDFFailureObserved':True,'exitCode':1,'caseRecordsOutcomesAndChecksIdentical':True,'faultCountedAsOriginalPASS':False,'reportDifferences':ds})
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
 assert eqa['checks']==eqb['checks'] and len(eqb['checks'])==515
 oldpairs={x['id']:x for x in eqa['pairs']};pairs={x['id']:x for x in eqb['pairs']};gap='association-role-scope-reifiers'
 assert oldpairs.keys()==pairs.keys() and all(oldpairs[id]==pairs[id] for id in oldpairs if id!=gap)
 a,b=oldpairs[gap],pairs[gap];ds=diff(a,b)
 assert b['kind']=='reader-capability-gap-not-equivalence-PASS' and not b['successfulReaderPair']
 assert b['missingCapability']=='XTM role deserialization' and b['xtmCondition']['class']=='XTM-UNSUPPORTED'
 assert b['xtmCondition']['code']=='unsupported-construct' and 'role reification' in b['xtmCondition']['message']
 assert all(x['path'].startswith('/xtmCondition/') or x['path']=='/missingCapability' for x in ds)
 assert sum(x['kind']=='direct-reader-equivalence-pair' for x in eqb['pairs'])==29
 save(out/'equivalence-boundary.json',{'all29PairsAnd3ContrastsUnchanged':True,'remainingGapIsRoleReification':True,'checks':515,'differences':ds,'before':a,'after':b})
 # Native gate really executed on the original Reader, before its edit.
 gate=read(D/'native-before-execution.json');native=read(D/'native-before/report.json')
 assert gate['exitCode']==0 and gate['beforeAnyProductionChange'] and gate['network']==gate['repositoryWrites']=='denied'
 assert gate['executionSourceSHA256']['src/xtm/reader.lisp']==initial['trackedFileSHA256']['src/xtm/reader.lisp']
 for p,h in gate['executionSourceSHA256'].items():
  if p!='src/xtm/reader.lisp':assert sha(ROOT/p)==h
 assert sha(D/'native-before/run.log')==gate['logSHA256'] and sha(D/'native-before/report.json')==gate['reportSHA256']
 assert len(native['checks'])==12 and not native['ReaderInvoked'] and native['originalRegistrationsAdded']==0
 assert native['observations']==new['associationReifierNative'] and all(c in new['checks'] for c in native['checks'])
 assert len(new['associationReifierControls'])==34
 save(out/'native-preflight-confirmation.json',{'executedBeforeReaderChange':True,'nativeChecksBefore':12,'sameNativeChecksAndObservationsRepeatedInASDF':True,'nativeExecution':gate})
 prior=read(PRIOR/'execution.json');log=(out/'regression.log').read_text()
 for marker,count in dict(prior['retainedChecks'],**prior['stageChecks']).items():assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',log).group(1))==count
 assert 'CTM-XTM-EQUIVALENCE-PASS: 515 checks; 29 actual reader pairs;' in log
 assert 'Ran 2 tests' in log and 'NFC-ORACLE-PASS: 16294' in log and 'CXML-SUMMARY 146 PASS 0 FAIL' in (out/'xml.log').read_text()
 lock=read(ROOT/'references/corpus-lock.json')
 for f in lock['files']:
  p=ROOT/'vendor/cxtm'/f['path'];assert p.stat().st_size==f['size'] and sha(p)==f['sha256']
 assert protected=={p:sha(ROOT/p) for p in protected}
 save(out/'integrity.json',{'protectedBaseFilesSHA256':protected,'pinnedCorpusFilesVerified':len(lock['files']),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
  'originalsBaselinesHistoricalReportsAndCorpusLockUnchanged':True,'productionChanges':['src/xtm/reader.lisp'],'TMDM_CTM_CXTM_XMLUnchanged':True})
 save(out/'execution.json',{'kind':'slice-22m-XTM-association-reification','baseCommit':BASE,'branch':git('branch','--show-current'),'runtime':'SBCL 2.5.4',
  'startedAtUTC':run['startedAtUTC'],'finishedAtUTC':run['finishedAtUTC'],'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runs':run['runs'],
  'collector':'scripts/validate-slice-22d.py::collect (unchanged)','auditToolSHA256':sha(Path(__file__)),'standaloneXTMChecks':len(labels),'retainedStandaloneXTMChecks':len(old['checks']),
  'newXTMChecks':len(labels)-len(old['checks']),'retainedLispChecks':12100,'retainedChecks':prior['retainedChecks'],'stageChecks':prior['stageChecks'],
  'equivalenceChecks':515,'equivalenceReaderPairs':29,'faultControls':113,'allOriginalStatusesCompared':124,'diagnosticChanges':len(changes),'registeredStatusChanges':5,
  'statusesBefore':prior['statusesAfter'],'statusesAfter':{'XTM':{'pass':115,'fail':0,'not-run':9},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':377,'fail':4,'not-run':16}},
  'originalRegistrationsAdded':5,'xmlQualificationChecks':146,'pythonUnitTests':2,'nfcOracleComparisons':16294,'pinnedCorpusFilesVerified':len(lock['files']),
  'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),'knownCTMFailuresUnchanged':prior['knownCTMFailuresUnchanged'],
  'productionChanges':['src/xtm/reader.lisp'],'nativePreflightBeforeReaderChange':gate,'nativeGateChecks':12,'totalFreshProcessesIncludingBeforeGate':120,'newDependencyDownloads':0,'persistentImagesTouched':False,'acceptancePassed':True})
 print(json.dumps({'acceptancePassed':True,'XTMChecks':len(labels),'newOriginalPASS':5,'allOriginalStatusesCompared':124,'diagnosticChanges':len(changes),'faultControls':113}))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--audit-only',action='store_true');a=ap.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=True)
 if not a.audit_only:
  spec=importlib.util.spec_from_file_location('v22d',ROOT/'scripts/validate-slice-22d.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);v.EXECUTION_FILES=SOURCES;v.collect(out,ROOT/'reports/slice-22d/baseline')
 audit(out)
if __name__=='__main__':main()
