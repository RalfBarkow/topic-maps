#!/usr/bin/env python3
"""Configure the retained offline collector; no new test executor or fetches."""
import importlib.util
import sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]

def collect(out):
    spec = importlib.util.spec_from_file_location('retained_collector', ROOT/'scripts/validate-slice-22d.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    # Preserve all 113 already qualified failure controls without retargeting.
    m.TOOLS = ROOT/'reports/slice-22s'
    m.EXECUTION_FILES = {str(p.relative_to(ROOT)) for folder in ['src', 'tests', 'examples']
                         for p in (ROOT/folder).rglob('*.lisp')} | {
        'topic-maps.asd', 'scripts/validate-slice-22d.py', 'scripts/fresh-sbcl.lisp', 'examples/project-work.ctm',
        'reports/slice-22s/failure-controls.lisp',
        'reports/slice-22u/collect.py', 'reports/slice-22u/reproduce.py'}
    out.mkdir(parents=True, exist_ok=True)
    m.collect(out, ROOT/'reports/slice-22d/baseline')

if __name__ == '__main__':
    out = Path(sys.argv[1]).resolve()
    assert not out.is_relative_to(ROOT)
    collect(out)
