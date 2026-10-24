# P780 perf v0.1.0 实机结果（2026-10-25）

结论：**普通 ADB shell 下，自身线程用户态软件 CPU-clock 计数链 PASS。** 不是 kernel/register sampling PASS，更不是 GhostLock 可用或 Root 成功。

## 机主提供的日志

- 开始：2026-10-25T03:05:32.2261227+08:00；结束：03:05:32.9425316+08:00。
- uid/euid=2000，machine=aarch64，kernel=5.4.233-qgki-gea5245e94afe-dirty。
- PERF_COUNT_SW_CPU_CLOCK，pid=0、cpu=-1、attr_size=64；工具配置 exclude_kernel=1 / exclude_hv=1、sampling=off。
- open=PASS、close=PASS、result=USER_COUNT_PASS；probe_adb_exit=0。
- counter_ns=200523699；time_enabled_ns=200533596；time_running_ns=200533596。
- ADB push/chmod/执行及固定路径删除均 exit=0。日志中的 push 大小为635656字节；本次没有从手机独立重算ELF哈希。

原始附件：P780-perf-permission-20261025-030532.log，1411字节，
SHA-256 `88fe054056f7f0a75dccb1a990e352bc7f7142130f70ecdfc5a070c75b08e4d9`。原始附件留会话/机主；Git 的[日志副本](../../evidence/perf/20261025/user-count-v010.log)只替换机主PC绝对路径为占位符，并统一行尾，不冒称原始字节。见[提取结果](../../evidence/perf/20261025/user-count-v010.json)。

## 可推出与不能推出

日志和[工具实现](../../tools/perf-permission/perf_permission.c)相互支持：事件创建、reset/enable/disable、完整24字节读取与关闭通过；记录的非零运行时间说明不只是成功创建了fd。约200.5毫秒的计数与工具负载规模相符。

perf并未在该shell上下文中被全面阻断。但软件用户态计数和内核指令/调用链/寄存器采样是不同权限与数据路径；本轮完全未测试后者。不能依据time_running=time_enabled推断地址可见、硬件断点可用、漏洞未修补、内核布局正确、root/BL解锁或永久写入能力。

## 下一边界

不重复这一计数探测或已完成的IPsec/UDP/sendfile回环。下一项可单独设计的最小检查是：仍只对自身线程，核验包含内核执行时间的纯计数事件能否创建与运行，继续不采样、不输出地址/寄存器。该检查也不能替代完整采样权限验证；本次没有交付或执行第二阶段工具。

匹配kernel Image/源码、修复状态及布局证据缺口保持不变。AQUOS R6载荷和偏移不能直接用于P780。无Root、Bootloader仍Locked。
