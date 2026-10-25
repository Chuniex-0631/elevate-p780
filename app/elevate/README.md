# Elevate：P780 临时 root 控制台

界面与交互层（2026-10-25）。一次触发后，在重启前可以反复以 `uid 0`
（`u:r:installd:s0`）执行命令。

## 现状

| 部分 | 状态 |
|---|---|
| 图标与名称 | 完成（深色圆角方块 + 青色箭头，单字名称 Elevate） |
| 单页界面 | 完成（状态药丸 / 获取按钮 / 命令输入 / 等宽输出台） |
| 守护进程协议 | 完成并上机验证（`docs/research/p780-root-daemon-20261025.md`） |
| 命令执行 | 完成（写 cmd + seq，轮询 out） |
| 触发安装（dummy APK） | **待实现** —— 目前触发仍靠 `cmd package compile` 或一次安装 |

## 界面

- 顶部：图标 + `Elevate` + 副标题 `P780 · temporary root console`
- 状态药丸：`未连接` / `已连接 · uid 0`（读 `/data/local/tmp/p780_state`）
- 主按钮：`获取 Root`（已连接时变 `重新获取`）
- 命令行：输入框 + `执行`
- 输出台：等宽字体、可选中、深色卡片

## 构建

```bash
python build_elevate.py
# 产物：Elevate.apk（约 46 KB）
```

流水线：`aapt2 compile --dir res` → `aapt2 link --java`（生成 R）→ `javac`
→ `d8` → NDK clang（native 探针）→ `zipalign` → `apksigner`。

## 下一步

1. 生成空 dummy APK（无 launcher、`hasCode=false`、≈10 KB），作为 asset 打进主 App；
2. `PackageInstaller` 安装 dummy 作为触发（一次系统确认）；
3. 安装回调后轮询 `p780_state`，自动切到「已连接」。
