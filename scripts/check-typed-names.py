#!/usr/bin/env python3
"""Independent model-property checks against the four unchanged Name baselines.
The separate check-cxtm.py checks canonical bytes; these checks compare objects.
"""
import collections
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'typed-name-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
assert [c['id'] for c in report['cases']] == ['ctm/in/' + n + '.ctm' for n in
                                          ['name', 'name2', 'name-type', 'name-duplicate']]
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
    assert actual['topicCount'] == len(expected_keys) == 2 and actual['nameCount'] == 1
    expected_names = collections.Counter((n.find('value').text, expected_keys[t.attrib['number']],
                                         expected_keys[n.find('type').attrib['topicref']])
                                        for t in expected.findall('topic') for n in t.findall('name'))
    actual_names = collections.Counter((n['value'], actual_keys[str(n['parentTopicOrdinal'])],
                                       actual_keys[str(n['typeTopicOrdinal'])])
                                      for t in actual['topics'] for n in t['names'])
    assert expected_names == actual_names, case['id']
    assert all(t['parentIsMap'] for t in actual['topics'])
print('TYPED-NAMES-INDEPENDENT-PASS: four original sources, exact identifier sets and Name value/Parent/Type relations')
