#!/usr/bin/env python3
"""Evaluate the stored CXTM baselines of the original isa/ako inputs and compare with the Lisp readers.

This is an independent evaluation of serialized data: it counts, in each unchanged baseline, the
associations that have the structure of TMDM 7.2 or 7.3. It is not a proof of conformance to the
standard; the normative expectations are argued clause by clause in tests/core-relationships.lisp.
"""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
PREFIX = 'http://psi.topicmaps.org/iso13250/model/'
RULES = {'type_instance': ('type-instance', 'type', 'instance'),
         'supertype_subtype': ('supertype-subtype', 'supertype', 'subtype')}


def count(baseline, rule):
    relationship, first, second = (PREFIX + local for local in RULES[rule])
    identifiers = {topic.attrib['number']: {locator.text for locator in topic.findall('subjectIdentifiers/locator')}
                   for topic in baseline.findall('topic')}
    found = 0
    for association in baseline.findall('association'):
        roles = [identifiers[role.find('type').attrib['topicref']] for role in association.findall('role')]
        if (relationship in identifiers[association.find('type').attrib['topicref']] and len(roles) == 2
                and any(first in a and second in b for a, b in (roles, roles[::-1]))):
            found += 1
    return found


report = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert len(report['cases']) == 11 and len({case['id'] for case in report['cases']}) == 11
for case in report['cases']:
    assert case['id'].startswith('ctm/in/') and case['id'].endswith('.ctm'), case['id']
    name = pathlib.Path(case['id']).name
    baseline = ET.parse(ROOT / 'vendor/cxtm/ctm/baseline' / (name + '.cxtm')).getroot()
    for rule in RULES:
        assert count(baseline, rule) == case[rule], (case['id'], rule, count(baseline, rule), case[rule])
print('CORE-RELATIONSHIPS-SERIALIZED-DATA-PASS: 11 original CXTM baselines hold the association counts '
      'the TMDM 7.2/7.3 readers report; an evaluation of serialized data, not a conformance proof')
