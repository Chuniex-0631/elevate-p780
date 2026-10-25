# DirtyFrag 探针工具（P780）

本目录收录 2026-10-25 实机专题用到的全部离线工具与载荷源码，配套报告见
[`docs/research/p780-dirtyfrag-live-exploit-20261025.md`](../../docs/research/p780-dirtyfrag-live-exploit-20261025.md)。

## 文件

| 文件 | 作用 |
|---|---|
| `sendfile_probe.c` | APK 的 JNI 层。包含：文件 `sendfile` 回环、ESP 页缓存写入探针、系统库写入、按块写入、空桩自测、孤儿触发 |
| `stub.S` | 完整钩子桩：域判定（tid/uid/pid 或 comm）、一次性锁、标记、exec 尝试、PC 相对跳回 |
| `stub_noop.S` | 空桩：只执行被覆盖的 4 条原始指令再跳回，用于证明 trampoline 透明 |
| `build_patch.py` | 生成入口跳转、桩 blob、逐块写入计划。target 可选 `libcxx` / `libbase` / `libbase_noop` |
| `gen_patchdata.py` | 把计划生成为应用内 Java 常量（`PatchData.java`） |
| `scan_refs.py` | 牺牲函数零引用扫描：直接分支、`adrp/add`、`adrp/ldr`、`RELATIVE` 重定位、数据段裸地址 |
| `trace_calls.py` | 定位导入符号的调用点（`.rela.plt` → PLT → `BL` → 所属函数） |

## 使用顺序

```text
# 1. 离线：确认牺牲函数零引用
python scan_refs.py <lib.so> --candidates --min-size 700

# 2. 离线：生成补丁计划（决定 target 的 lib / entry / victim）
python build_patch.py libcxx

# 3. 生成应用常量并构建 APK
python gen_patchdata.py
python build_apk.py

# 4. 上机：patch → check → unpatch
adb shell am start -n <pkg>/.MainActivity -e probe patch
adb shell am start -n <pkg>/.MainActivity -e probe check
adb shell am start -n <pkg>/.MainActivity -e probe unpatch
```

## 需要自备的本地文件

`build_patch.py` 需要目标库的本地副本用于计算 IV 与原始字节，默认路径：

- `libcxx` → `../20/P780-libc++.so`（可用 `adb pull /system/lib64/libc++.so` 获取）
- `libbase` → `../22-netd-hook-20261025/libbase.so`（同上）

`.gnu_debugdata` 段的符号表解压方法见报告第 6 节。

## 边界

- 只写页缓存，不改磁盘、不刷写、不加载内核模块；重启即恢复。
- 每次改写前备份原始字节，回滚按同一机制写回并逐块校验。
- **检查标记务必用应用侧 `stat`**：`adb shell` 读 `/dev` 下这些文件会被 SELinux 拒绝，报错容易被误读为"文件不存在"。
