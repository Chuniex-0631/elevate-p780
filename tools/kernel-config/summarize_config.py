#!/usr/bin/env python3
"""Summarize actual Linux Kconfig decisions; no third-party dependencies."""
import json
import os
import re
import sys
from pathlib import Path

SET = re.compile(r"^(CONFIG_[A-Za-z0-9_]+)=(.*)$")
UNSET = re.compile(r"^# (CONFIG_[A-Za-z0-9_]+) is not set$")
IMPORTANT = (
    "CONFIG_ARCH_HOLI", "CONFIG_ARCH_BLAIR", "CONFIG_FUTEX_PI",
    "CONFIG_RT_MUTEXES", "CONFIG_LTO_CLANG", "CONFIG_CFI_CLANG",
    "CONFIG_MODVERSIONS", "CONFIG_KALLSYMS", "CONFIG_IKHEADERS",
    "CONFIG_CC_VERSION_TEXT", "CONFIG_LOCALVERSION",
    "CONFIG_PREEMPT", "CONFIG_KASLR",
)

def read_config(filename):
    table = {}
    for line in Path(filename).read_text(errors="replace").splitlines():
        match = SET.match(line)
        if match:
            table[match.group(1)] = match.group(2)
        else:
            match = UNSET.match(line)
            if match:
                table[match.group(1)] = "n"
    return table

def compare(before, after):
    keys = sorted(set(before) | set(after))
    return {
        "added": [k for k in keys if k not in before],
        "removed": [k for k in keys if k not in after],
        "changed": [k for k in keys if k in before and k in after and before[k] != after[k]],
        "unchanged": sum(1 for k in keys if k in before and k in after and before[k] == after[k]),
    }

def main():
    original, resolved, final, reports = map(Path, sys.argv[1:5])
    reports.mkdir(parents=True, exist_ok=True)
    a, b, c = (read_config(x) for x in (original, resolved, final))
    first = compare(a, b)
    after = compare(b, c)
    full = compare(a, c)
    lines = [
        "# P780 kernel config audit",
        "",
        "Research-only cross-device build; do NOT flash this output to the device.",
        "",
        f"- Original parsed symbols: **{len(a)}**",
        f"- Resolved parsed symbols: **{len(b)}**",
        f"- Final parsed symbols: **{len(c)}**",
        f"- olddefconfig: **{len(first['changed'])} changed, {len(first['added'])} added, {len(first['removed'])} removed**",
        f"- Compilation-stage drift: **{len(after['changed'])} changed, {len(after['added'])} added, {len(after['removed'])} removed**",
        f"- Overall original to final: **{len(full['changed'])} changed, {len(full['added'])} added, {len(full['removed'])} removed**",
        "",
        "## Security and platform-critical symbols",
        "",
        "| Symbol | Device original | After olddefconfig | After compile |",
        "|---|---|---|---|",
    ]
    for k in IMPORTANT:
        lines.append(f"| {k} | {a.get(k, '(missing)')} | {b.get(k, '(missing)')} | {c.get(k, '(missing)')} |")
    for title, delta, left, right in [
        ("Original to resolved", first, a, b),
        ("Resolved to final", after, b, c),
    ]:
        lines += ["", f"## {title} details", ""]
        for kind in ("changed", "removed", "added"):
            symbols = delta[kind]
            lines.append(f"### {kind}: {len(symbols)}")
            for k in symbols[:120]:
                lines.append(f"- {k}: {left.get(k, '(missing)')} → {right.get(k, '(missing)')}")
            if len(symbols) > 120:
                lines.append(f"- ... {len(symbols)-120} additional changes in JSON report")
            lines.append("")
    summary = "\n".join(lines) + "\n"
    (reports / "config-summary.md").write_text(summary)
    (reports / "config-changes.json").write_text(
        json.dumps({"original_to_resolved": first, "resolved_to_final": after,
                    "original_to_final": full, "critical": {
                        k: {"original": a.get(k), "resolved": b.get(k), "final": c.get(k)}
                        for k in IMPORTANT
                    }}, indent=2, ensure_ascii=False) + "\n")
    concise = "\n".join(lines[:len(IMPORTANT)+16])
    print(concise)
    print("Change lists saved to reports/config-changes.json and reports/config-summary.md")
    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(path, "a") as fh:
            fh.write(summary)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
