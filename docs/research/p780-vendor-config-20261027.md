# /vendor 配置解析：块写域、SELinux 与 VINTF（2026-10-27）

> 数据来源：`evidence/20261027/vendor-config/`（62+117 个文件，全部由 shell 只读拉取）。
> 本文只做离线解析；行号对应当前入仓文件。

> 2026-10-28 启动链复核：本机 RC 同时声明 Boot HAL 1.0/1.1；未见成功日志不能判切槽 no-op。GPT 属性是优先存储后端候选，尚未完成本机二进制/样本核验。见 [新复核](p780-boot-chain-review-20261028.md)。

## 1. 历史结论与后续更正

1. **没有任何"可直接触达"的 boot 块写域**。能写 `boot_block_device` 的只有
   `update_engine_common` 和 `hal_bootctl`，前者受 OTA 签名门控，后者只暴露 slot 管理 API。
2. `vendor_install_recovery` 本来可以"读 boot、写 recovery"，但它的服务
   `vendor_flash_recovery` 指向的 `/vendor/bin/install-recovery.sh` **不存在**，
   服务也没有运行（`getprop init.svc.vendor_flash_recovery` 为空），该域**不可达**。
3. **没有域被允许 `setenforce`**；`init` 只有 selinuxfs 的 `file write` 和
   `security compute_av/compute_create`，不足以改 enforce。permissive 仍只能靠内核写。
4. 模块加载（`module_load`）只给 `vendor_modprobe`、`vendor_init`、`ueventd`，
   shell/system_app/installd 都不在其中。

## 2. 块写域矩阵（vendor_sepolicy.cil / plat_pub_versioned.cil）

| 域 | 可写块设备 | 关键限制 |
|---|---|---|
| `update_engine_common` | boot、system、misc、super、xbl、uefi、modem、ssd、recovery、vendor_custom_ab（L5544–L5549、L9893–L9921） | 静态类型权限；后续已有 metadata 验签通过及 boot_a 有限写入摘录，非任意块写 |
| `hal_bootctl` | misc、root、boot、gpt、xbl（L3604–L3623） | 只有 boot_control HAL 的 slot 接口（setActiveBootSlot / markBootSuccessful 等），没有"写任意镜像"的方法 |
| `vold` | userdata、metadata、misc（L10317、L10460、L10485） | 不碰 boot；misc 只用于 boot 命令 |
| `init` | misc（write）、metadata、swap；以及块设备 relabel（L7642–L7909） | 不能写 boot；relabel 不等于写数据 |
| `vendor_init` | misc（write）（L10025） | 同上 |
| `uncrypt` | misc、userdata（L9821–L9823） | 只在 recovery 流程里跑 |
| `vendor_misc_writer` | misc（L10252） | 只能写 misc |
| `vendor_install_recovery` | **recovery 写**、boot 只读（L2996–L2999） | **域不可达**：`vendor_flash_recovery` 的脚本缺失，`init.svc` 为空 |
| `fsck` / `e2fs` / `tee` / `thermal` / `qti_init_shell` | persist/qmcs/ssd/limits/swap 等 | 与 boot 无关 |

### 2.1 `vendor_install_recovery` 为什么是死路

- `init/vendor_flash_recovery.rc`：

  ```
  service vendor_flash_recovery /vendor/bin/install-recovery.sh
      class main
      oneshot
  ```

- 真机上 `/vendor/bin/install-recovery.sh` **不存在**（`ls` 报 No such file）；
- `getprop init.svc.vendor_flash_recovery` 为空，说明服务未启动/已失败；
- `vendor_file_contexts` 里也没有该脚本的标签（只有 `vendor_modprobe.sh` 的
  `vendor_modinstall-sh_exec`），所以 `vendor_install_recovery` 域没有 entrypoint。

结论：这条"写 recovery"的潜在路径在 P780 上是**残留配置**，不可用。

## 3. SELinux：enforce 与模块加载

- `setenforce` 只出现在 neverallow（`plat_pub_versioned.cil` L5338），
  以及 `kernel_30_0 self (security (setcheckreqprot))`（L8275）；
- `init` 对 selinuxfs 有 `file (write)`（L7877），但 `security` 类只有
  `compute_av` / `compute_create`（L7878–L7880），**没有 `setenforce`**；
- `shell` 对 selinuxfs 只有读（L9574–L9575）；
- 因此"写 `/sys/fs/selinux/enforce`"仍会被 SELinux 拒绝，和之前实测一致。

模块加载：

```
(allow vendor_modprobe vendor_file_30_0 (system (module_load)))   L3016
(allow vendor_init_30_0 vendor_file_30_0 (system (module_load)))  L5610/L5624
(allow ueventd_30_0 vendor_file_30_0 (system (module_load)))      plat L9792
```

没有 shell / system_app / installd 的 `module_load`。

## 4. VINTF 与 fstab

- `vintf/manifest.xml` 是 vendor 主 manifest；`vintf/manifest/` 有 32 个 fragment，
  其中 `android.hardware.boot@1.1.xml` 存在（boot HAL 1.1）；
- `hal_bootctl_client` 只有 `update_engine`、`update_verifier`、`vold`
  （`vendor_sepolicy.cil` L223）——普通应用/system_app 不是 boot HAL 客户端；
- `fstab.default`：`system`/`system_ext`/`product`/`vendor` 都在 `super` 逻辑分区，
  带 `avb=vbmeta_system` / `avb`；`metadata`、`persist`、`userdata`、`misc` 独立；
- `vendor_file_contexts` 给 `recovery`/`recovery_[ab]` 打了
  `recovery_block_device` 标签（L445/L489），说明 **recovery 分区真实存在**；
  但只有 update_engine（签名门控）和不可达的 vendor_install_recovery 能写它。

## 5. `/vendor/build.prop` 为什么读不到

`vendor_file_contexts` 没有 `build.prop` 条目；它由平台策略标成
`vendor_configs_file`（或等价受限类型），shell 没有读权限，所以 `ls` 就 Permission denied。
这不是文件缺失，而是 SELinux 标签限制；permissive 或 init 桩可解。

## 6. 对刷机路线的影响

- 旧建议的内核 permissive 路线已暂停，不能称唯一现实路径；运行时权限扩大、目标分区写入、镜像启动与跨重启保持须分别验证；
- update_engine 已有后续有限写入记录；Boot HAL 的实际调用与 GPT 存储后端仍待复核，不能以旧签名门结论关闭整条路线；
- recovery 写路径是死配置，不能作为绕行；
- 商业 EDL（有签名 loader）是另一条独立路径，但截至该轮未获可验证匹配 programmer。

## 7. 保留的负结论

- 不要再去尝试 `vendor_install_recovery`：脚本不存在，域无法进入；
- 不要再尝试从 shell/system_app 写 selinuxfs 或加载模块：策略里没有 allow；
- 不要指望 `/vendor/build.prop` 通过 shell 读取：只能 permissive/init 桩。

## 8. 证据

- 目录：`evidence/20261027/vendor-config/`（62 个首批 + 117 个 `init/` rc）；
- 索引与哈希：`docs/EVIDENCE_MANIFEST.md`（由 `tools/build_research_index.py` 重建）；
- 关联：[信息层清单](p780-info-layer-20261027.md)、[6931 报告](p780-uring-cve-2023-6931-20261025.md)。
