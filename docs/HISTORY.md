# 研究时间线

> 2026-10-26 重建为 UTF-8。只记录能从已保存报告、文件元数据、终端片段或 GitHub Actions 回溯的事项；仅有摘要而无原始日志的，会标"历史记录"。

| 日期 | 阶段与资料 | 实际结果 |
|---|---|---|
| 2026-06-12 | 最早的公开资料 | P780 的 EDL/Sahara/Fastboot 资料：`fastboot locked`、unlock 返回 `unknown command`。 |
| 2026-10-03/04 | 设备取证与去预装 | 设备基线、去预装实验；用户 0 包状态会变化，不同日期不混用。 |
| 2026-10-10 | config / 候选构建 / GhostLock | 实机 config 5238 项；Clang11/14 候选构建；GhostLock 源码与配置核对。 |
| 2026-10-18 | AVB / DSU / OEM / 策略 | AVB 测试根密钥身份核验；DSU A/B 离线验签、B 安装回原厂；OEM Unlock Journey gate；policy/static 专题。 |
| 2026-10-19 | EDL Sahara v2 / OEM gate / native | QDL v2.8 读到 Sahara v2/HWID/PKHash；OEMLOCK 调用边界；native 接口交叉核对。 |
| 2026-10-24 | IPsec / DirtyFrag v0.2 / v0.3 / supplement | UDP/ESP 回环 PASS；file-backed sendfile 回环 PASS；VINTF/OTA 证书补充；TINNO 5.4.61 源码审计。 |
| 2026-10-25 | DirtyFrag 实机 / init / installd / perf / repo rebuild | ESP 页缓存写入确认；`libc++`/`libbase` 改写；init/installd 域代码执行；perf 无镜像采样；仓库重建。 |
| 2026-10-26 | ABL 菜单 / GhostLock 5.4 / EDL / CVE-2024-23373 / 26923 | ABL 菜单无 Unlock、FFBM/QMMI fallback；GhostLock 七条车辆判负；EDL 无 TINNO 签名 loader；CVE-2024-23373 受影响但触发未解决；CVE-2024-26923 未触发。 |

## 说明

- 日期按报告日期，不杜撰精确小时；实机采集以每次 `ro.boot`/uptime/槽位快照为准。
- 旧页面中不可逆的编码损坏段落不再引用；以 `docs/STATUS.md` 和未损坏专题为准。
- 详细证据路径与 SHA-256 见 `docs/EVIDENCE_MANIFEST.md`。
