# 归档维护日志

> **2026-10-18 batch2：** system/lib64 的514项大小/SHA-256全部匹配PC清单（509 ELF、5 bitcode）。通用 bootloader message 库不等于 Journey builtin，尚未建立调用链或新增Root能力。详见[第二批交叉分析](docs/research/p780-static-batch2-analysis-20261018.md)。

> **2026-10-18 batch1原件分析：** ZIP中742个文件条目已逐条重算大小/SHA256，全部匹配1759项PC清单中的对应内容；提取init service声明与ELF依赖。ST factory链确认属于NFC测试；Journey root诊断socket/属性动作仅为待核验权限边界，尚无可利用证据。下一步补SELinux静态映射，不运行工程动作、不恢复DSU重试。详见[原件验证与交叉分析](docs/research/p780-static-batch1-analysis-20261018.md)。

> **2026-10-18 20:31 更新：DSU 路线已由机主停止。** B已安装并尝试原生启用/重启，最终回到原厂Android11，Locked/green、installed/disabled；并非“B尚未上机”。失败阶段未知，不能认定厂商禁止DSU。恢复出厂后的原生Loader回退为用户报告，镜像身份未核实。最新实机证据、系统数据段哈希、安装器静态审计及新路线见[阶段收束与维护接口审计](docs/research/p780-dsu-closure-maintenance-route-20261018.md)。当前优先审计原厂维修/工厂测试/更新组件的权限与可核验读取入口；不重复DSU测试，Root/解锁仍未取得。下文与此冲突的DSU待测状态为历史记录。

## 2026-10-18 — 第十七轮：Android15 测试根签名 GSI 真正生成，原版与重签版 AVB 完整验证通过

- 用户Windows真实运行v1.1工具并上传AVB原始/重签info和审计TXT，3个文件本轮独立计算SHA256；AOSP `avbtool verify_image` 对两份真实1.9GB镜像都验证footer/VBMeta RSA4096签名和 system Hashtree 成功。**此前工具仅模拟验证的状态已被真实实验结果取代。**
- A组原版Google Android15 system公钥SHA256 `e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925`（Q Developer GSI）；B组重签为AOSP Root testkey SHA256 `7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`，与P780 TEE Boot Root匹配。B组完整镜像 SHA256 `fd98af142b11263e997adba190810c544857c7b750fd905a663e87256a71d880`，原版SHA256 `27321f9655530f014c884a690f49a53e6f3beeda71f4f27cbc141b17a8e86954`（PC报告）。
- 工具脚本核对VBMeta offset1899151360/size2432，分段SHA比较确认VBMeta前/后所有字节不变；文件系统、Merkle Hashtree、FEC、Footer、image大小、Flags0、RollbackIndex、SPL完全相同。VBMeta内描述符顺序不同但内容相同。助手独立比较AVB元数据28项，有效字段仅公钥发生变化。没有下载/上传完整多GB镜像作助手侧再次哈希。
- 新建 [第十七轮Windows AVB实证报告](docs/research/p780-dsu-testroot-resign-verified-20261018.md)，同步研究状态与下一步。**离线验签成功≠P780 Loaded/受信/Root**。后续优先真实ramdisk公钥；如需要上机B组，须先备份、规划清理原始DSU与Recovery失败恢复，使用非Root安装并停在Restart通知，另行确认才启动。

## 2026-10-18 — Windows OpenSSL 前置检查失败，提供离线 DSU 重签工具 v1.1

- 机主Windows PowerShell执行v1启动器在`[1/4]`阶段因`OpenSSL CLI is not on PATH`安全中止，系统镜像未修改；不是AVB验签结果，也没有连接P780。
- 已创建会话附件 `P780-DSU-testroot-offline-tools-v1.1.zip`（10708B、SHA256 `467c36c5c89957a044c2ddcb2adfaf21ed180e797c965bf8db447878f3ff17e4`）；启动器可发现当前PATH、Git for Windows和常见Windows安装目录的OpenSSL，并实际运行版本测试，只为当前进程设置PATH。若缺少OpenSSL则提示官方Winget的`ShiningLight.OpenSSL.LTS.Light`安装方式。
- 核心Python签名工具没有变更，ZIP CRC与Python语法自检通过；**尚未在用户Windows环境/真实1.9GB GSI上完成新版本签名运行**。研究方案与现行NEXT_STEPS已同步，未触碰手机、Bootloader仍LOCKED、未Root。


## 2026-10-18 — 第十六轮离线签名工具 v1：VBMeta-only重新签名和逐字节控制变量校验

- 完成用户同意的Windows PC端可下载工具包 `P780-DSU-testroot-offline-tools-v1.zip`，9769B SHA256 `189d3a4b6e92eea0cc21e24dfde29950a981b35bef72c6997925bcc26ee4dab6`，含Python脚本、PowerShell引导器和中文README；原测试Root样例私钥可由引导器自行从AOSP公开源下载，Python会校验其AVB公钥SHA256与P780 TEE已证实AOSP测试根一致。
- 为减少变量修正最初方案：**不重建 Hashtree 和 FEC**，直接保留原Android15系统镜像的fs/verity tree/FEC/footer和分区长度，仅重新签署 `system.img` 中2432B嵌入式VBMeta；新旧非VBMeta数据分区两段SHA256检查一致，前后各跑一次AOSP `avbtool verify_image`，始终Flags0且不会使用官方ZIP带Flags2的通用 `vbmeta.img`。
- 完成Python语法/真实上轮AVB metadata检验/模拟avbtool端到端测试，**尚未对完整1.9GB真镜像和Windows+原版avbtool作真实运行**；因此状态仅“工具交付、等待用户执行”。无ADB/Fastboot/EDL、手机未写入、未root或解锁。
- 详见 [第十六轮自签名GSI专项](docs/research/p780-dsu-custom-testkey-gsi-hypothesis-20261018.md)及 [NEXT_STEPS](docs/NEXT_STEPS.md)。实验产物能通过PC侧AVB签名/数据一致性校验，也不能证实P780的first-stage `avb_keys`信任样例测试Root。

## 2026-10-18 — 第十六轮：提出针对P780 AVB测试密钥漏洞的自签名DSU GSI控制变量实验

- 机主提出：既然JVN#47427200/CVE-2026-107153确认P780使用AOSP测试AVB根密钥，能否制作或编译一个测试GSI，借助DSU Sideloader保持BL Locked启动。独立核验JVN官方报告与 Android官方 DSU 自定义镜像签名机制；**理论可试，但Root of Trust 与 first-stage standalone GSI允许的公钥不是同一信任判定**。
- 通过AOSP `fs_avb.cpp` 源码确认 Locked 对GSI系统镜像独立公钥白名单做严格匹配，未知公钥不能忽略；用户实机fstab只见普通Q/R/S key，Google Android15实际system用Q Developer公钥，根测试密钥签的改版镜像也可能因独立公钥检查失败。不能把漏洞公告解读成“DSU一定能绕过AVB”。
- 经VegaBobo DSU Sideloader官方README，非Root ADB/Shizuku模式只是DSU Installer前端，不能自动绕签名；项目将解锁BL列为一般要求。在P780上只有**实际设备信任该镜像**才有锁定态成功机会。
- 新建 [实验方案：CVE-2026-107153 × AOSP测试根自签GSI × DSU Sideloader](docs/research/p780-dsu-custom-testkey-gsi-hypothesis-20261018.md)。首选固定现有Android15文件系统不从零编译新Android，仅在PC生成重签AVB副本并本地verify，必须单独同意且备份后才考虑实际DSU安装和重启。**本轮无新签名镜像、无手机操作、无Root或BL解锁**。

## 2026-10-18 — 第十五轮重大证据：Android15 system公钥确定为Q Developer，generic vbmeta不能证明可启动

- 用户运行PC离线提取后上传五件AVB元数据/公钥文件，官方ZIP SHA256在PC侧报告校验通过。助手本地独立哈希两个真实1032B公钥：Android15 `system.img` SHA1=`1ffb1af796b18ebf40d18faed213f686720f73f2`、SHA256=`e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925`，**精确匹配Q Developer GSI公钥**。
- 与P780原厂fstab仅已确认的普通 q/r/s GSI 公钥路径形成锁定态 AVB 信任配置差异的**强疑点**，但目前没有 `_162` ramdisk实际key或 first-stage AVB拒绝日志，所以不能将其登记为已确认root cause，也不能排除image mapping/active slot更早失败。
- 同ZIP `vbmeta.img` 嵌入 SHA256=`7728e30f...`的AOSP RSA4096测试root，恰好与P780 TEE attested root一致；**但Flags=2为verification_disabled，其system chain descriptor公钥SHA1=`cdbb7717...`属于另外的AOSP RSA2048 testkey，和真实 system q-developer公钥不匹配**。这种generic vbmeta不能当作系统会通过AVB的通行证，也不应刷入手机。
- 新建 [第十五轮真实公钥与AVB链式元数据审计](docs/research/p780-dsu-android15-avb-key-verified-20261018.md)、更新第十四轮事前协议、Locked信任专项、NEXT_STEPS、STATUS、EVIDENCE/README，后续研究重点是P780 `_162`可信Boot/Ramdisk及签名公钥集合。未对手机执行任何新操作。

## 2026-10-18 — 第十四轮 DSU 受信密钥取证：准备 Google Android15 GSI ZIP PC 校验与 AVB Key 提取

- 用户同意继续提取 Google Android15 非GMS ARM64 的真实 GSI signing pubkey。由之前已核验的官方 `vic/gsi-dsc.json` 及 Google官方发布说明确认为 `aosp_arm64-exp-BP1A.250405.005.C1-13151952-61d23231.zip`，完整 SHA256 `61d232315ad773bd4820c76c175efe6a61cd8a9a257508db588032be213e15f7`。
- 生成当前聊天可下载 `p780_gsi_avb_run.ps1` 和 `p780_gsi_avb_extract.py`（源码SHA及说明见 [第十四轮操作协议](docs/research/p780-dsu-android15-avb-extraction-plan-20261018.md)）；工具会验证整包SHA、只提取 `system.img`/`vbmeta*.img`、调用AOSP官方 `avbtool info_image --output_pubkey` 输出真实AVB key字节与SHA1/SHA256。Python语法与模拟数据流程测试通过，**尚未对完整官方GB级ZIP进行联机实测**。
- 强调即便拿到Android15真实签名公钥，仍**不能证明P780 ramdisk是否信任该密钥**，因为 `_162` 实际ramdisk里可信AVB文件仍缺。六份公共AOSP q/r/s普通/Developer公钥只作为参考；继续排查 first-stage DSU slot/mapping 而不无证据地归咎AVB。
- 更新 NEXT_STEPS 和研究索引，等待机主PC输出；不操作P780、不刷机、不重复DSU Restart。Root/BL Locked状态无变化。

## 2026-10-18 — DSU 卡在 Locked BL 吗？核验公钥信任分歧，调整研究优先级

- 回答机主“未解锁BL是否使DSU无法加载”的关键疑问：AOSP官方 **支持 LOCKED + Verified Boot开启**的 Developer GSI，但需预装对应受信任公钥，并非“DSU一定要解锁”。Locked 设备遇未知GSI AVB签名时，`fs_avb` 拒绝宽松验证；可信公钥是否存在是具体可验证的阻断条件。
- 将 P780 fstab 引用的**普通** q/r/s-GSI公钥与 Google AOSP **Developer GSI** q/r/s-developer公钥严格区分；结合 Google 2021-12-22 移除普通合规 GSI 公钥打包、只留 VTS 的提交，发现配置层面的强疑点。当前既没有读取P780实际 first-stage ramdisk中的信任keys，也未取得Android15 GSI实际 AVB签名公钥，**拒绝把假说写成AVB签名失败实证**。
- Android11 `gsi_tool status`源码证实非root只输出 installed/disabled，Root才打印已装GSI签名key SHA1；普通 shell 不可获得，不反复折腾权限。AOSP当前 GSI release makefile 已显式支持30～34旧VNDK snapshot（目标BP1A包未开箱验证）。
- 新建 [LOCKED/Developer GSI 信任链核验](docs/research/p780-dsu-locked-bl-vs-gsi-trust-20261018.md)，更新NEXT_STEPS/STATUS/证据/README及文档索引。仍认为 first-stage activeDSU、MapAllImages等直接返回原厂逻辑是独立高价值候选。此轮仅源码研究，无用户新ADB，也未Root/解锁/刷分区。

## 2026-10-18 — 第十三轮：P780 Bugreport 全量审计，LAST KMSG 与 LAST LOGCAT 均无法取得

- 收到机主真实 `adb bugreport` ZIP（362成员，原档SHA256 `64a097d0911e35675c75dff09d68a7e28b5aa15bd342ed796387d12758d5f141`），离线完整读取主TXT 19.7 MB / 约240,297行，未将可能含账号/设备MAC/网络记录的完整原件上传GitHub。
- 找到 `persist.sys.boot.reason.history` 中两次 `reboot,dynsystem`，换算为UTC+8 2026-10-18 06:30:31和06:31:30，确认机主连续两次手动触发DSU专用重启。属性 `gsid.image_installed=1`、`ro.gsid.image_running=0` 与原厂B槽dm映射证明收集报告时GSI不运行。
- `dumpstate` 不能读取 `/proc/last_kmsg`（文件不存在）；incidentd不能打开两个 `console-ramoops`及last_kmsg；`logcat -L`失败。当前 `dmesg`首行已是开机943秒后，因此没有包含失败的early init时段，无法确认映射/AVB/厂商启动问题。**零匹配不能写成零故障**。
- 新建 [P780 Bugreport 13轮取证报告](docs/research/p780-dsu-bugreport-audit-20261018.md)，更新 STATUS/NEXT_STEPS与证据表；停止重复同路径bugreport/logcat/kernel和无诊断差异的DSU Restart，转向可信 `_162` boot/ramdisk/first-stage 公钥及镜像签名的离线来源研究。**本轮未重新启动GSI、更改设备、获得Root/BL解锁。**

## 2026-10-18 — 找到无需再次重启的 DSU early boot 取证途径（Bugreport）

- 研究 AOSP framework/native `dumpstate.cpp::DoKmsg()` 证实官方 Bugreport 会尝试读取 `/sys/fs/pstore/console-ramoops`、`console-ramoops-0` 或 `/proc/last_kmsg` 并加入 `LAST KMSG`。普通 ADB shell pstore Permission denied、kernel logcat 0B **不能自动排除** dumpstate 对持久化 early boot 日志的访问。
- 在 [DSU 启动回退专题](docs/research/p780-dsu-stock-fallback-20261018.md) 和 [NEXT_STEPS](docs/NEXT_STEPS.md) 新增机主可选的 `adb bugreport .\P780-DSU-Bugreport.zip`，**当前尚未在 P780 执行**。不需要再次 Restart，也不触碰 boot/vbmeta；若厂商没有保存 pstore 则可能无内容。
- Bugreport 可能包含账号/网络/设备标识，强调先本地保留、脱敏后才分享，不把未经核对的原始 ZIP 提交私有或公开 Github。无新增手机实机结果，Root/解锁/DSU 可启动性结论不变。

## 2026-10-18 — DSU 启动失败后的执行决策：停止重复试错，收敛 first-stage 分支

- 基于已有 `installed/disabled`、`reboot,dynsystem`、单次重启返回原厂、Kernel logcat 0B 和 pstore权限拒绝，认定此时没有能证明具体 root cause 的第一阶段错误日志。
- 核对 AOSP Android11 `UseDsuIfPresent()` 的 `CanBootIntoGsi`、`GetActiveDsu`、`MapAllImages`、`MarkSystemAsGsi` 等可能早退路径；one-shot 机制在一次尝试中预先将**下一轮**状态置disabled，不能仅依据事后 `disabled` 判断 enable失败。
- 更新 [DSU first-stage 诊断矩阵](docs/research/p780-dsu-stock-fallback-20261018.md) 和 [NEXT_STEPS](docs/NEXT_STEPS.md)：没有新诊断观测量时不再重复 Restart；不用无 `-s` 的 `gsi_tool enable` sticky mode，不冒险换 Android16/Recovery wipe。优先查找与P780 `_162` 对应的可验证 boot ramdisk与DSU签名证据。
- 该轮**没有新的用户 ADB 实测、没有镜像下载或手机改动**，属于已收集证据上的源码审计与方案更新。Root、BL 锁和原厂镜像写入状态不变。

## 2026-10-18 — 第十二轮：DSU reboot reason 已证实，一次重启返回原厂，内核缓冲区空

- 机主明确 DSU Restart 是**单次正常重启直接回 Android11 原厂系统**，没有观察到 GSI 系统桌面或第二次自动重启。`ro.boot.bootreason=reboot,dynsystem`、`sys.boot.reason=reboot,dynsystem`，证明该次重启携带官方 DSU 专用原因；不能再把问题定位在“通知按钮没调用重启”上。
- `adb shell logcat -g` 显示 kernel buffer 配额 2MiB、当前记录**0B**；筛选 `logcat -b kernel -d` 无任何行，前次 pstore Permission denied。说明无法取得本次失败前的 first-stage 错误，不证明内核无错误。
- [AOSP Android11 `UseDsuIfPresent()`](https://android.googlesource.com/platform/system/core/+/9583e92257ab85075231b014f0999d5a5dab9910/init/first_stage_mount.cpp) 在启动允许状态、DSU slot、映像映射、indicator 等环节失败均可能返回正常系统，而 one-shot 消费使事后 status=disabled 可能正常。综合机主只重启一次的观察，**优先研究首次启动阶段早退**，AVB/映射失败具体根因尚未证实。
- 同步 DSU诊断专题、NEXT_STEPS、STATUS、README、证据表；停止重复不产出证据的 `logcat kernel`、普通 getprop 或DSU Restart。当前设备仍可进入原厂 Android11，未Root/解锁。

## 2026-10-18 — 第十一轮 DSU 日志核验与一次性启动状态消费机制确认

- 机主返回 GSID：`gsi_tool status`= `installed` + `disabled`，当前槽 `_b`，`ro.gsid.image_running` 空，pstore访问被SELinux/权限拒绝。UI重复返回原厂系统这一现象得到了安装backend的独立证据。
- 本地独立解析用户上传的 UTF-16LE 4.1MB Logcat（15455行，SHA256 `955c9775371658b36d59e749c648149193a05746a72d26807f09a3f97de6e970`）与三行过滤日志（SHA256 `333d7ac1de09d46f4a77a3611842a38d47c0ec14819d2b2b23d6ebfb2a74cf76`）；直接提取 `DynamicSystemService: isInstalled(): true`、`NOTIFY_IF_IN_USE` 和启动后通知，未发现 first-stage/AVB/镜像映射故障原始记录。**不提交原始敏感日志**。
- Android 11 AOSP `libgsi.cpp::CanBootIntoGsi` 在默认one-shot模式**本次尝试继续前**就标记下一次为disabled，因此在当前原厂系统看到disabled不能简单诊断成“UI未设置启动标记”。AOSP first_stage仍有 images map、AVB/fstab验证等后续步骤，根因尚无直接日志。
- 更新 [第十一轮调查专题](docs/research/p780-dsu-stock-fallback-20261018.md)、STATUS、NEXT_STEPS、证据清单、README，后续仅建议内核日志缓冲区/bootreason只读查阅；不重复重启、重新下载、Root或修改GSID启用状态。

## 2026-10-18 — 首次 DSU 安装提示成功，重启两次仍返回原厂系统（诊断待收集）

- 机主实际操作 DSU：GSI 下载完成、系统提示点击 Restart；至少两次手动点击后设备均重启回原厂 Android11，随后仍显示 DSU Restart 通知。**原厂系统正常可用，尚未成功运行 Android15 GSI；并非无外力的自动 bootloop。**
- 分辨 UI 完成提示和 GSID真实 installed/enabled/early boot验签：现无直接 status、pstore、logcat 和安装 build ID；AVB 公钥不匹配、one-shot状态重置、DSU映像映射失败、init/HAL故障都只是待证假说。
- 新建 [启动回原厂系统专题](docs/research/p780-dsu-stock-fallback-20261018.md)，更新 STATUS、NEXT_STEPS、EVIDENCE_MANIFEST、早期实验协议与说明；建议暂停重复 Restart、暂缓 Discard以保留证据，先用当前原厂系统保存日志与状态查询，禁止盲目 `gsi_tool enable/disable/wipe` 和其他刷写。

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
