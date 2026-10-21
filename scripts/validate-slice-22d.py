#!/usr/bin/env python3
"""Reproduce Slice 22D using the existing ASDF, XML and corpus harnesses.
Writes only to --output outside the repository. --audit-only rechecks saved runs;
it never represents them as new executions. Dependencies come from local pins.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = 'b5c5ea5cc84dd31104045d032c25880b8bd62839'
TOOLS = ROOT / 'reports/slice-22d'
TARGET = 'xtm2/in/variant-datatype-unknown.xtm'
RUNTIME = '/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl'
POLICY = f'(version 1)(allow default)(deny network*)(deny file-write* (subpath "{ROOT}"))(deny file-write* (subpath "/Users/rgb/workspace/hyperdoc-dreyeck-ch"))'
CTM = {'pass':262,'fail':4,'unsupported':0,'not-run':7}
ALLOWED = {'src/xtm/reader.lisp','topic-maps.asd'} | {r['file'] for r in json.loads((TOOLS/'retargetings.json').read_text())}
EXECUTION_FILES = ALLOWED | {'tests/xtm-resource-datatypes.lisp','reports/slice-22d/failure-controls.lisp'}
MODES = {'mismatch':('cxtm-mismatch',None,None), 'xml':('execution-error','XTM-XML-ERROR','xml-not-well-formed'),
         'xtm':('execution-error','XTM-REJECTION','invalid-id'), 'unsupported':('unsupported','XTM-UNSUPPORTED','resource-data-datatype'),
         'tmdm':('execution-error','REIFICATION-ERROR','reifier-conflict')}

def read(p): return json.loads(p.read_text())
def save(p,v): p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def prepare_pinned(target):
    spec=importlib.util.spec_from_file_location('slice22b',ROOT/'scripts/validate-slice-22b.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.prepare_pinned(target)
def old_label(s):
    return s.replace('resourceData-anyType','resourceData-integer').replace('anyType-text-still-unsupported','integer-still-unsupported')
def changes(a,b,path=''):
    if a==b:return []
    if isinstance(a,dict) and isinstance(b,dict):
        return [d for k in sorted(a.keys()|b.keys()) for d in changes(a.get(k),b.get(k),path+'/'+k)]
    if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        return [d for i,(x,y) in enumerate(zip(a,b)) for d in changes(x,y,path+'/'+str(i))]
    return [{'path':path,'before':a,'after':b}]


def condition_nodes(value,path=''):
    if isinstance(value,dict):
        for k,v in value.items():
            if k=='condition' and isinstance(v,dict):yield path+'/'+k,v
            else:yield from condition_nodes(v,path+'/'+k)
    elif isinstance(value,list):
        for i,v in enumerate(value):yield from condition_nodes(v,path+'/'+str(i))

def verify_baseline(baseline):
    ex=read(baseline/'execution.json'); assert ex['acceptancePassed']
    assert ex['statusesAfter']['XTM']=={'pass':71,'fail':0,'not-run':53}
    assert ex['statusesAfter']['CTM']=={'pass':262,'fail':4,'not-run':7}
    assert ex['standaloneXTMChecks']==2396 and ex['retainedLispChecks']==12100
    assert len(ex['runs'])==114 and ex['faultControls']==108
    assert all(r['exitCode']==r['expectedExitCode'] for r in ex['runs'])
    # Preserve the provenance of the reused 22B runner; its older base/statusBefore
    # fields describe that runner, not the actual 22D pre-change checkout.
    previous=ROOT/'reports/slice-22b/after'
    rows=[]
    for p in sorted(baseline.rglob('*.json')):
        rel=p.relative_to(baseline); old=previous/rel
        if str(rel) in {'execution.json','integrity.json','source-preparation.json','baseline-comparison.json','retained-fault-reports.json'}: continue
        if old.exists():
            assert read(p)==read(old),str(rel)
            rows.append({'report':str(rel),'sha256':sha(p),'historical22BBehaviorIdentical':True})
    assert read(baseline/'xtm.json')['cases']==read(previous/'xtm.json')['cases']
    return rows

def collect(output,baseline):
    assert not (output/'runs.json').exists(),'Use an unused output directory, or --audit-only.'
    assert subprocess.check_output([RUNTIME,'--version'],text=True).strip()=='SBCL 2.5.4'
    env={k:v for k,v in os.environ.items() if not k.startswith('TOPIC_MAPS_')}
    env.update(PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0',SBCL=RUNTIME)
    sources={p:sha(ROOT/p) for p in sorted(EXECUTION_FILES)}
    started=now();runs=[];retained=output/'retained';retained.mkdir()
    def run(label,cmd,env,expected=0):
        command=['/usr/bin/sandbox-exec','-p',POLICY]+cmd;t=now()
        r=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
        log=output/(label+'.log');log.write_bytes(r.stdout)
        runs.append({'label':label,'command':command,'startedAtUTC':t,'finishedAtUTC':now(),
          'exitCode':r.returncode,'expectedExitCode':expected,'logSHA256':sha(log),'network':'denied',
          'repositoryWrites':'denied','hyperdocWrites':'denied','freshProcess':True})
        save(output/'runs.json',{'startedAtUTC':started,'runs':runs,'executionSourcesSHA256':sources})
        assert r.returncode==expected,(label,r.stdout.decode()[-2500:])
        print(f'{label}: expected exit {expected}',flush=True)
        return r.stdout.decode()
    with tempfile.TemporaryDirectory(prefix='topic-maps-22d-sources-') as tmp:
        # The source-preparation subprocess is also network/repository-write denied.
        text=run('source-preparation',['python3',str(Path(__file__)),'--prepare',tmp+'/sources'],env)
        provenance=json.loads(text);save(output/'source-preparation.json',provenance)
        env.update(CL_SOURCE_REGISTRY=provenance['sourceRegistry'],TOPIC_MAPS_REPORT=str(retained/'core.json'),
          TOPIC_MAPS_XTM_REPORT=str(output/'xtm.json'),TOPIC_MAPS_XTM_MERGEMAP_REPORT=str(retained/'xtm-mergemap'),
          TOPIC_MAPS_REGISTERED_ORIGINALS_REPORT=str(retained/'slice20a'),TOPIC_MAPS_REGISTERED_NEGATIVES_REPORT=str(retained/'slice20b'),
          TOPIC_MAPS_PROLOG_REPORT=str(retained/'slice20c'),TOPIC_MAPS_EMPTY2_REPORT=str(retained/'slice20e'),
          TOPIC_MAPS_CTM_INTEGER_REPORT=str(retained/'slice20f'),TOPIC_MAPS_TRIPLE_REPORT=str(retained/'slice20g'),TOPIC_MAPS_ENCODING_REPORT=str(output/'ctm'))
        prefix=[RUNTIME,'--noinform','--no-sysinit','--no-userinit','--script']
        run('xml',prefix+['tests/cxml-probe.lisp'],env)
        run('variant-reifier-api-preflight',prefix+['reports/slice-21o/api-preflight.lisp'],env)
        run('xtm',prefix+['scripts/fresh-xtm.lisp'],env)
        run('regression',[str(ROOT/'scripts/test.sh')],env)
        run('diagnostics',prefix+['reports/slice-21o/diagnostics.lisp'],dict(env,TOPIC_MAPS_21O_ROOT=str(ROOT),
          TOPIC_MAPS_21O_DIAGNOSTICS=str(output/'after-diagnostics.json'),TOPIC_MAPS_21O_EXTRA=tmp+'/reader-only-extra.json'))
        labels=[r['label'] for r in read(baseline/'execution.json')['runs'] if '-control-' in r['label']]
        assert len(labels)==108
        labels += ['datatype-control-'+mode for mode in MODES]
        for label in labels:
            family,mode=label.split('-control-')
            run(label,prefix+[str(TOOLS/'failure-controls.lisp')],dict(env,TOPIC_MAPS_XTM_REPORT=str(output/(label+'.json')),
              TOPIC_MAPS_21O_FAMILY=family,TOPIC_MAPS_21O_FAULT=mode),1)
    assert sources=={p:sha(ROOT/p) for p in sources}
    r=read(output/'runs.json');r['finishedAtUTC']=now()
    r['rawReportSHA256']={str(p.relative_to(output)):sha(p) for p in sorted(output.rglob('*.json')) if p.name!='runs.json'}
    save(output/'runs.json',r)

def audit(output,baseline,initial):
    start=read(initial);assert start['baseCommit']==BASE and start['indexClean'] and start['worktreeClean']
    assert set(git('diff','--name-only',BASE).splitlines())&set(start['trackedFileSHA256'])<=ALLOWED
    protected={p:h for p,h in start['trackedFileSHA256'].items() if p not in ALLOWED}
    assert protected=={p:sha(ROOT/p) for p in protected}
    save(output/'baseline-comparison.json',verify_baseline(baseline))
    runs=read(output/'runs.json');assert len(runs['runs'])==119
    assert all(r['exitCode']==r['expectedExitCode'] and sha(output/(r['label']+'.log'))==r['logSHA256'] for r in runs['runs'])
    assert runs['executionSourcesSHA256']=={p:sha(ROOT/p) for p in runs['executionSourcesSHA256']}
    assert runs['rawReportSHA256']=={p:sha(output/p) for p in runs['rawReportSHA256']}
    previous=read(baseline/'xtm.json');xtm=read(output/'xtm.json')
    labels=re.findall(r'^XTM-CHECK-PASS (.+)$',(output/'xtm.log').read_text(),re.M)
    assert labels==xtm['checks'] and len(labels)==len(set(labels))
    normalized=[old_label(l) for l in labels]
    assert [l for l in normalized if l in set(previous['checks'])]==previous['checks']
    assert xtm['statuses']=={'pass':72,'fail':0,'unsupported':0,'not-run':0}
    assert xtm['otherCorpusInputs']=={'positiveUnexecuted':49,'negativeUnregisteredUnexecuted':3}
    assert xtm['cases'][:71]==previous['cases'] and len(xtm['cases'])==len({c['id'] for c in xtm['cases']})==72
    assert xtm['cases'][-1]['id']==TARGET and xtm['cases'][-1]['status']=='pass'
    assert f'XTM-SUMMARY {len(labels)} PASS 0 FAIL; 64 original CXTM PASS; 8 negative originals PASS' in (output/'xtm.log').read_text()
    # Every prior original model/output stays identical. Control retargetings are
    # recorded separately, including source and exact condition/position changes.
    meta={'scope','statuses','otherCorpusInputs','checks','cases'}
    control_diffs=[]
    for k,v in previous.items():
        if k in meta: continue
        if k.endswith('Controls'):
            assert len(v)==len(xtm[k]),k
            for i,(a,b) in enumerate(zip(v,xtm[k])):
                if a!=b:
                    ds=changes(a,b)
                    assert all(d['path'] in {'/label','/sourceText','/sourceKey','/condition/code','/condition/column','/condition/detail','/condition/message','/condition/sourceKey'} for d in ds),(k,i,ds)
                    if a.get('condition') and b.get('condition'):assert a['condition']['class']==b['condition']['class']
                    control_diffs.append({'field':k,'index':i,'before':a,'after':b,'differences':ds})
        else:assert xtm[k]==v,k
    save(output/'retargeted-control-observations.json',control_diffs)
    before_diags=read(baseline/'after-diagnostics.json');after_diags=read(output/'after-diagnostics.json')
    assert len(before_diags)==len(after_diags)==124
    delta=[{'id':a['id'],'before':a,'after':b} for a,b in zip(before_diags,after_diags) if a!=b]
    assert len(delta)==1 and delta[0]['id']==TARGET
    assert delta[0]['after']['byteExact'] and delta[0]['after']['condition'] is None
    save(output/'diagnostic-changes.json',{'readerObservations':124,'changed':1,'unchanged':123,'changes':delta})
    faults=[]
    for r in runs['runs']:
        label=r['label']
        if '-control-' not in label:continue
        result=read(output/(label+'.json'));family,mode=label.split('-control-')
        if family=='datatype':
            assert result['cases'][:71]==xtm['cases'][:71] and len(result['cases'])==72
            failed=result['cases'][-1];outcome,cls,code=MODES[mode]
            assert failed['id']==TARGET and failed['actualOutcome']==outcome and failed['status']!='pass'
            assert result['statuses']['pass']==71
            original=result['datatypeOriginals'][0];c=original['condition']
            if cls: assert c['class']==cls and c['code']==code,(mode,c)
            else: assert c is None and original['firstDifferentByte']==0
            faults.append({'label':label,'retained':False,'target':TARGET,'condition':c,'actualOutcome':outcome,
              'caseStatus':failed['status'],'retainedOriginalPASS':71,'expectedASDFFailureObserved':True,'faultCountedAsPass':False})
        else:
            old=read(baseline/(label+'.json'))
            assert len(old['cases'])==len(result['cases']),label
            for a,b in zip(old['cases'],result['cases']):
                assert {k:v for k,v in a.items() if k!='diagnostics'}=={k:v for k,v in b.items() if k!='diagnostics'},(label,a,b)
                if a['status']=='pass': assert a==b
            # Stop-on-error execution retains the same successful prefix. Later
            # cases are not executed; the normal run verifies all prior 71 PASS.
            assert result['statuses']==old['statuses'],label
            old_conditions=dict(condition_nodes(old));new_conditions=dict(condition_nodes(result))
            assert old_conditions.keys()==new_conditions.keys(),label
            condition_diffs=[]
            for path,c in old_conditions.items():
                d=new_conditions[path]
                assert c['class']==d['class'],(label,path,c,d)
                if c.get('code')!=d.get('code'):
                    # This documented synthetic source was changed from invalid
                    # default-string XML to valid but unimplemented anyType XML.
                    assert path=='/variantControls/52/condition' and c.get('code')=='resource-data-markup' and d.get('code')=='resource-data-datatype'
                if c!=d:condition_diffs.append({'path':path,'before':c,'after':d})
            faults.append({'label':label,'retained':True,'sameCaseStatusesAndOutcomes':True,
              'conditionClassesUnchanged':True,'conditionCodesUnchangedExceptDocumentedEmbeddedXMLRetargeting':True,'conditionChanges':condition_diffs,
              'priorCorrectPASSRetained':sum(c['status']=='pass' for c in result['cases']),
              'expectedASDFFailureObserved':True,'faultCountedAsPass':False,
              'caseDiagnosticChanges':changes(old['cases'],result['cases'])})
    assert len(faults)==113
    save(output/'failure-controls.json',{'retained':108,'new':5,'controls':faults,'allExpectedFailureExitsObserved':True})
    unchanged=[]
    for old in [*sorted((baseline/'retained').glob('*.json')),*[baseline/f'ctm.{s}.json' for s in ['validation','cxtm','encoding']]]:
        rel=old.relative_to(baseline)
        if str(rel)=='retained/xtm-mergemap.integration.json' and old.read_bytes()!=(output/rel).read_bytes():
            ds=changes(read(old),read(output/rel))
            save(output/'mergemap-retargeting.json',{'report':str(rel),'differences':ds})
            assert all('Only textual xsd:string and xsd:anyURI' in str(d['before']) or 'XMLSchema#integer' in str(d['before']) for d in ds),ds
            continue
        assert old.read_bytes()==(output/rel).read_bytes(),str(rel)
        unchanged.append({'report':str(rel),'sha256':sha(old),'byteIdentical':True})
    assert len(unchanged) in (47,48)
    save(output/'retained-reports.json',unchanged)
    regression=(output/'regression.log').read_text();ex=read(baseline/'execution.json')
    for marker,count in dict(ex['retainedChecks'],**ex['stageChecks']).items():
        assert int(re.search(r'(?m)^'+marker+r'-PASS: (\d+)',regression).group(1))==count
    assert 'Ran 2 tests' in regression and 'NFC-ORACLE-PASS: 16294' in regression
    xml=(output/'xml.log').read_text();assert 'CXML-SUMMARY 146 PASS 0 FAIL' in xml
    assert len(set(re.findall(r'^CXML-CHECK-PASS (.+)$',xml,re.M)))==146
    assert read(output/'ctm.validation.json')['statuses']==CTM
    original=xtm['datatypeOriginals'][0];source=ROOT/'vendor/cxtm'/TARGET
    baseline_file=ROOT/'vendor/cxtm/xtm2/baseline/variant-datatype-unknown.xtm.cxtm'
    actual=original['actualCXTM'].encode();expected=baseline_file.read_bytes()
    assert actual==expected==original['expectedCXTM'].encode() and len(actual)==original['actualBytes']==original['expectedBytes']==579
    assert source.read_bytes()==bytes.fromhex(original['sourceHex'])==original['sourceText'].encode()
    assert original['sourceBytes']==source.stat().st_size and original['condition'] is None and original['firstDifferentByte'] is None
    assert original['qualifiedParserCalls']==1 and original['status']=='pass' and original['sourceKey']==TARGET
    save(output/'original-contract.json',dict(original,sourceSHA256=sha(source),baselineSHA256=sha(baseline_file),
      actualSHA256=hashlib.sha256(actual).hexdigest(),byteExact=True,executedInASDFTestOp=True))
    (output/'actual').mkdir(exist_ok=True);(output/'actual/variant-datatype-unknown.xtm.cxtm').write_bytes(actual)
    matrix=read(ROOT/'reports/slice-22a/matrix.json');rows=[]
    prior_registered={c['id']:c['status'] for c in previous['cases']}
    for c in matrix['cases']:
        before=prior_registered.get(c['id'],c['registeredStatus']);after='pass' if c['id']==TARGET else before
        rows.append({'id':c['id'],'slice22A':c['registeredStatus'],'slice22C':before,'slice22D':after,'changedIn22D':before!=after})
    assert sum(r['changedIn22D'] for r in rows)==1
    save(output/'closure-delta.json',{'sourceMatrix':'reports/slice-22a/matrix.json','sourceMatrixSHA256':sha(ROOT/'reports/slice-22a/matrix.json'),
      'changedCase':TARGET,'newPASS':1,'remainingOpenCases':63,'slice22CDecisionsUnchanged':True,'twelveOpenCDecisionsUnchanged':True,'cases':rows})
    lock=read(ROOT/'references/corpus-lock.json')
    for entry in lock['files']:
        p=ROOT/'vendor/cxtm'/entry['path'];assert p.stat().st_size==entry['size'] and sha(p)==entry['sha256']
    assert protected=={p:sha(ROOT/p) for p in protected}
    save(output/'integrity.json',{'baseCommit':BASE,'protectedBaseFilesSHA256':protected,'executionSourcesSHA256':runs['executionSourcesSHA256'],
      'pinnedCorpusFilesVerified':len(lock['files']),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
      'productionChanges':['src/xtm/reader.lisp'],'historicalReportsUnchanged':True,'originalSourcesBaselinesAndLockUnchanged':True})
    after={'XTM':{'pass':72,'fail':0,'not-run':52},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':334,'fail':4,'not-run':59}}
    save(output/'execution.json',{'kind':'slice-22d-textual-resource-datatypes','baseCommit':BASE,'branch':git('branch','--show-current'),
      'runtime':'SBCL 2.5.4','auditToolSHA256':sha(Path(__file__)),'startedAtUTC':runs['startedAtUTC'],'finishedAtUTC':runs['finishedAtUTC'],'auditedAtUTC':now(),'runs':runs['runs'],
      'standaloneXTMChecks':len(labels),'retainedXTMChecks':2396,'newXTMChecks':len(labels)-2396,'retainedLispChecks':12100,
      'retainedChecks':ex['retainedChecks'],'stageChecks':ex['stageChecks'],'xmlQualificationChecks':146,
      'retainedOriginals':71,'newPositiveOriginals':1,'faultControls':113,'retainedFaultControls':108,'newFaultControls':5,
      'diagnosticOriginalObservations':124,'diagnosticChanges':1,'statusesBefore':ex['statusesAfter'],'statusesAfter':after,
      'pythonUnitTests':2,'nfcOracleComparisons':16294,'retainedNonXTMReportsByteIdentical':len(unchanged),
      'knownCTMFailuresUnchanged':[c['id'] for c in read(output/'ctm.validation.json')['cases'] if c['status']=='fail'],
      'pinnedCorpusFilesVerified':len(lock['files']),'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
      'productionChanges':['src/xtm/reader.lisp'],'historicalReportsUnchanged':True,'originalSourcesAndBaselinesUnchanged':True,
      'newDependencyDownloads':0,'persistentLispImagesTouched':False,'acceptancePassed':True})
    print(json.dumps({'acceptancePassed':True,'statuses':after,'xtmChecks':len(labels),'faultControls':113,'output':str(output)}))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path);ap.add_argument('--baseline',type=Path,default=TOOLS/'baseline')
    ap.add_argument('--initial',type=Path,default=TOOLS/'initial-state.json');ap.add_argument('--prepare',type=Path)
    ap.add_argument('--audit-only',action='store_true');args=ap.parse_args()
    if args.prepare:print(json.dumps(prepare_pinned(args.prepare)));return
    assert args.output;output=args.output.resolve();assert not output.is_relative_to(ROOT)
    output.mkdir(parents=True,exist_ok=True)
    verify_baseline(args.baseline)
    if not args.audit_only:collect(output,args.baseline)
    audit(output,args.baseline,args.initial)

if __name__=='__main__':main()
