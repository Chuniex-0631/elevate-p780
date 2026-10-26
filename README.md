# Rakuten Hand 5G / TINNO P780 研究档案

> 更新：2026-10-26（Asia/Shanghai）。记录机主实机取证、离线样本分析与候选源码实验。
> **Bootloader 仍为 Locked；历史记录已取得临时 UID0 shell（SELinux installd 域、Enforcing），并已做成 Elevate；永久 Root、BL 解锁与完整 EDL 仍未证实。**

设备：Qualcomm 平台（holi / SD480），Android 11，内部固件 `P780AE_11.0_RMN_JP_162`，系统指纹末段 `264:user/release-keys`，内核 `5.4.233-qgki-gea5245e94afe-dirty`（Clang 11.0.2，2024-02-20 构建），SPL **2024-02-01**，`ro.debuggable=0`，SELinux Enforcing。

## 当前结论

| 方向 | 已取得的证据 | 当前状态 |
|---|---|---|
| DirtyFrag / CVE-2026-43284 | 公开 IPsec API 建 SA + `splice` 钉页 + 内核原地解密；有效 ESP 报文被接受并覆盖文件页；可写只读系统库页缓存 | **原语已实机确认** |
| 代码执行 | 改写 `libc++.so` / `libbase.so` 代码页，在 **init 域**与 **installd 域**（均 uid 0）执行任意系统调用；全程可回滚 | **成立** |
| Root shell | 后续 daemon / Elevate 记录 `uid=0`、`u:r:installd:s0`；早期 exec 失败不代表最终状态 | **已记录临时受限 shell**；非永久 root |
| AVB 测试根密钥 | 本机 TEE 证书公钥摘要匹配 AOSP 默认 RSA4096 AVB 测试公钥；vbmeta digest 同时吻合 | 公钥身份已核验；不等于可写入或解锁 |
| DSU / GSI | A/B 槽离线验签通过；B 已安装并尝试启动，最终回原厂；恢复出厂后原生 Loader 也由机主报告回退 | **路线已停止** |
| OEM Unlock 灰化 | Journey gate：`OemLockService` 读 `ro.boot.journey.customer=1` 后返回 false；296 份去壳 APK/JAR 中仅 6 个直接调用点 | 静态根因已定位；无普通调用者入口 |
| Fastboot / EDL | unlock 系列全 `unknown command`；QDL v2.8 通到 Sahara v2（HWID `0016f0e100000780`，PKHash `c19a5029…`） | 未取得 Firehose；未取得经完整签名与 UFS 核验的 programmer |
| ABL 工厂菜单 | 关机后 Vol Up + Power 菜单：START / Restart bootloader / Recovery mode / Power off / **Boot to FFBM** / **Boot to QMMI**；**无 Unlock**；FFBM/QMMI 均回 Android | 历史选择后回 Android；FRP→菜单因果与无工厂镜像均未证实 |
| GhostLock 5.4 | 5.4.233 `remove_waiter` 漏洞确认；pselect/mcast/tcp/sigreturn/process_vm/bpf 公开车辆在 P780 帧/结构上全部判负；AArch64 Path B data-only 可用但无完整车辆 | **无可用车辆**；公开车辆不能直接移植 |
| EDL programmer | SD480/Holi；Sahara v2 可达；五份候选根 `d9357db8…`/`4352b3bf…`/`a51a1c2e…` 均不匹配 `c19a5029…`；本轮未找到可验证匹配的 loader | **缺签名 loader** |
| CVE-2024-23373 | NVD 明确含 Snapdragon 480 5G；`kgsl_mmu_put_gpuaddr` 的 unmap 失败→释放 DMA/anon 页模式成立；但 P780 kgsl 无 VBO、无 sparse，GPUAF 的 VBO 触发不适用 | **待触发**；缺非 VBO 的 `iommu_unmap < size` 路径 |
| CVE-2024-26923 | 5.4.233 < 5.4.275；`unix_gc` 未修复；触发 PoC 两轮 30s 未赢 | **未触发** |

结论以 [`docs/STATUS.md`](docs/STATUS.md) 为准；任务与停止条件见 [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md)。

## 最新专题（2026-10-25 / 10-26）

- [分区证据再提取](docs/research/p780-partition-reextract-20261026.md) — 本地丢失的 `48-init-capability` 分区集按原方法重取：`vendor_boot_a/b`、`dtbo_a` 与 45+45 个 first-stage `.ko`、22 个 dtb 全部与 manifest 哈希一致。
- [ABL / EDL 离线复核](docs/research/p780-boot-edl-audit-20261026.md) — 真实注册表、FRP 读取、misc 字节比较、Root 状态纠正。
- [Firehose 与商业读取筛查](docs/research/p780-firehose-screening-20261026.md) — 五份候选证书算法/来源与 UFS 边界。
- **公开隐私提醒**：当前仓库公开，`evidence/restricted/` 没有访问隔离；原始材料尚未完成全面脱敏，见 [SECURITY.md](SECURITY.md)。

- [`docs/research/p780-abl-avb-gsi-20261026.md`](docs/research/p780-abl-avb-gsi-20261026.md) — ABL 工厂菜单实测、AVB/GSI 信任链、XBL EDL 复核。
- [`docs/research/p780-ghostlock-5.4-20261026.md`](docs/research/p780-ghostlock-5.4-20261026.md) — GhostLock 5.4.233 漏洞确认、AArch64 Path B、七条车辆的判负记录。
- [`docs/research/p780-edl-programmer-20261026.md`](docs/research/p780-edl-programmer-20261026.md) — EDL 签名 programmer 公开渠道搜索结论（SD480/Holi）。
- [`docs/research/p780-kgsl-cve-2024-23373-20261026.md`](docs/research/p780-kgsl-cve-2024-23373-20261026.md) — CVE-2024-23373、GPUAF、P780 kgsl 无 VBO/sparse 与 unmap 失败触发分析。
- [`docs/research/p780-afunix-cve-2024-26923-20261026.md`](docs/research/p780-afunix-cve-2024-26923-20261026.md) — AF_UNIX GC 竞态触发 PoC 与两轮实测。
- [`docs/research/p780-uring-cve-2023-6931-20261025.md`](docs/research/p780-uring-cve-2023-6931-20261025.md) — CVE-2023-6931 的 ring/CFI/地址泄漏边界。
- [`docs/research/p780-init-capability-20261025.md`](docs/research/p780-init-capability-20261025.md) — init 域代码执行能力、SELinux 边界与回滚。
- [`docs/research/p780-artifact-scan-20261025.md`](docs/research/p780-artifact-scan-20261025.md) — 静态样本敏感串扫描。
- [`docs/research/p780-oem-unlock-final-20261025.md`](docs/research/p780-oem-unlock-final-20261025.md) — OEM unlock 最终结论与 `getvar all` 记录。
- [`docs/research/p780-vuln-surface-analysis-20261025.md`](docs/research/p780-vuln-surface-analysis-20261025.md) — property/kprobe/uring 攻击面分析。

## 导航

| 入口 | 内容 |
|---|---|
| [`docs/index.md`](docs/index.md) | **全量文档索引**（自动生成，含全部专题与旧档） |
| [`docs/STATUS.md`](docs/STATUS.md) | 当前结论、证据等级与边界 |
| [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md) | 下一步计划与停止条件 |
| [`docs/HISTORY.md`](docs/HISTORY.md) | 时间线 |
| [`docs/EVIDENCE_MANIFEST.md`](docs/EVIDENCE_MANIFEST.md) | 证据清单（路径 / 字节 / SHA-256） |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | 目录职责与维护约定 |
| [`tools/README.md`](tools/README.md) | 可复跑工具 |
| [`SECURITY.md`](SECURITY.md) | 范围与伦理 |

## 范围

本仓库保存机主自有设备的取证、离线分析与历史受控实验（含页缓存改写、App 安装和 misc 字段写入；不应把全库描述为严格只读）；不包含第三方利用载荷、不提供解锁/刷写服务、不针对他人设备。证据中已剔除个人分区（`persist`/`modemst`/`fsg`/`fsc`）与第三方 exploit 源码；大体积 GSI/system 只登记来源与哈希；`boot_b_full.img`（51 MB）与 `P780-kernel-symbol-recovery-20261025.zip`（22 MB）已入 `evidence/20261026/kernel/`。



