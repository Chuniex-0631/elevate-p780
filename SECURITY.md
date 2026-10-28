# 私人设备研究资料的隐私与安全

本仓库记录用户本人持有的 Rakuten Hand 5G P780。**2026-10-26 本轮 GitHub API 核对当前 visibility=public；下文“已改回 Private”只描述 10-18 的历史状态，不代表当前状态。****2026-10-18 曾由 GitHub API 检测到 visibility=public；机主随后已改回 Private，经 GitHub API 再次确认。此前的公开可见性不能撤销已发生的外部访问。** Private 也不等于可以随意提交机主隐私。

**安全标注**：`evidence/restricted/` 是文件分类，GitHub 不支持通过文件夹实现细粒度读取权限。原始 Bugreport、ADB dumpsys、OTA 日志已经上传至此目录，仍可能含个人信息。即使未来从 `main` 删除，Git 历史和 `archive/pre-cleanup-20261010` 仍保存旧提交；公开仓库前必须对所有 refs 做全面审查与必要的历史重写。

后续不要额外提交 IMEI、完整设备序列号、SIM 标识、电话号码、联系人、Wi-Fi/Bluetooth MAC、登录凭据或带 token 的下载地址。本次已上传的 `hand5g_bugreport.zip` 含未经完整人工隐私审阅的系统材料，**目前只能按敏感原件管理**；将来分享时应制作独立脱敏摘要。

`archive/scripts/` 下的 PowerShell 去预装脚本会改变 Android 软件包状态，只作为历史存档，不代表推荐执行。其他机型源码编译所得的内核对象与 P780 出厂镜像不等同。

本仓库不是固件来源仓库，不应把 `evidence/apk` 中的实机 APK 当成推荐下载、安装或投产文件。TEE 采集中的 `Permission denied` 属于历史证据，不构成提升权限建议。

**2026-10-26 记录为公开；历史与附件可能已被外部访问。目录名 restricted 不提供访问隔离。** 建议机主先限制仓库可见性，再对整个提交历史、所有 refs 和二进制附件开展隐私审核；仅删除 main 的文件无法清除历史。后续若拟公开分享，应创建单独审计和脱敏完成的仓库或发布包。

研究成果包含历史临时 UID0 shell 成功记录（installd 域、Enforcing，重启后需重新触发）；永久 Root、Bootloader 解锁、完整 EDL 及可靠刷写启动链均未证实。历史 misc 固定字段写入与后续 boot_a 有限块写记录不代表任意分区可写。公开证据应使用脱敏输出、样本身份和哈希，不以读取私人数据来证明权限。

2026-10-26 审计只做风险路径盘点，没有声称全库脱敏完成，也没有改可见性、删除原件或重写历史。优先复核 `evidence/restricted/bugreport/hand5g_bugreport.zip`、`evidence/restricted/adb/*.zip`、OTA日志，以及 `evidence/20261026/partitions/` 的 FRP/misc/devinfo 原件；这些原件可能包含设备状态或身份信息。不要在公开 issue 贴出发现的秘密。处理应覆盖所有 refs、附件、release、缓存和副本；.gitignore 或删除 main 文件不能消除既有历史。

> 2026-10-28：仅整理证据措辞，未重新核验或更改仓库可见性，未完成全历史隐私审核。
