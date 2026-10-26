# 内核 / boot

两项均已入仓。

- `boot_b_full.img`：51,408,896 B，header v3；SHA-256 `877fd16220feb3488e6c4f8d6f5af4dc6ccd3670d2ae93f40e9301d3eeb1b825`；`tools/abl/unpack_boot.py` 可解。
- `P780-kernel-symbol-recovery-20261025.zip`：22,370,728 B；SHA-256 `92baa993385105d68f75ee734229ffe8bbe60221c75b569d185ccc5fad826a83`；symbolized ELF/kallsyms；来源 27 号。
- 符号/静态补丁证据见 `evidence/kernel/20261025-symbol-recovery/` 与 `evidence/kernel/20261025-static-patch-review/`。

