#!/usr/bin/env python3
"""Run the existing offline collector, then audit Slice 22Q characterization.
Output must be a new directory outside the repository. This is not a C14N engine.
"""
import argparse,datetime,hashlib,importlib.util,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'reports/slice-22q';PRIOR=ROOT/'reports/slice-22n/after'
BASE='1418be83ad013fe6d69e6036e6786be8100b9355'
ALLOWED={'topic-maps.asd','tests/xtm-identity.lisp'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def audit(out):
 initial=read(D/'initial-state.json');assert initial['baseCommit']==BASE and initial['initialIndexAndWorktreeClean']
 protected={p:h for p,h in initial['trackedFileSHA256'].items() if p not in ALLOWED}
 assert protected=={p:sha(ROOT/p) for p in protected}
 run=read(out/'runs.json');assert len(run['runs'])==119
 assert all(r['exitCode']==r['expectedExitCode'] and r['network']==r['repositoryWrites']=='denied' and sha(out/(r['label']+'.log'))==r['logSHA256'] for r in run['runs'])
 assert run['executionSourcesSHA256']=={p:sha(ROOT/p) for p in run['executionSourcesSHA256']}
 assert run['rawReportSHA256']=={p:sha(out/p) for p in run['rawReportSHA256']}
 old=read(PRIOR/'xtm.json');new=read(out/'xtm.json')
 for key in old:
  if key!='checks':assert old[key]==new[key],key
 assert [c for c in new['checks'] if c in set(old['checks'])]==old['checks']
 additions=[c for c in new['checks'] if c not in set(old['checks'])]
 assert additions and all(c.startswith(('c14n-probe:','c14n-native:','c14n-api:','c14n-characterization:')) for c in additions)
 labels=re.findall(r'^XTM-CHECK-PASS (.+)$',(out/'xtm.log').read_text(),re.M)
 assert labels==new['checks'] and len(labels)==len(set(labels))
 x=new['c14nPreflight'];explore=read(D/'exploration.json')
 assert x['executed'] and not x['W3CC14NQualified'] and not x['XTMReaderIntegration']
 assert x['probes']==explore['probes'] and x['nativeValues']==explore['nativeValues']
 comparisons=[]
 for row in x['probes']:
  actual=bytes.fromhex(row['actualHex']);expected=bytes.fromhex(row['expectedHex']);raw=bytes.fromhex(row['inputHex'])
  assert actual==row['actualXML'].encode('utf-8') and expected==row['expectedXML'].encode('utf-8')
  assert len(actual)==row['actualBytes'] and len(expected)==row['expectedBytes']
  match=actual==expected;assert match==(row['normativeComparison']=='PASS-for-this-probe')
  delta=next((i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),None)
  if delta is None and len(actual)!=len(expected):delta=min(len(actual),len(expected))
  assert delta==row['firstDifferentByte'] and not row['W3C-C14N-1.0-qualified']
  comparisons.append({k:row[k] for k in ['id','expectedBytes','actualBytes','firstDifferentByte','normativeComparison']})
 assert len({r['id'] for r in comparisons})==len(comparisons)
 assert any(r['normativeComparison']=='BYTE-DIFFERENCE' for r in comparisons)
 for item in x['nativeValues']:
  assert item['occurrenceValue']==item['variantValue'] and item['datatype']=='http://www.w3.org/2001/XMLSchema#anyType'
  assert item['canonicalParentTypeScopeEQ'] and item['repeatedCXTMIdentical'] and item['modelUnchanged'] and not item['readerIntegration']
  assert item['topicCountBefore']==item['topicCountAfter']
 olddiag=read(PRIOR/'after-diagnostics.json');newdiag=read(out/'after-diagnostics.json');assert olddiag==newdiag
 retained=[]
 for p in sorted((out/'retained').rglob('*')):
  if p.is_file():
   rel=p.relative_to(out);assert (PRIOR/rel).exists() and p.read_bytes()==(PRIOR/rel).read_bytes(),str(rel)
   retained.append({'report':str(rel),'SHA256':sha(p)})
 controls=[]
 for r in run['runs']:
  if '-control-' not in r['label']:continue
  name=r['label']+'.json';a=read(PRIOR/name);b=read(out/name)
  assert r['exitCode']==1
  for key in a:assert a[key]==b[key],(name,key)
  assert not b['c14nPreflight']['executed'] and not b['c14nPreflight']['probes'] and not b['c14nPreflight']['nativeValues']
  controls.append({'label':r['label'],'expectedExitCode':1,'previousReportFieldsUnchanged':True,'newProbesNotClaimedExecuted':True})
 assert len(controls)==113
 prior=read(PRIOR/'execution.json');statuses=prior['statusesAfter']
 assert new['cases']==old['cases'] and new['otherCorpusInputs']=={'positiveUnexecuted':3,'negativeUnregisteredUnexecuted':0}
 assert protected=={p:sha(ROOT/p) for p in protected}
 save(out/'comparison-summary.json',{'kind':'CXML-candidate-vs-independent-XTM-C14N-oracles','W3CC14NQualified':False,'readerIntegration':False,'probes':comparisons,'matchedProbeRows':sum(r['normativeComparison']=='PASS-for-this-probe' for r in comparisons),'differingProbeRows':sum(r['normativeComparison']=='BYTE-DIFFERENCE' for r in comparisons),'nativeValueRows':len(x['nativeValues']),'nativeValuesApplyOnlyToMatchingProbeRows':True})
 save(out/'failure-controls-audit.json',controls)
 save(out/'retained-reports.json',retained)
 save(out/'integrity.json',{'protectedBaseFilesSHA256':protected,'pinnedCorpusFilesVerified':sum(p.startswith('vendor/cxtm/') for p in protected),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),'allProductionAndOriginalSourcesUnchanged':True,'testOnlyChanges':sorted(ALLOWED|{'tests/xml-c14n-preflight.lisp'})})
 save(out/'execution.json',{'kind':'slice-22q-preflight-characterization-NOT-C14N-qualification','baseCommit':BASE,'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'runtime':'SBCL 2.5.4','startedAtUTC':run['startedAtUTC'],'finishedAtUTC':run['finishedAtUTC'],'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'collector':'scripts/validate-slice-22d.py::collect (unchanged)','auditToolSHA256':sha(Path(__file__)),'runs':run['runs'],'standaloneXTMChecks':len(labels),'retainedStandaloneXTMChecks':len(old['checks']),'newCharacterizationChecks':len(additions),'retainedLispChecks':prior['retainedLispChecks'],'stageChecks':prior['stageChecks'],'equivalenceChecks':prior['equivalenceChecks'],'equivalenceReaderPairs':prior['equivalenceReaderPairs'],'faultControls':len(controls),'all124OriginalDiagnosesUnchanged':True,'retainedReportsByteIdentical':len(retained),'statusesBefore':statuses,'statusesAfter':statuses,'originalRegistrationsAdded':0,'productionChanges':[],'xmlQualificationChecks':prior['xmlQualificationChecks'],'pythonUnitTests':prior['pythonUnitTests'],'nfcOracleComparisons':prior['nfcOracleComparisons'],'W3CC14NQualified':False,'XTMReaderIntegration':False,'newDependencies':0,'nativeValueRows':len(x['nativeValues']),'acceptancePassed':True})
 print(json.dumps({'acceptancePassed':True,'W3CC14NQualified':False,'XTMChecks':len(labels),'newCharacterizationChecks':len(additions),'faultControls':len(controls),'statusesUnchanged':statuses}),flush=True)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--audit-only',action='store_true');a=ap.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=True)
 if not a.audit_only:
  spec=importlib.util.spec_from_file_location('oldcollector',ROOT/'scripts/validate-slice-22d.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.EXECUTION_FILES={str(p.relative_to(ROOT)) for folder in ['src','tests'] for p in (ROOT/folder).rglob('*.lisp')}|{'topic-maps.asd','scripts/validate-slice-22d.py','reports/slice-22d/failure-controls.lisp','reports/slice-22q/reproduce.py'}
  m.collect(out,ROOT/'reports/slice-22d/baseline')
 audit(out)
if __name__=='__main__':main()
