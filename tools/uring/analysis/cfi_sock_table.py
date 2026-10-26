#!/usr/bin/env python3
"""Decode the arm64 CFI canonical jump table for `void (*)(struct sock *)`
found in __sk_destruct: base 0xffffffc0114dea48, 0x56 entries of 4 bytes.
Each entry is expected to be a `b <target>` stub (opcode 0x14xxxxxx).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kdis

BASE = 0xffffffc0114dea48
N = 0x56

# symbol lookup by exact address
BYADDR = {}
for name, lst in kdis.SYMS.items():
    for a, t in lst:
        BYADDR.setdefault(a, []).append(name)

print('table @ %#x entries=%d' % (BASE, N))
for i in range(N):
    a = BASE + i * 4
    w = int.from_bytes(kdis.read(a, 4), 'little')
    if (w >> 26) == 0b000101:  # b
        imm = w & 0x3ffffff
        if imm & 0x2000000:
            imm -= 0x4000000
        tgt = a + imm * 4
        names = BYADDR.get(tgt, [])
        nm = names[0] if names else '?'
        print('%3d  %#x  b %#x  %s' % (i, a, tgt, nm))
    else:
        print('%3d  %#x  raw %08x  (not b)' % (i, a, w))
