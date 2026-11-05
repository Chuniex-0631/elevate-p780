# Rakuten Hand 5G · P780 研究档案

设备取证、启动链分析与离线工具的可追溯研究库。

> **状态入口：[当前研究状态](docs/STATUS.md)**。已记录临时、受 SELinux 限制的 UID0 shell；永久 Root、Bootloader 解锁与完整 EDL 均未证实。
> 本次仓库重构日期：2026-11-05。未连接设备，未新增设备实验结论。

## 从这里开始

| 你的目标 | 阅读入口 |
|---|---|
| 了解已证实的结果与边界 | [STATUS](docs/STATUS.md) |
| 查看最近一次设备实验 | [2026-11-05 实验总结](docs/research/p780-20261105-summary.md) |
| 了解后续计划与停止条件 | [NEXT_STEPS](docs/NEXT_STEPS.md) |
| 查找全部专题与历史材料 | [文档索引](docs/index.md) · [时间线](docs/HISTORY.md) |
| 复跑离线分析 | [工具目录](tools/README.md) |
| 查看 Elevate 应用 | [应用说明与构建要求](app/elevate/README.md) |
| 核对原始材料 | [证据清单](docs/EVIDENCE_MANIFEST.md) · [归档说明](evidence/README.md) |
| 参与维护 | [贡献指南](CONTRIBUTING.md) · [目录职责](docs/ARCHITECTURE.md) |

## 设备基线

| 项目 | 已保存的设备信息 |
|---|---|
| 设备 / 平台 | Rakuten Hand 5G / TINNO P780，Qualcomm holi / Snapdragon 480 |
| 系统 | Android 11，`P780AE_11.0_RMN_JP_162` |
| 内核 | `5.4.233-qgki-gea5245e94afe-dirty` |
| 安全补丁 | 2024-02-01 |
| 权限基线 | `ro.debuggable=0`，SELinux Enforcing，Bootloader Locked |

以上为历史保存信息，不代表当前实时设备检查。研究结论及其证据边界统一维护在 STATUS，首页不再复制完整状态表。

## 最近记录

2026-11-05 的实验记录支持 A 槽 stock 镜像写入完成；重启仍从 B 槽启动，未完成切槽，未形成永久 Root。具体日志与哈希见[当日总结](docs/research/p780-20261105-summary.md)。早期候选路线保留研究背景，执行计划以 NEXT_STEPS 为准。

## 本地检查

维护命令仅需 Python 3.11+ 和 Git，无需连接手机、安装 Android SDK 或下载 Python 依赖。各研究工具的额外依赖见各自 README。

```sh
python tools/verify_repository.py
python -m unittest discover -s tools/tests -v
python tools/build_research_index.py --check
```

添加文档或证据后，先用 `git add` 纳入跟踪，再运行 `python tools/build_research_index.py` 更新索引和清单。检查范围与日常流程见[贡献指南](CONTRIBUTING.md)。

## 范围与原始材料

本库保存机主自有设备的取证、离线分析及历史受控实验，包含会改变设备状态的工具。运行前阅读对应工具的边界与恢复说明。

原始日志与样本不随整理改写；大体积材料按来源和哈希登记。**仓库公开，`evidence/restricted/` 不构成访问隔离，材料尚未完成全面脱敏。** 详见 [SECURITY](SECURITY.md)。本库不提供解锁或刷写服务，不针对他人设备。
