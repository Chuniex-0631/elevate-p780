# P780 ABL / EDL 只读复核（2026-10-26）

基线提交：`60fe37381d4c2b7bf5152d1d8b36cf5ebbcbc3de`。本轮未连接手机、未执行 ADB/fastboot/EDL、未刷写；只读取仓库文件与公开网页。历史设备操作以下均注明为历史记录。本页修正旧专题中过强的推论，不把未证实项视为成功。

## 1. ABL 原件与地址体系

| 输入 | 字节 | SHA-256 |
|---|---:|---|
| `evidence/20261026/partitions/abl_b.00.bin` | 1048576 | `cf1487794d6e7288092e78f29590a72a74255213760da409c3fd72131c86680b` |
| `evidence/20261026/abl/abl_lzma.bin` | 434376 | `8bca951a25f8bd19a38bca333843f7a982b589d738d6a518bbb934c5afd87437` |

本轮从分区原件 `0x3078` 开始用 Python LZMADecompressor 解压，与现存解包文件逐字节相等。解包文件自身仍有 FV 包装，PE 从 **0xb8** 开始；不能把解包文件偏移直接当 PE RVA。PE 为 AArch64 (`0xaa64`)，`.text` RVA/raw 均 `0x1000`、长度 `0x4d000`；`.data` 在 `0x4e000`。下文地址一律是 PE RVA，换算本解包文件偏移为 `RVA + 0xb8`（仅适用于这份布局），不是运行时绝对地址。

工具：[control_flow_audit.py](../../tools/abl/control_flow_audit.py)。局部 ADR/ADRP+ADD 扫描只是引用候选；本轮关键结论另人工核对了下述反汇编。没有完整恢复间接调用图，也没有反编译所有路径。

## 2. fastboot 命令注册与分派

**已证实的静态链**：

1. `0x310d0–0x310f4`：表基址计算为 `0x4ae88`，每次加 `0x10`，`ldp x0,x1,[x8,#0x10]`，共 `0xe0 / 0x10 = 14` 次调用 `0x312d0`。实际首条表项在 `0x4ae98`。
2. `0x312d0–0x31310`：分配 `0x20` 字节节点，保存命令指针至 `+8`、长度至 `+0x10`、handler 至 `+0x18`，链接到全局 `0x680d8`。
3. `0x2f988–0x2f9c0`：遍历同一链表，比较命令前缀，命中后 `blr x9` 调用保存的 handler；未命中路径引用 `unknown command` (`0x2f9ec`)。

完整 14 项及 handler 见[机器表](../../evidence/analysis/boot-edl-20261026/fastboot-registration.json)：

| 命令 | Handler RVA |
|---|---|
| `oem enable-charger-screen` | `0x31390` |
| `oem disable-charger-screen` | `0x313e8` |
| `oem off-mode-charge` | `0x31440` |
| `oem select-display-panel` | `0x315b0` |
| `oem device-info` | `0x31934` |
| `continue` | `0x31a04` |
| `reboot` | `0x31ac4` |
| `reboot-recovery` | `0x31b00` |
| `reboot-fastboot` | `0x31b58` |
| `snapshot-update` | `0x31bb0` |
| `reboot-bootloader` | `0x31d10` |
| `getvar:` | `0x31d54` |
| `download:` | `0x32000` |
| `oem display-cmdline` | `0x321ec` |

这张已执行注册循环中**没有** `flashing unlock`、`oem unlock`、`boot`、`flash:`、`erase:`。本轮逐字解码 `.text` 搜索直接 `bl 0x312d0` 仅命中 `0x310ec`；不排除间接调用、其它阶段或不同固件的注册。历史 `unknown command` 与本镜像所见吻合；结论限定为本镜像、本注册路径，不能表述为所有固件永远无法解锁。`download:` 存在只说明可接收缓冲区，不证明可启动或持久写盘。fastbootd 是另一实现，不可用 ABL 的表覆盖其行为。

## 3. FRP / OEM Unlock：确认了什么

`0x31100` 构造指向 UTF-16 `frp` (`0x4ae80`) 的参数，`0x31108 → 0x32624 → 0x3232c` 获取分区对象；成功分支 `0x311b0–0x31210` 按对象给出的块长度分配缓冲区，经对象函数指针读取，返回 0 后取**该缓冲区末字节 bit 0**写入全局 `0x68080`。这是块缓冲区末字节；本轮尚未完整追踪所读 LBA，不能直接把它等同整分区末字节。

`IsAllowUnlock is %d` 日志在 `0x31130` 读取同一全局。`Error Reading FRP partition` 则在错误路径打印状态。由此可以确认有真实 FRP 读取与许可位缓存，已超出字符串相邻证据。

**未证实**：本轮没有找到该缓存到“显示 Unlock 菜单”的完整消费链。`Creating unlock keys detect event` 字符串存在，但局部引用扫描没有建立其可达路径。历史菜单无 Unlock 只能作为观察，不能反推本次门控一定为 0，不能把 Android 的 `sys.oem_unlock_allowed` 当同一时刻的 ABL 内存值。仓库 `frp.00.bin` 的末字节本轮读得 0，但前述读取位置与采集时序尚未闭合，所以不能据此补齐门控因果关系。

Android 侧 Journey gate 的证据独立成立：[OEMLOCK-01](p780-oemlock-journey-gate-20261019.md) 记录服务 getter 在读取后端后还检查缓存的 `IS_CUSTOMER_VERSION`；这不自动证明 ABL 使用同样条件。UID0、UI开关、后端许可位、BL unlocked 状态是不同层。

## 4. FFBM/QMMI 与 Journey misc

ABL `0x1dc60–0x1dd90` 存在读取缓冲区、错误分支以及与 `qmmi`、`ffbm-02`、`ffbm-` 比较的真实指令路径。本轮没有完整追踪读取偏移与菜单所有路径。历史选择 FFBM/QMMI 后回 Android，不足以证明“retail 无工厂镜像”；可兼容配置、启动参数、用户空间回退等不同解释。

本轮离线比较三份 misc：

- 原件 offset 64 实际是 **`recovery\ntest\n`**；此前文档用点号表示分隔符不准确。`recovery` 占 64–71，换行是 72，`test` 从 73 起。
- `misc_after` 与原件差异仅在十进制 **73–84**，形成 `recovery\nP780WMARK01\n`；0–63 的 command/status 未变化。
- `misc_restore` 与原件完整 1048576 字节相等。这是恢复样本一致性，不能代表任意未来实验都能恢复。

历史 `write_misc` 验证的是固定字段写入，不是任意分区/任意偏移写，更不证明能改 BCB command、FRP、devinfo、RPMB 或解锁。`restorecon_recursive` 按既有 file_contexts 恢复默认标签，不是任意设置 SELinux 域。diag socket 的历史 EACCES 仍按具体调用域/操作记录；socket DAC 0666 不等于 SELinux 可达。

## 5. 受限 UID0 与 Root 成功记录

[root daemon 记录](p780-root-daemon-20261025.md) 保存了 `uid=0(root) ... context=u:r:installd:s0` 和 `Enforcing` 输出；[Elevate README](../../app/elevate/README.md) 记录 App 工作流及相同身份。故“未取得任何 Root shell”已过时，应更新为：**历史记录已取得临时、SELinux installd 域下的 UID0 shell；BL 仍锁定，完整 EDL 未取得，永久 root 未证实**。

本轮没有上机复现；daemon 专题的文本输出与 App 实测说明属于仓库保存记录，不能冒充本轮新实测。早期 `exec` 和路径写入失败是特定载荷、标签、时序下的负例，不能覆盖之后已成功的 sh 守护。目录名枚举 282 项不证明能读取所有应用文件。`sh` 可执行也不推出 toybox、su、域切换或 selinuxfs 可写。保留旧专题作为历史阶段，并标注后续结果，避免删掉失败证据。

## 6. 当前结论与后续停止条件

BL/完整 EDL 目标仍未完成。当前最具体的离线发现是：本 ABL 注册路径没有 unlock 命令；FRP 存在真实读取，但菜单因果链未闭合；受限临时 UID0 已有成功记录。

下一步应优先补全 `0x68080` 的消费者与间接注册调用、核实其它固件 ABL 的差异；取得有来源的 loader 后使用[筛查清单](p780-firehose-screening-20261026.md)。只有供应商提供 P780 精确版本的读取能力证据、授权条件、GPT/LUN 与小分区重复读取哈希，才可把商业 EDL 读分区记为已证实。此次没有新候选足以进入设备验证；不以搜索未命中宣称全球不存在 loader，也不把同 SoC 或 PKHash 前缀一致当刷写许可。

相关证据：[注册反汇编](../../evidence/analysis/boot-edl-20261026/frp-registration-disassembly.txt)、[分派](../../evidence/analysis/boot-edl-20261026/fastboot-dispatch-disassembly.txt)、[注册辅助函数](../../evidence/analysis/boot-edl-20261026/register-helper-disassembly.txt)、[输入与比较清单](../../evidence/analysis/boot-edl-20261026/input-manifest.json)。
