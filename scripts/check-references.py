#!/usr/bin/env python3
"""Check observed TMDM graphs against original baselines, independent of Lisp/CXTM code."""
import collections
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'topic-reference-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
expected_counters = dict(zip([
    'wildcard', 'wildcard-named', 'wildcard-named2', 'wildcard-named-merge',
    'association-scope-embedded', 'association-scope-embedded2',
    'association-type-embedded', 'association-type-embedded-merge',
    'embedded-semicolon', 'name-scope-embedded', 'name-scope-embedded2', 'name-type-embedded', 'nested-twice',
    'occurrence-scope-embedded', 'occurrence-scope-embedded2', 'occurrence-type-embedded',
    'role-player-embedded', 'role-type-embedded', 'subject-identifier-embedded',
    'variant-scope-embedded', 'variant-scope-embedded2'],
    [1, 1, 3, 1, 2, 3, 1, 2, 1, 2, 3, 1, 2, 2, 3, 1, 1, 1, 1, 3, 4]))
assert [c['id'] for c in report['cases']] == ['ctm/in/' + n + '.ctm' for n in expected_counters]
properties = ['itemIdentifiers', 'subjectIdentifiers', 'subjectLocators']
for case in report['cases']:
    name = pathlib.Path(case['id']).stem
    assert case['ctmSource'] == (root / 'vendor/cxtm' / case['id']).read_bytes().decode('utf-8')
    assert case['documentIRI'] == case['wildcardIRI']
    assert case['finalCounter'] == expected_counters[name]
    baseline = ET.parse(root / 'vendor/cxtm/ctm/baseline' / (name + '.ctm.cxtm')).getroot()
    def absolute(value):
        return case['documentIRI'] + value if value.startswith('#') else value
    expected_keys = {t.attrib['number']: tuple(tuple(sorted(absolute(v.text) for v in t.findall(p + '/locator')))
                                              for p in properties) for t in baseline.findall('topic')}
    def topic_keys(snapshot):
        return {str(t['ordinal']): tuple(tuple(sorted(t[p])) for p in properties) for t in snapshot['topics']}
    actual = case['scopedObjects']
    actual_keys = topic_keys(actual)
    assert actual_keys == topic_keys(case['nameObjects'])
    assert collections.Counter(expected_keys.values()) == collections.Counter(actual_keys.values()), name
    def scope(keys, refs):
        assert len(refs) == len(set(refs))
        return tuple(sorted(keys[str(r)] for r in refs))
    def xml_scope(item):
        return scope(expected_keys, [t.attrib['topicref'] for t in item.findall('scope/scopingTopic')])
    expected_items = []
    expected_names = []
    for owner in baseline.findall('topic'):
        for kind in ['name', 'occurrence']:
            for i in owner.findall(kind):
                key = expected_keys[owner.attrib['number']]
                item_type = expected_keys[i.find('type').attrib['topicref']]
                expected_items.append((kind, key, item_type, i.findtext('value'), i.findtext('datatype'), xml_scope(i), ()))
                if kind == 'name':
                    expected_names.append((key, i.findtext('value'), item_type, xml_scope(i), tuple(sorted(
                        (v.findtext('value'), v.findtext('datatype'), xml_scope(v)) for v in i.findall('variant')))))
    for i in baseline.findall('association'):
        roles = tuple(sorted((expected_keys[r.find('type').attrib['topicref']], expected_keys[r.find('player').attrib['topicref']])
                             for r in i.findall('role')))
        expected_items.append(('association', 'map', expected_keys[i.find('type').attrib['topicref']], None, None, xml_scope(i), roles))
    observed = []
    for i in actual['items']:
        assert all(r['parentIsAssociation'] for r in i['roles'])
        observed.append((i['kind'], 'map' if i['parent'] == 'map' else actual_keys[str(i['parent'])],
                         actual_keys[str(i['typeTopicOrdinal'])], i['value'], i['datatype'],
                         scope(actual_keys, i['scopeTopicOrdinals']), tuple(sorted(
                             (actual_keys[str(r['typeTopicOrdinal'])], actual_keys[str(r['playerTopicOrdinal'])]) for r in i['roles']))))
    assert collections.Counter(expected_items) == collections.Counter(observed), name
    observed_names = []
    for n in case['nameObjects']['names']:
        for v in n['variants']:
            assert v['parentIsName'] and v['rawParentIsName']
            assert set(n['scope']) < set(v['scope'])
        observed_names.append((actual_keys[str(n['owner'])], n['value'], actual_keys[str(n['type'])],
                               scope(actual_keys, n['scope']), tuple(sorted(
                                   (v['value'], v['datatype'], scope(actual_keys, v['scope'])) for v in n['variants']))))
    assert collections.Counter(expected_names) == collections.Counter(observed_names), name
    generated = [iri for key in actual_keys.values() for iri in key[0] if iri.startswith(case['wildcardIRI'] + '#$__')]
    assert len(generated) == len(set(generated)) == case['finalCounter']
    numbers = [int(re.fullmatch(re.escape(case['wildcardIRI']) + r'#\$__(\d+)(?:\..+)?', iri).group(1)) for iri in generated]
    assert sorted(numbers) == list(range(1, case['finalCounter'] + 1)), name

print('REFERENCES-INDEPENDENT-PASS: 21 original model graphs; identity categories, generated locators/counters, Parent/Type/Player/Scope/Variant relations')
