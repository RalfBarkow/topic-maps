#!/usr/bin/env python3
"""Execute the existing offline collector; audit 22U without original reclassification."""
import argparse,datetime,hashlib,importlib.util,json,re,sys
from pathlib import Path
from urllib.parse import urlparse,unquote
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'reports/slice-22u';PRIOR=ROOT/'reports/slice-22t/after'
BASE='b9517b977fca2105422892a14b4cf9fe9790bbba'
ALLOWED={'topic-maps.asd','scripts/fresh-sbcl.lisp'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def audit(out):
 initial=read(D/'initial-state.json');assert initial['baseCommit']==BASE and initial['initialIndexAndWorktreeClean']
 protected={p:h for p,h in initial['trackedFileSHA256'].items() if p not in ALLOWED}
 assert protected=={p:sha(ROOT/p) for p in protected}
 runs=read(out/'runs.json');assert len(runs['runs'])==119
 assert runs['executionSourcesSHA256']=={p:sha(ROOT/p) for p in runs['executionSourcesSHA256']}
 assert runs['rawReportSHA256']=={p:sha(out/p) for p in runs['rawReportSHA256']}
 for r in runs['runs']:
  assert r['exitCode']==r['expectedExitCode'] and r['freshProcess']
  assert r['network']==r['repositoryWrites']==r['hyperdocWrites']=='denied'
  assert sha(out/(r['label']+'.log'))==r['logSHA256']
 faults=[]
 for r in runs['runs']:
  if '-control-' not in r['label']:continue
  name=r['label']+'.json';assert (out/name).read_bytes()==(PRIOR/name).read_bytes()
  assert r['exitCode']==1;faults.append({'label':r['label'],'reportByteIdenticalTo22T':True,'expectedExitCode':1})
 assert len(faults)==113
 for name in ['xtm.json','after-diagnostics.json','ctm.validation.json','ctm.cxtm.json','ctm.encoding.json']:
  assert (out/name).read_bytes()==(PRIOR/name).read_bytes(),name
 assert len(read(out/'after-diagnostics.json'))==124
 newrel='retained/core.json.project-work.json';retained=[]
 for p in (PRIOR/'retained').rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(PRIOR);assert p.read_bytes()==(out/rel).read_bytes(),str(rel)
  retained.append({'report':str(rel),'SHA256':sha(p)})
 assert {str(p.relative_to(out)) for p in (out/'retained').rglob('*') if p.is_file()}=={r['report'] for r in retained}|{newrel}
 prep,oldprep=read(out/'source-preparation.json'),read(PRIOR/'source-preparation.json')
 assert prep['sources']==oldprep['sources'] and prep['patches']==oldprep['patches']
 project=read(out/newrel);obs=project['observation'];checks=project['checks']
 assert len(checks)==len(set(checks))==27 and all(c.startswith('project-work:') for c in checks)
 assert project['productionChanges'] is False and project['originalRegistrationsAdded']==0
 isolated=read(D/'isolated.json')['observation']
 assert all(obs[k]==v for k,v in isolated.items())
 assert obs['source']==(ROOT/'examples/project-work.ctm').read_text()
 assert obs['nativeReferencesCurrent'] and obs['sourceUnchanged'] and obs['reparsedOriginalMatchesBefore']
 before,after=bytes.fromhex(obs['beforeCXTMHex']),bytes.fromhex(obs['afterCXTMHex'])
 assert len(before)==obs['beforeBytes'] and len(after)==obs['afterBytes'] and before!=after
 assert next(i for i,(a,b) in enumerate(zip(before,after)) if a!=b)==obs['firstDifferentByteZeroBased']
 facts=obs['historicalFactsFromNativeItems'];historical=read(PRIOR/'execution.json')
 assert facts['commitHash']==BASE and facts['sliceStatus']=='abgeschlossen'
 assert facts['questionStatus']=='offene normative Frage'
 assert facts['evidenceSummary']==f"{historical['equivalenceReaderPairs']} Reader-Paare, {historical['equivalenceContrasts']} Kontraste, {historical['equivalenceChecks']} Checks."
 assert historical['acceptancePassed']
 sources=[]
 for key in ['questionSource','sliceSource','evidenceDocument']:
  u=urlparse(facts[key]);assert u.scheme=='file' and not u.netloc and not u.fragment
  p=Path(unquote(u.path));assert p.is_relative_to(ROOT) and str(p.relative_to(ROOT)) in protected
  assert sha(p)==protected[str(p.relative_to(ROOT))]
  sources.append({'nativeFact':key,'IRI':facts[key],'repositorySource':str(p.relative_to(ROOT)),'SHA256':sha(p)})
 disposition=(ROOT/'docs/slice-22o-qualified-xtm-corpus-disposition.md').read_text()
 assert 'Offene normative Frage' in disposition and '**Registrierter Status bleibt NOT-RUN.**' in disposition
 assert facts['disposition']=='NOT-RUN beibehalten; keine normative Zyklussemantik festgelegt.'
 reg=(out/'regression.log').read_text();previous=read(PRIOR/'execution.json')
 core=read(ROOT/'reports/slice-22d/baseline/execution.json')['retainedChecks'];assert sum(core.values())==12100
 for marker,count in dict(core,**previous['stageChecks'],**{'PROJECT-WORK':27}).items():
  assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',reg).group(1))==count,marker
 assert 'CTM-XTM-EQUIVALENCE-PASS: 728 checks; 34 actual reader pairs; 4 contrasts; 0 capability gaps.' in reg
 assert 'Ran 2 tests' in reg and 'NFC-ORACLE-PASS: 16294' in reg
 assert 'CXML-SUMMARY 146 PASS 0 FAIL' in (out/'xml.log').read_text()
 assert protected=={p:sha(ROOT/p) for p in protected}
 (out/'project-before.cxtm').write_bytes(before);(out/'project-after.cxtm').write_bytes(after)
 (out/'project-before-native.sexp').write_text(obs['beforeNativeView']+'\n')
 (out/'project-after-native.sexp').write_text(obs['afterNativeView']+'\n')
 (out/'project-repl.txt').write_text(obs['transcript'])
 save(out/'failure-controls-audit.json',faults);save(out/'retained-reports.json',retained)
 save(out/'source-grounding.json',{'historicalFactsReadFromActualNativeItems':facts,'verifiedSources':sources,'historicalExecutionAccepted':True,'newNormativeDecision':False,'canonicalDifferenceZeroBased':obs['firstDifferentByteZeroBased']})
 save(out/'diagnostic-changes.json',{'observations':124,'changed':0,'registrationsAdded':0,'retargetings':[]})
 save(out/'integrity.json',{'protectedBaseFilesSHA256':protected,'protectedBaseFileCount':len(protected),'pinnedCorpusFilesVerified':sum(p.startswith('vendor/cxtm/') for p in protected),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),'allProductionSourcesUnchanged':True,'allowedTrackedChanges':sorted(ALLOWED)})
 save(out/'execution.json',{'kind':'slice-22u-native-project-work-example-not-corpus-registration','baseCommit':BASE,'runtime':'SBCL 2.5.4','startedAtUTC':runs['startedAtUTC'],'finishedAtUTC':runs['finishedAtUTC'],'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runs':runs['runs'],'runCount':119,'faultControls':113,'projectWorkChecks':27,'exampleSourceSHA256':sha(ROOT/'examples/project-work.ctm'),'exampleLispSHA256':sha(ROOT/'examples/project-work.lisp'),'retainedCoreChecks':12100,'standaloneXTMChecks':4327,'equivalenceChecks':728,'equivalencePairs':34,'equivalenceContrasts':4,'xmlQualificationChecks':146,'pythonTests':2,'nfcComparisons':16294,'stageChecks':previous['stageChecks'],'statusesBefore':previous['statusesAfter'],'statusesAfter':previous['statusesAfter'],'all124OriginalDiagnosesUnchanged':True,'originalRegistrationsAdded':0,'retargetings':0,'newProductionAPIs':0,'allRetainedReportsByteIdentical':True,'retainedReportCount':len(retained),'acceptancePassed':True})
 print(json.dumps({'acceptancePassed':True,'exampleChecks':27,'nativeTopics':obs['TopicCountBeforeAndAfter'],'nativeAssociations':obs['associationCountBeforeAndAfter'],'beforeBytes':len(before),'afterBytes':len(after),'faultControls':113,'statuses':previous['statusesAfter']}),flush=True)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--audit-only',action='store_true');a=ap.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT)
 if not a.audit_only:
  spec=importlib.util.spec_from_file_location('retained_collector',D/'collect.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.collect(out)
 audit(out)
if __name__=='__main__':main()
