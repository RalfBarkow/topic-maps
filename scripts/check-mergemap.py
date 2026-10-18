#!/usr/bin/env python3
"""Independently verify Mergemap originals, resource identities and observed TMDM."""
import collections
import json
import pathlib
import sys
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'ctm-mergemap-execution-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
assert len(report['cases']) == 4 and len(report['rejections']) == 3
expected_bytes = {'mergemap': 1511, 'mergemap-syntax-qname': 1511,
                  'mergemap-template': 1529, 'mergemap-tm-reifier': 134}
for case in report['cases']:
    name = pathlib.Path(case['id']).stem
    assert name in expected_bytes
    source = ROOT / 'vendor/cxtm' / case['id']
    assert case['ctmSource'].encode() == source.read_bytes()
    baseline = ROOT / 'vendor/cxtm/ctm/baseline' / (name + '.ctm.cxtm')
    xml = ET.fromstring(baseline.read_bytes())
    assert case['byteCount'] == expected_bytes[name] == len(baseline.read_bytes())
    model = case['model']
    assert len(xml.findall('topic')) == model['topicCount'] == len(model['topics'])
    assert len(xml.findall('association')) == model['associationCount']
    actual = collections.Counter(tuple(tuple(sorted(t[k])) for k in
                                 ('itemIdentifiers', 'subjectIdentifiers', 'subjectLocators')) for t in model['topics'])
    expected = collections.Counter(tuple(tuple(sorted(urllib.parse.urljoin(case['documentIRI'], loc.text)
                                        for loc in t.findall(k + '/locator'))) for k in
                                        ('itemIdentifiers', 'subjectIdentifiers', 'subjectLocators')) for t in xml.findall('topic'))
    assert actual == expected, name
    assert all(not t['names'] and not t['occurrences'] for t in model['topics'])
    assert len(case['requests']) == 1
    request = case['requests'][0]
    resource_name = ('mergemap.sub' if name == 'mergemap-syntax-qname' else name + '.sub')
    assert request == {'resourceIRI': urllib.parse.urljoin(case['documentIRI'], resource_name),
                       'purpose': 'MERGEMAP', 'fromDocumentIRI': case['documentIRI'],
                       'notation': 'http://psi.topicmaps.org/iso13250/ctm',
                       'sourceKey': 'ctm/in/' + resource_name}
    assert (ROOT / 'vendor/cxtm' / request['sourceKey']).is_file()
expected_negative = {'mergemap-missing-syntax-iri': ('CTM-REJECTION', 'EXPECTED-MERGEMAP-NOTATION', 0),
                     'mergemap-template': ('UNDEFINED-TEMPLATE', 'UNDEFINED-TEMPLATE', 1),
                     'mergemap-unknown-syntax': ('CTM-REJECTION', 'UNKNOWN-MERGEMAP-NOTATION', 0)}
for case in report['rejections']:
    name = pathlib.Path(case['id']).stem
    assert (case['class'], case['code'], len(case['requests'])) == expected_negative[name]
    assert case['source'] == case['id']
    text = (ROOT / 'vendor/cxtm' / case['id']).read_text()
    assert 0 <= case['position'] <= len(text)
    prefix = text[:case['position']]
    assert case['line'] == 1 + prefix.count('\n')
    assert case['column'] == len(prefix.rsplit('\n', 1)[-1]) + 1
    if name == 'mergemap-template':
        request = case['requests'][0]
        assert request['sourceKey'] == 'ctm/invalid/mergemap-template.sub'
        assert '/ctm/invalid/' in request['resourceIRI']
        assert 'def template()' in (ROOT / 'vendor/cxtm' / request['sourceKey']).read_text()
        assert text[case['position']:].startswith('template()')
print('MERGEMAP-INDEPENDENT-PASS: four unchanged byte baselines/model identities; three intended negative causes and exact resources')
