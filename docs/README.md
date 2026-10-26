# 文档导航

> 2026-10-26 优先顺序更新：先[ABL控制流复核](research/p780-boot-edl-audit-20261026.md)，再[Firehose/商业读取核对](research/p780-firehose-screening-20261026.md)，之后核对 UID0/Journey 边界与公开隐私。当前只做离线分析，不执行旧文档中的写分区建议。

> 2026-10-26 更新。完整目录见 [`index.md`](index.md)（自动生成）；本页只给入口。

| 入口 | 内容 |
|---|---|
| [`index.md`](index.md) | 全部文档索引（按目录分组，含标题与首句） |
| [`STATUS.md`](STATUS.md) | 当前结论与边界（唯一权威状态页） |
| [`NEXT_STEPS.md`](NEXT_STEPS.md) | 下一步计划与停止条件 |
| [`HISTORY.md`](HISTORY.md) | 时间线 |
| [`EVIDENCE_MANIFEST.md`](EVIDENCE_MANIFEST.md) | 证据清单 |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | 目录职责与维护约定 |

## 2026-10-25 / 10-26 新专题

- [`research/p780-abl-avb-gsi-20261026.md`](research/p780-abl-avb-gsi-20261026.md) — ABL 工厂菜单、AVB/GSI、XBL EDL。
- [`research/p780-ghostlock-5.4-20261026.md`](research/p780-ghostlock-5.4-20261026.md) — GhostLock 5.4.233 车辆判负。
- [`research/p780-edl-programmer-20261026.md`](research/p780-edl-programmer-20261026.md) — EDL 签名 programmer 搜索。
- [`research/p780-kgsl-cve-2024-23373-20261026.md`](research/p780-kgsl-cve-2024-23373-20261026.md) — kgsl / CVE-2024-23373 / GPUAF。
- [`research/p780-afunix-cve-2024-26923-20261026.md`](research/p780-afunix-cve-2024-26923-20261026.md) — AF_UNIX GC 触发。
- [`research/p780-uring-cve-2023-6931-20261025.md`](research/p780-uring-cve-2023-6931-20261025.md) — CVE-2023-6931。
- [`research/p780-init-capability-20261025.md`](research/p780-init-capability-20261025.md) — init 域能力。
- [`research/p780-artifact-scan-20261025.md`](research/p780-artifact-scan-20261025.md) — 静态样本扫描。
- [`research/p780-oem-unlock-final-20261025.md`](research/p780-oem-unlock-final-20261025.md) — OEM unlock final。
- [`research/p780-vuln-surface-analysis-20261025.md`](research/p780-vuln-surface-analysis-20261025.md) — 攻击面分析。

## 专题分区

- [`research/`](research/)：按主题与日期的专题报告（`p780-<主题>-<日期>.md`）
- [`reference/`](reference/)：来源、归档规范、证据完整性方法
- [`archive/`](archive/)：已被取代的阶段性文档，保留原样

## 注意

少量早期页面正文含不可逆的编码替换字符（U+FFFD），在 [`index.md`](index.md) 中标记为"部分损坏"；其结论不再引用，以 `STATUS.md` 与未损坏专题为准。
