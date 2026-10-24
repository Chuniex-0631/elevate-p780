# P780 IPsec diagnostics 0.2.0 实机 UDP/ESP 回环结果

日期：2026-10-24（Asia/Shanghai）  
状态：**三个诊断步骤全部 PASS；测试后 IpSecService 资源计数与记录均为 0。此结果不证明 DirtyFrag 或 Root。**

## 1. 构建与设备身份

- 源码提交：`1bf4848b3571b20f07704f3d755091335d490ed5`
- GitHub Actions run：`40077884020`，结论 `success`
- artifact：`p780-ipsec-preflight-debug-apk`（artifact ID `12554320232`）
- 解包后 `app-debug.apk` SHA-256：`EB0EE55485BF8078AB7EA00EA5BAA2C8DCFFCF2ADA4B7C8F74F3D1A160CB0E76`
- ADB 序列号：`b940328a`
- 产品/型号：`P780` / `P780`
- Android API：`30`
- 指纹：`Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`

初次 `adb install -r` 被系统拒绝，原因为手机上的 0.1.0 与本次 GitHub Actions 调试 APK 签名不同：`INSTALL_FAILED_UPDATE_INCOMPATIBLE`。卸载前用普通 `run-as` 检查应用私有目录，只见空的 `cache` 与 `code_cache` 目录，没有需保留文件。随后仅卸载 `top.dcmqht.p780ipsec` 并安装 0.2.0；包管理器报告 `versionCode=2`、`versionName=0.2.0`。

未使用 ADB Root、`su`、SELinux 更改、Bootloader 操作或系统分区写入。

## 2. 第一步：只读环境检查

应用界面原文：

```text
P780 IPsec diagnostics 0.2.0
Android API: 30
Device model: P780
Kernel version: 5.4.233-qgki-gea5245e94afe-dirty
IPsec service: manager accessible
NO resource allocation; NO traffic.
Does NOT establish DirtyFrag vulnerability or root access.
```

结论：PASS。设备、内核版本与 0.1.0 基线一致，普通应用可取得 `IpSecManager`。

## 3. 第二步：临时资源检查（不发包）

应用界面资源段原文：

```text
RESOURCE PROBE (user-initiated)
1. Reserve SPI (198.51.100.1): PASS; SPI allocated
2. Open UDP encapsulation socket: PASS; bound local port 49805; no traffic
3. Create unassigned transport transform: PASS; installed temporarily, NEVER applied
Transform closed.
UDP socket closed.
SPI allocation closed.
No packets sent; no sockets assigned; no exploit attempted.
PASS indicates public API resource support only, NOT DirtyFrag.
```

结论：PASS。端口 `49805` 是此次临时分配值，不是固定设备参数。

## 4. 第三步：普通 UDP/ESP 回环诊断

应用界面诊断段原文：

```text
UDP/ESP LOOPBACK DIAGNOSTIC (user-initiated)
Scope: 127.0.0.1 only; one plain UDP datagram and one API-protected datagram.
1. Plain UDP loopback: PASS; 1 datagram sent and received
2. Public-API UDP-encapsulated ESP loopback: PASS; 1 protected datagram sent and received
Transport policies removed from diagnostic socket.
Diagnostic UDP socket closed.
Transform closed.
Encapsulation socket closed.
SPI allocation closed.
Only loopback traffic was used; no raw/malformed/fragmented packet was built.
PASS confirms ordinary API loopback only, NOT DirtyFrag or root access.
```

结论：PASS。一个普通 UDP 数据报和一个由 Android 公开 API 保护的数据报均在 `127.0.0.1` 完成发送、接收及字节比对；应用随后报告策略与所有资源按顺序释放。

## 5. 系统侧释放核对

测试结束后，未提权执行 `adb shell dumpsys ipsec`。`IpSecService` 报告 Netd 连接存活，并对列出的两个应用 UID 均显示：

- SPI、Transform、Socket、Tunnel 当前计数全部为 `0`；
- `mSpiRecords`、`mTransformRecords`、`mEncapSocketRecords`、`mTunnelInterfaceRecords` 全部为空。

这为框架服务资源已释放提供了独立于应用文本的只读佐证。普通 shell 继续读取 `ip xfrm state` 和 `ip xfrm policy` 时均返回 `Cannot open netlink socket: Permission denied`；未绕过权限、未请求 Root，因此没有直接取得内核 XFRM 表输出。

UI 自动化产生的四个 `/sdcard/p780-v02-*.xml` 临时文件已在取证副本拉回 PC 后从手机删除。0.2.0 应用保留安装状态。

## 6. 证据边界

此次成功只证明该 P780 Android 11 build 的普通应用公开 API 能完成：资源创建、双向 transport transform 绑定、一个 UDP 封装的受保护回环数据报收发、策略移除及服务资源释放。

本次没有原始 socket、手工 ESP、畸形或分片数据包、重复喷射、DirtyFrag/DFRoot 载荷、页面缓存/COW 操作或权限提升。不能据此判断运行内核是否包含特定漏洞或补丁，也不能推出 Root 或锁定态写入能力。

