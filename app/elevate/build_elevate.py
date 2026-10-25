"""Assemble the Elevate APK (resources + dex + native lib) without Gradle."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROBE = ROOT.parent / "21-dirtyfrag-probe-20261025"
CFG = json.loads((PROBE / "toolchain.json").read_text(encoding="utf-8"))
JAVA = Path(CFG["java"])
SDK = Path(CFG["sdk"])
PROJECT = ROOT / "app" / "src" / "main"
BUILD = ROOT / "build"
LOGS = ROOT / "build-logs"
VERSION_CODE = 1
VERSION_NAME = "1.0"


def run(cmd, log_name: str, env: dict | None = None) -> int:
    LOGS.mkdir(parents=True, exist_ok=True)
    log = LOGS / f"{log_name}.log"
    full = os.environ.copy()
    if env:
        full.update(env)
    with open(log, "wb") as fh:
        proc = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT, env=full)
    print(f"{log_name}: exit={proc.returncode}")
    return proc.returncode


def require(path: Path, what: str) -> Path:
    if not path.exists():
        raise SystemExit(f"missing {what}: {path}")
    return path


def main() -> None:
    build_tools = require(SDK / "build-tools" / "30.0.3", "build-tools")
    platform = require(SDK / "platforms" / "android-30" / "android.jar", "android.jar")
    ndk = require(SDK / "ndk" / "26.3.11579264", "NDK")
    javac = require(JAVA.parent / "javac.exe", "javac")
    java = require(JAVA, "java")
    jar = require(JAVA.parent / "jar.exe", "jar")

    BUILD.mkdir(parents=True, exist_ok=True)
    for d in ("classes", "dex", "lib/arm64-v8a", "gen"):
        p = BUILD / d
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True)

    # 1. resources
    rc = run([str(build_tools / "aapt2.exe"), "compile", "--dir", str(PROJECT / "res"),
              "-o", str(BUILD / "res.zip")], "aapt2-compile")
    if rc != 0:
        raise SystemExit("aapt2 compile failed")

    rc = run([str(build_tools / "aapt2.exe"), "link", "-I", str(platform),
              "--manifest", str(PROJECT / "AndroidManifest.xml"),
              "--min-sdk-version", "28", "--target-sdk-version", "30",
              "--version-code", str(VERSION_CODE), "--version-name", VERSION_NAME,
              "-R", str(BUILD / "res.zip"),
              "--java", str(BUILD / "gen"),
              "-A", str(PROJECT / "assets"),
              "-o", str(BUILD / "base.apk")], "aapt2-link")
    if rc != 0:
        raise SystemExit("aapt2 link failed")

    # 2. java
    sources = sorted(str(p) for p in (PROJECT / "java").rglob("*.java"))
    sources += sorted(str(p) for p in (BUILD / "gen").rglob("*.java"))
    rc = run([str(javac), "-encoding", "UTF-8", "--release", "11", "-Xlint:-options", "-nowarn",
              "-classpath", str(platform), "-d", str(BUILD / "classes"), *sources], "javac")
    if rc != 0:
        raise SystemExit("javac failed; see build-logs/javac.log")

    rc = run([str(jar), "cf", str(BUILD / "classes.jar"), "-C", str(BUILD / "classes"), "."], "jar")
    if rc != 0:
        raise SystemExit("jar failed")

    rc = run([str(java), "-cp", str(build_tools / "lib" / "d8.jar"), "com.android.tools.r8.D8",
              "--lib", str(platform), "--min-api", "28", "--output", str(BUILD / "dex"),
              str(BUILD / "classes.jar")], "d8")
    if rc != 0:
        raise SystemExit("d8 failed; see build-logs/d8.log")

    # 3. native
    clang = ndk / "toolchains" / "llvm" / "prebuilt" / "windows-x86_64" / "bin" / "aarch64-linux-android30-clang.cmd"
    require(clang, "NDK clang")
    so = BUILD / "lib" / "arm64-v8a" / "libsendfile_probe.so"
    rc = run([str(clang), "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror", "-DANDROID",
              "-o", str(so), str(PROJECT / "cpp" / "sendfile_probe.c"),
              str(PROJECT / "cpp" / "stub.S")], "clang")
    if rc != 0:
        raise SystemExit("clang failed; see build-logs/clang.log")

    # 4. stage
    staged = BUILD / "staged.apk"
    if staged.exists():
        staged.unlink()
    with zipfile.ZipFile(BUILD / "base.apk") as src, zipfile.ZipFile(staged, "w", zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            dst.writestr(info, src.read(info.filename))
        dst.write(BUILD / "dex" / "classes.dex", "classes.dex")
        dst.write(so, "lib/arm64-v8a/libsendfile_probe.so")

    aligned = BUILD / "aligned.apk"
    rc = run([str(build_tools / "zipalign.exe"), "-f", "-p", "4", str(staged), str(aligned)], "zipalign")
    if rc != 0:
        raise SystemExit("zipalign failed")

    keystore = PROBE / "build" / "debug.keystore"
    require(keystore, "debug keystore")
    out = ROOT / "Elevate.apk"
    if out.exists():
        out.unlink()
    rc = run([str(java), "-jar", str(build_tools / "lib" / "apksigner.jar"), "sign",
              "--ks", str(keystore), "--ks-pass", "pass:android", "--key-pass", "pass:android",
              "--out", str(out), str(aligned)], "apksigner")
    if rc != 0:
        raise SystemExit("apksigner failed")
    print(f"APK: {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
