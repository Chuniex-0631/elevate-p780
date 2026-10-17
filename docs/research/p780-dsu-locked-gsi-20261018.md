# P780 Android 11 DSU / GSI 可信启动支线 — 源码交叉核对（2026-10-18）

> **现阶段只是一条新的有根据的研究假说，P780 尚未执行 DSU/GSI 操作、未安装任何镜像。** 重点不是刷写原有分区，而是核对是否存在官方提供的、在 LOCKED 状态下临时启动受信任 GSI 的 DSU 通道。不能把它误称为 Root/BL 解锁/AVB 漏洞的现成 PoC。

## 发现源头：实际 Fstab 中的 GSI 公钥

2026-10-18 机主读取并作为会话内容提交 `/vendor/etc/fstab.default`、`/vendor/etc/fstab.emmc`，两者 `system` 行均含：

```text
avb=vbmeta_system,logical,first_stage_mount,avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey
```

而 AOSP Android 11 [system/core/fs_mgr/fs_mgr_fstab.cpp](https://android.googlesource.com/platform/system/core/+/ebce675b177f22a3248b1104b21c9c79937b8fda/fs_mgr/fs_mgr_fstab.cpp) 的 `BuildGsiSystemFstabEntry()`，明确包含相同的 q/r/s GSI 公钥路径。AOSP [Dynamic System Updates](https://source.android.com/docs/core/ota/dynamic-system-updates) 说明开发者 GSI 可通过预置开发公钥在 **LOCKED** 状态下验证并临时启动。**这证明所见配置符合标准 DSU/GSI 设计，不足以证明 P780 已实际启用该功能或这三份文件当前可读取/生效。**

## 与 P780 已证实实机信息的条件交叉检查

| AOSP DSU 需要 | 当前 P780 证据 | 判定 |
|---|---|---|
| Android 11+ DSU Loader 用户界面 | Android 11 | 版本相容；**未证实 OEM 未隐藏/禁用前端** |
| Android 动态分区 | `ro.boot.dynamic_partitions=true` | 满足 |
| F2FS 或 ext4 `/data` | 两份 fstab 都声明 `f2fs` | 配置符合 |
| 首阶段 `/metadata` | fstab `/metadata` ext4 `first_stage_mount` | 配置符合；需硬件/运行态佐证 |
| dm-verity、部分 DSU kernel configs | 已观察到五份 dm-verity 设备；kernel 5.4.233 | DM_VERITY 运行迹象强；`CONFIG_DM_VERITY_FEC` 与完整 DSU 依赖尚未直接复核 |
| 能够验开发 GSI 签名的对应公钥 | `avb_keys=/avb/q-gsi...` 等 fstab 声明 | **仅配置候选**；未核对 `/avb/*` 的启动时文件、内容和 DSU 验证结果 |
| System/GSI 与 Vendor HAL 兼容 | P780 Android 11 / arm64 / vendor HAL、Gatekeeper/Weaver 未审计 | 未验证 |
| 空间需求 | AOSP 提示大约 10GB 临时空间 | 未确认可用空间（当前阶段不安装） |

**隔离两种钥匙：**
- Key Attestation 已独立证实 `verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6` 匹配 `testkey_rsa4096_pub.pem` 的根 AVB 公钥二进制 SHA-256。
- `/avb/q-gsi.avbpubkey` / `r-gsi` / `s-gsi` 是另一组由系统启动 ramdisk 配置引用的**开发 GSI 签名公钥候选**，不能当作根 AVB 签名密钥、不能以其中之一的存在直接得出任意 root GSI 会被接受。

## 第一阶段允许的只读验证（Windows PowerShell）

以下只读 Android 属性、列举包/系统可见文件，**不执行** `adb reboot`、`setprop`、`gsi_tool enable/install/wipe`、DSU Loader 下载、EDL、Fastboot 或 `dd`：

```powershell
adb shell pm path com.android.dynsystem
adb shell ls -l /system/bin/gsi_tool /system/bin/gsid
adb shell getprop init.svc.gsid
adb shell getprop persist.sys.fflag.override.settings_dynamic_system
adb shell getprop ro.gsid.image_running
adb shell ls -l /avb/q-gsi.avbpubkey /avb/r-gsi.avbpubkey /avb/s-gsi.avbpubkey
```

需要手动在开发者选项中**只观察** `DSU Loader` 是否存在，不点击镜像或开始安装。应用包存在与服务二进制存在，都不等于功能运行成功。`/avb/*` 路径在启动 ramdisk 内存在但启动后不可见、或 shell 权限不足，都不能单独否定功能。`init.svc.gsid` 为空/`stopped` 也不能证明系统不支持按需启动的服务。

注意：官方 Android 11 [gsi_tool.cpp](https://android.googlesource.com/platform/system/gsid/+/refs/tags/android-cts-11.0_r16/gsi_tool.cpp) 虽允许 `gsi_tool status` 作为普通用户查询，但工具会在必要时通过 `ctl.start=gsid` **启动服务**，所以本轮严格只读阶段不将它列为默认操作。禁止执行 `gsi_tool install|enable|disable|wipe`。

## 研究价值与停损

- 如果正常 DSU 组件、前端、GSI 公钥和相容的供应商支持均存在，则考虑单独评估**官方签名的临时 GSI** 能否运行；这是一条不会直接覆盖原厂 boot/system 分区的标准 OS 测试路径，不等于漏洞利用或 Root。
- 如果仅 Fstab 写了 AVB GSI keys，系统却缺少 DSU 组件或强制禁用，则优先判为模板配置/不可用功能，不继续通过 `setprop` 强行开启，也不冒险向 Android 11 的锁定态设备写镜像。
- 不混用本次 DSU 与先前 Google OTA Prober；后者为旧版本 OTA 查询、机主已决定暂缓。
- P780 的真正两个未解决主阻断仍是**匹配 `_162` 的分区原始镜像/签名描述符**与**经证实的 locked 状态分区写入/可信修复能力**。DSU 如果可用也只能作为独立、受限制的实验接口，不能代替后者。

## 2025 SPICES 论文交叉限制

[AVBTestKeyInTheWild 论文摘要](https://research.jku.at/en/publications/workshop-avbtestkeyinthewild-bypassing-android-verified-boot-usin/) 的关键是区分 AVB 加密验签与设备允许的刷写/修复通路。2026-10-14 [JVN#47427200](https://jvn.jp/en/jp/JVN47427200/) 确认 P780 全版本弱密钥和物理接触威胁，但没有发布该机的具体成功写入/恢复过程。若 DSU 受官方内置公钥限制，它不是“借助主 AVB 弱密钥自然获得写入权限”的证明。
