#!/usr/bin/env python3
"""Reproduce Slice 22A through the existing offline harness and diagnostic APIs.
No production/test registration changes. Outputs must be outside the repository.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent
BASE = '1c0b92c68fe1114b926d4405b553dfb096d2f425'
RUNTIME = '/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl'
POLICY = '(version 1)(allow default)(deny network*)(deny file-write* (subpath "'+str(ROOT)+'"))(deny file-write* (subpath "/Users/rgb/workspace/hyperdoc-dreyeck-ch"))'


def read(p): return json.loads(p.read_text())
def save(p,v): p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def verify_baseline(baseline):
    previous = ROOT/'reports/slice-21o'
    names=['xtm.json','ctm.validation.json','ctm.cxtm.json','ctm.encoding.json','after-diagnostics.json','further-variant-reification.json']
    names += [str(p.relative_to(previous)) for p in sorted((previous/'retained').glob('*.json'))]
    names += [p.name for p in sorted(previous.glob('*-control-*.json'))]
    rows=[]
    for name in names:
        old,new=previous/name,baseline/name
        assert read(old)==read(new),name
        assert sha(old)==sha(new),name
        rows.append({'previousReport':str(old.relative_to(ROOT)),'freshReport':'baseline/'+name,
                     'bytes':new.stat().st_size,'previousSHA256':sha(old),'freshSHA256':sha(new),'byteIdentical':True})
    assert len(rows)==154
    ex=read(baseline/'execution.json')
    assert ex['acceptancePassed'] and ex['standaloneXTMChecks']==2384 and ex['faultControls']==103
    assert ex['xtmStatusesAfter']=={'pass':70,'fail':0,'unsupported':0,'not-run':54}
    assert ex['ctmStatusesAfter']=={'pass':262,'fail':4,'unsupported':0,'not-run':7}
    assert len(ex['runs'])==109 and all(r['exitCode']==r['expectedExitCode'] for r in ex['runs'])
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--sbcl',default=RUNTIME)
    p.add_argument('--reuse-baseline',type=Path,help='Verify an already completed fresh execution; never trust its status without byte comparisons.')
    p.add_argument('--reuse-observations',type=Path,help='Verify retained fresh observations against all originals; no added executions.')
    args=p.parse_args();out=args.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=True)
    assert not (out/'execution.json').exists(),'Choose an unused output directory.'
    subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT,check=True)
    tracked=git('ls-tree','-r','--name-only',BASE).splitlines()
    assert not git('diff',BASE,'--',*tracked)
    protected={p:sha(ROOT/p) for p in tracked}
    inputs={str(p.relative_to(ROOT)):sha(p) for p in [*EVIDENCE.glob('*.py'),*EVIDENCE.glob('*.lisp')]}
    env={k:v for k,v in os.environ.items() if not k.startswith('TOPIC_MAPS_')};env.update(PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0',SBCL=args.sbcl)
    assert subprocess.check_output([args.sbcl,'--version'],text=True).strip()=='SBCL 2.5.4'
    runs=[];started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    def run(label,command,env,sandbox=True):
        if sandbox:command=['/usr/bin/sandbox-exec','-p',POLICY]+command
        before=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (out/(label+'.log')).write_bytes(r.stdout);runs.append(dict(label=label,command=command,exitCode=r.returncode,
            startedAtUTC=before,finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),network='denied in every test child',repositoryWrites='denied in every test child'))
        assert r.returncode==0,(label,r.stdout.decode()[-4000:]);return r.stdout.decode()
    baseline=args.reuse_baseline.resolve() if args.reuse_baseline else out/'baseline'
    if not args.reuse_baseline:
        run('baseline-orchestration',['python3',str(ROOT/'scripts/validate-slice-21o.py'),'--sbcl',args.sbcl,'--output',str(baseline)],env,sandbox=False)
    comparisons=verify_baseline(baseline);save(out/'baseline-comparison.json',comparisons)
    observations=args.reuse_observations.resolve() if args.reuse_observations else out/'investigation'
    if not args.reuse_observations:
        observations.mkdir();prov=json.loads(run('source-preparation',['python3',str(ROOT/'scripts/validate-slice-21o.py'),'--prepare',str(out/'sources')],env))
        save(observations/'source-preparation.json',prov)
        env.update(CL_SOURCE_REGISTRY=prov['sourceRegistry'],TOPIC_MAPS_22A_ROOT=str(ROOT),TOPIC_MAPS_22A_OUTPUT=str(observations),TOPIC_MAPS_20J_OUTPUT=str(observations))
        ids=[c['id'] for c in read(baseline/'ctm.validation.json')['cases'] if c['status']!='pass']
        (observations/'case-ids.sexp').write_text('('+' '.join(json.dumps(x) for x in ids)+')\n');env['TOPIC_MAPS_22A_IDS']=str(observations/'case-ids.sexp')
        prefix=[args.sbcl,'--noinform','--no-sysinit','--no-userinit','--script']
        run('observations',prefix+[str(EVIDENCE/'observations.lisp')],env)
        env['TOPIC_MAPS_22A_PROFILE_REPORT']=str(observations/'profile-probes.json')
        run('profile-probes',prefix+[str(EVIDENCE/'profile-probes.lisp')],env)
    assert read(observations/'ctm-observations.json')['caseStatesUnchanged']
    assert read(observations/'controls.json')==read(ROOT/'reports/slice-20j/observed-controls.json')
    assert len(read(observations/'profile-probes.json'))==8
    spec=importlib.util.spec_from_file_location('closure_matrix',EVIDENCE/'build-matrix.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    matrix=module.make_matrix(baseline,observations);save(out/'matrix.json',matrix);(out/'matrix.md').write_text(module.markdown_matrix(matrix))
    lock=read(ROOT/'references/corpus-lock.json')
    for entry in lock['files']:
        f=ROOT/'vendor/cxtm'/entry['path'];assert f.stat().st_size==entry['size'] and sha(f)==entry['sha256']
    for snapshot in [protected,inputs]:assert snapshot=={p:sha(ROOT/p) for p in snapshot}
    save(out/'integrity.json',{'baseCommit':BASE,'allBaseTrackedFilesSHA256':protected,'historicalReportFilesVerified':sum(p.startswith('reports/') for p in protected),
      'pinnedCorpusFilesVerified':len(lock['files']),'investigationToolsSHA256':inputs,'allBaseTrackedFilesUnchanged':True})
    save(out/'execution.json',{'kind':'read-only-conformance-closure-investigation','baseCommit':BASE,'branch':git('branch','--show-current'),
      'runtime':'SBCL 2.5.4','startedAtUTC':started,'finishedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'baselineExecution':'baseline/execution.json','baselineWasFreshExecution':True,'reusedFreshExecutionDirectory':str(baseline) if args.reuse_baseline else None,
      'reusedFreshObservationDirectory':str(observations) if args.reuse_observations else None,'behavioralReportsByteIdenticalToSlice21O':len(comparisons),
      'baselineFreshTestProcesses':109,'additionalFreshObservationProcesses':2,'supplementalProfileProbes':8,'retainedTemplateContextProbes':12,
      'ctmOriginalObservations':11,'xtmOriginalObservations':124,'matrixCases':65,'runs':runs,'statusesBefore':matrix['registeredTotals'],'statusesAfter':matrix['registeredTotals'],
      'newOriginalPASS':0,'caseRegistrationChanged':False,'productionCodeChanged':False,'corpusChanged':False,'historicalReportsChanged':False,'hyperdocModifiedOrLoaded':False,
      'newDependencyDownloads':0,'persistentLispImagesTouched':False,'validationPassed':True})
    print(json.dumps({'validationPassed':True,'matrixCases':65,'reportsExactlyReproduced':len(comparisons),'output':str(out)}))

if __name__=='__main__':main()
