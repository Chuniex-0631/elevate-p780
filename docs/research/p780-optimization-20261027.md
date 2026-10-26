# P780 官方系统优化方案（2026-10-27）

> 前提：设备为 B 槽 stock、Enforcing；我们只有 **Elevate 的 uid0 shell（installd 域）**
> 作为额外权限，没有完整 root，不能改 `/system`，但可以：
> `pm disable-user` / `pm uninstall --user 0` / `pm clear` / `cmd appops` /
> `settings put` / `cmd deviceidle` / `am set-standby-bucket`。
>
> 原则：只做 **可逆** 的用户级禁用/隐藏；不动 system 分区；不碰 telephony/IMS/
> eSIM/紧急广播；每一步可回滚。

## 1. 基线

- RAM：3.5 GB，当前 `MemAvailable` 约 1.5 GB；
- 系统包：271 个；第三方仅 Elevate；
- 默认 Home：`com.android.launcher3`（Rakuten launcher 不是默认）；
- 默认输入法：Gboard；
- 当前 RSS 大户：
  - `com.google.android.gms` 325 MB
  - Gboard 245 MB
  - Gmail 215 MB
  - YouTube 214 MB
  - `jp.co.rakuten.mobile.rcs` 210 MB
  - Google Docs/Maps/Play Store/Photos/YouTube Music/Android Auto/Felica 各 130–165 MB
- 明显可省：Google 媒体套件、Rakuten 推广/客服、Felica（若不用）、Android Auto、
  Wellbeing、Duo/Meet、Files、Play Movies、部分 Qualcomm 诊断/XR。

## 2. 三档方案

### L1 保守（几乎无功能损失，推荐先做）

只禁用“内容消费/推广/诊断”，保留 Google 账号、Play 商店、地图、Gmail、
Chrome、Gboard、相机、电话、IMS、紧急广播、Felica。

- Google：
  - `com.google.android.apps.docs`
  - `com.google.android.apps.docs.editors.docs`
  - `com.google.android.apps.docs.editors.sheets`
  - `com.google.android.apps.docs.editors.slides`
  - `com.google.android.videos`
  - `com.google.android.apps.youtube.music`
  - `com.google.android.apps.wellbeing`
  - `com.google.android.projection.gearhead`（Android Auto）
  - `com.google.android.apps.tachyon`（Meet/Duo）
  - `com.google.android.apps.restore`
  - `com.google.android.onetimeinitializer`
  - `com.google.android.partnersetup`
  - `com.google.android.feedback`
  - `com.google.mainline.telemetry`
- Rakuten / TINNO：
  - `com.rakuten.feed`
  - `jp.co.rakuten.mobile.ecare`
  - `com.tinno.hightlights`
  - `com.rakuten.launcher3`（不是默认 Home）
  - `com.ape.factory`
  - `com.ape.setupwizard`（已完成开机设置后）
- AOSP 可选：
  - `com.android.bips`
  - `com.android.printspooler`（不打印时）
  - `com.android.bookmarkprovider`
  - `com.android.providers.partnerbookmarks`
  - `com.android.dreams.basic`
  - `com.android.wallpaper.livepicker`
  - `com.android.wallpaperpicker`
  - `com.android.wallpapercropper`
  - `com.android.wallpaperbackup`
  - `com.android.egg`
  - `com.android.traceur`
  - `com.android.managedprovisioning`（没有工作资料时）
  - `com.android.companiondevicemanager`（没有手表/伴侣设备时）

预期：少 10–15 个常驻进程，释放 300–600 MB RSS；不影响电话/短信/相机/支付。

### L2 均衡（推荐，按是否使用逐项确认）

在 L1 基础上，再禁用“你确实不用”的大户：

- `com.google.android.youtube`（不用 YouTube）
- `com.google.android.apps.photos`（不用 Google 相册）
- `com.google.android.apps.maps`（不用 Google 地图）
- `com.google.android.gm`（不用 Gmail）
- `com.google.android.apps.nbu.files`（不用 Files）
- `com.google.android.apps.googleassistant`
- `com.google.android.googlequicksearchbox`（不用 Google 搜索/发现）
- `com.google.android.apps.messaging`（用其他短信 App 时）
- `com.android.chrome`（已用其他浏览器；WebView 是另一个包，不受影响）
- `jp.co.rakuten.mobile.rcs`（不用 Rakuten RCS/Link 时；可能影响运营商 RCS，
  不影响普通短信/电话）
- `com.google.android.apps.youtube.music` 已含 L1
- `com.ape.soundrecorder`（不用录音机）
- `com.google.android.marvin.talkback`（不需要无障碍时；否则保留）
- `com.google.android.tts`（不需要 TTS 时；否则保留）

预期：再释放 400–900 MB RSS；日常内存明显宽松。

### L3 激进（不建议普通使用）

- `com.felicanetworks.mfc` / `mfm.main` / `mfs` / `mfw.a.boot`（不用 Osaifu-Keitai）
- `com.android.vending`（不用 Play 商店；会失去应用更新）
- `com.google.android.inputmethod.latin`（必须先装好替代输入法）
- `com.android.cts.ctsshim` / `com.android.cts.priv.ctsshim`（测试 shim）
- 部分 Qualcomm 诊断/XR：
  - `com.qti.diagservices`
  - `com.qualcomm.qti.qdma`
  - `com.qualcomm.qti.xrvd.service`
  - `com.qualcomm.wfd.service`（不用 Miracast）
  - `com.qualcomm.qti.performancemode`
  - `com.qualcomm.qti.devicestatisticsservice`

不要动：
`com.google.android.gms`、`gsf`、`webview`、`networkstack`、
`permissioncontroller`、`systemui`、`settings`、`phone`、`telecom`、
`org.codeaurora.ims`、`com.qualcomm.qti.ims`、`com.google.android.ims`、
`vendor.qti.iwlan`、`cellbroadcast*`、`emergency`、`launcher3`（无替代桌面时）。

## 3. 执行方式

### 3.1 先快照

```sh
pm list packages -e > /data/local/tmp/pkgs_enabled.txt
pm list packages -d > /data/local/tmp/pkgs_disabled.txt
```

### 3.2 禁用（可逆）

```sh
pm disable-user --user 0 <pkg>
# 或更强：隐藏并清数据/更新
pm uninstall --user 0 <pkg>
```

`uninstall --user 0` 不会删系统镜像，可用
`cmd package install-existing <pkg>` 恢复。

### 3.3 清数据/缓存

```sh
pm clear <pkg>
pm trim-caches 4G
```

### 3.4 后台限制（保留应用但降耗）

```sh
cmd appops set <pkg> RUN_IN_BACKGROUND ignore
cmd appops set <pkg> RUN_ANY_IN_BACKGROUND ignore
am set-standby-bucket <pkg> restricted
cmd deviceidle whitelist -<pkg>
```

### 3.5 系统设置

```sh
settings put global window_animation_scale 0.5
settings put global transition_animation_scale 0.5
settings put global animator_duration_scale 0.5
settings put secure limit_ad_tracking 1
# 可选：Private DNS（先确认网络可用）
settings put global private_dns_mode hostname
settings put global private_dns_specifier dns.adguard.com
```

### 3.6 回滚

```sh
pm enable <pkg>
cmd package install-existing <pkg>
settings put global window_animation_scale 1
...
```

## 4. 验证清单

每次批量后重启，检查：

- 电话/短信/移动数据/VoLTE；
- 紧急警报（不要禁用 cellbroadcast）；
- 相机/指纹/人脸；
- 蓝牙/热点/Wi-Fi；
- Felica（若保留）；
- Play 商店/GMS 通知（若保留）；
- 默认桌面/输入法是否正常。

## 5. 预期与边界

- L1：少 300–600 MB RSS，无功能损失；
- L2：再少 400–900 MB，取决于禁用项；
- 最大内存占用仍是 **GMS**，不能安全禁用；优化主要是减少同时驻留的媒体/推广 App；
- 这些操作不会改变内核、SELinux、boot/vbmeta，也不会带来完整 root；
- 任何“改 /system、删系统 App、改 build.prop”的方案都不在 uid0 shell 能力内，
  需要可写 system 或 EDL。

## 6. 建议

先执行 **L1**，重启观察一天；确认无影响后按“是否使用”逐项执行 **L2**。
Felica、RCS、Play 商店、Gboard 这类有实际依赖的，默认不放入 L1。
