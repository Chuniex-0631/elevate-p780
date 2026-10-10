# ARCHIVED READ-ONLY INSPECTION UTILITY. CHECK INPUTS AND OUTPUT PATHS BEFORE USE.
#!/usr/bin/env python3
"""P780 / GhostLock local evidence audit.

Offline, read-only inspection of a saved Android kernel configuration,
tracefs ring-buffer page, and optionally an extracted TinnoOSS/P780 source tree.
Does NOT connect to a phone, use ADB, invoke a kernel exploit, or modify files.
"""
from __future__ import annotations
import argparse
import gzip
import json
from pathlib import Path
import re
import struct

KEYS = (
    'CONFIG_FUTEX', 'CONFIG_FUTEX_PI', 'CONFIG_RT_MUTEXES',
    'CONFIG_PREEMPT', 'CONFIG_ASHMEM', 'CONFIG_FTRACE',
    'CONFIG_KALLSYMS', 'CONFIG_KALLSYMS_ALL', 'CONFIG_RANDOMIZE_BASE',
    'CONFIG_ARM64_4K_PAGES', 'CONFIG_ARM64_VA_BITS',
    'CONFIG_ARCH_QCOM', 'CONFIG_ARCH_HOLI',
    'CONFIG_CFI_CLANG', 'CONFIG_CFI_CLANG_SHADOW',
    'CONFIG_SHADOW_CALL_STACK', 'CONFIG_VMAP_STACK',
    'CONFIG_LTO', 'CONFIG_LTO_CLANG',
    'CONFIG_SLAB_FREELIST_HARDENED', 'CONFIG_SLAB_FREELIST_RANDOM',
    'CONFIG_SECURITY_SELINUX', 'CONFIG_DEBUG_INFO_DWARF4',
    'CONFIG_DEBUG_INFO_BTF', 'CONFIG_MODULES', 'CONFIG_MODULE_SIG',
    'CONFIG_MODVERSIONS', 'CONFIG_PANIC_ON_OOPS',
    'CONFIG_PANIC_TIMEOUT', 'CONFIG_QCOM_FORCE_WDOG_BITE_ON_PANIC',
    'CONFIG_CC_VERSION_TEXT',
)


def load_config(path: Path):
    with gzip.open(path, 'rt', errors='replace') as fp:
        data = fp.read()
    found = {}
    for line in data.splitlines():
        m = re.match(r'(CONFIG_[A-Z0-9_]+)=(.*)$', line)
        if m:
            found[m.group(1)] = m.group(2)
            continue
        m = re.match(r'# (CONFIG_[A-Z0-9_]+) is not set$', line)
        if m:
            found[m.group(1)] = 'n'
    return {
        'total_lines': len(data.splitlines()),
        'config': {k: found.get(k, 'not listed') for k in KEYS},
        'config_header': next((s for s in data.splitlines() if 'Kernel Configuration' in s), ''),
    }


def load_raw(path: Path, marker: bytes):
    b = path.read_bytes()
    off = b.find(marker)
    outcome = {'file_size': len(b), 'marker': marker.decode('utf-8', 'replace'),
               'marker_found': off >= 0}
    if len(b) >= 12:
        outcome['ring_buffer_commit_raw'] = struct.unpack_from('<I', b, 8)[0]
        # Important: this is a ring-buffer commit field, not necessarily
        # equivalent to the count of user-level events.
    if off < 8:
        outcome['warning'] = 'No marker with a preceding 8-byte field; cannot extract a candidate pointer.'
        return outcome
    ip = struct.unpack_from('<Q', b, off - 8)[0]
    outcome.update({
        'marker_offset_hex': hex(off),
        'candidate_ip_field_offset_hex': hex(off - 8),
        'candidate_ip': f'0x{ip:016x}',
        'candidate_ip_page_offset': hex(ip & 0xfff),
        'looks_like_high_aarch64_kernel_address': (ip >> 48) == 0xffff,
        'important_limit': 'A candidate trace record IP is not the _text kernel base. Exact image-relative offset is unknown.',
    })
    return outcome


def source_check(base: Path):
    root = base / 'msm-5.4' if (base / 'msm-5.4').is_dir() else base
    rt = root / 'kernel' / 'locking' / 'rtmutex.c'
    fut = root / 'kernel' / 'futex.c'
    mf = root / 'Makefile'
    result = {'root': str(root), 'all_expected_files_present': all(p.exists() for p in (rt, fut, mf))}
    if not result['all_expected_files_present']:
        result['missing'] = [str(p) for p in (rt, fut, mf) if not p.exists()]
        return result
    a = rt.read_text(errors='replace')
    b = fut.read_text(errors='replace')
    m = mf.read_text(errors='replace')
    match = re.search(r'static\s+void\s+remove_waiter\s*\([^)]*\)\s*\{(.*?)\n\}', a, re.S)
    body = match.group(1) if match else ''
    proxy = re.search(r'int\s+rt_mutex_start_proxy_lock\s*\([^)]*\)\s*\{(.*?)\n\}', a, re.S)
    result.update({
        'kernel_version_from_makefile': '.'.join((re.search(rf'(?m)^{x}\s*=\s*(\d+)', m).group(1) if re.search(rf'(?m)^{x}\s*=\s*(\d+)', m) else '?') for x in ('VERSION','PATCHLEVEL','SUBLEVEL')),
        'remove_waiter_found': bool(match),
        'remove_waiter_uses_current_pi_lock': 'raw_spin_lock(&current->pi_lock)' in body,
        'remove_waiter_clears_current_pi_blocked_on': 'current->pi_blocked_on = NULL' in body,
        'proxy_lock_calls_remove_waiter': bool(proxy and 'remove_waiter(lock, waiter)' in proxy.group(1)),
        'futex_requeue_calls_proxy_lock': bool(re.search(r'rt_mutex_start_proxy_lock\s*\(', b)),
        'important_limit': 'This tests the supplied source tree only; not the phone\'s running kernel binary.',
    })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('p780-config.gz'))
    parser.add_argument('--trace', type=Path, default=Path('p780-cpu4.raw'))
    parser.add_argument('--marker', default='P780_GHOSTLOCK_PROBE')
    parser.add_argument('--source', type=Path, help='Optional local TinnoOSS/P780 repository directory')
    args = parser.parse_args()
    report = {'tool': 'P780 GhostLock offline evidence check', 'phone_modified': False}
    report['config'] = load_config(args.config) if args.config.is_file() else {'error': 'missing: ' + str(args.config)}
    report['trace'] = load_raw(args.trace, args.marker.encode()) if args.trace.is_file() else {'error': 'missing: ' + str(args.trace)}
    if args.source:
        report['source'] = source_check(args.source)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()