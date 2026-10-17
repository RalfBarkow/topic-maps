#!/usr/bin/env python3
"""Independent model/baseline correspondence and Variant XML ordering checks."""
import collections
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'variant-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
assert [c['id'] for c in report['cases']] == ['ctm/in/' + n + '.ctm' for n in
                                          ['variant', 'variants', 'variant-duplicate']]
properties = ['itemIdentifiers', 'subjectIdentifiers', 'subjectLocators']
for case in report['cases']:
    assert case['ctmSource'] == (root / 'vendor/cxtm' / case['id']).read_bytes().decode('utf-8')
    baseline = ET.parse(root / 'vendor/cxtm/ctm/baseline' /
                        (pathlib.Path(case['id']).name + '.cxtm')).getroot()
    def absolute(value):
        return case['documentIRI'] + value if value.startswith('#') else value
    expected_keys = {t.attrib['number']: tuple(tuple(sorted(absolute(v.text) for v in t.findall(p + '/locator')))
                                              for p in properties) for t in baseline.findall('topic')}
    actual = case['actualObjects']
    actual_keys = {str(t['ordinal']): tuple(tuple(sorted(t[p])) for p in properties) for t in actual['topics']}
    assert collections.Counter(expected_keys.values()) == collections.Counter(actual_keys.values())
    def scope(keys, refs):
        return tuple(sorted(keys[str(r)] for r in refs))
    expected = []
    for topic in baseline.findall('topic'):
        for n in topic.findall('name'):
            variants = sorted((v.findtext('value'), v.findtext('datatype'),
                               scope(expected_keys, [t.attrib['topicref'] for t in v.findall('scope/scopingTopic')]))
                              for v in n.findall('variant'))
            expected.append((expected_keys[topic.attrib['number']], n.findtext('value'),
                             expected_keys[n.find('type').attrib['topicref']],
                             scope(expected_keys, [t.attrib['topicref'] for t in n.findall('scope/scopingTopic')]),
                             tuple(variants)))
    observed = []
    for n in actual['names']:
        assert all(v['parentIsName'] and v['rawParentIsName'] for v in n['variants'])
        for v in n['variants']:
            assert len(v['scope']) == len(set(v['scope']))
            assert set(n['scope']) < set(v['scope'])
        variants = sorted((v['value'], v['datatype'], scope(actual_keys, v['scope'])) for v in n['variants'])
        observed.append((actual_keys[str(n['owner'])], n['value'], actual_keys[str(n['type'])],
                         scope(actual_keys, n['scope']), tuple(variants)))
    assert collections.Counter(expected) == collections.Counter(observed), case['id']

# Exercise each comparison key using XML independently of the Lisp comparator.
xml = ET.fromstring(report['orderingWitnessCXTM'])
keys = {t.attrib['number']: t.findtext('itemIdentifiers/locator') for t in xml.findall('topic')}
owner = next(t for t in xml.findall('topic') if t.findtext('itemIdentifiers/locator') == 'urn:owner')
variants = owner.find('name').findall('variant')
assert [v.attrib['number'] for v in variants] == ['1', '2', '3', '4', '5']
assert [(v.findtext('value'), v.findtext('datatype'),
         tuple(keys[t.attrib['topicref']] for t in v.findall('scope/scopingTopic'))) for v in variants] == [
    ('A', 'http://www.w3.org/2001/XMLSchema#string', ('urn:a',)),
    ('V', 'urn:a', ('urn:b',)),
    ('V', 'urn:b', ('urn:a',)),
    ('V', 'urn:b', ('urn:a', 'urn:b')),
    ('urn:0', 'http://www.w3.org/2001/XMLSchema#anyURI', ('urn:a',))]
for v in variants:
    assert [c.tag for c in v] == ['value', 'datatype', 'scope']
    assert v.find('type') is None
print('VARIANTS-INDEPENDENT-PASS: three original model observations; Parent identity, datatype locators, Scope sets and XML ordering')
