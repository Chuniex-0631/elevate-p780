# P780 DSU 第十六轮：CVE-2026-107153 公共 AVB 测试根密钥 × 自签名 GSI × DSU Sideloader 可行性（2026-10-18）

> **历史阶段文档（2026-10-18收束）：DSU已停止。** B组后来已安装并尝试启动、最终回到原厂；本文的“未上机／下一步”限于当时阶段，不是当前指令。最新见[收束报告](p780-dsu-closure-maintenance-route-20261018.md)与[当前状态](../STATUS.md)。

> **第十七轮真实PC实验证据已返回：** 机主上传 v1.1 的三份 AVB 输出，真实 1,899,589,632B Google Android15原镜像和 AOSP Root测试密钥重签候选镜像都经 `avbtool verify_image` 报告 VBMeta签名与sha256 Hashtree 验证成功。原版SHA256=`27321f9655530f014c884a690f49a53e6f3beeda71f4f27cbc141b17a8e86954`，B组SHA256=`fd98af142b11263e997adba190810c544857c7b750fd905a663e87256a71d880`；所有非VBMeta区域经脚本强制SHA相同。旧段落“等待真实1.9GB镜像验证”属于历史状态，**最新结论请看 [第十七轮 AVB 实测报告](p780-dsu-testroot-resign-verified-20261018.md)**。P780的Locked first-stage是否信任Root测试密钥仍未知，B**尚未上机**。

> **第十六轮落地进展（2026-10-18）：** 已制作并在当前会话提供 `P780-DSU-testroot-offline-tools-v1.zip`（仅包含 `p780_dsu_resign_run.ps1`、`p780_dsu_resign_offline.py`、中文README），**未对真实多GB GSI执行最终签名**。与本页初始“重新生成hashtree/footer”设想相比，新工具改为**只重新生成并替换原 system.img 的嵌入式 VBMeta（2432B）**，通过 `make_vbmeta_image --include_descriptors_from_image` 保留原始 Hashtree/Prop 描述符，同时保持原始系统数据、Hashtree、FEC、Footer及分区大小逐字节不变。离线模拟端到端测试与真实上传 `system.img.avb-info.txt` 字段检查已通过；须待机主Windows实测 `avbtool verify_image` 才能确认实包兼容。**截至此时没有新镜像上传或设备操作，更不能确认 Locked P780信任Root测试密钥作为standalone GSI。**

> **状态：研究方案/源码分析，尚未重新签名、安装或启动任何新镜像。** 用户提出：P780 既然以AOSP测试密钥作为 Locked Bootloader 的 AVB Root of Trust，可否自编译/重签系统镜像，通过 DSU Sideloader 在 Locked 状态试验？结论是**值得做受控的本地签名实验**，但漏洞影响的 Bootloader 根公钥验证与 DSU 第一阶段额外 `avb_keys` 不等价，DSU Sideloader仅改变安装入口，不自动绕过 AVB。

## 外部权威核验

1. [JVN#47427200 / CVE-2026-107153](https://jvn.jp/en/jp/JVN47427200/) 于2026-10-14确认 Rakuten Hand5G 全版本在Android Verified Boot使用AOSP已知测试密钥，风险为有物理访问时可能安装经特殊构造的镜像；**没有声称 DSU 是已证实的利用载体，也没有声称用户持有任何解锁/flash写入能力。** 参考 [AVBTestKeyInTheWild 研究摘要](https://www.android-device-security.org/publications/)；漏洞可能被利用不意味着真实P780已具备分区写入通道。
2. 用户 P780 TEE/Google Key Attestation已核验 `verifiedBootKey` SHA256 `7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`，与公开AOSP RSA4096 `testkey_rsa4096_pub.pem`转换的AVB blob一致；Locked/green仍成立。此为**设备Root of Trust的公钥身份**，并不表示后续 DSU standalone `system.img` 自动允许该公钥。
3. [Google官方 DSU 说明](https://source.android.com/docs/core/ota/dynamic-system-updates) 支持设备厂商自签 `system.img` / `product.img`、逐镜像 AVB Footer，并要求第一阶段Ramdisk持有配对 `/avb/*.avbpubkey`；密钥黑名单和系统镜像大小等也会影响安装与启动。官方 [Android Developers DSU](https://developer.android.com/topic/dsu)说明可以通过 Android原厂 DynamicSystemInstallationService 使用 ADB触发本地 gzip 镜像安装，原则上不必额外第三方安装器。
4. [AOSP fs_avb.cpp（Android 11历史和当前实现）](https://android.googlesource.com/platform/system/core/+/d572c80acec5d04a4bee7a8d9774940839406203/fs_mgr/libfs_avb/fs_avb.cpp) 说明 standalone DSU/system AVB 公钥必须与预加载 keys 或 fstab指定 `avb_keys` 其中一把逐字节匹配；Locked时 `allow_verification_error=false`，遇未知公钥报 `Unknown public key is not allowed`。此额外检查**不是**“Bootloader vbmeta根公钥自动放行”。P780厂商固件的具体源码实现仍无对应 `_162`原件核对。
5. [VegaBobo DSU Sideloader README](https://github.com/VegaBobo/DSU-Sideloader/blob/master/README.md)：应用的非Root ADB/Shizuku模式仅调用系统原生 DSU 安装服务，并且自身说明普通GSI通常要求解锁BL，否则仅允许受信任签名。其Root/System模式可能替换 `gsid` 或使用Magisk模块，**与研究Locked stock P780 的目标相悖，不推荐**。手机此前的Bugreport中只看到应用图标，**没有证据本轮安装流程用它完成**。

## P780已经证明的签名现状

| 层 | 实机/PC可复核证据 | 不能推导出的结论 |
|---|---|---|
| Bootloader 认可的设备AVB Root | 实机Hardware Attestation SHA256 `7728e30f…6defef6` = AOSP RSA4096 test root | 不表示任何由此签名的单独 DSU system自动受信 |
| P780 `fstab`的standalone GSI键 | 配置引用普通 `/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey` | 还没读取本机 ramdisk 中真实钥匙bytes、不能排除额外key |
| 已尝试的Google Android15官方system | 真实提取 `system.img` AVB SHA256 `e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925` = Q **Developer** GSI key | 不能证明P780在AVB阶段拒绝它；也可能更早 MapAllImages/active slot回退 |
| Google ZIP附带通用 `vbmeta.img` | 真实根公钥SHA256 `7728e30f…6defef6`，Flags=2(verification_disabled)，链式system公钥是不同RSA2048测试key | **不能**证明该`vbmeta.img`在 DSU 载入，不能将其当作允许 system Q developer签名的通行证，更不能刷入原厂vbmeta |

## 关键限制：测试Root私钥≠DSU额外公钥

即使 AOSP RSA4096 测试**私钥**可以公开获得并用于在**电脑离线**重签 `system.img`，如果 `_162` first-stage standalone AVB路径只加载普通 Q/R/S GSI公钥，而这三把公钥均非 RSA4096 Root testkey（第九轮已计算公开版SHA256），那么重新签名为Root测试密钥的system依旧会在该验证阶段**被拒绝**。重签“可以生成密码学有效映像”与“能通过P780 ramdisk密钥白名单”是独立判断。绝不可为追求成功要求关闭AVB或刷入`Flags=2`通用vbmeta。

## 推荐实验流程（控制变量，不一开始编译全新系统）

**阶段0（PC纯离线，无手机变更）：** 以此前用户已SHA256核验Google Android15非GMS ARM64 ZIP中system filesystem为固定基础。原始官方镜像保留只读，拷贝另做 `system-AOSP-root-testkey.img`：仅替换AVB签名/必要的hashtree/footer，**尽可能保持system文件系统分区的原始字节、OS版本、安全补丁、partition_name、AVB rollback-index和空间预算**一致。使用公开、可追溯的AOSP RSA4096测试私钥离线做`avbtool`签名。以`avbtool info_image`、`verify_image`核对新的签名、AVB hash/hashtree、partition info和两版镜像SHA256，并记录新Key SHA1/SHA256、原始文件系统数据段比较结果。**此阶段只能证明创建了格式/密码学自洽的目标镜像，不能证明设备信任。**

**阶段1（设备前置评估）：** 尽量先通过现有 `fstab`和任何可信 `_162` boot/ramdisk进一步检查是否存在允许AOSP RSA4096测试根 key 作为 standalone DSU keys的可能；核对设备正常 Recovery恢复路径、机主重要数据备份/容量、目前安装的原版DSU临时系统如何由官方UI安全Discard。当前已安装GSI无法未经规划直接叠加另一新镜像，**不要在未保存证据时贸然覆盖**。如查明设备确实不信任Root密钥，不能把再次同参数启动作为有价值试验。

**阶段2（需机主再次明确同意的单次有对照安装实验）：** 仅在阶段0 `verify_image` 完整成功、介质/签名/分区大小/兼容性满足要求、数据与Recovery失败方案准备好时，通过官方 `DynamicSystemInstallationService` 的 ADB安装入口，或第三方 **DSU Sideloader的非Root ADB/Shizuku前端模式**，安装重签的 `system.img` 为临时GSI分区。先只验证安装状态/错误和签名预检，停止在通知 Restart；之后独立评估是否需要第一次启动该变体。**不启用 sticky，不替换gsid，不使用 Magisk、Root/System模式，不修改原厂boot/vbmeta，不用fastboot/EDL写入。**

**阶段3（解释结果）：**

| 实验结果 | 解读 |
|---|---|
| B在首次启动可进入GSI，而A用Q Developer同内容失败 | 强烈支持签名信任链差异（但要确认没有改变其它AVB参数/镜像内容，检查first-stage仍有可能不完全一致） |
| B在安装阶段被拒 | 安装入口/公钥黑名单/镜像格式/空间/权限限制候选；需要具体错误；不能认定AVB first-stage不信任 |
| B成功安装但像A一样单次重启回原厂 | 不能区分前置DSU映射问题与两把公钥均不受信；保留早退假说，不做无限重试 |
| B发生额外重启或原厂开机异常 | 立即停止继续写入；按此前确认的 Recovery/备份方案处理，承认存在userdata损失风险 |

**不推荐最初从零编译一份全新的第三方ROM：** 会同时引入Android版本、VNDK、APEX、HAL、SELinux、服务配置、分区大小与签名多个变量，不能诊断P780第一次失败的具体原因。若离线重签有意义，优先保留原始系统内容。

## 当前结论与待办

**想法可行性：可以制作并通过DSU安装自签名GSI，原则上无需先解BL；Locked成功启动是否可能，取决于P780 ramdisk单独的可信签名规则和first-stage映射等条件**。CVE-2026-107153提供真实的测试根密钥风险基础，但不是DSU成功证明。没有用户本轮新ADB结果或自签镜像，**本文件只记录新增研究方向**。下一步优先实现**完全离线、对照明确、可验证的重签实验包**；如设备密钥不信任测试根，没必要让机主冒险安装。仍Bootloader Locked，无Root成果。

## Windows v1 离线签名工具包（已创建，待真实系统镜像实测）

- 交付产物：会话附件 `P780-DSU-testroot-offline-tools-v1.zip`；**9769 bytes**，SHA-256 `189d3a4b6e92eea0cc21e24dfde29950a981b35bef72c6997925bcc26ee4dab6`。
- `p780_dsu_resign_offline.py`：**12630B**，SHA-256 `7c98b90740189d3bdc403b6b47afa8e6b8cbcc869cc1347698b73dec8d223135`。仅依赖Python标准库+AOSP `avbtool.py`、Windows OpenSSL，在本机文件上做 AVB 原始签名公钥检查、签名前 `verify_image`、密钥导出和指纹校验、`make_vbmeta_image --include_descriptors_from_image` 、对预期VBMeta位置覆盖、前后完整范围SHA256一致性检查、最终 `verify_image --key`、纯文本审计报告。
- `p780_dsu_resign_run.ps1`：**2811B**，SHA-256 `33fba5c210e007e27d001d503775b743388834c8071d65a1c5b8992d46f1cdf6`。只在PC验证前置条件、若缺失则从AOSP官方Gitiles下载公开的 `test/data/testkey_rsa4096.pem` 样例私钥（实际公钥指纹还会由Python再次强制确认），然后运行Python；无ADB、Fastboot、DSU安装、更新boot/vbmeta动作。
- 可验证输入：已完成上一轮的 `p780-gsi15-avb/system.img` 原始镜像（1899589632B），且原镜像的VBMeta offset=1899151360、size=2432、签名公钥SHA256=`e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925`、Android15 fingerprint/SPL、rollback index 1743811200、原Hashtree salt/root digest均必须符合已上传原文；**如任一条件不符必须中止**。
- 预期公钥：离线测试密钥所对应1032B AVB公钥SHA256=`7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`，与实机Bootloader Test Root摘要相同，但其在 **DSU first-stage Fstab可信keys中尚未证实**。
- 操作：把ZIP解压进机主Windows原 `RakutenHand5G`工作目录，确保已有官方 `avbtool.py` 和 `p780-gsi15-avb/system.img`、安装Python+OpenSSL、磁盘≥3GiB，运行 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\\p780_dsu_resign_run.ps1"`。
- 仅需机主分享小型 `p780-dsu-testroot-output/P780-DSU-testroot-audit.txt` 与 `testroot-avb-info.txt`，不上传多GB重签 `system.img`。未取得真实成功报告之前，**仓库不得将这一实验记为签名成功，更不得进入手机安装/重启测试**。
- 测试覆盖：工具Python语法检查通过，且用上一轮上传的真实 `system.img.avb-info.txt` 通过 metadata guard；以模拟AVB工具完成完整 `system.img` 仅VBMeta预定区域变化/签名调用/文件哈希/审计报告的端到端模拟。**未真实调用Google原版 `avbtool`+1.9GB镜像签名**，也未对Windows OpenSSL组合做真实兼容性测试。
- 为什么不重新生成 Hashtree/FEC：官方 `avbtool add_hashtree_footer` 默认依赖外部 `fec` 工具生成FEC数据，而Windows环境不一定具备。如果只换独立AVB公钥且系统/verity树原样不变，正确做法可以只重签 `VBMeta`，保留原根摘要、Merkle tree和FEC以减少变量；并严格校验新旧所有非VBMeta字节相同。详见[AOSP avbtool 源码](https://android.googlesource.com/platform/external/avb/+/refs/heads/main/avbtool.py)。
- **仍不证明设备兼容**：AOSP `fs_avb::IsPublicKeyMatching` 在Locked状态还会核对fstab/ramdisk允许的GSI公钥；即便此离线镜像能通过AVB签名自检，也不能直接宣称P780的Locked DSU会启动。


## 2026-10-18 Windows 第一轮实测：缺少可调用 OpenSSL，v1.1 仅修复自动定位依赖

机主 PowerShell 实测执行 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\p780_dsu_resign_run.ps1"`，在阶段 `[1/4] Checking prerequisites` 立即报 `OpenSSL CLI is not on PATH`，退出位置 v1 启动脚本第19行。**这是运行环境缺少可见 openssl.exe 的前置错误，不是 AVB、公钥、GSI 格式或镜像签名验证失败；脚本未执行签名、未修改 system.img、未对 P780 发起任何访问。**

已创建并在本次会话提供 `P780-DSU-testroot-offline-tools-v1.1.zip`（**10708B**，SHA256 `467c36c5c89957a044c2ddcb2adfaf21ed180e797c965bf8db447878f3ff17e4`），以及仅包含启动器的 `p780_dsu_resign_run_v1.1.ps1`（**4582B**，SHA256 `9281f049cea91fbfc51720120593ae13040d3ad79662c5920454fac8a4031cf3`）。v1.1 仅修改 PowerShell 启动器：优先使用本机 PATH 已有 OpenSSL，然后探测 `C:\Program Files\Git\mingw64\bin`、`Git\usr\bin`、`C:\Program Files\OpenSSL-Win64\bin`及部分用户级Git安装位置；**实际执行候选 openssl version 并确认退出码为0** 才继续，仅修改临时进程 PATH。若都找不到则安全停止，提示 `winget install -e --id ShiningLight.OpenSSL.LTS.Light`，由机主自行安装。该包在官方Microsoft Winget 仓库可查，不涉及Root/Flash。有关Git内部PATH可能影响DLL优先级，调整只限脚本进程而不写入永久环境变量。

**Python签名核心脚本无任何修改**：`p780_dsu_resign_offline.py`仍12630B，SHA256 `7c98b90740189d3bdc403b6b47afa8e6b8cbcc869cc1347698b73dec8d223135`；v1.1只涉及依赖检测及中文说明。修订ZIP CRC自检通过、Python核心语法检查通过；因执行容器没有原生Windows PowerShell/用户的OpenSSL环境，**还未在用户Windows真实环境完整测试v1.1发现过程，也仍未用1.9GB GSI做签名**。等待机主回传v1.1 OpenSSL版本、签名报告或下一处实际失败错误后再调整。

