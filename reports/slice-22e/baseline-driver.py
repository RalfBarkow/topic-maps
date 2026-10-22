from pathlib import Path
import importlib.util,subprocess,json,os,hashlib
root=Path('/Users/rgb/workspace/topic-maps');out=Path(__file__).parent;baseline=out/'baseline';baseline.mkdir()
spec=importlib.util.spec_from_file_location('v',root/'scripts/validate-slice-22d.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
pins=v.prepare_pinned(str(out/'sources'));(out/'source-preparation.json').write_text(json.dumps(pins,indent=2)+'\n')
env={k:x for k,x in os.environ.items() if not k.startswith('TOPIC_MAPS_')};env.update(CL_SOURCE_REGISTRY=pins['sourceRegistry'],TOPIC_MAPS_XTM_REPORT=str(baseline/'xtm.json'),TOPIC_MAPS_21O_ROOT=str(root),TOPIC_MAPS_21O_DIAGNOSTICS=str(baseline/'diagnostics.json'),TOPIC_MAPS_21O_EXTRA=str(baseline/'extra.json'),PYTHONDONTWRITEBYTECODE='1')
runs=[];prefix=['/usr/bin/sandbox-exec','-p',v.POLICY,v.RUNTIME,'--noinform','--no-sysinit','--no-userinit','--script']
for label,path in [('xtm','scripts/fresh-xtm.lisp'),('diagnostics','reports/slice-21o/diagnostics.lisp')]:
 r=subprocess.run(prefix+[path],cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(baseline/(label+'.log')).write_bytes(r.stdout);assert r.returncode==0,(label,r.stdout[-3000:]);runs.append({'label':label,'command':prefix+[path],'exitCode':r.returncode})
previous=json.loads((root/'reports/slice-22d/after/xtm.json').read_text());current=json.loads((baseline/'xtm.json').read_text());assert current==previous
assert json.loads((baseline/'diagnostics.json').read_text())==json.loads((root/'reports/slice-22d/after/after-diagnostics.json').read_text())
assert current['statuses']['pass']==72 and len(current['checks'])==2522
manifest=json.loads((root/'reports/slice-22d/final-audit.json').read_text())['artifactSHA256']
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in manifest.items())
(baseline/'execution.json').write_text(json.dumps({'kind':'slice-22e-fresh-targeted-baseline-with-verified-full-22d-provenance','runs':runs,'xtmChecks':2522,'xtmPASS':72,'diagnoses':124,'freshReportsEqualAccepted22D':True,'fullPreviousRegression':'reports/slice-22d/after/execution.json','previousExecutionSourcesAndArtifactsVerified':len(manifest),'productionChanged':False},indent=2)+'\n')
print('Fresh before: 2522 XTM checks, 72 PASS; all 124 diagnoses identical to accepted 22D; full previous artifact manifest verified.')
