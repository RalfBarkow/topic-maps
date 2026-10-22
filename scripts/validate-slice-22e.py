#!/usr/bin/env python3
"""Run/audit Slice 22E through the unchanged 22D offline executor and ASDF tests.
--output must be outside the repository. --audit-only verifies saved executions,
without pretending they are fresh runs. Local pinned dependencies only.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/'reports/slice-22e'
BASE='791969ca59922d61e967198eaee4c1fe172b5a0d'
PRIOR=ROOT/'reports/slice-22d/after'
ALLOWED={'src/xtm/package.lisp','src/xtm/reader.lisp','tests/xtm-identity.lisp','tests/xtm-map-reification.lisp','tests/ctm-xtm-mergemap.lisp','topic-maps.asd'}
NEW={'tests/xtm-mergemap.lisp','scripts/validate-slice-22e.py'}
TARGET='xtm2/in/mergemap-itemid.xtm'

def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a,cwd=ROOT):return subprocess.check_output(['git',*a],cwd=cwd,text=True).strip()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def previous_validator():
    spec=importlib.util.spec_from_file_location('slice22d',ROOT/'scripts/validate-slice-22d.py')
    v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    return v

def audit(out,baseline,initial):
    v=previous_validator();start=read(initial)
    assert start['baseCommit']==BASE and start['indexClean'] and start['worktreeClean']
    assert set(git('diff','--name-only',BASE).splitlines())&set(start['trackedFileSHA256'])<=ALLOWED
    protected={p:h for p,h in start['trackedFileSHA256'].items() if p not in ALLOWED}
    assert protected=={p:sha(ROOT/p) for p in protected}
    runs=read(out/'runs.json');assert len(runs['runs'])==119
    assert all(r['exitCode']==r['expectedExitCode'] and sha(out/(r['label']+'.log'))==r['logSHA256'] for r in runs['runs'])
    assert runs['executionSourcesSHA256']=={p:sha(ROOT/p) for p in runs['executionSourcesSHA256']}
    assert runs['rawReportSHA256']=={p:sha(out/p) for p in runs['rawReportSHA256']}
    before=read(baseline/'xtm.json');xtm=read(out/'xtm.json')
    assert before==read(PRIOR/'xtm.json') and len(before['checks'])==2522
    assert read(baseline/'diagnostics.json')==read(PRIOR/'after-diagnostics.json')
    assert xtm['cases']==before['cases'] and len(xtm['cases'])==72
    assert xtm['statuses']==before['statuses']=={'pass':72,'fail':0,'unsupported':0,'not-run':0}
    assert xtm['otherCorpusInputs']==before['otherCorpusInputs']
    labels=re.findall(r'^XTM-CHECK-PASS (.+)$',(out/'xtm.log').read_text(),re.M)
    assert labels==xtm['checks'] and len(labels)==len(set(labels))
    assert [x for x in labels if x in set(before['checks'])]==before['checks']
    assert all(x.startswith(('mm:','mm-error:','mm-original:')) for x in set(labels)-set(before['checks']))
    retargets=[]
    for k,value in before.items():
        if k=='checks':continue
        if k=='mapReifierControls':
            assert len(value)==len(xtm[k])
            for i,(a,b) in enumerate(zip(value,xtm[k])):
                if a!=b:
                    assert a['label']==b['label']=='mergeMap'
                    assert a['condition']['class']==b['condition']['class']=='XTM-UNSUPPORTED'
                    assert a['condition']['code']=='unsupported-construct' and b['condition']['code']=='resource-resolver-required'
                    assert all(d['path'] in {'/condition/code','/condition/detail','/condition/message','/expectedCode'} for d in v.changes(a,b))
                    retargets.append({'field':k,'index':i,'before':a,'after':b})
        else:assert xtm[k]==value,k
    save(out/'retargeted-observations.json',retargets)
    olddiag=read(baseline/'diagnostics.json');newdiag=read(out/'after-diagnostics.json')
    assert len(olddiag)==len(newdiag)==124
    changes=[{'id':a['id'],'before':a,'after':b} for a,b in zip(olddiag,newdiag) if a!=b]
    merge_ids={x['id'] for x in olddiag if x.get('condition') and x['condition'].get('detail')=='XTM mergeMap is not implemented in this subset.'}
    assert len(merge_ids)==7 and {x['id'] for x in changes}==merge_ids
    assert all(b'<mergeMap ' in (ROOT/'vendor/cxtm'/id).read_bytes() for id in merge_ids)
    for x in changes:
        assert x['before']['condition']['code']=='unsupported-construct'
        assert x['after']['condition']['class']=='XTM-UNSUPPORTED' and x['after']['condition']['code']=='resource-resolver-required'
        assert not x['after']['byteExact']
    save(out/'diagnostic-changes.json',{'kind':'all-124-originals-without-resolver','changed':7,'unchanged':117,'changes':changes,
      'separateExplicitResolverObservations':'original-observations.json','registeredStatusesChanged':False})
    faults=[]
    for r in runs['runs']:
        label=r['label']
        if '-control-' not in label:continue
        a=read(PRIOR/(label+'.json'));b=read(out/(label+'.json'))
        assert a['cases']==b['cases'] and a['statuses']==b['statuses'],label
        ca=dict(v.condition_nodes(a));cb=dict(v.condition_nodes(b));assert ca.keys()==cb.keys(),label
        ds=[]
        for path,c in ca.items():
            d=cb[path];assert c['class']==d['class'],(label,path,c,d)
            if c.get('code')!=d.get('code'):
                assert path.startswith('/mapReifierControls/') and path.endswith('/condition')
                assert c.get('code')=='unsupported-construct' and d.get('code')=='resource-resolver-required'
            if c!=d:ds.append({'path':path,'before':c,'after':d})
        assert all(x['status']!='pass' for x in b['cases'] if x['status'] in ('fail','unsupported'))
        faults.append({'label':label,'expectedASDFFailureObserved':True,'caseRecordsAndOutcomesIdentical':True,
          'previousCorrectPASSRetained':sum(x['status']=='pass' for x in b['cases']),
          'conditionClassesUnchanged':True,'conditionChanges':ds,'faultCountedAsPass':False})
    assert len(faults)==113
    save(out/'failure-controls.json',{'retained':113,'new':0,'controls':faults,'allExpectedFailureExitsObserved':True})
    unchanged=[];adapter=[]
    for p in [*sorted((PRIOR/'retained').glob('*.json')),*[PRIOR/f'ctm.{s}.json' for s in ['validation','cxtm','encoding']]]:
        rel=p.relative_to(PRIOR);q=out/rel
        if p.read_bytes()!=q.read_bytes():
            assert str(rel)=='retained/xtm-mergemap.integration.json'
            adapter=v.changes(read(p),read(q));assert len(adapter)==1,adapter
            assert adapter[0]['before']=='UNSUPPORTED-CONSTRUCT' and adapter[0]['after']=='RESOURCE-RESOLVER-REQUIRED',adapter
        else:unchanged.append({'report':str(rel),'sha256':sha(p),'byteIdentical':True})
    assert len(unchanged)==47
    save(out/'retained-reports.json',unchanged);save(out/'adapter-retargeting.json',{'differences':adapter,'adapterProductionCodeChanged':False})
    regression=(out/'regression.log').read_text();prior=read(PRIOR/'execution.json')
    for marker,count in dict(prior['retainedChecks'],**prior['stageChecks']).items():
        assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',regression).group(1))==count
    assert 'Ran 2 tests' in regression and 'NFC-ORACLE-PASS: 16294' in regression
    xml=(out/'xml.log').read_text();assert 'CXML-SUMMARY 146 PASS 0 FAIL' in xml
    assert len(set(re.findall(r'^CXML-CHECK-PASS (.+)$',xml,re.M)))==146
    assert read(out/'ctm.validation.json')['statuses']==read(PRIOR/'ctm.validation.json')['statuses']
    originals=xtm['mergemapOriginalObservations'];assert len(originals)==2
    item=originals[0];assert item['id']==TARGET and item['condition'] is None and item['registeredStatus']=='not-run' and not item['registeredAsPASS']
    raw=ROOT/'vendor/cxtm'/TARGET;child=ROOT/'vendor/cxtm/xtm2/in/mergemap-itemid.sub';expected=ROOT/'vendor/cxtm/xtm2/baseline/mergemap-itemid.xtm.cxtm'
    assert raw.read_bytes()==bytes.fromhex(item['sourceHex']) and child.read_bytes()==bytes.fromhex(item['childHex'])
    actual=item['actualCXTM'].encode();assert expected.read_bytes()==item['expectedCXTM'].encode() and actual!=expected.read_bytes()
    mismatch=next(i for i,(a,b) in enumerate(zip(actual,expected.read_bytes())) if a!=b)
    assert mismatch==item['firstDifferentByte'] and item['onlyBaselineRootMapItemIdentifiersDiffer']
    assert item['targetMapItemIdentifiers']==[] and item['sourceMapItemIdentifiers']==[item['childIRI']+'#the-topic-map']
    item=dict(item,sourceSHA256=sha(raw),childSHA256=sha(child),baselineSHA256=sha(expected),actualSHA256=hashlib.sha256(actual).hexdigest())
    save(out/'original-observations.json',[item,originals[1]])
    (out/'actual').mkdir(exist_ok=True);(out/'actual/mergemap-itemid.xtm.cxtm').write_bytes(actual)
    assert originals[1]['condition']['code']=='cyclic-mergemap' and originals[1]['registeredStatus']=='not-run'
    lock=read(ROOT/'references/corpus-lock.json')
    for e in lock['files']:
        p=ROOT/'vendor/cxtm'/e['path'];assert p.stat().st_size==e['size'] and sha(p)==e['sha256']
    assert protected=={p:sha(ROOT/p) for p in protected}
    hd=Path('/Users/rgb/workspace/hyperdoc-dreyeck-ch');assert git('rev-parse','HEAD',cwd=hd)==start['hyperdocHEAD'] and git('status','--porcelain=v1',cwd=hd)==start['hyperdocStatus']
    save(out/'integrity.json',{'baseCommit':BASE,'protectedBaseFilesSHA256':protected,'executionSourcesSHA256':runs['executionSourcesSHA256'],
      'pinnedCorpusFilesVerified':len(lock['files']),'historicalReportFilesVerified':sum(x.startswith('reports/') for x in protected),
      'historicalReportsOriginalsBaselinesCorpusLockUnchanged':True,'hyperdocUnchanged':True,'productionChanges':['src/xtm/package.lisp','src/xtm/reader.lisp']})
    save(out/'execution.json',{'kind':'slice-22e-noncyclic-xtm-mergemap','baseCommit':BASE,'branch':git('branch','--show-current'),
      'runtime':'SBCL 2.5.4','startedAtUTC':runs['startedAtUTC'],'finishedAtUTC':runs['finishedAtUTC'],'auditedAtUTC':now(),
      'runs':runs['runs'],'collector':'scripts/validate-slice-22d.py::collect (unchanged)','collectorSHA256':sha(ROOT/'scripts/validate-slice-22d.py'),
      'auditToolSHA256':sha(Path(__file__)),'standaloneXTMChecks':len(labels),'retainedXTMChecks':2522,'newXTMChecks':len(labels)-2522,
      'registeredXTMOriginals':72,'newPositiveOriginals':0,'originalObservationsNotRegistrations':2,
      'retainedLispChecks':12100,'retainedChecks':prior['retainedChecks'],'stageChecks':prior['stageChecks'],'xmlQualificationChecks':146,
      'faultControls':113,'newFaultControls':0,'originalDiagnoses':124,'diagnosticChangesWithinSlice':7,'diagnosesOutsideScopeUnchanged':117,
      'statusesBefore':prior['statusesAfter'],'statusesAfter':prior['statusesAfter'],'pythonUnitTests':2,'nfcOracleComparisons':16294,
      'nonXTMReportsByteIdentical':47,'adapterControlCodeRetargetings':1,'pinnedCorpusFilesVerified':len(lock['files']),
      'historicalReportFilesVerified':sum(x.startswith('reports/') for x in protected),'knownCTMFailuresUnchanged':prior['knownCTMFailuresUnchanged'],
      'mapItemMetadataImported':False,'normativeCycleSemanticsImplemented':False,'anyTypeImplemented':False,'anyTypePlannedSlice':'22I',
      'newDependencyDownloads':0,'persistentImagesTouched':False,'acceptancePassed':True})
    print(json.dumps({'acceptancePassed':True,'xtmChecks':len(labels),'statuses':prior['statusesAfter'],'faultControls':113,'actualBytes':len(actual),'baselineBytes':len(expected.read_bytes()),'firstDifferentByte':mismatch}))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--baseline',type=Path,default=TOOLS/'baseline');ap.add_argument('--initial',type=Path,default=TOOLS/'initial-state.json');ap.add_argument('--audit-only',action='store_true');a=ap.parse_args()
    out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=True)
    if not a.audit_only:
        v=previous_validator();v.EXECUTION_FILES=ALLOWED|{'tests/xtm-mergemap.lisp','scripts/validate-slice-22d.py','reports/slice-22d/failure-controls.lisp'}
        # Its historical 108 labels plus the five datatype controls are exactly
        # the 113 accepted controls, using the unchanged 22D executor driver.
        v.collect(out,ROOT/'reports/slice-22d/baseline')
    audit(out,a.baseline,a.initial)
if __name__=='__main__':main()
