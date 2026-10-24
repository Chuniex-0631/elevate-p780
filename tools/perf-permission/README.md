# P780 perf 最小权限探测 v0.1.0

目标：仅验证 Android ADB shell（UID 2000）能否创建、启用、读取并关闭自身线程的用户态 perf 软件计数事件。
本版不做第二阶段采样；不采集内核地址、调用链或寄存器，不包含 GhostLock/DirtyFrag 利用。

## Windows 使用

1. 将压缩包全部解压到一个可写目录。手机正常进入 Android，开启并授权 USB 调试，只连接这一台 ADB 设备。
2. 如果平时 PowerShell 能运行 `adb`，双击 `Run-Probe.cmd` 即可。
3. 若提示找不到 adb，可在本目录打开 PowerShell，指定你已有的 platform-tools：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Run-Probe.ps1 -AdbPath '你的platform-tools目录\adb.exe'
```

执行策略选项仅作用于此次 PowerShell 进程，不修改系统执行策略。
无需 su、Shizuku、Stellar 或 KernelSU。不要在 Root ADB 环境运行：程序发现 UID 不是 2000 会拒绝检查。

脚本会临时推送并执行 `/data/local/tmp/p780-perf-permission-v0.1.0`，最后仅删除该固定文件。
日志保存在解压目录，名为 `P780-perf-permission-日期时间.log`。把完整日志发回即可。失败时不反复运行，不更改权限限制。
若设备断开，日志可能标记 CLEANUP_PENDING；保留记录，稍后在设备恢复连接后仅删除该固定文件即可。

## 检测边界

- 只有一个 `PERF_TYPE_SOFTWARE / PERF_COUNT_SW_CPU_CLOCK` 事件，pid=0、cpu=-1、独立事件、close-on-exec。
- `exclude_kernel=1`、`exclude_hv=1`，不继承子线程；不做全系统或其他进程监控。
- 无 sample_period、sample_type、采样 ring buffer、mmap、tracepoint、硬件断点或寄存器采集。
- 约 200ms 自身 CPU 运算，最多约 1 秒工作负载（受调度影响）；4 秒进程 alarm 兜底。
- 创建后逐项检查 RESET/ENABLE/DISABLE/read/close；发生错误即停止，不重试、不绕过。
- 手机端不写文件、不联网；仅计数事件与进程资源生命周期。ADB 包装脚本会暂存上述可执行文件。
- 输出 UID、架构、内核版本及计数结果，不主动读取序列号、IMEI、账户或指纹。
- 使用 Linux 静态 AArch64 ELF，免依赖手机动态链接器；仍须实机确认 Android 执行兼容性。

## 结果解释

|结果|含义|
|---|---|
|USER_COUNT_PASS|本次自身线程用户态软件计数创建、控制、读取成功且有非零计数；不证明内核采样权限|
|OPEN_DENIED|perf_event_open 返回 EACCES/EPERM；不能只凭这个错误确定是 SELinux、seccomp 或其他检查|
|OPEN_ERROR|其他创建错误，如 ENOSYS/EINVAL；记录 errno，不当作漏洞不存在|
|CONTROL_ERROR / READ_ERROR / CLOSE_ERROR|创建成功后某一阶段失败；不标为完整可用|
|OPEN_OK_COUNT_INCONCLUSIVE|打开及读取成功，但计数或运行时间为零|
|WRONG_CONTEXT|不是普通 ADB shell UID 2000，未调用 perf_event_open|
|WORKLOAD_CLOCK_ERROR|无法可靠执行定时工作负载|
|RUNNER_ERROR|电脑侧 ADB、连接、执行或文件问题，尚不能判断 perf 权限|

任何结果均不证明 GhostLock/DirtyFrag 漏洞、临时 Root、Bootloader 解锁或永久写入能力。
若 USER_COUNT_PASS，下一阶段也需要单独确定内核采样权限，不能直接运行夏普载荷。

## 源码与构建

源码为 `perf_permission.c`，独立编写，不包含夏普仓库代码或偏移。MIT 许可。
Linux 交叉工具链：GCC AArch64 + ARM64 glibc 开发库；运行 `sh build.sh`。
这里的 GCC 是用户态诊断程序编译器，与 P780 内核当年的 Clang 版本无需一致。

接口依据：https://man7.org/linux/man-pages/man2/perf_event_open.2.html
使用 64 字节 ABI v0 属性，仅用于计数。

`tests/run_tests.py` 是宿主模拟测试，覆盖通过、拒绝、接口不可用、上下文不符、控制错误、零计数、短读与读失败。
测试 mock 绝不链接到交付 ARM64 程序。详见 `VALIDATION.txt`。
