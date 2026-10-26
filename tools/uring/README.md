# CVE-2023-6931 研究工具

- `analysis/kdis.py`、`analysis/cfi_sock_table.py`、`analysis/DATA-CHAIN-20261026.md`。
- `uring_cve.c` / `uring_cve2.c`：触发/self 模式；`shell_surface.c`、`perf_overflow.c`、`gen_syms.py`、`build_p780_ndk.ps1`。
- `pipa/` 第三方源码不入仓；文中只保留本地说明。
- 触发会改动内核状态；只在自有设备运行。
