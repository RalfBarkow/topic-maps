#!/usr/bin/env python3
"""Independent raw UTF-8 comparison, XML reference integrity and C14N checks."""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET
root = pathlib.Path(__file__).resolve().parent.parent
report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert report['kind'] == 'cxtm-byte-equality' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))
expected_count = {'--slice-5': 28, '--slice-6': 33, '--slice-7': 39, '--slice-8': 46}.get(sys.argv[2] if len(sys.argv) > 2 else '', 24)
assert len(report['cases']) == expected_count
for case in report['cases']:
    actual = case['actualCXTM'].encode('utf-8')
    expected = (root / 'vendor/cxtm/ctm/baseline' / (pathlib.Path(case['id']).name + '.cxtm')).read_bytes()
    assert actual == expected == case['expectedCXTM'].encode('utf-8'), case['id']
    assert case['byteCount'] == len(actual) and case['status'] == 'pass'
    assert case['baseLocator'].endswith('/' + case['id'])
    # CXTM 3.1 adds an LF after the root. XML reparsing drops that Infoset
    # sibling; this check is separate from the unmodified byte comparison.
    assert actual.endswith(b'</topicMap>\n') and not actual.startswith(b'\xef\xbb\xbf')
    assert ET.canonicalize(case['actualCXTM']) + '\n' == case['actualCXTM'], case['id']
    xml = ET.fromstring(actual)
    topics = xml.findall('topic'); associations = xml.findall('association')
    assert [t.attrib['number'] for t in topics] == list(map(str,range(1,len(topics)+1)))
    role_refs = {}
    for i, a in enumerate(associations,1):
        assert a.attrib['number'] == str(i)
        for j, r in enumerate(a.findall('role'),1):
            assert r.attrib['number'] == str(j)
            role_refs[f'association.{i}.role.{j}'] = r.find('player').attrib['topicref']
    for t in topics:
        assert [o.attrib['number'] for o in t.findall('occurrence')] == list(map(str, range(1,len(t.findall('occurrence'))+1)))
        for r in t.findall('rolePlayed'):
            assert role_refs[r.attrib['ref']] == t.attrib['number']
    assert sum(len(t.findall('rolePlayed')) for t in topics) == len(role_refs)
    for ref in xml.iter():
        if 'topicref' in ref.attrib:
            assert 1 <= int(ref.attrib['topicref']) <= len(topics)
print(f'CXTM-INDEPENDENT-PASS: {expected_count} unchanged baselines, exact UTF-8 bytes, canonical XML and reference integrity')
