"""Find call sites of an imported symbol inside an aarch64 ELF.

Resolves the PLT stub that forwards to the symbol (via .rela.plt), then finds
every BL that targets that stub and reports which function contains it, using
the symbol table recovered from .gnu_debugdata when present.
"""
from __future__ import annotations

import lzma
import struct
import sys
from pathlib import Path

DT = {"x": lambda s: int(s, 0)}


def load(path: Path):
    d = path.read_bytes()
    e_shoff, = struct.unpack_from("<Q", d, 0x28)
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", d, 0x3A)
    secs = []
    for i in range(e_shnum):
        o = e_shoff + i * e_shentsize
        name, typ, flags, addr, offset, size, link, info, align, entsize = struct.unpack_from(
            "<IIQQQQIIQQ", d, o)
        secs.append(dict(name=name, typ=typ, flags=flags, addr=addr, offset=offset,
                         size=size, link=link, entsize=entsize))
    shstr = secs[e_shstrndx]

    def nm(i):
        s = shstr["offset"] + i
        e = d.index(b"\0", s)
        return d[s:e].decode("utf-8", "replace")

    for s in secs:
        s["nm"] = nm(s["name"])
    return d, secs


def sec(d, secs, name):
    for s in secs:
        if s["nm"] == name:
            return s
    return None


def symbols(d, secs):
    out = []
    for s in secs:
        if s["typ"] not in (2, 11) or not s["entsize"]:
            continue
        strtab = secs[s["link"]]
        blob = d[s["offset"]:s["offset"] + s["size"]]
        for i in range(0, len(blob), s["entsize"]):
            st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack_from(
                "<IBBHQQ", blob, i)
            if not st_name:
                continue
            st = strtab["offset"] + st_name
            en = d.index(b"\0", st)
            out.append((d[st:en].decode("utf-8", "replace"), st_value, st_size, st_shndx,
                        (st_info >> 4) & 0xF))
    return out


def plt_map(d, secs):
    """Map PLT stub address -> imported symbol name."""
    out = {}
    rela = sec(d, secs, ".rela.plt")
    plt = sec(d, secs, ".plt")
    got = sec(d, secs, ".got.plt")
    if not rela or not plt:
        return out
    dyn = sec(d, secs, ".dynsym")
    strtab = secs[dyn["link"]]
    entries = rela["size"] // rela["entsize"]
    for i in range(entries):
        r_offset, r_info, _ = struct.unpack_from("<QQq", d, rela["offset"] + i * rela["entsize"])
        sym_idx = r_info >> 32
        st_name, = struct.unpack_from("<I", d, dyn["offset"] + sym_idx * dyn["entsize"])
        st = strtab["offset"] + st_name
        en = d.index(b"\0", st)
        name = d[st:en].decode("utf-8", "replace")
        # PLT entry i+1 (first entry is the resolver stub), 16 bytes each
        out[plt["addr"] + 16 * (i + 1)] = name
    return out


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit("usage: trace_calls.py <binary> <symbol-substring>")
    path, needle = Path(sys.argv[1]), sys.argv[2]
    d, secs = load(path)

    syms = symbols(d, secs)
    plt = plt_map(d, secs)
    # Resolve PLT stubs whose import matches the needle
    targets = {addr: name for addr, name in plt.items() if needle in name}
    if not targets:
        sys.exit("symbol not imported")
    print("PLT stubs:", {hex(a): n for a, n in targets.items()})

    text = sec(d, secs, ".text")
    blob = d[text["offset"]:text["offset"] + text["size"]]
    words = struct.unpack_from(f"<{len(blob) // 4}I", blob)
    calls = []
    for i, w in enumerate(words):
        if (w & 0xFC000000) == 0x94000000:      # BL
            imm = w & 0x03FFFFFF
            if imm & (1 << 25):
                imm -= (1 << 26)
            tgt = text["addr"] + i * 4 + imm * 4
            if tgt in targets:
                calls.append(text["addr"] + i * 4)
    print(f"{len(calls)} call(s) to {needle}")

    # Map to containing functions using the debugdata symtab when available
    dd = sec(d, secs, ".gnu_debugdata")
    funcs = []
    if dd:
        try:
            dec = lzma.decompress(d[dd["offset"]:dd["offset"] + dd["size"]])
            tmp = Path(str(path) + ".debug.elf")
            tmp.write_bytes(dec)
            d2, secs2 = load(tmp)
            for name, value, size, shndx, info in symbols(d2, secs2):
                if shndx != 0 and info == 2 and size > 0:
                    funcs.append((value, size, name))
            print(f"symtab from gnu_debugdata: {len(funcs)} functions")
        except Exception as exc:
            print("debugdata parse failed:", exc)

    for call in calls:
        owner = "(unknown)"
        for value, size, name in funcs:
            if value <= call < value + size:
                owner = f"{name[:80]} +0x{call - value:x}"
                break
        print(f"  call at {call:#x}  in {owner}")


if __name__ == "__main__":
    main()
