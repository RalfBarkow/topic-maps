#!/usr/bin/env python3
"""Read-only audit of Slice 22C evidence; writes its result only outside both repos."""
import argparse, ast, datetime, hashlib, json, re, subprocess
from pathlib import Path
from urllib.parse import unquote
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
HYPERDOC = Path('/Users/rgb/workspace/hyperdoc-dreyeck-ch')
BASE = 'bc9dcfb02f945422970d65266dc66b991806777d'
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args, cwd=ROOT): return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    out=ap.parse_args().output.resolve()
    assert not out.is_relative_to(ROOT) and not out.is_relative_to(HYPERDOC)
    out.mkdir(parents=True,exist_ok=True)
    initial=read(HERE/'initial-state.json');protected=initial['trackedFileSHA256']
    assert len(protected)==6891 and protected=={p:sha(ROOT/p) for p in protected}
    assert git('merge-base',BASE,'HEAD')==BASE
    historical=[p for p in protected if p.startswith('reports/')];assert len(historical)==4615
    lock=read(ROOT/'references/corpus-lock.json')
    for f in lock['files']:
        p=ROOT/'vendor/cxtm'/f['path'];assert p.stat().st_size==f['size'] and sha(p)==f['sha256']
    assert len(lock['files'])==2006
    hyperdoc=initial['priorHyperdocInspection']
    hyperdoc_head=git('rev-parse','HEAD',cwd=HYPERDOC)
    hyperdoc_status=git('status','--porcelain=v1',cwd=HYPERDOC)
    hyperdoc_hashes={p:sha(HYPERDOC/p) for p in hyperdoc['files']}
    hyperdoc_changed={p:{'before':h,'after':hyperdoc_hashes[p]} for p,h in hyperdoc['files'].items() if h!=hyperdoc_hashes[p]}
    # Other work may advance this neighbouring repo while the user pauses/resumes
    # the task. Record that observation; never reset it or attribute it to 22C.
    new_paths=set(git('ls-files','--others','--exclude-standard').splitlines())|set(git('diff','--name-only',BASE).splitlines())
    allowed=lambda p: p.startswith('reports/slice-22c/') or p in ['docs/slice-22c-normative-decisions.md','docs/slice-22c-original-evidence.md']
    assert all(allowed(p) for p in new_paths)
    # Also include committed 22C files when verifying the finished commit later.
    artifacts=[p for p in HERE.rglob('*') if p.is_file()]+[ROOT/'docs/slice-22c-normative-decisions.md',ROOT/'docs/slice-22c-original-evidence.md']
    assert not any(p.is_symlink() or p.suffix in ['.fasl','.pyc','.pdf','.html'] for p in artifacts)
    json_count=0
    for p in artifacts:
        if p.suffix=='.json':read(p);json_count+=1
        if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
    execution=read(HERE/'execution.json');reg=read(HERE/'regression/execution.json')
    expected={'CTM':{'pass':262,'fail':4,'not-run':7},'XTM':{'pass':71,'fail':0,'not-run':53},'total':{'pass':333,'fail':4,'not-run':60}}
    assert execution['statusesBefore']==execution['statusesAfter']==reg['statusesAfter']==expected
    assert execution['validationPassed'] and execution['newOriginalPASS']==0 and reg['acceptancePassed']
    assert len(reg['runs'])==114 and sum(r['expectedExitCode']==1 for r in reg['runs'])==108
    for r in reg['runs']:
        assert r['exitCode']==r['expectedExitCode']
        assert r['network']==r['repositoryWrites']==r['hyperdocWrites']=='denied'
        assert r['command'][:2]==['/usr/bin/sandbox-exec','-p'] and '(deny network*)' in r['command'][2]
        if any('/sbcl' in arg for arg in r['command']):
            assert '--no-sysinit' in r['command'] and '--no-userinit' in r['command']
    comparisons=read(HERE/'regression-comparison.json');assert len(comparisons)==159
    for c in comparisons:
        previous=ROOT/c['previous'];fresh=HERE/c['fresh']
        assert previous.read_bytes()==fresh.read_bytes() and sha(fresh)==c['sha256']
    assert len(read(HERE/'regression/after-diagnostics.json'))==124
    for c in read(HERE/'observation-comparison.json'):
        p=HERE/'investigation'/c['name']
        assert sha(p)==c['sha256'] and p.read_bytes()==(ROOT/'reports/slice-22a/investigation'/c['name']).read_bytes()
    evidence=read(HERE/'case-evidence.json');assert len(evidence['cases'])==13
    assert evidence['decisionCounts']=={'A':1,'B':0,'C':12} and evidence['statusChanges']==evidence['newPASS']==0
    original_ids={c['id'] for c in read(ROOT/'reports/slice-22a/matrix.json')['cases'] if c['id'].startswith('ctm/') or c['id'] in ['xtm2/in/mergemap-itemid.xtm','xtm2/in/mergemap-loop.xtm']}
    assert {c['id'] for c in evidence['cases']}==original_ids
    count_diff=count_templates=count_expanded=0
    for c in evidence['cases']:
        assert c['registeredBefore']==c['registeredAfter']
        for f in [c['source'],c['baseline'],*c['auxiliarySources']]:
            if f is None:continue
            p=ROOT/f['path'];b=p.read_bytes()
            assert b.hex()==f['hex'] and len(b)==f['bytes'] and sha(p)==f['sha256']
        if c.get('completeModelComparison'):
            count_diff+=1
            assert c['actualCondition'] is None and c['completeModelComparison']['nativePropertiesMatchActualCXTM']
            assert len(c['completeModelComparison']['differences'])==1 and not c['comparison']['byteExact']
            actual=HERE/'comparisons'/(Path(c['id']).name+'.actual.cxtm')
            assert sha(actual)==c['actualCXTM']['sha256'] and actual.read_bytes().hex()==c['actualCXTM']['hex']
            assert (HERE/'comparisons'/(Path(c['id']).name+'.diff')).read_text()==c['completeCXTMUnifiedDiff']
        if c.get('templateAnalysis'):
            count_templates+=1;assert c['variablePositionsReverifiedFromOriginal']
            assert c['actualCondition']['condition']=='INVALID-TEMPLATE-BODY'
            for control in c['expandedControls']:
                count_expanded+=1;assert control['byteExact'] and control['condition'] is None
                assert control['actualCXTM']==c['baseline']['text']
            if c.get('intendedNegativeCause'):assert c['intendedNegativeCause']['currentlyReached'] is False
    assert (count_diff,count_templates,count_expanded)==(4,7,3)
    links=[]
    for p in [ROOT/'docs/slice-22c-normative-decisions.md',ROOT/'docs/slice-22c-original-evidence.md']:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in target:continue
            dest=(p.parent/unquote(target.split('#')[0])).resolve()
            assert dest.exists() or dest in [HERE/'precommit-audit.json',HERE/'artifacts.json'],(p,target)
            links.append(dict(document=str(p.relative_to(ROOT)),target=target))
    sources=['scripts/validate-slice-22b.py','scripts/validate-slice-21o.py','reports/slice-22a/observations.lisp','reports/slice-20j/controls.lisp','reports/slice-22c/reproduce.py','reports/slice-22c/auxiliary.lisp','reports/slice-22c/build-evidence.py','reports/slice-22c/audit-evidence.py']
    result=dict(kind='slice-22c-final-read-only-evidence-audit',timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        baseCommit=BASE,observedHEAD=git('rev-parse','HEAD'),branch=git('branch','--show-current'),
        baseTrackedFilesVerified=len(protected),historicalReportsVerified=len(historical),pinnedCorpusFilesVerified=len(lock['files']),
        allOriginalFilesUnchanged=True,onlyNewSlice22CPaths=True,
        hyperdocUnchanged=(hyperdoc_head==hyperdoc['head'] and hyperdoc_status==hyperdoc['status'] and not hyperdoc_changed),
        hyperdocHead=hyperdoc_head,hyperdocHeadAtStart=hyperdoc['head'],hyperdocClean=(hyperdoc_status==''),
        hyperdocInspectedSourceCount=len(hyperdoc['files']),hyperdocSourceHashesUnchanged=len(hyperdoc['files'])-len(hyperdoc_changed),
        hyperdocChangedSourceHashes=hyperdoc_changed,
        hyperdocChangedPathsSinceStart=git('diff','--name-only',hyperdoc['head'],'HEAD',cwd=HYPERDOC).splitlines(),
        hyperdocTouchedBySlice=False,
        hyperdocProvenance='Observed neighbouring-repository change during interruption, after the completed offline regression; earlier audit retained in audit-before-resume.json. No writes or loads by Slice 22C.',
        regressionProcesses=114,expectedFaultExits=108,readerDiagnostics=124,byteIdenticalBehavioralReports=159,
        completeOriginalComparisons=4,templateObservations=7,expandedControls=3,decisionCounts=evidence['decisionCounts'],
        statuses=expected,newRegistrations=0,allJSONParsed=json_count,localMarkdownLinks=links,
        examinedToolHashes={p:sha(ROOT/p) for p in sources},
        sandboxStartupError='UnsupportedOperation("writable root /Users/rgb/.nix-profile contains symlink component /Users/rgb/.nix-profile; symlinked writable roots are not supported.\nIf this writable root is at or beneath CODEX_HOME and you trust its symlink targets, set `allow_symlinked_codex_home = true` at the top level of `$CODEX_HOME/config.toml` (normally `~/.codex/config.toml`) on the execution host, then restart Codex or its executor. This opt-out trusts targets outside CODEX_HOME and targets changed between commands. It does not apply to other writable roots.")',
        sandboxResolution='Regular require_escalated approval; canonical SBCL path and explicit child sandbox. No symlink/config edits or approval bypass.',
        passed=True)
    (out/'precommit-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','baseTrackedFilesVerified','historicalReportsVerified','pinnedCorpusFilesVerified','decisionCounts']}))
if __name__=='__main__':main()
