#!/usr/bin/env python3
"""Replay Kbuild's asm-offsets invocation for an offline, candidate-only probe.

Method reference: JingMatrix/pixel-ksu-root tools/kernel-source-offsets,
commit 063ad1352860f0bf114bab5d7c368ee226206534. This implementation avoids
eval, reads the complete saved Kbuild command, and preserves provenance.
It does not obtain runtime addresses or certify source/device equivalence.
"""
import argparse
import hashlib
import json
import re
import shlex
import subprocess
from pathlib import Path

def compile_args(command, probe, output):
    args = shlex.split(command)
    if any(t in (';', '&&', '|', '||') for t in args):
        raise ValueError('Unexpected shell operation in compiler invocation')
    marker = args.index('-S')
    if args[marker + 1] != '-o' or not args[-1].endswith('asm-offsets.c'):
        raise ValueError('Unexpected Kbuild compiler invocation shape')
    # Keep architecture, include paths, conditional defines and hardening flags.
    # Give the probe its own dependency file instead of overwriting Kbuild's.
    flags = [x for x in args[:marker] if not x.startswith('-Wp,-M')]
    return flags + ['-S', '-o', str(output), str(probe)]

def parse_assembly(text):
    values = {}
    for name, number in re.findall(r'\.ascii\s+"->([A-Z0-9_]+)\s+[$#]?(-?\d+)', text):
        if name in values:
            raise ValueError(f'Duplicate measurement: {name}')
        values[name] = int(number)
    if not values:
        raise ValueError('No DEFINE measurements in probe assembly')
    return values

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', required=True)
    p.add_argument('--probe', required=True)
    p.add_argument('--reports', required=True)
    p.add_argument('--source-commit', required=True)
    a = p.parse_args()
    out, probe, reports = map(lambda x: Path(x).resolve(), (a.out, a.probe, a.reports))
    reports.mkdir(parents=True, exist_ok=True)
    cmdfile = out / 'arch/arm64/kernel/.asm-offsets.s.cmd'
    line = next(x for x in cmdfile.read_text().splitlines() if x.startswith('cmd_') and ' := ' in x)
    command = line.split(' := ', 1)[1]
    (reports / 'kbuild-command.txt').write_text(command + '\n')
    assembly = reports / 'layout-probe.s'
    args = compile_args(command, probe, assembly)
    (reports / 'probe-command.json').write_text(json.dumps(args, indent=2) + '\n')
    with (reports / 'probe-compile.log').open('w') as log:
        subprocess.run(args, cwd=out, stdout=log, stderr=subprocess.STDOUT, check=True)
    values = parse_assembly(assembly.read_text())
    data = {'evidence_level': 'offline candidate source; NOT verified device layout',
            'source_commit': a.source_commit,
            'config_sha256': hashlib.sha256((out / '.config').read_bytes()).hexdigest(),
            'probe_sha256': hashlib.sha256(probe.read_bytes()).hexdigest(),
            'measurements': values}
    (reports / 'candidate-layout.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))

if __name__ == '__main__':
    main()
