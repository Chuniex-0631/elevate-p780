"""Extract ASCII/UTF-16LE strings from a firmware blob and flag keywords."""
from __future__ import annotations

import re
import sys
from pathlib import Path

KW = [
    "fastboot", "unlock", "oem", "edl", "dload", "ffbm", "factory",
    "recovery", "set-gpu", "set-hw", "sahara", "firehose", "devinfo",
    "rpmb", "misc", "boot-mode", "boot_mode", "power", "charge", "qmmi",
    "ftm", "diag", "secure", "verified", "avb", "slot", "unlock_ability",
    "flashing", "erase", "format", "download", "partition", "reboot",
]


def main():
    p = Path(sys.argv[1])
    data = p.read_bytes()
    asc = [m.group().decode("ascii", "replace") for m in re.finditer(rb"[\x20-\x7e]{4,}", data)]
    utf = [m.group().decode("utf-16le", "replace") for m in re.finditer(rb"(?:[\x20-\x7e]\x00){4,}", data)]
    lines = []
    seen = set()
    for s in asc + utf:
        if s not in seen:
            seen.add(s)
            lines.append(s)
    out = p.with_suffix(p.suffix + ".strings.txt")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"{p}: {len(asc)} ascii, {len(utf)} utf16, {len(lines)} unique -> {out}")
    hits = []
    for s in lines:
        low = s.lower()
        if any(k in low for k in KW):
            hits.append(s)
    print(f"keyword hits: {len(hits)}")
    for s in hits[:400]:
        print(s[:300])


if __name__ == "__main__":
    main()
