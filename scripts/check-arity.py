#!/usr/bin/env python3
"""Independently verify observed n-ary object references and emitted CXTM."""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'association-arity-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
original = report['original']
assert original['id'] == 'ctm/in/association-duplicate-role.ctm'
assert original['ctmSource'] == (ROOT / 'vendor/cxtm' / original['id']).read_text()
assert original['topicCount'] == 7 and original['associationCount'] == 1
baseline = ROOT / 'vendor/cxtm/ctm/baseline/association-duplicate-role.ctm.cxtm'
assert len(baseline.read_bytes()) == 1157
xml = ET.parse(baseline).getroot()
doc = original['documentIRI']
identifiers = {t.attrib['number']: [doc + l.text if l.text.startswith('#') else l.text
                                   for l in t.findall('itemIdentifiers/locator')]
               for t in xml.findall('topic')}
association = xml.find('association')
assert original['typeIdentifiers'] == identifiers[association.find('type').attrib['topicref']]
expected_roles = {(tuple(identifiers[r.find('type').attrib['topicref']]),
                   tuple(identifiers[r.find('player').attrib['topicref']]))
                  for r in association.findall('role')}
actual_roles = {(tuple(r['typeIdentifiers']), tuple(r['playerIdentifiers'])) for r in original['roles']}
assert expected_roles == actual_roles and len(original['roles']) == 3
assert all(r['parentIsAssociation'] and r['roleIsCanonical'] and r['inverseContainsRole'] for r in original['roles'])
assert len(report['witnesses']) == 12
for witness in report['witnesses']:
    xml = ET.fromstring(witness['actualCXTM'])
    assert ET.canonicalize(witness['actualCXTM']) + '\n' == witness['actualCXTM']
    topics = xml.findall('topic')
    roles = {}
    for i, a in enumerate(xml.findall('association'), 1):
        assert a.attrib['number'] == str(i)
        for j, role in enumerate(a.findall('role'), 1):
            assert role.attrib['number'] == str(j)
            roles[f'association.{i}.role.{j}'] = role.find('player').attrib['topicref']
    assert len(roles) == witness['roleCount']
    played = [(t.attrib['number'], r.attrib['ref']) for t in topics for r in t.findall('rolePlayed')]
    assert len(played) == len(roles)
    assert len({ref for _, ref in played}) == len(roles)
    assert all(roles[ref] == number for number, ref in played)
    for node in xml.iter():
        for attribute in ['topicref', 'reifier']:
            if attribute in node.attrib:
                assert 1 <= int(node.attrib[attribute]) <= len(topics)
print('ARITY-INDEPENDENT-PASS: original Topic/Role object observations; 12 canonical XML witnesses with complete Role references')
