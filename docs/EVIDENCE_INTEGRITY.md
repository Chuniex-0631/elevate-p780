# P780 核心证据完整性校验（2026-10-10）

这是 GitHub Actions Linux Runner 对**已上传 Git 仓库版本**的原始文件进行的 SHA-256、GZIP/ZIP 解码与 ZIP CRC 检查。由流水线自动打印完整结果，本文为持续保存的审计摘要。

- [完整性工作流](../.github/workflows/p780-final-audit.yml)
- [第一次验收 #38055450831](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055450831)：原件 SHA 与 ZIP CRC，全库当时 Markdown 内部相对链接 58 条、无失效。
- [交叉核验 #38055530285](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055530285)：再检查四份 ZIP 包各自自带的设备配置与 Tracefs 副本，均与仓库现存两份原始证据**字节完全一致**；内置 CHECKSUMS.sha256 中找到的匹配条目未发现不一致。

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
