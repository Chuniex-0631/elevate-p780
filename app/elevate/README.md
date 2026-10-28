# Elevate：P780 临时 root 控制台

> 2026-10-28 文档复核：只更正解释与证据范围，未新增设备实测；当前状态以 [STATUS](../../docs/STATUS.md) 为准，历史候选步骤不作为当前执行计划。

**已实机验证**：点「获取 Root」→ 系统安装确认 → Play Protect「仍然安装」→ 安装成功 →
状态变「已连接 · uid 0」→ 输入 `id` 得到 `uid=0(root) context=u:r:installd:s0`。

## 用法

1. 打开 Elevate，点「获取 Root」；
2. 系统弹「要安装此应用吗？」→ 点「安装」；
3. 如果 Play Protect 提示风险，点「仍然安装」；
4. 约 5–10 秒后状态变「已连接 · uid 0」；
5. 输入命令（`sh` 内建命令与脚本），点「执行」查看输出。

上述受限 UID0 会话随重启消失，需重新触发；不具备已验证的永久 Root。**代码页修改针对页缓存；App/触发包与命令文件会写入 userdata。重启后的文件残留和清理结果应单独核实，不能承诺恢复出厂即可验证全部恢复。**

## 能力边界

| 可以做 | 不可以做 |
|---|---|
| 以 uid 0 在已测 `/data` 路径读写（部分应用目录、`/data/app`、`/data/dalvik-cache`）；不代表任意文件 | 写 `/system`、`/vendor` |
| 执行 `sh` 内建命令与脚本逻辑 | exec 其它系统二进制（`ls`/`cat`/`toybox`） |
| 枚举已记录的 `/data/data` 目录项（不等于读取全部文件） | 关闭 SELinux、安装系统服务 |

## 工作原理

1. **写入载荷**：用 DirtyFrag（CVE-2026-43284）把 52 个 16 字节块写进
   `/system/lib64/libc++.so` 的页缓存，劫持 `sentry` 入口，载荷落在零引用函数里；
2. **触发**：安装内置的 13.5 KB dummy 包（`top.dcmqht.trigger`，无 launcher、无代码），
   `installd` 处理安装时走 `libbase::LogMessage` → 命中钩子；
3. **守护进程**：载荷在 `u:r:installd:s0`、uid 0 下 fork 出 `sh`，轮询 App 私有目录里的
  命令文件，执行结果写回；
4. **通道**：`files/p780_cmd`（命令）、`p780_seq`（提交标记）、`p780_out`（输出）、
   `p780_beat`（心跳，用于判断存活）、`p780_lock`（一次性锁）。

## 关键实现细节（踩过的坑）

| 问题 | 原因 | 解法 |
|---|---|---|
| 安装弹窗不出现 | 广播接收器拉起 Activity 被 Android 11 后台启动限制拦截 | 改由前台 Activity 直接发 `ACTION_INSTALL_PACKAGE` |
| 重启后显示已连接但命令超时 | `p780_state` 是磁盘文件，重启后残留 | 改用 5 秒心跳判断存活 |
| 命令在 `/data/local/tmp` 无法创建 | 普通应用无该目录写权限 | 通道移到应用私有目录 |
| 锁在重启后残留 | 锁放在 `/dev`/tmp | 锁移入应用目录，App 获取前清除 |
| 命令被执行两次 | 锁用 `O_TRUNC` 而非 `O_EXCL` | 改 `O_CREAT\|O_EXCL` |

## 构建

```bash
python build_elevate.py     # 约 54 KB，含图标、R、dex、native 与签名
```

依赖：`aapt2`（资源与 R）、`javac --release 11`、`d8`、NDK clang、`zipalign`、`apksigner`。

## 已知限制

- Play Protect 会拦一次，需要手动点「仍然安装」（dummy 用自签名密钥）；
- dummy 装一次后常驻（桌面无图标，可在设置里卸载）；
- 每次重启需重新执行一次完整流程。
