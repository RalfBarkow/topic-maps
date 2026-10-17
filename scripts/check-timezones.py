#!/usr/bin/env python3
"""Independent arbitrary-integer UTC oracle; fixed-offset datetime cross-checks.

Fractions stay text; no float, implicit local timezone or platform calendar.
"""
import datetime
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
report = json.loads(Path(sys.argv[1]).read_text())
assert report['kind'] == 'datetime-timezone-evidence' and report['failed'] == 0
assert report['passed'] == len(report['checks']) == len(set(report['checks']))


def canonical(text):
    match = re.fullmatch(r'(-?[0-9]{4,})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]+))?(Z|[+-][0-9]{2}:[0-9]{2})?', text)
    assert match
    year, month, day, hour, minute, second, fraction, zone = match.groups()
    y, mo, d, h, mi, se = map(int, (year, month, day, hour, minute, second))
    original = y, mo, d, h, mi, se
    assert se < 60, 'new nonzero-offset leap-second semantics deliberately excluded'
    offset = 0 if not zone or zone == 'Z' else (1 if zone[0] == '+' else -1) * (int(zone[1:3]) * 60 + int(zone[4:]))
    carry, minutes = divmod(h * 60 + mi - offset, 1440)

    def days(y, mo):
        leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
        return [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mo - 1]

    d += carry
    while d < 1:
        mo -= 1
        if mo == 0:
            mo = 12
            y -= 1
            if y == 0:
                y = -1
        d += days(y, mo)
    while d > days(y, mo):
        d -= days(y, mo)
        mo += 1
        if mo == 13:
            mo = 1
            y += 1
            if y == 0:
                y = 1
    h, mi = divmod(minutes, 60)
    fraction = (fraction or '').rstrip('0')
    result = f'{"-" if y < 0 else ""}{str(abs(y)).zfill(4)}-{mo:02d}-{d:02d}T{h:02d}:{mi:02d}:{se:02d}'
    result += ('.' + fraction if fraction else '') + ('Z' if zone else '')
    # A second, standard-library implementation for CE dates in its range.
    if 1 <= original[0] <= 9998:
        yy, mm, dd, hh, mn, ss = original
        value = datetime.datetime(yy, mm, dd) + datetime.timedelta(hours=hh, minutes=mn, seconds=ss)
        if zone:
            value = value.replace(tzinfo=datetime.timezone(datetime.timedelta(minutes=offset))).astimezone(datetime.timezone.utc)
        spelling = value.strftime('%Y-%m-%dT%H:%M:%S') + ('.' + fraction if fraction else '') + ('Z' if zone else '')
        assert spelling == result
    return result


offsets = set()
for probe in report['lexicalProbes']:
    expected = canonical(probe['input'])
    assert probe['canonicalValue'] == expected
    mode = probe['mode']
    if mode == 'helper':
        offsets.add(probe['input'][-6:])
        continue
    assert probe['storedValue'] == (expected if mode == 'bare' else ' ' + probe['input'] + '\t' if mode == 'qualified' else probe['input'])
    item, = ET.fromstring(probe['actualCXTM']).findall('topic/occurrence')
    assert item.findtext('value') == expected
    assert item.findtext('datatype') == 'http://www.w3.org/2001/XMLSchema#dateTime'
assert len(offsets) == 1681
print(f'TIMEZONE-INDEPENDENT-PASS: {len(report["lexicalProbes"])} exact UTC probes; 1681 signed offset minutes; stored strings and CXTM checked separately')
