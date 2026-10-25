# 变更记录

## 2026-10-25 — GhostLock 判负、域能力边界与只读榨取

- GhostLock（CVE-2026-43499）：M1/M2 实机成立；M3 卡在 6 秒窗口的 prio 门与单次读，9 种尝试均无效，判负。
- 能力：init/installd 域代码执行成立；init 可读 kmsg/块设备、写 `/metadata`；installd 触发可靠。
- SELinux：`security:setenforce` 无任何 allow（avc 证据），运行时 Permissive 与 tracefs/kprobe 一并关闭。
- 只读榨取 9 类分区；AVB 根信任 = AOSP testkey；B 槽 vendor_boot 与运行内核同源。
- OEM Unlock：fastboot 解锁命令全 `unknown command`，线路关闭。

## 2026-10-25 — 厂商服务审计与 io_uring 候选

- Journey diag socket 对 untrusted_app / shell / installd 全部 EACCES。
- `sys.journey.diag.write_misc` shell 可写 → init 写 misc（`recovery.<value>`），已实机验证并还原。
- shell 域可 `io_uring_setup` + SCM_RIGHTS；CVE-2023-52654 未修复（5.4.233 < 5.4.264）。

## 2026-10-25 — ROM 元数据核验、离线审计工具与状态统一

- GitHub Release `p780-rom-20261025` 七个资产已全部存在；资产大小和 GitHub digest 与 `release-assets.json` 一致。
- 复核 `file-manifest.txt`：五组 tar 清单合计 4,789 个普通文件；`MISSING.txt` 32 项未被误算为已取得。
- 明确审计分层：**尚未**下载实算七个资产哈希、合并验证 Product 分卷或逐 TAR 解读真实字节；见 [ROM 审计](docs/rom/AUDIT-20261025.md)。
- 新增 [`tools/rom/verify_release.py`](tools/rom/verify_release.py)：本地 SHA-256、可选只新增 `product.tar`、只读 TAR 条目与 manifest 比对。脚本的逻辑通过小型模拟归档检查，真实 Release 运行记录待补。
- 复核本机内核 173,205 符号已有证据、ROM 路径级组件线索及受限 `installd` 域 `uid 0` shell 能力边界；见 [联合复核](docs/research/p780-rom-kernel-system-triage-20261025.md)。
- 同步 `README.md`、`docs/STATUS.md`、`docs/NEXT_STEPS.md`、`docs/rom/README.md` 的过期结论。未操作设备、未修改 Elevate 或其它 App 代码。


## 2026-10-25 — 内核符号恢复与独立核验

- 从机主Image恢复173,205个kallsyms符号；独立标准库解码核对全部名称/静态地址、256个token和677个marker。
- 文件末端恰为__bss_start，头声明长度与_end一致；1,773,056字节BSS解释大小差异，未冒称取得原厂完整debug信息。
- 生成保留原始Image字节的合成分析ELF；回读全部符号对通过。完整文件随交付包保存，Git归档工具、结果、日志和摘要。
- 无设备操作、利用执行或Root成果；[专题](docs/research/p780-kernel-symbol-recovery-20261025.md)。


> 2026-10-25 重建：本页只保留可被仓库文件或 Actions 证据支持的里程碑。
> 早期逐条日志（含编码损坏段落）不再重排，原始内容保留在 git 历史中。

## 2026-10-25 — DirtyFrag 实机利用链

- 确认 CVE-2026-43284 页缓存写入原语在 P780（5.4.233）成立：有效 ESP 报文被接受并覆盖 `splice` 进来的文件页。
- 建立"只读系统库页缓存写入"能力：`libc++.so` `.rodata` 填充区改写并在另一进程验证，随后写回零恢复。
- 改写 `libc++.so` `sentry` 入口与 `libbase.so` `LogMessage` 入口，在 **init 域**与 **installd 域**（均 uid 0）取得代码执行。
- 明确能力边界：两域 `exec` 均被拒、`/data/local/tmp` 写入被拒、selinuxfs 不可写，**未取得交互式 root shell**。
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

## 2026-10-25 — 静态修复核对与外部文章参考

- 归档已审函数/调用者反汇编和摘要：相关清理仍呈现旧式current语义，未观察到公开修复在该位置的语义；不泛化为可利用性或全部缓解审计结论。
- 纳入junyu33 Magic3文章的方法启示，区分旧CFI、厂商布局、运行时映射和权限分层；外部设备结论不转移到P780。
- 未操作设备或生成适配载荷。[报告](docs/research/p780-static-patch-review-20261025.md)。
