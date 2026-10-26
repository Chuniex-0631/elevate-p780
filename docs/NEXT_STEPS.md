# 下一步计划

> 2026-10-26 晚：先读[提权与刷机路线图](research/p780-escalation-roadmap-20261026.md)。
> 结论是"块写 > 解锁"：AVB 用 AOSP testkey，拿到 boot 分区写通道即可刷入自签 boot/vbmeta；
> BL 解锁在本机 ABL 上大概率死路。下面优先级 1/2 仍有效，但新增的
> CVE-2025-38352（5.4 确认受影响）与 `update_engine`/`hal_bootctl` 块写域应并行评估。

> 2026-10-26 优先顺序更新：先[ABL控制流复核](research/p780-boot-edl-audit-20261026.md)，再[Firehose/商业读取核对](research/p780-firehose-screening-20261026.md)，之后核对 UID0/Journey 边界与公开隐私。当前只做离线分析，不执行旧文档中的写分区建议。

> 2026-10-26 更新。每项都写明"要什么证据"与"什么情况下停止"，避免把推断当结论。

## 2026-10-27 当前优先

1. **6931 —— 完整 root 主线**：
   - 不依赖 A 槽启动；成功后 permissive / uid0 shell 即完整 root；
   - 已有：KASLR/sock/cred 泄漏、perf 组 u16 回绕、delta 校准；
   - 观测点已改为 `perf_read` 的 **x24**（x19 在 IRQ 关闭区，采样不可靠）；
   - 文件页缺页 + 16 页步长可校准 delta 且不移动 X；
   - ⛔ 新阻塞：values 常落在 slab 顶部，X 上方 15 槽没有活 sock；
     喷 512 sock / UDP 占 X 均失败，一次 sock churn 还导致重启；
   - ⛔ 顶部槽位策略也失败：先分配 4 个 sock 占 X 及相邻槽，再 read0，
     X1 跳到 57 槽外的另一页；SLUB 当前页 freelist 不能按“向下连续”控制；
   - **下一步 A**：直接 OOB 到 cred 的可行性——检查已知 cred 是否落在
     `X..X+67KB` 内，命中则直接 `values[index] += delta` 改
     `cred->cap_effective`，绕开 victim sock/fake skb；
   - **下一步 B**：若 X→cred 距离长期不命中，停止 6931 堆 groom；
     优先找 misc/slot 元数据写入路径，或 EDL 签名 loader。
   - 现成记录：[`OBSERVED-V-20261027.md`](../tools/uring/analysis/OBSERVED-V-20261027.md)。
2. **update_engine 路线（暂停，能力已备）**：
   - ✅ 验签绕过、任意块写都已实测；
   - ⛔ **切槽是静默 no-op**：设备只运行 `android.hardware.boot@1.1` HAL，
     update_engine / `bootctl` 请求 v1.0，v1.0 service 不存在；日志只有
     `Marking new slot as unbootable`，没有 `SetActiveBootSlot`；
   - A 槽从未真正 active；fastboot 无 set_active/flash，misc 不被 payload 接受；
   - A=build 263、B=264，A 的 boot 镜像缺失；OTA 包无法获取
     （见 [`p780-ota-recon-20261027.md`](research/p780-ota-recon-20261027.md)）。
   - **下一步**：要么提供/触发 v1.0 bootctl（或在允许域内调用 v1.1），
     要么找到能写 misc 的 vold/init 路径；否则此路线无解。
   - 已排除：`RUN_POST_INSTALL=1` 只打印成功、不执行子进程；vold 的公开
     binder 接口没有 slot/misc 方法；shell/system_app 都不能 find
     `hal_bootctl_hwservice`。
3. **EDL 只做询价/验证**：官方与商业渠道确认是否提供 TINNO/holi 签名 programmer；
   没有文件、没有真机写，就不算进展。

以下 2026-10-26 的优先级 1/2/3 转为**暂停**，保留原触发条件。
2. **EDL 只做询价/验证**：官方与商业渠道确认是否提供 TINNO/holi 签名 programmer；
   没有文件、没有真机写，就不算进展。
3. **6931 恢复条件**（满足其一再上设备）：
   - 找到两次 read 之间"零分配"的同步释放载体；或
   - 双组规模能压到不卡死且采样可统计；或
   - 换一个不依赖 values 放置的内核写原语。
   未满足前保持暂停，避免再次卡死/panic。

路线对比与详细步骤见
[`p780-full-root-routes-20261027.md`](research/p780-full-root-routes-20261027.md)。
信息层清单已收口（`p780-info-layer-20261027.md`）。

以下 2026-10-26 的优先级 1/2/3 转为**暂停**，保留原触发条件。

## 优先级 1（暂停）：CVE-2024-23373 的非 VBO unmap 失败触发

CVE-2024-23373 在 NVD 中明确覆盖 SD480；P780 的 `kgsl_mmu_put_gpuaddr` 在
`kgsl_mmu_unmap` 失败时不释放 gpuaddr、但清零 pagetable/gpuaddr，caller 随后
`kgsl_sharedmem_free` 释放 DMA/anon 页，形成 page UAF。缺的是让 `iommu_unmap`
返回 `unmapped < size` 的路径。

| 任务 | 要取得的证据 | 停止条件 |
|---|---|---|
| 读 `kgsl_iommu_unmap` 完整实现 | `guarded`/size/footprint 的 unmap 范围 | — |
| 找 `qcom_io_pgtable` 的 `tblcnt`/`ptep` 路径 | `tblcnt` 归零、ptep 提前销毁的可控入口 | 只读源码无法找到可达路径 |
| 设计非 VBO 触发 | 能稳定得到 `iommu_unmap < size` 的最小序列 | 连续 3 个候选路径均不可达则记录为负结论 |
| 触发后 | page UAF 的可观测判据（不立即接 `selinux_state`） | 触发前不进入提权步骤 |

## 优先级 2（暂停）：EDL 签名 programmer

| 任务 | 要取得的证据 | 停止条件 |
|---|---|---|
| 找 TINNO/Rakuten 签名 programmer | 根证书 PKHash = `c19a5029…`，`fhloaderparse` 通过 | 官方/第三方渠道均确认不提供 |
| 验证签名后读分区 | `read` 成功、Firehose 不 reset | 认证失败或通信失败即停 |
| 可行时刷 testkey boot/vbmeta | AVB 通过、root 持久 | 只做已验证的只读/受控写 |

## 优先级 3（暂停）：CVE-2024-26923 触发调参（可选）

| 任务 | 要取得的证据 | 停止条件 |
|---|---|---|
| 轻量预填 + 少量 SCM_RIGHTS | 连接速率与 scan 长度的平衡 | 仍无 `BUG_ON`/oops |
| 内核可见判据 | init 域 kmsg dump 抓到 `BUG_ON`/oops | 只靠设备是否重启不算 |

## 已停止（不再重复）

- GhostLock 公开车辆移植：pselect/mcast/tcp/sigreturn/process_vm/bpf 已全部判负。
- ABL 工厂菜单：无 Unlock；FFBM/QMMI 均回 Android。
- DSU / GSI 启动实验：已安装、已回原厂，失败阶段未知。
- OEM Unlock 静态扫描：296 份已完成，无新入口即停。
- EDL Sahara 盲目重试：只保留 `<programmer> reset` 单次传输验证，需先备份。

## 记录规则

任何新结论必须同时更新：`docs/STATUS.md`、`CHANGELOG.md`、对应 `docs/research/` 专题；
证据变更后重跑 `docs/EVIDENCE_MANIFEST.md` 与 `docs/index.md`。
