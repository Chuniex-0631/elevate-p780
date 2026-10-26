# init 域分区 dumper

- `dump_partition.py`：通过 DirtyFrag init 域分块读取 block device，输出到 `/metadata`；**会写设备**。
- `cleanup_template.S`：48 号 init 清理桩。
- 只在自有设备使用；依赖 48 号 init 代码执行；分区快照见 `evidence/20261026/partitions/`。
