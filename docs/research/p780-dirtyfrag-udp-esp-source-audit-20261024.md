# P780 DirtyFrag / CVE-2026-43284：UDP sendpage 与 ESP 静态源码核对

日期：2026-10-24（Asia/Shanghai）  
状态：**公开源码路径存在；P780 running kernel 漏洞状态 UNDETERMINED；未执行 PoC / 未取得 Root。**

## 目标与边界

本轮只追踪 Linux 5.4 系列的 `udp_sendpage → ip_append_page → skb_append_pagefrags` 与 ESP 解密 `skb_cow_data` 决策。不得把“配置启用”“用户空间符号存在”升级为实际可达的页面缓存写入，更不能升级为 Root 或 BL 解锁证据。所有源码均非 `P780AE_11.0_RMN_JP_162` 的已核实原厂 running source。

## 输入和出处

| 输入 | 身份/范围 | 可信边界 |
|---|---|---|
| 实机 ADB 输出（用户 2026-10-24 提供） | Android 11；`5.4.233-qgki-gea5245e94afe-dirty`；SPL 2024-02-01；SELinux Enforcing | 直接运行时观测；不包含内核 Image |
| 实机 `/proc/config.gz`（用户提供） | `CONFIG_XFRM=y`、`CONFIG_INET_ESP=y`、`CONFIG_NET_UDP_TUNNEL=y`、`CONFIG_CRYPTO_AES=y`、`CONFIG_CRYPTO_CBC=y`；`CONFIG_MODULES=y`、`CONFIG_MODVERSIONS=y`、`CONFIG_CFI_CLANG=y`、`# CONFIG_MODULE_SIG is not set`、`# CONFIG_USER_NS is not set` | 内核编译配置，不是运行时代码或权限证明；repo 已有 `evidence/device/p780-config.gz` |
| 用户提取的 `crash_dump64` 与 `libc++.so` | 均 ELF64/AArch64；`crash_dump64` 在 `/system/bin`；`libc++.so` 含 `basic_ostream::sentry` C1 与 C2 动态符号 | 用户空间静态检查；原件当前只在会话附件，**本轮不提交二进制** |
| TINNO P780 公开源码 | `TinnoOSS/P780` commit `20c26c7658cb5273cc71b10c3704b445b0efbe6b`，`msm-5.4` / 5.4.61 | 厂商早期公开源码；**不是** 5.4.233 |
| Qualcomm/Samsung 5.4.233 候选 | `arminask/linux-android-samsung-a52sxq` commit `1f58b196e0dc8de740eb45b51261ea9c5741a30e` | 版本接近但厂商/设备不同；**不是** P780 源码 |
| Linux 上游 v5.4 | `torvalds/linux` tag `v5.4` | 历史参考，不代替 Android/QGKI 厂商实现 |
| AOSP Android 11 IpSecService | `android11-mainline-release` | 参考标准平台 API 及权限，不证明 P780 服务完整实现一致 |

## 静态代码路径：两个公开候选都具有相同的关键形态

1. `net/ipv4/udp.c`：`udp_sendpage` 在 TINNO 约第 1248–1300 行、A52s 约第 1260–1311 行，调用 `ip_append_page`；`udp_prot.sendpage = udp_sendpage`。  
2. `net/ipv4/ip_output.c`：`ip_append_page` 在 TINNO 约第 1322–1450 行、A52s 约第 1335–1460 行，调用 `skb_append_pagefrags(skb, page, offset, len)`。所见函数路径未设置 `SKBFL_SHARED_FRAG`。  
3. `net/ipv4/esp4.c`：`esp_input` 在 TINNO 约第 696–780 行、A52s 约第 695–779 行，存在 `!skb_cloned(skb)` 且非线性 skb 没有 `frag_list` 时跳过 `skb_cow_data` 的分支，并随后构建 scatterlist。**这是潜在原语相关的静态逻辑形态，不证明实际上有共享页到达。**
4. TINNO 与 A52s 在上述关键语义片段上相似，部分不同如 `READ_ONCE(up->corkflag)` 和其他维护改动；不能从这些片段推断两棵树全体实现相同，也不能断言 running P780 二进制如此。

固定引用：
- [TINNO `udp.c`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/net/ipv4/udp.c)
- [TINNO `ip_output.c`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/net/ipv4/ip_output.c)
- [TINNO `esp4.c`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/net/ipv4/esp4.c)
- [A52s `udp.c`](https://github.com/arminask/linux-android-samsung-a52sxq/blob/1f58b196e0dc8de740eb45b51261ea9c5741a30e/net/ipv4/udp.c)
- [A52s `ip_output.c`](https://github.com/arminask/linux-android-samsung-a52sxq/blob/1f58b196e0dc8de740eb45b51261ea9c5741a30e/net/ipv4/ip_output.c)
- [A52s `esp4.c`](https://github.com/arminask/linux-android-samsung-a52sxq/blob/1f58b196e0dc8de740eb45b51261ea9c5741a30e/net/ipv4/esp4.c)

## 不要简单套用 MSG_SPLICE_PAGES 的内核版本界线

`MSG_SPLICE_PAGES` UDP 支持属于较新的路径；Linux 内核邮件列表指出该提交不在 6.1.y 及更早稳定分支，且 CVE 初始受影响版本描述曾存在争议。同时，一名研究者在公开邮件列表报告使用独立 ESP 专用测试程序在 5.15.204 上成功，而 ESP 修复后 5.15.206 的相同测试失败。**这是其它 Linux 设备的测试报告，不是 P780 成功证据。**

- [LKML 讨论与实验结果](https://lists.openwall.net/linux-kernel/2026/05/11/1874)
- [CVE 公告](https://kernel.googlesource.com/pub/scm/linux/security/vulns/+/a981c8ea6a81204e4b5af022b4956719a5515424/cve/published/2026/CVE-2026-43284.mbox)

因此，“5.4 没有新 `MSG_SPLICE_PAGES` 接口”**不能单独排除**旧 `udp_sendpage/ip_append_page` 路径；反过来，“旧路径代码存在”也**不能证明**完整利用成功。

## Android API 与权限边界

Android 11 AOSP 的 `IpSecService` 支持应用持有自己的 transport-mode transform；其权限检查对 tunnel mode 更严格。实机已列出 `ipsec` Binder 服务，但并未执行应用侧 transform 建立/套接字路径的安全诊断。Android 的 `CONFIG_USER_NS` 关闭，使依赖 user namespace/CAP_NET_ADMIN 的桌面 Linux PoC 不可直接照搬。

- [AOSP Android 11 IpSecService](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/android11-mainline-release/services/core/java/com/android/server/IpSecService.java)

## 附加实机边界（2026-10-24）

- `/proc/sys/kernel/modules_disabled` 与 `kptr_restrict` 从 shell 读取均为 Permission denied；不表示值为 0 或 1。
- `/system/bin/crash_dump64` 存在，SELinux label `crash_dump_exec`；`/apex/com.android.runtime/bin/crash_dump64` 不存在。
- `/system/lib64/libc++.so` 存在且动态符号表包含 DFRoot 文档涉及的 `sentryC1ERS3_`。
- `/vendor/bin/insmod` 是 `toybox_vendor` 的符号链接；普通 shell 对目标读取受到拒绝；存在命令并不意味着有模块加载权限。
- `/vendor/lib64/libbinderdebug.so` 不存在；现有 DFRoot 日志中的暂存路径不能照搬。
- DFRoot Android 预编译模块集不包含 P780 的 Android 11 / 5.4 QGKI，`CONFIG_MODVERSIONS` + CFI 导致跨设备模块风险显著。

## 证据矩阵与结论边界

| 命题 | 等级 | 结论 |
|---|---|---|
| 两棵公开 Linux 5.4 源码具有 UDP `sendpage` → page frags → ESP no-COW 分支 | 公开源码直接观测 | YES（仅限明确固定版本） |
| P780 内核启用了 ESP/XFRM/AES-CBC | 设备 config 直接观测 | YES |
| P780 用户空间具备 C++ 目标符号与 crash_dump 可执行文件 | 提取 ELF/ADB 直接观测 | YES |
| P780 5.4.233 running binary 与任一公开源码相关函数逐字节相同 | 未证实 | UNKNOWN |
| P780 普通应用能完成 UDP page-cache page 的零复制传递及 ESP 解密原语 | 未动态测试 | UNKNOWN |
| P780 可由 DirtyFrag/DFRoot 临时 Root | 未验证 | NO SUCCESS EVIDENCE |
| Root 可永久解锁 Bootloader/改写签名分区 | 不可推出 | NO |

## 下一阶段一个最小任务

**源代码身份/实现核验（优先只读、离线）：** 若后续取得与 `_162` 构建匹配的授权内核 Image、`vmlinux`、或经过可核实溯源的 5.4.233 P780 厂商源码，优先核对 `udp_sendpage`、`ip_append_page`、`esp_input` 三处实现及对应编译选项。当前不再重复受拒绝的 `/proc/sys`、`/vendor/bin` 探测，不拿候选源码当运行中事实。

若另行决定制作手机侧诊断，仅允许显式只读/无恶意载荷的功能检查并单独评估风险；不运行通用 DirtyFrag APK，不修改系统页面缓存，不加载内核模块，不刷写 Boot/AVB/EDL。


## 2026-10-24 追加：普通应用 IPsec API 安全预检工具

- 已提交独立 Android 11 Java 预检工具：[tools/ipsec-preflight-android](../../tools/ipsec-preflight-android/README.md)。只读按钮仅查看系统版本、内核版本与 `IpSecManager` 是否存在。
- 另一按钮仅在用户主动触发时，短暂申请 SPI、UDP 封装套接字与 AES-CBC/HMAC-SHA256 transport transform；资源于 `finally` 中回收，**不会绑定网络连接、发送 ESP/UDP、触碰 page cache 或使用提权载荷**。这属于可逆的临时内核状态分配，**并非严格只读**，设备端执行前必须经机主确认。
- [GitHub Actions 运行 40068867263](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/40068867263)：Gradle Android APK 编译及 artifact 上传成功；这是**构建证据**，另有第一项只读实机回传（见下）。SPI/UDP/Transform 资源接口仍未执行。
- 即使 transform 建立成功，也不能推出 ESP 收包 zero-copy/COW 原语或 DirtyFrag 可利用；失败也不能排除内核代码路径。对本机漏洞状态继续标注 **UNDETERMINED**。


## 2026-10-24 追加：P780 实机第一项只读检查（用户手工回传）

**来源/信任边界：** 机主将已安装的 `P780 IPsec Preflight 0.1.0` 应用屏幕结果原样复制到本项目聊天；这不是由仓库 CI、独立 ADB 脚本或可核验日志自动采集。

```text
P780 IPsec preflight 0.1.0
Android API: 30
Device model: P780
Kernel version: 5.4.233-qgki-gea5245e94afe-dirty
IPsec service: manager accessible
NO resource allocation; NO traffic.
Does NOT establish DirtyFrag vulnerability or root access.
```

**已观测：** API 30、型号与先前基线一致；普通应用成功通过 `getSystemService(IpSecManager.class)` 获得非空管理器实例。

**不能推出：** 该按钮未调用 `allocateSecurityParameterIndex`、`openUdpEncapsulationSocket` 或 `buildTransportModeTransform`，因此未证实 Binder 服务实际分配资源、内核 ESP/XFRM 配置可用、收包原语存在或 DirtyFrag 可利用。资源分配按钮等待机主单独同意，暂未触发。DirtyFrag 状态仍为 **UNDETERMINED**。
