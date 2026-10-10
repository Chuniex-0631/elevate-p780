# P780 GhostLock v0.1–v0.4 历史工作包索引

这四份 ZIP 是此前围绕 CVE-2026-43499 构建的 **离线预检 / 源码对照工具**，不是可运行的 P780 Root 发布版。原文件目前位于用户的历史文件库，尚未将 ZIP 的全部字节提交到本仓库。

| 版本 | 文件名 | 原 ZIP 大小 | 当前可核实用途 |
|---|---|---:|---|
| v0.1 | `P780-GhostLock-port-v0.1.zip` | 57,818 B | 基线、设备资料校验与初期静态研究 |
| v0.2 | `P780-GhostLock-port-v0.2.zip` | 72,599 B | 继续检查旧源码与 CVE 相关模式 |
| v0.3 | `P780-GhostLock-port-v0.3.zip` | 67,667 B | 新增版本桥接、预检与数据交叉对照 |
| v0.4 | `P780-GhostLock-port-v0.4.zip` | 99,662 B | 原有实机证据整理、符号/配置可能性与阻断条件梳理 |

**版本对应的细项应以各 ZIP 内文件为准**。上表说明历史研究方向，不表示已经逐文件检查四份原始 ZIP，也不表示每版拥有独立的 exploit 代码或新增可用偏移。

已明确的 P780 条件：

- 设备 `5.4.233-qgki`，公开 TINNO 5.4.61 源码的 `remove_waiter` 具有错误代理任务模式，但**没有证据证明实机 5.4.233 二进制没有私有修补**。
- 已经有 `p780-config.gz`（39,170B）与 `p780-cpu4.raw`（4,096B）的历史实验材料；后者原始字节未入 Git 仓库。
- 从 tracefs 样本中提取的候选 64 位地址字段，不足以推出 `_text` 或完整结构/符号偏移。
- 原始设备处于 locked BL；Android kernel root 即使成功也**不自动完成 Bootloader 解锁**。
- 当前尚无匹配原厂的 `boot.img`、`vmlinux`、`System.map`。

原始源码核对：[完整历史报告](../archive/reports/P780_GhostLock_source_audit_2026-10-10.md)。

旧工具已经迁入 [archive/tools](../archive/tools)，但**历史 ZIP 尚待单独保存**。如果需要实现原始字节级的 GitHub 备份，请设备所有者将这四份小型 ZIP 上传到私有仓库的 `evidence/historical-packages/` 目录（总大小不足 300 KB）。无需重新运行工具或连接手机。
