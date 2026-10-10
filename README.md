# Rakuten Hand 5G (TINNO P780) · 技术研究档案

> **私人设备 / 长期研究档案** · 资料跨度：2026-06-12 — 2026-10-10  
> 主线：实机 Android/内核信息、Fastboot/EDL、OEM Unlock、QAS/Mink/TZ/PFM、GhostLock 源码核对、A/B 固件与 OTA、GitHub Actions 重建实验。  
> **结论：未 Root、未解锁 Bootloader、未获得可刷写的原厂固件镜像。**

本仓库不是一个刷机工具或 GhostLock 现成利用包。它的目的，是把长期研究中的**已验证事实、原始证据、历史实验、离线分析、构建日志、失败记录和待办问题**集中保存，防止后续重复走过的弯路。

## 最先看这几份文档

| 入口 | 内容 |
|---|---|
| **[研究状态与可信度](docs/STATUS.md)** | 哪些实机证实，哪些仅由源码/构建证实，哪些仍失败或未知 |
| **[研究时间线](docs/HISTORY.md)** | 2026 年 6 月起的 EDL、ADB、QAS、GhostLock 和 Actions |
| **[设备基线、Bootloader 和 EDL](docs/DEVICE_AND_BOOT.md)** | 型号、固件、内核、AVB、Fastboot 回显、Sahara / HWID、分区发现 |
| **[GhostLock 专题](docs/GHOSTLOCK.md)** | CVE-2026-43499 旧源码路径、真机配置、Tracefs、偏移阻断 |
| **[QAS → Mink → PFM → TZAccessService](docs/QAS_TZ_PFM.md)** | eMBMS 许可查询、class 119、功能 700/2100、白名单和 JWT/TEE 混淆边界 |
| **[固件、官方更新与 2026 安全公告](docs/FIRMWARE_OTA_AND_OFFICIAL.md)** | _162 官方版本对应日期、OTA 缺失、固件真实性验证问题 |
| **[ADB 清理 / 精简系统实验](docs/DEBLOAT_AND_APP_TESTS.md)** | 302→242→157 历史包数及可恢复性提示 |
| **[全部已定位历史文件清单](docs/EVIDENCE_MANIFEST.md)** | 56 份历史资产逐项标注 GitHub 是否真的归档 |
| **[下一步与仍缺的原始证据](docs/NEXT_STEPS.md)** | 明确差什么、何时才值得碰手机 |
| **[证据来源及复现标准](docs/RESEARCH_SOURCES.md)** | 厂商、公开源码、实机文件与云端工件的区别 |

## 核心设备基线（真实 P780）

| 项目 | 证据结果 |
|---|---|
| 型号 / 厂商 | Rakuten Hand 5G / TINNO P780 |
| Android / 编译号 | Android 11，`264` |
| 固件版本 | **`P780AE_11.0_RMN_JP_162`** |
| 安全补丁 | 2024-02-01 |
| 内核 | **`5.4.233-qgki-gea5245e94afe-dirty`** |
| Clang | Android 11.0.2 / `r383902b1` |
| BL / AVB | Locked；fastboot 常规解锁指令返回 `unknown command` |
| EDL | 05C6:9008，Sahara v2，`mannar`，`HWID 0x0016f0e100000780` |
| 最新源码实验 | 匹配版 Clang11 的 `olddefconfig`、`rtmutex.o` **成功**；并非原厂 `vmlinux` |

## 已永久保存的实机证据与技术报告

- [设备 `p780-config.gz`](p780-config.gz) · 39,170 字节，原始 SHA-256 `0ff9cbb1844e043e1211b527509f5f435862cace25649bab6641d5d62c7bbce0`。
- [设备内核版本文本](archive/device/hand5g_kernel.txt) · Android Clang 11 / 真机编译日期。
- [设备 `/dev/block/by-name` 分区链接](archive/device/hand5g_byname.txt)。
- [2026 年 6 月 EDL 原始记录的脱敏转写](archive/device/P780_EDL_2026-06-12_sanitized.txt)。
- [QAS/PFM 全文报告](archive/reports/P780_PFM_QAS_2026-10-04.md)、[TZAccess 服务分析](archive/reports/P780_TZAccess_2026-10-04.md)、[MinkNative 全文报告](archive/reports/P780_MinkNative_2026-10-04.md)。
- [GhostLock 源码与实机数据报告](archive/reports/P780_GhostLock_source_audit_2026-10-10.md)。
- 历史工具及脚本：[archive/tools](archive/tools)、[archive/scripts](archive/scripts)，其中去预装脚本能修改系统，**不要直接执行**。

## GitHub Actions：完整研究证据已保存，不再依赖 Artifact 到期时间

| 测试 | 实验结果 | 永久归档 |
|---|---|---|
| Ubuntu Clang14 + Qualcomm 5.4.233 [#38052323798](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38052323798) | Kconfig + `rtmutex.o` 成功；2 值变 / 24 消失 / 327 新增 | [Clang14 工件](evidence/actions/2026-10-10-clang14) |
| 配置完整差异 [#38053251640](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38053251640) | 24 项删减、44 项新启用明确列出 | [差异报告](evidence/actions/2026-10-10-config-delta) |
| **Android Clang11 `r383902b1`** [#38053176845](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38053176845) | **0 值变 / 24 消失 / 322 新增**；`rtmutex.o` 成功 | [Clang11 全部日志和对象文件](evidence/actions/2026-10-10-clang11) |

候选代码是 **Galaxy A52s** 下游 5.4.233 代码，而 P780 公开的 TINNO OSS 源码是 **5.4.61**；构建成功不等于 P780 原厂 5.4.233 编译产物、已验证漏洞或真实内核地址。

## 官方核对

- [Rakuten Hand 5G 更新页面](https://network.mobile.rakuten.co.jp/information/software/rakuten-hand-5g/)：官方 `_162` 更新于 2024-03-21 开始发布。
- [Rakuten Hand 5G 支持/安全页面](https://network.mobile.rakuten.co.jp/product/smartphone/rakuten-hand-5g/support/index.html)：官方于 2026-09-28 公告固件真实性验证缺陷；这**不是**已经证明任意固件可由 Fastboot 刷写。

## 归档完整性的声明

我们已找到 **56 份历史相关文件**并建立清单，但部分只存在于原始 ChatGPT 文件库：旧 ZIP 工作包、APK、Bugreport、OTA 系统日志及 4 KB Tracefs 二进制。**这些原件尚未全部复制到 GitHub**，不能把一张清单当作已经完成的原始字节备份。完整名单见 [EVIDENCE_MANIFEST](docs/EVIDENCE_MANIFEST.md)。

本库为 Private，仍应避免存储设备独有标识、个人通信、运营商凭据、手机号及账户痕迹；公开前应独立审查全部 Git 历史。参见 [SECURITY.md](SECURITY.md)。

---

**研究规则：证据与结论分层、失败同样存档、不可擅自补出没有实测的成功结果。**
