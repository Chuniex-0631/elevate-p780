# 分区快照

- 保留：`abl`/`xbl_config`/`devcfg`/`misc`/`misc_after`/`misc_restore`/`frp`/`devinfo`/`vbmeta_a`/`vbmeta_b`/`vbmeta_system_a`/`vbmeta_system_b`/`vbmeta_system_a.avbpubkey`；`xbl_b` 的 strings/scan 已入仓。
- 未入仓：`xbl_b.00.bin`（3.67 MB，GitHub API 401，疑似内容扫描/拒收；本地保留）、boot 分区块（用 `../kernel/boot_b_full.img`）、`persist`/`modemst1`/`modemst2`/`fsg`/`fsc`（个人/IMEI）。
- 2026-10-26 再提取（原 `48-init-capability-20261025/partitions/` 本地副本丢失后）：
  `vendor_boot_a.00.bin`、`vendor_boot_b.00.bin`、`dtbo_a.00.bin` 及三个解包目录
  `vendor_boot_a_ramdisk/`、`vendor_boot_b_ramdisk/`（各 51 个文件，含 45 个 first-stage `.ko`）、
  `dtbo_a_entries/`（22 个 `.dtb`）。SHA-256 与 `evidence/partitions/manifest-20261025.json` 全部一致，
  方法与过程见 [`docs/research/p780-partition-reextract-20261026.md`](../../../docs/research/p780-partition-reextract-20261026.md)。
- 核验：`python tools/partitions/verify_manifest.py`（ok=133、mismatch=0）。
- 来源：48 号 init 域 dumper；只读证据。
