#!/usr/bin/env python3
"""Check Include model observations separately from the original byte contracts."""
import collections
import json
import pathlib
import sys
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'ctm-include-execution-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
assert len(report['cases']) == 9 and len(report['rejections']) == 3
sizes = {'include': (1939, 1939), 'include-prefix': (140, 140), 'include-prefix2': (261, 261),
         'include-template': (353, 401), 'include-template-wildcard': (330, 330),
         'include-tm-reifier': (375, 375), 'include-topicref': (1490, 1490),
         'include-wildcard': (499, 499), 'include-wildcard2': (719, 669)}
properties = ('itemIdentifiers', 'subjectIdentifiers', 'subjectLocators')


def identity(topic):
    return tuple(tuple(sorted(topic[k])) for k in properties)


def by_identifier(model, iri):
    return next(t for t in model['topics'] if iri in t['itemIdentifiers'])


def signature(topic, topics):
    return (identity(topic),
            tuple(sorted((n['value'], identity(topics[n['type'] - 1])) for n in topic['names'])),
            tuple(sorted((o['value'], o['datatype'], identity(topics[o['type'] - 1])) for o in topic['occurrences'])))


for case in report['cases']:
    name = pathlib.Path(case['id']).stem
    assert name in sizes
    assert case['ctmSource'].encode() == (ROOT / 'vendor/cxtm' / case['id']).read_bytes()
    baseline = (ROOT / 'vendor/cxtm/ctm/baseline' / (name + '.ctm.cxtm')).read_bytes()
    assert (case['byteCount'], case['expectedByteCount']) == sizes[name]
    assert len(baseline) == sizes[name][1]
    known = name in {'include-template', 'include-wildcard2'}
    assert case['baselineMatch'] is (not known)
    assert bool(case['discrepancy']) == known
    doc = case['documentIRI']
    model = case['model']
    topics = model['topics']
    xml = ET.fromstring(baseline)
    assert model['topicCount'] == len(topics) == len(xml.findall('topic'))
    assert model['associationCount'] == len(xml.findall('association'))
    assert case['counter'] == {'include-template-wildcard': 1, 'include-wildcard': 2, 'include-wildcard2': 3}.get(name, 0)
    for i, topic in enumerate(topics, 1):
        assert topic['ordinal'] == i
        for item in topic['names'] + topic['occurrences']:
            assert item['parent'] == i and 1 <= item['type'] <= len(topics)
            assert not item['scope']
    expected_topics = []
    for i, t in enumerate(xml.findall('topic'), 1):
        expected_topics.append({**{k: [urllib.parse.urljoin(doc, l.text) for l in t.findall(k + '/locator')]
                                  for k in properties},
                                'names': [dict(value=n.findtext('value'), type=int(n.find('type').attrib['topicref'])) for n in t.findall('name')],
                                'occurrences': [dict(value=o.findtext('value'), datatype=o.findtext('datatype'), type=int(o.find('type').attrib['topicref'])) for o in t.findall('occurrence')]})
    if not known:
        assert collections.Counter(signature(t, topics) for t in topics) == collections.Counter(signature(t, expected_topics) for t in expected_topics), name
    elif name == 'include-template':
        assert len(case['environments']) == 2
        child = case['environments'][0]
        assert (child['model']['topicCount'], child['templateCount'], child['initialCounter'], child['finalCounter']) == (0, 1, 0, 0)
        assert child['wildcardIRI'] == doc
        owner = by_identifier(model, doc + '#topic')
        typ = by_identifier(model, doc + '#occtype')
        assert owner['itemIdentifiers'] == [doc + '#topic']
        assert typ['itemIdentifiers'] == [doc + '#occtype']
        assert owner['occurrences'] == [dict(value='Test', datatype='http://www.w3.org/2001/XMLSchema#string', parent=owner['ordinal'], type=typ['ordinal'], scope=[])]
        assert any('include-template.sub#occtype' in l.text for l in xml.findall('.//locator'))
    else:
        b = urllib.parse.urljoin(doc, 'include-wildcard2.sub')
        c = urllib.parse.urljoin(doc, 'include-wildcard2.sub2')
        envs = case['environments']
        assert [(e['documentIRI'], e['wildcardIRI'], e['initialCounter'], e['finalCounter']) for e in envs] == [(c, b, 0, 1), (b, doc, 0, 2), (doc, doc, 0, 3)]
        assert by_identifier(envs[0]['model'], b + '#$__1.foo')['itemIdentifiers'] == [b + '#$__1.foo']
        assert set(by_identifier(model, doc + '#$__1.foo')['itemIdentifiers']) == {doc + '#$__1.foo', b + '#$__1.foo'}
        for i, value in enumerate(['Sub Sub', 'Sub', 'Master'], 1):
            owner = by_identifier(model, doc + f'#$__{i}.foo')
            assert len(owner['names']) == 1 and owner['names'][0]['value'] == value
        assert len({t['names'][0]['type'] for t in topics if t['names']}) == 1
        assert len(xml.findall('.//itemIdentifiers/locator')) == 3
        assert sum(len(t['itemIdentifiers']) for t in topics) == 4
    for transfer in case['aliasTransfers']:
        child, parent = transfer['childDocumentIRI'], transfer['parentDocumentIRI']
        before, after = transfer['before']['topics'], transfer['after']['topics']
        # Independent string-prefix/remapping on the actual pre-transfer sets.
        expected = []
        for topic in before:
            ids = set(topic['itemIdentifiers'])
            ids.update(urllib.parse.urljoin(parent, i[len(child):]) for i in topic['itemIdentifiers'] if i.startswith(child))
            expected.append((tuple(sorted(ids)), tuple(sorted(topic['subjectIdentifiers'])), tuple(sorted(topic['subjectLocators']))))
        assert collections.Counter(expected) == collections.Counter(identity(t) for t in after)
    assert len(case['aliasTransfers']) == len(case['requests']) == (2 if name == 'include-wildcard2' else 1)
    for request in case['requests']:
        assert request['purpose'] == 'INCLUDE' and request['notation'] is None
        assert request['resourceIRI'] == urllib.parse.urljoin(request['fromDocumentIRI'], pathlib.Path(request['sourceKey']).name)
        assert (ROOT / 'vendor/cxtm' / request['sourceKey']).is_file()

negative = {'include-prefix': ('UNDEFINED-PREFIX', 'UNDEFINED-PREFIX', 'ctm/invalid/include-prefix.ctm', 31),
            'include-prefix2': ('UNDEFINED-PREFIX', 'UNDEFINED-PREFIX', 'ctm/invalid/include-prefix2.sub', 1),
            'include-xtm': ('CTM-REJECTION', 'INVALID-IRI', 'ctm/invalid/include-xtm.sub', 9)}
for case in report['rejections']:
    name = pathlib.Path(case['id']).stem
    assert (case['class'], case['code'], case['source'], case['position']) == negative[name]
    assert len(case['requests']) == 1
    text = (ROOT / 'vendor/cxtm' / case['source']).read_text()
    prefix = text[:case['position']]
    assert case['line'] == prefix.count('\n') + 1
    assert case['column'] == len(prefix.rsplit('\n', 1)[-1]) + 1
print('INCLUDE-INDEPENDENT-PASS: nine model traces, each alias level, separate two baseline discrepancies, three intended negative causes')
