"""Build a hook patch plan for a chosen target library (offline only).

Usage:
    python build_patch.py [libcxx|libbase]

Targets:
    libcxx  - /system/lib64/libc++.so, entry = ostream sentry ctor
    libbase - /system/lib64/libbase.so, entry = LogMessage ctor (installd calls it)

Outputs build/target.json plus hook_entry.bin / hook_stub.bin / patch_plan.json.
Nothing here touches the device.
"""
from __future__ import annotations

import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
CPP = ROOT / "probe-src" / "app" / "src" / "main" / "cpp"
NDK_BIN = (ROOT / "sdk" / "ndk" / "26.3.11579264" / "toolchains" / "llvm"
           / "prebuilt" / "windows-x86_64" / "bin")
LOCAL = ROOT.parent / "22-netd-hook-20261025"

TARGETS = {
    "libcxx": {
        "lib": "/system/lib64/libc++.so",
        "local": ROOT.parent / "20" / "P780-libc++.so",
        "entry": 0x62FB4,
        "victim": 0x790B0,
    },
    "libbase": {
        "lib": "/system/lib64/libbase.so",
        "local": LOCAL / "libbase.so",
        "entry": 0x12D60,      # android::base::LogMessage::LogMessage(...)
        "victim": 0x19ED4,     # fmt::v6::internal::format_float<double>
        "stub": "stub.S",
    },
    "libbase_noop": {
        "lib": "/system/lib64/libbase.so",
        "local": LOCAL / "libbase.so",
        "entry": 0x12D60,
        "victim": 0x19ED4,
        "stub": "stub_noop.S",
    },
}

ENTRY_LEN = 16


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"command failed: {' '.join(cmd)}\n{proc.stdout}\n{proc.stderr}")
    return proc.stdout


def find_stub_layout(obj: Path) -> tuple[int, int, int]:
    dis = run([str(NDK_BIN / "llvm-objdump.exe"), "-d", str(obj)])
    stolen: list[int] = []
    jump = None
    for line in dis.splitlines():
        s = line.strip()
        if ":" not in s:
            continue
        try:
            addr = int(s.split(":")[0].strip(), 16)
        except ValueError:
            continue
        body = s.split("\t", 1)[-1].strip()
        if body.startswith(".word") and "d503201f" in body:
            stolen.append(addr)
        if jump is None and body.startswith("adrp") and "x9" in body:
            jump = addr
    if not stolen or jump is None:
        sys.exit("could not locate stub placeholders")
    stolen_off = min(stolen)
    # Blob length must cover the strings after the jump, so take the address of
    # the next symbol (the self-test stub) as the end of the production blob.
    symtab = run([str(NDK_BIN / "llvm-readelf.exe"), "-sW", str(obj)])
    end = None
    for line in symtab.splitlines():
        if "p780_stub_test" in line and "FUNC" in line:
            parts = line.split()
            end = int(parts[1], 16)
            break
    if end is None:
        sys.exit("could not find p780_stub_test symbol")
    blob_len = end
    return blob_len, stolen_off, jump


def main() -> None:
    target_name = sys.argv[1] if len(sys.argv) > 1 else "libcxx"
    if target_name not in TARGETS:
        sys.exit(f"unknown target {target_name}")
    target = TARGETS[target_name]
    entry = target["entry"]
    victim = target["victim"]

    BUILD.mkdir(exist_ok=True)
    clang = NDK_BIN / "clang.exe"

    stub_obj = BUILD / "stub.o"
    run([str(clang), "--target=aarch64-linux-android30", "-c",
         str(CPP / target.get("stub", "stub.S")), "-o", str(stub_obj)])
    blob_len, stolen_off, jump_off = find_stub_layout(stub_obj)

    stub_raw = BUILD / "stub.raw"
    run([str(NDK_BIN / "llvm-objcopy.exe"), "-O", "binary", "--only-section=.text",
         str(stub_obj), str(stub_raw)])
    blob = bytearray(stub_raw.read_bytes()[:blob_len])

    lib = Path(target["local"]).read_bytes()
    stolen = lib[entry:entry + ENTRY_LEN]
    blob[stolen_off:stolen_off + 16] = stolen

    pc_page = entry & ~0xFFF
    target_page = victim & ~0xFFF
    pages = (target_page - pc_page) >> 12
    adrp = 0x90000010 | ((pages & 0x3) << 29) | (((pages >> 2) & 0x7FFFF) << 5)
    add = 0x91000010 | (16 << 5) | ((victim & 0xFFF) << 10)
    entry_bytes = struct.pack("<IIII", adrp, add, 0xD61F0200, 0xD503201F)
    (BUILD / "hook_entry.bin").write_bytes(entry_bytes)

    ret_target = entry + ENTRY_LEN
    pc_adrp = victim + jump_off
    pages2 = ((ret_target & ~0xFFF) - (pc_adrp & ~0xFFF)) >> 12
    adrp2 = 0x90000009 | ((pages2 & 0x3) << 29) | (((pages2 >> 2) & 0x7FFFF) << 5)
    add2 = 0x91000009 | (9 << 5) | ((ret_target & 0xFFF) << 10)
    struct.pack_into("<II", blob, jump_off, adrp2, add2)
    (BUILD / "hook_stub.bin").write_bytes(blob)

    def blocks(base: int, payload: bytes, label: str) -> list[dict]:
        out = []
        for i in range(0, len(payload), 16):
            chunk = payload[i:i + 16]
            if len(chunk) < 16:
                chunk = (chunk + b"\x1f\x20\x03\xd5" * 4)[:16]
            out.append({"label": label, "offset": base + i, "desired_hex": chunk.hex()})
        return out

    plan = blocks(victim, bytes(blob), "stub") + blocks(entry, entry_bytes, "entry")
    meta = {
        "target": target_name,
        "lib": target["lib"],
        "entry": entry,
        "victim": victim,
        "prologue_hex": stolen.hex(),
        "stub_bytes": len(blob),
        "stolen_off": stolen_off,
        "jump_off": jump_off,
    }
    (BUILD / "target.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (BUILD / "patch_plan.json").write_text(
        json.dumps({**meta, "blocks": plan}, indent=2), encoding="utf-8")

    print(f"target={target_name} lib={target['lib']}")
    print(f"entry=0x{entry:x} victim=0x{victim:x} stub={len(blob)}B "
          f"({len(plan) - 1} stub blocks + 1 entry block)")
    print(f"prologue={stolen.hex()}")
    print(f"entry bytes={entry_bytes.hex()}")


if __name__ == "__main__":
    main()
