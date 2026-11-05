#!/usr/bin/env python3
"""Inventory actual references to removed config symbols in two source trees."""
import argparse
import json
import re
from pathlib import Path
from summarize_config import read_config, compare

def scan(root, symbols):
    found = {k: [] for k in symbols}
    short = {k.removeprefix('CONFIG_'): k for k in symbols}
    pattern = re.compile(r'\bCONFIG_(' + '|'.join(map(re.escape, short)) + r')\b')
    definition = re.compile(r'^\s*(?:menuconfig|config)\s+(' + '|'.join(map(re.escape, short)) + r')\b')
    for path in sorted(root.rglob('*')):
        if not path.is_file() or '.git' in path.parts:
            continue
        if not (path.suffix in ('.c', '.h', '.S') or path.name.startswith(('Kconfig', 'Makefile'))):
            continue
        for number, line in enumerate(path.read_text(errors='replace').splitlines(), 1):
            hits = set(pattern.findall(line))
            if path.name.startswith('Kconfig') and (match := definition.match(line)):
                hits.add(match.group(1))
            for symbol in hits:
                found[short[symbol]].append({'path': str(path.relative_to(root)), 'line': number,
                                            'text': line.strip()[:300]})
    return found

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original', required=True)
    p.add_argument('--resolved', required=True)
    p.add_argument('--tinno', required=True)
    p.add_argument('--candidate', required=True)
    p.add_argument('--reports', required=True)
    a = p.parse_args()
    old, new = read_config(a.original), read_config(a.resolved)
    removed = compare(old, new)['removed']
    t, c = scan(Path(a.tinno), removed), scan(Path(a.candidate), removed)
    records = [{ 'symbol': k, 'device_value': old[k], 'tinno': t[k], 'candidate': c[k]} for k in removed]
    out = Path(a.reports)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'missing-config-references.json').write_text(json.dumps(records, indent=2) + '\n')
    lines = ['# Removed symbols: actual source references', '',
             'Source-level inventory only. A missing Kconfig symbol does not prove missing functionality.', '',
             '| Symbol | Device | TINNO references | Candidate references |', '|---|---|---:|---:|']
    lines += [f"| {r['symbol']} | {r['device_value']} | {len(r['tinno'])} | {len(r['candidate'])} |" for r in records]
    for r in records:
        lines += ['', '## ' + r['symbol']]
        for label in ('tinno', 'candidate'):
            lines += ['', '### ' + label]
            lines += [f"- `{x['path']}:{x['line']}` — `{x['text'].replace('`', '')}`" for x in r[label]] or ['- No references in scanned C/H/S/Kconfig/Makefile files.']
    (out / 'missing-config-references.md').write_text('\n'.join(lines) + '\n')
    print(f'{len(removed)} removed symbols; {sum(old[k] in ("y", "m") for k in removed)} originally enabled')

if __name__ == '__main__':
    main()
