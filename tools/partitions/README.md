# init 域分区 dumper

- `dump_partition.py`：2026-10-25 的分块读取脚本，把 block device 经 init 域载荷写到 `/metadata`，
  再 `adb pull`；它引用的 `21-dirtyfrag-probe-20261025/`、`25-kernel-dump-20261025/` 是当时的工作目录，
  未入仓，**不能直接复跑**，保留作流程记录。
- `init_dump_stub.S`：2026-10-26 再提取时实际使用的载荷源码（init 门控、8 MiB 一次性 dump、
  重放 sentry 序言）；配合 Elevate APK 的 `patchProbe()` 使用。
- `cleanup_template.S`：48 号 init 清理桩。
- `verify_manifest.py`：按 `evidence/partitions/manifest-20261025.json` 校验
  `evidence/20261026/partitions/` 的字节数与 SHA-256；个人分区缺失只报告，哈希不符或多余文件才失败。
- 只在自有设备使用；**会写设备**（页缓存与 `/metadata`），回滚与后果见
  [`docs/research/p780-partition-reextract-20261026.md`](../../docs/research/p780-partition-reextract-20261026.md)。
