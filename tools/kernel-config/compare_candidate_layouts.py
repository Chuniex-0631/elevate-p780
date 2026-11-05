#!/usr/bin/env python3
"""Compare only measurements which really exist; retain build failures."""
import json
import sys
from pathlib import Path

def main():
    root, url = Path(sys.argv[1]), sys.argv[2]
    variants = ('tinno-5.4.61', 'a52s-5.4.233')
    results = {}
    for name in variants:
        p = root / 'builds' / ('p780-layout-' + name) / 'candidate-layout.json'
        results[name] = json.loads(p.read_text()) if p.exists() else None
    lines = ['# Candidate source layout comparison', '', f'Run: {url}', '',
             '**Offline source measurement, not a certified layout of the running P780.**', '',
             '| Source | Extraction result |', '|---|---|']
    for k, v in results.items():
        lines.append(f'| {k} | ' + (f'{len(v["measurements"])} measurements' if v else 'FAILED / not extracted; inspect saved logs') + ' |')
    if all(results.values()):
        a, b = [results[k]['measurements'] for k in variants]
        keys = sorted(set(a) | set(b))
        lines += ['', '| Fact | TINNO 5.4.61 | A52s 5.4.233 | Same? |', '|---|---:|---:|---|']
        for k in keys:
            lines.append(f'| {k} | {a.get(k, "missing")} | {b.get(k, "missing")} | {a.get(k) == b.get(k)} |')
        changed = [k for k in keys if a.get(k) != b.get(k)]
        lines += ['', f'{len(changed)} of {len(keys)} measured facts differ.', '',
                  'Equal numbers do not prove source identity or runtime equivalence. Differences mix version, vendor and configuration changes.']
    (root / 'layout-comparison.md').write_text('\n'.join(lines) + '\n')
    (root / 'layout-comparison.json').write_text(json.dumps({'run_url': url, 'results': results}, indent=2) + '\n')

if __name__ == '__main__':
    main()
