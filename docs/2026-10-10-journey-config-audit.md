# P780 JourneyConfigService 实机 JAR 审计

日期：2026-10-10。输入为机主新采集的 services.jar、framework.jar 与目录清单；纯离线 DEX 反汇编及调用点扫描，没有执行网络替换、服务更新、Root 或固件写入。

## 当前结论

JourneyConfigService 是 system_server 内的应用行为配置服务。已确认网络 config.xml 的消费者为 JourneyPerformanceService 的应用保活/限制判定；它不是目前已证实的 OTA 固件下载链，也不能等同于官方固件认证漏洞。

在所审查的 URL 读取、XML 解析及保存路径中，未观察到密码学签名、证书或摘要验证；观察到的校验包括 URL 最终主机一致、数字版本比较及 XML 版本一致性。明文 HTTP 和数字版本检查不构成密码学真实性验证，但静态结果没有证明可取得 Root/系统权限。

## 原件与证据范围

- 上传 ZIP CRC 通过，services.jar 为 15,353,744 B（2 DEX），framework.jar 为 30,153,054 B（4 DEX）；与目录清单大小相同。
- [输入清单及 SHA](../evidence/framework/2026-10-10/input-manifest.json) 保留每个 JAR/DEX 与上传 ZIP 的哈希。
- [54 个方法的原始指令字节](../evidence/framework/2026-10-10/journey-bytecode.json) 与 [全部 8 类反汇编](../evidence/framework/2026-10-10/journey-disassembly.txt)。
- [跨两份 JAR 的 17 个引用点](../evidence/framework/2026-10-10/journey-callsites.json)：17 是指令引用数，不是 17 个不同调用者。
- 五份采集文本在 evidence/framework/2026-10-10 保留 UTF-8 阅读视图；GMS 路径文本为空，不推断 GMS 已卸载。
- 原始大 ZIP/JAR 当前保留于机主上传文件，**未将其原始字节上传 GitHub**；仓库归档的是输入身份、方法原始字节与分析结果，不冒称原件完整入 Git。

## 已追踪流程

| 阶段 | 真实方法/字段 | 行为 |
|---|---|---|
| 启动 | SystemServer.startOtherServices → JourneyConfigService$Lifecycle | 发布 Binder 服务名 TCS，初始化服务 |
| 默认输入 | DEFAULT_FILE_PATH | vendor/etc/journey/system/config/r/ 下的 config.xml、version.txt |
| 本地缓存 | LOCAL_FILE_PATH | /data/system/journey/ 下的 config.xml、version.txt |
| 网络输入 | NETWORK_FILE_PATH | 默认 http://cdn.jstinno.com/journey/system/config/r/；从系统属性读取覆盖值 |
| 周期调度 | TCSHandler、网络 callback、Update | 常规路径检查网络是否计费，默认更新周期 24 小时；有私有调试开关，不把属性可读等同于 shell 可写 |
| 更新判定 | Update(ZZ) | 正常路径比较网络和本地数字版本；满足条件才读取 config.xml |
| 内容读取 | loadFile(URL) | HttpURLConnection 输入流；最终 URL 主机与起始主机不同则不读取内容，无所见验签步骤 |
| 解析 | loadConfigSettings(String,J,Z) | config 根，package 的 names/label/behavior/area；UpdateFrequency 与 version 的 value |
| 接受与保存 | loadConfigSettings、saveFile | XML 版本不匹配则不接受配置；接受后更新内存包名映射，条件满足时保存配置与版本 |
| 消费 | JourneyPerformanceService.isPackageAllow/isUidAllow/isSystem | 查询 ALLOW_PERSIST、NO_LIMIT、DISALLOW_BLACK_CALLER、ASSUMING_IN_SYSTEM/NOT_IN_SYSTEM |

行为枚举还包含 ALLOW_LOCATION、PRELOAD、DISABLED_COMPONENT、REJECT_ACTIVITY_WAKEUP；在这两份 JAR 的所见调用点中没有直接外部消费这些枚举的证据。不能仅依据枚举名称认定它们授予 Android 定位权限或停用实际组件。

JourneyPerformanceService.isSystem 的私有策略判断亦不能等同于 PackageManager 给应用分配 system UID 或签名权限。本轮未发现该配置服务调用 UpdateEngine.applyPayload、写 boot 分区、设置 OEM Unlock 或安装 APK 的链。

## 分析方法与限制

使用 androguard 对实际 DEX 反汇编，并扫描 services.jar/framework.jar 的全部 6 DEX 中直接引用目标类的指令。未扫描未上传的其它厂商 JAR/native 库、反射字符串消费者或运行时配置。

androguard 对 framework hidden-API 域标志存在兼容性错误。调用点扫描仅在内存解析副本中忽略 type 0xf000 的 hidden-API map 项并重算解析副本校验和；原件字节不变，清单 SHA 来自原件。目标 services classes2 的 54 个方法原始指令取自未改动 DEX。[可重复扫描脚本](../tools/scan_journey_framework.py) 明示这个处理。

反汇编偏移为方法内部字节偏移，不是内核地址或可刷写参数。静态未见验签仅限定于本轮审查路径，不扩大为全系统签名绕过结论。

## 下一步：只读确认实机配置

下列三项已由代码定位；无需再拉取整个 framework 或 GMS APK。Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force p780-journey-config | Out-Null
adb pull /vendor/etc/journey/system/config/r/config.xml p780-journey-config/
adb pull /vendor/etc/journey/system/config/r/version.txt p780-journey-config/
adb shell dumpsys TCS > p780-journey-config/tcs-state.txt
Compress-Archive -Path p780-journey-config -DestinationPath p780-journey-config.zip -Force
```

dumpsys 使用无参数的读取分支。若 Permission denied 或文件不存在，保留报错即可；不调用 update/reset/test，不尝试读取受限缓存或修改系统属性。确认默认配置与当前内存状态后，再判断保留为系统策略支线还是终止与固件主线的关联假设。

## 持续维护规则

机主要求：每个可核验阶段同步研究文件、文档和说明；修订过时结论，统一索引与状态，必要时去重，不采用只追加而不修正文档的方式。维护时明确区分 GitHub 已保存字节与只登记来源的原件。
