#!/usr/bin/env python3
"""Audit saved Slice 22F executions and final artifact scope; starts no tests."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import re
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'reports/slice-22f';A=D/'after';P=ROOT/'reports/slice-22e/after'
BASE='aeebbc7c6fdbf26642db0b7b5a358a3d04d62cca'
ALLOWED={'topic-maps.asd'}
NEW={'tests/ctm-xtm-equivalence.lisp','scripts/validate-slice-22f.py','docs/slice-22f-ctm-xtm-equivalence.md'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd,text=True).strip()
s=read(D/'initial-state.json');assert s['baseCommit']==BASE and s['initialIndexAndWorktreeClean']
assert set(s['trackedFileSHA256'])==set(git('ls-tree','-r','--name-only',BASE).splitlines())
protected={p:h for p,h in s['trackedFileSHA256'].items() if p not in ALLOWED}
assert protected=={p:sha(ROOT/p) for p in protected}
changed=set(git('diff','--name-only',BASE).splitlines());untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
assert all(p in ALLOWED|NEW or p.startswith('reports/slice-22f/') for p in changed|untracked)
assert not any(p.startswith('src/') for p in changed|untracked)
e=read(A/'execution.json');runs=read(A/'runs.json')
assert e['acceptancePassed'] and e['auditToolSHA256']==sha(ROOT/'scripts/validate-slice-22f.py')
assert len(runs['runs'])==119
assert all(x['exitCode']==x['expectedExitCode'] and x['network']==x['repositoryWrites']==x['hyperdocWrites']=='denied' and x['freshProcess'] and sha(A/(x['label']+'.log'))==x['logSHA256'] for x in runs['runs'])
assert runs['executionSourcesSHA256']=={p:sha(ROOT/p) for p in runs['executionSourcesSHA256']}
assert runs['rawReportSHA256']=={p:sha(A/p) for p in runs['rawReportSHA256']}
assert e['equivalenceChecks']==487 and e['actualReaderPairs']==27 and e['originalCorpusRegistrationsAdded']==0
assert e['retainedStandaloneXTMChecks']==2704 and e['retainedLispChecks']==12100
assert e['statusesBefore']==e['statusesAfter']=={'XTM':{'pass':72,'fail':0,'not-run':52},'CTM':{'pass':262,'fail':4,'not-run':7},'total':{'pass':334,'fail':4,'not-run':59}}
assert (A/'xtm.json').read_bytes()==(P/'xtm.json').read_bytes()
assert (A/'after-diagnostics.json').read_bytes()==(P/'after-diagnostics.json').read_bytes()
assert len(read(A/'after-diagnostics.json'))==124
faults=read(A/'failure-controls.json');assert faults['retained']==113 and faults['new']==0 and faults['allFaultReportsByteIdentical']
assert len(faults['controls'])==113
for f in faults['controls']:
 assert f['expectedASDFFailureObserved'] and f['exitCode']==1 and f['behavioralReportByteIdentical']
 p=f['label']+'.json';assert sha(A/p)==f['sha256'] and (A/p).read_bytes()==(P/p).read_bytes()
unchanged=read(A/'retained-reports.json');assert len(unchanged)==48
for f in unchanged:assert sha(A/f['report'])==f['sha256'] and (A/f['report']).read_bytes()==(P/f['report']).read_bytes()
q=read(A/'retained/xtm-mergemap.equivalence.json');summary=read(A/'equivalence-summary.json')
assert q['condition'] is None and q['originalCorpusRegistrationsAdded']==0
labels=re.findall(r'^XTM-MERGEMAP-CHECK-PASS (equivalence:.+)$',(A/'regression.log').read_text(),re.M)
assert labels==q['checks'] and len(labels)==len(set(labels))==487
pairs=[p for p in q['pairs'] if p['kind']=='direct-reader-equivalence-pair']
assert len(pairs)==len(summary['pairs'])==27
for p,sm in zip(pairs,summary['pairs']):
 assert p['id']==sm['id'] and p['ctmModel']==p['xtmModel'] and p['nativePropertiesEqual'] and p['ctmCanonicalEQ'] and p['xtmCanonicalEQ'] and not p['crossMapEQRequired']
 assert p['ctmCondition'] is p['xtmCondition'] is None and p['byteExact'] and p['firstDifferentByte'] is None
 for syntax in ['ctm','xtm']:
  data=p[syntax+'CXTM'].encode('utf-8');file=A/'actual'/(p['id']+'.'+syntax+'.cxtm')
  assert file.read_bytes()==data and len(data)==p[syntax+'Bytes'] and sha(file)==sm[syntax+'SHA256']
  assert hashlib.sha256(p[syntax+'Source'].encode('utf-8')).hexdigest()==sm['source'+syntax.upper()+'SHA256']
 assert (A/'actual'/(p['id']+'.ctm.cxtm')).read_bytes()==(A/'actual'/(p['id']+'.xtm.cxtm')).read_bytes()
 assert p['ctmTrace']['documentIRI']==p['xtmTrace']['documentIRI']==p['documentIRI']==p['canonicalBaseIRI']
 assert p['ctmTrace']['sourceKey']!=p['xtmTrace']['sourceKey']
for p in summary['contrasts']:
 a=p['ctmCXTM'].encode();b=p['xtmCXTM'].encode()
 assert p['ctmModel']!=p['xtmModel'] and len(a)==p['ctmBytes'] and len(b)==p['xtmBytes'] and a!=b
 assert next(i for i,(x,y) in enumerate(zip(a,b)) if x!=y)==p['firstDifferentByte']
assert len(summary['contrasts'])==len(summary['gaps'])==3
for p in summary['gaps']:
 assert p['ctmModel'] and p['ctmCondition'] is None and p['xtmModel'] is None and not p['successfulReaderPair']
 assert p['xtmCondition']['class']=='XTM-UNSUPPORTED' and p['xtmCondition']['code']=='unsupported-construct'
imp=pairs[-1];assert imp['id']=='content-import'
for lang in ['ctm','xtm']:
 trace=imp[lang+'Trace'];assert len(trace['resolverCalls'])==1 and len(trace['imports'])==1
 assert trace['imports'][0]=={'sourceMapItemIdentifiers':['urn:child-map'],'sourceMapReifierPresent':True,'sourceMapPreserved':True}
 assert all(x['originalResourceOctetsEQ'] for x in trace['qualifiedXMLParserCalls'] if x['documentIRI']==imp['resourceIRI'])
lock=read(ROOT/'references/corpus-lock.json');assert len(lock['files'])==2006
for f in lock['files']:
 p=ROOT/'vendor/cxtm'/f['path'];assert p.stat().st_size==f['size'] and sha(p)==f['sha256']
assert len(protected)==8109 and sum(p.startswith('reports/') for p in protected)==5826
hd=Path('/Users/rgb/workspace/hyperdoc-dreyeck-ch')
assert git('rev-parse','HEAD',cwd=hd)==s['hyperdocHEAD'] and git('status','--porcelain=v1',cwd=hd)==s['hyperdocStatus']
for p in ['scripts/validate-slice-22f.py','reports/slice-22f/final-audit.py']:ast.parse((ROOT/p).read_text(),filename=p)
# Literal whitespace is immutable output evidence, not source formatting.
ws=subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,text=True,capture_output=True)
expected='reports/slice-22f/after/actual/unicode-whitespace-escaping.ctm.cxtm:7: trailing whitespace.\n+<value> 馬🦊 &amp; &lt; &gt; \nreports/slice-22f/after/actual/unicode-whitespace-escaping.ctm.cxtm:8: space before tab in indent.\n+ \t " \\ </value>\nreports/slice-22f/after/actual/unicode-whitespace-escaping.xtm.cxtm:7: trailing whitespace.\n+<value> 馬🦊 &amp; &lt; &gt; \nreports/slice-22f/after/actual/unicode-whitespace-escaping.xtm.cxtm:8: space before tab in indent.\n+ \t " \\ </value>\n'
assert ws.returncode==2 and ws.stdout==expected and not ws.stderr
clean=subprocess.run(['git','diff','--cached','--check','--','.',
 ':(exclude)reports/slice-22f/after/actual/unicode-whitespace-escaping.ctm.cxtm',
 ':(exclude)reports/slice-22f/after/actual/unicode-whitespace-escaping.xtm.cxtm'],cwd=ROOT,text=True,capture_output=True)
assert clean.returncode==0 and not clean.stdout and not clean.stderr
whitespace={'kind':'literal-whitespace-evidence-not-formatting-change','actualGitCheckExitCode':ws.returncode,'actualMessages':ws.stdout,
 'scope':'Exactly four findings in two byte-identical actual CXTM outputs. Spaces and tab belong to the native Unicode Name value.',
 'actualBytesPreserved':True,'allOtherStagedFilesWhitespaceCheckPassed':True}
(D/'whitespace-check.json').write_text(json.dumps(whitespace,indent=2,ensure_ascii=False)+'\n')
doc=ROOT/'docs/slice-22f-ctm-xtm-equivalence.md'
for link in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
 if '://' not in link:assert (doc.parent/link).resolve().exists() or (doc.parent/link).resolve()==D/'final-audit.json',link
manifest={str(p.relative_to(ROOT)):sha(p) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='final-audit.json'}
manifest.update({p:sha(ROOT/p) for p in ALLOWED|NEW})
audit={'kind':'final-slice-22f-artifact-and-scope-audit-not-new-test-execution','baseCommit':BASE,'observedHEAD':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),
 'auditedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'initialIndexAndWorktreeClean':True,'allowedTrackedChanges':sorted(ALLOWED),
 'productionChanges':[],'newRegisteredPASS':0,'actualReaderPairs':27,'equivalenceChecks':487,'fullByteExactPairs':27,'intraMapCanonicalEQBothReaders':True,
 'intentionalSemanticDifferences':3,'documentedReaderCapabilityGaps':3,'standaloneXTMChecks':2704,'retainedCoreChecks':12100,
 'executorControls':113,'unchangedOriginalDiagnoses':124,'statuses':e['statusesAfter'],'pinnedCorpusFilesVerified':2006,'historicalReportFilesVerified':5826,
 'protectedBaseFilesVerified':len(protected),'historicalReportsOriginalsBaselinesCorpusLockUnchanged':True,'openSlice22CDecisionsUnchanged':True,
 'hyperdocHEAD':s['hyperdocHEAD'],'hyperdocStatusUnchanged':True,'newDependencyDownloads':0,'persistentImagesTouched':False,'pushOrDeployment':False,
 'artifactSHA256':manifest,'selfExcludedFromManifest':True,'acceptancePassed':True}
(D/'final-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in audit.items() if k not in ['artifactSHA256','allowedTrackedChanges']}))
