#!/usr/bin/env python3
"""Check actual model observations, original sources and specific rejection positions."""
import json
import pathlib
import sys
root = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'prefix-and-explicit-datatype-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
assert {c['id'] for c in report['cases']} == {
    'ctm/in/' + n + '.ctm' for n in ['occurrence-explicit-datatype', 'occurrence-datatype-unknown',
                                    'prefix-duplicate', 'prefix-duplicate2', 'prefix-multiline']
} | {'ctm/invalid/prefix-collision.ctm', 'ctm/invalid/prefix-undefined2.ctm'}
assert len(report['cases']) == 7
prefix = 'https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/'
for c in report['cases']:
    ident = c['id']; doc = c['documentIRI']; name = pathlib.Path(ident).stem
    source = (root / 'vendor/cxtm' / ident).read_bytes()
    assert c['ctmSource'].encode('utf-8') == source
    assert doc == prefix + ident and c['status'] == 'pass'
    if '/invalid/' in ident:
        collision = name == 'prefix-collision'
        assert c['conditionClass'] == ('PREFIX-COLLISION' if collision else 'UNDEFINED-PREFIX')
        assert c['code'] == c['conditionClass'] and c['positionUnit'] == 'character' and c['source'] == ident
        text = source.decode('utf-8')
        position = text.index('ex http://www.example.net' if collision else 'xsd:int')
        assert c['position'] == position and c['line'] == text[:position].count('\n') + 1
        assert c['column'] == position - text.rfind('\n', 0, position)
        continue
    m = c['actualObjects']; topics = m['topics']; occurrence = name.startswith('occurrence-')
    assert m['nameCount'] == m['associationCount'] == 0
    assert m['topicCount'] == len(topics) == (2 if occurrence or name == 'prefix-duplicate2' else 1)
    assert m['occurrenceCount'] == int(occurrence)
    for i, t in enumerate(topics, 1):
        assert t['ordinal'] == i and t['subjectLocators'] == []
        if occurrence:
            assert t['itemIdentifiers'] == [doc + ('#topic' if i == 1 else '#occtype')]
            assert t['subjectIdentifiers'] == []
        else:
            assert t['itemIdentifiers'] == [] and t['occurrences'] == []
            assert t['subjectIdentifiers'] == ['http://psi.example.org/' + ('fake' if i == 1 else 'fake2')]
    if occurrence:
        unknown = name == 'occurrence-datatype-unknown'
        assert topics[1]['occurrences'] == []
        assert topics[0]['occurrences'] == [dict(value='BOGUS' if unknown else 'Occurrence',
            datatype='http://example.com/bogus' if unknown else 'http://www.w3.org/2001/XMLSchema#string',
            parentTopicOrdinal=1, typeTopicOrdinal=2, itemIdentifiers=[])]
print('PREFIX-INDEPENDENT-PASS: 7 original sources, 5 model observations, 2 specific rejections with independently checked positions')
