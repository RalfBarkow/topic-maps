#!/usr/bin/env python3
"""Independent Decimal arithmetic oracle, TMDM observations and baseline evidence.
Decimal.normalize runs with explicitly sufficient precision, never binary float.
"""
import decimal
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'decimal-semantic-and-cxtm-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
names = ['occurrence-decimal', 'occurrence-decimal-dot', 'occurrence-decimal-dot-neg',
         'occurrence-decimal-leading-zeros', 'occurrence-decimal-minus-sign',
         'occurrence-decimal-plus-sign', 'occurrence-decimal-1.0']
values = ['9.3', '0.3', '-0.3', '0.3', '-9.3', '9.3', '1.0']
datatype = 'http://www.w3.org/2001/XMLSchema#decimal'
prefix = 'https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/'
assert [c['id'] for c in report['cases']] == ['ctm/in/' + n + '.ctm' for n in names]
for c, value in zip(report['cases'], values):
    ident = c['id']; doc = c['documentIRI']; m = c['actualObjects']
    assert c['ctmSource'].encode() == (root / 'vendor/cxtm' / ident).read_bytes()
    assert doc == prefix + ident and c['status'] == 'pass'
    assert m['topicCount'] == len(m['topics']) == 2 and m['occurrenceCount'] == 1
    assert m['nameCount'] == m['associationCount'] == 0
    for ordinal, (topic, local) in enumerate(zip(m['topics'], ['topic', 'occtype']), 1):
        assert topic['ordinal'] == ordinal and topic['itemIdentifiers'] == [doc + '#' + local]
        assert topic['subjectIdentifiers'] == topic['subjectLocators'] == []
    assert m['topics'][0]['occurrences'] == [dict(value=value, datatype=datatype, parentTopicOrdinal=1,
                                                 typeTopicOrdinal=2, itemIdentifiers=[])]
    assert m['topics'][1]['occurrences'] == []
assert len(report['lexicalProbes']) == 157
for p in report['lexicalProbes']:
    literal = p['input'].strip(' \t\r\n')
    with decimal.localcontext() as context:
        context.prec = len(literal) + 10
        number = decimal.Decimal(literal)
        assert number.is_finite()
        expected = '0.0' if number.is_zero() else format(number.normalize(), 'f')
        if '.' not in expected:
            expected += '.0'
        assert decimal.Decimal(expected) == number
    assert p['datatype'] == datatype
    assert p['storedValue'] == (expected if p['mode'] == 'implicit' else p['input'])
    xml = ET.fromstring(p['actualCXTM'])
    items = xml.findall('topic/occurrence')
    assert len(items) == 1 and items[0].findtext('value') == expected
    assert items[0].findtext('datatype') == datatype
print('DECIMAL-INDEPENDENT-PASS: 7 original sources/model observations; 157 Decimal arithmetic-oracle probes, including 10000-digit components')
