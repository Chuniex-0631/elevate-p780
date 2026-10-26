# 工具

> 2026-10-26 更新。每个工具目录自带 README，写明用途、依赖、运行方式与边界。

| 工具 | 用途 | 是否改动设备 |
|---|---|---|
| [`dirtyfrag-probe/`](dirtyfrag-probe/README.md) | DirtyFrag 探针：ESP 页缓存写入、系统库改写、钩子桩、离线分析脚本 | **是**（仅页缓存，可回滚） |
| [`p780-avb-readonly.ps1`](p780-avb-readonly.ps1) | 只读 AVB 信息采集 | 否 |
| [`native/`](native/README.md) | APK DEX / JNI ELF / CFI 的历史取证结果 | 否 |
| [`gaps/`](gaps/README.md) | ADB 只读取证缺口与 policy 记录 | 否 |
| [`dsu/`](dsu/README.md) | DSU 固定只读快照与 GSI VINTF 提取 | 否（不尝试安装） |
| [`verify_repository.py`](verify_repository.py) | 仓库结构、Markdown 链接与证据一致性校验 | 否 |
| [`summarize_config.py`](summarize_config.py) / [`audit_missing_config.py`](audit_missing_config.py) | 内核 config 差异与缺失项分析 | 否 |
| [`derive_candidate_layout.py`](derive_candidate_layout.py) / [`p780-layout-probe.c`](p780-layout-probe.c) | 候选源码结构测量 | 否 |
| [`compare_candidate_layouts.py`](compare_candidate_layouts.py) | 候选布局对比 | 否 |
| [`scan_journey_framework.py`](scan_journey_framework.py) | Journey 框架调用点扫描 | 否 |
| [`read_performance_dex.py`](read_performance_dex.py) | 原始 DEX 读取 | 否 |
| [`compare_journey_config.py`](compare_journey_config.py) | vendor XML 与 TCS dump 对比 | 否 |
| [`abl/`](abl/README.md) | boot image 解析、ABL 控制流/注册表与 Firehose DER/UFS 离线筛查 | 否 |
| [`afunix/`](afunix/README.md) | CVE-2024-26923 触发 harness | **是**（成功时可能 panic/reboot） |
| [`kgsl/`](kgsl/README.md) | 内核 ELF 反汇编辅助 | 否 |
| [`gsi/`](gsi/README.md) | 官方 GSI 下载/验签辅助 | 否（只联网） |
| [`partitions/`](partitions/README.md) | init 域分区 dumper | **是**（写 `/metadata`） |
| [`uring/`](uring/README.md) | CVE-2023-6931 研究工具 | **是**（触发会改内核状态） |
| [`artifact-scan/`](artifact-scan/README.md) | 静态样本敏感串扫描 | 否 |
| [`vuln-surface/`](vuln-surface/README.md) | property/kprobe/uring 输出解析 | 否 |

历史脚本见 [`../archive/scripts`](../archive/scripts)。

## 约定

- **只读工具**与**会改动设备状态**的工具必须在上表标注。
- 任何会改动设备的工具都要写回滚方法与最坏后果。
- 工具输出若被引用为证据，必须归档到 `evidence/` 并在清单中登记。
- 第三方 exploit 源码（如 `pipa/`）不入仓；`uring/` 只保留自己的分析/触发代码。
