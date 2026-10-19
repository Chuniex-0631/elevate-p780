# Evidence gap tools

`compare_policy_records.py` and `verify_policy_comparator.py` are offline Python-standard-library tools. They read original PC policy files without executing phone binaries or modifying policies.

```powershell
python tools/gaps/compare_policy_records.py LIVE_POLICY DISK_POLICY --avtab-offset 0x25602 --output comparison.json
python tools/gaps/verify_policy_comparator.py LIVE_POLICY --output validation.json
```

The offset and policy-v30/8-symbol-table/7-object-table layout are specific to the P780 pair in the report. The parser fails if unsupported nonempty conditional/role tables occur, or the symbol prefix differs beyond config. It does not independently parse the symbol table, interpret the extra header bit, evaluate policy access, or replace SETools. Its input originals are retained on the owner's PC; hashes and derived results are in Git.

`collect_gap_readonly.py --output CAPTURE_DIR` uses a fixed ADB whitelist for metadata, kernel/config/policy exports and selected read-only sysctls. It requires one authorized device. It writes PC output files only, and does not write Android properties, invoke service methods, push binaries, install, reboot or flash. The revised collector skips kernel-notes pull after metadata denial. The first executed revision attempted both; both refusals remain in the evidence log. Do not rerun completed/denied checks without new justification.

See [GAP-01 report](../../docs/research/p780-evidence-gap-audit-20261019.md) for findings, source layouts, acquisition limits and remaining independent verification.

