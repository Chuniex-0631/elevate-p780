# 后续研究与待归档证据

当前：研究用途；手机仍处于 Bootloader locked 状态；没有执行 Root 成功或解锁成功。

## 已归档

- 详细时间线、硬件/固件、EDL、Fastboot、QAS/PFM/TZ、GhostLock 源码分析。
- Clang11 与 Clang14 的真实 GitHub Actions 构建日志、原始/求解配置、对象文件和配置差异 JSON。
- 历史脚本与已保存的 Markdown 分析报告。

## 尚缺的原始材料

- `p780-cpu4.raw`：4,096 字节 Tracefs 实机原始数据，当前仅保存在用户原始文件库。建议上传到私有仓库 `evidence/device/p780-cpu4.raw`。
- `hand5g_getprop.txt`、`hand5g_fastboot_all.txt`、`hand5g_bugreport.zip`、OTA 日志：源文件仍在个人文件库，可能带设备/账户敏感数据；仓库目前只保存脱敏摘要和索引。
- `P780-GhostLock-port-v0.1...v0.4.zip` 历史研究工作包：原件已定位，但完整 ZIP 尚未迁入 Git。
- 对应设备 `P780AE_11.0_RMN_JP_162` 的可信 `boot.img`、`vmlinux` 或完整官方 OTA：尚未取得。

## 研究边界

A52s 源码编译成功不代表 P780 固件二进制一致。TINNO 公共源代码版本是 5.4.61；手机运行内核为 5.4.233。当前没有可信的真实设备符号偏移，也没有可用的设备 Root/解锁成果。

仅在材料可信且与固件完全匹配时继续离线核对。不要把跨机型镜像用于实机刷写。