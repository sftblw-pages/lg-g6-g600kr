#!/usr/bin/env python3
"""Verify the 51 partition + 7 GPT files created by scripts/backup-stock.sh."""
import argparse, hashlib, re
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('directory',type=Path)
a=p.parse_args()
entries=[]
for line in (a.directory/'SHA256SUMS.txt').read_text().splitlines():
    expected,remote=line.split(maxsplit=1)
    name=remote.strip().rsplit('/',1)[-1]
    if not re.fullmatch('[0-9a-f]{64}',expected) or not re.fullmatch(r'[a-z0-9-]+\.(img|bin)',name):
        raise ValueError('Invalid backup manifest entry')
    entries.append((name,expected))
if len(entries)!=58 or len({name for name,_ in entries})!=58:
    raise ValueError('Expected 58 unique backup images')
sizes={name+'.img':int(size) for name,size in (line.split() for line in (a.directory/'sizes.txt').read_text().splitlines())}
sizes.update({disk+'-gpt-primary.bin':24576 for disk in ('sda','sdb','sdc','sdd','sde','sdf','sdg')})
if len(sizes)!=58:
    raise ValueError('Unexpected size inventory')
for name,expected in entries:
    f=a.directory/name
    if f.stat().st_size!=sizes[name]:
        raise ValueError('Size mismatch: '+name)
    h=hashlib.sha256()
    with f.open('rb') as source:
        for data in iter(lambda:source.read(8*1024*1024),b''):
            h.update(data)
    if h.hexdigest()!=expected:
        raise ValueError('SHA-256 mismatch: '+name)
print('ALL_58_PRIVATE_BACKUPS_VERIFIED')
