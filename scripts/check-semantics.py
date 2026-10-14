#!/usr/bin/env python3
"""Read frozen CXTM baselines as evidence for selected semantic properties.
No XML is generated, serialized, canonicalized or compared byte-for-byte here.
"""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET
root = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'semantic-observations-not-cxtm'
assert report['failed'] == 0 and report['passed'] == len(report['checks'])
assert len(set(report['checks'])) == len(report['checks'])
assert [c['id'] for c in report['cases']] == ['ctm/in/'+n+'.ctm' for n in
       ['simple','subject-identifier','subject-locator','item-identifier','name']]
for case in report['cases']:
    assert case['status'] == 'pass'
    assert case['ctmSource'] == (root/'vendor/cxtm'/case['id']).read_bytes().decode('utf-8')
    baseline = root/'vendor/cxtm/ctm/baseline'/(pathlib.Path(case['id']).name+'.cxtm')
    xml = ET.parse(baseline).getroot()
    assert xml.tag == 'topicMap'
    xml_topics = xml.findall('topic')
    actual = case['actualObjects']
    assert actual['topicCount'] == len(xml_topics)
    assert actual['nameCount'] == sum(len(t.findall('name')) for t in xml_topics)
    for topic, expected in zip(actual['topics'], xml_topics):
        assert topic['ordinal'] == int(expected.attrib['number']) and topic['parentIsMap'] is True
        assert all(child.tag in ['itemIdentifiers','subjectIdentifiers','subjectLocators','name'] for child in expected)
        for property_name in ['itemIdentifiers','subjectIdentifiers','subjectLocators']:
            values = [locator.text for locator in expected.findall(property_name+'/locator')]
            # Only a Document-IRI-relative fragment is interpreted here. This
            # illustrates the selected baselines; it is not a CXTM resolver.
            values = [case['documentIRI']+v if v.startswith('#') else v for v in values]
            assert topic[property_name] == values, (case['id'], property_name)
        assert len(topic['names']) == len(expected.findall('name'))
        for name, expected_name in zip(topic['names'], expected.findall('name')):
            assert name['value'] == expected_name.find('value').text
            assert name['typeTopicOrdinal'] == int(expected_name.find('type').attrib['topicref'])
            assert name['parentTopicOrdinal'] == topic['ordinal']
print('BASELINE-SEMANTIC-EVIDENCE-PASS: five frozen baselines support the selected properties; no canonicalization claimed')
