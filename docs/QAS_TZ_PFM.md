# QAS → Mink → PFM → TZAccessService：已知事实索引

2026-10-04 对真实 P780 提取的应用、库与日志进行静态分析，详细原始报告已永久提交至：

- [QAS / PFM 完整报告](../archive/reports/P780_PFM_QAS_2026-10-04.md)
- [MinkNative 完整报告](../archive/reports/P780_MinkNative_2026-10-04.md)
- [TZAccessService 完整报告](../archive/reports/P780_TZAccess_2026-10-04.md)

## 路径关系（已定位）

```text
QAS_DVC_MSP (com.qti.ltebc)
  └─ LTELicenseManager.processLicenseCheck
     └─ MinkSocketFd / TZAccessService Binder service
        └─ IMinkSocketFd.request(...)
           └─ nativeGetEnvHandle(remoteSocket, callerName, credentials, whitelist)
              └─ IClientEnv.Proxy.open(classId=119)
                 └─ IPFM.Proxy.CheckInstalledLicense(featureId=700 / eMBMS)
```

相同 class 119 的 XRVD 调用 feature 2100（XR 相关）；XRVD 的 `IPFM object created successfully` 运行日志表明代理对象已经创建，但**不代表许可证通过或具备任意类权限**。

## 服务端进一步查出的条件

- TZAccessService 从 `/vendor/etc/ssg/tz_whitelist.json` 读取 classId 与 permissions 条目。
- Binder UID/PID 及 PackageManager 身份信息进入凭据采集；请求中的 callerName 不是攻击者任意替代真实 Binder UID。
- CBOR 载荷包括 UID、时间、应用 flags、包名、签名证书和授权权限（按调用路径决定）。
- 当 remoteSocket 为 null/空或带 `ssgtzd` / `qwes_ipc` 时走 `nativeGetEnvHandle`；其他非空字符串走 `nativeGetOpenerHandle`。
- 客户端 native 转发代码识别 `SO_PEERCRED`，但不等于已查清安全世界的所有鉴权。

## 阴性发现同样重要

未在已分析的 Java/DEX/JNI 路径中定位到将 PFM 功能许可写入 **OEM Unlock / FRP / Bootloader** 状态的调用。无法据此断言整个 TEE 绝无相关代码，只是说**当前提议的 QAS 解锁路线没有得到证据支持**。未尝试任意 license 写入和 classId 乱试。

## 后续

离线阅读已上传 TZ APK 和 JNI 样本仍可补充调用链；如真正分析 ROM 启动鉴权，应另行取得匹配 P780 固件的可信二进制，不将 QAS 与 BL 解锁等同。
