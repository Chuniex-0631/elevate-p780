"""Offline AArch64 PE audit. Requires capstone; never opens a device.

Addresses in output are PE RVAs (not runtime VAs). ADRP/ADD pairs are
conservative candidates, not a full data-flow analysis or reachability proof.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM


def audit(path):
    original = Path(path).read_bytes()
    image_offset = original.find(b'MZ')
    if image_offset < 0:
        raise ValueError('PE signature not found')
    b = original[image_offset:]
    pe = struct.unpack_from('<I', b, 0x3c)[0]
    if b[:2] != b'MZ' or b[pe:pe+4] != b'PE\0\0':
        raise ValueError('expected unpacked PE image')
    machine, count = struct.unpack_from('<HH', b, pe+4)
    optional_size = struct.unpack_from('<H', b, pe+20)[0]
    if machine != 0xaa64:
        raise ValueError('expected AArch64')
    sections = []
    for n in range(count):
        off = pe+24+optional_size+n*40
        name = b[off:off+8].rstrip(b'\0').decode('ascii')
        vs, rva, size, raw = struct.unpack_from('<IIII', b, off+8)
        flags = struct.unpack_from('<I', b, off+36)[0]
        if raw+size > len(b):
            raise ValueError('truncated section')
        sections.append(dict(name=name, rva=rva, raw=raw, size=size, flags=flags))
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    md.detail = True
    instructions = []
    for s in sections:
        if s['flags'] & 0x20000000:
            # Decode each aligned word so one embedded data word cannot truncate a section.
            for off in range(0, s['size']-3, 4):
                instructions.extend(md.disasm(b[s['raw']+off:s['raw']+off+4], s['rva']+off))
    def text_at(rva):
        for s in sections:
            d = rva-s['rva']
            if 0 <= d < s['size']:
                off = s['raw']+d
                v = b[off:off+160].split(b'\0')[0]
                if len(v) >= 4 and all(32 <= c < 127 or c in (10,13,9) for c in v):
                    return v.decode('ascii')
        return None
    refs = []
    for i, ins in enumerate(instructions):
        if ins.mnemonic not in ('adrp', 'adr'):
            continue
        ops = ins.operands
        if len(ops) != 2:
            continue
        reg, base = ops[0].reg, ops[1].imm
        if ins.mnemonic == 'adr':
            targets = [(ins.address, base)]
        else:
            targets = []
            for step, nxt in enumerate(instructions[i+1:i+7], 1):
                if nxt.address != ins.address+4*step:
                    break
                no = nxt.operands
                if nxt.mnemonic == 'add' and len(no) == 3 and no[1].type == 1 and no[1].reg == reg and no[2].type == 2:
                    targets.append((nxt.address, base+no[2].imm))
                _, writes = nxt.regs_access()
                if reg in writes or nxt.mnemonic in ('b','bl','br','blr','ret'):
                    break
        for at, target in targets:
            txt = text_at(target)
            if txt:
                refs.append(dict(adr=hex(ins.address), at=hex(at), target=hex(target), text=txt))
    return original, image_offset, sections, instructions, refs


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image')
    p.add_argument('--range', nargs=2, metavar=('RVA','BYTES'))
    p.add_argument('--table', nargs=2, metavar=('RVA','COUNT'), help='inspect explicit <command,handler> pointer pairs')
    a = p.parse_args()
    b, image_offset, sections, ins, refs = audit(a.image)
    if a.table:
        start, count = (int(x,0) for x in a.table)
        def raw(rva):
            for s in sections:
                if s['rva'] <= rva < s['rva']+s['size']:
                    return image_offset+s['raw']+rva-s['rva']
            raise ValueError('RVA outside file sections')
        entries = []
        for rva in range(start, start+count*16, 16):
            name, handler = struct.unpack_from('<QQ', b, raw(rva))
            at = raw(name)
            command = b[at:at+128].split(b'\0')[0].decode('ascii')
            executable = any(s['rva'] <= handler < s['rva']+s['size'] and s['flags'] & 0x20000000 for s in sections)
            entries.append(dict(table_rva=hex(rva), command=command, handler_rva=hex(handler), handler_in_executable_section=bool(executable)))
        print(json.dumps(entries, indent=2))
        return
    if a.range:
        start, size = (int(x,0) for x in a.range)
        for x in ins:
            if start <= x.address < start+size:
                print(f'{x.address:08x}: {x.bytes.hex():8} {x.mnemonic:8} {x.op_str}')
        return
    print(json.dumps(dict(sha256=hashlib.sha256(b).hexdigest(), bytes=len(b),
                         pe_file_offset=image_offset, sections=sections, string_references=refs,
                         limitations=['Local ADR/ADRP+ADD candidates only; manually verify register lifetimes.',
                                      'No call-graph completeness or runtime reachability claim.']), indent=2))


if __name__ == '__main__':
    main()
