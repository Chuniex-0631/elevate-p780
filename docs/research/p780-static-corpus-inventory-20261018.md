# P780 实机静态样本第一批清单审核（2026-10-18）

## 研究方向
机主指出原厂工程/维护APK此前已排查且无线索，不能将重复APK检查冒充新路线。本阶段转为广覆盖静态样本建库、init—框架—native调用及版本交叉分析。DSU停止不变；无新Root/解锁/写入成果。

## 输入和边界
机主上传manifest(2).csv、pull.log、system-packages.txt、fingerprint.txt、services.txt。仅清单/日志已取得，1759个文件原件仍在机主Windows；摘要为用户PC计算，助手没有独立校验对应1.13GB文件。Fingerprint仍Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys。服务清单201项；注册服务不是可访问能力或漏洞证明。

[原始相对路径/长度/SHA256清单](../../evidence/static/20261018-220912/manifest.csv)。

## 数量
- 本地清单1759项，合计1131297358字节；1653种不同摘要（包含空文件摘要）。
- APK 177，JAR 121，SO 789，RC 194；另有ODEX/VDEX/ART/OAT等编译产物。
- system/lib64 514项，system_ext/lib64 280项；framework三处分别257/258/15项。注意system/framework的pull日志报告256项，本地清单257项，不能宣称全部条目均由此次成功传输得到。
- pull尝试281次：189次退出0，92次退出1。目录成功可能仍跳过文件，不能称为189个完整目录或1759个完整有效样本。
- vendor/bin及vendor/lib64均退出0但0 files pulled；没有取得这些native文件，不代表设备目录为空。
- system/bin读取在secilc处失败；后面的条目可能未被遍历。
- system_ext/bin跳过11项；system/lib64跳过bootstrap。
- 两个零字节项：system/bin/secilc（日志明确读取失败，按无效残留排除）；system/etc/init/journey.factory.rc（来源是否真为空待核实，不自动认定真实原文件为空）。
- /data/app中的更新版系统应用被采集脚本白名单跳过；当前清单不覆盖它们。overlay/vendor APK也有权限拒绝。ODM目标不存在不等于不存在ODM分区。

## 有价值的交叉分析样本
先取得全部已采集init配置和vendor/etc/fstab.default，建立service executable、user/group、socket、property触发关系；再与framework Binder声明及native库符号/依赖相连。不执行工程命令。
- init.journey_diag_ext_system.rc、init.journey_diag_ext_vendor.rc、journey.init.rc、journey.init.vendor.rc；
- vendor.journey.hardware.warehouse@1.0-service.rc、vendor.qti.hardware.factory@1.0-service.rc；
- libstfactory.so + stfactorydemo；libdiag_system*.so + libDiagService.so；
- libQSEEComAPI_system.so + vendor.qti.hardware.qseecom@1.0.so；
- framework相关JAR仅在确有调用关系时补取；factory命名可能只是普通接口工厂，不作为漏洞证据。
旧GhostLock/TEE/维护APK报告应先对照，已排除方向不重复安排实机测试。

## 下一步
1. 机主只打包电脑已有files/system/etc/init、system_ext/etc/init、product/etc/init、vendor/etc/init和fstab.default；不再从手机重采。
2. 如压缩包适合，再加入system_ext/bin、system_ext/lib64及system_ext/framework作为依赖样本（不能仅凭清单内容做二进制结论）。
3. 本机分析原件后才写入Build ID、DT_NEEDED、导出符号、权限边界等结果。权限缺口按路径记录，不改变SELinux、不提权、不读原始块设备。
4. 分阶段向GitHub提交脱敏清单和分析，小型配置在检查后入库，大体积原厂二进制不直接堆进Git。
