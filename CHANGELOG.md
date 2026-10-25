# 变更记录

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
