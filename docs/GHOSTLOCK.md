# GhostLock (CVE-2026-43499) / P780 适配调查

详情请查看 [2026-10-10 源码核对报告](../archive/reports/P780_GhostLock_source_audit_2026-10-10.md)。

## 源码证据及局限

- 设备内核 `5.4.233-qgki-gea5245e94afe-dirty`，而 TINNO OSS 公开的 `TinnoOSS/P780/msm-5.4` 为 **5.4.61**。
- 旧 `kernel/futex.c` 的 PI requeue → `rt_mutex_start_proxy_lock` → 失败清理逻辑，可以进入 `kernel/locking/rtmutex.c` 的 `remove_waiter` 路径；旧源码存在使用 `current` 而非 `waiter->task` 的 CVE 类似调用模式。
- 即使两份公开源码的 `rtmutex.c` 一样，也不能把它们当作对设备**运行内核二进制**的两份独立证明。
- 实机 `CONFIG_FUTEX_PI=y`, `CONFIG_RT_MUTEXES=y`, `CONFIG_ASHMEM=y`, `CONFIG_RANDOMIZE_BASE=y`; `CONFIG_CFI_CLANG=y`, `CONFIG_LTO_CLANG=y`, `CONFIG_PANIC_ON_OOPS=y`。
- [原始 `p780-cpu4.raw`](../evidence/device/p780-cpu4.raw) 4096B Tracefs 测试标记 `P780_GHOSTLOCK_PROBE`，提取一个候选地址字段。这是测试追踪原始数据、**不是 GhostLock UAF 利用结果**；不能从字段直接得出 `_text`。
- JingMatrix `entry.ghostlock@qgki-5.4` 是针对**其他手机**环境的参考实现，包含大量逐内核偏移需求；不应直接为 P780 填三星偏移。
- [v0.1–v0.4 四份原始 ZIP](../evidence/ghostlock) 已完整归档，均通过 ZIP CRC 和 SHA 校验，内嵌两份设备证据与主仓库逐字节一致。它们属于**预检和只读调查工具**，不是已验证 Root 安装包。
- `/vendor/lib/modules/5.4-gki` 可列出约 190 模块文件名，shell `u:r:shell:s0`/SELinux `Enforcing` 下读取 `modules.load` 和 `tinno_gesture.ko` 等返回 `Permission denied`。不继续重复尝试同一路径。
- 尚未取得固件 `boot.img`、`vmlinux` 或可信 `System.map`；没有应用 GhostLock 成功提权。

## 拓展：2026-10-10 GitHub 构建验证

### 与原厂工具链精确匹配的候选实验

`arminask/linux-android-samsung-a52sxq` 的 `droidian` 分支 commit `1f58b196e0dc8de740eb45b51261ea9c5741a30e`，Linux 5.4.233；Google Android Clang 11.0.2/`r383902b1` prebuilt repo commit `659f7cadd7ec920e470bffbb799b031d4344c8d9`。

| Actions | 状态 |
|---|---|
| [#38051600739](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38051600739) | Kconfig 与 Clang14 `rtmutex.o` 编译成功 |
| [#38052323798](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38052323798) | Clang14：2 值变、24 删除、327 新增；LLVM bitcode 已保存 |
| [#38053251640](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38053251640) | 精确列出差异、24 缺失、44 新启用配置 |
| [#38053176845](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38053176845) | **Clang11：0 值变、24 删除、322 新增；rtmutex.o 成功** |

这是源码可编译性和配置保存率的证据，**不是 P780 出厂二进制、运行漏洞证据或可用 GhostLock 偏移**。

## 后续关卡

参阅 [四代研究包逐版对照](GHOSTLOCK_PORT_VERSIONS.md) 与 [原始证据校验](EVIDENCE_INTEGRITY.md)。


1. 匹配真实 P780 固件的内核二进制或 OTA/镜像；核对厂商私有补丁与具体代码身份。
2. 核对 A52s 候选源码丢失的 24 个配置，包括 15 个曾启用的 TINNO 驱动/内核保护，并查清所有重要新增选项。
3. 在安全的纯离线状态进行符号和 DWARF 分析；先不要尝试实机崩溃/解锁 payload。

**利用可行性：当前 BLOCKED。**
