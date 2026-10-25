# P780 下一步计划（2026-10-25 复核更新）

> 以 [STATUS](STATUS.md) 为唯一当前状态入口。此前“缺内核 Image / 符号”“尚未取得任何 Root Shell”的阻塞条件均已被新实机记录更新；旧方案不可再作为当前进度。
>
> **本阶段不修改 Elevate，不操作手机，不尝试写入分区。** 先验证归档真实字节，再开展静态分析，最后维护清晰的权限能力边界。

## 阶段 1：ROM Release 完整性（优先进行）

| 工作 | 已有证据 | 下一步验收标准 |
|---|---|---|
| Release 上传确认 | 七个资产全部存在，size / GitHub SHA-256 digest 与 JSON 一致 | **已完成（元数据层）** |
| 文本清单审计 | 4,789 个普通文件条目自洽，32 项 system 缺口未误列 | **已完成（文本层）** |
| Product 分卷重组 | part1 1,700,000,000 B + part2 1,558,192,896 B；完整 tar SHA 已记录 | 用真实文件顺序拼接；长度 3,258,192,896 B，实算 SHA-256 与 `SHA256SUMS.txt` 相同 |
| 归档逐字节与条目核验 | [离线工具](../tools/rom/verify_release.py) 已入库 | 对七个本地资产实算 SHA-256；逐 TAR 遍历，与 manifest 匹配；保存运行日志 |

指引：[ROM 审计](rom/AUDIT-20261025.md)。如资产不可下载或校验失败，应记录 **BLOCKED/FAIL**，不能写“已验证”。

## 阶段 2：内核与系统组件离线基线

| 工作 | 已有证据 | 下一步验收标准 |
|---|---|---|
| 内核身份与符号 | 本机 `kernel.Image`，173,205 个符号恢复及独立核验 | 保留原始 Image SHA、验证 JSON；不把静态地址当成运行时 KASLR 地址 |
| 静态修复审计 | 局部函数检查未观察到公开修复相应语义 | 报告仅指已审范围；任何扩展结论需有新二进制证据 |
| ROM 的 APK / native / init 信息 | 各分区的清单路径和大小已有 | 下载并核验资产后，在副本上记录 ELF/DEX/APK 元数据与 SHA，保留原文件不修改 |
| SELinux / VINTF | 既有 CIL 与 46 份 XML 的采集记录 | 区分静态声明、缺失文件与实际服务；不将 XML 可解析等同于整机兼容 |
| 厂商缺口 | `MISSING.txt` 的 32 项及 vendor 大量读取失败 | 明确缺口来源及影响；不宣称获得完整镜像 |

专题：[只读组件/权限复核](research/p780-rom-kernel-system-triage-20261025.md)。

## 阶段 3：Root 能力边界和文档同步

已有实机证据：`uid=0(root)`、SELinux `u:r:installd:s0` / Enforcing、部分 `/data` 路径可读写、`/system/bin/sh` 可运行；重启后不持久，不等于有完整 root、Bootloader 解锁或分区写通道。

1. 对外统一称为“受限、临时 `installd` 域 UID 0 shell”。
2. 静态及实机结论分栏，声明已测操作和失败操作，不能从 UID 0 推断未测试能力。
3. 已同步：[README](../README.md)、[STATUS](STATUS.md)、[Root Shell 原始报告](research/p780-installd-root-shell-20261025.md)和本计划；本轮不新增权限实验。

## 当前不重复的任务

- 不重复提取已经取得的 `kernel.Image` 或再次从零恢复同一符号表。
- 不重复 DSU/GSI 启动实验、EDL Sahara 盲试、无新入口的 OEM Unlock 静态扫描。
- 无原厂完整源码时，不把 TINNO 5.4.61/A52s 5.4.233 当本机同构建源码。
- 不修改 Elevate、自动触发逻辑或其它应用代码。

## 记录规范

新的二进制“PASS”必须附输入大小、完整 SHA-256、执行步骤、实际输出和缺失项。需更新 `docs/STATUS.md`、`CHANGELOG.md` 与对应研究专题；若改变 `evidence/` 再更新 `EVIDENCE_MANIFEST.md`，新增文档须纳入索引。

## 阶段 4：io_uring CVE-2023-52654（当前主战线）

| 工作 | 已有证据 | 验收 / 停止条件 |
|---|---|---|
| 触发可行性 | shell 域可 `io_uring_setup` + `socketpair` + `sendmsg(SCM_RIGHTS ring)`；本机 5.4.233 未含 5.4.264 的修复（`io_destruct_skb` 符号在场） | 能稳定触发内核异常/崩溃 |
| 触发 → 利用 | 目标是把 `struct file` UAF 做成任意读写 | 连续 10 次无异常则标记“不可触发” |
| 域逃逸 | 任意读写后改写 `selinux_state.enforcing` | 一次绕过整份策略 |
