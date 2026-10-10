# GhostLock P780 离线研究包：v0.1—v0.4

> **四份 ZIP 原件现已全部上传并通过 CRC/SHA 校验。** 这是一组离线预检、证据分类与源码核对工程，**不是 P780 Root 工具、不是已验证漏洞利用程序**。四版实际复用同一份 `p780-config.gz` 和 `p780-cpu4.raw`。

## 版本和可复核产物

| 版本 | ZIP 原件 | 内容条目数 | 经过 ZIP 内清单核对的新内容 | Root 状态 |
|---|---|---:|---|---|
| v0.1 | [下载 v0.1](../evidence/ghostlock/P780-GhostLock-port-v0.1.zip) | 13 | `p780_preflight.py`、31 项 required facts 目标列表、目标 JSON、初始预检报告、回归测试 | `BLOCKED` |
| v0.2 | [下载 v0.2](../evidence/ghostlock/P780-GhostLock-port-v0.2.zip) | 16 | 增加 `target/fact-matrix.json`、按来源分类并交叉验证构建指纹与版本；**2 项基础事实验证、29 项仍缺** | `BLOCKED` |
| v0.3 | [下载 v0.3](../evidence/ghostlock/P780-GhostLock-port-v0.3.zip) | 17 | 新增 `tools/p780_source_audit.py`、`source/PROVENANCE.json` 与旧版 TINNO `rtmutex.c`/`futex.c`/Makefile 离线对比测试 | `BLOCKED` |
| v0.4 | [下载 v0.4](../evidence/ghostlock/P780-GhostLock-port-v0.4.zip) | 27 | 添加 `v04-preflight.json`、`source-audit-user.json`、`test_p780_version_bridge.py` 和更多版本桥接预检脚本/测试 | `BLOCKED` |

关于 v0.4 的**原件内部不一致**：压缩包外层目录与文件名标注为 v0.4，但其内部 `README.md` 首行仍写“适配工程 v0.3”。这属于保留的历史打包瑕疵，不能因此将 ZIP 误认作另一个 v0.3，也**不应篡改历史 ZIP 原件**。区分时以包名、哈希、文件清单、`v04-preflight.json` 和新增的测试文件为依据。

## 原件校验状态

- 4 个压缩包的 ZIP CRC 测试全部成功（完整条目数分别为 **13、16、17、27**）。
- 4 个 ZIP 内嵌 `evidence/p780-config.gz` 和 `evidence/p780-cpu4.raw`，都与仓库主证据**逐字节相同**，不是四次独立采集。
- 包内 `CHECKSUMS.sha256` 已检查到的匹配条目均未发现哈希不一致。
- 每个 ZIP 文件自身的 SHA-256 记录在 [证据完整性报告](EVIDENCE_INTEGRITY.md)。本次校验来自 [GitHub Actions #38055530285](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055530285)。

## 原始实验价值

1. **真实内核配置**：`CONFIG_FUTEX_PI=y`、`CONFIG_RT_MUTEXES=y`、`CONFIG_ASHMEM=y` 等关键基础条件可见。
2. **Tracefs 只读痕迹**：包含 `P780_GHOSTLOCK_PROBE` 标记及候选地址字段，但无法推出真实 kernel `_text`。
3. **厂商旧版源码**：TINNO 5.4.61 `rtmutex` 中存在 CVE-2026-43499 相关旧错误模式，不能用来断言实际 5.4.233 固件尚未修补。
4. **目标参数缺口**：上游参考 stage 需要 31 项信息；早期 v0.2 仅校验其中 2 项静态基础事实，**缺少 29 项**。之后的 Clang11 候选对象编译不自动填补这些逐构建偏移。
5. **原始运行结果**：所有版本均保持 `Research-only / BLOCKED`；无已验证提权、无刷机、无 Bootloader 解锁。

## 查阅建议

先读 [GhostLock 研究专题](GHOSTLOCK.md) 和 [原版源码核对报告](../archive/reports/P780_GhostLock_source_audit_2026-10-10.md)；若需要逐版复现，再打开对应 ZIP 内的 `RESEARCH_PROGRESS.md`、`CHECKSUMS.sha256`、`tests/` 和 `reports/`。**不要把旧 ZIP 中的报告视为晚于 2026-10-10 Clang11 构建的新实机证据。**
