# 从 installd root 继续提权与平台联动（2026-10-25）

> 现状：uid 0、域 `u:r:installd:s0`，可 exec `/system/bin/sh`（`shell_exec` 的
> `execute_no_trans`），可读写 `/data`（`app_data_file`、`apk_data_file`、
> `dalvikcache_data_file`、`shell_data_file`），可读 `system_file`。
> 本页基于设备自带的 CIL 策略与实机验证，判断还能走多远。

## 1. 为什么当前止步于 installd

提权的本质是**换域**或**拿到内核写**。当前两条路都不通：

| 路径 | 依据 | 结论 |
|---|---|---|
| 换域（exec 别的入口点） | `installd` 只有 `shell_exec:file execute execute_no_trans`；对 `system_file` 只有 read | 不能 exec `app_process`、`toybox`、`su` 等 |
| 内核写（改 `init_cred` / `modprobe_path`） | 无任意内核写原语；GhostLock 缺 profile | 不通 |
| 写 `/system` | `system_file` 仅 getattr/read | 不通 |
| 写 `/data/system`（packages.xml 等） | `system_data_file` 只有 `getattr relabelfrom unlink` | 不通 |

`unlink` 那一项值得注意：installd 对 `system_data_file` **可以 unlink 但不能 create/write**。
能删不能写，对提权没有直接价值，但可用于破坏性实验（不建议）。

## 2. 候选提权路线与判定

### A. 通过 `/data/dalvik-cache` 或 APK 注入获得更高域

- 可以写 `dalvikcache_data_file` 与 `apk_data_file`（已实测）；
- 但这些代码被 `zygote` / `appdomain` 加载，运行在**应用域**，不是 root；
- 目标若是系统应用，其 APK 在 `/system`（只读），注入不了。

**判定**：能获得"以某应用身份执行代码"，但不会超过该应用的权限；对"完整 root"无帮助。

### B. 通过 Binder 调 system_server 的高权限接口

- 调用方身份是 uid 0，但权限检查通常按包名/签名，native 调用方查不到包记录；
- 部分接口按 uid 判断（如 `checkCallingUid`），uid 0 有可能通过，但需要逐个实验。

**判定**：存在理论空间，需实测；即使成功也只是"以 system 身份调用某些接口"，不是 root shell。

### C. 让某个更高权限进程执行我们写的文件

- 需要"installd 可写 + 高权限域可执行"的交集；
- `system_data_file` 能 unlink 不能写，`dalvikcache_data_file` 可写但只被应用域加载；
- `/data/local/tmp` 可写，但没有 root 域从这里执行。

**判定**：当前策略下没有这样的交集。

### D. 内核侧（GhostLock / CVE-2026-43499）

- 我们已经有完整内核镜像与 173,205 条符号，`remove_waiter`、`init_cred`、
  `commit_creds` 的偏移都已验证；
- 缺的是 exploit 所需的路线几何（`waiter_shift` 等）与逐构建结构偏移；
- 一旦打通，可直接拿到内核写 → 改 `init_cred` 或 `modprobe_path` → 完整 root。

**判定**：这是唯一有希望通向"完整 root"的方向，但工程量大。

## 3. 与 Shizuku 的联动

Shizuku 的工作方式是：以 `shell`（uid 2000）或 root 身份启动 `app_process`，
在其中运行一个 Binder 服务，再通过 `rish` 让普通应用借用该身份。

| 前置条件 | 当前是否满足 |
|---|---|
| exec `app_process`（`system_file`） | ❌ installd 无执行权限 |
| 以 shell uid 运行（`adb shell` 路线） | ✅ 但那是现有 adb 能力，与本工具无关 |
| 以 root uid 运行 | ❌ 无法 exec |

**判定**：**当前 root 无法启动 Shizuku 服务端**。能用的只有原本的
`adb shell sh /storage/.../start.sh`（uid 2000）路径——那是 Shizuku 官方支持的"无线调试"方式，
与本工具无关。

## 4. 与 KernelSU 的联动

KernelSU 需要内核侧钩子（GKI 内核打补丁或 LKM 模块）：

| 前置条件 | 当前是否满足 |
|---|---|
| 加载内核模块（`insmod`） | ❌ 无内核写、`CONFIG_MODVERSIONS=y` 需逐构建符号 |
| 替换 `su` 到 `/system/bin` | ❌ `/system` 只读 |
| 提供 KernelSU 的 `/dev` 节点 | ❌ 内核未打补丁 |

**判定**：**不可能**。KernelSU 是内核方案，本工具是用户态方案，两者不在一层。

## 5. 现实可做的增强（不涉及提权）

在当前域内，可以把它做成更好用的"半 root"：

1. **文件搬运器**：以 uid 0 读取任意可读文件并按需写入 `/data/local/tmp`，
   等价于把 `cp`/`cat` 的能力内置进 App（不依赖 toybox）；
2. **应用数据备份/恢复**：读写 `/data/data/<pkg>`，做单应用备份；
3. **系统文件提取**：已实现（`framework.jar` 30 MB 校验一致）；
4. **权限修改**：对 `app_data_file` 有 `setattr`，可 chmod/chown 指定文件。

## 6. 建议的下一步实验（按性价比）

| 顺序 | 实验 | 预期 |
|---|---|---|
| 1 | 从 installd 域尝试 Binder 调用若干 system_server 接口 | 判断 uid 0 能否绕过部分权限检查 |
| 2 | 验证 `dalvik-cache` 注入是否被 ART 接受（写一个 oat 看是否加载） | 判断能否获得应用域代码执行 |
| 3 | 继续 GhostLock 的路线几何测量 | 唯一通向完整 root 的路 |

## 7. 边界声明

以上判断基于 **本机** 的策略与实测，不外推到其他机型。策略以设备自带
`/system/etc/selinux/*.cil` 为准，实机行为以实际测试为准。
