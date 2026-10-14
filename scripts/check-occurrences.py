#!/usr/bin/env python3
"""Independent semantic expectations, separate from raw CXTM equality checks."""
import json
import pathlib
import sys
report=json.loads(pathlib.Path(sys.argv[1]).read_text())
root=pathlib.Path(__file__).resolve().parent.parent
assert report['kind']=='occurrence-semantic-and-cxtm-evidence' and report['failed']==0
assert report['passed']==len(report['checks'])==len(set(report['checks']))
assert len(report['cases'])==4
prefix='https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/'
for case in report['cases']:
    ident=case['id']; doc=case['documentIRI']; m=case['actualObjects']
    assert doc==prefix+ident
    assert case['ctmSource'].encode('utf-8')==(root/'vendor/cxtm'/ident).read_bytes()
    two=ident.endswith('/occurrence-two.ctm'); uri=ident.endswith('/occurrence-uri-relative.ctm')
    identifiers=['tmcl-schema','description','see-also'] if two else ['topic','occtype']
    assert m['topicCount']==len(identifiers) and m['occurrenceCount']==(2 if two else 1)
    assert m['nameCount']==m['associationCount']==0
    for index,(t,local) in enumerate(zip(m['topics'],identifiers),1):
        assert t['ordinal']==index and t['itemIdentifiers']==[doc+'#'+local]
        assert t['subjectIdentifiers']==t['subjectLocators']==[]
        if index!=1: assert t['occurrences']==[]
    values=['A meta-schema for TMCL, describing the allowed structure\n                    of TMCL schemas.',
            'http://www.isotopicmaps.org/tmcl/tmcl.html'] if two else [prefix+'ctm/in/file.html' if uri else 'Occurrence']
    for index,(o,value) in enumerate(zip(m['topics'][0]['occurrences'],values),1):
        kind='anyURI' if uri or (two and index==2) else 'string'
        assert o=={'value':value,'datatype':'http://www.w3.org/2001/XMLSchema#'+kind,
                   'parentTopicOrdinal':1,'typeTopicOrdinal':index+1,'itemIdentifiers':[]}
    assert case['status']=='pass'
print('OCCURRENCE-INDEPENDENT-PASS: four original sources, actual parents/types, lexical values, datatype locators, no extra items')
