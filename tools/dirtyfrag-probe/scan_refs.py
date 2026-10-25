"""Offline reference scanner for aarch64 ELF binaries.

For a candidate function address it reports every place that can reach it:
  * direct b/bl immediate branches inside .text
  * adrp + add pairs forming the address
  * adrp + ldr pairs whose literal slot holds the address
  * R_AARCH64_RELATIVE relocation addends (function pointer tables)
  * raw 8-byte occurrences of the address in data sections

With --candidates it also lists functions of a minimum size and ranks them by
reference count, so a victim for stub placement can be chosen safely.
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

MASK = (1 << 64) - 1


class Elf:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = path.read_bytes()
        d = self.data
        if d[:4] != b"\x7fELF" or d[4] != 2:
            raise SystemExit("not a 64-bit ELF")
        e_shoff, = struct.unpack_from("<Q", d, 0x28)
        e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", d, 0x3A)
        self.secs = []
        for i in range(e_shnum):
            off = e_shoff + i * e_shentsize
            name, typ, flags, addr, offset, size, link, info, align, entsize = struct.unpack_from(
                "<IIQQQQIIQQ", d, off)
            self.secs.append(dict(name=name, typ=typ, flags=flags, addr=addr, offset=offset,
                                  size=size, link=link, entsize=entsize))
        shstr = self.secs[e_shstrndx]

        def name_of(idx: int) -> str:
            start = shstr["offset"] + idx
            end = d.index(b"\0", start)
            return d[start:end].decode("utf-8", "replace")

        for s in self.secs:
            s["nm"] = name_of(s["name"])

    def by_name(self, name: str):
        for s in self.secs:
            if s["nm"] == name:
                return s
        return None

    def section_bytes(self, sec) -> bytes:
        return self.data[sec["offset"]:sec["offset"] + sec["size"]]

    def relocations(self):
        """Yield (offset, type, symbol, addend) for RELA sections."""
        for s in self.secs:
            if s["typ"] != 4 or not s["entsize"]:      # SHT_RELA
                continue
            blob = self.section_bytes(s)
            for i in range(0, len(blob), s["entsize"]):
                r_offset, r_info, r_addend = struct.unpack_from("<QQq", blob, i)
                yield r_offset, r_info & 0xFFFFFFFF, r_info >> 32, r_addend

    def symbols(self):
        for s in self.secs:
            if s["typ"] not in (2, 11) or not s["entsize"]:
                continue
            blob = self.section_bytes(s)
            strtab = self.secs[s["link"]]
            for i in range(0, len(blob), s["entsize"]):
                st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack_from(
                    "<IBBHQQ", blob, i)
                if not st_name:
                    continue
                start = strtab["offset"] + st_name
                end = self.data.index(b"\0", start)
                yield (self.data[start:end].decode("utf-8", "replace"),
                       st_value, st_size, st_shndx, (st_info >> 4) & 0xF)


def decode_branch(word: int) -> int | None:
    """Return the signed byte offset for B/BL, else None."""
    if (word & 0x7C000000) == 0x14000000:      # B
        imm = word & 0x03FFFFFF
    elif (word & 0xFC000000) == 0x94000000:    # BL
        imm = word & 0x03FFFFFF
    else:
        return None
    if imm & (1 << 25):
        imm -= (1 << 26)
    return imm << 2


def decode_adrp(word: int, pc: int) -> int | None:
    if (word & 0x9F000000) != 0x90000000:
        return None
    immlo = (word >> 29) & 0x3
    immhi = (word >> 5) & 0x7FFFF
    imm = (immhi << 2) | immlo
    if imm & (1 << 20):
        imm -= (1 << 21)
    return (pc & ~0xFFF) + (imm << 12)


def scan(elf: Elf, target: int) -> dict:
    text = elf.by_name(".text")
    tb = elf.section_bytes(text)
    base = text["addr"]
    hits = {"branch": [], "adrp_add": [], "adrp_ldr": [], "reloc": [], "raw": []}

    words = struct.unpack_from(f"<{len(tb) // 4}I", tb)
    for i, word in enumerate(words):
        pc = base + i * 4
        off = decode_branch(word)
        if off is not None and pc + off == target:
            hits["branch"].append(pc)
    for i in range(len(words) - 1):
        page = decode_adrp(words[i], base + i * 4)
        if page is None:
            continue
        nxt = words[i + 1]
        if (nxt & 0x7F800000) == 0x11000000:        # ADD (immediate)
            rn = (nxt >> 5) & 0x1F
            rd = nxt & 0x1F
            imm12 = (nxt >> 10) & 0xFFF
            if rn == ((words[i]) & 0x1F) and page + imm12 == target:
                hits["adrp_add"].append(base + i * 4)
        # LDR (unsigned offset, 64-bit) from the same page
        if (nxt & 0xFFC00000) == 0xF9400000:
            rn = (nxt >> 5) & 0x1F
            imm12 = (nxt >> 10) & 0xFFF
            slot = page + imm12 * 8
            if rn == (words[i] & 0x1F):
                for sec in elf.secs:
                    if sec["typ"] == 1 and sec["addr"] <= slot < sec["addr"] + sec["size"]:
                        val, = struct.unpack_from("<Q", elf.data, sec["offset"] + slot - sec["addr"])
                        if val == target:
                            hits["adrp_ldr"].append(base + i * 4)
                        break

    for offset, rtype, sym, addend in elf.relocations():
        if rtype == 1027 and (addend & MASK) == target:   # R_AARCH64_RELATIVE
            hits["reloc"].append(offset)

    needle = struct.pack("<Q", target)
    for sec in elf.secs:
        if sec["typ"] == 1 and sec["nm"] in (".data.rel.ro", ".data", ".rodata", ".got"):
            blob = elf.section_bytes(sec)
            start = 0
            while True:
                idx = blob.find(needle, start)
                if idx < 0:
                    break
                hits["raw"].append(sec["addr"] + idx)
                start = idx + 8
    return hits


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("binary", type=Path)
    ap.add_argument("--target", type=lambda s: int(s, 0))
    ap.add_argument("--candidates", action="store_true")
    ap.add_argument("--min-size", type=int, default=700)
    args = ap.parse_args()

    elf = Elf(args.binary)

    if args.target is not None:
        hits = scan(elf, args.target)
        total = sum(len(v) for v in hits.values())
        print(f"target {args.target:#x}: {total} reference(s)")
        for kind, values in hits.items():
            for v in values[:12]:
                print(f"  {kind}: {v:#x}")
        return

    if args.candidates:
        funcs = {}
        for name, value, size, shndx, info in elf.symbols():
            if shndx != 0 and size >= args.min_size and info == 2:
                funcs[(value, size)] = name
        print(f"{len(funcs)} candidate functions >= {args.min_size} bytes")
        rows = []
        for (value, size), name in funcs.items():
            hits = scan(elf, value)
            rows.append((sum(len(v) for v in hits.values()), size, value, name, hits))
        rows.sort()
        for count, size, value, name, hits in rows[:15]:
            detail = ",".join(f"{k}={len(v)}" for k, v in hits.items() if v)
            print(f"  refs={count:2d} size={size:5d} {value:#08x} {name[:70]} [{detail}]")


if __name__ == "__main__":
    main()
