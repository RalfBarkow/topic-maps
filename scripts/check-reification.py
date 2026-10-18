#!/usr/bin/env python3
"""Independent pinned-source/baseline comparison of observed Reifier references."""
import collections
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'reification-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
names = ['tm-reifier', 'tm-reifier2', 'tm-reifier3', 'name-reifier', 'variant-reifier',
         'occurrence-reifier', 'occurrence-reifier-nested', 'occurrence-reifier-nested-nested',
         'association-reifier', 'role-reifier', 'role-duplicate-reified-qnames']
assert [c['id'] for c in report['cases']] == ['ctm/in/' + n + '.ctm' for n in names]
properties = ['itemIdentifiers', 'subjectIdentifiers', 'subjectLocators']
kind = dict(topicMap='topic-map', name='topic-name', variant='variant', occurrence='occurrence',
            association='association', role='association-role')
for case in report['cases']:
    assert case['ctmSource'] == (ROOT / 'vendor/cxtm' / case['id']).read_bytes().decode('utf-8')
    doc = case['documentIRI']
    base = ET.parse(ROOT / 'vendor/cxtm/ctm/baseline' / (pathlib.Path(case['id']).name + '.cxtm')).getroot()
    def absolute(s):
        return doc + s if s.startswith('#') else s
    expected_keys = {t.attrib['number']: tuple(tuple(sorted(absolute(l.text) for l in t.findall(p + '/locator')))
                                              for p in properties) for t in base.findall('topic')}
    observed_keys = {str(t['ordinal']): tuple(tuple(sorted(t[p])) for p in properties) for t in case['model']['topics']}
    assert collections.Counter(expected_keys.values()) == collections.Counter(observed_keys.values())
    expected = collections.Counter((kind[i.tag], i.findtext('value'), expected_keys[i.attrib['reifier']])
                                   for i in base.iter() if 'reifier' in i.attrib)
    observed = collections.Counter((r['kind'], r['value'], observed_keys[str(r['reifierTopic'])])
                                   for r in case['reifications'])
    assert expected == observed, case['id']
    assert all(r['inverseIsItem'] and r['itemIsCanonical'] and r['reifierIsCanonical'] for r in case['reifications'])
negative = [('reifier-collision', 'reifier-conflict'), ('tm-reifier-not-ontop', 'topic-map-reifier-position')]
assert [c['id'] for c in report['negativeCases']] == ['ctm/invalid/' + n + '.ctm' for n, _ in negative]
for case, (name, code) in zip(report['negativeCases'], negative):
    source = (ROOT / 'vendor/cxtm' / case['id']).read_text()
    pos = source.rfind('~')
    assert case['code'] == code and case['position'] == pos
    assert case['line'] == source[:pos].count('\n') + 1
    assert case['column'] == pos - source.rfind('\n', 0, pos)
print('REIFICATION-INDEPENDENT-PASS: 11 original model observations, canonical Topic identity and bidirectional Reifier references; 2 specific rejection reasons/positions')
