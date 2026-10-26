# 下一步计划

> 2026-10-26 晚：先读[提权与刷机路线图](research/p780-escalation-roadmap-20261026.md)。
> 结论是"块写 > 解锁"：AVB 用 AOSP testkey，拿到 boot 分区写通道即可刷入自签 boot/vbmeta；
> BL 解锁在本机 ABL 上大概率死路。下面优先级 1/2 仍有效，但新增的
> CVE-2025-38352（5.4 确认受影响）与 `update_engine`/`hal_bootctl` 块写域应并行评估。

> 2026-10-26 优先顺序更新：先[ABL控制流复核](research/p780-boot-edl-audit-20261026.md)，再[Firehose/商业读取核对](research/p780-firehose-screening-20261026.md)，之后核对 UID0/Journey 边界与公开隐私。当前只做离线分析，不执行旧文档中的写分区建议。

> 2026-10-26 更新。每项都写明"要什么证据"与"什么情况下停止"，避免把推断当结论。

## 2026-10-27 当前优先

1. **信息层收尾**：整理已有分区/模块/配置（`evidence/20261026/partitions`、
   `docs/rom/file-manifest.txt`）与各 shell 的读取边界，形成可交付清单；
   不再为单个文件烧设备。
2. **EDL 只做询价/验证**：官方与商业渠道确认是否提供 TINNO/holi 签名 programmer；
   没有文件、没有真机写，就不算进展。
3. **6931 恢复条件**（满足其一再上设备）：
   - 找到两次 read 之间"零分配"的同步释放载体；或
   - 双组规模能压到不卡死且采样可统计；或
   - 换一个不依赖 values 放置的内核写原语。
   未满足前保持暂停，避免再次卡死/panic。

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
