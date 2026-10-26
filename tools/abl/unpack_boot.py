"""Parse an Android boot image, extract the ramdisk, list cpio entries.

Usage: python unpack_boot.py <boot.img> [outdir]

Handles header v0-v4 layout used by Android 11 (v3/v4) well enough to pull
the boot ramdisk; extracts gzip ramdisks and lists newc cpio entries.
"""
from __future__ import annotations

import gzip
import os
import struct
import sys
from pathlib import Path


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def align(x: int, p: int) -> int:
    return (x + p - 1) // p * p


def parse_header(b: bytes):
    if b[:8] != b"ANDROID!":
        raise SystemExit("not an Android boot image (magic mismatch)")
    ver = u32(b, 40)
    if ver >= 3:
        kernel_size = u32(b, 8)
        ramdisk_size = u32(b, 12)
        os_version = u32(b, 16)
        header_size = u32(b, 20)
        page_size = 4096
        cmdline = b[44:44 + 1536].split(b"\0")[0]
    else:
        kernel_size = u32(b, 8)
        ramdisk_size = u32(b, 16)
        page_size = u32(b, 36)
        header_size = 1632
        os_version = 0
        cmdline = b[64:64 + 512].split(b"\0")[0]
    return ver, kernel_size, ramdisk_size, page_size, header_size, os_version, cmdline


def cpio_list(data: bytes, outdir: Path | None):
    off = 0
    entries = []
    while off + 110 <= len(data):
        magic = data[off:off + 6]
        if magic not in (b"070701", b"070702"):
            break
        f = [int(data[off + 6 + 8 * i: off + 6 + 8 * (i + 1)], 16) for i in range(13)]
        namesize, filesize = f[11], f[6]
        name = data[off + 110:off + 110 + namesize - 1]
        off = align(off + 110 + namesize, 4)
        body = data[off:off + filesize]
        off = align(off + filesize, 4)
        if name == b"TRAILER!!!":
            break
        entries.append((name.decode("utf-8", "replace"), filesize))
        if outdir is not None:
            nm = name.decode("utf-8", "replace")
            p = outdir / nm
            try:
                kind = f[1] & 0o170000
                if kind == 0o040000:          # directory
                    p.mkdir(parents=True, exist_ok=True)
                elif kind == 0o120000:        # symlink: store target text
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(body.decode("utf-8", "replace"), encoding="utf-8")
                else:                         # regular file
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(body)
            except OSError:
                pass
    return entries


def main():
    src = Path(sys.argv[1])
    outdir = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".unpacked")
    outdir.mkdir(parents=True, exist_ok=True)
    b = src.read_bytes()
    ver, ks, rs, ps, hs, osv, cmd = parse_header(b)
    print(f"header_version={ver} kernel_size={ks} ramdisk_size={rs} "
          f"page_size={ps} header_size={hs} os_version={osv:#x}")
    print(f"cmdline={cmd.decode('utf-8', 'replace')!r}")
    koff = ps
    roff = ps + align(ks, ps)
    print(f"kernel@{koff:#x} ramdisk@{roff:#x} image_size={len(b):#x}")
    if roff + rs > len(b):
        print(f"WARNING: ramdisk extends past image ({roff + rs:#x} > {len(b):#x})")
    rd = b[roff:roff + rs]
    (outdir / "ramdisk.img").write_bytes(rd)
    print(f"wrote ramdisk.img ({len(rd)} bytes)")
    if rd[:2] == b"\x1f\x8b":
        cpio = gzip.decompress(rd)
        (outdir / "ramdisk.cpio").write_bytes(cpio)
        print(f"gzip -> ramdisk.cpio ({len(cpio)} bytes)")
    elif rd[:4] == b"\x04\x22\x4d\x18":
        print("ramdisk is lz4; need lz4/magiskboot to decompress")
        return
    elif rd[:4] == b"\x28\xb5\x2f\xfd":
        print("ramdisk is zstd; need zstd to decompress")
        return
    else:
        cpio = rd
        print("ramdisk looks uncompressed")
    entries = cpio_list(cpio, outdir / "root")
    print(f"cpio entries: {len(entries)}")
    for name, size in entries:
        print(f"  {size:>9}  {name}")


if __name__ == "__main__":
    main()
