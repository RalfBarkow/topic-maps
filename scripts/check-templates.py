#!/usr/bin/env python3
"""Independent JSON/model-reference checks against unchanged original XML."""
import collections
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'template-execution-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
assert len(report['cases']) == 57 and len(report['rejections']) == 10
assert len({c['id'] for c in report['cases']}) == 57
for case in report['cases']:
    original = ROOT / 'vendor/cxtm/ctm/baseline' / (pathlib.Path(case['id']).name + '.cxtm')
    xml = ET.fromstring(original.read_bytes())
    model = case['model']
    assert model['topicCount'] == len(model['topics']) == len(xml.findall('topic')), case['id']
    assert model['associationCount'] == len(xml.findall('association')), case['id']
    topics = model['topics']
    assert [t['ordinal'] for t in topics] == list(range(1, len(topics) + 1))

    def identity(values):
        # The actual byte comparison is separate. These examples use local
        # fragment IIs or absolute external locators. Relate observed absolute
        # locators to the baseline's CXTM 3.18 base-relative representations.
        return tuple(sorted(v[len(case['documentIRI']):] if v.startswith(case['documentIRI']) else v for v in values))

    def model_key(t):
        return tuple(identity(t[k]) for k in ('itemIdentifiers', 'subjectIdentifiers', 'subjectLocators'))

    def xml_key(t):
        return tuple(tuple(sorted(x.text or '' for x in t.findall(k + '/locator')))
                     for k in ('itemIdentifiers', 'subjectIdentifiers', 'subjectLocators'))

    xml_by_key = {xml_key(t): t for t in xml.findall('topic')}
    assert len(xml_by_key) == len(topics)
    refs = {t['ordinal']: xml_by_key[model_key(t)].attrib['number'] for t in topics}
    observed_names = []
    observed_occurrences = []
    for topic in topics:
        for name in topic['names']:
            assert name['parent'] == topic['ordinal']
            observed_names.append((refs[name['parent']], refs[name['type']], name['value'],
                                   tuple(sorted(refs[s] for s in name['scope'])), name['variantCount']))
        for occurrence in topic['occurrences']:
            assert occurrence['parent'] == topic['ordinal']
            observed_occurrences.append((refs[occurrence['parent']], refs[occurrence['type']], occurrence['value'],
                                         occurrence['datatype'], tuple(sorted(refs[s] for s in occurrence['scope']))))
    expected_names = []
    expected_occurrences = []
    for topic in xml.findall('topic'):
        for name in topic.findall('name'):
            expected_names.append((topic.attrib['number'], name.find('type').attrib['topicref'], name.findtext('value') or '',
                                   tuple(sorted(s.attrib['topicref'] for s in name.findall('scope/scopingTopic'))), len(name.findall('variant'))))
        for occurrence in topic.findall('occurrence'):
            expected_occurrences.append((topic.attrib['number'], occurrence.find('type').attrib['topicref'], occurrence.findtext('value') or '',
                                         occurrence.findtext('datatype'), tuple(sorted(s.attrib['topicref'] for s in occurrence.findall('scope/scopingTopic')))))
    assert collections.Counter(observed_names) == collections.Counter(expected_names), case['id']
    assert collections.Counter(observed_occurrences) == collections.Counter(expected_occurrences), case['id']
expected_rejections = {
    'embedded-topic-template': ('INVALID-TEMPLATE-BODY', 'INVALID-TEMPLATE-BODY'),
    'occurrence-explicit-datatype-as-parameter': ('INVALID-TEMPLATE-BODY', 'VARIABLE-DATATYPE'),
    'prefix-template-scope': ('INVALID-TEMPLATE-BODY', 'INVALID-TEMPLATE-BODY'),
    'template-bad-type': ('INVALID-TEMPLATE-ARGUMENT', 'INVALID-TEMPLATE-ARGUMENT'),
    'template-missing-args': ('TEMPLATE-ARITY-ERROR', 'TEMPLATE-ARITY'),
    'template-missing-def': ('UNDEFINED-TEMPLATE', 'UNDEFINED-TEMPLATE'),
    'template-name-collision': ('DUPLICATE-TEMPLATE', 'DUPLICATE-TEMPLATE'),
    'tm-reifier-in-template': ('INVALID-TEMPLATE-BODY', 'INVALID-TEMPLATE-BODY'),
    'variable-undefined': ('UNBOUND-TEMPLATE-VARIABLE', 'VARIABLE-OUTSIDE-TEMPLATE'),
    'variable-undefined2': ('UNBOUND-TEMPLATE-VARIABLE', 'VARIABLE-OUTSIDE-TEMPLATE'),
}
for rejection in report['rejections']:
    assert (rejection['class'], rejection['code']) == expected_rejections[pathlib.Path(rejection['id']).stem]
    assert rejection['source'] == rejection['id']
    text = (ROOT / 'vendor/cxtm' / rejection['id']).read_text()
    assert 0 <= rejection['position'] <= len(text)
    before = text[:rejection['position']]
    assert rejection['line'] == before.count('\n') + 1
    assert rejection['column'] == len(before.rsplit('\n', 1)[-1]) + 1
print('TEMPLATES-INDEPENDENT-PASS: 57 original model graphs and 10 specific rejection contracts')
