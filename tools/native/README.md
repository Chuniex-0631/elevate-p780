# P780 diagnostic offline audit

These tools read exported files on the PC. They do not connect to or execute code on the phone.

Requirements: Python 3, androguard 4.1.4, loguru, pyelftools 0.33, capstone 5.0.9. The DEX script also uses the existing `tools/oemlock/dex_tables.py` helper. Install dependencies in a separate environment.

Capture directory must contain `QTIDiagServices.apk`, `libDiagService.so` and `services.jar`. Original bytes are retained on the owner's PC; the evidence directory contains derived data rather than all original binaries.

```powershell
python tools/native/diag_live_audit.py --capture-dir CAPTURE_DIR --historical-root HISTORICAL_ROOT
python tools/native/diag_elf_audit.py --capture-dir CAPTURE_DIR
```

The historical root is the original numbered PC corpus containing `09/P780-static-20261018-220912/files/` and `09/P780-services.jar`. The first command verifies exact input hashes, decodes 16 method bodies plus native declarations, and writes manifest/method evidence. The second decodes AArch64 functions from dynamic and minidebug symbols, retains CFI veneers, and labels PLT calls using relocations. Android packed dynamic relocations are not completely reconstructed; this is not a runtime linker emulator or an exhaustive call graph.

The initial read-only acquisition used targeted `getprop`, `ps -AZ`, `dumpsys package/activity services`, target-process logcat, directory metadata, and `adb pull` for the three readable system files. It did not send diagnostic commands or initialize the library again. Denied vendor paths are recorded in observations and must not be repeatedly retried without new evidence.

See [the report](../../docs/research/p780-native-live-endpoints-20261019.md) for source identity, findings and limits.
