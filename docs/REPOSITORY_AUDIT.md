# 2026-10-18 全库总结与整理验收

基准提交：`cc92c49c397dd01e9aecc002a7ca60b63aea500a`。完整递归树未截断，整理前289个文件；[逐项树清单](../evidence/analysis/repository-inventory-20261018.json)记录路径、大小、模式和Git blob SHA。当前研究仍Locked/未Root，DSU停止。

## 审查范围

获取并检查87份Markdown、Python与工作流文件的结构、链接和相关研究内容；全树289项做元数据盘点。结合已上传批次，继续native依赖/符号、JAR定向字符串与编译策略交叉分析。本轮不是对全部历史二进制、所有网页或所有方法重新做安全审计。

## 整理结果

|问题|处理|
|---|---|
|首页/状态同时出现B已上机与B未安装|重写当前入口；以实机回退与停止路线为准|
|Attestation、fstab、策略核验仍列待测|从当前任务移除，专题补完成状态或历史说明|
|逐轮追加使证据索引变成实验流水账|按保存等级/资产类型重建索引，完整旧账本冻结归档|
|DSU占据导航主线|独立历史索引，旧专题保留路径并标记状态|
|维护APK已做过却继续列为新路线|修订收束报告的后续章节；改为已有样本交叉核对|
|库API/服务声明容易被当成可调用能力|新增native接口、权限与缺失服务端矩阵|
|10/11验收和监测描述被当现在|旧验收单独归档；当前任务运行状态须另查|
|邮件发送日期10/10与10/11不一致|标注待邮件头核对；本轮不伪称已重新查邮箱|
|静态证据新增不单独触发完整性检查|将evidence/static/**及CHANGELOG.md纳入既有push触发范围|

README负责摘要；STATUS负责当前结论；NEXT_STEPS负责尚未完成任务；专题负责具体证据；HISTORY/CHANGELOG负责时间顺序。今后不向各入口重复粘贴同一阶段通知。

## 原件保留与历史恢复

既有evidence原件、脚本和构建结果未删除或改写；同SHA的跨运行产物保留上下文。新增树清单是索引，不是重复存放二进制。旧逐轮证据账本和10/11验收复制归档时只调整相对链接和历史说明。

- [整理前完整状态](https://github.com/Chuniex-0631/p780-kernel-research/tree/cc92c49c397dd01e9aecc002a7ca60b63aea500a)
- [旧证据账本](archive/evidence-ledger-before-consolidation-20261018.md)
- [10/11结构验收](archive/repository-audit-20261011.md)

## 验证

提交前核对Markdown相对路径与完整目标树、Python语法、工作流YAML、新增JSON，以及当前入口不再包含过时的B待上机/Attestation待测指令。具体本地结果见[结构检查记录](../evidence/analysis/repository-review-20261018.json)。路径检查不覆盖标题锚点和外部网页可达性。

云端既有[完整性工作流](../.github/workflows/p780-final-audit.yml)会对实际提交重新检查全部Git文件、ZIP/配置/Tracefs、Journey原件与方法字节、历史迁移blob身份。实际结果以对应提交的GitHub Actions为准；本地只拉取文本，不能把本地结构检查称为全库二进制CRC重验。

本轮未操作手机、未发送邮件、未修改监测任务或仓库可见性，也未完成全历史隐私审查。原件仍有未入Git部分，见[资产清单](EVIDENCE_MANIFEST.md)。
