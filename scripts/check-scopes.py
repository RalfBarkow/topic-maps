#!/usr/bin/env python3
"""Independently compare observed Scope object relations with unchanged baselines.
Canonical byte equality is checked separately by check-cxtm.py.
"""
import collections
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'scope-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
assert [c['id'] for c in report['cases']] == ['ctm/in/' + n + '.ctm' for n in
                                          ['name-scope', 'occurrence-scope', 'association-scope']]
properties = ['itemIdentifiers', 'subjectIdentifiers', 'subjectLocators']
for case in report['cases']:
    assert case['ctmSource'] == (root / 'vendor/cxtm' / case['id']).read_bytes().decode('utf-8')
    expected = ET.parse(root / 'vendor/cxtm/ctm/baseline' /
                        (pathlib.Path(case['id']).name + '.cxtm')).getroot()
    def locator(value):
        return case['documentIRI'] + value if value.startswith('#') else value
    expected_keys = {t.attrib['number']: tuple(tuple(sorted(locator(v.text) for v in t.findall(p + '/locator')))
                                              for p in properties) for t in expected.findall('topic')}
    actual = case['actualObjects']
    actual_keys = {str(t['ordinal']): tuple(tuple(sorted(t[p])) for p in properties) for t in actual['topics']}
    assert collections.Counter(expected_keys.values()) == collections.Counter(actual_keys.values())
    expected_items = []
    for owner in expected.findall('topic'):
        for kind in ['name', 'occurrence']:
            for i in owner.findall(kind):
                expected_items.append((kind, expected_keys[owner.attrib['number']],
                  expected_keys[i.find('type').attrib['topicref']], i.find('value').text,
                  i.findtext('datatype'), frozenset(expected_keys[s.attrib['topicref']]
                                                   for s in i.findall('scope/scopingTopic')), ()))
    for i in expected.findall('association'):
        expected_items.append(('association', 'map', expected_keys[i.find('type').attrib['topicref']], None, None,
          frozenset(expected_keys[s.attrib['topicref']] for s in i.findall('scope/scopingTopic')),
          tuple(sorted((expected_keys[r.find('type').attrib['topicref']],
                        expected_keys[r.find('player').attrib['topicref']]) for r in i.findall('role')))))
    actual_items = []
    for i in actual['items']:
        scope = i['scopeTopicOrdinals']
        assert len(scope) == len(set(scope)) == 2
        assert all(r['parentIsAssociation'] for r in i['roles'])
        actual_items.append((i['kind'], 'map' if i['parent'] == 'map' else actual_keys[str(i['parent'])],
          actual_keys[str(i['typeTopicOrdinal'])], i['value'], i['datatype'],
          frozenset(actual_keys[str(s)] for s in scope),
          tuple(sorted((actual_keys[str(r['typeTopicOrdinal'])], actual_keys[str(r['playerTopicOrdinal'])])
                       for r in i['roles']))))
    assert collections.Counter(expected_items) == collections.Counter(actual_items), case['id']

# A separate construction-order witness exercises equal Value/Type/role signatures.
# Inspect XML rather than invoking Lisp's sorting/comparison functions as oracle.
xml = ET.fromstring(report['orderingWitnessCXTM'])
topics = xml.findall('topic')
keys = {int(t.attrib['number']): t.findtext('itemIdentifiers/locator') for t in topics}
assert len(keys) == 4 and set(keys.values()) == {'urn:a', 'urn:b', 'urn:owner', 'urn:type'}
owner = next(t for t in topics if t.findtext('itemIdentifiers/locator') == 'urn:owner')
def scopes(items):
    return [tuple(keys[int(s.attrib['topicref'])] for s in i.findall('scope/scopingTopic')) for i in items]
expected_scopes = [(), ('urn:a',), ('urn:b',), ('urn:a', 'urn:b')]
assert scopes(owner.findall('name')) == expected_scopes
assert scopes(owner.findall('occurrence')) == expected_scopes
assert scopes(xml.findall('association')) == expected_scopes
assert [r.attrib['ref'] for r in owner.findall('rolePlayed')] == [f'association.{i}.role.1' for i in range(1,5)]
for i in xml.iter():
    if 'topicref' in i.attrib:
        assert int(i.attrib['topicref']) in keys
    if i.tag == 'scope':
        refs = [int(s.attrib['topicref']) for s in i]
        assert refs and refs == sorted(set(refs))
print('SCOPES-INDEPENDENT-PASS: three original model observations, Topic identity categories and Scope sets; independent XML ordering/Role references')
