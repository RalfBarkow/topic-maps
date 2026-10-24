#!/usr/bin/env python3
"""Configure the existing 22D offline collector; no second test executor."""
import importlib.util
import sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]

def collect(out):
    spec = importlib.util.spec_from_file_location('existing_collector', ROOT / 'scripts/validate-slice-22d.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.TOOLS = ROOT / 'reports/slice-22s'
    m.EXECUTION_FILES = {str(p.relative_to(ROOT)) for folder in ['src', 'tests']
                         for p in (ROOT / folder).rglob('*.lisp')} | {
                         'topic-maps.asd', 'scripts/validate-slice-22d.py',
                         'reports/slice-22s/failure-controls.lisp', 'reports/slice-22s/collect.py'}
    out.mkdir(parents=True, exist_ok=True)
    m.collect(out, ROOT / 'reports/slice-22d/baseline')

if __name__ == '__main__':
    out = Path(sys.argv[1]).resolve()
    assert not out.is_relative_to(ROOT)
    collect(out)
