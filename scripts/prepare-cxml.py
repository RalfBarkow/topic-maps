#!/usr/bin/env python3
"""Apply the versioned XML encoding patches to verified Nix sources, offline."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
NIX_EVAL = ['nix', 'eval', '--offline', '--option', 'eval-cache', 'false']
PATCHES = {'closure-common': ['encodings.lisp', 'xstream.lisp'],
           'cxml': ['xml/xml-parse.lisp']}


def command(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def source_environment():
    system = command(NIX_EVAL + ['--impure', '--raw', '--expr', 'builtins.currentSystem'])
    return system, json.loads(command(NIX_EVAL + ['--json', '.#lib.cxmlEnvironment',
                                                '--apply', 'f: f "' + system + '"']))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def registry(paths):
    return '(:source-registry ' + ' '.join('(:tree ' + json.dumps(str(p) + '/') + ')'
                                          for p in paths) + ' :ignore-inherited-configuration)'


def prepare(environment, target):
    target = Path(target).resolve()
    # Verify every pristine input before creating or changing an output.
    for package in environment['manifest']:
        source = Path(package['source'])
        assert source.is_dir(), 'Missing local source: ' + package['name']
        actual = command(['nix', 'hash', 'path', '--type', 'sha256', '--base32', str(source)])
        assert actual == package['sha256'], 'SOURCE HASH MISMATCH: ' + package['name']
    target.mkdir(parents=True, exist_ok=False)
    provenance = {'sources': environment['manifest'], 'patches': [], 'effectiveSources': []}
    for package in environment['manifest']:
        name = package['name']
        source = Path(package['source'])
        effective = source
        if name in PATCHES:
            effective = target / name
            shutil.copytree(source, effective)
            for path in [effective, *effective.rglob('*')]:
                path.chmod(path.stat().st_mode | 0o200)
            before = {str(p.relative_to(effective)): digest(p)
                      for p in effective.rglob('*') if p.is_file()}
            patch = ROOT / 'patches' / (name + '-19d0b.patch')
            pinned_patch = next(p for p in environment['localPatches'] if p['package'] == name)
            assert digest(patch) == pinned_patch['sha256'], 'LOCAL PATCH HASH MISMATCH: ' + name
            applied = subprocess.run(['patch', '--batch', '--fuzz=0', '-p1',
                                      '-d', str(effective), '-i', str(patch)],
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            assert applied.returncode == 0, applied.stdout
            assert 'offset' not in applied.stdout and 'fuzz' not in applied.stdout, applied.stdout
            after = {str(p.relative_to(effective)): digest(p)
                     for p in effective.rglob('*') if p.is_file()}
            assert before.keys() == after.keys(), 'Unexpected files from patch'
            changed = sorted(p for p in before if before[p] != after[p])
            assert changed == sorted(PATCHES[name]), changed
            provenance['patches'].append({
                'package': name, 'patch': str(patch.relative_to(ROOT)), 'sha256': digest(patch),
                'changedFiles': {p: {'before': before[p], 'after': after[p]} for p in changed},
                'application': applied.stdout.strip()})
        provenance['effectiveSources'].append({'name': name, 'source': str(effective)})
    provenance['sourceRegistry'] = registry([p['source'] for p in provenance['effectiveSources']])
    (target / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    return provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', required=True, type=Path, help='New output directory; never overwritten')
    parser.add_argument('--registry', action='store_true', help='Print only CL_SOURCE_REGISTRY')
    args = parser.parse_args()
    _, environment = source_environment()
    provenance = prepare(environment, args.directory)
    print(provenance['sourceRegistry'] if args.registry else json.dumps(provenance, indent=2))


if __name__ == '__main__':
    main()
