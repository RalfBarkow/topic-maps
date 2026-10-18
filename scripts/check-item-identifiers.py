#!/usr/bin/env python3
"""Independent XML/baseline checks for hand-built TMDM models, NOT an XTM reader."""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'general-item-identifier-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
stems = ['itemid-tm', 'itemid', 'itemid-name', 'itemid-variant', 'itemid-occurrence',
         'itemid-association', 'itemid-role']
assert [c['source'] for c in report['examples']] == ['xtm2/in/' + n + '.xtm' for n in stems]
for case in report['examples']:
    assert case['contract'] == 'Manual TMDM construction; NOT XTM deserialization'
    source = ET.parse(ROOT / 'vendor/cxtm' / case['source']).getroot()
    assert source.tag == '{http://www.topicmaps.org/xtm/}topicMap'
    expected = (ROOT / 'vendor/cxtm' / case['baseline']).read_bytes()
    actual = case['actualCXTM'].encode('utf-8')
    assert actual == expected and len(actual) == case['bytes'], case['source']

root = ET.fromstring(report['orderingCXTM'])
positions = {
    'topicMap': ['itemIdentifiers', 'topic', 'association'],
    'topic': ['subjectIdentifiers', 'subjectLocators', 'itemIdentifiers', 'name', 'occurrence', 'rolePlayed'],
    'name': ['value', 'type', 'scope', 'variant', 'itemIdentifiers'],
    'variant': ['value', 'datatype', 'scope', 'itemIdentifiers'],
    'occurrence': ['value', 'datatype', 'type', 'scope', 'itemIdentifiers'],
    'association': ['type', 'role', 'scope', 'itemIdentifiers'],
    'role': ['player', 'type', 'itemIdentifiers'],
}
kinds = dict(topicMap='TOPIC-MAP', topic='TOPIC', name='TOPIC-NAME', variant='VARIANT',
             occurrence='OCCURRENCE', association='ASSOCIATION', role='ASSOCIATION-ROLE')
found = set()
topics = {t.attrib['number'] for t in root.findall('topic')}
for item in root.iter():
    if item.tag in positions:
        order = [positions[item.tag].index(c.tag) for c in item]
        assert order == sorted(order), (item.tag, order)
        ids = item.find('itemIdentifiers')
        if ids is not None:
            kind = kinds[item.tag]
            assert [l.text for l in ids] == [f'urn:{kind}:a', f'urn:{kind}:z']
            found.add(item.tag)
    if 'topicref' in item.attrib:
        assert item.attrib['topicref'] in topics
    assert 'reifier' not in item.attrib
assert found == set(positions)
print('ITEM-IDENTIFIERS-INDEPENDENT-PASS: 7 hand-built original XTM2 baseline matches; all seven II positions, locator ordering and Topic references; no XTM deserialization claim')
