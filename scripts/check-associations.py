#!/usr/bin/env python3
"""Selected Association/Role properties from frozen baselines; no canonical XML."""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'semantic-observations-not-cxtm'
assert report['failed'] == 0 and report['passed'] == len(report['checks'])
assert len(report['checks']) == len(set(report['checks']))
files = ['association', 'association-binary', 'association-binary-duplicate', 'association-type-sid',
         'association-with-comment', 'association-with-comment2', 'association-with-comment3', 'association-with-comment4']
assert {c['id'] for c in report['cases']} == {'ctm/in/'+f+'.ctm' for f in files}
assert len(report['cases']) == len(files)
for case in report['cases']:
    assert case['ctmSource'] == (root/'vendor/cxtm'/case['id']).read_bytes().decode('utf-8')
    xml = ET.parse(root/'vendor/cxtm/ctm/baseline'/(pathlib.Path(case['id']).name+'.cxtm')).getroot()
    assert xml.tag == 'topicMap' and all(c.tag in ['topic', 'association'] for c in xml)
    model = case['actualObjects']
    expected_topics, expected_associations = xml.findall('topic'), xml.findall('association')
    assert model['topicCount'] == len(expected_topics)
    assert model['associationCount'] == len(expected_associations)
    assert model['roleCount'] == sum(len(a.findall('role')) for a in expected_associations)

    def identifiers(topic, baseline=False):
        result = []
        for prop in ['itemIdentifiers', 'subjectIdentifiers', 'subjectLocators']:
            values = ([v.text for v in topic.findall(prop+'/locator')] if baseline else topic[prop])
            values = [case['documentIRI']+v if v.startswith('#') else v for v in values]
            assert len(values) == len(set(values))
            result.append(tuple(sorted(values)))
        return tuple(result)

    actual_topics = {identifiers(t): t for t in model['topics']}
    assert len(actual_topics) == model['topicCount']
    topic_mapping = {}
    for topic in expected_topics:
        actual = actual_topics[identifiers(topic, True)]
        assert actual['parentIsMap'] and actual['nameCount'] == 0
        assert all(c.tag in ['itemIdentifiers', 'subjectIdentifiers', 'subjectLocators', 'rolePlayed'] for c in topic)
        topic_mapping[int(topic.attrib['number'])] = actual['ordinal']

    def role_signature(role, baseline=False):
        if baseline:
            return (topic_mapping[int(role.find('type').attrib['topicref'])],
                    topic_mapping[int(role.find('player').attrib['topicref'])])
        return role['typeTopicOrdinal'], role['playerTopicOrdinal']

    def association_signature(association, baseline=False):
        return ((topic_mapping[int(association.find('type').attrib['topicref'])] if baseline
                 else association['typeTopicOrdinal']),
                tuple(sorted(role_signature(r, baseline) for r in
                             (association.findall('role') if baseline else association['roles']))))

    actual_associations = {association_signature(a): a for a in model['associations']}
    assert len(actual_associations) == model['associationCount']
    role_mapping = {}
    for association in expected_associations:
        assert all(c.tag in ['type', 'role'] for c in association)
        actual = actual_associations[association_signature(association, True)]
        assert actual['parentIsMap'] and actual['roles']
        roles = {role_signature(r): r for r in actual['roles']}
        assert len(roles) == len(actual['roles'])
        for role in association.findall('role'):
            assert all(c.tag in ['type', 'player'] for c in role)
            observed = roles[role_signature(role, True)]
            assert observed['parentAssociationOrdinal'] == actual['ordinal']
            role_mapping[(int(association.attrib['number']), int(role.attrib['number']))] = (actual['ordinal'], observed['ordinal'])
    for topic in expected_topics:
        expected_played = []
        for ref in topic.findall('rolePlayed'):
            parts = ref.attrib['ref'].split('.')
            assert parts[0] == 'association' and parts[2] == 'role' and len(parts) == 4
            expected_played.append(role_mapping[(int(parts[1]), int(parts[3]))])
        actual = actual_topics[identifiers(topic, True)]
        observed = [(r['associationOrdinal'], r['roleOrdinal']) for r in actual['rolesPlayed']]
        assert sorted(observed) == sorted(expected_played)
print('ASSOCIATION-BASELINE-SEMANTIC-EVIDENCE-PASS: 8 frozen baselines, Role items and roles-played; no canonicalization')
