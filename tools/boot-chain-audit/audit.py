"""Read saved regular files only; never contact a device or modify an input.

Extract observations, not a verdict that a slot switch or root succeeded.
Hashes describe local input bytes, which may be connector-normalized views.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import xml.etree.ElementTree as ET


RC = "evidence/20261027/vendor-config/init/android.hardware.boot@1.1-service.rc"
XML = "evidence/20261027/vendor-config/vintf/manifest/android.hardware.boot@1.1.xml"
POLICY = "evidence/20261027/vendor-config/selinux/plat_pub_versioned.cil"
VENDOR = "evidence/20261027/vendor-config/selinux/vendor_sepolicy.cil"
FASTBOOT = "evidence/20261026/oem/fastboot-getvar-all.txt"
ABL = "evidence/20261026/abl/abl_lzma.bin.strings.txt"
PROBE = "tools/update-engine-probe/mkpayload_boot.py"


def read_saved(path):
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("Only saved regular files are accepted")
    data = path.read_bytes()
    return data.decode("utf-8-sig"), hashlib.sha256(data).hexdigest()


def select(text, pattern):
    return [{"line": i, "text": line.strip()} for i, line in
            enumerate(text.splitlines(), 1) if re.search(pattern, line)]


def inspect_log(text):
    """Return fixed semantic events without publishing URLs or raw log lines.

    Counts are observations only. Multiple attempts may occur in one file;
    missing events do not prove absence of the corresponding operation.
    """
    events = []
    for n, line in enumerate(text.splitlines(), 1):
        for flag in ("switch_slot_on_reboot", "run_post_install"):
            for m in re.finditer(r"\b" + flag + r"\s*[:=]\s*(true|false|[01])\b", line):
                events.append({"line": n, "kind": flag, "value": m[1]})
        for m in re.finditer(r"ErrorCode::(k\w+)", line):
            events.append({"line": n, "kind": "error_code", "value": m[1]})
        if re.search(r"Unable to (?:call SetActiveBootSlot|set the active slot)", line):
            events.append({"line": n, "kind": "set_active_error"})
        if "Error getting bootctrl" in line:
            events.append({"line": n, "kind": "bootctrl_lookup_error"})
    return {"events": events, "slot_switch_verdict": "undetermined",
            "warning": "Do not merge attempts or infer no-op from missing logs"}


def audit(root):
    views, inputs, missing = {}, [], []
    for name in (RC, XML, POLICY, VENDOR, FASTBOOT, ABL, PROBE):
        path = root / name
        if not path.exists():
            missing.append(name)
            continue
        text, digest = read_saved(path)
        views[name] = text
        inputs.append({"path": name, "local_sha256": digest})
    fragment = views.get(XML)
    interfaces = []
    if fragment:
        for hal in ET.fromstring(fragment).findall("hal"):
            if hal.findtext("name") == "android.hardware.boot":
                interfaces += [node.text for node in hal.findall("fqname")]
    return {
        "schema_version": 1, "scope": "offline_saved_files_only",
        "inputs": inputs, "missing": missing,
        "rc_interfaces": select(views.get(RC, ""), r"^\s*interface android\.hardware\.boot@"),
        "manifest_fqnames": interfaces,
        "policy_client_rules": select(views.get(POLICY, ""),
            r"^\(typeattributeset hal_bootctl_client |^\(allow hal_bootctl_client "),
        "server_storage_rules": select(views.get(VENDOR, ""),
            r"^\(allow hal_bootctl(?:_default|_server)? (?:vendor_gpt_block_device|misc_block_device_30_0|vendor_(?:bsg|sg)_device) "),
        "historical_fastboot_slots": select(views.get(FASTBOOT, ""),
            r"\b(?:current-slot|slot-(?:retry-count|unbootable|successful|count)):"),
        "abl_string_leads": select(views.get(ABL, ""),
            r"Slot suffix .*Part Attr|Updating GPT partition|SetActiveSlot|FindBootableSlot|A/B retry count"),
        "probe_source_leads": select(views.get(PROBE, ""),
            r"block = 4096|data = b.*xAA|extent = |part = "),
        "verdicts": {"runtime_hal_registration": "unverified",
            "gpt_storage_on_p780": "candidate_not_binary_verified",
            "slot_switch": "undetermined", "permanent_root": "unverified"},
        "limitations": ["Static config is not runtime registration or a HAL return value",
            "ABL strings do not establish reachable control flow or GPT layout",
            "Fastboot snapshot predates the later update experiments",
            "Local text hashes are not asserted to be original device-byte hashes"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--log", type=Path, help="Optional saved UTF-8 device log, never a device node")
    args = parser.parse_args()
    report = audit(args.root)
    if args.log:
        text, digest = read_saved(args.log)
        report["log"] = {"local_sha256": digest, **inspect_log(text)}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
