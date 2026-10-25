# Elevate

**Rakuten Hand 5G（TINNO P780）的临时 root 工具。**

一个 APK、一次点击、一次安装确认，即可在该机型上获得 `uid=0` 的 root 控制台。
不写任何分区、不刷机、不关闭 SELinux；重启后自动恢复，恢复出厂即完全复原。

![界面](docs/elevate-ui-20261025-final.png)

## 下载

见 [`release/Elevate-1.0.apk`](release/Elevate-1.0.apk)（约 58 KB）。

## 使用

1. 安装 APK，打开 **Elevate**；
2. 首次会提示授予「安装未知应用」权限，按引导打开开关；
3. 点 **获取 Root** → 系统弹出「要安装此应用吗？」→ 点 **安装**；
4. 若 Play Protect 提示风险，点 **仍然安装**；
5. 约 5–10 秒后状态变为 **已连接 · uid 0**；
6. 在命令框输入 `id` 等命令，点 **执行** 查看结果。

重启后 root 消失，重复第 3 步即可。想中途回到干净状态，点状态卡右侧的 **清理**。

## 能力边界

| 可以做 | 不可以做 |
|---|---|
| 以 uid 0 读写 `/data`（应用私有目录、`/data/app`、`/data/dalvik-cache`、`/data/local/tmp`） | 写 `/system`、`/vendor` |
| 执行 `/system/bin/sh` 的内建命令与脚本逻辑 | 执行 `ls`/`cat`/`toybox` 等系统二进制 |
| 枚举全部 `/data/data` 应用目录 | 关闭 SELinux、常驻守护进程 |
| 读取任意可读文件（含系统文件） | 保持 root 跨重启 |

> 这是**文件级 root**，不是 `su` 式的完整 shell。域为 `u:r:installd:s0`。

## 原理

1. **写入**：利用 DirtyFrag（CVE-2026-43284）页缓存写原语，把 52 个 16 字节块写进
   `/system/lib64/libc++.so`，劫持 `std::ostream::sentry` 入口，载荷放进零引用的
   `__do_get` 函数里；
2. **触发**：安装内置的 13.5 KB 空包（`top.dcmqht.trigger`，无 launcher、无代码），
   `installd` 处理安装时经过 `libbase::LogMessage` → 命中钩子；
3. **执行**：载荷在 `installd` 域（uid 0）fork 出 `sh`，轮询应用私有目录下的命令文件，
   把结果写回；
4. **可回收**：清理会先发 `__quit` 让守护进程退出，再从备份恢复被改写的库字节。

详情见 [`docs/research/p780-root-daemon-20261025.md`](docs/research/p780-root-daemon-20261025.md)。

## 从源码构建

```bash
cd app/elevate
python build_elevate.py      # 产出 Elevate.apk
```

依赖：`aapt2`、`javac --release 11`、`d8`、NDK clang、`zipalign`、`apksigner`。

## 仓库结构

| 路径 | 内容 |
|---|---|
| `app/elevate/` | App 源码、构建脚本、图标、内嵌触发包 |
| `release/` | 可直接安装的 APK |
| `docs/research/` | 前期的完整研究记录（利用链、内核镜像、符号表、结构体偏移、ROM 提取） |
| `docs/rom/` | 该机型最终 ROM 的内容提取索引 |
| `tools/` | 可复跑的分析与探针工具 |

## 兼容性

仅适用于 **Rakuten Hand 5G / TINNO P780**（Android 11，内核
`5.4.233-qgki-gea5245e94afe-dirty`，构建 `P780AE_11.0_RMN_JP_162`）。
其他机型请勿使用：载荷中的函数偏移与结构体布局是逐构建验证的。

## 免责声明

仅限机主本人设备的研究与备份用途。使用本工具产生的一切后果由使用者承担。
本仓库不提供解锁 bootloader、绕过账户锁或刷写分区的能力。

## 前期研究

本项目源自一条完整的研究线：从页面缓存写原语，到内核镜像提取、符号表重建、
结构体偏移验证，最终落到这个 App。全部记录保留在 [`docs/research/`](docs/research/) 下，
包括失败的尝试与踩过的坑。
