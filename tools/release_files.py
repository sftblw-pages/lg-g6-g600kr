#!/usr/bin/env python3
"""Download, verify, or reassemble release files; never writes to a phone."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def verify(path, item):
    if path.stat().st_size != item['size'] or digest(path) != item['sha256']:
        raise ValueError(f'Size/SHA-256 mismatch: {path.name}')

def prepare_temporary(path, restart):
    if path.exists():
        if not restart:
            raise FileExistsError(f'Incomplete output exists: {path.name}. Rerun with --restart to discard this temporary file and retry.')
        if not path.is_file() or path.is_symlink():
            raise ValueError('Refusing to discard a non-regular temporary file')
        path.unlink()

def assemble(directory, manifest, restart=False):
    item = manifest['reassembled_kdz']
    target = directory / item['name']
    if target.exists():
        verify(target, item)
        print('Already present and verified:', target)
        return target
    pieces = [i for i in manifest['assets'] if i['name'].startswith(item['name']+'.part')]
    if [p['name'] for p in pieces] != [item['name']+f'.part{i:02d}' for i in range(1,4)]:
        raise ValueError('Expected exactly three consecutive KDZ parts')
    for p in pieces:
        verify(directory / p['name'], p)
    temporary = target.with_name(target.name + '.assembling')
    prepare_temporary(temporary, restart)
    # Exclusive creation: never overwrite an existing download or previous attempt.
    owned_temp = False
    try:
        with temporary.open('xb') as output:
            owned_temp = True
            for p in pieces:
                with (directory / p['name']).open('rb') as source:
                    for chunk in iter(lambda: source.read(8 * 1024 * 1024), b''):
                        output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
        verify(temporary, item)
    except BaseException:
        if owned_temp and temporary.is_file():
            temporary.unlink()
        raise
    if target.exists():
        raise FileExistsError(target)
    temporary.rename(target)
    print('ASSEMBLED_AND_VERIFIED', target)
    return target

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['download','verify','assemble'])
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--name', help='A single asset; default selects every manifest asset')
    parser.add_argument('--restart', action='store_true', help='Discard only stale .downloading/.assembling files; keep completed assets')
    args = parser.parse_args()
    manifest = json.loads((ROOT/'downloads/manifest.json').read_text(encoding='utf-8'))
    for item in manifest['assets']:
        if Path(item['name']).name != item['name'] or '/' in item['name'] or '\\' in item['name']:
            raise ValueError('Invalid asset name')
    directory = args.directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    if args.operation == 'assemble':
        if args.name:
            parser.error('--name is not used for assemble')
        assemble(directory, manifest, args.restart)
        return
    selected = [i for i in manifest['assets'] if args.name is None or i['name'] == args.name]
    if not selected:
        parser.error('Asset not listed in manifest')
    for item in selected:
        path = directory/item['name']
        if args.operation == 'download' and not path.exists():
            url = f"https://github.com/{manifest['repository']}/releases/download/{manifest['tag']}/{item['name']}"
            temp = path.with_name(path.name+'.downloading')
            prepare_temporary(temp, args.restart)
            print('Downloading', item['name'], flush=True)
            request = urllib.request.Request(url, headers={'User-Agent':'g600kr-reproduction-guide'})
            owned_temp = False
            try:
                with urllib.request.urlopen(request, timeout=120) as source, temp.open('xb') as output:
                    owned_temp = True
                    for chunk in iter(lambda: source.read(8*1024*1024), b''):
                        output.write(chunk)
                verify(temp, item)
            except BaseException:
                if owned_temp and temp.is_file():
                    temp.unlink()
                raise
            if path.exists():
                raise FileExistsError(path)
            temp.rename(path)
        verify(path, item)
        print('VERIFIED', item['name'], flush=True)

if __name__ == '__main__':
    main()
