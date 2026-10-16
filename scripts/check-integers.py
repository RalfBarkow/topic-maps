#!/usr/bin/env python3
"""Independent integer arithmetic, TMDM property and raw baseline evidence checks."""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'integer-semantic-and-cxtm-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
names = ['occurrence-integer', 'occurrence-integer2', 'occurrence-integer-plus-sign',
         'occurrence-integer-minus-sign', 'occurrence-integer-leading-zeros', 'occurrence-explicit-datatype2']
assert [c['id'] for c in report['cases']] == ['ctm/in/' + n + '.ctm' for n in names]
iri_prefix = 'https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/'
datatype = 'http://www.w3.org/2001/XMLSchema#integer'
for c in report['cases']:
    ident = c['id']; doc = c['documentIRI']; m = c['actualObjects']
    assert c['ctmSource'].encode('utf-8') == (root / 'vendor/cxtm' / ident).read_bytes()
    assert doc == iri_prefix + ident and c['status'] == 'pass'
    zeros = ident.endswith('occurrence-integer-leading-zeros.ctm')
    expected = ['1', '1', '-1', '100', '0', '0', '0'] if zeros else ['-1'] if ident.endswith('minus-sign.ctm') else ['42'] if ident.endswith('datatype2.ctm') else ['1']
    assert m['topicCount'] == len(m['topics']) == (8 if zeros else 2)
    assert m['occurrenceCount'] == len(expected) and m['nameCount'] == m['associationCount'] == 0
    locals_ = ['topic'] + ([f'o{i}' for i in range(1, 8)] if zeros else ['occtype'])
    for ordinal, (topic, local) in enumerate(zip(m['topics'], locals_), 1):
        assert topic['ordinal'] == ordinal and topic['itemIdentifiers'] == [doc + '#' + local]
        assert topic['subjectIdentifiers'] == topic['subjectLocators'] == []
        if ordinal != 1:
            assert topic['occurrences'] == []
    assert m['topics'][0]['occurrences'] == [dict(value=v, datatype=datatype, parentTopicOrdinal=1,
                                                 typeTopicOrdinal=i + 2, itemIdentifiers=[]) for i, v in enumerate(expected)]
# Python big integers provide an independent algorithm, including 10,000 digits.
# Narrow the accepted whitespace here to XML whitespace, not Python's Unicode set.
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
assert len(report['lexicalProbes']) == 143
for p in report['lexicalProbes']:
    expected = str(int(p['input'].strip(' \t\r\n'), 10))
    assert p['datatype'] == datatype
    assert p['storedValue'] == (expected if p['mode'] == 'implicit' else p['input'])
    xml = ET.fromstring(p['actualCXTM'])
    occurrences = xml.findall('topic/occurrence')
    assert len(occurrences) == 1 and occurrences[0].findtext('value') == expected
    assert occurrences[0].findtext('datatype') == datatype
print('INTEGER-INDEPENDENT-PASS: 6 original sources/model observations; 143 arithmetic-oracle probes, including 10000-digit integers')
