# Rakuten Hand 5G / TINNO P780 研究档案

> 更新：2026-10-25（Asia/Shanghai）。记录机主实机取证、离线样本分析与候选源码实验。
> **Bootloader 仍为 Locked；已有 `installd` 域受限 `uid 0` Root Shell 的实机记录，但没有完整 SELinux 权限或永久分区写入通道。**

设备：Qualcomm 平台（holi / mannar），Android 11，内部固件 `P780AE_11.0_RMN_JP_162`，系统指纹末段 `264:user/release-keys`，内核 `5.4.233-qgki-gea5245e94afe-dirty`（Clang 11.0.2，2024-02-20 构建），`ro.debuggable=0`，SELinux Enforcing。

## 当前结论

| 方向 | 已取得的证据 | 当前状态 |
|---|---|---|
| DirtyFrag / CVE-2026-43284 | 公开 IPsec API 建 SA + `splice` 钉页 + 内核原地解密；有效 ESP 报文被接受并覆盖文件页；可写只读系统库页缓存 | **原语已实机确认** |
| 代码执行 | 改写 `libc++.so` / `libbase.so` 代码页，在 **init 域**与 **installd 域**（均 uid 0）进行受限域代码执行；installd 域另已执行 `/system/bin/sh` | **实机记录成立；权限仍受 SELinux 限制** |
| Root shell | 已实机记录 `uid=0(root)`、`u:r:installd:s0`、SELinux Enforcing；`/data/app` 与 dalvik-cache 写入测试成功 | **受限临时 Root Shell 已取得；非完整 Root** |
| AVB 测试根密钥 | 本机 TEE 证书公钥摘要匹配 AOSP 默认 RSA4096 AVB 测试公钥；vbmeta digest 同时吻合 | 公钥身份已核验；不等于可写入或解锁 |
| DSU / GSI | A/B 槽离线验签通过；B 已安装并尝试启动，最终回原厂；恢复出厂后原生 Loader 也由机主报告回退 | **路线已停止**；失败阶段未知 |
| OEM Unlock 灰化 | Journey gate：`OemLockService` 读 `ro.boot.journey.customer=1` 后返回 false；296 份去壳 APK/JAR 中仅 6 个直接调用点 | 静态根因已定位；无普通调用者入口 |
| Fastboot / EDL | unlock 系列全 `unknown command`；QDL v2.8 通到 Sahara v2（HWID / PKHash 已记录） | 未取得 Firehose；缺匹配签名的 programmer 与原厂镜像 |
| GhostLock / CVE-2026-43499 | 配置满足、TINNO 5.4.61 有同形 `remove_waiter` 调用链、tracefs 有候选指针 | 本机 Image / 符号已有；仍缺逐构建布局、缓解范围与适用性结论 |
| 源码与内核身份 | 实机 `config.gz` 5238 项；匹配 Clang11 候选编译与结构测量 | 本机 `Image` 和 173,205 个符号已核验；仍缺原厂调试 `vmlinux` / DWARF / 对应完整源码 |

结论以 [`docs/STATUS.md`](docs/STATUS.md) 为准；任务与验收标准见 [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md)。

## 导航

| 入口 | 内容 |
|---|---|
| [`docs/index.md`](docs/index.md) | **全量文档索引**（自动生成，含全部专题与旧档） |
| [`docs/STATUS.md`](docs/STATUS.md) | 当前结论、证据等级与边界 |
| [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md) | 下一步计划与停止条件 |
| [`docs/HISTORY.md`](docs/HISTORY.md) | 时间线 |
| [`docs/EVIDENCE_MANIFEST.md`](docs/EVIDENCE_MANIFEST.md) | 证据清单（路径 / 字节 / SHA-256） |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | 目录职责与维护约定 |
| [`docs/rom/README.md`](docs/rom/README.md) | ROM Release 七个资产索引（全部上线） |
| [`docs/rom/AUDIT-20261025.md`](docs/rom/AUDIT-20261025.md) | 元数据与清单审计；真实 TAR 复核待本地运行 |
| [`tools/rom/verify_release.py`](tools/rom/verify_release.py) | 本地哈希、Product 合并、TAR 文件清单核验 |
| [`docs/research/p780-rom-kernel-system-triage-20261025.md`](docs/research/p780-rom-kernel-system-triage-20261025.md) | 内核/系统组件静态分析范围与 Root 能力边界 |
| [`tools/README.md`](tools/README.md) | 可复跑工具 |
| [`SECURITY.md`](SECURITY.md) | 范围与伦理 |

## 最新专题

- [`docs/research/p780-installd-root-shell-20261025.md`](docs/research/p780-installd-root-shell-20261025.md) — 受限 `installd` 域 uid 0 shell 实机记录及能力边界。
- [`docs/research/p780-kernel-symbol-recovery-20261025.md`](docs/research/p780-kernel-symbol-recovery-20261025.md) — 本机 Image 符号恢复和独立核验。

- [`docs/research/p780-dirtyfrag-live-exploit-20261025.md`](docs/research/p780-dirtyfrag-live-exploit-20261025.md) — DirtyFrag 实机利用链：原语确认、系统库写入、init/installd 域代码执行、能力边界与回滚。
- [`tools/dirtyfrag-probe/README.md`](tools/dirtyfrag-probe/README.md) — 配套探针、钩子桩与离线分析工具。

## 范围

本仓库只做机主自有设备的只读取证、离线分析与可回滚的受控实验；不包含第三方利用载荷、不提供解锁/刷写服务、不针对他人设备。
