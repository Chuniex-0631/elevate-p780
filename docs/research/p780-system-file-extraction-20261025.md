# 从 /system 提取整文件（2026-10-25）

> 目标：机主真正想要的是**系统镜像文件**，不是持久 root。本页记录在这条目标下
> 现实可行的边界与已验证的能力。

## 1. 原始分区镜像：不可行

| 域 | 能读块设备 | 能写 shell 可读的大空间 |
|---|---|---|
| `init` | 是（dm / metadata / swap，实测可读 boot） | 否（只能写 11 MB 的 `/metadata`） |
| `vold` | 是（dm / metadata / userdata） | 否（`shell_data_file` 只有 dir 级权限） |
| `installd` | **否** | 是（`/data/local/tmp`，95 GB 空闲） |

没有任何一个域同时具备"读块设备 + 写大空间"。用 init 域往外搬，`/metadata` 一次
只有 8 MiB 可用，3 GB 的分区需要 300+ 轮打补丁，不可行。

结论：**整盘 `system.img` / `super.img` 目前拿不到。**

## 2. 文件级提取：完全可行，已实机验证

`installd` 域同时拥有：

- `system_file: read`（读 `/system`）
- `shell_data_file: write`（写 `/data/local/tmp`）

因此用一段系统调用级的复制载荷即可把任意 `/system` 文件搬到 `/data/local/tmp`，
再 `adb pull` 取回，**不受 11 MB 限制**。

### 实测

源文件：`/system/framework/framework.jar`（30,153,054 字节）

```
/data/local/tmp/p780_syscopy.bin   30,153,054
md5  2c3b78f7ec6201240b71b42d219dd058  (device, copy)
md5  2c3b78f7ec6201240b71b42d219dd058  (device, original)
md5  2C3B78F7EC6201240B71B42D219DD058  (local, after adb pull)
```

**逐字节一致**，速度约 30 MB/s，一次触发完成。

### 复现

```bash
# 1) 构建并安装带复制载荷的 APK
python 21-dirtyfrag-probe-20261025/build_patch.py libcxx
python 21-dirtyfrag-probe-20261025/gen_patchdata.py
python 21-dirtyfrag-probe-20261025/build_apk.py
adb install -r app-debug.apk

# 2) 打补丁（载荷里的源路径写死为目标文件）
adb shell am start -n top.dcmqht.p780ipsec/.MainActivity -e probe patch

# 3) 触发 installd（不改变 APK 路径）
adb shell cmd package compile -m speed -f top.dcmqht.p780ipsec

# 4) 取回
adb pull /data/local/tmp/p780_syscopy.bin ./framework.jar

# 5) 回滚
adb shell am force-stop top.dcmqht.p780ipsec
adb shell am start -n top.dcmqht.p780ipsec/.MainActivity -e probe unpatch
```

## 3. 覆盖范围

- `/system` 下 installd 可读的一切文件（`framework.jar`、`services.jar`、
  `framework-res.apk`、系统 APK、native 库、`etc/` 配置等）；
- `/vendor`、`/product`、`/apex` 是否可读取决于 `installd` 对这些类型的权限，尚未逐项验证；
- 应用私有数据（`/data/data`）已在之前的取证能力覆盖内。

## 4. 尚未解决

1. **批量提取**：目前一次载荷搬一个文件。要整目录，需要：
   - 用 shell 的 glob 生成文件清单写到 `/data/local/tmp`，再让载荷读清单逐个复制；
   - 或把递归目录遍历（`getdents64`）写进载荷。
2. **原始镜像**：若确实需要可刷写的 `system.img`，现有域组合无法实现，
   只能依赖 EDL/Firehose（当前无 programmer）或厂商固件。
3. APK 内 `classes.dex`、`resources.arsc` 等已随 `framework.jar` 验证了二进制完整性，
   说明复制路径没有编码/换行损坏。

## 5. 边界与风险

- 载荷修改的是页缓存，**重启即恢复**；不需要持久化；
- 全程 SELinux 保持 Enforcing，未改策略、未写分区；
- 提取的是**已安装运行中的系统文件**，不是出厂镜像（OTA 后的状态）。
