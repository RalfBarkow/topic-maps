#!/usr/bin/env python3
"""Reproduce/audit 22S through the existing offline harness; no downloads.
Use --audit-only for SAVED runs. Output must be outside the repository.
"""
import argparse, datetime, hashlib, importlib.util, json, re, sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
D = ROOT/'reports/slice-22s'
PRIOR = ROOT/'reports/slice-22r/after'
BASE = 'c1fa847c85017d4edf5c2439c772d903261e5a12'

def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, v): p.write_text(json.dumps(v, indent=2, ensure_ascii=False)+'\n')
def differences(a,b,path=''):
    if a==b: return []
    if isinstance(a,dict) and isinstance(b,dict):
        return [d for k in sorted(set(a)|set(b)) for d in differences(a.get(k),b.get(k),path+'/'+k)]
    if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        return [d for i,(x,y) in enumerate(zip(a,b)) for d in differences(x,y,path+'/'+str(i))]
    return [{'path':path,'before':a,'after':b}]

def check_control_row(a,b,where):
    if a==b: return None
    ca,cb=a.get('condition'),b.get('condition')
    assert ca and cb and ca['class']==cb['class']=='XTM-UNSUPPORTED',where
    assert ca['code']=='resource-data-datatype' and cb['code'] in {'resource-resolver-required','cyclic-mergemap'},where
    assert all(a.get(k)==b.get(k) for k in set(a)|set(b) if k not in {'condition','sourceText','expectedCode'}),where
    assert all(ca.get(k)==cb.get(k) for k in set(ca)|set(cb) if k not in {'code','detail','message','line','column'}),where
    return {'where':where,'purpose':'retain real Unsupported non-PASS and source diagnostic checks',
            'before':a,'after':b,'differences':differences(a,b)}

def compare_existing(a,b,where):
    changed=[]
    for k,v in a.items():
        if k=='checks':
            assert [c for c in b[k] if c in set(v)]==v,(where,k)
        elif k=='cases':
            assert len(v)==len(b[k])
            for old,new in zip(v,b[k]):
                assert {q:z for q,z in old.items() if q!='diagnostics'}=={q:z for q,z in new.items() if q!='diagnostics'},(where,k)
                if old!=new:
                    # Fault Unsupported payload changes code/text/position only.
                    ds=differences(old,new)
                    assert all('/diagnostics/' in d['path'] for d in ds),(where,ds)
                    changed.append({'where':where+'/cases/'+old['id'],'differences':ds})
        elif k.endswith('Controls'):
            assert len(v)==len(b[k]),(where,k)
            for i,(old,new) in enumerate(zip(v,b[k])):
                row=check_control_row(old,new,where+'/'+k+'/'+str(i))
                if row:changed.append(row)
        elif v!=b[k] and isinstance(v,list):
            assert len(v)==len(b[k]),(where,k)
            for i,(old,new) in enumerate(zip(v,b[k])):
                row=check_control_row(old,new,where+'/'+k+'/'+str(i))
                if row:changed.append(row)
        else: assert v==b[k],(where,k)
    return changed

def audit(out):
    initial=read(D/'initial-state.json');scope=read(D/'change-scope.json')
    assert initial['baseCommit']==BASE and initial['initialIndexAndWorktreeClean']
    allowed=set(scope['allowedTrackedChanges'])
    assert all(p in {'src/xtm/reader.lisp','topic-maps.asd','tests/ctm-xtm-mergemap.lisp'} or p.startswith('tests/xtm-') for p in allowed)
    protected={p:h for p,h in initial['trackedFileSHA256'].items() if p not in allowed}
    assert protected=={p:sha(ROOT/p) for p in protected}
    pre=read(D/'integration-preflight-run.json');proof=read(D/'integration-preflight.json')
    assert pre['exitCode']==0 and pre['readerMatchesBase'] and proof['qualificationPassed']
    assert pre['readerSHA256']==initial['trackedFileSHA256']['src/xtm/reader.lisp']==scope['preflightReaderSHA256']
    assert scope['preflightToolSHA256']==sha(D/'integration-preflight.lisp')
    run=read(out/'runs.json');assert len(run['runs'])==119
    assert all(r['exitCode']==r['expectedExitCode'] and r['network']==r['repositoryWrites']==r['hyperdocWrites']=='denied'
      and sha(out/(r['label']+'.log'))==r['logSHA256'] for r in run['runs'])
    assert run['executionSourcesSHA256']=={p:sha(ROOT/p) for p in run['executionSourcesSHA256']}
    assert run['rawReportSHA256']=={p:sha(out/p) for p in run['rawReportSHA256']}
    old,new=read(PRIOR/'xtm.json'),read(out/'xtm.json')
    retargets=compare_existing(old,new,'normal')
    assert new['cases']==old['cases']
    labels=re.findall(r'^XTM-CHECK-PASS (.+)$',(out/'xtm.log').read_text(),re.M)
    assert labels==new['checks'] and len(labels)==len(set(labels))
    added=[c for c in labels if c not in set(old['checks'])]
    assert added and all(c.startswith(('anytype:','anytype-error:','anytype-replay:')) for c in added)
    x=new['anyTypeReader'];assert x['executed'] and x['XTMReaderAnyTypeIntegration'] and x['originalRegistrationsAdded']==0
    assert len(x['retargetings'])==len(x['formerSourceReplays']) and all(r['condition'] is None for r in x['formerSourceReplays'])
    for row in x['positiveProbes']:
        assert sorted(row['expectedValues'])==sorted(row['actualValues']),row['id']
        assert bytes.fromhex(row['actualCXTMHex'])==row['actualCXTM'].encode('utf-8')
        assert row['canonicalReferencesEQ'] and row['repeatedCXTMPure'] and row['inputHex']
    assert all(row['condition'] for row in x['negativeProbes'])
    assert new['resourceDataC14N']==old['resourceDataC14N'] and new['c14nPreflight']==old['c14nPreflight']
    assert len(new['resourceDataC14N']['probes'])==44 and len(new['resourceDataC14N']['nativeValues'])==41
    before,after=read(PRIOR/'after-diagnostics.json'),read(out/'after-diagnostics.json')
    assert before==after and len(after)==124
    fault=[]
    for r in run['runs']:
        if '-control-' not in r['label']:continue
        name=r['label']+'.json';a,b=read(PRIOR/name),read(out/name)
        changes=compare_existing(a,b,r['label'])
        assert a['checks']==b['checks'] and a['statuses']==b['statuses']
        assert r['exitCode']==1 and not b['anyTypeReader']['executed'] and not b['anyTypeReader']['positiveProbes']
        fault.append({'label':r['label'],'expectedExitCode':1,'caseStatusesAndOutcomesUnchanged':True,
          'previousCheckLabelsUnchanged':True,'faultCountedAsOriginalPASS':False,'newReaderProbesNotClaimedExecuted':True,
          'retargetedDiagnostics':changes})
    assert len(fault)==113
    retained=[];retained_deltas=[]
    for p in sorted((out/'retained').rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(out);prior=PRIOR/rel
        if p.read_bytes()==prior.read_bytes():retained.append({'report':str(rel),'SHA256':sha(p)})
        else:
            assert str(rel)=='retained/xtm-mergemap.integration.json',str(rel)
            ds=differences(read(prior),read(p))
            assert ds==[{'path':'/rejections/13/code','before':'RESOURCE-DATA-DATATYPE','after':'RESOURCE-RESOLVER-REQUIRED'},
                        {'path':'/rejections/14/code','before':'RESOURCE-DATA-DATATYPE','after':'RESOURCE-RESOLVER-REQUIRED'}],ds
            retained_deltas.append({'report':str(rel),'differences':ds,
                'purpose':'two CTM/XTM child-resource Unsupported controls now require explicit XTM resolver; CTM production unchanged'})
    for rel in ['ctm.validation.json','ctm.cxtm.json','ctm.encoding.json']:
        assert (out/rel).read_bytes()==(PRIOR/rel).read_bytes(),rel
    prev=read(PRIOR/'execution.json');reg=(out/'regression.log').read_text()
    core=read(ROOT/'reports/slice-22d/baseline/execution.json')['retainedChecks']
    assert sum(core.values())==prev['retainedLispChecks']
    for marker,count in dict(core,**prev['stageChecks']).items():
        assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',reg).group(1))==count,marker
    assert 'CTM-XTM-EQUIVALENCE-PASS: 529 checks; 30 actual reader pairs; 3 contrasts; 0 capability gaps.' in reg
    assert 'Ran 2 tests' in reg and 'NFC-ORACLE-PASS: 16294' in reg
    assert 'CXML-SUMMARY 146 PASS 0 FAIL' in (out/'xml.log').read_text()
    assert new['statuses']==old['statuses']=={'pass':121,'fail':0,'unsupported':0,'not-run':0}
    assert new['otherCorpusInputs']=={'positiveUnexecuted':3,'negativeUnregisteredUnexecuted':0}
    assert read(out/'ctm.validation.json')['statuses']=={'pass':262,'fail':4,'unsupported':0,'not-run':7}
    assert protected=={p:sha(ROOT/p) for p in protected}
    save(out/'retargetings.json',{'controlRows':retargets,'runtimeSourceRetargetings':x['retargetings'],
      'formerSourceReplays':x['formerSourceReplays'],'retainedReportChanges':retained_deltas,
      'executorSourceBefore':'reports/slice-22d/failure-controls.lisp','executorSourceAfter':'reports/slice-22s/failure-controls.lisp',
      'executorChange':'Unsupported fixture is valid mergeMap with missing explicit resolver; 113 existing target/mode controls retained',
      'legacyLabelsAreHistoricalNotCurrentFeatureClaims':True})
    save(out/'diagnostic-changes.json',{'observations':124,'changed':0,'unchanged':124,'changes':[],'registrationsAdded':0})
    save(out/'failure-controls-audit.json',fault);save(out/'retained-reports.json',retained)
    save(out/'integrity.json',{'protectedBaseFilesSHA256':protected,'protectedBaseFileCount':len(protected),
      'pinnedCorpusFilesVerified':sum(p.startswith('vendor/cxtm/') for p in protected),
      'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
      'allXMLC14NTMDMCTMCXTMSourcesUnchanged':True,'allowedTrackedChanges':sorted(allowed),
      'newProductionFeature':'only XTM Reader anyType integration'})
    save(out/'execution.json',{'kind':'slice-22s-productive-XTM-anyType-integration','baseCommit':BASE,
      'runtime':'SBCL 2.5.4','startedAtUTC':run['startedAtUTC'],'finishedAtUTC':run['finishedAtUTC'],
      'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runs':run['runs'],
      'collector':'scripts/validate-slice-22d.py::collect with explicit 22S fault-driver path',
      'collectorConfigurationSHA256':sha(D/'collect.py'),'auditToolSHA256':sha(Path(__file__)),
      'standaloneXTMChecks':len(labels),'retainedStandaloneXTMChecks':len(old['checks']),'newReaderChecks':len(added),
      'positiveReaderProbes':len(x['positiveProbes']),'negativeReaderProbes':len(x['negativeProbes']),
      'retargetedSourceReplays':len(x['formerSourceReplays']),'retargetedRegularControlRows':len(retargets),
      'retainedC14NByteRows':44,'retainedNativeTMDMValueRows':41,'retainedLispChecks':prev['retainedLispChecks'],
      'stageChecks':prev['stageChecks'],'equivalenceChecks':529,'equivalenceReaderPairs':30,'equivalenceContrasts':3,
      'xmlQualificationChecks':146,'pythonUnitTests':2,'nfcOracleComparisons':16294,'faultControls':113,
      'retainedReportsByteIdentical':len(retained),'retargetedRetainedReports':len(retained_deltas),
      'all124OriginalDiagnosesUnchanged':True,'statusesBefore':prev['statusesAfter'],'statusesAfter':prev['statusesAfter'],
      'originalRegistrationsAdded':0,'XTMReaderAnyTypeIntegration':True,'C14NAlgorithmChanged':False,'newExternalDependencies':0,
      'preImplementationContractPassed':True,'acceptancePassed':True})
    print(json.dumps({'acceptancePassed':True,'XTMChecks':len(labels),'newChecks':len(added),
      'positiveReaderProbes':len(x['positiveProbes']),'negativeReaderProbes':len(x['negativeProbes']),
      'sourceReplays':len(x['formerSourceReplays']),'faultControls':113,'statuses':prev['statusesAfter']}),flush=True)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--audit-only',action='store_true');a=ap.parse_args()
    out=a.output.resolve();assert not out.is_relative_to(ROOT)
    if not a.audit_only:
        spec=importlib.util.spec_from_file_location('slice22s_collector',D/'collect.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.collect(out)
    audit(out)
if __name__=='__main__':main()
