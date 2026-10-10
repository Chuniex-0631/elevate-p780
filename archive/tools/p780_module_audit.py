# ARCHIVED READ-ONLY INSPECTION UTILITY. CHECK INPUTS AND OUTPUT PATHS BEFORE USE.
#!/usr/bin/env python3
"""Read-only ELF kernel module inventory for Rakuten Hand 5G P780.

Uses only Python standard library; never writes or executes a module.
Scans .ko (including .ko.xz/.ko.gz if present); parses ELF metadata,
modinfo and __versions, when available. Does not derive root offsets.
"""
import argparse
import gzip
import hashlib
import json
import lzma
import struct
import sys
from pathlib import Path

MAX_FILE = 100 * 1024 * 1024


def unpack(path):
    raw = path.read_bytes()
    if len(raw) > MAX_FILE:
        raise ValueError("Input exceeds maximum file size")
    if path.suffix == '.xz':
        raw = lzma.decompress(raw, memlimit=256 * 1024 * 1024)
    elif path.suffix == '.gz':
        raw = gzip.decompress(raw)
    if len(raw) > MAX_FILE:
        raise ValueError("Decompressed input too large")
    return raw


def elf_sections(data):
    if data[:4] != b'\x7fELF':
        raise ValueError('Not ELF (possibly a compressed or signed module)')
    elfclass = data[4]
    endian = '<' if data[5] == 1 else '>' if data[5] == 2 else None
    if elfclass not in (1, 2) or endian is None:
        raise ValueError('Unsupported ELF format')
    is64 = elfclass == 2
    if is64:
        hdr_fmt = endian + 'HHIQQQIHHHHHH'
        sh_fmt = endian + 'IIQQQQIIQQ'
        shoff_i, shentsize_i, shnum_i, shstr_i = 5, 10, 11, 12
    else:
        hdr_fmt = endian + 'HHIIIIIHHHHHH'
        sh_fmt = endian + 'IIIIIIIIII'
        shoff_i, shentsize_i, shnum_i, shstr_i = 5, 10, 11, 12
    header = struct.unpack_from(hdr_fmt, data, 16)
    shoff, shentsize, shnum, shstridx = (header[i] for i in (shoff_i, shentsize_i, shnum_i, shstr_i))
    real_sh_size = struct.calcsize(sh_fmt)
    if not shentsize or shentsize < real_sh_size or shoff + shnum * shentsize > len(data):
        raise ValueError('Invalid ELF section header table')
    sections = []
    for i in range(shnum):
        f = struct.unpack_from(sh_fmt, data, shoff + i * shentsize)
        nameoff, sec_type = f[0], f[1]
        offset, size = f[4], f[5]
        if offset + size > len(data):
            raise ValueError('Invalid ELF section boundary')
        sections.append(dict(nameoff=nameoff, type=sec_type, offset=offset, size=size, body=data[offset:offset+size]))
    if shstridx >= len(sections):
        raise ValueError('Invalid ELF string table reference')
    strings = sections[shstridx]['body']
    for sec in sections:
        off = sec['nameoff']
        end = strings.find(b'\0', off) if off < len(strings) else -1
        sec['name'] = strings[off:end].decode('ascii', 'replace') if end >= 0 else '<unnamed>'
    return {'arch': header[1], 'bits': 64 if is64 else 32, 'endian': 'little' if endian == '<' else 'big', 'sections': sections, 'prefix': endian}


def build_id(note, prefix):
    at = 0
    while at + 12 <= len(note):
        namesz, descsz, kind = struct.unpack_from(prefix+'III',note,at)
        at += 12
        if namesz > len(note) - at: break
        name = note[at:at+namesz].rstrip(b'\0')
        at += (namesz + 3) & ~3
        if descsz > len(note) - at: break
        val = note[at:at+descsz]
        at += (descsz + 3) & ~3
        if name == b'GNU' and kind == 3:
            return val.hex()
    return None


def decode_modinfo(data):
    result = {}
    for part in data.split(b'\0'):
        if b'=' not in part: continue
        k, v = part.split(b'=',1)
        key = k.decode('utf-8','replace')
        result.setdefault(key,[]).append(v.decode('utf-8','replace'))
    return result


def decode_modversions(data, prefix, bits):
    # Legacy Linux 5.4 struct modversion_info: (unsigned long crc; char name[56])
    stride = 64 if bits == 64 else 60
    crc_fmt = prefix + ('Q' if bits == 64 else 'I')
    sample = []
    n_valid = 0
    if not data or len(data) % stride: return {'count': None, 'reason': 'unexpected legacy __versions size'}
    for i in range(0, len(data),stride):
        crc = struct.unpack_from(crc_fmt,data,i)[0]
        name = data[i+struct.calcsize(crc_fmt):i+stride].split(b'\0',1)[0].decode('utf-8','replace')
        if name:
            n_valid += 1
            if len(sample)<25: sample.append({'symbol': name, 'crc': f'0x{crc:08x}'})
    return {'count':n_valid,'sample':sample}


def scan(path):
    data = unpack(path)
    elf = elf_sections(data)
    sections = {s['name']:s['body'] for s in elf['sections']}
    meta = decode_modinfo(sections.get('.modinfo',b''))
    out = {
        'name': path.name, 'bytes':path.stat().st_size,
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'arch_elf':elf['arch'],'bits':elf['bits'],'endian':elf['endian'],
        'vermagic':meta.get('vermagic',[]),
        'modinfo': {k:v for k,v in meta.items() if k in ('name','depends','srcversion','intree','license','compiler')},
        'sections_present':[s for s in ('.symtab','.strtab','.debug_info','.debug_abbrev','.BTF','__versions','__version_ext_crcs','__version_ext_names','.note.gnu.build-id','.comment') if s in sections],
        'section_count':len(sections),
    }
    if '.note.gnu.build-id' in sections:
        out['build_id'] = build_id(sections['.note.gnu.build-id'],elf['prefix'])
    if '.comment' in sections:
        out['compiler_comments'] = [v.decode('utf-8','replace') for v in sections['.comment'].split(b'\0') if v][:10]
    if '__versions' in sections:
        out['modversions'] = decode_modversions(sections['__versions'],elf['prefix'],elf['bits'])
    return out


def main():
    ap=argparse.ArgumentParser(description='P780 read-only kernel module metadata audit')
    ap.add_argument('folder',help='folder containing modules (.ko/.ko.xz/.ko.gz)')
    ap.add_argument('--output',default='p780-modules-audit.json')
    args=ap.parse_args()
    root=Path(args.folder)
    if not root.is_dir():
        ap.error('Folder does not exist: '+str(root))
    paths = sorted({p for pat in ('*.ko','*.ko.xz','*.ko.gz') for p in root.rglob(pat) if p.is_file()})
    results=[]
    for p in paths:
        try:
            result=scan(p)
            result['relative_path']=str(p.relative_to(root))
        except Exception as e:
            result={'relative_path':str(p.relative_to(root)),'error':str(e)}
        results.append(result)
    report={'mode':'OFFLINE_READ_ONLY', 'warning':'Module information does not establish vmlinux identity, GhostLock exploitability, or kernel symbol addresses.',
            'input_directory':str(root),'files_found':len(paths), 'files_parsed':sum('error' not in r for r in results), 'modules':results}
    Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Found {report["files_found"]} modules; parsed {report["files_parsed"]}; report {args.output}')
    if results:
        for r in results[:12]:
            print(' -',r['relative_path'],(r.get('vermagic') or [''])[0], r.get('error',''))
    else: print('No modules found; this is not an audit failure.')
if __name__=='__main__':
    main()