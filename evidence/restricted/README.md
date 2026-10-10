# 未脱敏的 P780 实机材料（需谨慎访问）

**警告：此目录不是加密文件夹。GitHub 不支持仅凭路径在同一仓库实施读权限隔离。**

这里保存机主实际设备采集的系统级记录，可能包含 IMEI/设备标识、第三方应用清单、系统日志与其它私有信息。请保留 Private，未经审核不要转为 Public 或复制到公开 Issue、论坛及第三方网盘。

- [adb/](adb)：两份原始完整审计 ZIP（各 22 / 9 个文件）以及 phase3 的包清单。与原先展开目录的字节内容一致，重复展开目录已清理。
- [ota/](ota)：SystemUpdate Activity 与 Logcat 的 UTF-16 原始文本；不是完整 OTA。
- [bugreport/](bugreport)：Android Bugreport ZIP（402 条目），包含历史 update_engine 日志和其他设备系统数据。

如需面向公众发布结论，请优先引用 [去身份化摘要](../../docs/archive/20261010-import-dedup.md) 和 [OTA 研究摘要](../../docs/research/ota-bugreport.md)，而不是引用这里的原始日志。

**重要：** 即使删除 `main` 文件，Git 历史与保留的 [清理前恢复分支](https://github.com/Chuniex-0631/p780-kernel-research/tree/archive/pre-cleanup-20261010) 中仍可含原件。要彻底删除秘密，需要跨所有 Git refs 重写历史及更新可访问的备份。
