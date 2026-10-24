# P780 DirtyFrag：v0.2 回环证据的含义与下一道安全门

日期：2026-10-24（Asia/Shanghai）  
状态：**普通应用 IPsec 保护回环已实机 PASS；UDP file-backed sendpage 路径和 DirtyFrag 页面缓存写入原语仍未验证。**

## 1. 本轮基线

- v0.2 源码提交：[1bf4848](https://github.com/Chuniex-0631/p780-kernel-research/commit/1bf4848b3571b20f07704f3d755091335d490ed5)。
- 实机结果归档：[P780 IPsec diagnostics 0.2.0 实机 UDP/ESP 回环结果](p780-ipsec-v0.2-live-loopback-20261024.md)。
- GitHub Actions 构建：[run 40077884020](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/40077884020)，结论 success；artifact `p780-ipsec-preflight-debug-apk`，artifact ID `12554320232`。
- 报告记录的解包 APK SHA-256：`EB0EE55485BF8078AB7EA00EA5BAA2C8DCFFCF2ADA4B7C8F74F3D1A160CB0E76`。
- 设备：P780，Android API 30，内核 `5.4.233-qgki-gea5245e94afe-dirty`。

## 2. v0.2 实机 PASS 证明什么

实机报告记录：

- 普通 UDP loopback：一个数据报发送、接收并完成字节比对。
- Android 公共 API UDP-encapsulated ESP transport loopback：一个受保护数据报发送、接收并完成字节比对。
- 入站/出站 transform 策略随后移除；诊断 socket、transform、封装 socket 与 SPI 释放。
- 之后的普通 shell `dumpsys ipsec` 记录中，相关 UID 的 SPI、Transform、Socket、Tunnel 计数均为 0，记录列表为空。读取内核 XFRM netlink 表仍因权限拒绝而未完成。

**结论：** 在这台 Android 11 build 上，普通应用通过 `IpSecManager` 完成了一次标准的 UDP-encapsulated ESP transport-mode 本机回环。它比仅创建 SPI/Transform 更进一步，支持正常 IPsec 保护数据路径在该配置下可用。

**证据边界：** 这是应用输出与非提权 `dumpsys ipsec` 的记录，不是内核 trace。它不证明运行内核源码身份，也不直接证明特定内核函数一定以预期分支执行。

## 3. 为什么这仍不是 DirtyFrag 测试

v0.2 的 Java 代码把一个普通 `byte[]` 包装成 `DatagramPacket`，通过 `DatagramSocket.send()` 发送。它没有使用文件描述符作为数据源，也没有调用 `sendfile()`、`splice()` 或构造原始 ESP。

DirtyFrag 的相关页面缓存原语依赖的是**文件支持页面进入 UDP skb/page-frag 路径，并在 ESP 解密时出现不应发生的原地写入**。普通的 IPsec 回环没有建立这项关键条件；因此 v0.2 不能确认或排除 CVE-2026-43284。

## 4. 上游修复与候选源码的对照

上游修复提交 [f4c50a4034e62ab75f1d5cdd191dd5f9c77fdff4](https://github.com/torvalds/linux/commit/f4c50a4034e62ab75f1d5cdd191dd5f9c77fdff4) 涉及两类保护：

1. IPv4/IPv6 的 IP append 路径在相应共享页面条件下标记 `SKBFL_SHARED_FRAG`（除非明确使用 `MSG_NO_SHARED_FRAGS`）。
2. `esp4_input` / `esp6_input` 的不复制快速分支增加 `!skb_has_shared_frag(skb)` 条件。

既有静态审计记录：TINNO P780 5.4.61 与 Samsung A52s 5.4.233 候选树的相关片段仍具有 UDP `sendpage → ip_append_page → skb_append_pagefrags` 与 ESP no-COW 代码形态；当前尚未把任何候选树证明为 P780 `_162` 的 running source。故这属于**候选源码的正向风险线索**，不是实机漏洞确认。

上游参考：
- [DirtyFrag 技术项目与受影响版本说明](https://github.com/V4bel/dirtyfrag)
- [Android DFRoot 的机制概述](https://github.com/diabl0w/DFRoot)
- [固定的上游修复提交](https://github.com/torvalds/linux/commit/f4c50a4034e62ab75f1d5cdd191dd5f9c77fdff4)

## 5. 下一道低风险验证门

若继续做手机侧诊断，建议先制作一个**纯 UDP、无 IPsec 的 file-backed sendfile 回环探针**，而不是直接运行 DirtyFrag：

- 在应用私有 cache 目录创建一份短暂测试文件。
- 通过普通应用权限，用文件描述符向 `127.0.0.1` 的 UDP 接收 socket 发送一次数据。
- 接收端比较完整数据；发送前后校验文件内容/哈希相同。
- 关闭 socket、删除临时文件；失败时记录 errno，不重试喷射、不构造 ESP、不访问系统文件。

该探针只用于检查普通应用是否能把文件支持的数据送入 UDP socket 的 sendpage/splice 路径。**PASS 仍不等于共享页进入 ESP 解密，更不等于 DirtyFrag 可利用；FAIL 也可能只是 Android/内核 API 限制。** 构建可以先在 CI 完成，安装和运行前须再次由机主明确确认。

## 6. 停止边界

当前没有执行 DirtyFrag/DFRoot payload，没有页面缓存修改、Root、模块加载、SELinux/Bootloader 更改或分区写入。由于仍缺可信原厂 recovery image 与 running kernel 源码身份，暂不建议直接运行通用 DirtyFrag APK。

最终状态继续为：**DirtyFrag = UNDETERMINED；Root 未取得；Bootloader 仍 Locked。**
