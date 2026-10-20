import os, sys, json, hashlib, tempfile, subprocess, datetime, importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
root=Path('/Users/rgb/workspace/topic-maps'); t=Path(tempfile.mkdtemp(prefix='xtm-slice-21o-',dir='/private/tmp'))
Path('/private/tmp/xtm-slice-21o-latest').write_text(str(t))
spec=importlib.util.spec_from_file_location('v',root/'scripts/validate-slice-21n.py'); v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tracked=subprocess.check_output(['git','ls-files'],cwd=root,text=True).splitlines(); save(t/'initial-hashes.json',{p:sha(root/p) for p in tracked})
candidates=[]
for stem in ['variant-reifier','variant-duplicate-reifier','variant-duplicate-reifier2']:
 p=root/f'vendor/cxtm/xtm2/in/{stem}.xtm'; b=root/f'vendor/cxtm/xtm2/baseline/{stem}.xtm.cxtm'
 import xml.etree.ElementTree as ET
 e=ET.fromstring(p.read_bytes()); ns={'x':'http://www.topicmaps.org/xtm/'}
 candidates.append(dict(id='xtm2/in/'+p.name,sourceBytes=p.stat().st_size,sourceSHA256=sha(p),sourceHex=p.read_bytes().hex(),sourceText=p.read_text(),baselineBytes=b.stat().st_size,baselineSHA256=sha(b),baselineText=b.read_text(),sourceNames=len(e.findall('.//x:name',ns)),sourceVariants=len(e.findall('.//x:variant',ns)),documentIRI='https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/'+p.name,register=stem!='variant-duplicate-reifier2'))
save(t/'candidate-inventory.json',dict(candidates=candidates)); print(json.dumps(candidates,indent=2),flush=True)
policy='(version 1)(allow default)(deny network*)(deny file-write* (subpath "'+str(root)+'"))'
env={k:x for k,x in os.environ.items() if not k.startswith('TOPIC_MAPS_')};runtime='/nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl';env.update(PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0',SBCL=runtime)
runs=[]
def run(label,args,env):
 cmd=['/usr/bin/sandbox-exec','-p',policy]+args; start=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(cmd,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300);(t/(label+'.log')).write_bytes(r.stdout);runs.append(dict(label=label,command=cmd,startedAtUTC=start,finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),exitCode=r.returncode,network='denied',repositoryWrites='denied',freshProcess=True));save(t/'baseline-execution.json',dict(runs=runs,acceptancePassed=False)); assert r.returncode==0,(label,r.stdout.decode()[-4000:]);print(label+' PASS',flush=True);return r.stdout.decode()
prov=json.loads(run('source-preparation',['python3',str(root/'scripts/validate-slice-21n.py'),'--prepare',str(t/'sources')],env));save(t/'source-preparation.json',prov);env['CL_SOURCE_REGISTRY']=prov['sourceRegistry'];save(t/'environment.json',env)
prefix=[runtime,'--noinform','--no-sysinit','--no-userinit','--script']
diag=(root/'reports/slice-21n/diagnostics.lisp').read_text().replace('TOPIC_MAPS_21N','TOPIC_MAPS_21O').replace('(negative-condition-data c)','(map-reifier-condition-data c)');(t/'diagnostics.lisp').write_text(diag)
run('baseline-xtm-diagnostics',prefix+[str(t/'diagnostics.lisp')],dict(env,TOPIC_MAPS_21O_ROOT=str(root),TOPIC_MAPS_21O_BASELINE=str(t/'baseline-xtm.json'),TOPIC_MAPS_21O_DIAGNOSTICS=str(t/'before-diagnostics.json')))
assert json.loads((t/'baseline-xtm.json').read_text())==json.loads((root/'reports/slice-21n/xtm.json').read_text())
assert json.loads((t/'before-diagnostics.json').read_text())==json.loads((root/'reports/slice-21n/after-diagnostics.json').read_text())
ret=t/'baseline-retained';ret.mkdir()
env.update(TOPIC_MAPS_REPORT=str(ret/'core.json'),TOPIC_MAPS_XTM_REPORT=str(t/'baseline-full-xtm.json'),TOPIC_MAPS_XTM_MERGEMAP_REPORT=str(ret/'xtm-mergemap'),TOPIC_MAPS_REGISTERED_ORIGINALS_REPORT=str(ret/'slice20a'),TOPIC_MAPS_REGISTERED_NEGATIVES_REPORT=str(ret/'slice20b'),TOPIC_MAPS_PROLOG_REPORT=str(ret/'slice20c'),TOPIC_MAPS_EMPTY2_REPORT=str(ret/'slice20e'),TOPIC_MAPS_CTM_INTEGER_REPORT=str(ret/'slice20f'),TOPIC_MAPS_TRIPLE_REPORT=str(ret/'slice20g'),TOPIC_MAPS_ENCODING_REPORT=str(t/'baseline-ctm'))
run('baseline-regression',[str(root/'scripts/test.sh')],env)
for p in (root/'reports/slice-21n/retained').glob('*.json'): assert json.loads(p.read_text())==json.loads((ret/p.name).read_text()),p
assert json.loads((t/'baseline-ctm.validation.json').read_text())['statuses']=={'pass':262,'fail':4,'unsupported':0,'not-run':7}
# Use only native TMDM operations before any Reader edit.
api='''(require :asdf)
(assert (string= "2.5.4" (lisp-implementation-version)))
(setf *compile-verbose* nil *load-verbose* nil)
(asdf:load-asd #P"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/xtm/tests")
(in-package :topic-maps.xtm.tests)
(dolist (both '(nil t))
 (let* ((map (make-topic-map)) (p (intern-topic map :item-identifier "urn:p")) (q (intern-topic map :item-identifier "urn:q"))
        (s (intern-topic map :item-identifier "urn:scope")) (n (add-default-name p "N")) (m (add-default-name q "N"))
        (a (add-variant n "V" :scope (list s))) (b (add-variant m "V" :scope (list s)))
        (r (intern-topic map :item-identifier "urn:r")) (u (intern-topic map :item-identifier "urn:u")))
  (assert (eq a (canonical-variant a))) (assert (eq a (set-item-reifier a r)))
  (assert (eq r (item-reifier a))) (assert (eq a (topic-reified r)))
  (assert (eq a (add-variant n "V" :scope (list s))))
  (add-item-identifier a "urn:a") (add-item-identifier b "urn:b")
  (when both (set-item-reifier b u))
  (merge-topics p q)
  (let ((current (canonical-variant a)))
   (assert (eq current (canonical-variant b))) (assert (not (eq current a)))
   (assert (eq (canonical-topic-name n) (variant-parent current)))
   (assert (eq (canonical-topic-name n) (canonical-topic-name m)))
   (assert (same-identifiers-p '("urn:a" "urn:b") (item-identifiers current)))
   (assert (eq (canonical-topic r) (item-reifier current))) (assert (eq current (topic-reified r)))
   (when both (assert (eq (canonical-topic r) (canonical-topic u))) (assert (eq current (topic-reified u))))
   (assert (topic-maps.tmdm::validate-map-reification map))
   (format t "VARIANT-REIFIER-API-NORMALIZATION: ~A existing Reifier(s), identifiers and old handles preserved~%" (if both 2 1)))))
(let* ((map (make-topic-map)) (p (intern-topic map :item-identifier "urn:p")) (s (intern-topic map :item-identifier "urn:s"))
       (n (add-default-name p "N")) (a (add-variant n "A" :scope (list s))) (b (add-variant n "B" :scope (list s)))
       (r (intern-topic map :item-identifier "urn:r")) (u (intern-topic map :item-identifier "urn:u")))
 (set-item-reifier a r) (set-item-reifier b u)
 (dolist (operation (list (lambda () (set-item-reifier b r)) (lambda () (merge-topics r u))))
  (let* ((before (map-reifier-state map)) (c (condition-from operation)))
   (assert (eq 'reification-error (type-of c))) (assert (eq :reifier-conflict (reification-error-code c)))
   (assert (equal before (map-reifier-state map)))
   (format t "VARIANT-REIFIER-API-CONDITION: ~A ~A; atomic~%" (type-of c) (reification-error-code c))))
 (add-item-identifier a "urn:variant")
 (let* ((before (map-reifier-state map)) (c (condition-from (lambda () (intern-topic map :item-identifier "urn:variant")))))
  (assert (typep c 'item-identifier-error)) (assert (eq :duplicate-item-identifier (item-identifier-error-code c)))
  (assert (equal before (map-reifier-state map)))
  (format t "VARIANT-REIFIER-API-CONDITION: ~A ~A; atomic~%" (type-of c) (item-identifier-error-code c))))
(format t "VARIANT-REIFIER-API-PREFLIGHT-PASS: normalize, assign II, resolve Reifier by II, set on current Variant, retain canonical result~%")
'''
(t/'api-preflight.lisp').write_text(api)
run('variant-reifier-api-preflight',prefix+[str(t/'api-preflight.lisp')],env)
assert all(sha(root/p)==h for p,h in json.loads((t/'initial-hashes.json').read_text()).items())
save(t/'baseline-execution.json',dict(runs=runs,acceptancePassed=True,readerAndAllTrackedFilesUnchanged=True,baselineXTM={'pass':68,'fail':0,'not-run':56},baselineCTM={'pass':262,'fail':4,'not-run':7}))
print('BASELINE AND PREFLIGHT ACCEPTED '+str(t),flush=True)
