#!/usr/bin/env python3
"""Independent UCD oracle: all canonical mappings, all Hangul, seeded CCC cases.
Invokes another fresh SBCL process; no input/output artifacts or network needed.
"""
import json
import os
import pathlib
import random
import subprocess
import unicodedata as u
# 15.0 and 15.1 have identical canonical mappings/CCC data (15.1 adds CJK).
assert u.unidata_version in ('15.0.0', '15.1.0'), 'NFC oracle requires UCD 15.0/15.1'
root = pathlib.Path(__file__).resolve().parent.parent
samples=[]
for n in range(0x110000):
    d=u.decomposition(chr(n))
    if d and not d.startswith('<'):
        samples += [[n], [int(x,16) for x in d.split()]]
for n in range(0xac00,0xd7a4):
    samples.append(list(map(ord,u.normalize('NFD',chr(n)))))
marks=[n for n in range(0x110000) if u.combining(chr(n))]
rng=random.Random(132504)
for _ in range(1000):
    samples.append([rng.choice([65,97,101,233,197]),*rng.choices(marks,k=5)])
forms = "\n".join('(format t "NFC~{ ~D~}~%" (map \'list #\'char-code (topic-maps.cxtm::nfc (map \'string #\'code-char \'(' + ' '.join(map(str,seq)) + ')))))' for seq in samples)
code='''(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:initialize-output-translations '(:output-translations (t (:root "tmp" "topic-maps-fasls")) :ignore-inherited-configuration))
(asdf:load-asd #p%s)
(asdf:load-system "topic-maps/cxtm")
(assert (not (find-package "TOPIC-MAPS.CTM")))
(assert (not (find-package "TOPIC-MAPS.TEST-FOUNDATION")))
''' % json.dumps(str(root/'topic-maps.asd')) + forms
result=subprocess.run([os.environ.get('SBCL','sbcl'),'--noinform','--no-sysinit','--no-userinit','--script','/dev/stdin'],input=code,text=True,capture_output=True)
if result.returncode:
    raise RuntimeError(result.stderr)
actual=[list(map(int,line.split()[1:])) for line in result.stdout.splitlines() if line.startswith('NFC ')]
assert len(actual)==len(samples), (len(actual),len(samples))
for index,(seq,output) in enumerate(zip(samples,actual)):
    expected=list(map(ord,u.normalize('NFC',''.join(map(chr,seq)))))
    assert expected==output, (index,seq,expected,output)
print(f'NFC-ORACLE-PASS: {len(samples)} independent Unicode {u.unidata_version} comparisons (canonical mappings, all Hangul, 1000 seeded combining sequences)')
