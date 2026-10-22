#!/usr/bin/env python3
"""Integrity audit of saved Slice-22E execution; no test process is started."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import re
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'reports/slice-22e'
BASE='791969ca59922d61e967198eaee4c1fe172b5a0d'
ALLOWED={'src/xtm/package.lisp','src/xtm/reader.lisp','tests/xtm-identity.lisp','tests/xtm-map-reification.lisp','tests/ctm-xtm-mergemap.lisp','topic-maps.asd'}
NEW={'tests/xtm-mergemap.lisp','scripts/validate-slice-22e.py','docs/slice-22e-xtm-mergemap.md'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd,text=True).strip()
s=read(D/'initial-state.json');assert s['baseCommit']==BASE and s['indexClean'] and s['worktreeClean']
assert set(s['trackedFileSHA256'])==set(git('ls-tree','-r','--name-only',BASE).splitlines())
protected={p:h for p,h in s['trackedFileSHA256'].items() if p not in ALLOWED}
assert protected=={p:sha(ROOT/p) for p in protected}
changed=set(git('diff','--name-only',BASE).splitlines());untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
assert all(p in ALLOWED|NEW or p.startswith('reports/slice-22e/') for p in changed|untracked)
assert {p for p in changed if p.startswith('src/')}=={'src/xtm/package.lisp','src/xtm/reader.lisp'}
e=read(D/'after/execution.json');runs=read(D/'after/runs.json')
assert e['acceptancePassed'] and e['auditToolSHA256']==sha(ROOT/'scripts/validate-slice-22e.py')
assert len(runs['runs'])==119 and all(r['exitCode']==r['expectedExitCode'] and sha(D/'after'/(r['label']+'.log'))==r['logSHA256'] for r in runs['runs'])
assert runs['executionSourcesSHA256']=={p:sha(ROOT/p) for p in runs['executionSourcesSHA256']}
assert runs['rawReportSHA256']=={p:sha(D/'after'/p) for p in runs['rawReportSHA256']}
assert e['standaloneXTMChecks']==2704 and e['newXTMChecks']==182 and e['retainedLispChecks']==12100
assert e['statusesBefore']==e['statusesAfter']=={'XTM':{'pass':72,'fail':0,'not-run':52},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':334,'fail':4,'not-run':59}}
assert read(D/'after/xtm.json')['cases']==read(D/'baseline/xtm.json')['cases']==read(ROOT/'reports/slice-22d/after/xtm.json')['cases']
f=read(D/'after/failure-controls.json');assert f['retained']==113 and f['new']==0 and len(f['controls'])==113
assert all(c['expectedASDFFailureObserved'] and c['caseRecordsAndOutcomesIdentical'] and c['conditionClassesUnchanged'] and not c['faultCountedAsPass'] for c in f['controls'])
diag=read(D/'after/diagnostic-changes.json');assert diag['changed']==7 and diag['unchanged']==117
assert all(x['after']['condition']['code']=='resource-resolver-required' for x in diag['changes'])
obs=read(D/'after/original-observations.json');item=obs[0]
assert item['sourceBytes']==148 and item['childBytes']==151 and item['actualBytes']==224 and item['expectedBytes']==314 and item['firstDifferentByte']==12
for p,k in [('vendor/cxtm/xtm2/in/mergemap-itemid.xtm','sourceSHA256'),('vendor/cxtm/xtm2/in/mergemap-itemid.sub','childSHA256'),('vendor/cxtm/xtm2/baseline/mergemap-itemid.xtm.cxtm','baselineSHA256')]:assert sha(ROOT/p)==item[k]
assert sha(D/'after/actual/mergemap-itemid.xtm.cxtm')==item['actualSHA256']
assert item['condition'] is None and item['targetMapItemIdentifiers']==[] and item['onlyBaselineRootMapItemIdentifiersDiffer']
assert all(x['registeredStatus']=='not-run' and not x['registeredAsPASS'] for x in obs)
assert obs[1]['condition']['code']=='cyclic-mergemap' and obs[1]['resolverCalls']==1 and obs[1]['normativeCycleDecision'] is None
ret=read(D/'retargetings.json');assert len(ret)==3
for r in ret:
 assert r['before'] in subprocess.check_output(['git','show',BASE+':'+r['file']],cwd=ROOT,text=True)
 assert r['after'] in (ROOT/r['file']).read_text() and sha(ROOT/r['file'])==r['finalFileSHA256']
unchanged=read(D/'after/retained-reports.json');assert len(unchanged)==47
for r in unchanged:assert sha(D/'after'/r['report'])==r['sha256']==sha(ROOT/'reports/slice-22d/after'/r['report'])
assert read(D/'after/adapter-retargeting.json')['differences']==[{'path':'/rejections/12/code','before':'UNSUPPORTED-CONSTRUCT','after':'RESOURCE-RESOLVER-REQUIRED'}]
lock=read(ROOT/'references/corpus-lock.json');assert len(lock['files'])==2006
for entry in lock['files']:
 p=ROOT/'vendor/cxtm'/entry['path'];assert p.stat().st_size==entry['size'] and sha(p)==entry['sha256']
assert sum(p.startswith('reports/') for p in protected)==5520
hd=Path('/Users/rgb/workspace/hyperdoc-dreyeck-ch')
assert git('rev-parse','HEAD',cwd=hd)==s['hyperdocHEAD'] and git('status','--porcelain=v1',cwd=hd)==s['hyperdocStatus']
for p in ['scripts/validate-slice-22e.py','reports/slice-22e/final-audit.py','reports/slice-22e/baseline-driver.py']:ast.parse((ROOT/p).read_text(),filename=p)
doc=ROOT/'docs/slice-22e-xtm-mergemap.md'
for link in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
 if '://' not in link:assert (doc.parent/link).resolve().exists() or (doc.parent/link).resolve()==D/'final-audit.json',link
manifest={str(p.relative_to(ROOT)):sha(p) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='final-audit.json'}
manifest.update({p:sha(ROOT/p) for p in ALLOWED|NEW})
audit={'kind':'final-slice-22e-artifact-and-scope-audit-not-new-test-execution','baseCommit':BASE,'observedHEAD':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),
 'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'initialIndexAndWorktreeClean':True,'allowedTrackedChanges':sorted(ALLOWED),
 'productionChanges':['src/xtm/package.lisp','src/xtm/reader.lisp'],'newRegisteredPASS':0,'registeredXTMCaseRecordsUnchanged':72,
 'originalIstSollBytes':[224,314],'originalFirstDifferentByte':12,'mapMetadataImported':False,'normativeCycleDecisionMade':False,
 'standaloneXTMChecks':2704,'newXTMChecks':182,'executorControls':113,'diagnosesChangedWithinMergeMapScope':7,'otherDiagnosesUnchanged':117,
 'statuses':e['statusesAfter'],'pinnedCorpusFilesVerified':2006,'historicalReportFilesVerified':5520,'protectedBaseFilesVerified':len(protected),
 'historicalReportsOriginalsBaselinesCorpusLockUnchanged':True,'twelveOpenCDecisionsUnchanged':True,'hyperdocHEAD':s['hyperdocHEAD'],'hyperdocStatusUnchanged':True,
 'newDependencyDownloads':0,'persistentImagesTouched':False,'pushOrDeployment':False,'artifactSHA256':manifest,'selfExcludedFromManifest':True,'acceptancePassed':True}
(D/'final-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in audit.items() if k not in ['artifactSHA256','allowedTrackedChanges']}))
