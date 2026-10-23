#!/usr/bin/env python3
"""Slice 22N offline execution and acceptance audit using the existing collector.
Use an unused --output outside the repository; --audit-only rechecks saved runs.
"""
import argparse,datetime,hashlib,importlib.util,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'reports/slice-22n';PRIOR=ROOT/'reports/slice-22m/after'
BASE='acc9eb65b0cce71409ad84841f082f5ca125c839'
ALLOWED={'tests/xtm-associations.lisp', 'tests/xtm-map-reification.lisp', 'tests/xtm-name-scopes.lisp', 'tests/ctm-xtm-equivalence.lisp', 'tests/xtm-identity.lisp', 'tests/xtm-association-reification.lisp', 'topic-maps.asd', 'src/xtm/reader.lisp', 'tests/xtm-occurrence-reification.lisp'}
SOURCES=ALLOWED|{'tests/xtm-role-reifier-native.lisp','tests/xtm-role-reification.lisp','reports/slice-22n/api-preflight.lisp','scripts/validate-slice-22d.py','reports/slice-22d/failure-controls.lisp'}
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
 assert old['statuses']=={'pass':115,'fail':0,'unsupported':0,'not-run':0}
 assert new['statuses']=={'pass':121,'fail':0,'unsupported':0,'not-run':0} and new['otherCorpusInputs']=={'positiveUnexecuted':3,'negativeUnregisteredUnexecuted':0}
 assert old['cases']==new['cases'][:len(old['cases'])] and set(after)-set(before)==targets
 assert len(after)==len(new['cases']) and all(after[id]['status']=='pass' for id in targets)
 assert [c for c in new['checks'] if c in set(old['checks'])]==old['checks']
 labels=re.findall(r'^XTM-CHECK-PASS (.+)$',(out/'xtm.log').read_text(),re.M)
 assert labels==new['checks'] and len(labels)==len(set(labels))==3743
 permitted={'scope','statuses','otherCorpusInputs','checks','cases','scopeControls','mapReifierControls','associationControls','occurrenceReifierControls','associationReifierControls','mergemapControls'}
 for key in old:
  if key not in permitted:assert old[key]==new[key],key
 retargets=[]
 for key,count in {'scopeControls':1,'mapReifierControls':1,'associationControls':4,'occurrenceReifierControls':2,'associationReifierControls':1}.items():
  assert len(old[key])==len(new[key]);changed=[(a,b) for a,b in zip(old[key],new[key]) if a!=b];assert len(changed)==count,(key,changed)
  for a,b in changed:
   assert a['label']==b['label'] and a['condition']['class']=='XTM-UNSUPPORTED' and b['condition']['class']=='XTM-REJECTION'
   assert a['condition']['code']=='unsupported-construct' and b['condition']['code']=='invalid-percent-escape'
   assert a['condition']['detail']=='XTM role reification is not implemented in this subset.'
   assert b['condition']['detail']=='Expected two hexadecimal digits.'
   expected=re.sub(r"(<role reifier=')([^']+)(')",lambda m:m.group(1)+m.group(2)+'%GG'+m.group(3),a['sourceText'],count=1)
   assert b['sourceText']==expected
   for k in ['sourceKey','documentIRI','line']:assert a['condition'][k]==b['condition'][k]
   retargets.append({'reportKey':key,'label':a['label'],'before':a,'after':b,'differences':diff(a,b)})
 assert new['mergemapControls'][1:]==old['mergemapControls']
 imported=new['mergemapControls'][0];assert imported['label']=='Role-Reification-import' and imported['sourceMapsPreserved'] and imported['qualifiedParserCalls']==2
 assert len(imported['resolverCalls'])==1 and imported['model']['canonicalNativeReferencesEQ']
 for fixture in read(D/'retargetings.json'):
  if 'afterSource' in fixture:assert fixture['afterSource'] in (ROOT/fixture['file']).read_text()
 save(out/'retargeted-control-observations.json',retargets)
 originals=[];(out/'actual').mkdir(exist_ok=True)
 assert {x['id'] for x in new['roleReifierOriginals']}==targets
 for row in new['roleReifierOriginals']:
  source=inputs[row['id']];raw=bytes.fromhex(row['sourceHex'])
  assert raw==(ROOT/'vendor/cxtm'/row['id']).read_bytes() and hashlib.sha256(raw).hexdigest()==source['sourceSHA256']
  assert row['status']=='pass' and row['originalOctetsEQ'] and row['qualifiedParserCalls']==1
  if '/invalid/' in row['id']:
   c=row['condition'];assert row['intendedCauseReached'] and c['class']=='REIFICATION-ERROR' and c['code']=='reifier-conflict'
   assert c['detail']=='Topic already reifies a different information item.' and c['line'] is c['column'] is c['sourceKey'] is c['documentIRI'] is None
   assert len(row['actualNativeAssignments'])==1
   frame=row['actualNativeAssignments'][0]
   assert frame['assignedItemKind']==frame['priorReifiedItemKind']=='ASSOCIATION-ROLE'
   assert frame['actualMapAssociationCount']==frame['actualMapRoleCount']==2
   assert frame['sameRoleTypeAndPlayerEQ'] and frame['differentParentsEQ'] and frame['nativeAssignmentUnchanged']
   assert frame['assignedParentTypeII']==[row['documentIRI']+'#assoctype2'] and frame['priorParentTypeII']==[row['documentIRI']+'#assoctype']
   assert after[row['id']]['actualOutcome']=='ctm-rejection'
   originals.append(dict(row,sourceSHA256=source['sourceSHA256'],baselineSHA256=None))
  else:
   assert row['condition'] is None and row['firstDifferentByte'] is None and row['oldHandlesCanonicalAndLive'] and row['model']['canonicalRoleReifierInverseEQ']
   actual=row['actualCXTM'].encode();expected=(ROOT/'vendor/cxtm/xtm2/baseline'/(Path(row['id']).name+'.cxtm')).read_bytes()
   assert actual==expected==row['expectedCXTM'].encode() and len(actual)==row['actualBytes']==row['expectedBytes']==source['baselineBytes']
   assert hashlib.sha256(expected).hexdigest()==source['baselineSHA256'] and after[row['id']]['actualOutcome']=='cxtm-match'
   p=out/'actual'/(Path(row['id']).name+'.cxtm');p.write_bytes(actual)
   originals.append(dict(row,actualSHA256=sha(p),completeByteExact=True,sourceSHA256=source['sourceSHA256'],baselineSHA256=source['baselineSHA256']))
 save(out/'original-contracts.json',originals)
 # Compare all 124 actual Reader diagnoses and registered statuses.
 oldd={x['id']:x for x in read(PRIOR/'after-diagnostics.json')};newd={x['id']:x for x in read(out/'after-diagnostics.json')}
 inventory=sorted('xtm2/'+sub+'/'+p.name for sub in ['in','invalid'] for p in (ROOT/'vendor/cxtm/xtm2'/sub).glob('*.xtm'))
 assert len(inventory)==124 and set(inventory)==set(oldd)==set(newd)
 changes=[];matrix=[]
 for id in inventory:
  a,b=oldd[id],newd[id];ds=diff(a,b)
  if ds:
   assert id in targets,id
   if '/in/' in id:assert b['byteExact'] and b['condition'] is None
   else:assert b['condition']['class']=='REIFICATION-ERROR' and b['condition']['code']=='reifier-conflict'
   changes.append({'id':id,'reason':'new Role Reification reaches intended original result','differences':ds})
  elif id in targets:raise AssertionError(id)
  bs=before.get(id,{}).get('status','not-run');ns=after.get(id,{}).get('status','not-run');assert (bs!=ns)==(id in targets)
  matrix.append({'id':id,'before':bs,'after':ns,'registeredStatusChanged':bs!=ns,'diagnosisChanged':bool(ds),'beforeDiagnosis':a,'afterDiagnosis':b})
 assert all(newd[id]==oldd[id] for id in before) and targets=={x['id'] for x in changes}
 save(out/'diagnostic-changes.json',{'originalDiagnoses':124,'changed':len(changes),'unchanged':124-len(changes),'changes':changes})
 save(out/'all-124-original-statuses.json',{'cases':matrix,'registeredChanges':6,'previous115OriginalPASSUnchanged':True})
 faults=[]
 for x in run['runs']:
  if '-control-' not in x['label']:continue
  a=read(PRIOR/(x['label']+'.json'));b=read(out/(x['label']+'.json'));ds=diff(a,b)
  assert a['cases']==b['cases'] and a['statuses']==b['statuses'] and a['checks']==b['checks'] and x['exitCode']==1
  aa=dict(a);bb=dict(b)
  for k in ['scope','roleReifierNative','roleReifierOriginals','roleReifierControls']:aa.pop(k,None);bb.pop(k,None)
  for rt in retargets:
   key=rt['reportKey'];aa[key]=[rt['after'] if row==rt['before'] else row for row in aa[key]]
  assert aa==bb,(x['label'],diff(aa,bb))
  assert not b['roleReifierNative'] and not b['roleReifierOriginals'] and not b['roleReifierControls']
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
 oldpairs={x['id']:x for x in eqa['pairs']};pairs={x['id']:x for x in eqb['pairs']};gap='association-role-scope-reifiers'
 assert oldpairs.keys()==pairs.keys() and all(oldpairs[id]==pairs[id] for id in oldpairs if id!=gap)
 a,b=oldpairs[gap],pairs[gap];assert a['ctmSource']==b['ctmSource'] and a['xtmSource']==b['xtmSource']
 assert b['kind']=='direct-reader-equivalence-pair' and b['nativePropertiesEqual'] and b['ctmCanonicalEQ'] and b['xtmCanonicalEQ']
 assert b['byteExact'] and b['firstDifferentByte'] is None and b['ctmCondition'] is b['xtmCondition'] is None and b['ctmBytes']==b['xtmBytes']
 assert a['ctmCXTM']==b['ctmCXTM']==b['xtmCXTM']
 oldgapchecks=[c for c in eqa['checks'] if 'gap:'+gap in c];assert len(oldgapchecks)==2
 remaining=[c for c in eqa['checks'] if c not in oldgapchecks]
 assert [c for c in eqb['checks'] if c in set(remaining)]==remaining
 assert sum(x['kind']=='direct-reader-equivalence-pair' for x in eqb['pairs'])==30 and not any(x['kind']=='reader-capability-gap-not-equivalence-PASS' for x in eqb['pairs'])
 save(out/'equivalence-progress.json',{'allPrevious29PairsAnd3ContrastsUnchanged':True,'resolvedGapOriginalSourcesUnchanged':True,'checks':len(eqb['checks']),'actualPairs':30,'remainingGaps':0,'before':a,'after':b,'replacedGapChecks':oldgapchecks})
 # Native gate really executed on the original Reader, before its edit.
 gate=read(D/'native-before-execution.json');native=read(D/'native-before/report.json')
 assert gate['exitCode']==0 and gate['beforeAnyProductionChange'] and gate['network']==gate['repositoryWrites']=='denied'
 assert gate['executionSourceSHA256']['src/xtm/reader.lisp']==initial['trackedFileSHA256']['src/xtm/reader.lisp']
 for p,h in gate['executionSourceSHA256'].items():
  if p!='src/xtm/reader.lisp':assert sha(ROOT/p)==h
 assert sha(D/'native-before/run.log')==gate['logSHA256'] and sha(D/'native-before/report.json')==gate['reportSHA256']
 assert len(native['checks'])==15 and not native['ReaderInvoked'] and native['originalRegistrationsAdded']==0
 assert native['observations']==new['roleReifierNative'] and all(c in new['checks'] for c in native['checks'])
 assert len(new['roleReifierControls'])==40
 save(out/'native-preflight-confirmation.json',{'executedBeforeReaderChange':True,'nativeChecksBefore':15,'sameNativeChecksAndObservationsRepeatedInASDF':True,'nativeExecution':gate})
 prior=read(PRIOR/'execution.json');log=(out/'regression.log').read_text()
 for marker,count in dict(prior['retainedChecks'],**prior['stageChecks']).items():assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',log).group(1))==count
 assert f"CTM-XTM-EQUIVALENCE-PASS: {len(eqb['checks'])} checks; 30 actual reader pairs;" in log
 assert 'Ran 2 tests' in log and 'NFC-ORACLE-PASS: 16294' in log and 'CXML-SUMMARY 146 PASS 0 FAIL' in (out/'xml.log').read_text()
 lock=read(ROOT/'references/corpus-lock.json')
 for f in lock['files']:
  p=ROOT/'vendor/cxtm'/f['path'];assert p.stat().st_size==f['size'] and sha(p)==f['sha256']
 assert protected=={p:sha(ROOT/p) for p in protected}
 save(out/'integrity.json',{'protectedBaseFilesSHA256':protected,'pinnedCorpusFilesVerified':len(lock['files']),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
  'originalsBaselinesHistoricalReportsAndCorpusLockUnchanged':True,'productionChanges':['src/xtm/reader.lisp'],'TMDM_CTM_CXTM_XMLUnchanged':True})
 save(out/'execution.json',{'kind':'slice-22n-XTM-role-reification','baseCommit':BASE,'branch':git('branch','--show-current'),'runtime':'SBCL 2.5.4',
  'startedAtUTC':run['startedAtUTC'],'finishedAtUTC':run['finishedAtUTC'],'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runs':run['runs'],
  'collector':'scripts/validate-slice-22d.py::collect (unchanged)','auditToolSHA256':sha(Path(__file__)),'standaloneXTMChecks':len(labels),'retainedStandaloneXTMChecks':len(old['checks']),
  'newXTMChecks':len(labels)-len(old['checks']),'retainedLispChecks':12100,'retainedChecks':prior['retainedChecks'],'stageChecks':prior['stageChecks'],
  'equivalenceChecks':len(eqb['checks']),'equivalenceReaderPairs':30,'faultControls':113,'allOriginalStatusesCompared':124,'diagnosticChanges':len(changes),'registeredStatusChanges':6,
  'statusesBefore':prior['statusesAfter'],'statusesAfter':{'XTM':{'pass':121,'fail':0,'not-run':3},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':383,'fail':4,'not-run':10}},
  'originalRegistrationsAdded':6,'xmlQualificationChecks':146,'pythonUnitTests':2,'nfcOracleComparisons':16294,'pinnedCorpusFilesVerified':len(lock['files']),
  'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),'knownCTMFailuresUnchanged':prior['knownCTMFailuresUnchanged'],
  'productionChanges':['src/xtm/reader.lisp'],'nativePreflightBeforeReaderChange':gate,'nativeGateChecks':15,'totalFreshProcessesIncludingBeforeGate':120,'newDependencyDownloads':0,'persistentImagesTouched':False,'acceptancePassed':True})
 print(json.dumps({'acceptancePassed':True,'XTMChecks':len(labels),'newOriginalPASS':6,'allOriginalStatusesCompared':124,'diagnosticChanges':len(changes),'faultControls':113}))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--audit-only',action='store_true');a=ap.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=True)
 if not a.audit_only:
  spec=importlib.util.spec_from_file_location('v22d',ROOT/'scripts/validate-slice-22d.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);v.EXECUTION_FILES=SOURCES;v.collect(out,ROOT/'reports/slice-22d/baseline')
 audit(out)
if __name__=='__main__':main()
