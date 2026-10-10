# P780 TrustZone 白名单、JNI 访问记录及系统 APK 原件

## 来源和文件

本章节根据**机主上传到 GitHub 的真实文件**编写，并与 [2026-10-04 QAS/Mink/PFM 分析](QAS_TZ_PFM.md) 对照。静态内容与实时鉴权的成功与否必须分开看。

| 实机文件 | 当前路径 | 类型和结果 |
|---|---|---|
| `hand5g_tz_whitelist.txt` | [原始文本](../evidence/tee/hand5g_tz_whitelist.txt) | UTF-16，34 行；Qualcomm 的 TrustZoneAccess class 白名单 |
| `hand5g_native_api_paths.txt` | [原始文本](../evidence/tee/hand5g_native_api_paths.txt) | UTF-16，10 行；native 库路径的查找失败 |
| `ApeHighLights.apk` | [原始 APK](../evidence/apk/ApeHighLights.apk) | 1,704,633 B，ZIP 测试通过，265 条目，含 DEX |
| `com.qualcomm.qti.services.secureui.apk` | [原始 APK](../evidence/apk/com.qualcomm.qti.services.secureui.apk) | 24,990 B，ZIP 测试通过，6 条目，含 DEX |
| `com.qualcomm.qti.services.systemhelper.apk` | [原始 APK](../evidence/apk/com.qualcomm.qti.services.systemhelper.apk) | 16,798 B，ZIP 测试通过，6 条目，含 DEX |

## 从白名单直接可读的 class IDs

`hand5g_tz_whitelist.txt` 内包含 10 个对象：

| classId | 文件中对应名称 |
|---:|---|
| 3 | App Loader |
| 34 | PVC License |
| 62 | Device Attestation |
| 78 | Haven Token |
| 70 | RTIC App |
| 71 | RTICe App |
| 101 | Celluar Security Measures（原文拼写） |
| 102 | SCPassThrough |
| **119** | **Platform Feature Management** |
| 146 | TLOC Service |

在此**已采集的白名单文件**中，上述对象的 `permissions` 列表均为空。它只能说明该文件里的规则，没有自动证明没有 Binder UID、应用签名、运行时 service 或可信执行环境的其它鉴权。本项与 QAS 对 PFM 的 `open(119)` 静态调用相符，但**没有新的 OEM Unlock 或 Root 证据**。

## JNI 访问的阴性结果

`hand5g_native_api_paths.txt` 记录了从 ADB Shell 查询 `/vendor/lib64/libnative-api.so`、`/vendor/lib/libnative-api.so` 返回 `Permission denied`；一些系统路径返回不存在。这些消息说明**当时 Shell 权限不足**，不证明设备不存在任何相关 native 库，也不建议不断重复相同的受限操作。

## APK 的归档边界

已验证压缩容器可读、有 `.dex` 和签名元数据，但**未重新进行逐方法反编译、签名证书比对、包可安装性或动态行为验证**。`ApeHighLights.apk` 与服务项名称按原始文件名保留；文件名并不能自动证明它与 QAS Bootloader 解锁有关。

完整调用链的原始技术结论见 [QAS/Mink/TZ 专题](QAS_TZ_PFM.md)，这三份系统应用仅作为后续离线交叉核对的素材，不是建议安装或执行的文件。
