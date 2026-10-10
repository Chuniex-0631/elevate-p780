# HISTORICAL TOOL; DOES NOT NEED TO BE USED NOW THAT GITHUB ACTIONS IS AVAILABLE.
#!/usr/bin/env bash
# P780 WSL source preparation (research only; NO device/ADB, NO exploit, NO flashing)
set -Eeuo pipefail

usage() {
  cat <<'EOF'
Usage: bash P780-WSL-source-prep.sh '/mnt/c/.../P780-GhostLock-port-v0.4/evidence/p780-config.gz'

Run under WSL Ubuntu. Requires common build dependencies already installed;
clones TinnoOSS/P780, preserves the original on-device kernel config, runs
Kbuild olddefconfig against the historic published vendor tree, and reports
changes. It does NOT compile a kernel, connect to a phone, or run any exploit.
EOF
}
if [[ "${1:-}" == '--help' || "${1:-}" == '-h' ]]; then usage; exit 0; fi
if [[ $# -ne 1 || ! -f "$1" ]]; then usage >&2; exit 2; fi
if ! grep -qi microsoft /proc/sys/kernel/osrelease; then
  echo 'WARNING: this is intended for WSL; continuing under Linux.' >&2
fi
for cmd in git make gzip sha256sum python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing: $cmd. Install packages first: sudo apt install -y git build-essential bc bison flex libssl-dev libelf-dev python3 cpio rsync" >&2
    exit 3
  fi
done
ROOT="${HOME}/p780-kernel-study"
SRC="${ROOT}/P780/msm-5.4"
OUT="${ROOT}/out-vendor-5.4.61"
REPORT="${ROOT}/reports"
mkdir -p "$ROOT" "$OUT" "$REPORT"
cp -f -- "$1" "$ROOT/device-config.gz"
sha256sum "$ROOT/device-config.gz" | tee "$REPORT/device-config.sha256"
gzip -t "$ROOT/device-config.gz"
gzip -dc "$ROOT/device-config.gz" > "$ROOT/device.config.original"

if [[ ! -d "$ROOT/P780/.git" ]]; then
  echo '[1/4] Cloning TinnoOSS/P780. This can be a large download.'
  git clone --depth 1 --single-branch --branch master \
    https://github.com/TinnoOSS/P780.git "$ROOT/P780"
else
  echo '[1/4] Repository already present; no automatic update to keep provenance stable.'
fi
if [[ ! -f "$SRC/Makefile" ]]; then
  echo "Missing kernel Makefile at $SRC" >&2; exit 4
fi

echo '[2/4] Recording source revision, kernel version, and original compiler metadata.'
(
  printf 'Source commit: '; git -C "$ROOT/P780" rev-parse HEAD
  printf 'Source version: '; make -s -C "$SRC" kernelversion
  printf 'Device compiler config: '; grep -m1 '^CONFIG_CC_VERSION_TEXT=' "$ROOT/device.config.original" || true
  printf 'Device LTO: '; grep -m1 '^CONFIG_LTO_CLANG=' "$ROOT/device.config.original" || true
  printf 'Device CFI: '; grep -m1 '^CONFIG_CFI_CLANG=' "$ROOT/device.config.original" || true
  printf 'Host compiler: '; (clang --version 2>/dev/null || gcc --version 2>/dev/null || true) | head -1
) | tee "$REPORT/provenance.txt"

# Make a fresh output dir. Preserve old logs; do not overwrite source files.
cp -f "$ROOT/device.config.original" "$OUT/.config"
echo '[3/4] Running historic vendor Kconfig olddefconfig (not kernel build).'
if ! make -C "$SRC" O="$OUT" ARCH=arm64 olddefconfig > "$REPORT/olddefconfig.log" 2>&1; then
  echo 'Kconfig failed; check reports/olddefconfig.log. Device data is untouched.' >&2
  tail -40 "$REPORT/olddefconfig.log" >&2
  exit 5
fi

echo '[4/4] Comparing resulting 5.4.61 configuration with the real 5.4.233 config.'
(diff -u "$ROOT/device.config.original" "$OUT/.config" || true) > "$REPORT/olddefconfig.diff"
python3 - "$ROOT/device.config.original" "$OUT/.config" > "$REPORT/config-summary.txt" <<'PY'
from pathlib import Path
import sys

def load(path):
    d = {}
    for line in Path(path).read_text(errors='replace').splitlines():
        if line.startswith('CONFIG_') and '=' in line:
            key, value = line.split('=', 1)
            d[key] = value
        elif line.startswith('# CONFIG_') and line.endswith(' is not set'):
            d[line[2:].split(' ',1)[0]] = 'n'
    return d
A, B = load(sys.argv[1]), load(sys.argv[2])
changed = [(k,A[k],B[k]) for k in A.keys() & B.keys() if A[k] != B[k]]
missing = sorted(A.keys() - B.keys())
added = sorted(B.keys() - A.keys())
print('Running kernel config symbols:', len(A))
print('Published vendor config symbols:',len(B))
print('Value changed:',len(changed))
print('Absent from published tree:',len(missing))
print('New in published tree:',len(added))
for k in ['CONFIG_FUTEX_PI','CONFIG_RT_MUTEXES','CONFIG_ASHMEM','CONFIG_CFI_CLANG','CONFIG_LTO_CLANG','CONFIG_MODVERSIONS','CONFIG_DEBUG_INFO_DWARF4']:
    print(f'{k}: actual={A.get(k,"<missing>")}; reconstructed={B.get(k,"<missing>")}')
print('Important: Kconfig success does NOT mean exact binary or vulnerability validation.')
PY
cat "$REPORT/config-summary.txt"
echo
printf 'Done. Output: %s\n' "$REPORT"
printf 'Please share config-summary.txt and (if needed) olddefconfig.log, olddefconfig.diff.\n'