#!/usr/bin/env python3
"""Independent date grammar/calendar arithmetic and unchanged baseline/model evidence.
Uses Python arbitrary-precision integers and calendar.isleap, never datetime/localtime.
"""
import calendar
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
root = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'date-semantic-and-cxtm-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
names = ['occurrence-date', 'occurrence-date2', 'occurrence-date3', 'occurrence-date-negative', 'occurrence-date-another-century']
values = [['1976-09-19'], ['1976-10-09'], ['0001-12-02', '0011-12-02', '0111-12-02', '1111-12-02'], ['-1976-09-19'], ['191976-09-19']]
dt = 'http://www.w3.org/2001/XMLSchema#date'
assert [c['id'] for c in report['cases']] == ['ctm/in/' + n + '.ctm' for n in names]
for c, expected in zip(report['cases'], values):
    doc = c['documentIRI']; model = c['actualObjects']
    assert doc == 'https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/' + c['id']
    assert c['ctmSource'].encode() == (root / 'vendor/cxtm' / c['id']).read_bytes()
    assert model['topicCount'] == len(expected) + 1 and model['occurrenceCount'] == len(expected)
    assert model['nameCount'] == model['associationCount'] == 0
    for i, t in enumerate(model['topics']):
        local = 'topic' if i == 0 else 'occtype' if len(expected) == 1 else 'o' + str(i)
        assert t['itemIdentifiers'] == [doc + '#' + local]
        assert t['subjectIdentifiers'] == t['subjectLocators'] == []
        if i:
            assert t['occurrences'] == []
    assert model['topics'][0]['occurrences'] == [dict(value=v, datatype=dt, parentTopicOrdinal=1,
                typeTopicOrdinal=i+2, itemIdentifiers=[]) for i, v in enumerate(expected)]
negative = ['date-invalid-day', 'date-invalid-month', 'date-invalid-year', 'date-invalid-year2', 'date-invalid-year3']
assert [c['id'] for c in report['negativeCases']] == ['ctm/invalid/' + n + '.ctm' for n in negative]
for c, code in zip(report['negativeCases'], ['INVALID-DATE-DAY', 'INVALID-DATE-MONTH'] + ['INVALID-DATE-YEAR']*3):
    assert c['ctmSource'].encode() == (root / 'vendor/cxtm' / c['id']).read_bytes()
    assert c['status'] == 'pass' and c['conditionClass'] == 'CTM-REJECTION' and c['code'] == code
    assert c['line'] == c['ctmSource'][:c['position']].count('\n') + 1
    assert c['column'] == c['position'] - c['ctmSource'].rfind('\n', 0, c['position']) == 14


def valid_date(text):
    match = re.fullmatch(r'(-?)([0-9]{4,})-([0-9]{2})-([0-9]{2})', text)
    if not match:
        return False
    sign, digits, month, day = match.groups()
    if len(digits) > 4 and digits.startswith('0'):
        return False
    year, month, day = int(sign + digits), int(month), int(day)
    if year == 0 or not 1 <= month <= 12:
        return False
    days = [31, 29 if calendar.isleap(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1]
    return 1 <= day <= days


assert len(report['calendarDecisions']) == 15
for c in report['calendarDecisions']:
    assert valid_date(c['input']) == (c['expected'] == 'valid'), c
for p in report['lexicalProbes']:
    lexical = p['input'].strip(' \r\t\n')
    assert valid_date(lexical), lexical
    assert p['storedValue'] == p['input'] and p['datatype'] == dt
    xml = ET.fromstring(p['actualCXTM'])
    items = xml.findall('topic/occurrence')
    assert len(items) == 1 and items[0].findtext('value') == lexical and items[0].findtext('datatype') == dt
print(f"DATE-INDEPENDENT-PASS: 5 original sources/model observations; 5 specific rejections; {len(report['lexicalProbes'])} arbitrary-precision calendar probes; 15 century decisions")
