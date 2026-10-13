#!/usr/bin/env python3
"""Acquisition/integrity only. No CTM parsing, XML comparison or network in verify."""
import argparse
import hashlib
import io
import json
import pathlib
import subprocess
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOCK = ROOT / 'references/corpus-lock.json'
DESTINATION = ROOT / 'vendor/cxtm'


def inventory(root):
    return [dict(path=p.relative_to(root).as_posix(), size=p.stat().st_size,
                 sha256=hashlib.sha256(p.read_bytes()).hexdigest())
            for p in sorted(root.rglob('*')) if p.is_file()]


def recount(root):
    ctm = root / 'ctm'
    valid = sorted((ctm / 'in').rglob('*.ctm'))
    invalid = sorted((ctm / 'invalid').rglob('*.ctm'))
    baselines = sorted((ctm / 'baseline').rglob('*.cxtm'))
    used = set(valid + invalid + baselines)
    auxiliary = sorted(p for p in ctm.rglob('*') if p.is_file() and p not in used)
    expected = {ctm / 'baseline' / (p.relative_to(ctm / 'in').as_posix()+'.cxtm') for p in valid}
    return dict(valid=len(valid), invalid=len(invalid), baselines=len(baselines),
                auxiliary=len(auxiliary),
                missingBaselines=sorted(p.relative_to(root).as_posix() for p in expected if not p.is_file()),
                unmatchedBaselines=sorted(p.relative_to(root).as_posix() for p in baselines if p not in expected))


def verify(lock, root=DESTINATION):
    if not root.is_dir():
        raise SystemExit('Corpus absent; run scripts/corpus.py acquire once with network access.')
    actual = inventory(root)
    if actual != lock['files']:
        expected_map = {e['path']: e for e in lock['files']}
        actual_map = {e['path']: e for e in actual}
        changed = sorted(k for k in expected_map.keys() | actual_map.keys()
                         if expected_map.get(k) != actual_map.get(k))
        raise SystemExit('CORPUS-INTEGRITY-FAIL: ' + ', '.join(changed[:20]))
    return recount(root)


def acquire(lock):
    if DESTINATION.exists():
        verify(lock)
        print('Pinned corpus already present and verified; no files overwritten.')
        return
    with tempfile.TemporaryDirectory(prefix='topic-maps-corpus-') as temporary:
        checkout = pathlib.Path(temporary) / 'upstream'
        subprocess.run(['git', 'clone', '--quiet', lock['repository'] + '.git', str(checkout)], check=True)
        subprocess.run(['git', 'cat-file', '-e', lock['commit'] + '^{commit}'], cwd=checkout, check=True)
        archive = subprocess.check_output(['git', 'archive', '--format=tar', lock['commit']], cwd=checkout)
        if hashlib.sha256(archive).hexdigest() != lock['archiveSHA256']:
            raise SystemExit('Pinned archive hash mismatch; acquisition stopped.')
        staging = pathlib.Path(temporary) / 'corpus'
        staging.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar.getmembers():
                parts = pathlib.PurePosixPath(member.name)
                if parts.is_absolute() or '..' in parts.parts or not (member.isfile() or member.isdir()):
                    raise SystemExit('Unsafe upstream archive entry: ' + member.name)
            tar.extractall(staging)
        verify(lock, staging)
        DESTINATION.parent.mkdir(exist_ok=True)
        # Copy into the absent destination; never merge over existing contents.
        import shutil
        shutil.copytree(staging, DESTINATION)
        verify(lock)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['verify', 'acquire'])
    args = parser.parse_args()
    lock = json.loads(LOCK.read_text())
    if args.operation == 'acquire':
        acquire(lock)
    result = verify(lock)
    print('CORPUS-INTEGRITY-PASS: ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
