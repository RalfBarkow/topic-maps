#!/usr/bin/env python3
"""Validate one XTM original registration through the existing offline harness.
Outputs are outside the repository. No production edits or new test architecture.
The pre-change execution is retained in reports/slice-22b/baseline; --baseline may
select another verified fresh baseline. The default reruns the complete current
regression and all 108 executor controls against the immutable Slice-22A evidence.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = 'b12ece02faa039e816fca3750acd9eceb6be1513'
PRIOR = ROOT / 'reports/slice-22a/baseline'
TOOLS = ROOT / 'reports/slice-22b'
TARGET = 'xtm2/in/variant-duplicate-reifier2.xtm'
RUNTIME = '/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl'
ALLOWED = {'tests/xtm-identity.lisp', 'tests/xtm-variant-reification.lisp', 'topic-maps.asd'}
POLICY = '(version 1)(allow default)(deny network*)(deny file-write* (subpath "'+str(ROOT)+'"))(deny file-write* (subpath "/Users/rgb/workspace/hyperdoc-dreyeck-ch"))'
CTM = {'pass':262,'fail':4,'unsupported':0,'not-run':7}


def read(p): return json.loads(p.read_text())
def save(p,v): p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def prepare_pinned(target):
    spec=importlib.util.spec_from_file_location('slice21o',ROOT/'scripts/validate-slice-21o.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.prepare_pinned(target)


def verify_before(path):
    ex=read(path/'execution.json')
    assert ex['acceptancePassed'] and ex['xtmStatusesAfter']=={'pass':70,'fail':0,'unsupported':0,'not-run':54}
    assert ex['ctmStatusesAfter']==CTM and len(ex['runs'])==109
    assert all(r['exitCode']==r['expectedExitCode'] for r in ex['runs'])
    rows=[]
    for item in read(ROOT/'reports/slice-22a/baseline-comparison.json'):
        name=item['freshReport'].removeprefix('baseline/')
        a,b=PRIOR/name,path/name
        assert a.read_bytes()==b.read_bytes(),name
        rows.append({'slice22AReport':str(a.relative_to(ROOT)),'freshBeforeReport':'baseline/'+name,
                     'sha256':sha(b),'byteIdentical':True})
    assert len(rows)==154
    return rows


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sbcl',default=RUNTIME);ap.add_argument('--output',type=Path)
    ap.add_argument('--baseline',type=Path,default=TOOLS/'baseline');ap.add_argument('--prepare',type=Path)
    args=ap.parse_args()
    if args.prepare: print(json.dumps(prepare_pinned(args.prepare)));return
    assert args.output,'--output outside the repository is required'
    output=args.output.resolve();assert not output.is_relative_to(ROOT)
    output.mkdir(parents=True,exist_ok=True);assert not (output/'execution.json').exists(),'Choose an unused output directory.'
    runtime=shutil.which(args.sbcl);assert runtime and subprocess.check_output([runtime,'--version'],text=True).strip()=='SBCL 2.5.4'
    subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT,check=True)
    tracked=git('ls-tree','-r','--name-only',BASE).splitlines()
    changed=set(git('diff','--name-only',BASE).splitlines()) & set(tracked);assert changed<=ALLOWED,changed
    before_hashes={p:sha(ROOT/p) for p in tracked};protected={p:v for p,v in before_hashes.items() if p not in ALLOWED}
    sources={p:sha(ROOT/p) for p in [*sorted(ALLOWED),'scripts/validate-slice-22b.py','reports/slice-22b/failure-controls.lisp']}
    save(output/'baseline-comparison.json',verify_before(args.baseline.resolve()))
    previous=read(PRIOR/'xtm.json');assert len(previous['cases'])==70 and TARGET not in {c['id'] for c in previous['cases']}
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();runs=[]
    env={k:v for k,v in os.environ.items() if not k.startswith('TOPIC_MAPS_')}
    env.update(PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0',SBCL=runtime)
    def run(label,command,env,exit_code=0):
        command=['/usr/bin/sandbox-exec','-p',POLICY]+command
        t=datetime.datetime.now(datetime.timezone.utc).isoformat()
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
        (output/(label+'.log')).write_bytes(result.stdout)
        runs.append({'label':label,'command':command,'startedAtUTC':t,'finishedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'exitCode':result.returncode,'expectedExitCode':exit_code,'network':'denied','repositoryWrites':'denied','hyperdocWrites':'denied','freshProcess':True})
        assert result.returncode==exit_code,(label,result.stdout.decode()[-3500:])
        return result.stdout.decode()
    retained=output/'retained';retained.mkdir()
    with tempfile.TemporaryDirectory(prefix='topic-maps-22b-sources-') as tmp:
        provenance=json.loads(run('source-preparation',['python3',str(Path(__file__)), '--prepare',tmp+'/sources'],env));save(output/'source-preparation.json',provenance)
        env.update(CL_SOURCE_REGISTRY=provenance['sourceRegistry'],TOPIC_MAPS_REPORT=str(retained/'core.json'),
          TOPIC_MAPS_XTM_REPORT=str(output/'xtm.json'),TOPIC_MAPS_XTM_MERGEMAP_REPORT=str(retained/'xtm-mergemap'),
          TOPIC_MAPS_REGISTERED_ORIGINALS_REPORT=str(retained/'slice20a'),TOPIC_MAPS_REGISTERED_NEGATIVES_REPORT=str(retained/'slice20b'),
          TOPIC_MAPS_PROLOG_REPORT=str(retained/'slice20c'),TOPIC_MAPS_EMPTY2_REPORT=str(retained/'slice20e'),
          TOPIC_MAPS_CTM_INTEGER_REPORT=str(retained/'slice20f'),TOPIC_MAPS_TRIPLE_REPORT=str(retained/'slice20g'),TOPIC_MAPS_ENCODING_REPORT=str(output/'ctm'))
        prefix=[runtime,'--noinform','--no-sysinit','--no-userinit','--script']
        xml=run('xml',prefix+['tests/cxml-probe.lisp'],env)
        assert 'CXML-SUMMARY 146 PASS 0 FAIL' in xml
        assert len(set(re.findall(r'^CXML-CHECK-PASS (.+)$',xml,re.M)))==146
        preflight=run('variant-reifier-api-preflight',prefix+['reports/slice-21o/api-preflight.lisp'],env)
        assert 'VARIANT-REIFIER-API-PREFLIGHT-PASS:' in preflight
        xtm_log=run('xtm',prefix+['scripts/fresh-xtm.lisp'],env);xtm=read(output/'xtm.json')
        labels=re.findall(r'^XTM-CHECK-PASS (.+)$',xtm_log,re.M);assert labels==xtm['checks'] and len(labels)==len(set(labels))
        assert [l for l in labels if l in set(previous['checks'])]==previous['checks']
        assert len(set(labels)-set(previous['checks']))==12
        assert f'XTM-SUMMARY {len(labels)} PASS 0 FAIL; 63 original CXTM PASS; 8 negative originals PASS' in xtm_log
        assert xtm['statuses']=={'pass':71,'fail':0,'unsupported':0,'not-run':0}
        assert xtm['otherCorpusInputs']=={'positiveUnexecuted':50,'negativeUnregisteredUnexecuted':3}
        assert xtm['cases'][:70]==previous['cases'] and len(xtm['cases'])==len({c['id'] for c in xtm['cases']})==71
        assert xtm['cases'][-1]['id']==TARGET and xtm['cases'][-1]['status']=='pass' and xtm['cases'][-1]['actualOutcome']=='cxtm-match'
        allowed_fields={'scope','statuses','otherCorpusInputs','checks','cases','variantReifierOriginals'}
        for k,v in previous.items():
            if k not in allowed_fields:assert xtm[k]==v,k
        assert xtm['scope']==previous['scope'].replace('62 positive','63 positive')
        assert len(xtm['variantReifierOriginals'])==3 and xtm['variantReifierOriginals'][:2]==previous['variantReifierOriginals']
        regression=run('regression',[str(ROOT/'scripts/test.sh')],env)
        # This unchanged reader-only diagnostic driver performs no registration.
        # Its historical extra flag is process-local and is not a registry report.
        run('diagnostics',prefix+['reports/slice-21o/diagnostics.lisp'],dict(env,TOPIC_MAPS_21O_ROOT=str(ROOT),
          TOPIC_MAPS_21O_DIAGNOSTICS=str(output/'after-diagnostics.json'),TOPIC_MAPS_21O_EXTRA=tmp+'/reader-only-extra.json'))
        assert read(output/'after-diagnostics.json')==read(PRIOR/'after-diagnostics.json')
        assert len(read(output/'after-diagnostics.json'))==124
        fault_controls=[];retained_faults=[]
        old_fault_runs=[r for r in read(args.baseline/'execution.json')['runs'] if '-control-' in r['label']]
        assert len(old_fault_runs)==103
        for entry in old_fault_runs:
            label=entry['label'];family,mode=label.split('-control-')
            run(label,prefix+['reports/slice-21o/failure-controls.lisp'],dict(env,TOPIC_MAPS_XTM_REPORT=str(output/(label+'.json')),
              TOPIC_MAPS_21O_FAMILY=family,TOPIC_MAPS_21O_FAULT=mode),1)
            old,new=read(args.baseline/(label+'.json')),read(output/(label+'.json'))
            assert new['scope']==old['scope'].replace('62 positive','63 positive')
            assert {k:v for k,v in old.items() if k!='scope'}=={k:v for k,v in new.items() if k!='scope'},label
            retained_faults.append({'label':label,'allBehavioralFieldsUnchanged':True,'onlyMetadataChange':'/scope: 62 -> 63 positive capacity',
              'beforeSHA256':sha(args.baseline/(label+'.json')),'afterSHA256':sha(output/(label+'.json'))})
            fault_controls.append({'label':label,'retained':True,'expectedASDFFailureObserved':True,'faultCountedAsPass':False})
        modes={'mismatch':('cxtm-mismatch',None,None),'xml':('execution-error','XTM-XML-ERROR','xml-not-well-formed'),
          'xtm':('execution-error','XTM-REJECTION','invalid-id'),'unsupported':('unsupported','XTM-UNSUPPORTED','resource-data-datatype'),
          'tmdm':('execution-error','REIFICATION-ERROR','reifier-conflict')}
        for mode,(outcome,cls,code) in modes.items():
            label='variant-reifier-followup-control-'+mode
            run(label,prefix+[str(TOOLS/'failure-controls.lisp')],dict(env,TOPIC_MAPS_XTM_REPORT=str(output/(label+'.json')),TOPIC_MAPS_22B_FAULT=mode),1)
            result=read(output/(label+'.json'));assert result['cases'][:70]==xtm['cases'][:70] and len(result['cases'])==71
            failed=result['cases'][-1];assert failed['id']==TARGET and failed['actualOutcome']==outcome and failed['status']!='pass'
            assert result['statuses']['pass']==70
            actual=next(c for c in result['variantReifierOriginals'] if c['id']==TARGET);c=actual['condition']
            if cls:assert c['class']==cls and c['code']==code,(mode,c)
            else:assert c is None and actual['firstDifferentByte']==0
            fault_controls.append({'label':label,'retained':False,'target':TARGET,'mode':mode,'actualOutcome':outcome,'condition':c,
              'caseStatus':failed['status'],'retainedOriginalPASS':70,'expectedASDFFailureObserved':True,'faultCountedAsPass':False})
    unchanged=[]
    for old in sorted((PRIOR/'retained').glob('*.json')):
        assert old.read_bytes()==(retained/old.name).read_bytes(),old.name
        unchanged.append({'previousReport':str(old.relative_to(ROOT)),'freshReport':'retained/'+old.name,'sha256':sha(old),'byteIdentical':True})
    for suffix in ['validation','cxtm','encoding']:
        name=f'ctm.{suffix}.json';assert (PRIOR/name).read_bytes()==(output/name).read_bytes()
        unchanged.append({'previousReport':str((PRIOR/name).relative_to(ROOT)),'freshReport':name,'sha256':sha(output/name),'byteIdentical':True})
    totals=read(PRIOR/'execution.json')['retainedChecks'];stages=read(PRIOR/'execution.json')['stageChecks']
    for marker,count in dict(totals,**stages).items():assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',regression).group(1))==count
    assert sum(totals.values())==12100 and 'Ran 2 tests' in regression and 'NFC-ORACLE-PASS: 16294' in regression
    assert read(output/'ctm.validation.json')['statuses']==CTM
    new=xtm['variantReifierOriginals'][-1];source=ROOT/'vendor/cxtm'/TARGET;baseline=ROOT/'vendor/cxtm/xtm2/baseline/variant-duplicate-reifier2.xtm.cxtm'
    actual=new['actualCXTM'].encode('utf-8');raw=source.read_bytes();expected=baseline.read_bytes()
    assert raw==bytes.fromhex(new['sourceHex'])==new['sourceText'].encode('utf-8') and len(raw)==new['sourceBytes']==543
    assert sha(source)=='87b740c6ec7d11b485b223cb5c28807bce9259d04c2d586ea557e6cd10c3faf4'
    assert actual==expected==new['expectedCXTM'].encode('utf-8') and len(actual)==new['actualBytes']==new['expectedBytes']==702
    assert sha(baseline)==hashlib.sha256(actual).hexdigest()=='014773fca95a2b7bb70038f8e118d402d311a2804f54f105ff05ee53c7eb0a60'
    assert new['firstDifferentByte'] is None and new['condition'] is None and new['status']=='pass'
    assert new['documentIRI']==new['model']['identity']['identity']['nameModel']['identity']['topics'][0]['itemIdentifiers'][0].removesuffix('#topic')
    assert new['sourceKey']==TARGET and new['primaryQualifiedParserCalls']==1
    assert new['model']==read(PRIOR/'further-variant-reification.json')['model']
    assert new['nativeHandleObservation']=={'sourceNameCalls':2,'sameRawNameHandleEQ':True,'preNormalizationPairs':1,'distinctRetainedVariantHandles':2,
      'retainedNameCanonicalEQ':True,'retainedVariantCanonicalEQ':True,'variantReplacementObserved':True,'canonicalParentScopeReifierInverseEQ':True}
    new=dict(new,sourceSHA256=sha(source),baselineSHA256=sha(baseline),actualSHA256=hashlib.sha256(actual).hexdigest(),byteExact=True,executedInASDFTestOp=True)
    (output/'actual').mkdir();(output/'actual/variant-duplicate-reifier2.xtm.cxtm').write_bytes(actual)
    save(output/'original-contract.json',new)
    save(output/'diagnostic-changes.json',{'readerObservations':124,'changed':0,'byteIdenticalToSlice22A':(output/'after-diagnostics.json').read_bytes()==(PRIOR/'after-diagnostics.json').read_bytes(),
      'beforeSHA256':sha(PRIOR/'after-diagnostics.json'),'afterSHA256':sha(output/'after-diagnostics.json'),'changes':[]})
    save(output/'retained-reports.json',unchanged);save(output/'retained-fault-reports.json',retained_faults)
    save(output/'failure-controls.json',{'kind':'executor-fault-controls-not-corpus-results','controls':fault_controls,'retained':103,'new':5,'allExpectedFailureExitsObserved':True})
    matrix=read(ROOT/'reports/slice-22a/matrix.json');rows=[]
    for c in matrix['cases']:
        after='pass' if c['id']==TARGET else c['registeredStatus']
        rows.append({'id':c['id'],'before':c['registeredStatus'],'after':after,'changed':after!=c['registeredStatus'],
          'readerConditionUnchanged':True,'newCapability':False,'newNormativeDecision':False})
    assert sum(c['changed'] for c in rows)==1
    save(output/'closure-delta.json',{'kind':'slice-22b-delta-to-immutable-slice-22a-matrix','sourceMatrix':'reports/slice-22a/matrix.json',
      'sourceMatrixSHA256':sha(ROOT/'reports/slice-22a/matrix.json'),'changedCase':TARGET,'newPASS':1,'otherOpenCasesUnchanged':64,'remainingOpenCases':64,
      'newCapability':False,'newNormativeDecision':False,'cases':rows})
    lock=read(ROOT/'references/corpus-lock.json')
    for entry in lock['files']:
        p=ROOT/'vendor/cxtm'/entry['path'];assert p.stat().st_size==entry['size'] and sha(p)==entry['sha256']
    for group in [protected,sources]:assert group=={p:sha(ROOT/p) for p in group}
    assert set(git('diff','--name-only',BASE).splitlines()) & set(tracked)<=ALLOWED
    save(output/'integrity.json',{'baseCommit':BASE,'protectedBaseFilesSHA256':protected,'executionSourcesSHA256':sources,
      'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),'pinnedCorpusFilesVerified':len(lock['files']),
      'productionSourcesTestsExceptThreeRegistrationFilesAndHistoricalEvidenceUnchanged':True})
    before={'XTM':{'pass':70,'fail':0,'not-run':54},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':332,'fail':4,'not-run':61}}
    after={'XTM':{'pass':71,'fail':0,'not-run':53},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':333,'fail':4,'not-run':60}}
    save(output/'execution.json',{'kind':'slice-22b-one-positive-original-registration','baseCommit':BASE,'branch':git('branch','--show-current'),
      'runtime':'SBCL 2.5.4','startedAtUTC':started,'finishedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runs':runs,
      'baselineBehavioralReportsReproduced':154,'retainedLispChecks':12100,'retainedChecks':totals,'stageChecks':stages,'xmlQualificationChecks':146,
      'standaloneXTMChecks':len(labels),'retainedXTMChecks':len(previous['checks']),'newXTMChecks':12,'retainedOriginals':70,'retainedNegativeOriginals':8,
      'newPositiveOriginals':1,'faultControls':108,'newFaultControls':5,'diagnosticOriginalObservations':124,'diagnosticChanges':0,
      'statusesBefore':before,'statusesAfter':after,'pythonUnitTests':2,'nfcOracleComparisons':16294,'retainedNonXTMReportsByteIdentical':len(unchanged),
      'knownCTMFailuresUnchanged':[c['id'] for c in read(output/'ctm.validation.json')['cases'] if c['status']=='fail'],
      'pinnedCorpusFilesVerified':len(lock['files']),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
      'productionChanges':[],'historicalReportsUnchanged':True,'originalSourcesAndBaselinesUnchanged':True,'hyperdocLoadedOrChanged':False,
      'newDependencyDownloads':0,'persistentLispImagesTouched':False,'acceptancePassed':True})
    print(json.dumps({'acceptancePassed':True,'statuses':after,'xtmChecks':len(labels),'faultControls':108,'output':str(output)}))

if __name__=='__main__':main()
