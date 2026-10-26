#!/usr/bin/env python3
"""Disassemble functions from the recovered P780 kernel image.

Usage:
  python kdis.py <symbol-or-offset> [count] [--from-file f]
  python kdis.py --range 0xADDR 0xNBYTES
Symbols are resolved from 27-symbol-recovery.../kernel.kallsyms.
Addresses are static (link base 0xffffffc010080000).
"""
import sys, os, struct, bisect
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '.tools'))
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
KSYM = os.path.join(ROOT, '27-symbol-recovery-20261025', 'P780-kernel-symbol-recovery', 'kernel.kallsyms')
ELF = os.path.join(ROOT, '27-symbol-recovery-20261025', 'P780-kernel-symbol-recovery', 'kernel.symbolized.elf')
KBASE = 0xffffffc010080000
IMGOFF = 0x1000

def load_syms():
    syms = {}
    order = []
    with open(KSYM, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            p = line.split()
            if len(p) < 3:
                continue
            try:
                a = int(p[0], 16)
            except ValueError:
                continue
            syms.setdefault(p[2], []).append((a, p[1]))
            order.append((a, p[2]))
    order.sort()
    return syms, order

SYMS, ORDER = load_syms()

with open(ELF, 'rb') as f:
    IMG = f.read()

def read(addr, n):
    off = IMGOFF + (addr - KBASE)
    if off < 0 or off + n > len(IMG):
        raise ValueError('address out of image: %#x' % addr)
    return IMG[off:off + n]

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = False

def dis(addr, n):
    code = read(addr, n)
    for ins in md.disasm(code, addr):
        line = '  %016x:  %-8s %s' % (ins.address, ins.mnemonic, ins.op_str)
        print(line)
        if ins.mnemonic == 'ret' or (ins.mnemonic == 'b' and ins.op_str == 'x30'):
            pass

def resolve(tok):
    if tok.startswith('0x') or tok.startswith('ffffff'):
        return int(tok, 16)
    if tok in SYMS:
        return SYMS[tok][0][0]
    cands = [(a, n) for a, n in ORDER if tok in n]
    if len(cands) == 1:
        return cands[0][0]
    if not cands:
        raise SystemExit('symbol not found: %s' % tok)
    print('ambiguous: %s' % tok)
    for a, n in cands[:30]:
        print('  %016x %s' % (a, n))
    raise SystemExit(2)

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    if args[0] == '--range':
        a = int(args[1], 16); n = int(args[2], 16)
        dis(a, n); return
    addr = resolve(args[0])
    n = int(args[1], 0) if len(args) > 1 else 0x400
    print('; %s @ %#x (%d bytes)' % (args[0], addr, n))
    dis(addr, n)

if __name__ == '__main__':
    main()
