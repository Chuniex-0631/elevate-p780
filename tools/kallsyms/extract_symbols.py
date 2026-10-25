"""Reconstruct a kernel symbol table from a raw arm64 Image plus /proc/kallsyms.

Inputs:
  image        raw Image extracted from the boot partition
  kallsyms     /proc/kallsyms captured from the same boot (addresses may be 0)

Method:
  * /proc/kallsyms preserves the kernel's symbol order
  * kallsyms_offsets in the Image is a long non-decreasing u32 array
  * the entry right after it is kallsyms_num_syms, then the packed names blob
  * pairing names[i] with offsets[i] must stay non-decreasing; we verify it

Usage:
  python extract_symbols.py <Image> <kallsyms.txt> [out.txt]
"""
from __future__ import annotations

import struct
import sys
from array import array
from pathlib import Path


def find_offsets_array(image: bytes) -> tuple[int, int]:
    """Return (offset of the array, number of entries) of kallsyms_offsets."""
    vals = array("I")
    vals.frombytes(image[: (len(image) // 4) * 4])
    n = len(vals)
    best_len, best_start = 0, 0
    run_start, run_len, prev = 0, 1, vals[0]
    for i in range(1, n):
        v = vals[i]
        if v >= prev and (v - prev) < (1 << 24):
            run_len += 1
        else:
            if run_len > best_len:
                best_len, best_start = run_len, run_start
            run_start, run_len = i, 1
        prev = v
    if run_len > best_len:
        best_len, best_start = run_len, run_start
    return best_start * 4, best_len


def main() -> None:
    image_path = Path(sys.argv[1])
    kallsyms_path = Path(sys.argv[2])
    out_path = Path(sys.argv[3]) if len(sys.argv) > 3 else image_path.with_suffix(".symbols.txt")

    image = image_path.read_bytes()
    start, count = find_offsets_array(image)
    print(f"offsets array at {start:#x}, run length {count}")

    # num_syms sits shortly after the array (padding + u64)
    num_syms = None
    for delta in range(0, 64, 4):
        val, = struct.unpack_from("<Q", image, start + count * 4 + delta)
        if 100_000 < val < 400_000:
            num_syms = val
            print(f"num_syms candidate {val} at {start + count*4 + delta:#x}")
            break

    names = [line.split()[-1] for line in kallsyms_path.read_text(errors="replace").splitlines()
             if line.strip()]
    offsets = array("I")
    offsets.frombytes(image[start:start + count * 4])
    n = min(len(names), len(offsets))

    prev = -1
    for i in range(n):
        if offsets[i] < prev:
            raise SystemExit(f"order mismatch at index {i} ({names[i]})")
        prev = offsets[i]

    out_path.write_text("\n".join(f"{offsets[i]:08x} {names[i]}" for i in range(n)) + "\n",
                        encoding="utf-8")
    print(f"wrote {out_path} with {n} symbols (num_syms={num_syms})")


if __name__ == "__main__":
    main()
