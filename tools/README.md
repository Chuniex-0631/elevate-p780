# 当前离线工具

绝大多数程序在工作目录读取文件、不连接手机；**`p780-avb-readonly.ps1` 为例外**，它通过已授权 ADB 执行只读属性查询与分区名称枚举，不读取分区镜像也不更改设备。研究输入和边界见 [文档导航](../docs/README.md)。历史设备清理脚本另存 [archive/scripts](../archive/scripts)，会修改手机状态。

| 文件 | 用途 |
|---|---|
| [p780-avb-readonly.ps1](p780-avb-readonly.ps1) | Windows PowerShell / ADB 白名单 AVB 属性与分区软链接只读采集；参见 [2026-10-18 AVB 基线](../docs/research/avb-live-baseline-20261018.md) |
| [verify_repository.py](verify_repository.py) | 全量相对路径链接、Python/JSON 格式、Journey 原件/视图与保留迁移 Blob 身份检查 |
| [summarize_config.py](summarize_config.py) | 原始/求解/编译后配置差异 |
| [audit_missing_config.py](audit_missing_config.py) | 缺失 CONFIG 符号的固定源码引用扫描 |
| [derive_candidate_layout.py](derive_candidate_layout.py)、[p780-layout-probe.c](p780-layout-probe.c) | 从实际 Kbuild 参数编译候选结构探针 |
| [compare_candidate_layouts.py](compare_candidate_layouts.py) | 逐运行候选布局比较 |
| [scan_journey_framework.py](scan_journey_framework.py) | 原有 JourneyConfigService 直接引用扫描；在内存副本处理 hidden-API 兼容问题 |
| [read_performance_dex.py](read_performance_dex.py) | 直接读取原始 DEX 表，提取性能服务与调用点；保留原件不修改 |
| [compare_journey_config.py](compare_journey_config.py) | vendor XML 与只读 TCS dump 对照，ALL 区域为比较假设 |

DEX 工具需要 Python、androguard、loguru，并从当前目录的 framework-audit/ 读取 services.jar 与 framework.jar，生成离线分析文件。配置对照用法：`python tools/compare_journey_config.py <解压目录>`，目录包含 config.xml、version.txt 和原始 tcs-state.txt。其它构建工具的参数与依赖以脚本及对应手动 workflow 为准。

原始 framework 输入未迁入 Git，不能仅克隆本库便重跑 DEX 提取；输入 SHA 和范围见 [Journey 专题](../docs/research/journey-config.md)。候选布局不是可直接用于实机的参数。
