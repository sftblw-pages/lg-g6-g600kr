#!/usr/bin/env python3
"""Read-only TWRP backup and local Wi-Fi staging. Does not flash or reboot."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BOOT_SHA = '0db389f0d9223d6b4aa4e0a60e3c2c2bbc0b1bfb29e1d773ef4bd2aea47cd05f'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--adb',default='adb')
    p.add_argument('--serial',required=True,help='Current TWRP serial from adb devices')
    p.add_argument('--assets',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True,help='New PRIVATE local directory; never upload')
    a=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9._:-]{1,100}',a.serial):
        raise ValueError('Unexpected serial format')
    out=a.out.resolve()
    if out.exists():
        raise FileExistsError('Use a new private output directory')
    manifest=json.loads((ROOT/'downloads/manifest.json').read_text(encoding='utf-8'))
    for name in ('boot-g600kr-wifi.img','g600kr20p-wifi-files.zip'):
        expected=next(i for i in manifest['assets'] if i['name']==name)
        source=a.assets/name
        if source.stat().st_size != expected['size'] or sha(source)!=expected['sha256']:
            raise ValueError('Release asset verification failed: '+name)
    adb=[a.adb,'-s',a.serial]
    def remote(command):
        r=subprocess.run(adb+['shell',command],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        return r.stdout.decode('utf-8').strip()
    for command,expected in [
        ('id -u','0'),('getprop ro.twrp.version','3.5.2_10-0'),
        ('getprop ro.product.device','h870'),('getprop ro.serialno',a.serial),
        ('blockdev --getsize64 /dev/block/bootdevice/by-name/boot','41943040'),
        ('blockdev --getsize64 /dev/block/bootdevice/by-name/system','5863636992')]:
        if remote(command)!=expected:
            raise ValueError('TWRP precondition mismatch: '+command)
    if remote('sha256sum /dev/block/bootdevice/by-name/aboot').split()[0] != 'bac7b2809e60cfcb695f0b4afcdfff016b395d546cbd29f36be38696410242f9':
        raise ValueError('Not the tested ENG aboot')
    recovery=remote('dd if=/dev/block/bootdevice/by-name/recovery bs=4096 count=8510 2>/dev/null | sha256sum').split()[0]
    if recovery!='e0c4134402fcd1697cc7395eb22a0ee2742837c933995898340e75cafabd6667':
        raise ValueError('Unexpected recovery image')
    mp='/tmp/g6-public-backup-system'
    remote('mkdir -p '+mp)
    remote('mount -t ext4 -o ro /dev/block/bootdevice/by-name/system '+mp)
    try:
        props=remote('cat '+mp+'/system/build.prop')
        if 'ro.lineage.version=21.0-20260531-UNOFFICIAL-h870' not in props.splitlines():
            raise ValueError('Not the tested LineageOS build')
        remote('test ! -e '+mp+'/system/vendor/etc/wifi/4359_lg.clm_blob')
        out.mkdir(parents=True)
        before=out/'before'
        before.mkdir()
        boot=before/'boot-partition.img'
        with boot.open('xb') as f:
            subprocess.run(adb+['exec-out','dd if=/dev/block/bootdevice/by-name/boot bs=1048576 2>/dev/null'],stdout=f,stderr=subprocess.PIPE,check=True)
        if boot.stat().st_size!=41943040 or sha(boot)!=remote('sha256sum /dev/block/bootdevice/by-name/boot').split()[0]:
            raise ValueError('Boot backup/readback mismatch')
        with boot.open('rb') as f:
            if hashlib.sha256(f.read(17571840)).hexdigest()!=BOOT_SHA:
                raise ValueError('Boot prefix differs from the tested original ROM')
        for name in ('fw_bcmdhd.bin','fw_bcmdhd_apsta.bin','fw_bcmdhd_mfg.bin','bcmdhd.cal'):
            relative='etc/wifi/' if name.endswith('.cal') else 'firmware/'
            source=mp+'/system/vendor/'+relative+name
            target=before/name
            subprocess.run(adb+['pull',source,str(target)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if sha(target)!=remote('sha256sum '+source).split()[0]:
                raise ValueError('Wi-Fi backup mismatch: '+name)
        (before/'boot.sha256').write_text(sha(boot)+'\n',encoding='ascii',newline='\n')
    finally:
        remote('umount '+mp)
    wifi=json.loads((ROOT/'downloads/wifi-files.json').read_text())
    with zipfile.ZipFile(a.assets/'g600kr20p-wifi-files.zip') as z:
        (out/'stock').mkdir()
        for name,expected in wifi.items():
            content=z.read('stock/'+name)
            if len(content)!=expected['size'] or hashlib.sha256(content).hexdigest()!=expected['sha256']:
                raise ValueError('Invalid stock Wi-Fi file: '+name)
            (out/'stock'/name).write_bytes(content)
    shutil.copyfile(a.assets/'boot-g600kr-wifi.img',out/'boot-g600kr-wifi.img')
    for source,name in [('wifi-apply.sh','apply.sh'),('wifi-restore.sh','restore.sh')]:
        shutil.copyfile(ROOT/'scripts'/source,out/name)
    (out/'expected-serial.txt').write_text(a.serial+'\n',encoding='ascii',newline='\n')
    (out/'PRIVATE-DO-NOT-UPLOAD.txt').write_text('Contains your device serial and rollback files. Keep offline.\n',encoding='utf-8')
    sums=''.join(sha(f)+'  '+f.relative_to(out).as_posix()+'\n' for f in sorted(out.rglob('*')) if f.is_file())
    (out/'SHA256SUMS').write_text(sums,encoding='ascii',newline='\n')
    print('PRIVATE_BACKUP_AND_STAGE_READY; no flash or reboot performed')

if __name__=='__main__':
    main()
