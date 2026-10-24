# P780 IPsec Preflight 实机结果与内核版本后缀来源核验

日期：2026-10-24（Asia/Shanghai）  
状态：**Android 11 应用侧资源检查全部 PASS；内核源码身份与 DirtyFrag 可利用性仍 UNDETERMINED。**

## 一、输入、出处与限制

1. 机主在 P780 Android 11 原厂 release 系统安装了仓库 [IPsec Preflight 0.1.0](../../tools/ipsec-preflight-android/README.md)，依次运行只读与资源检查按钮，并将界面输出原样复制到对话。**本文件仅是机主提供输出的忠实归档，不是独立 ADB 抓取或经外部复验的日志。**
2. 机主此前上传的真实 `/proc/config.gz`（本地复查其压缩配置），内核 `uname -a` 和系统指纹。
3. 固定源码：TINNO [P780 master / 20c26c7](https://github.com/TinnoOSS/P780/tree/20c26c7658cb5273cc71b10c3704b445b0efbe6b) 与 Linux [v5.4 / scripts/setlocalversion](https://github.com/torvalds/linux/blob/v5.4/scripts/setlocalversion)。

未运行 DirtyFrag/DFRoot PoC；未发 ESP 数据包、绑定 transform 到任何网络连接、读写 kernel pagecache、加载内核模块、刷写系统分区或改动 Bootloader。

## 二、第二项资源检查：机主回传原文

```text
P780 IPsec preflight 0.1.0
Android API: 30
Device model: P780
Kernel version: 5.4.233-qgki-gea5245e94afe-dirty
IPsec service: manager accessible
NO resource allocation; NO traffic.
Does NOT establish DirtyFrag vulnerability or root access.

RESOURCE PROBE (user-initiated)
1. Reserve SPI (198.51.100.1): PASS; SPI allocated
2. Open UDP encapsulation socket: PASS; bound local port 43964; no traffic
3. Create unassigned transport transform: PASS; installed temporarily, NEVER applied
Transform closed.
UDP socket closed.
SPI allocation closed.
No packets sent; no sockets assigned; no exploit attempted.
PASS indicates public API resource support only, NOT DirtyFrag.
```

注：开头 `NO resource allocation` 属于程序复用的**第一项只读环境段落**；下面 `RESOURCE PROBE` 明确进行了临时资源分配，并非同一次操作的矛盾结果。UDP 端口 43964 是该次测试的临时本地端口，不是厂商固定端口或漏洞参数。

| 命题 | 证据层级 | 当前结论 |
|---|---|---|
| P780 普通应用可取得 `IpSecManager` | 机主提供的应用输出 | PASS |
| `allocateSecurityParameterIndex(198.51.100.1)` 返回成功 | 机主提供的应用输出 | PASS |
| `openUdpEncapsulationSocket()` 返回成功，取得本地端口 | 机主提供的应用输出 | PASS |
| `buildTransportModeTransform(...)` 返回成功 | 机主提供的应用输出 | PASS |
| `close()` 对三个资源执行完毕 | 机主提供的应用输出 | 有关闭成功日志；未独立核验内核净状态 |
| ESP 接收、共享页面及 COW 决策受到动态执行 | 本测试未触发 | UNKNOWN |
| DirtyFrag 可利用、Root 或锁定态永久写入 | 无相应结果 | **NO SUCCESS EVIDENCE** |

**合理推断：** Android 用户态 IPC、系统 IPsec 服务及其正常资源创建路径没有在上述操作中拒绝普通应用；这缩小了可达性限制，但不能把 API 层 PASS 升级成特定 ESP/COW 数据路径已触发。Transform 从未应用到实际 socket，更未发送数据包。

## 三、内核 `-qgki-gea5245e94afe-dirty` 的来源解释

同一实机压缩配置的相关精确行：

```text
CONFIG_LOCALVERSION="-qgki"
CONFIG_LOCALVERSION_AUTO=y
CONFIG_IKCONFIG=y
CONFIG_IKCONFIG_PROC=y
```

公开 Linux v5.4 与 TINNO P780 5.4 源码的 `scripts/setlocalversion` 均包含：

- `CONFIG_LOCALVERSION` 附加自定义 `-qgki`；
- `CONFIG_LOCALVERSION_AUTO=y` 时使用 `scm_version()` 附加源代码管理信息；
- 有 Git 仓库且未能用标签匹配时，可能追加 `-g` + `git rev-parse --verify --short HEAD`；
- Git 工作树状态显示受检范围内存在未提交变动时，可能追加 `-dirty`；也可以从已有 `.scmversion` 文件直接读取后缀。

因此 `gea5245e94afe` **符合构建时 Git 提交缩写的形态**；`-dirty` **与构建时源码树含本地变更一致**，但并不能得知改了哪些文件、何时发生变化，更不能推出漏洞补丁状态。厂商构建脚本可能另有定制，或使用预生成 `.scmversion`；上述为有源码依据的解释，不是运行二进制身份认证。

本轮检索边界：

- TINNO 公开 P780 仓库经 API 仅发现 `master` 分支，固定提交 `20c26c7658cb5273cc71b10c3704b445b0efbe6b` 日期 2021-07-10；其 `msm-5.4/Makefile` 版本是 **5.4.61**，不是本机 **5.4.233**。
- 向 GitHub API 分别查询 `TinnoOSS/P780`、`aosp-mirror/kernel_common`、`torvalds/linux` 中的 `ea5245e94afe` 均未能解析到提交，返回 `No commit found for SHA`。广域网页搜索亦无可信精确命中。**这不排除该缩写属于其他公开/私有 Git 仓库**。
- 此轮未拿到与 `P780AE_11.0_RMN_JP_162` 对应的 `Image`、`vmlinux`、源码清单或完整 SHA；**不能从缩写验证运行中 `udp_sendpage`、`ip_append_page` 或 `esp_input` 的具体字节实现**。

## 四、下一步与停止条件

本阶段在设备端已经得到足够的**公开 IPsec API 基础能力**证据；不再重复测试或扩展到构造 ESP/UDP 载荷。最小后续任务：仅当获得可核实来源的 P780 5.4.233 内核二进制/源码或该提交的可验证映射时，离线固定其版本、比较上述三个函数及补丁状态。拿不到身份材料就保持 **UNDETERMINED**，不根据候选源码或版本后缀推断 Root 可行。
