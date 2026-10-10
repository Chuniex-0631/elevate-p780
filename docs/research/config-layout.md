# P780：24 项配置缺失与候选结构布局研究

日期：2026-10-10。研究对象为机主 P780 `_162` / `5.4.233-qgki-gea5245e94afe-dirty` 的已归档配置；本轮仅做离线源码核对和 GitHub Actions 编译，不连接或修改手机。

## 输入与证据等级

- 原厂配置：仓库 [evidence/device/p780-config.gz](../../evidence/device/p780-config.gz)，先前 Clang11 原生 Kconfig 工件为 5,238 项原始、24 项消失、322 项新增、已有值变化 0。
- TINNO 旧源码：`TinnoOSS/P780`，commit `20c26c7658cb5273cc71b10c3704b445b0efbe6b`，`msm-5.4` / 5.4.61。
- Qualcomm/Samsung 候选：`arminask/linux-android-samsung-a52sxq`，commit `1f58b196e0dc8de740eb45b51261ea9c5741a30e`，5.4.233。
- 结构测量使用 Android Clang 11.0.2 / r383902b1，prebuilt commit `659f7cadd7ec920e470bffbb799b031d4344c8d9`。
- 方法参考：[JingMatrix kernel-source-offsets](https://github.com/JingMatrix/pixel-ksu-root/tree/063ad1352860f0bf114bab5d7c368ee226206534/tools/kernel-source-offsets)。本仓库实现从 Kbuild 保存的 `.asm-offsets.s.cmd` 读取实际编译参数，用参数数组重编译探针，避免 `eval` 与重建编译参数。没有复制任何实机利用或写入流程。

## 24 项逐项核对

本轮对两棵固定源码扫描 C/H/S、Kconfig、Makefile 中的准确 `CONFIG_*` 引用及 Kconfig 定义。扫描命中及行号见 [原始引用清单](../../evidence/actions/2026-10-10-layout-audit/source-audit/missing-config-references.md)。未命中只适用于上述扫描范围，不推断闭源代码不存在。

| 配置（省略 CONFIG_） | 实机 | 实际源码核对与判断 |
|---|---|---|
| ABOV_SAR | y | TINNO `drivers/misc/abov/Kconfig` 定义；候选未找到相同符号 |
| AW9610X_SAR | y | 两棵公开树均未找到；旧 TINNO 树本身也不覆盖实机全部选项 |
| BATTERY_PROTECT_LIMIT | n | 两棵树均未找到；实机原本关闭 |
| EXFAT_FS | n | TINNO `fs/exfat/Kconfig` 定义；候选无同名符号；不能据此排除候选 SDFAT 等其它实现 |
| F2FS_CHECK_FS | n | 候选仍定义；依赖 `F2FS_FS && SEC_FACTORY`，原配置求解后 SEC_FACTORY=n |
| FINGERPRINT_FOCAL_FT9801_QSEE | n | TINNO 指纹驱动选项；候选无同名定义；实机原本关闭 |
| FINGERPRINT_GOODIX_GF9628_QSEE | y | TINNO 指纹驱动选项；候选无同名定义 |
| FORTIFY_SOURCE | y | 两棵树均仍定义；候选 Kconfig 的 `depends on !CC_IS_CLANG` 阻止 Clang 启用；属于真实构建行为差异 |
| INPUT_FINGERPRINT | y | TINNO 指纹菜单；候选无同名定义 |
| IPA_ETH | n | TINNO 有定义；候选残留 Makefile 引用但无同名 Kconfig 定义 |
| JEITA_WARM_OV_PROTECT | y | 两棵公开树均未找到；保留未覆盖状态 |
| LOWBATT_PWROFF | y | TINNO Qualcomm 电源 Kconfig 定义；候选无同名定义 |
| NFC_PN533_I2C | n | 候选 `drivers/nfc/pn533/Kconfig` 文件仍存在，但 Samsung 重写的上层 NFC Kconfig 未引入该文件 |
| NFC_PN533_USB | n | 同上，属于菜单可达性差异，不能记为源码目录消失 |
| NFC_QTI_I3C_GPIO | n | TINNO 有定义；候选残留 Makefile 引用但无同名定义 |
| NFC_ST54J | m | TINNO ST54J 驱动选项；候选无同名定义；实机是模块 |
| NVM | n | 候选仍定义；依赖 `BLOCK && BROKEN`，属已关闭的 Open-Channel SSD 功能，不是手机 NVRAM 分区 |
| REFCOUNT_FULL | y | 候选已无同名开关，但 `include/linux/refcount.h` 实现饱和及异常检查；不能写成引用计数保护全部丢失 |
| SCC_SUPPORT | y | TINNO 电源选项；候选无同名定义 |
| TINNO_DEMOMODECHG_CONTROL | y | TINNO 电源选项；候选无同名定义 |
| TINNO_LONGCHG_CONTROL | y | 两棵公开树均未找到；保留未覆盖状态 |
| TINNO_PRODUCT_INFO | y | TINNO `tinno/common_features/Kconfig` 定义；候选无同名定义 |
| TINNO_WARM_RECHARGE_CONTROL | y | 两棵公开树均未找到；保留未覆盖状态 |
| USB_SWITCH | y | TINNO `drivers/misc/usb_switch/Kconfig` 定义；候选无同名定义 |

总计：15 项原本启用（14 y + 1 m），9 项原本关闭。5 项在两棵公开源码中都未扫描到，其中 4 项实机启用。5 项在候选中仍有同名定义，但不出现在求解配置；其余 14 项在候选中无同名定义。

### 对布局与代码身份的意义

这些驱动开关的消失证明候选源并非完整原厂源码；本轮没有发现它们直接控制探针覆盖的 `task_struct` / `cred` / `rt_mutex_waiter` 字段声明，但这不覆盖间接依赖、所有结构及私有补丁。

`FORTIFY_SOURCE` 主要影响字符串/内存调用的编译检查；`REFCOUNT_FULL` 涉及引用计数实现。它们不能简单解释成同样数量的结构字段缺失。即使 `sizeof(refcount_t)` 一样，也不证明实现或代码生成相同。

候选树还存在 Android vendor-data/KABI 保留字段和 Samsung 修改。结构差异可能来自源码版本、厂商修改、Kconfig 条件的共同作用；两树对比不能单独归因于这 24 项。

## 可重复实验与结果

[最终完整构建 #38060518994](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38060518994) 对两棵固定树分别执行原厂配置的 `olddefconfig`、`prepare` 和 32 个结构大小/成员位置测量。不链接完整内核，不生成或刷写 boot.img。

结果由 workflow 在运行后保存到 [构建证据目录](../../evidence/actions/2026-10-10-layout-audit)，包括原始/求解配置、真实 Kbuild 命令、探针编译日志、汇编、候选 JSON、跨树对比。**具体成功/失败以该目录的实际产物为准，不把已提交流程写成编译成功。**

## 实际完成结果

最终 run **38060518994**：TINNO、A52s 的测量 job 与永久归档 job **全部 success**。两棵树分别提取 **32 / 32** 项，**0 项差异**，配置在 prepare 阶段均无进一步漂移。

| 输入树 | olddefconfig 已有值变化 | 消失 | 新增 | 探针完整性 |
|---|---:|---:|---:|---|
| TINNO 5.4.61 | 0 | 46 | 14 | 32 / 32 |
| A52s 5.4.233 | 0 | 24 | 322 | 32 / 32 |

TINNO 的 46 是本轮原生 Kconfig/Clang11 的结果，不是旧报告中静态源码符号检查的 45；不能把两种口径合并。

[完整对比表](../../evidence/actions/2026-10-10-layout-audit/runs/38060518994/layout-comparison.md) 与 [原始 JSON](../../evidence/actions/2026-10-10-layout-audit/runs/38060518994/layout-comparison.json) 已永久入 Git。采样包括 task_struct、cred、rt_mutex_waiter、rt_mutex、mm_struct、page、file、file_operations、pipe_inode_info、pipe_buffer、refcount_t 的大小或选定成员。

源文件比对另存 [核心头文件 SHA](../../evidence/actions/2026-10-10-layout-audit/source-audit/core-header-hashes.json) 与 [原始 diff](../../evidence/actions/2026-10-10-layout-audit/source-audit/core-header-diff.txt)：mm_types.h、rtmutex_common.h、pipe_fs_i.h 在两棵固定树中逐字节一致；sched.h、cred.h、refcount.h 不同。候选 sched.h 的 SEC_PERF_MANAGER 在本次求解配置关闭。

这个结果仅说明**本轮被测字段和大小**一致。即使头文件内容相同也不能代替真实 P780 的类型信息；布局相同不证明函数实现、编译后栈帧、全体字段或符号地址相同，不解除实机适配 BLOCKED。

### 保留的中间轮次

- #38060293186：TINNO 因官方脚本缺执行权限失败；A52s 输出 31 项，首项标签 TASK_SIZE 被内核同名宏展开，未通过后加的 32 项完整性要求。
- #38060466663：修复脚本执行权限后两棵树均产出 31 项；仍为缺首项的中间结果。
- #38060518994：首项改为独有名称 P780_TASK_STRUCT_BYTES，并要求 32 项全部提取，完整成功。

只修复构建脚本文件模式，不修改源码字节；模式修复列表在各 run 的 executable-mode-repairs.txt。所有中间原件保留，最终研究结论引用第三轮。

## 继续研究的关卡

1. 本轮 32 项一致；下一步优先核对原厂二进制、函数实现与栈帧。继续扩展布局探针只能扩大采样，不能替代原厂来源证据。
2. 仍需匹配 `_162` 的原厂 Image/OTA 或可信运行时类型证据；候选布局不得填入实机利用参数。
3. `vehicle-scan` 需要原厂 Image；`pagetrace` 启用事件需要 root，均不能自动消除目前阻断。

**Root / BL 解锁均未实现；P780 GhostLock 仍为 BLOCKED。**

