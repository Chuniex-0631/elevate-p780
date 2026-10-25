# 下一阶段研究选择（2026-10-25）

> 基于仓库现有全部结论、2026-10 的新公开线索，以及本轮已经取得的能力（受限域代码执行），
> 对"接下来做什么、哪些半途而废的路线值得重启"给出排序与判据。本页只做决策，不重复证据；
> 证据以 [`STATUS.md`](../STATUS.md) 与各专题为准。

## 1. 我们现在手里有什么

| 能力 | 覆盖范围 | 限制 |
|---|---|---|
| DirtyFrag 页缓存写入 | 任意**应用可读**文件，16 字节块、内容可控 | 不可写不可读的文件（`*_exec` 标签）无法作为目标 |
| 代码执行 | init 域、installd 域（均 uid 0） | 两域 `exec` 被拒；`/data/local/tmp` 写入被拒 |
| 文件外带 | init 域可把任意可读文件写到 `/metadata`（已搬运 netd 820 KB、installd 367 KB） | 写入依赖目标文件本身可读 |
| 回滚 | 页缓存逐字节写回，或重启 | `pm clear` 会删掉应用内备份 |

这三条合起来，本质上是**一个"以 init 身份只读取证"的通道**——这正是过去所有卡在"没有镜像 / 没有内核符号"的工作所缺的东西。

## 2. 半途而废的路线：逐条判定

| 路线 | 当时为什么停 | 现在值不值得重启 | 理由 |
|---|---|---|---|
| **GhostLock / CVE-2026-43499** | 缺 5.4.233 的 `Image`/`vmlinux`，算不出逐构建偏移 | **值得，且优先级最高** | 阻塞点正是我们现在能突破的：init 域可以尝试读块设备与内核文件 |
| **内核镜像 / 源码身份** | 官方与第三方都拿不到 `boot.img` | **值得** | 同上；拿到 `boot.img` 同时解决 GhostLock、`esp_input` 验证、AVB 链三条线 |
| **DSU / GSI** | 机主 2026-10-18 明确停止，失败阶段未知 | **低价值** | 即使跑通也只是"另一个系统"，不改变 locked bl 与 SELinux；且需要重开已被叫停的安装实验 |
| **OEM Unlock（OEMLOCK-02）** | 296 份 APK/JAR 中无普通调用者入口 | **先做一次终结性判定** | 现在可以用 uid 0 直接发 Binder；但要先确认 BL 是否支持 unlock——历史上 `fastboot flashing unlock` 返回 `unknown command`，若确实不支持，则整条线应当宣布死亡 |
| **EDL / Firehose** | Sahara v2 可达，缺匹配签名的 programmer | **维持低优先** | 没有厂商泄露或同型号 programmer 就不会有进展；可作为长期机会性搜索 |
| **AVB 测试密钥** | 身份已核验，但 locked 无写通道 | **不重启** | 结论已闭合；除非出现新的写通道，否则重复采集无意义 |
| **Frame/Journey 静态扫描** | 已扫完 296 份，无新入口 | **不重启** | 已穷举，重复无收益 |

## 3. 推荐的新主线（按性价比排序）

### 主线 A：把"init 只读取证"变成内核镜像（第一优先）

一句话：**既然 init 域能读文件并写 `/metadata`，就先测它能读什么，再用它去拿 `boot.img`。**

第一步实验（一个补丁周期即可全部回答）：

| 实验 | 目标路径 | 意义 |
|---|---|---|
| A1 | `/dev/block/by-name/boot_b`（及 `boot_a`） | 能读 → 直接拿到内核镜像 |
| A2 | `/proc/kallsyms` 前 4 KiB | 是否被 `kptr_restrict=2` 全部置零 |
| A3 | `/sys/kernel/notes` | 内核 build-id，用于匹配公开 vmlinux |
| A4 | `/proc/kcore` 前 4 KiB | 能力允许时可做内存侧符号定位 |

判据与停止条件：

- A1 成功 → **整条 GhostLock 线解锁**：从 `boot.img` 抽 `Image`，比对 `uname -r`/编译时间/config，再生成 5.4 profile 所需的偏移。
- A1 失败但 A2/A3 成功 → 仍可用 build-id 去公开构建库匹配同源内核，价值次一档。
- 四项全失败 → 记录为"init 域块设备/内核文件不可读"，回到主线 B。

### 主线 B：找"能 exec 或能写用户区"的域（第二优先）

已知 `libbase` 的 `LogMessage` 钩子在 installd 里确实生效（275 个调用点，标记落地）。下一步是**换域**：

1. 用主线 A 的外带能力把 `vold`、`zygote64`、`system_server` 的二进制拉出来（它们在 shell 侧不可读，但 init 域可读的可能性存在）；
2. 查它们的 `.dynsym` 是否 import `LogMessage`；
3. 对 import 的域试钩（`vold` 优先：uid 0、能写 `/data`、能挂载）；
4. 用"必然发生的事件"触发（插拔 USB / 屏幕解锁 / 安装应用）。

判据：拿到一个**同时能 `exec` 且能写 `/data`** 的域，才算真正打开 root 交付通道；只满足其一的域按负结论记录。

### 主线 C：OEM Unlock 的终结性判定（一次性，成本低）

用 uid 0 直接向 `OemLockService` 发 Binder 事务，调用 `setOemUnlockAllowedByCarrier(true, …)` 或 `setOemUnlockAllowedByUser(true)`，然后读回状态、看设置项是否变灰。

- 若权限被拒 → 记录为"uid 0 也不满足 signature 校验"，该线彻底关闭；
- 若成功但 `fastboot flashing unlock` 仍 `unknown command` → 说明 BL 不支持解锁，同样关闭；
- 只有两者都通才值得继续（概率低）。

## 4. 不建议现在做的事

- **重复 DSU 安装**：已被叫停，且收益与 locked bl 现状不匹配。
- **盲目 EDL 重试**：无 programmer 时每次重试都可能让设备停在 EDL，收益为零。
- **继续在 liblog 上找落点**：`liblog.so` `.text` 无零填充洞、最大函数 308 B，现有载荷 608 B 放不下；除非先做出 ≤170 B 的最小载荷。
- **把 SKELETONKEY 之类 Linux LPE 合集直接套用**：其 GhostLock 模块是"重建的、故意欠驱动的"触发，且收尾依赖 `modprobe_path`，而 P780 的 `CONFIG_STATIC_USERMODEHELPER=""` 让该路径失效。

## 5. 新线索评估（2026-09 至 2026-10）

| 线索 | 内容 | 对本机的价值 |
|---|---|---|
| [SKELETONKEY](https://git.churchofmalware.org/leviathan/SKELETONKEY) | 46 个 Linux LPE 模块 / 41 个 CVE 的合集，含 ghostlock 模块 | **低**：面向 x86/arm64 Linux 发行版，收尾依赖 `modprobe_path`，不适用于 Android 的 UMH 禁用与 SELinux |
| [DFRoot](https://github.com/diabl0w/DFRoot) | DirtyFrag 的完整链，仍以 `insmod` 收尾 | **低**：P780 的 `CONFIG_MODVERSIONS=y` 要求逐构建 `Module.symvers`，无匹配模块即不可用 |
| [Poco M7 Plus 越狱记录](https://kitploit.com/de/tools/github/aniketlab/poco-m7-plus-jailbreak) | 同代 SM6375 上 GBL 注入可用、GhostLock 在 6.1 内核 panic | **中**：佐证 GhostLock 对内核版本极敏感，5.4 必须自建 profile |
| [CVE-2026-24088 PoC](https://github.com/kasnria001/qualcomm_gbl_exploit_poc) | ABL 命令行注入（`set-gpu-preemption`） | **中**：一条命令即可判定，属于主线 C 的补充实验 |
| XDA 两条 P780 求固件帖 | 至今无可用回复 | **中**：说明公开渠道确实没有 `boot.img`，主线 A 的价值更高 |

## 6. 建议的执行顺序

1. **主线 A 的四项探测**（一个补丁周期，只读，无状态改变）——本轮就能做；
2. 若 A1 成功：转 GhostLock 适配（需要一次专门的 profile 设计）；
3. 若 A 全败：转主线 B 的域普查（需要先外带三个守护进程二进制）；
4. 主线 C 作为一次性的低成本判定，可随时插入。
