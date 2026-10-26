# OEM Unlock 终结性判定（2026-10-25）

> 起因：49 号扫描发现 `ro.oem_unlock_supported=1`，与早期"`fastboot flashing unlock` 返回
> `unknown command`"的结论矛盾。本轮把 fastboot 侧所有入口一次性试完，结论：**这条线关闭**。

## 1. 设备侧状态

| 属性 | 值 | 含义 |
|---|---|---|
| `ro.boot.flash.locked` | `1` | Bootloader 锁定 |
| `ro.boot.verifiedbootstate` | `green` | 锁 + 官方 key 链 |
| `ro.boot.secboot.enable` | `yes` | Secure Boot 开启 |
| `ro.oem_unlock_supported` | `1` | 厂商属性自报"支持 OEM 解锁" |
| `sys.oem_unlock_allowed` | `0` | 用户态开关未打开 |

`sys.oem_unlock_allowed=0` 说明"OEM unlocking"开关没开；但即便打开，也要 BL 实现解锁命令才行。

## 2. fastboot 侧实测

```
fastboot getvar unlocked        -> unlocked: no
fastboot getvar secure          -> secure: yes
fastboot getvar current-slot    -> b
fastboot getvar product         -> p780
fastboot oem device-info        -> Device unlocked: false
                                   Device critical unlocked: false
                                   Verity mode: false
```

解锁/查询类命令**全部 `unknown command`**：

| 命令 | 结果 |
|---|---|
| `fastboot flashing unlock` | unknown command |
| `fastboot flashing unlock_critical` | unknown command |
| `fastboot flashing get_unlock_ability` | unknown command |
| `fastboot oem unlock` | unknown command |
| `fastboot oem unlock-go` | unknown command |
| `fastboot oem enable-unlock` | unknown command |
| `fastboot oem get_unlock_ability` | unknown command |

对比：`oem device-info` 是能执行的——说明 ABL 的 fastboot 命令表里**根本没有解锁命令**，
不是权限/状态问题。

## 3. 结论

- `ro.oem_unlock_supported=1` 只是 vendor 配置里的一个通用属性，**与实际 ABL 能力不符**；
- 本机 retail ABL 不实现 OEM unlock 命令，`sys.oem_unlock_allowed` 开不开都没有意义；
- **OEM Unlock 线正式关闭**（常规 fastboot 路径）。理论上仅剩：
  1. 厂商签名的 unlock token（无泄露则不可行）；
  2. EDL/Firehose + 匹配签名的 programmer（09 号专题已判为低优先）；
  3. 某个未公开的 OEM 私有 fastboot 命令（无从枚举，除非拿到 ABL 镜像分析）。

## 4. 记录

- `fastboot getvar all` 全量输出：[fastboot-getvar-all.txt](../../evidence/20261026/oem/fastboot-getvar-all.txt)
- 设备已正常重启回系统（`flash.locked=1`、`Enforcing`、uptime 连续）。

## 5. 对仓库其它结论的影响

- 09 号"AVB testkey"结论不受影响：即使签名不是门槛，**写分区的通道**依旧没有；
- 12/14 号"无镜像/无写通道"的结论继续成立；
- 今后不必再重复 fastboot 解锁尝试，除非出现 ABL 镜像或厂商签名工具。

