# P780 证据归档规范

本仓库用于长期交接与跨对话续接。所有研究条目最少应说明：

1. **日期/测试环境**：实机 Android 固件与内核，或离线候选源码 commit。
2. **来源等级**：真机命令回显、用户提供的文件、软件逆向/静态分析、公开网页、模型推断。
3. **原始证据**：文件名、原始字节数、已验证的 SHA-256（如实际计算过）；仅见文件名则不要写内容已归档。
4. **实验输入与方法**：尽量只读、可重复、原命令和边界条件。
5. **实际结果**：成功/失败回显、输出路径或 GitHub Actions Run/Job ID。
6. **禁止混淆**：原源码不同版本、两台设备不同硬件、编译产物与真实运行内核、可列目录与可读文件。
7. **隐私筛查**：序列号、IMEI、电话号码、认证 token、私钥、个人通信/账号数据不得进入提交历史。
8. **不可逆风险**：任何涉及 EDL 写入、bootloader、分区操作、实机崩溃的尝试应作为独立待评估项，不得照搬网页命令。

## 目录

```text
README.md                      首要入口
docs/STATUS.md                 当前知识状态表
docs/HISTORY.md                跨月实验时间线
docs/EVIDENCE_MANIFEST.md      文件资产清单及搬迁状态
docs/{专题}.md                 按问题域拆分的详解
archive/reports/               原来的完整分析报告
archive/device/                已脱敏的真机观测
archive/tools/                 只读/历史分析工具
archive/scripts/               曾用于设备维护的历史脚本
evidence/actions/              实际 Clang 和 Kconfig 编译工件
evidence/device/               真机 Tracefs 原始字节
evidence/ghostlock/            四代离线研究 ZIP 原件
evidence/apk/                  实机提取的 3 份 APK（仅离线研究）
evidence/tee/                  PFM/TZ 白名单与 JNI 访问证据
evidence/restricted/           含潜在敏感数据的系统快照、OTA 和 Bugreport（非权限隔离）
.github/workflows/             GitHub 云端可重复检查
```

重要证据验收结论：[EVIDENCE_INTEGRITY.md](EVIDENCE_INTEGRITY.md)。

整理前历史快照：[archive/pre-cleanup-20261010](https://github.com/Chuniex-0631/p780-kernel-research/tree/archive/pre-cleanup-20261010)。新增上传文件的去重过程请参阅 [NEW_UPLOADS_AND_DEDUP](NEW_UPLOADS_AND_DEDUP.md)。原始 ZIP 内部内容不能为了美化目录随意重打包。

## 版本语义

在没有当前固件原厂内核二进制或逐构建符号证据时，GhostLock 的目标设备适配保持 `BLOCKED`；如果某个独立对象编译成功，也只是该对象在选定候选树和工具链中的构建结果。

未来将完整固件数据导入时，先生成单独来源/哈希清单，并在 `docs/STATUS.md` 标明它与真实设备版本匹配到何种程度。
