# 变更记录

> 2026-10-25 重建：本页只保留可被仓库文件或 Actions 证据支持的里程碑。
> 早期逐条日志（含编码损坏段落）不再重排，原始内容保留在 git 历史中。

## 2026-10-25 — GhostLock 判负、能力边界与只读榨取

- GhostLock（CVE-2026-43499）：M1/M2 实机成立；M3 卡在 6 秒窗口的 prio 门与单次读限制，9 种尝试全部无效，判负。
- 内核：从 `boot_b` 恢复 41,767,424 B Image 与 173,205 个符号；修正旧偏移表整体错位一个符号。
- 能力：init/installd 域代码执行成立；init 可读 kmsg/块设备、写 `/metadata`；installd 触发可靠。
- SELinux：`security:setenforce` 无任何 allow（avc 证据），运行时 Permissive 与 tracefs/kprobe 一并关闭。
- 只读榨取：vendor_boot×2、dtbo、vbmeta×4、persist、modemst×2、fsg/fsc、devinfo、frp；AVB 根信任 = AOSP testkey，B 槽 vendor_boot 与运行内核同源。
- OEM Unlock：所有解锁命令 `unknown command`，`ro.oem_unlock_supported=1` 与 ABL 能力不符，线关闭。
- 扫描：工作区根目录 GitHub PAT 待轮换；无其它私钥/keystore。

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
