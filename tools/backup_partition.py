#!/usr/bin/env python3
"""Read an offline TWRP partition to a PC, then compare size and SHA-256."""
import argparse, hashlib, json, subprocess
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--adb',default='adb')
    p.add_argument('--serial',required=True)
    p.add_argument('--partition',choices=['system','boot','recovery'],required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    adb=[a.adb,'-s',a.serial]
    def shell(command):
        return subprocess.check_output(adb+['shell',command],text=True).strip()
    if shell('id -u')!='0' or shell('getprop ro.twrp.version')!='3.5.2_10-0':
        raise ValueError('Expected root in the tested TWRP')
    block='/dev/block/bootdevice/by-name/'+a.partition
    size=int(shell('blockdev --getsize64 '+block))
    expected={'system':5863636992,'boot':41943040,'recovery':42467328}[a.partition]
    if size!=expected:
        raise ValueError('Partition layout differs from the tested device')
    report=a.output.with_suffix(a.output.suffix+'.json')
    if a.output.exists() or report.exists():
        raise FileExistsError('Output/report already exists')
    # A live writable filesystem can change while read: refuse its backup.
    realblock=shell('readlink -f '+block)
    for line in shell('cat /proc/mounts').splitlines():
        fields=line.split()
        if len(fields)>=4 and fields[0] in (block,realblock) and 'rw' in fields[3].split(','):
            raise ValueError('Partition is mounted writable; unmount it in TWRP first')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('xb') as out:
        subprocess.run(adb+['exec-out',f'dd if={block} bs=1048576 2>/dev/null'],stdout=out,stderr=subprocess.PIPE,check=True)
    h=hashlib.sha256()
    with a.output.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):
            h.update(chunk)
    local=h.hexdigest()
    remote=shell('sha256sum '+block).split()[0]
    verified=a.output.stat().st_size==size and local==remote
    report.write_text(json.dumps(dict(partition=a.partition,size=size,sha256=local,remote_sha256=remote,verified=verified),indent=2)+'\n',encoding='utf-8')
    if not verified:
        raise ValueError('Backup verification failed; stop before installing')
    print('BACKUP_VERIFIED',a.partition,size,local)

if __name__=='__main__':
    main()
