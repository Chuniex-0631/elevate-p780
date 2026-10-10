# 后续研究与待归档证据

当前：研究用途；手机仍处于 Bootloader locked 状态；没有执行 Root 成功或解锁成功。

## 已归档

- 详细时间线、硬件/固件、EDL、Fastboot、QAS/PFM/TZ、GhostLock 源码分析。
- Clang11 与 Clang14 的真实 GitHub Actions 构建日志、原始/求解配置、对象文件和配置差异 JSON。
- 历史脚本与已保存的 Markdown 分析报告。

## 已补齐的原件与真正仍缺的材料

- **Tracefs 数据已归档**：[原始 `p780-cpu4.raw`](../evidence/device/p780-cpu4.raw)，4,096 字节；字节级校验和 SHA-256 见 [完整性报告](EVIDENCE_INTEGRITY.md)。
- `hand5g_getprop.txt`、`hand5g_fastboot_all.txt` 等独立历史原件还在个人文件库。**完整 Bugreport 与 OTA 日志现已存于私有 GitHub 的 `evidence/restricted/`，未脱敏**；要公开时必须另做筛查。其它设备文件详见 [来源清单](EVIDENCE_MANIFEST.md)。
- **四代 GhostLock 包已归档**：v0.1–v0.4 ZIP 全部进入 [evidence/ghostlock](../evidence/ghostlock)，通过 CRC 与内嵌证据交叉校验；详见 [版本索引](GHOSTLOCK_PORT_VERSIONS.md)。
- 对应设备 `P780AE_11.0_RMN_JP_162` 的可信 `boot.img`、`vmlinux` 或完整官方 OTA：尚未取得。

## 可持续研究的主要阻断点

1. 官方 `P780AE_11.0_RMN_JP_162` 版本完全匹配的 `boot.img` / `vendor_boot.img` / `vmlinux` 或可信完整 OTA、内核私有补丁仍未取得。
2. 来自真实 P780 的内核对象布局和所有 GhostLock 所需逐构建参数仍未验证；旧版预检 31 项中只有 2 项基础元数据确定。
3. PFM 许可证路径与 OEM Unlock 状态修改之间仍无已知调用链。2026 年 9 月厂商固件认证漏洞具体触发环节仍需独立证据。
4. 新上传的 Bugreport、APK、OTA 与 ADB 全量记录已存 GitHub 私库，**仍需发布前隐私筛查**；另外尚未迁移的历史 APK、设备转储和其它分析 ZIP 按 [原件清单](EVIDENCE_MANIFEST.md) 保持明确状态。

## 研究边界

A52s 源码编译成功不代表 P780 固件二进制一致。TINNO 公共源代码版本是 5.4.61；手机运行内核为 5.4.233。当前没有可信的真实设备符号偏移，也没有可用的设备 Root/解锁成果。

仅在材料可信且与固件完全匹配时继续离线核对。不要把跨机型镜像用于实机刷写。