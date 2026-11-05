# 新突破口：不要再写 A 槽，先解决“写哪个槽 + 怎么激活”

日期：2026-11-05。对象：Rakuten Hand 5G / TINNO P780（holi / SD480，Android 11，5.4.233）。
本文只做离线分析与实验设计，未连接设备、未新增写入。
> **实测后注记（2026-11-05 晚）**：本文是实验前设计，部分前提已被实测修正：
> `boot_a` 实际为空白（前 4 KB 0xAA、其余全 0），无法补全 stock A；A 槽写入已成功，
> 但 `SetActiveBootSlot(A)` 未改变 GPT，重启仍进 B。实测记录见
> [2026-11-05 总结](p780-20261105-summary.md)。


## 1. 现有资产（来自本仓库）

| 能力 | 状态 |
| --- | --- |
| 临时 UID0（`u:r:installd:s0`） | 已达成 |
| DirtyFrag 页缓存写 + init/installd 域代码执行 | 已达成 |
| AVB 根信任 = AOSP `testkey_rsa4096`，`vbmeta_system` = `testkey_rsa2048` | 已核验 |
| OTA 验签绕过：页缓存替换 `/system/etc/security/otacerts.zip` | 已实测 `Verified correct signature` |
| update_engine 写入 `boot_a` 4096 B REPLACE | 已实测 |
| 写 `vbmeta_[ab]` 的策略权限 | `vbmeta_*` 标为 `vendor_custom_ab_block_device`，`update_engine_common` 有 `vendor_custom_ab` 写权限 → **可写** |
| 完整 `boot_b_full.img`、`vbmeta_b`、`testkey_rsa4096.pem` | 已在仓库 |
| `boot_a` 完整镜像 | **缺**（只有 B 槽 51 MB 全量；A 槽仅 vendor_boot_a/dtbo_a） |
| 切槽（SetActiveBootSlot / GPT） | 未证实；历史日志只有 `Marking new slot as unbootable` |

## 2. 关键认识：update_engine 永远写“非当前槽”

AOSP 11 `update_attempter_android.cc`：

```cpp
install_plan_.source_slot = GetCurrentSlot();
install_plan_.target_slot = GetTargetSlot();
...
BootControlInterface::Slot UpdateAttempterAndroid::GetTargetSlot() const {
  return GetCurrentSlot() == 0 ? 1 : 0;
}
```

当前槽是 B（`_b`），所以 update_engine 只会写 **A** 槽，然后尝试 `SetActiveBootSlot(A)`。

之前的 A 槽实验失败，很可能不是“AVB 不接受”，而是：

1. 只写了 4096 B 的 `0xAA` 探针，本来就不可能启动；
2. A/B 两槽构建不同（A=263，B=264），`vendor_boot_a` 与运行内核不同源；
3. 切槽是否成功没有闭环验证。

因此，**直接写当前槽 B** 可以绕开整个切槽问题：B 本来就是 active，AVB 用公开 testkey，写完整 `boot_b` + `vbmeta_b` 后重启即可。

## 3. 三条可行路线（按性价比排序）

### 路线 1（最低风险，先做）：补全 A 槽，让 update_engine 自己切

1. 用现有 init 域读块设备原语，完整 dump `boot_a`（A 槽 stock，51 MB 级）。
2. PC 离线：Magisk/KernelSU 修补 `boot_a`，用 `testkey_rsa4096` 调 `avbtool add_hash_footer` 重签
   （rollback index 取 ≥ 原值）。
3. 用原厂 `vbmeta_a` 只替换 boot 描述符的 hash/size，重新用 testkey 签名，保持其它链描述符不变。
4. 用现有 `mkpayload_boot.py` 扩展成 `partition=boot` 全量 REPLACE + `partition=vbmeta` 全量 REPLACE，
   用自建 OTA 证书签名；页缓存替换 `otacerts.zip` 后走 update_engine。
5. 写完后**先只读验证**：`dd` 读回 `boot_a`/`vbmeta_a` 的 SHA-256，对比本地；再读 GPT 属性确认
   哪个槽 active。
6. 重启，观察是否进 A 槽、AVB 是否 green、Magisk 是否在。

验收点：`SetActiveBootSlot` 是否真的生效（GPT 属性变化），以及 A 槽系统 263 与 A 槽 vendor 是否配套。
若 A 槽 system 与 vendor 不匹配导致起不来，则路线 1 仅能证明“写+切槽”，不能交付 root。

### 路线 2（最直接，需补丁）：让 update_engine 写当前槽 B

目标：`GetTargetSlot()` 返回 B（1），`SetActiveBootSlot` 不把槽切走。

可选补丁方式（按可行性）：

1. **页缓存改 `update_engine` 的 `.text`**：
   - `GetTargetSlot()` 只有几条指令，改成 `mov w0, #1; ret`；
   - 或改 `GetCurrentSlot()` 返回 0，使 target=1（B），同时把 `SetActiveBootSlot` 改成直接返回 true。
   - 运行中的 `update_engine` 是文件页映射，页缓存写入对已映射代码页可见（与现有 libc++ 钩子同原理）。
2. **改 `boot_control` HAL 服务**的 `getCurrentSlot()` 返回值（返回 0），让 update_engine 以为当前是 A。
   HAL 是独立进程，需要同样用页缓存代码钩子 + 触发一次 binder 调用。
3. **GPT 属性临时翻转**：把 active 从 B 改成 A（hal_bootctl 域有 gpt 写权限），
   update_engine 就会写 B，成功后它再把 active 设回 B。风险最高（GPT 双份+CRC）。

写 B 的好处：B 是当前槽，`vendor_boot_b`、`system_b`、`dtbo_b` 全是配套的 264 构建，
只要 `boot_b` 和 `vbmeta_b` 是 testkey 签名且描述符一致，AVB 必然通过。

### 路线 3（兜底）：拿 `hal_bootctl` 域的代码执行

`hal_bootctl` 策略同时有 `boot` 和 `gpt` 写权限（`update_engine_common` 只有 boot/vbmeta）。
如果能在这个域执行代码，就可以：

- 直接 `pwrite` 完整 `boot_b`；
- 直接改 GPT active/successful 属性；
- 甚至不需要 update_engine 和 OTA 证书。

难点是进入该域：需要给 `android.hardware.boot@1.1-service` 或其库打页缓存钩子，并触发一次
`getCurrentSlot/setActiveBootSlot` 调用。可行性与 init 钩子同级，但该进程是否加载 libc++ 需实测。

## 4. 已被证据排除/降级的路线

- **DirtyFrag 直接写块设备回写**：现有证据是页缓存修改重启即消失（`otacerts.zip` 替换重启恢复），
  说明页面并未可靠标脏；没有 `set_page_dirty` 的情况下 `blkdev_writepage` 不会落盘。该路线降级。
- **内核 LPE**：`CONFIG_NF_TABLES` 未开、`USER_NS` 未开，CVE-2024-1086 等主流 2024 LPE 不可达；
  GhostLock 5.4 无可用车辆。
- **EDL**：仍缺匹配的签名 firehose。
- **OEM Unlock 属性**：`ro.boot.journey.customer=1` 只影响开关显示，fastboot 无 unlock 命令。

## 5. 建议的第一轮离线准备工作

1. 从设备 dump `boot_a`（只读，低风险）。
2. 离线制作三件套：
   - `boot_a_magisk.img`（testkey 签名，hash footer）
   - `vbmeta_a_testkey.img`（保留原链描述符，仅替换 boot 描述符）
   - `payload_a_full.bin`（boot+vbmeta 全量 REPLACE，自建证书签名）
3. 本地 `avbtool verify_image` + `update_engine` payload 结构校验（不写设备）。
4. 设备侧先做一次“只写 vbmeta_a 的 testkey 版本、boot_a 保持 stock”的对照：
   如果 AVB 拒绝，说明链描述符/回滚索引有问题；如果通过，再写 boot_a。

## 6. 风险与回滚

- 写 A 槽失败：B 槽 stock 仍在，理论上仍可启动；但 ABL 可能因 A 标记 unbootable 而回退，需实测。
- 写 B 槽失败：没有 EDL 写通道，只能靠 A 槽 stock 回退；因此**路线 2 必须先确认 A 槽可启动**。
- 任何写入前保留：`boot_b_full.img`、`vbmeta_b`、`boot_a` 读回、GPT 主备副本。
- 不修改 `misc` 作为切槽手段（Qualcomm bootctrl 用 GPT 属性，不是 misc 字节）。
