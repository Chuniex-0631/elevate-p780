# 工具目录

> v1.1.0：按职责整理。下表覆盖全部工具子目录；旧的根目录 Python 脚本仅作为兼容入口。

仓库维护仅需 Python 3.11+ 与 Git；研究工具依赖、输入输出和恢复边界见各目录 README。运行前确认“设备影响”列。

## 维护入口

```sh
python tools/verify_repository.py
python tools/build_research_index.py --check
python -m unittest discover -s tools/tests -v
```

新增文件先 `git add`，再运行 `python tools/build_research_index.py`。完整流程见[贡献指南](../CONTRIBUTING.md)。

## 维护与索引

| 工具 | 用途 | 设备影响 |
|---|---|---|
| [tests/](tests/README.md) | 维护回归测试 | 离线 |
| [kernel-config/](kernel-config/README.md) | 内核配置与候选结构测量 | 离线 |
| [journey/](journey/README.md) | Journey XML / DEX 分析 | 离线 |

## 启动链与镜像

| 工具 | 用途 | 设备影响 |
|---|---|---|
| [abl/](abl/README.md) | ABL 与 Firehose 离线审计 | 离线 |
| [boot-chain-audit/](boot-chain-audit/README.md) | Boot HAL、GPT、更新日志审计 | 离线 |
| [dsu/](dsu/README.md) | DSU 只读快照与 VINTF 提取 | 只读设备/离线 |
| [gsi/](gsi/README.md) | 官方 GSI 下载与验签 | 联网/离线 |
| [rom/](rom/README.md) | ROM 发布产物核验 | 离线 |
| [partitions/](partitions/README.md) | 分区提取和清单核验 | 会写设备 |

## 内核研究

| 工具 | 用途 | 设备影响 |
|---|---|---|
| [ghostlock/](ghostlock/README.md) | 历史 PI 链研究骨架 | 实验/改变设备 |
| [afunix/](afunix/README.md) | AF_UNIX 历史触发实验 | 实验/可能重启 |
| [kgsl/](kgsl/README.md) | KGSL 离线反汇编 | 离线 |
| [uring/](uring/README.md) | io_uring 历史研究 | 实验/改变内核状态 |
| [kallsyms/](kallsyms/README.md) | 符号提取 | 离线 |
| [kernel-symbol-recovery/](kernel-symbol-recovery/README.md) | 符号恢复与验证 | 离线 |
| [vuln-surface/](vuln-surface/README.md) | 保存的攻击面输出分析 | 离线 |

## 框架与取证

| 工具 | 用途 | 设备影响 |
|---|---|---|
| [oemlock/](oemlock/README.md) | OEM lock 框架审计 | 离线 |
| [native/](native/README.md) | DEX / JNI / ELF 审计 | 离线 |
| [artifact-scan/](artifact-scan/README.md) | 静态样本敏感串扫描 | 离线 |
| [gaps/](gaps/README.md) | 补充只读取证与策略比较 | 只读设备/离线 |
| [supplement/](supplement/README.md) | 历史补充采集和分析 | 只读设备/离线 |

## 受控设备实验

| 工具 | 用途 | 设备影响 |
|---|---|---|
| [dirtyfrag-probe/](dirtyfrag-probe/README.md) | 历史页缓存改写探针 | 会改设备 |
| [ipsec-preflight-android/](ipsec-preflight-android/README.md) | IPsec 预检 Android 项目 | 设备预检 |
| [perf-permission/](perf-permission/README.md) | 最小 perf 权限探测 | 设备计数器实验 |
| [root-daemon/](root-daemon/README.md) | 历史 daemon 汇编材料 | 实验/改变设备 |
| [update-engine-probe/](update-engine-probe/README.md) | 历史 OTA payload 实验 | 会写分区 |
| [20261105/](20261105/README.md) | 2026-11-05 实验方法记录 | 历史实验说明 |

## 保留的兼容入口

`summarize_config.py`、`audit_missing_config.py`、`derive_candidate_layout.py`、`compare_candidate_layouts.py` 转发至 `kernel-config/`；三个 Journey 脚本转发至 `journey/`。新文档和工作流使用归类后的路径。`p780-layout-probe.c` 保留兼容 include。

独立只读采集入口：[p780-avb-readonly.ps1](p780-avb-readonly.ps1)。

迁移表见 [structure-migration.json](../docs/reference/structure-migration.json)。历史脚本另存 [archive/scripts](../archive/scripts/)，不会由维护检查执行。
