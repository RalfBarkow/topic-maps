#!/usr/bin/env python3
"""Independent integer/calendar/string DateTime oracle; no float or local timezone."""
import calendar
import datetime
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
root = Path(__file__).resolve().parent.parent
r = json.loads(Path(sys.argv[1]).read_text())
assert r['kind'] == 'datetime-semantic-and-cxtm-evidence' and r['failed'] == 0
assert len(r['checks']) == len(set(r['checks'])) == r['passed']
values = ['1976-09-19T12:01:01', '1976-09-19T12:02:00', '2011-01-01T00:00:00.001', '2011-01-01T00:00:00Z', '2010-12-31T22:00:00Z']
for c, value in zip(r['cases'], values):
    assert c['ctmSource'].encode() == (root / 'vendor/cxtm' / c['id']).read_bytes()
    items = [o for t in c['actualObjects']['topics'] for o in t['occurrences']]
    assert len(items) == 1 and items[0]['value'] == value
    assert items[0]['datatype'] == 'http://www.w3.org/2001/XMLSchema#dateTime'
    assert c['status'] == ('fail' if c['id'].endswith(('datetime2.ctm', 'timezone2.ctm')) else 'pass')
assert len(r['cases']) == 5


def canonical(text):
    m = re.fullmatch(r'(-?[0-9]{4,})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]+))?(Z|[+-]00:00)?', text)
    assert m, 'oracle only called for supported lexical probes'
    year, month, day, hour, minute, second, fraction, zone = m.groups()
    y, mo, d, h, mi, se = map(int, (year, month, day, hour, minute, second))
    fraction = (fraction or '').rstrip('0')
    leap = se == 60 and zone and h == 23 and mi == 59 and (mo, d) in [(3,31), (6,30), (9,30), (12,31)]
    if se == 60 and not leap:
        assert (mo, d) not in [(3,31), (4,1), (6,30), (7,1), (9,30), (10,1), (12,31), (1,1)]
        se = 0; mi += 1
    if mi == 60:
        mi = 0; h += 1
    if h == 24:
        h = 0; d += 1
        days = [31, 29 if calendar.isleap(y) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mo-1]
        if d > days:
            d = 1; mo += 1
        if mo == 13:
            mo = 1; y += 1
            if y == 0: y = 1
    ys = ('-' if y < 0 else '') + str(abs(y)).zfill(4)
    return f'{ys}-{mo:02d}-{d:02d}T{h:02d}:{mi:02d}:{se:02d}' + ('.'+fraction if fraction else '') + ('Z' if zone else '')


for p in r['lexicalProbes']:
    expected = canonical(p['input'])
    assert expected == p['canonicalValue']
    assert p['storedValue'] == (expected if p['mode'] == 'bare' else ' '+p['input']+'\t' if p['mode'] == 'qualified' else p['input'])
    items = ET.fromstring(p['actualCXTM']).findall('topic/occurrence')
    assert len(items) == 1 and items[0].findtext('value') == expected
    assert items[0].findtext('datatype') == 'http://www.w3.org/2001/XMLSchema#dateTime'
offset = r['timezoneObservation']
assert offset == r['cases'][-1] and offset['status'] == 'fail'
assert [x['contractStatus'] for x in r['normativeDiscrepancies']] == ['fail', 'fail']
assert datetime.datetime(2011,1,1,tzinfo=datetime.timezone(datetime.timedelta(hours=2))).astimezone(datetime.timezone.utc).isoformat() == '2010-12-31T22:00:00+00:00'
print(f'DATETIME-INDEPENDENT-PASS: {len(r["cases"])} original model observations; {len(r["lexicalProbes"])} exact calendar/fraction probes; 2 documented discrepancies')
