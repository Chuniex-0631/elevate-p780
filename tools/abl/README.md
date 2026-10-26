# ABL / boot 解析

- `unpack_boot.py`：解析 Android boot image（v3/v4），提取 kernel/ramdisk；只读本地镜像。
- `strings_scan.py`：ASCII/UTF-16 字符串提取。

输入见 `evidence/20261026/kernel/boot_b_full.img`；ABL 结论见 `docs/research/p780-abl-avb-gsi-20261026.md`。
