#!/usr/bin/env python3
"""Validate direct CTM/XTM semantic pairs via existing ASDF/offline executors.
--audit-only verifies saved executions; it starts no test processes.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import subprocess
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'reports/slice-22f';PRIOR=ROOT/'reports/slice-22e/after'
BASE='aeebbc7c6fdbf26642db0b7b5a358a3d04d62cca'
ALLOWED={'topic-maps.asd'}
SOURCES={'topic-maps.asd','tests/ctm-xtm-equivalence.lisp','reports/slice-22f/fresh-equivalence.lisp','scripts/validate-slice-22d.py','reports/slice-22d/failure-controls.lisp'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def git(*a,cwd=ROOT):return subprocess.check_output(['git',*a],cwd=cwd,text=True).strip()
def legacy():
 spec=importlib.util.spec_from_file_location('slice22d',ROOT/'scripts/validate-slice-22d.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);return v

def audit(out,initial):
 state=read(initial);assert state['baseCommit']==BASE and state['initialIndexAndWorktreeClean']
 assert set(git('diff','--name-only',BASE).splitlines())&set(state['trackedFileSHA256'])<=ALLOWED
 protected={p:h for p,h in state['trackedFileSHA256'].items() if p not in ALLOWED}
 assert protected=={p:sha(ROOT/p) for p in protected}
 run=read(out/'runs.json');assert len(run['runs'])==119
 assert all(x['exitCode']==x['expectedExitCode'] and sha(out/(x['label']+'.log'))==x['logSHA256'] for x in run['runs'])
 assert run['executionSourcesSHA256']=={p:sha(ROOT/p) for p in run['executionSourcesSHA256']}
 assert run['rawReportSHA256']=={p:sha(out/p) for p in run['rawReportSHA256']}
 # Existing standalone XTM behavior and registry are completely unchanged.
 assert (out/'xtm.json').read_bytes()==(PRIOR/'xtm.json').read_bytes()
 assert read(out/'xtm.json')['statuses']=={'pass':72,'fail':0,'unsupported':0,'not-run':0}
 assert (out/'after-diagnostics.json').read_bytes()==(PRIOR/'after-diagnostics.json').read_bytes()
 assert len(read(out/'after-diagnostics.json'))==124
 faults=[]
 for x in run['runs']:
  if '-control-' not in x['label']:continue
  p=x['label']+'.json';assert (out/p).read_bytes()==(PRIOR/p).read_bytes(),p
  faults.append({'label':x['label'],'exitCode':x['exitCode'],'expectedASDFFailureObserved':True,'behavioralReportByteIdentical':True,'sha256':sha(out/p)})
 assert len(faults)==113
 save(out/'failure-controls.json',{'retained':113,'new':0,'controls':faults,'allFaultReportsByteIdentical':True})
 unchanged=[]
 for old in [*sorted((PRIOR/'retained').glob('*.json')),*[PRIOR/f'ctm.{s}.json' for s in ['validation','cxtm','encoding']]]:
  rel=old.relative_to(PRIOR);assert old.read_bytes()==(out/rel).read_bytes(),str(rel)
  unchanged.append({'report':str(rel),'sha256':sha(old),'byteIdentical':True})
 assert len(unchanged)==48
 save(out/'retained-reports.json',unchanged)
 prior=read(PRIOR/'execution.json');log=(out/'regression.log').read_text()
 for marker,count in dict(prior['retainedChecks'],**prior['stageChecks']).items():
  assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',log).group(1))==count
 assert 'Ran 2 tests' in log and 'NFC-ORACLE-PASS: 16294' in log
 assert 'CXML-SUMMARY 146 PASS 0 FAIL' in (out/'xml.log').read_text()
 eq=read(out/'retained/xtm-mergemap.equivalence.json');assert eq['condition'] is None and eq['originalCorpusRegistrationsAdded']==0
 labels=re.findall(r'^XTM-MERGEMAP-CHECK-PASS (equivalence:.+)$',log,re.M)
 assert labels==eq['checks'] and len(labels)==len(set(labels))==487
 assert 'CTM-XTM-EQUIVALENCE-PASS: 487 checks; 27 actual reader pairs; 3 contrasts; 3 explicit capability gaps.' in log
 pairs=[p for p in eq['pairs'] if p['kind']=='direct-reader-equivalence-pair']
 contrasts=[p for p in eq['pairs'] if p['kind']=='intentional-semantic-difference']
 gaps=[p for p in eq['pairs'] if p['kind']=='reader-capability-gap-not-equivalence-PASS']
 assert len(pairs)==27 and len(contrasts)==3 and len(gaps)==3
 allids=[p['id'] for p in eq['pairs']];assert len(allids)==len(set(allids))==33
 (out/'actual').mkdir(exist_ok=True);summary=[]
 for p in pairs:
  assert p['nativePropertiesEqual'] and p['ctmCanonicalEQ'] and p['xtmCanonicalEQ'] and not p['crossMapEQRequired']
  assert p['ctmCondition'] is None and p['xtmCondition'] is None and p['byteExact'] and p['firstDifferentByte'] is None
  assert p['ctmTrace']['entryPoint']=='topic-maps.ctm:deserialize-string' and p['xtmTrace']['entryPoint']=='topic-maps.xtm:deserialize-octets'
  assert p['ctmTrace']['sourceKey']!=p['xtmTrace']['sourceKey']
  assert p['ctmTrace']['documentIRI']==p['xtmTrace']['documentIRI']==p['documentIRI']==p['canonicalBaseIRI']
  assert p['ctmModel']==p['xtmModel']
  ac=p['ctmCXTM'].encode();bc=p['xtmCXTM'].encode();assert ac==bc and len(ac)==p['ctmBytes']==p['xtmBytes']
  name=p['id'];(out/'actual'/(name+'.ctm.cxtm')).write_bytes(ac);(out/'actual'/(name+'.xtm.cxtm')).write_bytes(bc)
  summary.append({'id':name,'documentIRI':p['documentIRI'],'nativeCounts':p['ctmModel']['counts'],'ctmBytes':len(ac),'xtmBytes':len(bc),
   'ctmSHA256':hashlib.sha256(ac).hexdigest(),'xtmSHA256':hashlib.sha256(bc).hexdigest(),'sourceCTMSHA256':hashlib.sha256(p['ctmSource'].encode()).hexdigest(),
   'sourceXTMSHA256':hashlib.sha256(p['xtmSource'].encode()).hexdigest(),'firstDifferentByte':None,'completeByteExact':True})
 for p in contrasts:
  a=p['ctmCXTM'].encode();b=p['xtmCXTM'].encode();assert a!=b and not p['nativePropertiesEqual'] and not p['byteExact']
  assert p['firstDifferentByte']==next(i for i,(x,y) in enumerate(zip(a,b)) if x!=y)
 for p in gaps:
  assert p['ctmCondition'] is None and p['ctmModel'] and p['xtmModel'] is None and not p['successfulReaderPair']
  assert p['xtmCondition']['class']=='XTM-UNSUPPORTED' and p['xtmCondition']['code']=='unsupported-construct'
 save(out/'equivalence-summary.json',{'checks':487,'actualPairs':27,'intentionalDifferences':3,'readerCapabilityGaps':3,'pairs':summary,'contrasts':contrasts,'gaps':gaps,'originalCorpusRegistrationsAdded':0})
 save(out/'diagnostic-changes.json',{'originalDiagnoses':124,'changed':0,'byteIdenticalToSlice22E':True,'registeredStatusesChanged':False})
 lock=read(ROOT/'references/corpus-lock.json')
 for e in lock['files']:
  p=ROOT/'vendor/cxtm'/e['path'];assert p.stat().st_size==e['size'] and sha(p)==e['sha256']
 assert protected=={p:sha(ROOT/p) for p in protected}
 hd=Path('/Users/rgb/workspace/hyperdoc-dreyeck-ch');assert git('rev-parse','HEAD',cwd=hd)==state['hyperdocHEAD'] and git('status','--porcelain=v1',cwd=hd)==state['hyperdocStatus']
 save(out/'integrity.json',{'baseCommit':BASE,'protectedBaseFilesSHA256':protected,'executionSourcesSHA256':run['executionSourcesSHA256'],
  'pinnedCorpusFilesVerified':len(lock['files']),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
  'productionSourcesUnchanged':True,'originalSourcesBaselinesCorpusLockHistoricalReportsUnchanged':True,'hyperdocUnchanged':True})
 save(out/'execution.json',{'kind':'slice-22f-direct-CTM-XTM-semantic-equivalence','baseCommit':BASE,'branch':git('branch','--show-current'),
  'runtime':'SBCL 2.5.4','startedAtUTC':run['startedAtUTC'],'finishedAtUTC':run['finishedAtUTC'],'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'runs':run['runs'],'collector':'scripts/validate-slice-22d.py::collect (unchanged)','auditToolSHA256':sha(Path(__file__)),
  'equivalenceChecks':487,'actualReaderPairs':27,'intentionalSemanticDifferences':3,'documentedReaderCapabilityGaps':3,
  'retainedStandaloneXTMChecks':2704,'retainedLispChecks':12100,'retainedChecks':prior['retainedChecks'],'stageChecks':prior['stageChecks'],
  'xmlQualificationChecks':146,'faultControls':113,'newFaultControls':0,'originalDiagnoses':124,'diagnosticChanges':0,
  'statusesBefore':prior['statusesAfter'],'statusesAfter':prior['statusesAfter'],'originalCorpusRegistrationsAdded':0,
  'pythonUnitTests':2,'nfcOracleComparisons':16294,'retainedReportsByteIdentical':48,
  'pinnedCorpusFilesVerified':len(lock['files']),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
  'knownCTMFailuresUnchanged':prior['knownCTMFailuresUnchanged'],'productionChanges':[],'newDependencyDownloads':0,'persistentImagesTouched':False,'acceptancePassed':True})
 print(json.dumps({'acceptancePassed':True,'readerPairs':27,'equivalenceChecks':487,'faultControls':113,'statuses':prior['statusesAfter']}))

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--initial',type=Path,default=D/'initial-state.json');ap.add_argument('--audit-only',action='store_true');a=ap.parse_args()
 out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=True)
 if not a.audit_only:
  v=legacy();v.EXECUTION_FILES=SOURCES;v.collect(out,ROOT/'reports/slice-22d/baseline')
 audit(out,a.initial)
if __name__=='__main__':main()
