# P780 原始证据库（非可执行安装包）

| 目录 | 内容 | 处理规则 |
|---|---|---|
| [actions/](actions) | Clang11/14、Kconfig 的原始构建日志、配置、对象和差异 | 逐构建来源保留，不凭相同 SHA 删除其它运行的佐证 |
| [device/](device) | 实机 Tracefs 4KB 二进制 | SHA/标记已验证；不是内核基址 |
| [ghostlock/](ghostlock) | v0.1—v0.4 四份 GhostLock 离线研究 ZIP | 不重打包，保留原始字节和内部 SHA 清单 |
| [apk/](apk) | 三份实机来源 APK | 仅存档，不主动安装或分发 |
| [tee/](tee) | PFM/TZAccess 白名单与 native-api 访问记录 | 不等于任意 TEE 权限 |
| [restricted/](restricted) | 未脱敏的 Bugreport、ADB 审计 ZIP、OTA 日志与第三阶段包清单 | **仅是分类标签，不是访问控制！** 仓库应保持 Private |

新增材料和去重计算过程：[NEW_UPLOADS_AND_DEDUP](../docs/NEW_UPLOADS_AND_DEDUP.md)。历史全部文件的真实迁移状态：[EVIDENCE_MANIFEST](../docs/EVIDENCE_MANIFEST.md)。删除或重命名前查看 [ARCHIVE_PROTOCOL](../docs/ARCHIVE_PROTOCOL.md)。