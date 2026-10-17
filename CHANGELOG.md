# 归档维护日志

## 2026-10-18 — 用户决定推进 DSU 首次实机试验，采用分阶段安全方案

- 机主认为 DSU 不覆盖原系统因此愿意实际尝试。已核对 Google [官方 DSU](https://developer.android.com/topic/dsu) 与 [Android15 GSI 已知风险](https://developer.android.com/topic/generic-system-image/releases)：标准 DSU 避免写入原厂 system/boot，但仍修改 userdata，失败有 Recovery factory reset/数据丢失风险，不构成绝对无损保证。
- 基于实机 ARM64/VNDK30/Treble/空间已满足基础条件，选择 Google Android15 QPR2 `GSI ARM64` 无 GMS `BP1A.250405.005.C1` 作为第一个受控试验候选（仍未证明 AVB/GSI签名信任或 HAL 运行）。不选 GMS/Android16；无 fastboot/EDL 强刷。
- 新建 [DSU 首次实机分段试验协议](docs/research/p780-dsu-first-trial-protocol-20261018.md)：事先确认可丢失数据/备份与 USB ADB；阶段 A 由 Settings 下载/安装并在通知 Restart/Discard 处暂停；阶段 B 单独确认后才实际重启进 GSI。
- 当前只是准备文档和用户授权，尚无下载安装或重启实绩，设备仍 LOCKED/未Root。更新 STATUS、NEXT_STEPS 与证据清单；等待机主后续阶段 A 实机反馈再更新结果。

## 2026-10-18 — 第九轮 DSU 签名信任链：六份公开 GSI AVB 公钥哈希与 AOSP 早期启动核验

- 交叉审核 Android11 `target/product/gsi_keys.mk`、`developer_gsi_keys.mk` 与 `rootdir/avb/Android.mk`，明确两组标准 q/r/s-GSI 与 Developer q/r/s-GSI 公钥分别存在；P780 fstab 只声明**标准** q/r/s-GSI 文件，不可把它们笼统称作 Developer GSI key。
- 借助 GitHub 公共 Android11 源码镜像获得 q/r/s 普通与 Developer 共六份 RSA4096 AVB 公钥二进制（1032B/份），JS SHA256 用 abc 向量自测后逐份算哈希；六个摘要均不同于 P780 TEE KeyAttestation AVB Test 根密钥摘要。全部 SHA、Git blob 哈希、AOSP 源码证据见 [新增第九轮报告](docs/research/p780-dsu-trust-chain-audit-20261018.md)。**没有直接访问 P780 boot ramdisk 字节；公开公钥值是候选证据，不是机上加载实测。**
- AOSP 将 Settings DSU JSON 筛选、安装期可选公钥预检查/撤销检查和 first-stage AVB 最终受信公钥验证分开；缺少 JSON pubkey 不构成签名绕过。仍缺 Android15/16实际系统镜像 AVB Footer 签名钥匙和 P780 实际运行时受信钥匙。
- 从 Google 官方 Android15/16 GSI 发布页面核对未来ZIP SHA，并发现部分设备启动/重启 GSI 失败时可能需 Recovery 清空 userdata。此风险不允许仅凭 DSU 是“临时系统”便承诺无损回退；暂不下载、安装或重启 GSI，不影响 locked/未 Root 现状。
- 同步 STATUS、NEXT_STEPS、DSU 主专题、导航和证据索引；后续不重复已完成的 Treble、KeyAttestation/JSON 抓取。

## 2026-10-18 — DSU 六子目录镜像元数据已核验：24条全无 VNDK/pubkey；CP11 纠错

- 机主上传 `p780-dsu-catalog-detail.zip`，4073B / SHA-256 `ad732d61aa7751aeaa6f2a148e3a1998aeee645beb5fe3f344fff98d9ca74c74`。离线验证ZIP全部8项、六子目录原始字节SHA与report完整匹配，无读取错误；24条 GSI JSON 记录已经独立解析。
- 4个 P780 菜单项目确系 Google `vic` Android15（BP1A两项）与 `baklava` Android16（CP11两项），截图上字形与 JSON 对照后确认 **CP11（两数字1）**，而非旧脚本目标 `CPI1`；故自动 report.matches 只列4条 BP1A（含x86），漏掉Android16并非下载失败。保留此错误以供审计，不再要求重复抓取。
- **核心结论：全部24条 JSON均缺 `vndk` 和 `pubkey`**，客户端会跳过缺失字段对应的预筛；四项菜单出现不能表示 VNDK30明确支持或 GSI签名已被设备信任。R/S/T/U旧镜像的安全补丁早于P780 2024-02，导致SPL过滤仅留下Android15/16的ARM64×2。
- 新建 [独立分析](docs/research/p780-dsu-gsi-catalog-verified-20261018.md)，更新DSU主专题、计划、状态、证据清单、README。下一步仅公开源码和离线对照 GSI签名公钥及P780 q/r/s-GSI信任链；未下载安装GSI ZIP，未刷分区/重启/Root/解锁。

## 2026-10-18 — DSU Google 主索引已核验，六子目录待查

- 机主在 Windows 成功取得 `gsi-src.json` 原始文件（508 bytes），SHA-256 `0A1970ABFCEB6BF3962177881B255E6AF9D4F43903AAC3BA9AEF2C1E5B4A2D09`，本聊天附件也已离线二次哈希完全匹配。不是 P780 本机流量抓包。
- 根目录包含 Google `rvc/sc/tm/udc/vic/baklava` 六个子目录 `gsi-dsc.json`，自身没有 `images`，故此前关于 BP1A/CPI1 的 VNDK30/公钥身份仍不可升级为实测结论。AOSP DSU JSON 支持递归 include、可选 vndk/pubkey；元数据必须以实际子目录的原始响应为准。
- 当前研究环境无法直接抓取 Google 子目录。已在本聊天生成离线模拟测试通过的 Python metadata-only 辅助脚本，可由机主在 Windows 以固定 Google allowlist 小范围下载子 JSON、校验 SHA 并上传 ZIP，不会下载 GSI 镜像、执行 ADB 或改写 P780。
- 同步 [DSU 专题](docs/research/p780-dsu-locked-gsi-20261018.md)、[研究计划](docs/NEXT_STEPS.md)、证据总表；不重复已有基础 Treble/KeyAttestation 实机任务。Root/Bootloader/固件镜像写入状态均无变化。

## 2026-10-18 — 第六轮 DSU Treble/VNDK 隔离：本机三项官方前置检查完成

- 机主 Treble Check 截图显示 Treble、A/B、ARM64、System-as-root 支持；同时普通 ADB `ro.treble.enabled=true`，运行时 `/linkerconfig/ld.config.txt` 存在(90,115B)，`[vendor] namespace.default.isolated=true` 明确位于第370行，且包含真实 Vendor/ODM linker search paths。旧 `/system/etc/ld.config*` 不存在只是路径差异。
- 联合此前实机 VNDK=30、CPU=`arm64-v8a` 和空闲空间报告，Google 官方 GSI 兼容性指南的 Treble、Vendor 隔离、ABI 基础要求已确认，提升研究信心；**但 DSU 安装 GSI 的可信公钥、镜像内 VNDK 30、HAL、系统启动状态仍未确认**。
- AOSP 自 Android15 起废弃新的 VNDK，同时保留≤14旧 VNDK APEX 供旧 Vendor 使用：不能仅凭跨 Android 版本宣称不兼容，也不能假设任何 GSI 都能启动。下一轮转向截图中四项 GSI 的 Google DSU 原始 JSON 元数据，优先 PC 只读获取、离线核对 vndk/pubkey 等，不刷机、不下载大镜像。
- [DSU 专题](docs/research/p780-dsu-locked-gsi-20261018.md)、[NEXT_STEPS](docs/NEXT_STEPS.md)、STATUS、证据清单同步修订；手机仍 Bootloader LOCKED、未 Root。

## 2026-10-18 — DSU 第五轮基础预检：VNDK30、ARM64、数据空间报告 103G

- 机主四项只读结果：DSU `.list` 覆盖属性空、`ro.vndk.version=30`、`ro.product.cpu.abi=arm64-v8a`、`df -h /data` 报 dm-11 共106G/已用3.2G/可用103G/4%，Mounted on 指向 `/storage/emulated/0/Android/obb`（不武断认为该挂载点就是 `/data` 本身的真实块设备节点）。
- AOSP `DSULoader.java` 对 cpu_abi 必需值筛选；`os_version`/`vndk`/`spl` 只有 JSON 列出时才筛选，因此 DSU Loader 显示四项**不能**自动证明其中每一项都包含 VNDK30、签名验收或 HAL 兼容。官方 GSI 文档另要求先确认 `ro.treble.enabled` 与 vendor linker namespace isolation 以支持跨 Android 版本。
- DSU 安装器恢复成功已在前轮登记；本轮不再重复其命令。更新第五轮脱敏实测、状态和 NEXT_STEPS，把下轮工作限制为只读 Treble/ld.config 查询；没有选择 GSI、下载安装/启动、尝试 locked 写入或得到 Root。

## 2026-10-18 — P780 DSU 官方安装服务恢复成功；推进到只读兼容性预检

- 机主正式执行 `cmd package install-existing --user 0 com.android.dynsystem`，设备返回 `Package com.android.dynsystem installed for user: 0`；`pm path` 已恢复显示原厂 `DynamicSystemInstallationService.apk`；`dumpsys` 证明 `installed=true`（由恢复前 `false` 变为 `true`）。`enabled=0` 始终为 PackageManager DEFAULT。
- 本次通过用户级安装登记恢复预装组件，无需 Root、恢复出厂、APK 下载或刷机。`stopped=false` / `notLaunched=false` 不等于 DSU/GSI 已安装或镜像已启动。
- 已修订 DSU 专项、STATUS 和 NEXT_STEPS 中的旧“installed=false 当前状态 / 未恢复”描述，历史取证阶段保留追溯。下一阶段仅做 `settings_dynamic_system.list`、`ro.vndk.version`、ABI、`df -h /data` 只读检查；不选中截图中较新 Google GSI，也不触发下载/安装/重启。
- 尚无 P780 locked GSI 启动实证，仍未取得 boot/vbmeta 原始镜像、Root 或已证实分区写入通道。

## 2026-10-18 — 解释 DSU Loader 在线四项镜像与无需恢复出厂

- 机主确认从未主动安装 GSI，愿意必要时恢复原厂。根据 AOSP Android 11 DSU Loader 和 Settings `DSULoader.java`，进入开发者选项后 Settings 从 HTTPS DSU JSON 列表抓取元数据并按 ABI/OS/VNDK/SPL 筛选，显示四个远程候选并**不表示**镜像在本机或已下载。
- AOSP 默认目录 URL `https://dl.google.com/developers/android/gsi/gsi-src.json`，但 OEM 可通过 `persist.sys.fflag.override.settings_dynamic_system.list` 改写。之前查询的 `persist.sys.fflag.override.settings_dynamic_system` 不带 `.list`，不能用其空值确定目录来源；保留只读 getprop 核验。
- 标准系统 APK 在 `/system/priv-app/DynamicSystemInstallationService`，但当前 user0 `installed=false`；不需要为了单包恢复而清空整台手机、重装固件或 Root。若后续有必要且机主同意，可 `cmd package install-existing --user 0 com.android.dynsystem` 恢复预装应用，未实际执行；暂不选择或启动新版本 GSI。
- 已同步 [DSU 解释和只读检验](docs/research/p780-dsu-locked-gsi-20261018.md) 与 NEXT_STEPS；本轮没有新的写入通道、Root 或 Bootloader 解锁证据。

## 2026-10-18 — DSU 安装服务 user0 确认卸载；Settings 镜像选择界面仍可使用

- 机主提交 DSU Loader 真机截图：`Select DSU Package` 显示 4 个 ARM64 GSI/GMS 选项（BP1A.250405.005.C1 与 CPI1.251209.009.A1），证明开发者选项可加载线上镜像 JSON 目录；并非 GSI 已安装或可启动。
- ADB 全部判断闭环：当前用户 `0`；常规 pm list packages 找不到 `com.android.dynsystem`；`-u -f` 列表找到系统原 APK `/system/priv-app/DynamicSystemInstallationService/DynamicSystemInstallationService.apk`；`dumpsys` 明确 `installed=false`。**因此此前推测的用户级卸载已获得直接实机确认**。
- 校正重要字段：`enabled=0` 表示 PackageManager 默认组件启用状态，不是 `disabled`；无需优先执行 `pm enable`。历史两个 debloat 脚本均含目标包，机主确认深度清理，但没有具体卸载时间或单条成功日志。
- 对照 Android 官方 DSU Loader JSON→Settings 菜单→安装服务机制，解释“已卸载安装服务、但 Settings 仍显示最新 GSI 选项”的现象。BP1A 选项对应 Google 官方 Android 15 QPR2 GSI；本机 Android 11 vendor 的实际运行兼容未知，列表是筛选结果而非安全承诺。
- 已将 `install-existing --user 0` 作为**仅供机主同意后执行**的系统包恢复选项写入报告及 NEXT_STEPS；没有安装、下载或修改设备。仓库原件 `.p7b` 和 DSU 截图均未上传。

## 2026-10-18 — 实机 DSU Loader 入口确认，回溯发现精简脚本包含安装器

- 机主报告开发者选项真实存在 DSU Loader；`pm list packages -u` 返回 `com.android.dynsystem`，`gsid.rc` 590B 文件真实存在，`/metadata/gsi` 权限拒绝，相关属性无输出。此结果**推翻**先前“可能没有 DSU Loader 入口”的表述，但还未证明可以实际下载安装 GSI。
- 官方 ADB 文档表明 `-u` 列表含卸载包，原先 `pm path com.android.dynsystem` 无输出因此需进一步鉴别 user0 `installed=` 状态。新回查历史两个 P780 ADB 应用精简脚本均列 `com.android.dynsystem` 为卸载目标，旧 phase3 安装清单亦包含；历史执行成功与否**尚无证据**，只能登记为待验证的用户级卸载假说。
- AOSP `gsid.rc` 为 `/metadata/gsi` 设置 root:system `0771`，普通 `shell` Permission denied 是合理权限限制；无需 Root、更不能从拒绝访问判断服务不能使用。
- 已更新 [DSU/GSI 专题](docs/research/p780-dsu-locked-gsi-20261018.md)、STATUS、NEXT_STEPS、EVIDENCE_MANIFEST。下一步限于 user0 软件包状态的只读命令；`install-existing` 需机主明确同意，未执行任何恢复/安装/设备重启。

## 2026-10-18 — DSU/GSI 第一轮实机只读排查和 AOSP 重新归因

- 机主依次查询标准 `com.android.dynsystem` 安装器（未返回路径）、`gsi_tool`（存在且为 47,016B）、`gsid`（Permission denied）、三项相关 getprop（均空）、三份 `/avb` GSI 公钥（普通系统路径不存在）。没有进行任何安装/重启/镜像写入。
- AOSP Android 11 `gsid.rc` 把 GSID 设为 `disabled`/`oneshot`，不可由空运行属性断言组件缺失；Android 11 首阶段 Ramdisk 在正常启动切根后可释放，不能根据 shell 目前找不到 `/avb/*` 否认 fstab 所记启动候选钥匙。
- 现将 DSU 信心调整为：底层工具实机存在，标准 Loader 没有成功解析，完整用户可用性**未知**。只剩一小轮只读核对包和 `gsid.rc` 的价值，若仍无独立安装器或开发者选项入口，则封存 DSU 支线，继续固件/修复通道主阻断。
- 新结果已按 [DSU 研究报告](docs/research/p780-dsu-locked-gsi-20261018.md) 添加实测矩阵，更新 STATUS/NEXT_STEPS/EVIDENCE_MANIFEST。未把 DSU 当作 Bootloader 解锁或 Root 成功。

## 2026-10-18 — DSU/GSI 锁定态官方受信任启动通路的可行性研究

- 在已实机确认 AVB 默认 RSA4096 测试根公钥后，对仍缺原厂镜像、locked 写入渠道的阻断点重新梳理，避免重复普通 AVB/Key Attestation/OTA 采集。
- AOSP 官方 Android 11 DSU 文档指出，厂商可预置 Developer GSI 公钥以允许 Bootloader 保持 LOCKED 时临时启动经过验证的 GSI；`fs_mgr_fstab.cpp` 的 `BuildGsiSystemFstabEntry()` 使用与 P780 两份 fstab 完全一致的 `/avb/q-gsi...:/avb/r-gsi...:/avb/s-gsi...` 路径。
- P780 既有实机 Android 11、动态分区、F2FS `/data`、`/metadata` 首阶段挂载及 dm-verity 与 DSU 基本要求相容，但**尚未确认** DSU 前端/服务、公钥文件运行时可访问、厂商 HAL 或签名 GSI 实际可启动。**没有安装镜像或改变手机状态**，不能推断 Root / BL 解锁 / 物理分区写入。
- 新增 [LOCKED DSU/GSI 专项研究](docs/research/p780-dsu-locked-gsi-20261018.md) 与纯查询命令；AOSP `gsi_tool status` 在部分版本会按需启动 `gsid`，因此首次仅建议读取 app/二进制/属性/路径，不执行安装、启用、关闭或 setprop。
- 将原 `docs/NEXT_STEPS.md` 历史整份归档到 [2026-10-18 快照](docs/archive/next-steps-before-dsu-20261018.md)，重写为精简可执行计划，移除仍称硬件证明“未测试”等过时/重复结论；同步 STATUS、README、文档导航和 Fstab 专题。官方公告中的弱密钥与被允许写入分区仍是独立条件；本机仍 LOCKED、未 Root。

## 2026-10-18 — P780 硬件证明精确确认 AOSP AVB RSA4096 默认测试密钥（关键突破）

- 机主从真实 P780 `_162` 通过 KeyAttestation 导出 3475B `.p7b`；在独立电脑 Python 环境解析 4 张 X.509 证书和 Key Attestation v3 扩展；Google 2019 硬件证明 Root DER 字节完全相同，Root 自签及 Root→CA1→CA2→Leaf 各级签名验证通过，TEE 与 Keymaster 安全级别均 TrustedEnvironment。在线吊销状态尚未做生产级完整校验。
- 取得 `deviceLocked=true`、`verifiedBootState=Verified`、`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2`，与此前 ADB VBMeta Digest **逐字节一致**。
- **最重要发现**：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`，完全等于 AOSP RSA4096 `testkey_rsa4096_pub.pem` 使用官方 `avbtool.py` RSAKey 编码生成的 **1032 字节 AVB 公钥 blob 的 SHA-256**。SPKI DER、PKCS1 DER 和模数格式哈希均不相同；已确定正确编码和本机根公钥身份。
- 新建 [脱敏验证报告](docs/research/avb-attestation-confirmed-20261018.md)，同步 README、STATUS、NEXT_STEPS、证据清单与早期假说专题。没有将设备证书原件上传 Git；**没有 Root、解锁或已证实 P780 locked 写入渠道**。后续仍需原厂 VBMeta/chain descriptors/rollback index 和有真实证据的写入手段。

## 2026-10-18 — 暂停 OTA，聚焦硬件 Key Attestation（实机待测）

- 机主将 Google OTA 探测支线暂缓，研究转向不依赖原厂固件与 OEM 回复的 Android Keystore `RootOfTrust`。
- 核查 Android 官方 Keystore/Key Attestation、Google ASN.1 `RootOfTrust`、Trusty Keymaster 实现及开源 KeyAttestation app v1.8.4 的默认行为：APP 启动自动做普通 KeyStore 证明，返回的 `verifiedBootKey` 为十六进制，`verifiedBootHash` 可缺失。
- 新增关键编码限制：Bootloader 若直接提供 ≤32 字节公钥摘要，Keymaster 可原样转发；提供原始 key >32 字节才由 Keymaster SHA-256，因此不能预设 attested hash 与任何单一格式的 AOSP AVB 公钥 blob 哈希直接相等。
- 已将最小必要采集字段、证书信任根/软件级风险、过时吊销列表与隐私边界加入研究专题和 NEXT_STEPS；尚无 P780 硬件证明实测，Root/BL 状态不变。

## 2026-10-18 — 纠正外部 AI 的 P780 OTA 与 AVB 签名混淆

- 根据上游真实 CLI，纠正不存在的 `--device`、source/target fingerprint 参数和 `devices.json` 文件；否定毫无来源的 `264→151/120` 字符串改写作为旧构建证据。
- AOSP 官方 `signapk` 是 APK/OTA ZIP 签名而非 AVB 签名，AVB 使用 `avbtool`/libavb；Magisk + signapk 不能自动实现 locked P780 强刷。
- AOSP payload Full/Delta 区分决定镜像能否离线完整恢复；所谓 Google 下载直链固定数小时到期或长期保留旧包，缺乏 P780 证据。
- 新增楽天社区 2024-07-31 真实 `_161` 收到 `_162` OTA 提示但安装失败的历史材料；仍缺旧版完整 fingerprint、OTA URL 和分发服务器身份。
- 同步 [Google OTA Prober 核对专题](docs/research/google-ota-prober-p780-20261018.md) 与 NEXT_STEPS；设备无改动，Root/BL 无新成功证据。

## 2026-10-18 — P780 Google OTA 单次无 URL / 实机 Fstab 信任分组确定

- 机主在 Windows 执行 `python probe.py --fingerprint "Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys" --model P780`，程序返回 `No OTA URL found for your build`；无 HTTP 状态、无 Google OTA URL。最新 `_162` 构建下的单次负面查询不能证实 P780 不使用 Google OTA；不再对相同 fingerprint 重复查询。
- 机主通过 ADB **实际读取并作为聊天附件提交** `fstab.default` 和 `fstab.emmc` 全文。两个文件中 `system/system_ext/product` 均声明 `avb=vbmeta_system`，而 `vendor/odm` 声明普通 `avb`；与既有两级 vbmeta 分区及 dm-verity 线索相容，但仍不是 Bootloader chain descriptor 原件。
- 额外发现 `/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey` 只在 `system` 的 `avb_keys` 选项中出现。AOSP fs_mgr 优先验证独立 GSI 公钥、失败后回退默认 AVB 的代码路径已核对；**不能将 GSI 公钥当作生产根签名密钥或现成解锁路径**。
- 新增 [Fstab AVB 专题](docs/research/p780-fstab-avb-20261018.md)，修订原先“尚未读取 Fstab / 尚未查询 P780”的过时状态，更新 Google OTA 专题、AVB 取证计划、STATUS、证据索引、README 与文档导航。保留来源等级：会话原始输出非 Git 中原始文件二进制；设备仍 locked、未 Root、无原厂镜像。


## 2026-10-18 — P780 Google OTA Prober 源码审阅与同 OEM 更新链旁证

- 机主提供 `Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys` 完整 fingerprint；ADB 列出 `/vendor/etc/fstab.default`、`fstab.emmc`，`fstab.qcom` 不存在。改为只读前两份实际文件，暂停假设厂商 fstab 名称。
- 审阅 [tangalbert919/google-ota-prober](https://github.com/tangalbert919/google-ota-prober) `README/probe.py/config.yml/utils`：通过 Google `android.googleapis.com/checkin` 的 `fetchSystemUpdates=1` 获 OTA URL，只有采用 Google OTA 服务器的机型才适用；不具有通用厂商 OTA 穷举能力，且不能通过当前最终版 `_162` 的查询无结果排除历史 Google OTA。
- 发现 [mouseos OTA Archive](https://github.com/mouseos/ota-archive) 的 Rakuten/Tinno C330 (Rakuten Mini) 官方 Google OTA 历史 530→620、620→830；TINNO P710 存在 fingerprint 但无 OTA。未发现 P780 条目，且**尚未实机或网络模拟发送 P780 Check-in 请求**。不能将 C330/P710 视为 P780 镜像。
- 新增 [Google OTA Prober × P780 专题](docs/research/google-ota-prober-p780-20261018.md)，更新 README、STATUS、NEXT_STEPS、固件专题、证据清单与导航。只有在取得可信 P780 OTA URL 时才进一步离线核对 `pre-build`/`post-build`、增量与原厂镜像关系；未安装固件、未解锁、未 Root。


## 2026-10-18 — 跨 AVB / TEE / Keystore / CTS 发现新取证入口

- 按机主要求对现有 `green/locked`、`ro.boot.vbmeta.digest`、块设备 `0600 root`、TEE/Keymaster 以及双层 VBMeta 信息进行交叉分析。
- AOSP Key Attestation `RootOfTrust.verifiedBootKey` 可包含启动信任公钥哈希；`verifiedBootHash` 可包含 VBMeta Digest。Android CTS 源码对照 `verifiedBootHash` 与 `ro.boot.vbmeta.digest`。提出不需原厂镜像、Root 的普通 Keystore 证明研究路径；**P780 尚未运行，不宣称能成功**。
- 核对公开开源 KeyAttestation 应用（vvb2060，官方 latest v1.8.4、minSdk 24、源码 Manifest 无 INTERNET 请求），仅列为机主可选正常安装试验，不自动安装、不要求 Shizuku 和设备标识数据；硬件证明必须验证签发根、TEE 级别和吊销信息，隐私证书链不得直接公开。
- AOSP fstab 可用 `avb=vbmeta_system` 确认逻辑分区的第一阶段挂载目标，给出可选只读核查；AOSP 默认 RSA4096 测试钥匙成为有出处的候选，仍不可直接认定 P780 使用该密钥。
- 新增 [AVB 无镜像替代路径专题](docs/research/avb-attestation-alternative-20261018.md)，同步 README、STATUS、NEXT_STEPS；未运行利用、读取 root-only 原始块设备或改动手机，Root/BL 状态不变。

## 2026-10-18 — AVB 研究资源分配调整

- 机主判断重复邮件咨询难以推进，已有 TINNO 源码邮件暂无可用成果；**停止将 JVN/厂商/研究者主动咨询视为主要工作**（JV N 公告编号不变，联系信息仅作历史记录）。保留原邮件被动等待和可核验回复处理，不发催办邮件。
- 对公开的 CVE-2026-107153 技术资料、P780 VBMeta、公钥证据及固件进行再检索，仍未取得 P780 专用 PoC、镜像或可复核密钥指纹。不推断不存在私人研究结果。
- 主动工作集中在不依赖邮件回复的公开原件和离线比对；缺少本机 vbmeta / locked 写入通道的根本阻断不变；不对设备开展高风险测试。


## 2026-10-18 — 固件稀缺下的 AVB 分阶段研究策略

- 没有可靠取得匹配 `_162` 的完整 OTA；决定不再把完整固件作为**探索性测试密钥识别**的唯一前提，优先寻找附来源、版本和哈希的任意 P780 版本 `vbmeta*.img`、可信 AVB 公钥指纹与最小可核验的签名链结果。
- 强调 **机型级探索 ≠ 本机 `_162` 精确匹配**，其它版本或其它 Rakuten/同 SoC 设备不能直接代替本机镜像；Root/Bootloader/EDL 路线状态不变。
- JVN 已公开署名漏洞报告者松原正佳，[JVN 官方联系页](https://jvn.jp/contact/) 提供 `jvn@jvn.jp`；只是可考虑的公开信息咨询入口，**未发出邮件**、也不预设报告者持有可分享 PoC 或固件。
- 同步 AVB 专题与 NEXT_STEPS，避免继续对机主进行无效的重复 getprop/固件关键词采集。

## 2026-10-18 — P780 实机 AVB Green/Locked 基线与只读研究路径

- 用户提供的 ADB 输出：`green`、`locked`、`flash.locked=1`、活动槽 `_b` 与 VBMeta digest `33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2`。此为用户提供实机证据，尚非独立重测或镜像提取。
- 新增 [AVB 基线专题](docs/research/avb-live-baseline-20261018.md) 与 [Windows ADB 只读取证脚本](tools/p780-avb-readonly.ps1)；对照 Android 11 官方 avbtool 的链式 VBMeta digest 定义、NCC Group 测试公钥识别工具，明确只凭 digest 无法反推出签名钥匙。
- 同步 README、STATUS、NEXT_STEPS、专题索引、工具说明与公告专题。仍缺 `_162` 原厂 `vbmeta/boot`、经验证的 locked 写入通道；未执行刷机或 Root。
- 审核时 GitHub API 报告 visibility=public，和既有 Private 文案不符；SECURITY/README 已提示敏感原件风险，需机主确认设置并审查 Git 历史。

## 2026-10-18 — 第二轮 AVB 只读取证与仓库权限复核

- 用户新增 `ro.boot.vbmeta.hash_alg=sha256`、`ro.boot.vbmeta.size=7744`、`ro.boot.avb_version=1.1`，以及 `vbmeta_b→sde31` / `vbmeta_system_b→sda11` 等 A/B 分区映射。AOSP 实现确认 `size` 为启动所载入 VBMeta 结构总长度。
- 明确 `vbmeta_system_b` 是链式布局的强候选而非实际签名描述符的已确认内容；现仍缺原厂 `_162` 镜像、公钥指纹及可验证写入通道。
- 更新 AVB 专题、STATUS、NEXT_STEPS、README 与 PowerShell 采集脚本（新增可选公钥摘要属性、mapper 软链接及权限只读查看），未实施 Root 或刷写。
- 机主将仓库设回 Private，GitHub API 复核 `visibility=private`；SECURITY/README 同步更正，保留先前 Public 状态的潜在暴露说明。

## 2026-10-18 — AVB 第三轮：版本、dm-verity、root-only 分区与 COW

- 机主 ADB 证实：公钥摘要属性为空、`ro.boot.vbmeta.avb_version=1.0`（Bootloader libavb）、`ro.boot.avb_version=1.1`（Android fs_mgr libavb）、`ro.boot.veritymode=enforcing`。AOSP VINTF 资料说明版本差异并非异常。
- `/dev/block/sde31`、`/dev/block/sda11` 权限 `brw------- root root`；非 root Shell 只能列出而不能直接提取该 VBMeta 数据。五个 B 槽逻辑分区 dm-0..4、`system_b-cow` dm-5、五个 dm-verity dm-6..10 被原样记录，COW 仅为 OTA 快照候选而非写入或 Root 成果。
- 同步 AVB 专题、STATUS、NEXT_STEPS、README、证据索引及 PowerShell 只读取证工具；新工具补充 Virtual A/B 和 VBMeta device 的可选属性查询。设备不刷机不切槽，根本阻断仍是 `_162` 原厂 AVB 镜像与锁定态写入途径。

## 2026-10-18 — AVB 第四轮：动态分区确认、属性取证收束

- 用户实机：`ro.boot.dynamic_partitions=true`；`ro.virtual_ab.enabled`、`ro.virtual_ab.compression.enabled`、`ro.boot.vbmeta.device` 均为空。动态分区已确证，Virtual A/B 和镜像链条不因属性空而获得确认或否认。
- AOSP 文档：Android 11 Virtual A/B 使用 kernel COW，Android 12 引入压缩快照；`system_b-cow` 仍只有候选证据等级，未表明更新正在运行或出现可利用写入路径。
- 更新 AVB 专题、STATUS、NEXT_STEPS、固件/OTA 专题、README 及 EVIDENCE_MANIFEST；正式暂停普通 ADB getprop 重复采集，后续转向可信 `_162` OTA/镜像、AVB 公钥和 Descriptor 的离线比对，以及 P780 锁定态写入机制可核验来源。
- 公开搜索未取得匹配 `_162` 的可信镜像工件；搜索命中的 XDA 固件求助帖子仍未读取到完整网页或附件，不冒充已找到固件。无设备修改，Root/BL 状态不变。

## 2026-10-17 — XDA 正文补档与 Recovery 验签边界

- 原样保存用户提供的 XDA 4805241 正文，标注来源链及未独立复核状态；关闭同一正文人工获取提醒，保留既有邮件历史。
- 区分 OTA ZIP 证书与 AVB 测试钥匙；将签名失败限定为该包/该次测试结果，记录 whole-file 签名、包结构、公钥和完整日志缺口。
- 同步 README、STATUS、NEXT_STEPS、证据清单及公告专题；OPG105 仅为未验证别名，fastboot boot 未有成功证据，EDL 并非已证实唯一通道。
- 继续优先原厂镜像与可核验写入通道；未实施实机实验，Root/BL 状态不变。

## 2026-10-15 — JVN/CVE 技术归因入档

- 归档 2026-10-14 发布的 JVN#47427200、JVNDB-2026-000147、CVE-2026-107153 与 Rakuten 原公告：确认 Rakuten Hand 5G 全版本的 AVB 使用已知 AOSP 测试钥匙。
- 对照 JVN 引用的 AVBTestKeyInTheWild 论文，记录修改、重签、重建 vbmeta、设备特定部署四阶段；明确论文演示机型不含 P780，跨机型写入方法不能作为本机证据。
- 同步修订 README、STATUS、NEXT_STEPS、固件/OTA 和独立安全公告专题；把后续关卡收敛为 `_162` 原厂 boot/vbmeta 证据与 P780 锁定态写入通道。
- 本轮只做公开资料核对与文档维护，没有运行漏洞、下载执行不可信程序或刷写设备；本机仍未 Root、未解锁，Firehose 与 `_162` 原厂二进制仍缺。

## 2026-10-11 — 全库结构整理与待机监测

- 完整枚举 main 的 254 个文件，以整理前固定提交为基准，保存恢复分支 archive/pre-restructure-20261011。
- 文档按持续专题/来源规范/阶段历史分层；配置原件归位 evidence/device；初轮失败布局证据归位 run 38060293186，原始 Blob SHA 保持不变。
- 删除仅有扩展名不同且字节相同的 critical-delta.txt，保留 critical-delta.md；其它跨运行重复证据保留来源上下文。
- 重写 README、文档/证据/工具导航与待办，补齐时间线、历史验收上下文和当前原件迁移状态；全量修复相对链接及工作流配置路径。
- 候选构建与历史导入改为手动触发，自动归档检查保留并覆盖 Journey 编码原件。每日新线索监测更新为当前 GitHub 基线，仅有实质新增才通知与同步。
- 实际结构提交的 Actions #38069160978 全部通过：258 文件、48 Markdown、337 个相对路径链接/0 失效、10 Python/35 JSON、25 迁移 Blob 身份及原件/视图/字节哈希检查通过。
- 本轮是档案整理；未获取 Root/解锁/匹配原厂镜像。详见 docs/REPOSITORY_AUDIT.md。

## 2026-10-10 — Journey 消费者与匹配语义核对

- 提取性能服务及内部类 134 个有代码方法、类族之外 79 条引用/25 个调用者方法，保存反汇编、调用上下文、6 个决策方法的原始字节及逐 DEX SHA。
- 定位 OOM/进程清理与保留、Service/Provider 黑名单判定；核实末尾星号前缀匹配与精确键查询不同，RootProcess 为应用主进程概念。
- 大型 DEX 完整对象解析耗时过长，改用原始 DEX 表及指令读取；54 个既有配置方法的偏移/字节交叉核验通过，全部所扫描方法指令长度检查通过。
- 合并更新现有 Journey 专题、首页、STATUS、NEXT_STEPS、证据清单；未做实机行为实验，未发现新的 OTA/Root/解锁入口。暂缓扩大此支线，保留系统配置真实性发现及其限制。


## 2026-10-10 — Journey 实机配置核对完成

- 校验机主 3,940 B 配置 ZIP，保存可还原全部原始字节的 Base64、输入 SHA、vendor XML/version 与 TCS 阅读视图。
- XML、version.txt、运行版本均 42；39 条 XML 规则按 ALL 假设得到 64 个策略键，与实机 dump 的全部字段完全一致。
- 核实 panda、qqdownloader 重复键覆盖，不把策略条目解释为安装/系统权限；配置来源仍不能排除同内容缓存。
- 统一修订既有 Journey 报告、README、STATUS、NEXT_STEPS 和证据清单；下一阶段转为离线消费者追踪及匹配原厂固件证据，Root/BL 成果不变。


## 2026-10-10 OTA 与实机 framework 深入审计

补同步 OTA 报告/证据：6 份引擎日志均为启动清理，未得到固件。新增机主 JAR 的 54 个 Journey 方法原始字节、8 类反汇编、17 个外部引用与输入 SHA。定位应用行为 XML → JourneyPerformanceService，未证实 OTA/Root 链；统一修订 README、STATUS、NEXT_STEPS、OTA 与证据索引，记录阶段同步维护约定。原始 18MB framework ZIP/JAR 尚未迁入 Git，保留上传来源。


## 2026-10-10 — 继续研究：配置语义与候选结构布局

- 逐项扫描 24 个消失符号的 Kconfig/C/H/S/Makefile 引用，永久保存原始引用和 provenance。
- 区分 FORTIFY_SOURCE 的 Clang 依赖限制、REFCOUNT_FULL 的实现替换、不可达 NFC 菜单和未被两棵公开树覆盖的配置。
- 增加候选结构探针和 Kbuild 编译参数提取流程；固定两棵源码与 Android Clang11，保存每轮成功或失败工件。
- 首轮 TINNO 构建脚本缺执行权限已记录并修复；探针 TASK_SIZE 名称与内核宏冲突已改名，新增 32 项完整性检查；保留前两轮结果，不冒充完整布局。
- 最终 [#38060518994](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38060518994) 全部通过，两棵固定树各 32 项完整提取、0 项差异；永久保存全部原始工件。
- 专题：[配置与布局研究](docs/research/config-layout.md)。候选布局不代替原厂二进制，未实现 Root/BL 解锁。


## 2026-10-10 — 新一轮原始设备资料归档与去重

- 新收到 2 套 ADB 审计及各自压缩包、完整 Bugreport、三份 APK、两份 OTA 日志、TEE 白名单与 JNI 受限路径记录、phase3 包清单。
- GitHub Actions 校对证实，`hand5g_debloat_audit.zip` 对应展开的 22 个文件、`hand5g_final_audit.zip` 对应展开的 9 个文件**逐字节相同**；删除 31 个重复展开文件，总计 7,576,640 B，保留两个 ZIP 和完整恢复分支。
- 将原件重新组织为 `evidence/restricted/`、`evidence/apk/`、`evidence/tee/`。含敏感数据风险的系统日志不再堆放根目录；备份分支 [archive/pre-cleanup-20261010](https://github.com/Chuniex-0631/p780-kernel-research/tree/archive/pre-cleanup-20261010) 保存了清理前所有文件。
- 对照旧文件清单，特别区分历史 1,742 B 和本次 376,662 B 的同名审计 ZIP，避免误认为同一份字节原件。
- 新增 [文件去重报告](docs/archive/20261010-import-dedup.md)、[TEE/APK 资料](docs/research/tee-system-apks.md) 和 [OTA/Bugreport 资料](docs/research/ota-bugreport.md)，并更新 README、状态表、时间线、固件与应用清理专题。
- 这次整理为只读离线研究档案维护，没有实机 Root/BL 解锁或获取完整 OTA 的新成功证据。


## 2026-10-10 — 最终封存验收（经 GitHub 实际核查）

- 机主新上传的 **4 份 GhostLock 研究 ZIP** 和 **4,096 B 的 Tracefs 原始文件**已经全部入仓，按来源与用途移动至 `evidence/ghostlock/` 和 `evidence/device/`；使用 Git 已有 Blob 保持字节不变。
- 新建 [完整性报告](docs/reference/evidence-integrity.md)；Actions [#38055450831](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055450831)、[#38055530285](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055530285) 验证压缩包 CRC、SHA-256、ZIP 内部 `CHECKSUMS.sha256`、四版内嵌设备证据与主原件的字节一致性。
- 四个 ZIP 分别包含 **13 / 16 / 17 / 27** 个文件；v0.4 原始 README 首行错误标成 v0.3，已如实在 [版本索引](docs/archive/ghostlock-package-versions.md) 标记，不修改原件。
- 消除 README、GhostLock、Next Steps、文件清单、历史时间线与出处文档中“原件仍未上传”的旧描述；重写仓库首页，明确研究结果和未达成事项。
- 当时尚未迁入的材料已在**随后一轮新增上传**中部分补齐（Bugreport、三份 APK、OTA/ADB 日志），其余继续列入清单。新增原件尚未完成发布级脱敏，详见本日志上方的后续整理记录。
- 已发布 [最终验收报告](docs/archive/20261010-archive-review.md) 与全套双向证据索引；本轮为**资料验收**，没有在实体机运行漏洞、刷入固件、获得 Root 或解锁 Bootloader。


## 2026-10-10 — 首次整库整理

- 从早期 **2026-06-12 EDL / Fastboot 记录**，恢复并归档系统版本、Sahara、Bootloader、A/B 分区及历史失败信息。
- 从 2026-10-03～04 的文件，恢复 **QAS/PFM/Mink/TZAccessService** 完整技术报告与设备清理脚本/摘要。
- 归档旧版 **GhostLock v0.1–v0.4** 的资产清单、实机 Kernel Config、Tracefs 取证结论和只读核对工具；此初期记录在后续“最终封存验收”阶段已补全全部四份 ZIP 原件。
- 保存 **2026-10-10** Qualcomm 5.4.233 候选源码的原生 Kconfig、Android Clang11.0.2/14 编译过程，以及真实的 `rtmutex.o`。
- 将 GitHub Actions 原始工件转为 `evidence/actions/` 下可长久存储的 Git 文件，减少 CI 工件过期导致的资料丢失。
- 生成设备基线、可信度表、时间线、官方 OTA/安全公告、隐私规则、资料清单和当前阻断条件。
- 明确说明：**设备仍 locked，Root/BL 解锁尚未达成**，原厂 `_162` 镜像与实机匹配的 `vmlinux` 未取得。


## 未来每轮维护要求

新实验结束后，同步更新：`docs/STATUS.md` → 对应专题报告 → `docs/EVIDENCE_MANIFEST.md` → 本文件。

未经复核的结果只进入“假设/待验证”，不能更新为“成功”状态；所有 GitHub Actions 编译要保存运行编号、源码 commit、工具链版本和日志，重要工件应归档到 Git 历史。



## 2026-10-11 — 官方源码请求

- 向 TINNO 官网公开销售邮箱发送 P780 `_162` / 5.4.233 源码对应关系申请，并要求转交开源合规部门；Rakuten Mobile 暂无可靠公开源码专用邮箱，已备日语官方客服文稿但未提交。见 `docs/official-source-request-log.md`。
