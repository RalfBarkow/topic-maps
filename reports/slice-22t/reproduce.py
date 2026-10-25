#!/usr/bin/env python3
"""Reproduce/audit 22T via the existing offline harness; never downloads.
--audit-only inspects saved evidence and is not a new test execution.
"""
import argparse, datetime, hashlib, importlib.util, json, re, sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
D = ROOT/'reports/slice-22t'
PRIOR = ROOT/'reports/slice-22s/after'
BASE = '513de98e5f9dfb62ba3c6310a150bb43c5a4c151'
ALLOWED = {'tests/ctm-xtm-equivalence.lisp', 'topic-maps.asd'}
NEW_IDS = {'anytype-occurrence', 'anytype-variant', 'anytype-occurrence-normalization',
           'anytype-variant-normalization', 'anytype-namespace-meaning'}

def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v): p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')

def audit(out):
    initial = read(D/'initial-state.json')
    assert initial['baseCommit']==BASE and initial['initialIndexAndWorktreeClean']
    protected = {p:h for p,h in initial['trackedFileSHA256'].items() if p not in ALLOWED}
    assert protected=={p:sha(ROOT/p) for p in protected}
    restoration = read(D/'restoration.json')
    assert restoration['restorationPassed'] and len(restoration['acquisitions'])==2
    assert all(r['exitCode']==0 and r['identityVerified'] and r['verifiedNARHash']==r['expectedNARHash']
               and r['result']['storePath']==r['expectedStorePath'] for r in restoration['acquisitions'])
    prep,priorprep=read(out/'source-preparation.json'),read(PRIOR/'source-preparation.json')
    assert prep['sources']==priorprep['sources'] and prep['patches']==priorprep['patches']
    runs = read(out/'runs.json');assert len(runs['runs'])==119
    for r in runs['runs']:
        assert r['exitCode']==r['expectedExitCode'] and r['freshProcess']
        assert r['network']==r['repositoryWrites']==r['hyperdocWrites']=='denied'
        assert sha(out/(r['label']+'.log'))==r['logSHA256']
    assert runs['executionSourcesSHA256']=={p:sha(ROOT/p) for p in runs['executionSourcesSHA256']}
    assert runs['rawReportSHA256']=={p:sha(out/p) for p in runs['rawReportSHA256']}
    old,new=read(PRIOR/'xtm.json'),read(out/'xtm.json')
    assert new==old
    labels=re.findall(r'^XTM-CHECK-PASS (.+)$',(out/'xtm.log').read_text(),re.M)
    assert labels==new['checks'] and len(labels)==4327 and len(labels)==len(set(labels))
    assert new['statuses']=={'pass':121,'fail':0,'unsupported':0,'not-run':0}
    assert new['otherCorpusInputs']=={'positiveUnexecuted':3,'negativeUnregisteredUnexecuted':0}
    assert read(out/'after-diagnostics.json')==read(PRIOR/'after-diagnostics.json')
    assert len(read(out/'after-diagnostics.json'))==124
    faults=[]
    for r in runs['runs']:
        if '-control-' not in r['label']:continue
        name=r['label']+'.json'
        assert (out/name).read_bytes()==(PRIOR/name).read_bytes(),name
        assert r['exitCode']==1
        faults.append({'label':r['label'],'expectedExitCode':1,'reportByteIdenticalTo22S':True,
                       'faultCountedAsOriginalPASS':False})
    assert len(faults)==113
    rel=Path('retained/xtm-mergemap.equivalence.json')
    before,after=read(PRIOR/rel),read(out/rel)
    assert after['runtime']=='2.5.4' and after['condition'] is None
    assert after['productionModelChanges'] is False and after['originalCorpusRegistrationsAdded']==0
    assert len(before['checks'])==529 and len(after['checks'])==len(set(after['checks']))==728
    assert [c for c in after['checks'] if c in set(before['checks'])]==before['checks']
    added=[c for c in after['checks'] if c not in set(before['checks'])]
    assert len(added)==199 and all(c.startswith(('equivalence:anytype-', 'equivalence:contrast:anytype-')) for c in added)
    oldids={r['id'] for r in before['pairs']}
    assert [r for r in after['pairs'] if r['id'] in oldids]==before['pairs']
    assert len(oldids)==33 and len({r['id'] for r in after['pairs']})==len(after['pairs'])==38
    rows=[r for r in after['pairs'] if r['id'] not in oldids]
    assert {r['id'] for r in rows}==NEW_IDS
    positives=[r for r in rows if r['kind']=='direct-reader-equivalence-pair']
    assert len(positives)==4
    for r in rows:
        assert r['slice']=='22T' and r['expectedDatatype']=='http://www.w3.org/2001/XMLSchema#anyType'
        assert r['ctmModel']['counts']==r['xtmModel']['counts']==r['expectedNativeCounts']
        calls=r['actualReaderEntries'];n=4 if r in positives else 2
        assert len(calls)==len(r['nativeConstructorEvidence'])==n
        assert {c['entryPoint'] for c in calls}=={'topic-maps.ctm:deserialize-string','topic-maps.xtm:deserialize-octets'}
        assert all(c['documentIRI']==r['canonicalBaseIRI'] and c['inputHex'] for c in calls)
        assert bytes.fromhex(calls[0]['inputHex']).decode('utf-8')==r['ctmSource']
        assert bytes.fromhex(calls[1]['inputHex']).decode('utf-8')==r['xtmSource']
        for proof in r['nativeConstructorEvidence']:
            assert proof['allReturnedHandlesCanonicalAndLive']
            assert proof['nativeItemCountsBefore']==([0,1] if r['normalizationRequired'] else [0])
            assert proof['nativeItemCountsAfter']==([1,1] if r['normalizationRequired'] else [1])
        for lang in ['ctm','xtm']:
            assert len(r[lang+'CXTM'].encode('utf-8'))==r[lang+'Bytes']
        if r in positives:
            assert r['ctmCondition'] is None and r['xtmCondition'] is None
            assert r['documentIRI']==r['canonicalBaseIRI']
            assert r['nativePropertiesEqual'] and r['ctmCanonicalEQ'] and r['xtmCanonicalEQ']
            assert r['crossMapEQRequired'] is False
            assert r['byteExact'] and r['firstDifferentByte'] is None and r['ctmCXTM']==r['xtmCXTM']
            assert r['independentExpectedCanonicalValue']==r['expectedXTMCanonicalValue']
        else:
            assert r['id']=='anytype-namespace-meaning' and r['byteExact'] is False
            assert r['nativePropertiesEqual'] is False and r['ctmCXTM']!=r['xtmCXTM']
            assert r['independentExpectedCanonicalValue']!=r['expectedXTMCanonicalValue']
            a,b=r['ctmCXTM'].encode(),r['xtmCXTM'].encode()
            assert next(i for i,(x,y) in enumerate(zip(a,b)) if x!=y)==r['firstDifferentByte']
    retained=[]
    for p in sorted((out/'retained').rglob('*')):
        if not p.is_file() or p.relative_to(out)==rel:continue
        prior=PRIOR/p.relative_to(out)
        assert p.read_bytes()==prior.read_bytes(),str(p.relative_to(out))
        retained.append({'report':str(p.relative_to(out)),'SHA256':sha(p)})
    for name in ['ctm.validation.json','ctm.cxtm.json','ctm.encoding.json']:
        assert (out/name).read_bytes()==(PRIOR/name).read_bytes(),name
    assert read(out/'ctm.validation.json')['statuses']=={'pass':262,'fail':4,'unsupported':0,'not-run':7}
    previous=read(PRIOR/'execution.json');reg=(out/'regression.log').read_text()
    core=read(ROOT/'reports/slice-22d/baseline/execution.json')['retainedChecks']
    assert sum(core.values())==12100==previous['retainedLispChecks']
    for marker,count in dict(core,**previous['stageChecks']).items():
        assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',reg).group(1))==count,marker
    assert 'CTM-XTM-EQUIVALENCE-PASS: 728 checks; 34 actual reader pairs; 4 contrasts; 0 capability gaps.' in reg
    assert 'Ran 2 tests' in reg and 'NFC-ORACLE-PASS: 16294' in reg
    assert 'CXML-SUMMARY 146 PASS 0 FAIL' in (out/'xml.log').read_text()
    assert protected=={p:sha(ROOT/p) for p in protected}
    save(out/'failure-controls-audit.json',faults)
    save(out/'diagnostic-changes.json',{'observations':124,'changed':0,'unchanged':124,'changes':[],
                                      'registrationsAdded':0,'retargetings':[]})
    save(out/'retained-reports.json',retained)
    save(out/'equivalence-audit.json',{'retainedRowsByteIdentical':33,'retainedPositivePairs':30,
        'retainedContrasts':3,'retainedChecksUnchanged':529,'newChecks':len(added),'checks':728,
        'positiveReaderPairs':34,'contrasts':4,'newProductiveReaderCalls':18,
        'newSourceItemConstructorCalls':26,'newRows':rows})
    save(out/'integrity.json',{'protectedBaseFilesSHA256':protected,'protectedBaseFileCount':len(protected),
        'pinnedCorpusFilesVerified':sum(p.startswith('vendor/cxtm/') for p in protected),
        'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
        'allProductionSourcesUnchanged':True,'originalsBaselinesAndCaseRecordsUnchanged':True,
        'allowedTrackedChanges':sorted(ALLOWED),'newProductionFeatures':0})
    save(out/'execution.json',{'kind':'slice-22t-productive-CTM-XTM-anyType-equivalence',
        'baseCommit':BASE,'runtime':'SBCL 2.5.4','startedAtUTC':runs['startedAtUTC'],
        'finishedAtUTC':runs['finishedAtUTC'],'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'collector':'scripts/validate-slice-22d.py::collect with unchanged 22S failure driver',
        'collectorConfigurationSHA256':sha(D/'collect.py'),'auditToolSHA256':sha(Path(__file__)),
        'runCount':119,'runs':runs['runs'],'standaloneXTMChecks':4327,'faultControls':113,
        'retainedLispChecks':12100,'stageChecks':previous['stageChecks'],'equivalenceChecks':728,
        'equivalenceReaderPairs':34,'equivalenceContrasts':4,'newReaderPairs':4,'newNamespaceContrasts':1,
        'newProductiveReaderCalls':18,'newNativeConstructorCalls':26,
        'xmlQualificationChecks':146,'pythonUnitTests':2,'nfcOracleComparisons':16294,
        'all124OriginalDiagnosesUnchanged':True,'retargetings':0,'originalRegistrationsAdded':0,
        'statusesBefore':previous['statusesAfter'],'statusesAfter':previous['statusesAfter'],
        'productionSourceChanges':0,'newExternalDependencies':0,
        'pinnedSourceAndPatchIdentityRestored':True,'retainedReportsByteIdentical':len(retained),
        'acceptancePassed':True})
    print(json.dumps({'acceptancePassed':True,'equivalencePairs':34,'contrasts':4,
        'equivalenceChecks':728,'XTMChecks':4327,'faultControls':113,'statuses':previous['statusesAfter']}),flush=True)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--audit-only',action='store_true')
    args=ap.parse_args();out=args.output.resolve();assert not out.is_relative_to(ROOT)
    if not args.audit_only:
        spec=importlib.util.spec_from_file_location('slice22t_collector',D/'collect.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.collect(out)
    audit(out)
if __name__=='__main__': main()
