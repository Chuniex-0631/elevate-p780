"""Enumerate `on property:` triggers whose action is powerful, and check which
domains may set the property (property_contexts + sepolicy property_service set).

Outputs a ranked list to stdout; no device interaction.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"C:\Users\ASUS Vivobook\Desktop\RakutenHand5G")
STATIC = ROOT / "09" / "P780-static-20261018-220912" / "files"
WORK = ROOT / "52-vuln-surface-analysis-20261025"

POWER = ("exec", "exec_background", "exec_start", "start ", "stop ", "write ", "write_misc",
         "chmod ", "chown ", "restorecon", "mount ", "symlink ", "copy ", "rm ", "rmdir ")
OURS = {"shell", "untrusted_app", "installd", "system_app"}


def load_property_contexts():
    rules = []  # (prefix, type, exact)
    for name in ("plat_property_contexts", "vendor_property_contexts"):
        p = WORK / name
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            prefix = parts[0]
            m = re.search(r"u:object_r:([A-Za-z0-9_]+):s0", " ".join(parts[1:]))
            if not m:
                continue
            ptype = m.group(1)
            exact = len(parts) >= 3 and parts[2] == "exact"
            rules.append((prefix, ptype, exact))
    return rules


def prop_type(rules, name):
    best = None
    for prefix, ptype, exact in rules:
        if exact:
            if name == prefix:
                return ptype
            continue
        if name.startswith(prefix):
            if best is None or len(prefix) > len(best[0]):
                best = (prefix, ptype)
    return best[1] if best else None


def parser_allows():
    """prop type -> set of domains allowed property_service set."""
    allowed = {}
    for name in ("plat_sepolicy.cil", "vendor_sepolicy.cil"):
        p = WORK / name
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"\(allow ([A-Za-z0-9_]+) ([A-Za-z0-9_]+) \(property_service \(set\)\)\)", text):
            allowed.setdefault(m.group(2), set()).add(m.group(1))
    return allowed


def rc_blocks(path: Path):
    blocks = []
    cur = None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("on "):
            cur = {"trigger": line[3:].strip(), "actions": []}
            blocks.append(cur)
            continue
        if line.startswith("service ") or line.startswith("import ") or line.startswith("on "):
            cur = None
            continue
        if cur is not None:
            cur["actions"].append(line)
    return blocks


def main() -> None:
    rules = load_property_contexts()
    allows = parser_allows()
    rc_files = sorted(STATIC.glob("system/etc/init/*.rc")) + sorted(STATIC.glob("vendor/etc/init/*.rc"))
    for sub in ("odm", "product", "system_ext"):
        rc_files += sorted(STATIC.glob(f"{sub}/etc/init/*.rc"))

    findings = []
    for rc in rc_files:
        for block in rc_blocks(rc):
            trig = block["trigger"]
            m = re.match(r"property:([^=]+)=(.*)", trig)
            if not m:
                continue
            prop, value = m.group(1).strip(), m.group(2).strip()
            actions = block["actions"]
            joined = " ; ".join(actions)
            power = [a for a in actions if a.split()[0].rstrip(":") in
                     {"exec", "exec_background", "exec_start", "start", "stop", "write",
                      "write_misc", "chmod", "chown", "restorecon", "restorecon_recursive",
                      "mount", "symlink", "copy", "rm", "rmdir"}]
            if not power:
                continue
            ptype = prop_type(rules, prop)
            writers = allows.get(ptype, set()) if ptype else set()
            ours = sorted(writers & OURS)
            findings.append({
                "rc": str(rc.relative_to(STATIC)),
                "prop": prop,
                "value": value,
                "type": ptype,
                "ours": ours,
                "actions": power,
            })

    # Rank: our-domain-writable first, then the rest.
    findings.sort(key=lambda f: (0 if f["ours"] else 1, f["prop"]))
    print(f"total property-triggered power actions: {len(findings)}\n")
    print("=== our domains can set (shell/app/installd/system_app) ===")
    for f in findings:
        if f["ours"]:
            print(f"\n[{f['rc']}] on property:{f['prop']}={f['value']}  (type={f['type']}, writers={','.join(f['ours'])})")
            for a in f["actions"][:6]:
                print("   ", a[:160])
    print("\n=== other writers (not directly ours) ===")
    for f in findings:
        if not f["ours"]:
            print(f"[{f['rc']}] {f['prop']} (type={f['type']}, writers={','.join(sorted(allows.get(f['type'], set())))[:60]}) :: {f['actions'][0][:100]}")


if __name__ == "__main__":
    main()
