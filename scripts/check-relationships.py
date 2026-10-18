#!/usr/bin/env python3
"""Compare actual TMDM reference graphs to the untouched original CXTM graphs."""
import collections
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'type-relationship-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
prefix = 'http://psi.topicmaps.org/iso13250/model/'
core = ['type-instance', 'type', 'instance', 'supertype-subtype', 'supertype', 'subtype', 'sort', 'name-type']
assert report['coreSubjectIdentifiers'] == [prefix + name for name in core]
names = ['isa-relationship', 'isa-relationship-duplicate', 'isa-relationship-duplicate2',
         'isa-relationship-embedded', 'isa-relationship-type-qname', 'ako-relationship',
         'ako-relationship-duplicate', 'ako-relationship-duplicate2', 'ako-relationship-embedded',
         'ako-relationship-supertype-qname', 'ako-merge-away', 'subject-identifier-topicref', 'item-identifier-topicref']
assert [c['id'] for c in report['cases']] == ['ctm/in/' + name + '.ctm' for name in names]
properties = ['itemIdentifiers', 'subjectIdentifiers', 'subjectLocators']
for case in report['cases']:
    assert case['ctmSource'] == (ROOT / 'vendor/cxtm' / case['id']).read_text()
    baseline = ET.parse(ROOT / 'vendor/cxtm/ctm/baseline' / (pathlib.Path(case['id']).name + '.cxtm')).getroot()
    def absolute(s):
        return case['documentIRI'] + s if s.startswith('#') else s
    expected_keys = {t.attrib['number']: tuple(tuple(sorted(absolute(l.text) for l in t.findall(p + '/locator')))
                                              for p in properties) for t in baseline.findall('topic')}
    observed_keys = {t['ordinal']: tuple(tuple(sorted(t[p])) for p in properties) for t in case['model']['topics']}
    assert collections.Counter(expected_keys.values()) == collections.Counter(observed_keys.values()), case['id']
    expected = collections.Counter((expected_keys[a.find('type').attrib['topicref']],
                                    frozenset(expected_keys[s.attrib['topicref']] for s in a.findall('scope/scopingTopic')),
                                    frozenset((expected_keys[r.find('type').attrib['topicref']],
                                               expected_keys[r.find('player').attrib['topicref']]) for r in a.findall('role')))
                                   for a in baseline.findall('association'))
    observed = collections.Counter((observed_keys[a['type']], frozenset(observed_keys[t] for t in a['scope']),
                                    frozenset((observed_keys[r['type']], observed_keys[r['player']]) for r in a['roles']))
                                   for a in case['model']['associations'])
    assert expected == observed, case['id']
    for a in case['model']['associations']:
        assert a['parentIsMap'] and len(a['roles']) == 2 and len({r['type'] for r in a['roles']}) == 2
        assert all(r['parentIsAssociation'] and r['roleIsCanonical'] and r['inverseContainsRole'] for r in a['roles'])
        expected_vocabulary = ('supertype-subtype', 'subtype', 'supertype') if '/ako-' in case['id'] else ('type-instance', 'instance', 'type')
        assert observed_keys[a['type']][1] == (prefix + expected_vocabulary[0],)
        assert {observed_keys[r['type']][1] for r in a['roles']} == {(prefix + v,) for v in expected_vocabulary[1:]}
labels = [r['label'] for r in report['rejections']]
assert len(labels) == len(set(labels))
expected_pairs = {f'core:{i}:{j}:{route}' for i in range(1, 9) for j in range(1, 9) if i != j
                  for route in ['EXPLICIT', 'SUBJECT', 'ITEM', 'LOCATOR', 'INTERN']}
assert {label for label in labels if label.startswith('core:')} == expected_pairs
assert all(r['code'] == 'core-subject-conflict' and r['unchanged'] and 'TMDM 7.1' in r['detail'] for r in report['rejections'])
assert {'reifier:four-level-cascade:EXPLICIT', 'reifier:four-level-cascade:SUBJECT',
        'chain:normalize-entire-transitive-closure', 'intern:no-dangling-new-topic-after-late-conflict'} <= set(labels)
print(f'RELATIONSHIPS-INDEPENDENT-PASS: 13 original TMDM reference graphs; eight exact Core Subject locators; {len(labels)} atomic conflict observations')
