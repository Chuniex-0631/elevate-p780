"""Verify evidence/20261026/partitions against the 2026-10-25 hash manifest.

The manifest records the byte count and SHA-256 of every file that the original
init-domain dumper produced.  Personal partitions (persist / modemst / fsg / fsc)
are intentionally absent from the public repository, so missing entries are
reported but do not fail the run.  A hash mismatch, or an unlisted file inside
one of the recovered extraction trees, fails with exit code 1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# trees that the 2026-10-26 re-extraction rebuilt; anything unlisted there is a bug
RECOVERED_TREES = ("vendor_boot_a_ramdisk", "vendor_boot_b_ramdisk", "dtbo_a_entries")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", type=Path, default=ROOT / "evidence/20261026/partitions")
    ap.add_argument("--manifest", type=Path,
                    default=ROOT / "evidence/partitions/manifest-20261025.json")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    entries = manifest["files"]
    ok = mismatch = 0
    missing: list[str] = []
    for e in entries:
        p = args.base / e["path"]
        if not p.is_file():
            missing.append(e["path"])
            continue
        data = p.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if len(data) == e["bytes"] and digest == e["sha256"]:
            ok += 1
        else:
            mismatch += 1
            print(f"MISMATCH {e['path']}: {len(data)}/{digest} != {e['bytes']}/{e['sha256']}")

    listed = {e["path"] for e in entries}
    extras: list[str] = []
    for tree in RECOVERED_TREES:
        root = args.base / tree
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if p.is_file():
                rel = p.relative_to(args.base).as_posix()
                if rel not in listed:
                    extras.append(rel)

    print(f"manifest entries: {len(entries)}  ok={ok}  mismatch={mismatch}  "
          f"missing={len(missing)}  extras={len(extras)}")
    if missing and not args.quiet:
        for m in missing:
            print(f"  missing: {m}")
    for x in extras:
        print(f"  extra: {x}")
    return 1 if (mismatch or extras) else 0


if __name__ == "__main__":
    sys.exit(main())
