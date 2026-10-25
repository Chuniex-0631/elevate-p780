# 工具

> 2026-10-25 重建。每个工具目录自带 README，写明用途、依赖、运行方式与边界。

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

历史脚本见 [`../archive/scripts`](../archive/scripts)。

## 约定

- **只读工具**与**会改动设备状态**的工具必须在上表标注。
- 任何会改动设备的工具都要写回滚方法与最坏后果。
- 工具输出若被引用为证据，必须归档到 `evidence/` 并在清单中登记。
