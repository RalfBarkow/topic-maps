#!/usr/bin/env python3
"""Slice 22L acceptance audit over the existing offline collector and case records.
--audit-only checks saved executions without rerunning tests. Output is outside Git.
"""
import argparse,datetime,hashlib,importlib.util,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'reports/slice-22l';PRIOR=ROOT/'reports/slice-22k/after'
BASE='c02207856f1927302ea064bc901e07183242f2da'
ALLOWED={'tests/ctm-xtm-mergemap.lisp', 'tests/xtm-variant-reification.lisp', 'tests/xtm-identity.lisp', 'tests/ctm-xtm-equivalence.lisp', 'tests/xtm-name-scopes.lisp', 'topic-maps.asd', 'tests/xtm-map-reification.lisp', 'src/xtm/reader.lisp', 'tests/xtm-occurrences.lisp', 'tests/xtm-mergemap.lisp', 'tests/xtm-item-identities.lisp', 'tests/xtm-negative-originals.lisp', 'tests/xtm-resource-datatypes.lisp'}
SOURCES=ALLOWED|{'tests/xtm-occurrence-reifier-native.lisp','tests/xtm-occurrence-reification.lisp','reports/slice-22l/api-preflight.lisp','scripts/validate-slice-22d.py','reports/slice-22d/failure-controls.lisp'}
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
 assert old['statuses']=={'pass':107,'fail':0,'unsupported':0,'not-run':0}
 assert new['statuses']=={'pass':110,'fail':0,'unsupported':0,'not-run':0} and new['otherCorpusInputs']=={'positiveUnexecuted':13,'negativeUnregisteredUnexecuted':1}
 assert old['cases']==new['cases'][:len(old['cases'])] and set(after)-set(before)==targets
 assert len(after)==len(new['cases']) and all(after[id]['status']=='pass' for id in targets)
 assert [c for c in new['checks'] if c in set(old['checks'])]==old['checks']
 labels=re.findall(r'^XTM-CHECK-PASS (.+)$',(out/'xtm.log').read_text(),re.M)
 assert labels==new['checks'] and len(labels)==len(set(labels))==3447
 permitted={'scope','statuses','otherCorpusInputs','checks','cases','scopeControls','mapReifierControls','variantReifierControls','datatypeControls','occurrenceControls','itemIdentityControls','mergemapControls'}
 for key in old:
  if key not in permitted:assert old[key]==new[key],key
 retargets=[]
 expected={'scopeControls':1,'mapReifierControls':1,'variantReifierControls':1,'datatypeControls':1,'occurrenceControls':2,'itemIdentityControls':1,'mergemapControls':1}
 for key,count in expected.items():
  arows=old[key];brows=[row for row in new[key] if row['label']!='Occurrence-Reification-import']
  assert len(arows)==len(brows)
  changed=[(a,b) for a,b in zip(arows,brows) if a!=b];assert len(changed)==count,(key,changed)
  for a,b in changed:
   assert a['label']==b['label'] and a['condition']['class']==b['condition']['class']=='XTM-UNSUPPORTED'
   assert a['condition']['code']=='unsupported-construct' and b['condition']['code']=='resource-data-datatype'
   if key=='mergemapControls':
    assert b['sourceText']==a['sourceText'] and "<mergeMap href='child.xtm'/>" in b['sourceText']
    fixture=next(r for r in read(D/'retargetings.json') if r['file']=='tests/xtm-mergemap.lisp')
    assert fixture['afterSource'] in (ROOT/fixture['file']).read_text()
    assert run['executionSourcesSHA256'][fixture['file']]==sha(ROOT/fixture['file'])
   else:assert 'http://www.w3.org/2001/XMLSchema#anyType' in b['sourceText']
   retargets.append({'reportKey':key,'label':a['label'],'before':a,'after':b,'differences':diff(a,b)})
 imported=new['mergemapControls'][0];assert imported['label']=='Occurrence-Reification-import' and imported['sourceMapsPreserved'] and imported['qualifiedParserCalls']==2
 assert len(imported['resolverCalls'])==1 and imported['model']['canonicalNativeReferencesEQ']
 save(out/'retargeted-control-observations.json',retargets)
 originals=[];(out/'actual').mkdir(exist_ok=True)
 assert {x['id'] for x in new['occurrenceReifierOriginals']}==targets
 for row in new['occurrenceReifierOriginals']:
  source=inputs[row['id']];raw=bytes.fromhex(row['sourceHex'])
  assert raw==(ROOT/'vendor/cxtm'/row['id']).read_bytes() and hashlib.sha256(raw).hexdigest()==source['sourceSHA256']
  assert row['status']=='pass'
  if '/invalid/' in row['id']:
   c=row['condition'];assert row['intendedCauseReached'] and c['class']=='REIFICATION-ERROR' and c['code']=='reifier-conflict'
   assert c['detail']=='Topic already reifies a different information item.' and c['line'] is c['column'] is c['sourceKey'] is c['documentIRI'] is None
   frames=row['actualNativeAssignments'];assert len(frames)==1 and frames[0]['assignedItemKind']=='OCCURRENCE' and frames[0]['priorReifiedItemKind']=='TOPIC-MAP' and frames[0]['nativeAssignmentUnchanged']
   assert after[row['id']]['actualOutcome']=='ctm-rejection'
  else:
   assert row['condition'] is None and row['firstDifferentByte'] is None and row['originalOctetsEQ'] and row['qualifiedParserCalls']==1 and row['oldHandlesCanonicalAndLive']
   assert row['model']['canonicalOccurrenceReifierInverseEQ']
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
   assert id in targets
   if '/in/' in id:assert b['byteExact'] and b['condition'] is None
   else:assert b['condition']['class']=='REIFICATION-ERROR' and b['condition']['code']=='reifier-conflict'
   changed.append({'id':id,'reason':'new Occurrence Reification reaches the intended original result','differences':ds})
  elif id in targets:raise AssertionError(id)
  bs=before.get(id,{}).get('status','not-run');ns=after.get(id,{}).get('status','not-run');assert (bs!=ns)==(id in targets)
  matrix.append({'id':id,'before':bs,'after':ns,'registeredStatusChanged':bs!=ns,'diagnosisChanged':bool(ds),'beforeDiagnosis':a,'afterDiagnosis':b})
 assert all(newd[id]==oldd[id] for id in before)
 assert {x['id'] for x in changed}==targets
 save(out/'diagnostic-changes.json',{'originalDiagnoses':124,'changed':len(changed),'unchanged':124-len(changed),'changes':changed})
 save(out/'all-124-original-statuses.json',{'cases':matrix,'registeredChanges':3,'previous107OriginalPASSUnchanged':True})
 faults=[]
 for x in run['runs']:
  if '-control-' not in x['label']:continue
  a=read(PRIOR/(x['label']+'.json'));b=read(out/(x['label']+'.json'));changes=diff(a,b)
  assert a['cases']==b['cases'] and a['statuses']==b['statuses'] and a['checks']==b['checks'] and x['exitCode']==1
  aa=dict(a);bb=dict(b)
  for k in ['scope','occurrenceReifierNative','occurrenceReifierOriginals','occurrenceReifierControls']:aa.pop(k,None);bb.pop(k,None)
  for rt in retargets:
   key=rt['reportKey'];aa[key]=[rt['after'] if row==rt['before'] else row for row in aa[key]]
  assert aa==bb,(x['label'],diff(aa,bb))
  assert not b['occurrenceReifierNative'] and not b['occurrenceReifierOriginals'] and not b['occurrenceReifierControls']
  faults.append({'label':x['label'],'expectedASDFFailureObserved':True,'exitCode':1,'caseRecordsOutcomesAndChecksIdentical':True,'faultCountedAsOriginalPASS':False,'reportDifferences':changes})
 assert len(faults)==113
 save(out/'failure-controls.json',{'retained':113,'new':0,'controls':faults,'allTargetCasesAndChecksUnchanged':True,'failureDriverUnchanged':True})
 retained=[]
 for p in sorted((PRIOR/'retained').glob('*.json')):
  rel=p.relative_to(PRIOR)
  if p.name.endswith('.equivalence.json'):continue
  if p.name=='xtm-mergemap.integration.json':
   aa=read(p);bb=read(out/rel);ds=diff(aa,bb)
   index=next(i for i,row in enumerate(aa['rejections']) if row['label']=='unsupported-occurrence-reification')
   assert ds==[{'path':f'/rejections/{index}/code','before':'UNSUPPORTED-CONSTRUCT','after':'RESOURCE-DATA-DATATYPE'}]
   save(out/'adapter-retargeting.json',{'report':str(rel),'onlyExpectedCodeChanged':True,'checksAndOuterClassAndCauseAndPositionsPreserved':True,'differences':ds,'before':aa['rejections'][index],'after':bb['rejections'][index]})
   continue
  assert p.read_bytes()==(out/rel).read_bytes(),str(rel)
  retained.append({'report':str(rel),'sha256':sha(p),'byteIdentical':True})
 for name in ['ctm.validation.json','ctm.cxtm.json','ctm.encoding.json']:
  assert (out/name).read_bytes()==(PRIOR/name).read_bytes();retained.append({'report':name,'sha256':sha(out/name),'byteIdentical':True})
 assert len(retained)==47;save(out/'retained-reports.json',retained)
 eqpath=next((out/'retained').glob('*.equivalence.json'));eqa=read(PRIOR/eqpath.relative_to(out));eqb=read(eqpath)
 oldpairs={x['id']:x for x in eqa['pairs']};pairs={x['id']:x for x in eqb['pairs']}
 assert oldpairs.keys()==pairs.keys() and all(oldpairs[id]==pairs[id] for id in oldpairs if id!='occurrence-scope-reifier')
 pair=pairs['occurrence-scope-reifier'];assert pair['byteExact'] and pair['nativePropertiesEqual'] and pair['ctmCanonicalEQ'] and pair['xtmCanonicalEQ']
 assert pair['ctmBytes']==pair['xtmBytes'] and pair['firstDifferentByte'] is None and pair['ctmCondition'] is pair['xtmCondition'] is None
 assert sum(x['kind']=='direct-reader-equivalence-pair' for x in eqb['pairs'])==29
 assert sum(x['kind']=='reader-capability-gap-not-equivalence-PASS' for x in eqb['pairs'])==1
 save(out/'equivalence-progress.json',{'previous28PairsAnd3ContrastsAndRemainingGapUnchanged':True,'resolvedCapabilityGap':pair,'checks':len(eqb['checks']),'pairs':29,'remainingGaps':1})
 # The required native gate was really executed before the Reader was changed.
 gate=read(D/'native-before-execution.json');native=read(D/'native-before/report.json')
 assert gate['exitCode']==0 and gate['beforeAnyProductionChange'] and gate['network']==gate['repositoryWrites']=='denied'
 assert gate['executionSourceSHA256']['src/xtm/reader.lisp']==initial['trackedFileSHA256']['src/xtm/reader.lisp']
 for p,h in gate['executionSourceSHA256'].items():
  if p!='src/xtm/reader.lisp':assert sha(ROOT/p)==h
 assert sha(D/'native-before/run.log')==gate['logSHA256'] and sha(D/'native-before/report.json')==gate['reportSHA256']
 assert len(native['checks'])==9 and not native['ReaderInvoked'] and native['originalRegistrationsAdded']==0
 assert native['observations']==new['occurrenceReifierNative'] and all(c in new['checks'] for c in native['checks'])
 save(out/'native-preflight-confirmation.json',{'executedBeforeReaderChange':True,'nativeChecksBefore':9,'sameNativeChecksAndObservationsRepeatedInASDF':True,'nativeExecution':gate})
 prior=read(PRIOR/'execution.json');log=(out/'regression.log').read_text()
 for marker,count in dict(prior['retainedChecks'],**prior['stageChecks']).items():assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',log).group(1))==count
 assert f"CTM-XTM-EQUIVALENCE-PASS: {len(eqb['checks'])} checks; 29 actual reader pairs;" in log
 assert 'Ran 2 tests' in log and 'NFC-ORACLE-PASS: 16294' in log and 'CXML-SUMMARY 146 PASS 0 FAIL' in (out/'xml.log').read_text()
 lock=read(ROOT/'references/corpus-lock.json')
 for f in lock['files']:
  p=ROOT/'vendor/cxtm'/f['path'];assert p.stat().st_size==f['size'] and sha(p)==f['sha256']
 assert protected=={p:sha(ROOT/p) for p in protected}
 save(out/'integrity.json',{'protectedBaseFilesSHA256':protected,'pinnedCorpusFilesVerified':len(lock['files']),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
  'originalsBaselinesHistoricalReportsAndCorpusLockUnchanged':True,'productionChanges':['src/xtm/reader.lisp'],'TMDM_CTM_CXTM_XMLUnchanged':True})
 save(out/'execution.json',{'kind':'slice-22l-XTM-occurrence-reification','baseCommit':BASE,'branch':git('branch','--show-current'),'runtime':'SBCL 2.5.4',
  'startedAtUTC':run['startedAtUTC'],'finishedAtUTC':run['finishedAtUTC'],'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runs':run['runs'],
  'collector':'scripts/validate-slice-22d.py::collect (unchanged)','auditToolSHA256':sha(Path(__file__)),'standaloneXTMChecks':len(labels),'retainedStandaloneXTMChecks':len(old['checks']),
  'newXTMChecks':len(labels)-len(old['checks']),'retainedLispChecks':12100,'retainedChecks':prior['retainedChecks'],'stageChecks':prior['stageChecks'],
  'equivalenceChecks':len(eqb['checks']),'equivalenceReaderPairs':29,'faultControls':113,'allOriginalStatusesCompared':124,'diagnosticChanges':len(changed),'registeredStatusChanges':3,
  'statusesBefore':prior['statusesAfter'],'statusesAfter':{'XTM':{'pass':110,'fail':0,'not-run':14},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':372,'fail':4,'not-run':21}},
  'originalRegistrationsAdded':3,'xmlQualificationChecks':146,'pythonUnitTests':2,'nfcOracleComparisons':16294,'pinnedCorpusFilesVerified':len(lock['files']),
  'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),'knownCTMFailuresUnchanged':prior['knownCTMFailuresUnchanged'],
  'productionChanges':['src/xtm/reader.lisp'],'nativePreflightBeforeReaderChange':gate,'nativeGateChecks':9,'totalFreshProcessesIncludingBeforeGate':120,'newDependencyDownloads':0,'persistentImagesTouched':False,'acceptancePassed':True})
 print(json.dumps({'acceptancePassed':True,'XTMChecks':len(labels),'newOriginalPASS':3,'allOriginalStatusesCompared':124,'diagnosticChanges':len(changed),'faultControls':113}))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--audit-only',action='store_true');a=ap.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=True)
 if not a.audit_only:
  spec=importlib.util.spec_from_file_location('v22d',ROOT/'scripts/validate-slice-22d.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);v.EXECUTION_FILES=SOURCES;v.collect(out,ROOT/'reports/slice-22d/baseline')
 audit(out)
if __name__=='__main__':main()
