# P780 核心证据完整性校验（2026-10-10）

这是 GitHub Actions Linux Runner 对**已上传 Git 仓库版本**的原始文件进行的 SHA-256、GZIP/ZIP 解码与 ZIP CRC 检查。由流水线自动打印完整结果，本文为持续保存的审计摘要。

- [完整性工作流](../.github/workflows/p780-final-audit.yml)
- [第一次验收 #38055450831](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055450831)：原件 SHA 与 ZIP CRC，全库当时 Markdown 内部相对链接 58 条、无失效。
- [交叉核验 #38055530285](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055530285)：再检查四份 ZIP 包各自自带的设备配置与 Tracefs 副本，均与仓库现存两份原始证据**字节完全一致**；内置 CHECKSUMS.sha256 中找到的匹配条目未发现不一致。
- [正式文档封存验收 #38056019230](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38056019230)：最终结构改动后，**138 个 Markdown 相对链接、0 个失效**；GZIP/ZIP/Tracefs 检查、四套内嵌证据和哈希再次通过。今后 README / docs / archive / 关键 evidence 发生改动时，CI 将自动再次检查，并对损坏的相对链接报告失败。

## 原始文件检验清单

| GitHub 路径 | 字节数 | SHA-256 | 验收 |
|---|---:|---|---|
| [`p780-config.gz`](../p780-config.gz) | 39170 | `0ff9cbb1844e043e1211b527509f5f435862cace25649bab6641d5d62c7bbce0` | gzip 正常，FUTEX_PI/RT_MUTEXES=y |
| [`evidence/device/p780-cpu4.raw`](../evidence/device/p780-cpu4.raw) | 4096 | `435e5e1d05767ebc7a65322a2da2599ad07c58c7277456cd96d6960620587fac` | Tracefs 标记存在 |
| [`evidence/ghostlock/P780-GhostLock-port-v0.1.zip`](../evidence/ghostlock/P780-GhostLock-port-v0.1.zip) | 57818 | `e93c02077af6b5998d6adcb4720acce6fedf4b98a17757dca2cde68938f8691a` | 13 条目，CRC 全部通过 |
| [`evidence/ghostlock/P780-GhostLock-port-v0.2.zip`](../evidence/ghostlock/P780-GhostLock-port-v0.2.zip) | 72599 | `3fedf983e6489711bd25ded2b23d25b44ade084f6ff25810fe0f426bf30ad142` | 16 条目，CRC 全部通过 |
| [`evidence/ghostlock/P780-GhostLock-port-v0.3.zip`](../evidence/ghostlock/P780-GhostLock-port-v0.3.zip) | 67667 | `247e1c6277be550d38e29263981ed21836acee2a6a5b50cb8eb9e7b3d0368fca` | 17 条目，CRC 全部通过 |
| [`evidence/ghostlock/P780-GhostLock-port-v0.4.zip`](../evidence/ghostlock/P780-GhostLock-port-v0.4.zip) | 99662 | `64cf94d149a113b69758285e923f1e445a2a01aaf19592eab3b97596f8485f19` | 27 条目，CRC 全部通过 |

## 解释与边界

- 五份新上传的原件已由 Git Blob 直接移动至 `evidence/`，移动不改变内容（对象 SHA 沿用），不需要重复上传。
- 这里的 SHA-256 是 GitHub 内文件的**内容哈希**；旧电脑和用户文件库中的原始副本未经独立 SHA 比对，不应将大小相同称为严格独立来源验证。
- 同一 `p780-config.gz` 与 `p780-cpu4.raw` 在 v0.1–v0.4 的 ZIP 内均可读取且与主仓库原件一致。这意味着四个 ZIP 并非四次独立实机取证，而是在逐版打包过程中**重复包含同一份实机证据**。
- `p780-cpu4.raw` 中找到 `P780_GHOSTLOCK_PROBE`，证明追踪标记可复核，**没有**验证 GhostLock 触发、内核基址或 Bootloader 解锁。
- 四个 ZIP 内只有离线调查/预检工具和历史结果。CRC/哈希正确证明完整存档，**不证明漏洞运行成功或参数可信**。
- Markdown 链接扫描只覆盖 Git 仓库**相对路径**，不代表外部网址始终有效。后续文档编辑会导致链接计数变化，准确结果以最新 Actions 运行为准。


## 2026-10-10 第二批实体机原件（迁移前后字节身份不变）

来源：GitHub Actions [新文件清单 #38056324556](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38056324556) 的自动 SHA-256、ZIP CRC 和同名展开文件逐项对比；归档整理仅改变路径，没有重新压缩或替换二进制内容。下表不是旧本地原件与 GitHub 之间的独立来源认证。

| 当前仓库原件路径 | 字节数 | SHA-256 |
|---|---:|---|
| [两阶段审计 ZIP：debloat](../evidence/restricted/adb/hand5g_debloat_audit.zip) | 376662 | `549042553411cc702019a378bc7a21d21f0129e10c0f6014b01a691b8b2bda8e` |
| [两阶段审计 ZIP：final](../evidence/restricted/adb/hand5g_final_audit.zip) | 419387 | `54ebd6a48c244e86dfea78061f723b5a86acb61d229e9082e9b9233babfa1a3e` |
| [Android Bugreport](../evidence/restricted/bugreport/hand5g_bugreport.zip) | 5684665 | `7e662b108af7b1fa33113636ef86178e5e177ce6a1eb7c498fc12daadec159dc` |
| [SystemUpdate Activity](../evidence/restricted/ota/hand5g_update_activity.txt) | 94710 | `7d69799a7b0c06240cb3d04e8cddf27a92d7d9bb5cc79c048b37d8ace3dccba1` |
| [SystemUpdate Logcat](../evidence/restricted/ota/hand5g_update_log.txt) | 283944 | `c100d7f7c32527f763b3d26dc30f8bd32d72f96e6bc9b83cca2bed20e844f33b` |
| [native-api 受限路径](../evidence/tee/hand5g_native_api_paths.txt) | 1174 | `ffe7521fd4cd0942b6a04c86b10a5c7bbd2b8d1b500ae179defdf4ce2db561f2` |
| [TEE 白名单](../evidence/tee/hand5g_tz_whitelist.txt) | 3148 | `56937f268c4363b7314dd00163e0283dfc587eb6a6a738b4c9542cc07de17a00` |
| [phase3 所有包清单](../evidence/restricted/adb/phase3/hand5g_packages_all_phase3.txt) | 22482 | `8171f6e8db3f66121d7a9b69a9e226bf14eabacf7fc5c7577176f0756aa49613` |
| [phase3 安装包清单](../evidence/restricted/adb/phase3/hand5g_packages_installed_phase3.txt) | 17724 | `243e0de522382f3f7ab8e1c272231943507b6dbd240ed74d116c5281b3f84530` |
| [ApeHighLights.apk](../evidence/apk/ApeHighLights.apk) | 1704633 | `e8755aabeae90f6b8b0b00b27eaf87ae8bdda1aac64eed3c06cdd1a20b11fa91` |
| [Qualcomm SecureUI APK](../evidence/apk/com.qualcomm.qti.services.secureui.apk) | 24990 | `23d1fca23ce3e81d976817c4fd75dc851e4de9e4c8a35a840394518135984144` |
| [Qualcomm SystemHelper APK](../evidence/apk/com.qualcomm.qti.services.systemhelper.apk) | 16798 | `94f81b017ce0b0ebc11f5b0dbdbad07cc06a871b983b92c8bd4169fb30c91791` |

- ZIP CRC：两个审计包分别 **22 / 9** 条目，Bugreport **402** 条目，三个 APK 均检查通过。
- 22+9 个审计展开文件在清理前与对应 ZIP 内文件分别 SHA-256 一致；仅在 `main` 中删除重复展开目录，字节未丢失。
- 本轮在清理前创建恢复分支 [archive/pre-cleanup-20261010](https://github.com/Chuniex-0631/p780-kernel-research/tree/archive/pre-cleanup-20261010)；不能把在 `main` 中删除理解为从所有 Git 历史安全擦除。
- 自动复验扩展到 Bugreport/ADB ZIP、APK、TEE/OTA 文件：[完整性工作流](../.github/workflows/p780-final-audit.yml)。  
**重要：** 上述文件存在**未脱敏的用户设备资料**，目录 `restricted` 不是加密容器或独立 ACL。
