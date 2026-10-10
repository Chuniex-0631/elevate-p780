# P780 OTA 日志与 Journey 配置服务核对

日期：2026-10-10。只读取已归档材料，并对日志中的无鉴权公共配置地址执行 HTTP/HTTPS GET；没有连接、修改手机或重放设备鉴权请求。

## 结果

没有取得 `_162` OTA、payload.bin 或 boot.img。本轮确认了三个容易误读的“成功”事件，并识别出一个独立的厂商配置服务线索。

| 证据 | 实际观察 | 可支持的结论 |
|---|---|---|
| Activity dump | `com.google.android.gms.update.SystemUpdateActivity` | 观察到的系统更新界面由 Google Play 服务提供；不能排除其它更新组件 |
| Logcat 605–606 | Checkin code 21021，Config update succeeded | 更新客户端配置请求完成；未显示固件下载或安装成功 |
| Logcat 479–481、552–554 等 | INSTALL_UPDATE 事件触发 `finished-execution`，0.00 秒结束 | intent/action 名称不能证明固件安装发生 |
| Logcat 400、402 | DownloadManager SUCCESS；紧邻 403–404 删除 SMS denylist 缓存 | 不能把这两个成功下载归为 OTA；邻近上下文指向短信名单，日志未提供请求 URL 或下载记录的严格映射 |
| 6 份 update_engine 历史日志 | 全部启动 CleanupPreviousUpdateAction、无快照可合并、cleanup kSuccess | 成功的是清理任务；这些片段不包含固件下载、applyPayload 或签名验证过程 |

6 份日志日期为 2026-06-14（三份）、2026-08-12（一份）、2026-10-04（两份）；每份 16 或 17 行。无 HTTP URL，无 payload 引用。启动时快照状态文件缺失，随后清理成功，不据此判断有 OTA 损坏或认证绕过。

21021、21041、21042 保留为 Google 客户端内部返回码，本轮没有可靠对照表，不擅自映射为“最新版本”或错误类型。UI status=0x000 亦只记录原值。

## 新识别的 JourneyConfigService

Bugreport 主文本 15016–15021：

- 服务日志属于 UID 1000 的 system_server 进程，handler 类为 `com.journey.server.JourneyConfigService$TCSHandler`。
- 本地配置版本文件：`/data/system/journey/version.txt`。
- 实际请求地址：`http://cdn.jstinno.com/journey/system/config/r/version.txt`，无查询参数。
- 原始记录：请求出现异常，空值转换失败，network_version=0，local_version=42，判为网络版本不更新，未继续。
- 当前公共 HTTP 与 HTTPS GET 均返回 HTTP 502；工具/网络路径可能影响结果，不把它等同于原服务器已永久下线。
- 公开网页及 GitHub 搜索未定位到相关 Android 服务源码。

该服务使用明文 HTTP 的事实值得核对，但日志没有显示它下载什么配置、是否另验签、允许改变哪些系统功能，更没有固件分区写入链。**不能把它认定为 OTA 固件服务器或 2026-09-28 官方漏洞的实现。** 它运行于 system_server，优先查厂商 framework/services 代码，不能仅因没有独立升级 APK 就停止。

Bugreport 中另一个带“ota”的 gstatic URL 是 adservices UI strings 资源，不是 P780 固件。

## 原件与可复核性

- [审计结果 JSON](../evidence/analysis/2026-10-10-ota-log-audit.json)：每份引擎日志的 SHA-256、大小、路径和判定。
- Bugreport ZIP：5,684,665 B；SHA-256 `7e662b108af7b1fa33113636ef86178e5e177ce6a1eb7c498fc12daadec159dc`；ZIP CRC 全通过。
- 本轮下载的 ZIP 按 Git blob 算法得到 `25a379b25a6dcadcaca61e3389cf93dfdd881097`，与仓库原件一致。
- 两份 UTF-16 OTA 文本经连接器获得的是规范化 UTF-8 视图，行数仍为 607/609。本轮不把这个视图哈希称为原件字节哈希。
- 未提交整份解压 Bugreport、副本或敏感上下文，原件仍在既有 restricted 目录。

## 下一步所需材料

优先离线反编译含 JourneyConfigService 的实际 P780 系统 Java 代码，查看网络配置消费路径与校验，而不是尝试替换服务器响应。现有 Bugreport 没有 APK/JAR 原件。

机主可在 Windows ADB 目录执行以下只读命令：

```powershell
New-Item -ItemType Directory -Force p780-framework-audit | Out-Null
adb shell ls -l /system/framework > p780-framework-audit/system-framework-list.txt
adb shell ls -l /system_ext/framework > p780-framework-audit/system-ext-framework-list.txt
adb shell ls -l /product/framework > p780-framework-audit/product-framework-list.txt
adb shell printenv SYSTEMSERVERCLASSPATH > p780-framework-audit/systemserver-classpath.txt
adb shell pm path com.google.android.gms > p780-framework-audit/gms-paths.txt
adb pull /system/framework/services.jar p780-framework-audit/
adb pull /system/framework/framework.jar p780-framework-audit/
```

不存在的目录可能报错，保留该信息即可；JAR 若无 classes.dex，需结合目录清单再定位对应 ODEX/VDEX。本阶段无需 Root、重启、清数据或刷写，也无需提交整个 Google Play 服务 APK。

Root/BL 状态仍未改变，原厂内核来源仍未解决。
