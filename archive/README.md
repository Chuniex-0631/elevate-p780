# 旧研究成果归档

`reports/` 保存完整 Markdown 技术报告，包括 QAS/ PFМ /Mink /TZ、GhostLock 源码核对。

`device/` 保存从真机收集的内核版本、分区映射及去掉序列号的 EDL 摘要。

`tools/` 保存历史只读检查程序；`scripts/` 保存历史 PowerShell 去预装脚本。后者能改变设备状态，请不要将其当作只读命令执行。

新增机主原始审计 ZIP、Logcat、Bugreport、APK 和 TEE 材料分别保存至 `evidence/restricted/`、`evidence/apk/`、`evidence/tee/`，不再与早期去身份化摘要混合。详见 [新增原件整理说明](../docs/archive/20261010-import-dedup.md)。

原始 Tracefs 4,096B 二进制和四份 GhostLock ZIP 已存于 [evidence](../evidence)，并通过 CRC/SHA 校验；三份 APK 和完整 Bugreport 已入 Git；另有历史 APK/ZIP 与原始 framework JAR 未迁入；详细原件清单及状态见 [文件清单](../docs/EVIDENCE_MANIFEST.md)。
