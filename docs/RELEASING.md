# 版本发布

仓库版本与 APK 版本分别管理：`v1.1.0` 表示本库目录、文档和维护流程版本；`release/Elevate-1.0.apk` 的应用版本仍为 1.0。

## 发布门槛

1. 更新 `docs/releases/<版本>.md`、CHANGELOG 与 VERSION。
2. 新增内容纳入 Git，重建索引并通过完整性校验、维护测试、启动链离线测试和结构测试。
3. PR 的 Windows / Linux × Python 3.11 / 3.13 维护检查全部通过后合入 main。
4. 给已合并提交建立 `v*` 标签并推送。`repository-release.yml` 将再次验证四组环境，通过后打包并发布 GitHub Release，标记为最新版本。

## 发布内容

- `elevate-p780-<标签>.zip`：使用 `git archive` 从标签提交生成，包含完整已跟踪仓库内容，不包含本地报告、凭据、构建缓存或未跟踪文件。
- `Elevate-1.0.apk`：保留仓库已有 APK 字节，不改名为新应用版本。
- `repository.json`：离线校验报告。
- `SHA256SUMS`：以上三个产物的 SHA-256。下载后可用 `sha256sum -c SHA256SUMS`（Linux），或 PowerShell `Get-FileHash <文件> -Algorithm SHA256` 逐项核对。

GitHub 还会提供自动生成的 Source code 归档。发布不修改证据，不执行设备探针，不重签 APK。

## 恢复失败的发布

工作流仅创建不存在的新 Release，不覆盖既有发布。若同名标签已发布，先核对失败步骤和产物，避免移动已公开标签或无意覆盖历史文件。失败发生在 Release 创建前时，可从 Actions 重跑该次工作流。
