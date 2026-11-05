# init 域 dump 与 boot_a 结果（2026-11-05）

对象：Rakuten Hand 5G / TINNO P780（holi，Android 11，5.4.233）。本轮在实机上重新打通 init 域读块设备，并完成 boot_a / vbmeta_a / update_engine 的导出。

## 1. 方法（可复跑）

1. 从 `release/Elevate-1.0.apk` 取出 `STUB_HEX`（1632 个十六进制字符 = 816 字节，位于 `classes.dex` 的字符串常量）。
2. 用 keystone 汇编 `tools/partitions/init_dump_stub.S`：
   - 修正 `.inst` 不被 keystone 支持 → 改 `.word`；
   - sentry 前 16 字节按**内存字节序**写入（`fd 7b be a9 …`），不是按 word；
   - 返回 trampoline 的 `adrp/add` 必须按 blob 基址 `0x790b0` 计算；
   - blob 补 NOP 到 816 字节。
3. 把新 blob 的 hex 原地替换进 APK 的 `classes.dex`，重算 dex 的 SHA-1 与 Adler32。
4. 用 `uber-apk-signer`（v1/v2/v3）重签，卸载旧包后安装（避免 uid/data 目录错位导致 EACCES）。
5. `am start -n top.dcmqht.p780ipsec/.MainActivity -e probe patch`，orphan reap 触发 init 主线程执行 stub。
6. 每次最多写 `/metadata/cur.bin`（8 MiB），`adb pull` 后重新 patch 下一块；`/metadata` 仅 11 MiB，不能一次放整个分区。

## 2. 校验结果

| 对象 | 结果 |
| --- | --- |
| `vendor_boot_b` 前 8 MiB | 与仓库 `vendor_boot_b.00.bin` SHA-256 完全一致（`226b58c3…e384`） |
| `boot_b` 偏移 8 MiB 的 8 MiB | 与 `boot_b_full.img[8M:16M]` SHA-256 完全一致（`4391099a…6567`） |
| `vbmeta_a` 64 KiB | 合法 AVB0 头；与仓库 2026-10-26 快照有 572 字节差异（设备当前状态已被历史实验改过） |
| `boot_a` 96 MiB | **前 4096 字节为 0xAA，之后全 0x00**；A 槽 boot 已被清空/覆盖 |

## 3. 结论

- init 域读块设备能力**重新打通且逐字节可验证**。
- `boot_a` 没有可恢复的 stock boot：A 槽 boot 被 0xAA 探针清空。
- 因此“补全 A 槽再让 update_engine 切槽”的路线缺少 A 槽内核；A 槽 vendor_boot/system 是另一构建（263），不能直接用 B 槽内核拼。
- 永久 Root 的主路线应改为：**让 update_engine 写当前 B 槽**（`boot_b` + `vbmeta_b` 都是 264 构建、已在仓库），再解决 OTA 签名与 target slot。

## 4. update_engine 二进制

已从设备导出：

```
evidence/20261105/update_engine.bin  1,109,200 B
ELF aarch64 ET_DYN（PIE），已 strip，只有 .dynsym
```

已定位字符串与代码引用（RVA）：

| 字符串 | 地址 | 代码引用 |
| --- | --- | --- |
| `Verifying using certificates: ` | 0x10d0e | 0x83a98 |
| `Unable to call SetActiveBootSlot for slot ` | 0x1a425 | 0x6fc5c |
| `, target_slot: ` | 0x16478 | 0x95c80 |

下一步（反编译重点）：

1. 以 0x83a98 为锚点向前找函数边界，确认 `PayloadVerifier::VerifySignature` 入口，评估 `mov w0,#1; ret` 补丁；
2. 定位 `UpdateAttempterAndroid::GetTargetSlot()`（`GetCurrentSlot()==0?1:0`），或 `GetCurrentSlot()`，把 target 固定为 B；
3. 两条补丁都通过页缓存写入 `/system/bin/update_engine`（app 侧 `writeBlock` 或重建 Elevate 的 `PatchData`），再触发 `update_engine_client`，payload 写 `boot_b` + `vbmeta_b`；
4. `vbmeta_b`/`boot_b` 用公开 `testkey_rsa4096` 重签，rollback index 提高；B 槽本来就是 active，不需要切槽。

## 5. 产物

```
evidence/20261105/boot_a.img                 100,663,296 B  all-zero after 4K 0xAA
evidence/20261105/vbmeta_a.dump.bin              65,536 B  AVB0, current device state
evidence/20261105/boot_b.offset8M.bin         8,388,608 B  validated offset slice
evidence/20261105/update_engine.bin           1,109,200 B
evidence/20261105/stub_init_vendor_boot_b.bin         816 B
evidence/20261105/stub_update_engine_dump.bin         816 B
```
