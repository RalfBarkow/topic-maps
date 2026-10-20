#!/usr/bin/env python3
"""Slice 22C: reuse the existing offline regression and read-only observers.
Default: execute all 114 regression processes, then CTM/auxiliary observations.
--reuse-regression accepts only a freshly executed, fully checked report directory.
Writes only to --output outside the repositories; no registration or norm download.
"""
import argparse, datetime, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = 'bc9dcfb02f945422970d65266dc66b991806777d'
SBCL = '/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl'
HYPERDOC = Path('/Users/rgb/workspace/hyperdoc-dreyeck-ch')
POLICY = f'(version 1)(allow default)(deny network*)(deny file-write* (subpath "{ROOT}"))(deny file-write* (subpath "{HYPERDOC}"))'
def read(p): return json.loads(p.read_text())
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a): return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--sbcl',default=SBCL)
    ap.add_argument('--reuse-regression',type=Path)
    args=ap.parse_args();out=args.output.resolve()
    assert not out.is_relative_to(ROOT) and not out.is_relative_to(HYPERDOC)
    out.mkdir(parents=True,exist_ok=True)
    assert not (out/'execution.json').exists(),'Choose a new output directory.'
    assert subprocess.check_output([args.sbcl,'--version'],text=True).strip()=='SBCL 2.5.4'
    subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT,check=True)
    tracked=git('ls-tree','-r','--name-only',BASE).splitlines()
    assert not set(git('diff','--name-only',BASE).splitlines()) & set(tracked)
    protected={p:sha(ROOT/p) for p in tracked}
    env={k:v for k,v in os.environ.items() if not k.startswith('TOPIC_MAPS_')}
    env.update(PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0',SBCL=args.sbcl)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();runs=[]
    def run(label,command,child_env=env,sandbox=True):
        if sandbox:command=['/usr/bin/sandbox-exec','-p',POLICY]+command
        start=datetime.datetime.now(datetime.timezone.utc).isoformat()
        p=subprocess.run(command,cwd=ROOT,env=child_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=900)
        (out/(label+'.log')).write_bytes(p.stdout)
        runs.append(dict(label=label,command=command,exitCode=p.returncode,startedAtUTC=start,
            finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            network='denied in test children',repositoryWrites='denied in test children',freshProcess=True))
        assert p.returncode==0,(label,p.stdout.decode()[-4000:])
        return p.stdout.decode()
    regression=args.reuse_regression.resolve() if args.reuse_regression else out/'regression'
    if not args.reuse_regression:
        run('regression-orchestration',['python3',str(ROOT/'scripts/validate-slice-22b.py'),'--sbcl',args.sbcl,'--output',str(regression)],sandbox=False)
    ex=read(regression/'execution.json')
    expected={'XTM':{'pass':71,'fail':0,'not-run':53},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':333,'fail':4,'not-run':60}}
    assert ex['acceptancePassed'] and ex['statusesAfter']==expected
    assert len(ex['runs'])==114 and ex['faultControls']==108
    assert all(r['exitCode']==r['expectedExitCode'] and r['network']=='denied' and r['repositoryWrites']=='denied' for r in ex['runs'])
    old=ROOT/'reports/slice-22b/after'
    report_names=['xtm.json','ctm.validation.json','ctm.cxtm.json','ctm.encoding.json','after-diagnostics.json','original-contract.json']
    report_names += [str(p.relative_to(old)) for p in sorted((old/'retained').glob('*.json'))]
    report_names += [p.name for p in sorted(old.glob('*-control-*.json'))]
    comparisons=[]
    for name in report_names:
        assert (old/name).read_bytes()==(regression/name).read_bytes(),name
        comparisons.append(dict(previous='reports/slice-22b/after/'+name,fresh='regression/'+name,sha256=sha(regression/name),byteIdentical=True))
    assert len(read(regression/'after-diagnostics.json'))==124
    save(out/'regression-comparison.json',comparisons)
    obs=out/'investigation';obs.mkdir()
    prov=json.loads(run('source-preparation',['python3',str(ROOT/'scripts/validate-slice-21o.py'),'--prepare',str(out/'sources')]))
    save(obs/'source-preparation.json',prov)
    ids=[c['id'] for c in read(regression/'ctm.validation.json')['cases'] if c['status']!='pass']
    assert len(ids)==11
    (obs/'case-ids.sexp').write_text('('+' '.join(json.dumps(x) for x in ids)+')\n')
    env.update(CL_SOURCE_REGISTRY=prov['sourceRegistry'],TOPIC_MAPS_22A_ROOT=str(ROOT),TOPIC_MAPS_22A_OUTPUT=str(obs),
        TOPIC_MAPS_22A_IDS=str(obs/'case-ids.sexp'),TOPIC_MAPS_20J_OUTPUT=str(obs),TOPIC_MAPS_22C_OUTPUT=str(obs))
    prefix=[args.sbcl,'--noinform','--no-sysinit','--no-userinit','--script']
    run('ctm-observations',prefix+[str(ROOT/'reports/slice-22a/observations.lisp')])
    run('xtm-auxiliary-observations',prefix+[str(HERE/'auxiliary.lisp')])
    obs_comp=[]
    for name in ['ctm-observations.json','controls.json']:
        prior=ROOT/'reports/slice-22a/investigation'/name
        assert (obs/name).read_bytes()==prior.read_bytes(),name
        obs_comp.append(dict(name=name,sha256=sha(obs/name),byteIdenticalTo22A=True))
    assert read(obs/'ctm-observations.json')['caseStatesUnchanged']
    save(out/'observation-comparison.json',obs_comp)
    lock=read(ROOT/'references/corpus-lock.json')
    for e in lock['files']:
        p=ROOT/'vendor/cxtm'/e['path'];assert p.stat().st_size==e['size'] and sha(p)==e['sha256']
    assert protected=={p:sha(ROOT/p) for p in tracked}
    save(out/'integrity.json',dict(baseCommit=BASE,allBaseTrackedFilesSHA256=protected,allBaseTrackedFilesUnchanged=True,
        pinnedCorpusFilesVerified=len(lock['files']),historicalReportFilesVerified=sum(p.startswith('reports/') for p in tracked)))
    save(out/'execution.json',dict(kind='slice-22c-read-only-normative-investigation',baseCommit=BASE,branch=git('branch','--show-current'),
        runtime='SBCL 2.5.4',startedAtUTC=started,finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),runs=runs,
        regressionDirectory=str(regression),reusedFreshRegression=args.reuse_regression is not None,
        regressionStartedAtUTC=ex['startedAtUTC'],regressionFinishedAtUTC=ex['finishedAtUTC'],regressionProcesses=114,
        regressionBehavioralReportsByteIdentical=len(comparisons),diagnosticObservations=124,faultControls=108,
        additionalObservationProcesses=2,ctmOriginalObservations=11,xtmOriginalObservations=124,auxiliaryReads=2,
        statusesBefore=expected,statusesAfter=expected,newOriginalPASS=0,productionChanged=False,registrationChanged=False,
        originalSourcesAndBaselinesUnchanged=True,historicalReportsUnchanged=True,newDownloads=0,persistentImages=False,validationPassed=True))
    print(json.dumps(dict(validationPassed=True,reportsExactlyReproduced=len(comparisons),output=str(out))))
if __name__=='__main__':main()
