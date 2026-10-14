#!/usr/bin/env python3
"""Compare selected model properties with frozen baselines, never canonical XML.

Match topics by identifier sets, not observation order or CXTM numbering.
This bounded semantic oracle does not implement ISO 13250-4 canonicalization.
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
expected_ids = {'ctm/in/'+name+'.ctm' for name in [
    'topic-subject-identifier', 'topic-subject-identifier-wrapped',
    'topic-subject-identifier-duplicate', 'topic-subject-locator',
    'topic-subject-locator-wrapped', 'topic-subject-locator-semi',
    'topic-subject-locator-duplicate', 'topic-item-identifier',
    'topic-item-identifier-wrapped', 'topic-item-identifier-duplicate', 'name-duplicate']}
assert len(report['cases']) == len(expected_ids)
assert {case['id'] for case in report['cases']} == expected_ids
for case in report['cases']:
    baseline = root/'vendor/cxtm/ctm/baseline'/(pathlib.Path(case['id']).name+'.cxtm')
    xml = ET.parse(baseline).getroot()
    actual = case['actualObjects']
    expected_topics = xml.findall('topic')
    assert xml.tag == 'topicMap'
    assert actual['topicCount'] == len(expected_topics)
    assert actual['nameCount'] == sum(len(t.findall('name')) for t in expected_topics)

    def key(topic, xml_item=False):
        values = []
        for prop in ['itemIdentifiers', 'subjectIdentifiers', 'subjectLocators']:
            locators = ([e.text for e in topic.findall(prop+'/locator')]
                        if xml_item else topic[prop])
            locators = [case['documentIRI']+v if v.startswith('#') else v for v in locators]
            assert len(locators) == len(set(locators))
            values.append(tuple(sorted(locators)))
        return tuple(values)

    by_identity = {key(t): t for t in actual['topics']}
    assert len(by_identity) == actual['topicCount']
    mapping = {}
    for expected in expected_topics:
        observed = by_identity[key(expected, True)]
        assert observed['parentIsMap'] is True
        assert all(c.tag in ['itemIdentifiers', 'subjectIdentifiers', 'subjectLocators', 'name'] for c in expected)
        mapping[int(expected.attrib['number'])] = observed['ordinal']
    for expected in expected_topics:
        observed = by_identity[key(expected, True)]
        names = [(n['value'], n['typeTopicOrdinal'], n['parentTopicOrdinal']) for n in observed['names']]
        expected_names = [(n.find('value').text, mapping[int(n.find('type').attrib['topicref'])],
                           observed['ordinal']) for n in expected.findall('name')]
        assert sorted(names) == sorted(expected_names)
print('MERGING-BASELINE-SEMANTIC-EVIDENCE-PASS: 11 frozen baselines; no canonicalization or canonical numbering')
