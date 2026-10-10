# P780 更新服务日志与 Android Bugreport 原始证据

> 原始系统日志和 Bugreport 可能记录私有标识、APP 状态或账号信息。这里保留**必要的技术摘要和文件来源**，不在正文复刻敏感行。相关文件目前位于私有 Git 仓库的 `evidence/restricted/` 分类目录——**该目录并不提供额外 GitHub 访问权限隔离**。

| 原件 | 存放位置 | 读取结果 |
|---|---|---|
| `hand5g_update_activity.txt` | [Activity dump](../evidence/restricted/ota/hand5g_update_activity.txt) | 94,710 B，UTF-16，609 行 |
| `hand5g_update_log.txt` | [Logcat](../evidence/restricted/ota/hand5g_update_log.txt) | 283,944 B，UTF-16，607 行 |
| `hand5g_bugreport.zip` | [完整 Bugreport](../evidence/restricted/bugreport/hand5g_bugreport.zip) | 5,684,665 B，ZIP CRC 通过，含 402 个条目 |

## 当前实证的观察

- `hand5g_update_activity.txt` 是 Activity/系统状态记录，其中可见 `SystemUpdate` 相关组件名，但没有直接可复用的完整 OTA 文件。
- `hand5g_update_log.txt` 为 Logcat，含 `SystemUpdate`、`FOTA`、`DownloadManager` 等日志内容。**并未从这份 Logcat 识别出 `payload.bin` 本体或可直接使用的 OTA ZIP。**
- Bugreport 压缩包**确实存在** `FS/data/misc/update_engine_log/` 下的多份历史日志，文件名覆盖 2026 年 6、8、10 月。它们证明该设备保留过更新引擎日志，**不能据此认定某次更新已成功下载完整固件、绕过鉴权或提供未使用的刷机映像**。
- 官方 `P780AE_11.0_RMN_JP_162` 与 2024-03-21 推送起始日期另见 [官方固件专题](FIRMWARE_OTA_AND_OFFICIAL.md)；“系统记录涉及更新服务”与“取得原厂可验证固件文件”是不同等级的事实。

## 隐私及保留策略

原件目前仍保存在**Private Git 仓库**，应视为受限研究材料。未来若需要发布去身份化研究成果，先删除/脱敏敏感字段，再复查整个 Git 历史与备份分支。仅在 `main` 中删除并不能从旧 Git 对象中擦除它们。

本阶段已实际读取全部 6 份历史引擎日志：只记录 CleanupPreviousUpdateAction，没有下载 URL/payload；清理 kSuccess 不等于固件安装成功。Logcat 配置检查成功和 INSTALL_UPDATE/finished-execution 也不证明 OTA 安装。详见 [逐事件审计](2026-10-10-ota-log-audit.md)。

本节不记录未核实的下载 URL、访问令牌、手机号或设备唯一 ID。

## Journey 配置线索已完成初步代码定位

新上传实机 JAR 确认其是应用行为 XML 配置服务，所见消费者为 JourneyPerformanceService；未发现固件下载/安装链。主机/版本检查与密码学验签需区分。当前材料与下一步只读配置采集见 [Journey 审计](2026-10-10-journey-config-audit.md)。
