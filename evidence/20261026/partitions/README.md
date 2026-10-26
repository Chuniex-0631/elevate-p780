# 分区快照

- 保留：`abl`/`xbl_config`/`devcfg`/`misc`/`misc_after`/`misc_restore`/`frp`/`devinfo`/`vbmeta_a`/`vbmeta_b`/`vbmeta_system_a`/`vbmeta_system_b`/`vbmeta_system_a.avbpubkey`；`xbl_b` 的 strings/scan 已入仓。
- 未入仓：`xbl_b.00.bin`（3.67 MB，GitHub API 401，疑似内容扫描/拒收；本地保留）、boot 分区块（用 `../kernel/boot_b_full.img`）、`vendor_boot`/`dtbo`、`persist`/`modemst1`/`modemst2`/`fsg`/`fsc`（个人/IMEI）。
- 来源：48 号 init 域 dumper；只读证据。
