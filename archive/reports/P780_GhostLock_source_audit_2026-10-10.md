<!-- Historical research report, preserved from an earlier user-provided artifact. Not a fresh assertion; see docs/STATUS.md. -->

# Rakuten Hand 5G (P780) / GhostLock 源码核对报告

**研究基线：** Android 11，固件 `P780AE_11.0_RMN_JP_162`，Linux `5.4.233-qgki-gea5245e94afe-dirty`，ARM64 / Qualcomm Holi。  
**核对日期：** 2026-10-10  
**资料：** 用户实机 `p780-config.gz`、`p780-cpu4.raw`；TinnoOSS/P780 公开 `master` 源码；Linux CVE-2026-43499 官方公告及修复补丁；JingMatrix/pixel-ksu-root 的 QGKI 5.4 stage。

> **总判断：** 厂商公开内核源码中的 CVE 关键错误调用链已核实；实际运行内核满足主要配置条件；Tracefs 实际泄露可疑内核代码指针已复核；但**未验证设备当前二进制内核仍包含漏洞、未取得逐构建偏移，也未实现 Root，更未解锁 Bootloader**。

## 1. 原厂源码核验：漏洞调用链具备

1. `msm-5.4/kernel/futex.c`：`futex_requeue()` 在 PI 重排路径中，以 `this->rt_waiter` 与 `this->task` 调用 `rt_mutex_start_proxy_lock(&pi_state->pi_mutex, this->rt_waiter, this->task)`。见 1916 行起的 `futex_requeue()` 和 2135 行附近的调用。
2. `msm-5.4/kernel/locking/rtmutex.c`：`rt_mutex_start_proxy_lock()` 中调用 `__rt_mutex_start_proxy_lock(lock, waiter, task)`，失败时通过 `remove_waiter(lock, waiter)` 清理；见约 1693–1704 行。
3. 同文件 `remove_waiter()` 约 1005–1053 行操作 `current->pi_lock`、`current->pi_blocked_on`，并把 `current` 传给优先级链调整。对代理锁操作，`current` 不保证是实际的 `waiter->task`。
4. Linux 官方 CVE-2026-43499 的修补要求在上述清理流程使用 `waiter->task`，与厂商公开源码中的错误模式精准对应。

**重要边界：** 源码树 Makefile 显示 `5.4.61`，设备实际是 `5.4.233`，所以这只是源代码层面的明确发现，并**不证明当前设备二进制内核没有厂商私有修补**。

## 2. 实机配置（上传的 6,576 行 config.gz 已检查）

| 要点 | 实机配置 | 对研究的意义 |
|---|---|---|
| Futex PI / RT Mutex | `CONFIG_FUTEX_PI=y`, `CONFIG_RT_MUTEXES=y` | 基本代码路径可编译 |
| 追踪接口 | `CONFIG_FTRACE=y` | 已有实机追踪数据支持 |
| Ashmem | `CONFIG_ASHMEM=y` | 对应移植利用链某些对象操作 |
| 安全防护 | `CONFIG_CFI_CLANG=y`, `CONFIG_CFI_CLANG_SHADOW=y`, `CONFIG_SHADOW_CALL_STACK=y` | 对控制流与内核对象伪造造成约束 |
| 栈与内存防护 | `CONFIG_VMAP_STACK=y`, `CONFIG_SLAB_FREELIST_HARDENED=y`, `CONFIG_SLAB_FREELIST_RANDOM=y` | 不能直接照搬其他构建的栈、堆对象布局 |
| 内核地址随机化 | `CONFIG_RANDOMIZE_BASE=y` | 需精确二进制偏移而不仅是原始地址泄露 |
| 可加载模块 | `CONFIG_MODULES=y`, `CONFIG_MODVERSIONS=y`, `CONFIG_MODULE_SIG=n` | 没有强制模块签名不代表可加载不匹配内核模块 |
| 调试与符号 | `CONFIG_DEBUG_INFO_DWARF4=y`, `CONFIG_DEBUG_INFO_BTF=n` | 有编译期 DWARF 设置，但没有可直接读取的运行时 BTF/vmlinux |
| 崩溃处理 | `CONFIG_PANIC_ON_OOPS=y`, `CONFIG_PANIC_TIMEOUT=5`, `CONFIG_QCOM_FORCE_WDOG_BITE_ON_PANIC=y` | 错误的利用可能引发强制重启；禁止用未经适配的通用 payload 碰运气 |
| 工具链 | Android Clang 11.0.2，启用 LTO | 偏移高度依赖具体构建，不可套用三星值 |

## 3. Tracefs 原始数据：再验证

`p780-cpu4.raw` 文件 **4096 字节**；Ring Buffer 提交长度字段 `52`；标记 `P780_GHOSTLOCK_PROBE` 位于文件偏移 `0x2c`；其前 8 字节位于 `0x24`，按小端解码得到候选代码指针：

`0xffffffecdc1dc9c8`

页内偏移为 `0x9c8`。这与 JingMatrix 的 Tracefs 原始 `ip` 字段回收思路一致，但**没有对应 `SLIDE_TRACE_MARK_IP_OFF` 就不能得出真实 `_text`，也不能从当前数据推算 CVE 所需其他地址**。该地址来自原先一次开关追踪、写入无害测试标记的实验，不是 GhostLock 触发结果。

## 4. JingMatrix QGKI-5.4 阶段的实际限制

`runner/stages/entry.ghostlock@qgki-5.4/stage.toml` 中：

- 标明硬件测试通过，但该阶段面向**三星 QGKI 5.4**；DEFEX、预构建内核模块与外围 App 干扰的备注都是三星案例环境，不能视为 P780 已有支持。
- `[facts].requires` 包括内核符号、结构体字段、ashmem 相关操作、虚拟和物理地址布局、内核堆配置、pselect waiter 栈布局等大量逐构建参数。这些不能单凭 `config.gz` 算出。
- 项目声明 `panic_risk = { pre_slide = "high", post_slide = "low" }`，并会临时改动内核中的 logger/ashmem 相关对象。这些步骤与此前我们做的无害 Tracefs 标记测试性质完全不同。
- 其 root 后流程依赖与目标内核 ABI/配置相符的 KernelSU 模块。P780 已启用 `CONFIG_MODVERSIONS`、LTO、CFI，不能假设其他设备模块可用。

## 5. 移植所缺的证据 / 不应跨越的条件

| 关卡 | 当前状态 | 通过标准 |
|---|---|---|
| 厂商旧源码漏洞调用链 | **通过** | 已对照 Linux 官方修复逻辑 |
| 设备编译期配置条件 | **通过主要部分** | Futex PI、RT Mutex、Ashmem、Tracefs 已确认 |
| 原始追踪代码指针 | **通过** | 二进制包含有效测试标记及前置高位地址字段 |
| 当前 5.4.233 内核仍有同一漏洞 | **未知** | 必须有真实二进制/准确的构建材料作离线对照 |
| 精确 kernel `_text` 和全部逐构建偏移 | **未知** | 需要匹配构建的可信代码/符号与验证，不得复制三星 header |
| Root/KernelSU 模块兼容性 | **未知** | 需要内核 ABI 和模块加载策略的独立证明 |
| Android root → BL 解锁 | **独立课题** | 还需额外的设备特定 ABL/安全启动漏洞，GhostLock 本身不解锁 BL |

## 6. 下一轮建议（不要求继续碰手机）

**工作包 A（优先）：** 将 TinnoOSS 旧源码和官方 CVE 修补代码做一个纯静态、最小范围的对照；梳理代理锁失败路径并确认和当前配置中 Futex PI 的对应关系。已完成核心调用链检查。

**工作包 B（主瓶颈）：** 寻找/重建与 P780 `_162` **完全匹配** 的 Linux 5.4.233 编译材料，并制定二进制一致性证据标准。旧的 `5.4.61` 源码可以用来理解构造，但重编译得到的数值**不得**用于现有设备的内核读写操作。

**工作包 C（条件性）：** 只有工作包 B 成功、且逐构建参数能严格核实，再考虑设计低风险的 P780 专项漏洞实验与可复原方案。禁止直接运行 A52s 的 `.so`、替换目标头文件中的品牌字符串，或照抄其他机器的偏移。

**风险边界：** 目前不进行任何 Bootloader、GPT、ABL、Keymaster、VBMeta、RPMB、EDL 写入；不试通用 GhostLock 崩溃 PoC。

## 来源

- TinnoOSS/P780 源码：https://github.com/TinnoOSS/P780
- 关键函数：https://raw.githubusercontent.com/TinnoOSS/P780/master/msm-5.4/kernel/locking/rtmutex.c
- Futex 调用点：https://raw.githubusercontent.com/TinnoOSS/P780/master/msm-5.4/kernel/futex.c
- 源码版号：https://raw.githubusercontent.com/TinnoOSS/P780/master/msm-5.4/Makefile
- Linux 官方 CVE 公告：https://lists.openwall.net/linux-cve-announce/2026/05/21/7
- 修复代码示例：https://lists.ubuntu.com/archives/kernel-team/2026-July/169898.html
- QGKI 5.4 stage：https://github.com/JingMatrix/pixel-ksu-root/blob/main/runner/stages/entry.ghostlock%40qgki-5.4/stage.toml
- KASLR 模块说明：https://github.com/JingMatrix/pixel-ksu-root/blob/main/cves/lib/kaslr/README.md
- 用户实机上传资料：`p780-config.gz`, `p780-cpu4.raw`。

## 可复核工具

同目录的 `p780_ghostlock_audit.py` 可对上述两份实机文件进行离线复核；如果本地下载了 TinnoOSS 源码，还可传入 `--source` 检查源代码中的基本模式。工具只读文件，不运行 exploit、没有 ADB 调用或网络请求。

```powershell
py .\p780_ghostlock_audit.py --config .\p780-config.gz --trace .\p780-cpu4.raw
# 可选：若已在当前电脑上克隆 TinnoOSS/P780
py .\p780_ghostlock_audit.py --config .\p780-config.gz --trace .\p780-cpu4.raw --source .\P780
```
