"""Scan extracted artifacts for keys, credentials and build metadata.

Usage: python scan_secrets.py [--roots a,b] [--json out.json]

The scan is read-only and never prints secret values; it reports paths,
matched pattern names and counts only.  PEM blocks are reported by their
header line (e.g. "RSA PRIVATE KEY"), not by their body.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import zipfile
from pathlib import Path

ROOT = Path(r"C:\Users\ASUS Vivobook\Desktop\RakutenHand5G")

DEFAULT_ROOTS = [
    "48-init-capability-20261025",
    "47-ghostlock-20261025",
    "09",
    "10-oem-unlock",
    "20",
    "01",
    "32-system-extract-20261025",
    "45-elevate-app",
    "44-root-daemon-20261025",
    "46-escalation-20261025",
    "31-installd-root-20261025",
    "30-selinux-policy-20261025",
    "27-symbol-recovery-20261025",
    "25-kernel-dump-20261025",
    "24-next-research-20261025",
    "26-pahole-ci-20261025",
    "28-ghostlock-profile-20261025",
    "29-exec-domain-20261025",
    "33-full-extract-20261025",
    "41-fill-gaps-20261025",
    "42-github-rom-20261025",
    "23-repo-rebuild",
    "19-repository-sync-20261025",
    "14-supplement-20261024",
    "13-dsu-readonly",
    "12-evidence-gaps",
    "11-native-live",
    "07",
    "08",
    "06",
    "05",
    "04",
    "03",
    "02",
    "P780-ROM-20261025",
]

SKIP_PARTS = {
    "sdk", "toolchain", "downloads", "jdk", "zig", ".git", "__pycache__",
    "node_modules", ".gradle", "sdkmanager", "cmdline-tools", "platform-tools",
}

PATTERNS = {
    "pem_begin": re.compile(rb"-----BEGIN ([A-Z0-9 ]{1,40})-----"),
    "private_key": re.compile(rb"PRIVATE KEY"),
    "openssh_key": re.compile(rb"ssh-(rsa|ed25519|dss)"),
    "aws_key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(rb"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "slack_token": re.compile(rb"xox[baprs]-[A-Za-z0-9-]{10,}"),
    "google_api": re.compile(rb"AIza[0-9A-Za-z_-]{35}"),
    "password_kv": re.compile(rb"(?i)pass(word|wd)?\s*[=:]\s*\S{3,}"),
    "secret_kv": re.compile(rb"(?i)secret\s*[=:]\s*\S{3,}"),
    "token_kv": re.compile(rb"(?i)token\s*[=:]\s*\S{3,}"),
    "build_path": re.compile(rb"/(build|home)/[A-Za-z0-9._/-]{3,60}"),
    "build_host": re.compile(rb"[a-zA-Z0-9._-]+@[A-Za-z0-9._-]+"),
    "imei_kw": re.compile(rb"(?i)\b(imei|meid|serialno|serial_no)\b"),
    "testkey_kw": re.compile(rb"(?i)(testkey|test_key|platform\.x509|\.pk8)"),
}

KEY_SUFFIXES = {".pem", ".pk8", ".p12", ".pfx", ".jks", ".keystore", ".key", ".der", ".crt", ".cer"}

MAX_FILE = 64 * 1024 * 1024
CHUNK = 4 * 1024 * 1024


def iter_files(roots):
    for rel in roots:
        base = ROOT / rel
        if not base.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_PARTS]
            for fn in filenames:
                p = Path(dirpath) / fn
                try:
                    if p.is_symlink() or not p.is_file():
                        continue
                except OSError:
                    continue
                yield p


def scan_file(p: Path):
    hits = {}
    try:
        size = p.stat().st_size
    except OSError:
        return hits, 0
    try:
        with p.open("rb") as f:
            read = 0
            while True:
                buf = f.read(CHUNK)
                if not buf:
                    break
                read += len(buf)
                for name, rx in PATTERNS.items():
                    n = len(rx.findall(buf))
                    if n:
                        hits[name] = hits.get(name, 0) + n
                if read >= MAX_FILE:
                    break
    except OSError:
        return hits, size
    return hits, size


def archive_entries(p: Path):
    try:
        with zipfile.ZipFile(p) as z:
            return [n for n in z.namelist() if n.lower().endswith(tuple(KEY_SUFFIXES))]
    except Exception:
        return []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", default="")
    ap.add_argument("--json", default=str(ROOT / "49-artifact-scan-20261025" / "scan.json"))
    args = ap.parse_args()
    roots = [r for r in args.roots.split(",") if r] or DEFAULT_ROOTS

    key_files = []
    results = {}
    archive_hits = {}
    scanned = 0
    for p in iter_files(roots):
        rel = str(p.relative_to(ROOT))
        suffix = p.suffix.lower()
        if suffix in KEY_SUFFIXES:
            key_files.append(rel)
        if suffix in (".apk", ".jar", ".zip") and p.stat().st_size < 80 * 1024 * 1024:
            ents = archive_entries(p)
            if ents:
                archive_hits[rel] = ents[:20]
        hits, size = scan_file(p)
        scanned += 1
        if hits:
            results[rel] = {"size": size, "hits": hits}

    out = {
        "scanned_files": scanned,
        "key_files": sorted(key_files),
        "archive_key_entries": archive_hits,
        "hits": results,
    }
    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("scanned", scanned, "files;", len(results), "with hits;", len(key_files), "key-like files")


if __name__ == "__main__":
    main()
