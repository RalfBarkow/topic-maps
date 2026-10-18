#!/usr/bin/env python3
"""Independently check the exported import-model evidence, without promoting contracts."""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'map-content-import-model-evidence'
assert report['failed'] == 0 and report['passed'] == len(report['checks']) == len(set(report['checks']))
assert len(report['witnesses']) == 2
assert len(report['rejections']) == 50
for case in report['rejections']:
    assert case['bothGraphsUnchanged'] and case['bothCXTMUnchanged']
    assert case['code'] in {'DUPLICATE-ITEM-IDENTIFIER', 'CORE-SUBJECT-CONFLICT',
                            'REIFIER-CONFLICT', 'VARIANT-SCOPE-COLLAPSE', 'SAME-MAP'}
for witness in report['witnesses']:
    assert witness['sourceUnchanged']
    xml = ET.fromstring(witness['targetCXTM'])
    topics = xml.findall('topic')
    assert len(topics) == 12
    assert len(xml.findall('association')) == 1
    assert len(xml.findall('.//name')) == len(xml.findall('.//variant')) == len(xml.findall('.//occurrence')) == 1
    assert len(xml.findall('.//role')) == 2
    # Every canonical Topic/Role reference must identify an actual output item.
    ids = {t.attrib['number'] for t in topics}
    role_ids = {f"association.{a.attrib['number']}.role.{r.attrib['number']}"
                for a in xml.findall('association') for r in a.findall('role')}
    for element in xml.findall('.//rolePlayed'):
        assert element.attrib['ref'] in role_ids
    for element in xml.iter():
        if 'topicref' in element.attrib:
            assert element.attrib['topicref'] in ids
        if 'reifier' in element.attrib:
            assert element.attrib['reifier'] in ids
    root_ids = [i.text for i in xml.findall('itemIdentifiers/locator')]
    assert root_ids == (['urn:target-map'] if witness['label'] == 'full-six-kind-transfer' else ['urn:t:map'])
    assert 'urn:source:map' not in root_ids and 'urn:s:map' not in root_ids
    assert xml.find('.//occurrence/value').text == '7'
    if 'sourceCXTM' in witness:
        source = ET.fromstring(witness['sourceCXTM'])
        assert len(source.findall('topic')) == 11
        assert source.find('itemIdentifiers/locator').text == 'urn:source:map'
print('MAP-IMPORT-REPORT-PASS: model/metadata/reference evidence only; imported contracts unchanged')
