# P780 实机取得 uid 0 root shell（2026-10-25）

> 2026-10-26 审计更正：本页保留早期失败上下文；后续 [daemon](p780-root-daemon-20261025.md) 和 [Elevate](../../app/elevate/README.md) 已记录 UID0 / installd 域临时 sh 成功，不能以此页概括当前 Root 状态。

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


---

## 8. 写能力实测（2026-10-25 继续）

### 8.1 策略层面

从设备自带的 CIL 解析出的 `installd` 文件权限：

| 类型 | 权限 |
|---|---|
| `apk_data_file` | append create link read rename setattr unlink write ... |
| `dalvikcache_data_file` | append create link read rename setattr unlink write ... |
| `app_data_file` | append create read rename setattr unlink write ... |

而可执行这些类型的域：

| 类型 | 可执行域 |
|---|---|
| `dalvikcache_data_file` | `zygote`、`appdomain`、`app_zygote`、`webview_zygote` |
| `apk_data_file` | `appdomain`、`app_zygote`、`webview_zygote` |

### 8.2 实机验证

在 installd 域的 root shell 里执行：

```sh
echo hello > /data/app/p780_root_test
echo hello > /data/dalvik-cache/p780_write_test
```

结果（shell 侧回读）：

```
-rw-rw-rw- 1 root root 6 /data/app/p780_root_test        # 内容 hello
-rw-rw-rw- 1 root root 6 /data/dalvik-cache/p780_write_test  # 内容 hello
```

**两个受保护目录都被成功写入**，属主 root。（`ls /data/app` 对 shell 仍是 Permission denied，
说明这是 installd 域的特权，不是文件系统权限被放开。）

### 8.3 限制

- shell 只能执行 `sh` 内建命令：`cat`/`cp`/`dd`/`rm` 都是 toybox 二进制，`system_file` 无执行权限，
  所以**无法用 shell 直接做二进制拷贝**；
- 但载荷本身（我们注入的机器码）以 root 身份运行，可以直接用 syscall 做 read/write 循环复制，
  已在 dump 载荷里验证过这种模式可行；
- 因此"APK 替换 / dalvik-cache 注入"在能力上可达，**但需要把复制逻辑写进载荷**，而不是靠 shell 命令。

### 8.4 遗留

- 两个测试文件（`/data/app/p780_root_test`、`/data/dalvik-cache/p780_write_test`）仍在设备上，
  内容是无害的 `hello`；清理需要再由载荷执行 `unlinkat`（本轮第二次载荷未触发，未清理）。
- 库已回滚，`getenforce` 仍 Enforcing，uptime 连续。

### 8.5 下一步

1. 用载荷实现 syscall 级文件复制，验证能否替换 `/data/app` 内的 APK（需处理 ART/fs-verity 校验）；
2. 评估 dalvik-cache 注入：写一个 oat/vdex 是否会被 zygote 接受（ART 会校验 oat 与 APK 的一致性）；
3. 清理测试文件。


---

## 9. fs-verity 判定：APK 可写（2026-10-25 继续）

### 9.1 方法

复用已验证的 exec-sh 载荷，只把脚本换成：

```sh
umask 0
O=/data/local/tmp/p780_verity
if read P < /data/local/tmp/p780_apkpaths.txt; then
  if echo x >> $P 2>/dev/null; then echo WRITE_OK >> $O; else echo WRITE_FAIL >> $O; fi
else
  echo NOPATH >> $O
fi
chmod 666 $O
```

触发方式改为 `cmd package compile -m speed -f <pkg>`（dexopt 会让 installd 走
`libbase::LogMessage`，且**不改变 APK 路径**，这是关键）。

### 9.2 结果

```
WRITE_OK
WRITE_OK
...
```

**从 installd 域向已安装的 `/data/app/.../base.apk` 追加字节成功**，说明本机对该 APK
**没有启用 fs-verity 强制保护**（或未对该应用启用）。

### 9.3 含义与边界

- `/data/app` 下的 APK 在 installd root 下是**可写**的；
- 但"能写"不等于"能持久注入"：安装时的签名校验、dex/oat 一致性、ART 校验仍可能拦截；
- 本次为验证可行性确实改坏了 APK（追加了若干 `x` 字节），随后用 `adb install -r` 修复，
  应用可正常启动。

### 9.4 过程中踩到的坑（重要）

1. `pm clear` 会**删除应用 cache 里的回滚备份**，导致 `unpatch` 无法恢复库——
   两次都只能靠重启清页缓存恢复。**结论：打补丁期间绝对不要执行 `pm clear`。**
2. 之前的 APK 探针载荷有栈展开错误（两个不同大小的栈帧共用一个出口），
   导致 init SIGABRT → 设备重启。已放弃该载荷，改用"已验证的 exec-sh + 只换脚本"的方式。
3. 触发 installd 的稳定方式有两个：
   - `adb install`（会改变 APK 路径，不适合路径相关实验）；
   - `cmd package compile -m speed -f <pkg>`（不改变路径，推荐）。

### 9.5 当前状态

- 库已恢复（重启后 `sentry` 入口与牺牲函数均为原始字节）；
- SELinux 仍 Enforcing；
- 应用已修复并可正常启动。
