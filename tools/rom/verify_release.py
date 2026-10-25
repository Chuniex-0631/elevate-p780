#!/usr/bin/env python3
"""Offline P780 Release verifier. Standard-library only; no extraction or device access."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile

CHUNK = 8 * 1024 * 1024
TARS = ("system.tar", "product.tar", "system_ext.tar", "vendor.tar", "meta1.tar")


def hash_parts(paths, output=None):
    h = hashlib.sha256()
    size = 0
    dest = output.open("xb") if output else None
    try:
        for path in paths:
            with path.open("rb") as source:
                while block := source.read(CHUNK):
                    h.update(block)
                    size += len(block)
                    if dest:
                        dest.write(block)
    except BaseException:
        if dest:
            dest.close()
            output.unlink(missing_ok=True)
        raise
    finally:
        if dest and not dest.closed:
            dest.close()
    return size, h.hexdigest()


class PartsReader:
    def __init__(self, paths):
        self.paths = iter(paths)
        self.current = None
        self.advance()

    def advance(self):
        if self.current:
            self.current.close()
        path = next(self.paths, None)
        self.current = path.open("rb") if path else None

    def read(self, n=-1):
        blocks = []
        remaining = n
        while self.current and (n < 0 or remaining > 0):
            b = self.current.read(CHUNK if n < 0 else remaining)
            if not b:
                self.advance()
                continue
            blocks.append(b)
            if n >= 0:
                remaining -= len(b)
        return b"".join(blocks)

    def close(self):
        if self.current:
            self.current.close()


def manifest_sections(path):
    sections = {}
    name = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        if line.startswith("### "):
            match = re.fullmatch(r"### (\S+)\s+\((\d+) bytes, (\d+) files\)", line)
            if not match:
                raise ValueError(f"invalid section: {line}")
            name, size, count = match.groups()
            if name in sections:
                raise ValueError(f"duplicate section: {name}")
            sections[name] = {"size": int(size), "count": int(count), "files": {}}
            continue
        match = re.fullmatch(r"\s*(\d+)\s+(.+)", line)
        if not match or name is None:
            raise ValueError(f"invalid manifest item: {line}")
        size, filename = match.groups()
        if filename in sections[name]["files"]:
            raise ValueError(f"duplicate path: {filename}")
        sections[name]["files"][filename] = int(size)
    for section, values in sections.items():
        if len(values["files"]) != values["count"]:
            raise ValueError(f"count mismatch: {section}")
    return sections


def safe_path(path):
    p = PurePosixPath(path)
    return not p.is_absolute() and ".." not in p.parts and "\\" not in path


def audit_tar(paths, expected):
    reader = PartsReader(paths)
    seen = set()
    failures = []
    all_entries = 0
    try:
        with tarfile.open(fileobj=reader, mode="r|") as archive:
            for member in archive:
                all_entries += 1
                if not safe_path(member.name):
                    failures.append(f"unsafe archive member: {member.name}")
                if (member.issym() or member.islnk()) and not safe_path(member.linkname):
                    failures.append(f"unsafe link target: {member.name} -> {member.linkname}")
                if not member.isfile():
                    continue
                if member.name in seen:
                    failures.append(f"duplicate regular file: {member.name}")
                seen.add(member.name)
                want = expected.get(member.name)
                if want is None:
                    failures.append(f"unexpected regular file: {member.name}")
                elif member.size != want:
                    failures.append(f"size mismatch: {member.name}: {member.size} != {want}")
    finally:
        reader.close()
    failures.extend(f"missing regular file: {p}" for p in sorted(set(expected) - seen))
    return all_entries, failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("asset_dir", type=Path, help="directory containing seven downloaded Release assets")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--merge-product", action="store_true",
                        help="create product.tar by concatenating two parts; never overwrite it")
    args = parser.parse_args()
    assets = args.asset_dir.resolve()
    docs = args.repo_root / "docs" / "rom"
    manifest = manifest_sections(docs / "file-manifest.txt")
    release = json.loads((docs / "release-assets.json").read_text(encoding="utf-8"))
    sums = {}
    for line in (docs / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})\s+(.+)", line)
        if match:
            sums[match.group(2)] = match.group(1)
    failures = []
    for name, (want_size, want_hash) in release.items():
        source = assets / name
        if not source.is_file():
            failures.append(f"missing Release asset: {name}")
            continue
        size, digest = hash_parts([source])
        if (size, digest) != (want_size, want_hash):
            failures.append(f"SHA-256 or size mismatch: {name}")
        else:
            print(f"[PASS] {name}: SHA-256 and size ({size:,} bytes)")
    parts = [assets / "product.tar.part1", assets / "product.tar.part2"]
    product = assets / "product.tar"
    if all(x.is_file() for x in parts):
        if args.merge_product and not product.exists():
            size, digest = hash_parts(parts, product)
            print(f"[INFO] Created {product} ({size:,} bytes)")
        else:
            size, digest = hash_parts([product] if product.is_file() else parts)
        if (size, digest) != (manifest["product.tar"]["size"], sums.get("product.tar")):
            failures.append("reconstructed product.tar size / SHA-256 mismatch")
        else:
            print(f"[PASS] product.tar reconstructed SHA-256 and size ({size:,} bytes)")
        if product.exists() and args.merge_product and hash_parts(parts)[1] != hash_parts([product])[1]:
            failures.append("existing product.tar differs from part1 + part2")
    elif args.merge_product:
        failures.append("cannot merge product.tar: parts missing")
    for name in TARS:
        expected = manifest.get(name)
        if expected is None:
            failures.append(f"missing manifest section: {name}")
            continue
        sources = ([product] if product.is_file() else parts) if name == "product.tar" else [assets / name]
        if not all(p.is_file() for p in sources):
            failures.append(f"cannot inspect TAR {name}: local file missing")
            continue
        try:
            entries, issues = audit_tar(sources, expected["files"])
            failures.extend(f"{name}: {msg}" for msg in issues)
            if not issues:
                print(f"[PASS] {name}: {len(expected['files']):,} regular files / {entries:,} TAR entries")
        except (OSError, EOFError, tarfile.TarError) as exc:
            failures.append(f"invalid TAR {name}: {exc}")
    if failures:
        print("\nINCOMPLETE / FAILED:", file=sys.stderr)
        for problem in failures:
            print("- " + problem, file=sys.stderr)
        return 1
    print("\nSUCCESS: all seven assets, reconstructed product and TAR inventories checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
