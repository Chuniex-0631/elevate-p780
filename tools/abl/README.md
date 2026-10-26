# ABL / boot 解析

- `unpack_boot.py`：解析 Android boot image（v3/v4），提取 kernel/ramdisk；只读本地镜像。
- `strings_scan.py`：ASCII/UTF-16 字符串提取。

输入见 `evidence/20261026/kernel/boot_b_full.img`；ABL 结论见 `docs/research/p780-abl-avb-gsi-20261026.md`。

## 离线控制流与 Firehose 筛查（2026-10-26）

`control_flow_audit.py` 读取 FV 中嵌入的 AArch64 PE，输出局部字符串引用、指定 RVA 反汇编或显式命令表；需要 capstone。地址是 PE RVA，非 FV 文件偏移。

`firehose_screen.py` 仅扫描本地文件的 DER 证书与存储字符串，需要 cryptography；可用 `--pkhash` 提供完整摘要。它不验证完整 Qualcomm 镜像签名，不将 UFS 字符串判为兼容，不连接设备。

用法、来源与边界见 [ABL 审计](../../docs/research/p780-boot-edl-audit-20261026.md)和 [Firehose 清单](../../docs/research/p780-firehose-screening-20261026.md)。测试：`python -m unittest discover -s tools/abl -p test_offline_audit.py -v`。
