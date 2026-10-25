# 下一步计划

> 2026-10-25 重建。每项都写明"要什么证据"与"什么情况下停止"，避免把推断当结论。

## 优先级 1：新的突破点（详见 `research/p780-phase-3-closure-20261025.md` §9）

| 候选 | 要取得的证据 | 停止条件 |
|---|---|---|
| OTA / 供应链 | 拿到 TINNO 签名 OTA 包，分析 update_engine 验证与回滚 | 无法获取签名包或服务端地址 |
| EDL / Firehose | 找到匹配签名的 programmer 并完成一次读操作 | programmer 不可得 |
| installd 域宽权限 | 枚举 `(allow installd …)` 中未利用的 `relabelfrom`/`setattr` 等 | 连续 3 条候选均被策略拒绝 |
| 内核 5.4.233 其它 CVE | 用已恢复的 Image/符号定位可达点并验证触发 | 无可达触发路径 |
| ABL 镜像 | 从固件包拿到 `abl_a/b`，枚举私有 fastboot 命令 | 无镜像来源 |
| 供应商预置服务 | 审计 `QAS_DVC_MSP`、`Journey` 等本地接口 | 无新增可达入口 |

## 旧优先级 1：把 DirtyFrag 的域执行变成可用 root（已被阶段收尾取代）

| 任务 | 要取得的证据 | 停止条件 |
|---|---|---|
| 找到可写可读的中转路径 | 某目录能被目标域 `create` **且** `write`，同时 shell 可读 | 连续 5 个候选目录均被拒则记录为负结论 |
| 换权限更宽的域 | 目标域的 `exec` 与 `/data` 写入至少一项可用 | 若 `vold`/`netd` 仍无可用触发，转优先级 2 |
| 压缩载荷以适配 `liblog` | 载荷 ≤170 字节且能在 `liblog` 的 `.text` 中找到零引用落点 | `liblog` 无零填充洞且无冷门函数则放弃该载体 |

## 已完成（2026-10-25）：内核镜像与符号

- `boot_b` 已提取 41,767,424 B arm64 Image（SHA-256 `6df574af…4f373`）；
- `vmlinux-to-elf` + 独立校验恢复 173,205 个符号，旧偏移表错位一个符号已修正；
- 仍缺原厂源码，但符号级分析不再受阻。

## 旧优先级 2：补齐内核镜像（已完成）

| 任务 | 要取得的证据 | 停止条件 |
|---|---|---|
| 取得 `_162` 对应的 `boot.img` / `vmlinux` / 厂商源码 | 与实机 `uname -r`、编译时间、config 逐项吻合 | 官方与第三方渠道均确认不提供 |
| 用镜像确证 `esp_input` 是否回移共享页修复 | 反汇编或符号级比对结论 | 无镜像则保持"未判定" |

## 已完成（2026-10-25）：GhostLock 判负

- M1/M2 实机成立；M3 在 6 秒窗口内无可用观测/改写手段，9 种尝试全部无效；
- 细节见 `research/p780-phase-3-closure-20261025.md` §2。

## 旧优先级 3：GhostLock 移植可行性（已判负）

| 任务 | 要取得的证据 | 停止条件 |
|---|---|---|
| 评估 5.4 profile 的构造路径 | 明确所需字段、来源（Image/符号/偏移）与工作量 | 必须依赖原厂 Image 且 Image 无法取得 |

## 已停止（不再重复）

- DSU / GSI 启动实验：已安装、已回原厂，失败阶段未知。
- EDL Sahara 盲目重试：只保留 `<programmer> reset` 单次传输验证，需先备份。
- OEM Unlock 静态扫描：296 份已完成，无新入口即停。
- OEM Unlock 的 fastboot 入口：`flashing unlock` 等全部 `unknown command`，已关闭。
- 运行时 Permissive / tracefs / kprobe：`security:setenforce` 无 allow，已关闭。
- AVB 测试密钥身份核验：已完成，不再重复采集。

## 记录规则

任何新结论必须同时更新：`docs/STATUS.md`、`CHANGELOG.md`、对应 `docs/research/` 专题；证据变更后重跑 `docs/EVIDENCE_MANIFEST.md` 与 `docs/index.md`。
