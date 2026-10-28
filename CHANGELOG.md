# 变更记录

> 2026-10-28 文档整理：本页只保留可被仓库文件或 Actions 证据支持的里程碑。
> 早期逐条日志（含编码损坏段落）不再重排，原始内容保留在 git 历史中。

## 2026-10-28 — 状态口径与历史结论整理

- 统一临时 installd UID0、永久 Root、Bootloader、Sahara/Firehose 与有限写入的证据边界；未新增设备实测。
- 状态页和下一步计划重排；原页存入 docs/archive，保留历史阶段记录。
- 将 boot_a 4096 B 操作限定为仓库保存的有限写入记录；不再称任意块写或已完成刷写启动。
- 就地更正 FRP 菜单因果、misc 偏移、programmer 检索与 testkey 持久 Root 推论。
- 当前设备实验保持暂停；未更改原始证据、工具实现或仓库可见性，未完成全面脱敏。

## 2026-10-27 — 6931 原语打通与暂停、信息层收尾

- **完整 root 软件路径收口（晚）**：update_engine 切槽被 v1.0 bootctl 缺失挡住（日志只有 `Marking new slot as unbootable`，没有 `SetActiveBootSlot`）；6931 的 values 槽位不可控；KGSL 无 VBO，CVE-2024-23380/23373 不适用且 CVE-2025-21479 仅 A7xx；FastRPC 的 CVE-2024-21455 被 `ASYNC_FASTRPC_CAP=0` 挡住，CVE-2024-43047 虽能创建两个 `vaddrin=0` 的重叠 map，但 shell 没有有效 DSP handle（`handle=0/3..6` ENOSUCH，`7..20` EPERM），`put_args` 不可达；EDL 仍缺签名 loader。设备保持 B 槽 stock，保留已记录的临时 installd UID0 shell，非永久 Root。

- CVE-2023-6931：perf 组 u16 回绕、8446 sibling、delta 页错误校准（1888/5984/10080/14176/22368 一次命中）、KASLR/sock/cred 泄漏均实机验证；`__perf_read_group_add` 的 `x19` 可读出 values 地址。
- observed-V：校准会移动 X；双组 8446 规模在真机卡死，小观察组采样为 0；**暂停 6931 设备实验**，恢复条件写入 `docs/NEXT_STEPS.md`。
- 进程因卡死重启两次；无 OOB 写盘，设备恢复。`boot_id` 记录在对应报告。
- EDL：截至该轮检索未获得可验证匹配的 programmer；同 SoC 不证明兼容。
- 新增 [`docs/research/p780-info-layer-20261027.md`](docs/research/p780-info-layer-20261027.md)：已有分区/模块/配置清单与各执行域读取边界；`STATUS.md`、`NEXT_STEPS.md` 同步更新。
- **完整 root 路线复审**（[p780-full-root-routes-20261027.md](docs/research/p780-full-root-routes-20261027.md)）：实测 system_app 可直接调用 update_engine；在已检查服务中，update_engine 有相关类型写权限及可达调用者，实际写入范围须另验；OTA 证书为 RSA-2048 releasekey（非 testkey）；Linux 5.4 块设备 page cache 支持 splice + writepage + fsync。当时主线改为 update_engine 验签绕过（后续已暂停）（先离线确认证书加载时机与 payload 格式），6931 降为 fallback。
- **update_engine 基线打通**：AOSP 11 源码确认每次 apply 重读 `otacerts.zip`；生成 166 B 最小 payload（大端头、签 `header+manifest`）并通过 openssl 校验；system_app + 本地 HTTP 触发成功，日志精确停在 `kDownloadMetadataSignatureMismatch`。工具与复现步骤在 [`tools/update-engine-probe/`](tools/update-engine-probe/)。
- **OTA 签名门已绕过**：自建小 APK（`tools/update-engine-probe/app/`）把 1135 B `otacerts_ours.zip` 写进 `/system/etc/security/otacerts.zip` 页缓存（`match=true`），紧接着触发 update_engine，日志出现 `Verified correct signature 1 out of 1 signatures.` 与 `Metadata hash signature matches value in Omaha response.`。RSA-1024 不被 `PadRSASHA256Hash()` 接受，已改用 RSA-2048。空分区 manifest 会让 `DeltaPerformer::Write` SIGSEGV。
- **有限 boot_a 写入已记录**：`mkpayload_boot.py` 的 `partition=boot` + `REPLACE` payload 被 update_engine 接受的 4096 B REPLACE 操作记为写入 `/dev/block/bootdevice/by-name/boot_a`，日志 `Applying 1 operations` → `Completed 1/1` → `FilesystemVerifierAction kSuccess`；结束码 `kUpdatedButNotActive` 只因 `SWITCH_SLOT_ON_REBOOT=0`。
- **未进入 A 槽，刷机路线暂停**：原厂 `vbmeta_a` 的 boot 描述符对应 build 263，B 为 264，A/B boot 镜像不同；只替换描述符重签、以及用 B 的 vbmeta/boot 均未进入 A；后续确认未成功切槽，不能据此断言修改后的 A 镜像已接受启动验证。update_engine 拒绝写 `misc`（`kInstallDeviceOpenError`），fastboot 无 set_active/flash/erase，`bootctl` 不可用。OTA 情报收集（[p780-ota-recon-20261027.md](docs/research/p780-ota-recon-20261027.md)）确认 `/data/ota_package` 与 `/data/misc/update_engine` 不可读、无 OTA URL/包。当时主线切回 6931 target A（后续同样暂停）。

## 2026-10-26 — 离线审计更正与可复跑筛查

- 原件解压逐字节核验，恢复 ABL 的 14 项 fastboot 注册表与分派链；FRP 缓冲区末位读取成立，菜单隐藏因果未闭合。
- 五份 Firehose 候选固定来源、Git blob 与 SHA-256，区分 SHA-256/SHA-384/SPKI；UFS 字符串不视为兼容。
- Chimera 精确 P780 页面仅列 Get Info，商业 EDL 分区读取仍未证实；没有设备操作。
- 更正 README/STATUS 为“临时 installd UID0 shell 已有成功记录”；补充公开仓库隐私警示与 misc 换行/偏移字节复核。
- 旧条目中的“retail 无工厂镜像、FRP 门控为 0、公开渠道绝无 loader”作为历史推论保留，由新审计报告更正。

## 2026-10-26 — ABL 菜单 / GhostLock 5.4 / EDL / kgsl

- 实机进入 ABL 工厂菜单：`Vol Up + Power` 后有 START / Restart bootloader / Recovery mode / Power off / **Boot to FFBM** / **Boot to QMMI**，**没有 Unlock**；FFBM/QMMI 均重启回 Android，仅支持菜单与回退观察；旧推论“无工厂镜像、FRP 门控为 0”已由离线审计更正，因果未闭合。
- GhostLock 5.4.233：反汇编确认 `remove_waiter` 清 `current->pi_blocked_on`（0x930）而非 `waiter->task`，漏洞成立；但 pselect（waiter word 15 > 7）、multicast（REFUSE-gated）、tcp_zerocopy（5.4 struct 16B）、sigreturn（off -0x118）、process_vm、bpf 全部判负，公开车辆无法移植。
- EDL programmer：P780 为 SD480/Holi；该轮检索未获可验证匹配样本；已扫描根 DER 摘要未见目标前缀，不是完整签名或设备兼容性裁决。
- CVE-2024-23373：NVD 明确含 SD480；`kgsl_mmu_put_gpuaddr` 失败模式成立；但 P780 kgsl 无 VBO（`GPUMEM_BIND_RANGES` 不存在）、无 sparse（`kgsl_ioctl_sparse_bind` 不存在），GPUAF 的 VBO 触发不适用；非 VBO 的 `iommu_unmap < size` 路径待找。
- CVE-2024-26923：5.4.233 < 5.4.275，`unix_gc` 未修复；触发 PoC 两轮 30s 未赢。
- 新增 48–58 号专题：init capability、artifact scan、OEM unlock final、vuln surface、CVE-2023-6931 uring、CVE-2024-26923、ABL/AVB/GSI、GhostLock 5.4、EDL programmer、CVE-2024-23373。
- 新增 `tools/abl`、`tools/afunix`、`tools/kgsl`、`tools/gsi`、`tools/partitions`、`tools/uring`、`tools/artifact-scan`、`tools/vuln-surface` 与 `evidence/20261026/`。

## 2026-10-25 — DirtyFrag 实机利用链

- 确认 CVE-2026-43284 页缓存写入原语在 P780（5.4.233）成立：有效 ESP 报文被接受并覆盖 `splice` 进来的文件页。
- 建立"只读系统库页缓存写入"能力：`libc++.so` `.rodata` 填充区改写并在另一进程验证，随后写回零恢复。
- 改写 `libc++.so` `sentry` 入口与 `libbase.so` `LogMessage` 入口，在 **init 域**与 **installd 域**（均 uid 0）取得代码执行。
- 明确能力边界：两域 `exec` 均被拒、`/data/local/tmp` 写入被拒、selinuxfs 不可写，**该早期阶段未取得交互式 shell**；后续 daemon/Elevate 已记录临时 installd UID0 成功，不能据此概括为从未取得。
- 新增 `tools/dirtyfrag-probe/`（探针、钩子桩、补丁生成、零引用扫描、调用点定位）与专题报告。
- 仓库重建：`README.md`、`docs/STATUS.md`、`docs/NEXT_STEPS.md`、`docs/EVIDENCE_MANIFEST.md`、`docs/index.md`、`docs/ARCHITECTURE.md` 全部重写为 UTF-8 并重新对齐证据。

## 2026-10-24 — IPsec / DirtyFrag 前置验证

- IPsec diagnostics v0.2/v0.3：普通 UDP 与 UDP 封装 ESP 回环 PASS；file-backed `sendfile` 到 UDP 回环 PASS。
- TINNO 5.4.61 源码审计：旧式 IPv4 `udp_sendpage` 路径、ESP no-COW 形态；明确"候选源码不等于本机实现"。

## 2026-10-18 ~ 10-20 — DSU / AVB / 策略

- AVB 测试根密钥身份核验：TEE 公钥摘要与 AOSP 默认 RSA4096 测试公钥一致。
- DSU / GSI：A/B 离线验签、B 槽安装完成、重启回原厂；随后停止。
- OEM Unlock（OEMLOCK-01/02）、原生接口、policy 边界、QAS/Mink/PFM 专题完成。
- EDL：QDL v2.8 到达 Sahara v2，Firehose 未通。

## 2026-10-10 ~ 10-11 — 早期建档

- 设备取证与去预装实验、静态样本清单、仓库结构审计。

## 2026-06-12 — 最早的公开资料

- P780 的 EDL / Sahara / Fastboot 资料：`fastboot locked`、unlock 返回 `unknown command`。
