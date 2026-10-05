#!/usr/bin/env python3
"""Anonymize Windows user directories in non-loaded ELF debug sections only."""
import argparse, hashlib, json, re, struct
from pathlib import Path

ORIGINAL='65918c945819636ade9051c57c751629bccb7002dc8c4fcd5efca91fe80c5820'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original',type=Path)
    p.add_argument('output',type=Path)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists() or a.report.exists(): raise FileExistsError('Output/report already exists')
    data=a.original.read_bytes()
    if hashlib.sha256(data).hexdigest()!=ORIGINAL: raise ValueError('Unexpected original binary')
    if data[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',data,18)[0]!=183:
        raise ValueError('Expected little-endian ELF64 AArch64')
    phoff,shoff=struct.unpack_from('<QQ',data,32)
    phsize,phnum,shsize,shnum,shstr=struct.unpack_from('<HHHHH',data,54)
    loads=[]
    for i in range(phnum):
        entry=phoff+i*phsize
        if struct.unpack_from('<I',data,entry)[0]==1:
            loads.append((struct.unpack_from('<Q',data,entry+8)[0],struct.unpack_from('<Q',data,entry+32)[0]))
    string_entry=shoff+shstr*shsize
    string_offset,string_size=struct.unpack_from('<QQ',data,string_entry+24)
    names=data[string_offset:string_offset+string_size]
    sections=[]
    for i in range(shnum):
        entry=shoff+i*shsize
        name_offset=struct.unpack_from('<I',data,entry)[0]
        name=names[name_offset:].split(b'\0',1)[0].decode('ascii')
        offset,size=struct.unpack_from('<QQ',data,entry+24)
        if name.startswith('.debug_'): sections.append((name,offset,size))
    result=bytearray(data)
    edits=[]
    for match in re.finditer(rb'(?i)([A-Z]:[\\/]Users[\\/])([^\\/:\x00\r\n]+)',data):
        start,end=match.span(2)
        if any(start<offset+size and end>offset for offset,size in loads):
            raise ValueError('User path found in a loaded segment: refuse to change executable contents')
        section=next((name for name,offset,size in sections if offset<=start and end<=offset+size),None)
        if section is None: raise ValueError('Path is outside a debug section')
        result[start:end]=b'x'*(end-start)
        edits.append(dict(offset=start,length=end-start,section=section))
    if not edits: raise ValueError('No debug paths found')
    unchanged=all(result[offset:offset+size]==data[offset:offset+size] for offset,size in loads)
    if not unchanged or len(result)!=len(data): raise AssertionError('Loadable segments changed')
    report=dict(original_sha256=ORIGINAL,public_sha256=hashlib.sha256(result).hexdigest(),size=len(result),
                change='Equal-length username masking in non-loaded DWARF debug sections',
                all_PT_LOAD_bytes_identical=unchanged,patches=edits)
    a.output.write_bytes(result)
    a.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in report.items() if k!='patches'},indent=2))

if __name__=='__main__': main()
