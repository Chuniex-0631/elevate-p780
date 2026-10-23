# P780 supplemental evidence tools

The fixed ADB collector exports selected VINTF directories, the public OTA certificate archive, and a small baseline/bootctl whitelist. It does not write Android settings or properties, install, enable DSU, push binaries, reboot or flash. Rejected/absent paths are logged and not worked around.

```powershell
python tools/supplement/collect_supplement_20261024.py --output CAPTURE
python tools/supplement/analyze_supplement_20261024.py CAPTURE
```

The analyzer is offline and requires Python plus cryptography. It verifies ZIP CRC, parses XML, calculates certificate DER/SPKI fingerprints and verifies the RSA self-signature. Its historical main-manifest comparison expects the owner's numbered PC corpus with `13-dsu-readonly/vendor-manifest.xml` beside CAPTURE. It does not merge libvintf inputs, validate all runtime HALs, authenticate a downloaded OTA, or prove signature bypass.

All 46 XML originals are preserved as UTF-8 text without newline normalization, and the 1135-byte public certificate ZIP is reversibly Base64 encoded in the evidence directory. Decode and verify against files.json before use. The manifest contains hashes of original acquisition bytes rather than later analysis files.

See [report](../../docs/research/p780-supplement-20261024.md) and [evidence overview](../../evidence/supplement/20261024/README.md). The collector is provided for reproducibility, not an instruction to repeat completed or denied checks.
