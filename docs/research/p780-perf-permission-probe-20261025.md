# P780 perf permission v0.1.0（2026-10-25）

状态更新：**机主已提供 P780 v0.1.0 用户态计数实机 PASS 日志**，见[结果报告](p780-perf-v010-live-result-20261025.md)。下文保留工具交付阶段的范围和验证记录；内核/寄存器采样仍未测试。

## 背景与范围

AQUOS R6 [验证记录](https://github.com/mouseos/aquos-r6-ghostlock/blob/main/VERIFICATION.md)及独立 ghostlock54 实现依赖特定构建上的 perf 观测。它是第三方夏普实例，不是 P780 适配证据。P780 已知 perf_event_paranoid=-1 不等于允许 perf_event_open、内核采样或寄存器采样。

本任务只验证第一层：普通 ADB shell UID 2000 创建一个自身线程、用户态的软件 CPU-clock 计数事件，检查 RESET/ENABLE/DISABLE/read/close，并要求非零计数和启用/运行时间。无采样、内核地址/寄存器/调用链收集，不包含夏普代码或偏移，不触发 futex 利用。属性采用 ABI v0（64B）。

原生工具仅输出内核版本、架构、UID 和诊断值；Windows 脚本临时推送、chmod、运行并移除一个固定文件。不改属性/SELinux，不安装应用、不加载模块、不重启或刷写。

## 交付与验证

源码、Windows 包装脚本、构建与宿主模拟测试见 [工具目录](../../tools/perf-permission/README.md)。交付 ZIP 含静态 AArch64 ELF；Git 只存源码和构建说明，不保存该二进制。
交付 ELF SHA-256：`5ae66d2fb349462dd33661f229843c0577d3965ef65da5e2769179ed6882d98b`。

GCC 13.3.0 ARM64 静态构建通过 -Wall/-Wextra/-Werror；ELF 无 PT_INTERP，GNU_STACK 不可执行。8 项宿主 mock 覆盖通过、EACCES、ENOSYS、上下文、控制、零计数、短读与读错误。mock 不链接交付程序。原生宿主运行观察到 root 上下文拒绝。

**未进行 Android/P780 或 Windows 实机测试，未在 ARM64 模拟器执行。** 用户态诊断工具的 GCC 不要求等同设备内核的 Clang。

## 结果与停止条件

- USER_COUNT_PASS：只证明本次用户态计数链成功；kernel/register sampling 仍 UNTESTED，GhostLock 仍 UNDETERMINED。
- OPEN_DENIED：记录 EACCES/EPERM 后停止；不把错误直接归因于 SELinux，不更改限制或换身份重试。
- OPEN_ERROR / CONTROL_ERROR / READ_ERROR / CLOSE_ERROR / 零计数：按原始阶段保存，不能记为完整可用。
- WRONG_CONTEXT / RUNNER_ERROR：先保留日志，未证明普通 ADB shell 的 perf 可用性。
- 本项已收到完整设备日志，不重复本轮计数检查；不重复已完成的 IPsec/UDP/sendfile 测试，也不运行 GhostLock/DirtyFrag payload。匹配内核 Image/源码、漏洞修复与布局证据缺口保持不变。

接口依据：[perf_event_open(2)](https://man7.org/linux/man-pages/man2/perf_event_open.2.html)。
