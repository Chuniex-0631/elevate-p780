# 来源、引用和可重复性

## 一手实机材料

仓库主来源：实际持有的 TINNO P780，从 2026-06-12 至 2026-10-10 各阶段采集的 ADB、Fastboot、Sahara 和应用/内核证据。

- `p780-config.gz`（39,170 B，已提交于 repo root），Actions 记录校验 SHA-256：
  `0ff9cbb1844e043e1211b527509f5f435862cace25649bab6641d5d62c7bbce0`。
- [`evidence/device/p780-cpu4.raw`](../evidence/device/p780-cpu4.raw)：实机 Tracefs 4,096 字节原件；标记和 SHA 校验通过。
- [`evidence/ghostlock`](../evidence/ghostlock)：v0.1—v0.4 四份原始 ZIP，包含分阶段预检、内部回归测试和同源设备证据。
- `archive/device/hand5g_kernel.txt`：实机 `/proc/version` / `uname` 输出整理。
- `archive/device/hand5g_byname.txt`：真实 `/dev/block/by-name` 符号链接记录。
- `archive/device/P780_EDL_2026-06-12_sanitized.txt`：六月 EDL 及 Fastboot 摘要，去掉设备独有标识。
- `archive/reports/P780_PFM_QAS_2026-10-04.md`：从用户提取的 APK/Dex 得到的 eMBMS 许可链。
- `archive/reports/P780_TZAccess_2026-10-04.md`：从实际 APK/Dex 得到的服务端凭据传递与白名单分析。
- `archive/reports/P780_MinkNative_2026-10-04.md`：从用户提取的 JNI 库与应用日志得到的结果。
- `archive/reports/P780_GhostLock_source_audit_2026-10-10.md`：实机配置+tracefs 原始数据+旧源码交叉核对。
- 已迁移原件的 CRC、哈希及内嵌副本校验见 [证据完整性](EVIDENCE_INTEGRITY.md)；**其它**尚未迁移的文件详见 [文件清单](EVIDENCE_MANIFEST.md)。

## 本次新增真实资料来源（2026-10-10）

- [ADB 去预装与综合审计两份完整原件](../evidence/restricted/adb)：其中 ZIP 原始数据与此前上传的展开目录逐文件 SHA-256 相同，去重删除了展开的 31 份重复文件。
- [TEE 白名单和 JNI 受限路径回显](../evidence/tee)、[三份 Android APK](../evidence/apk)：只作为设备采集资料，不等于 APK 动态行为和权限安全性已完成验证。
- [OTA/Activity/Logcat 和完整 Bugreport](../evidence/restricted)：原始字节已入 Git，但因潜在隐私信息未经发布级脱敏；具体内容与结论见 [OTA/Bugreport 专题](OTA_LOGS_AND_BUGREPORT.md)。
- 本轮分类规则、同名 ZIP 版本大小差异见 [接收与去重记录](NEW_UPLOADS_AND_DEDUP.md)。

## 上游项目源码（只作版本参考）

- [TINNO P780 内核源码](https://github.com/TinnoOSS/P780) `master/msm-5.4`，Makefile `5.4.61`。
- [Samsung/Qualcomm Android 5.4.233 候选](https://github.com/arminask/linux-android-samsung-a52sxq) `droidian`，研究固定 commit `1f58b196e0dc8de740eb45b51261ea9c5741a30e`。
- [Google Android Clang 11 prebuilt](https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86/) `android11-qpr2-release/clang-r383902b1`，研究记录 commit `659f7cadd7ec920e470bffbb799b031d4344c8d9`。
- [GhostLock 参考项目](https://github.com/JingMatrix/pixel-ksu-root) 的 `entry.ghostlock@qgki-5.4`，**不支持推断 P780 已适配**。
- [Linux CVE-2026-43499 公告](https://lists.openwall.net/linux-cve-announce/2026/05/21/7) 与修复示例：仅用于核对公开源码中的模式。

## 官方厂商信息

- [Rakuten Hand 5G 官方固件更新列表](https://network.mobile.rakuten.co.jp/information/software/rakuten-hand-5g/)
- [Rakuten Hand 5G 官方支持与安全声明](https://network.mobile.rakuten.co.jp/product/smartphone/rakuten-hand-5g/support/index.html)

## 云端机器生成的原始编译证据（Git 永久保存）

| 工件路径 | 对应运行 |
|---|---|
| [`evidence/actions/2026-10-10-clang11`](../evidence/actions/2026-10-10-clang11) | Android Clang 11.0.2 #38053176845 |
| [`evidence/actions/2026-10-10-clang14`](../evidence/actions/2026-10-10-clang14) | Ubuntu Clang14 #38052323798 |
| [`evidence/actions/2026-10-10-config-delta`](../evidence/actions/2026-10-10-config-delta) | 配置差异 #38053251640 |

构建工具链和 Linux 代码来源是“公开源码”，而不是用户原厂镜像。研究数据完全不支持声称已获得未经授权的生产固件或实际成功 root。

## 原件保护原则

- 文件名 + 大小不是 SHA 验证；除本仓库已明确列出的 config/编译摘要，未计算的原件不编造校验值。
- 对于来自日志和 ELF 的地址，必须区分文件偏移、ELF 虚拟地址、泄露的候选地址和内核 `_text`；**不能混为一谈**。
- 本轮已经上传了含潜在隐私风险的原始 Bugreport 与系统日志；目前只在 Private 仓库的 `evidence/restricted/` 分类存档。**不能认为它们已脱敏或适宜公开**；如需对外提供研究记录，须重新生成去身份化副本并审查所有 Git refs。
