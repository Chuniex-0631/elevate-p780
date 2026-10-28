# 厂商预置服务审计（第一轮）：Journey 根服务与属性触发的 init 原语（2026-10-25）

> 2026-10-28 文档复核：只更正解释与证据范围，未新增设备实测；当前状态以 [STATUS](../STATUS.md) 为准，历史候选步骤不作为当前执行计划。

> 2026-10-26 审计更正：字节复核更正：misc offset64 实际为 `recovery\ntest\n`，值从73起；不是 `recovery.test`。三份样本仅73–84改变，恢复样本全字节相等。固定字段写不等同任意 BCB command/分区写入，详见[本轮复核](p780-boot-edl-audit-20261026.md)。

> 背景：在"已有 root 代码执行、但受 SELinux 域限制出不去"的瓶颈下，转向 TINNO/Journey
> 预置服务，寻找新的域跳板或更高权限接口。本轮完成静态盘点与两次受控实机验证。
> 结论先行：**diag socket 对 app/shell 不可达；但发现一条 shell → init 域的 misc 写原语。**

## 1. 结论摘要

| 发现 | 级别 | 状态 |
|---|---|---|
| `journey_diag_ext_system` / `_vendor` 以 **uid 0** 常驻运行；system 侧有 `/dev/socket/diag_ext_socket`（SOCK_SEQPACKET，权限 0666） | 高关注 | 已确认运行 |
| **`sys.journey.diag.write_misc` shell 可写**，init 收到后把值写进 **misc 分区**（样本值从十进制 73 起，保留 `recovery\n` 前缀） | **新原语** | 已实机验证、已还原 |
| `sys.journey.restorecon` → init 执行 `restorecon_recursive <属性值>` | 待评估 | shell 可写已确认 |
| `sys.journey.diag.wallpaper.theme` → init 向固定文件写任意内容 | 低 | 静态可见 |
| `odm.journey.diag.factory.reset=1` → `write_misc --wipe_data` + 重启进 recovery | 危险 | 未测试（odm 属性 shell 不可写） |
| 其它 root 服务：`qttestservice`（root，oneshot，属性触发）、`poweropt-service`（root，常驻） | 中 | 静态可见 |

## 2. 服务清单

### 2.1 Journey diag（uid 0，常驻）

```
service journey_diag_ext_system /system/bin/journey_diag_ext_system
    user root
    socket diag_ext_socket seqpacket 0666 system system
    group vendor_qti_diag root readproc system radio vendor_rfs_shared sdcard_rw media_rw sdcard_r shell drmrpc
    disabled
on property:persist.vendor.diag.journey.enabled=1
    start journey_diag_ext_system
```

实机：`init.svc.journey_diag_ext_system = running`、`init.svc.journey_diag_ext_vendor = running`；
`/proc/net/unix` 可见 `/dev/socket/diag_ext_socket`（LISTEN）。

### 2.2 其它 root 服务

| 服务 | 用户 | 触发 | 备注 |
|---|---|---|---|
| `qttestservice` | root | `vendor.qttestservice=enable` | oneshot，`/vendor/bin/qttestservice` |
| `poweropt-service` | root | 常驻（class main） | `/vendor/bin/poweropt-service` |
| `journey_diag_ext_vendor` | root | `persist.vendor.diag.journey.enabled=1` | 无 socket，走 diag 设备 |

## 3. diag socket 可达性（实测：不可达）

JNI 探针（`am start -e probe diagsock`）在 **untrusted_app** 中实测：

```
uid=10232 ctx=u:r:untrusted_app:s0:c232,c256,c512,c768
stat              -> -1 EACCES (13)
getxattr(selinux) -> -1 EACCES (13)
socket(SEQPACKET) -> 65 ok
connect           -> -1 EACCES (13)
socket(STREAM)    -> 65 ok
connect           -> -1 EACCES (13)
```

- app 连 `stat`/`getxattr` 都被拒；`connect` 两种类型均 EACCES；
- shell 侧此前也已确认被拒（`ls -lZ /dev/socket/diag_ext_socket` → EACCES）；
- installd 域载荷（uid 0，raw syscall）实测同样是 `connect -> -13 EACCES`：

```
socket(SEQPACKET) -> 8    connect -> -13
socket(STREAM)    -> 8    connect -> -13
```

三个域全部 EACCES：

| 域 | stat/getxattr | connect |
|---|---|---|
| `untrusted_app` | EACCES | EACCES |
| `shell` | EACCES | — |
| `installd`（uid 0） | — | EACCES |

**结论：Journey diag socket 对 app / shell / installd 全部不可达，这条线关闭。**

## 4. 新原语：shell → init 写 misc 分区

### 4.1 机制

`journey.init.rc` 中：

```
on property:sys.journey.diag.write_misc=*
    write_misc ${sys.journey.diag.write_misc}
on property:sys.journey.restorecon=*
    restorecon_recursive ${sys.journey.restorecon}
on property:sys.journey.diag.wallpaper.theme=*
    write /mnt/journey/journey_persist/wallpaper.theme ${sys.journey.diag.wallpaper.theme}
```

`sys.journey.diag.write_misc` 没有被 property_contexts 特别标注，实测 **shell（uid 2000）可以 setprop**。

### 4.2 实机验证（misc 分区前后对比）

```
原始 misc offset 64 起:   recovery\ntest\n
setprop ...write_misc P780WMARK01
写入后:                  recovery\nP780WMARK01\n
setprop ...write_misc test
恢复后:                  recovery\ntest\n   （与原始 dump 逐字节一致，diff = 0）
```

- 样本 offset 64–71 是 recovery，72 是换行；值从 73 起，差异仅 73–84；0–63 的 command/status 未变；
- `journey_diag_ext_vendor.rc` 里存在 `write_misc --wipe_data` + `setprop sys.powerctl reboot,recovery`，
  这仅为另一条静态动作记录，不能证明普通文本写入控制相同 BCB/启动语义；
- 即：**未提权 shell 可触发 misc 固定文本字段写入；启动模式是否受其控制未证实**。

### 4.3 影响与边界

- 不等同 root：misc 是 1 MiB 标记分区，写的是文本标记；
- 未建立该字段到 Bootloader/Recovery 启动选择的完整消费链，不将其称作可控 boot-mode 接口；
- 本次恢复样本与原件相等，仅证明该次还原，不保证任意未来写入可恢复。

## 5. 第二原语候选：`sys.journey.restorecon`

`restorecon_recursive ${sys.journey.restorecon}`：shell 可写该属性（rc=0），init 以 `u:r:init` 对任意路径重打标签。
`restorecon` 只能按 `file_contexts` 赋默认标签，不能指定目标类型；需要找"可控路径 → 特权标签"的映射才能利用，
目前希望不大，先记录。

## 6. 历史候选（当前暂停，见 ../NEXT_STEPS.md）

| 任务 | 方法 | 停止条件 |
|---|---|---|
| installd → diag socket | installd 载荷 `socket()+connect()` 探针 | 仍 EACCES 则该线关闭 |
| `restorecon` 属性利用评估 | 找可写路径与特权标签映射 | 无映射则关闭 |
| journey 二进制协议 | 用 installd/init 载荷拷出 `system/bin/journey_diag_ext_system`（shell 无读权限） | 载荷拿不到文件 |
| boot-mode 标记枚举 | 从 Bootloader/Recovery 镜像找有效 `recovery.*` 值 | 无镜像则保持未判定 |

## 7. 边界

- 本轮只做属性写入与分区 dump，misc 恢复样本与原件相等（diff=0）；不等于整个设备没有文件残留；
- 设备保持 `Enforcing`、libc++ 未打补丁。
