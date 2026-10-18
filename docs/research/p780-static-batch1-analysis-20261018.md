# P780 静态样本 batch1 原件验证与交叉分析（2026-10-18）

## 结果
收到P780-static-analysis-batch1.zip，CRC全包通过，SHA256 340765c47e7a9bc8d96b6eb368902117ce631d84a3d34ca0ae1d0eff2e92ca3b。743个ZIP条目中742个文件条目，逐一按ZipInfo读取，长度及SHA256全部匹配用户第一批manifest；0不匹配。此为原件对用户PC清单的独立重算，不是独立OEM来源认证。

压缩命令丢失父目录，将system/system_ext/product/vendor的init合并成init目录；init\\hw\\init.stnfc.rc出现两次同名条目。本轮通过每条目字节哈希对清单恢复可能来源，没有按重名路径直接覆盖。字节完全相同的多来源仅说明字节身份，不强行唯一化来源。无需重新上传。

[逐文件来源、哈希、ELF依赖和init服务索引](../../evidence/static/20261018-220912/batch1-verified-analysis.json)。

## 静态覆盖
- 还原来源中194份RC，解析285个service声明，230种不同可执行路径，其中54个声明显式user root。
- 这些是静态文本声明，可能含条件配置、disabled/oneshot、重复或未加载定义，不能当作285个运行服务或54个可调用Root入口。
- system_ext中识别381个ELF文件（包含ODEX/OAT等，不等于381个服务或SO）。已提取Build ID、DT_NEEDED及动态符号数量，未执行二进制。
- 0字节journey.factory.rc仍不用于功能结论。

## 排除名称误导：ST factory链
stfactorydemo -> libstfactory.so -> libstnfc-nci.so。
libstfactory导出ST_AntennaSelfTest、ST_eSE_CE_Test、ST_CLF_getInfo、ST_HCE_CE_Test、ST_RW_Test、ST_SwpTest、ST_TestMode_open/close、ST_eSE_getCPLC等。说明功能集中NFC/安全元件工厂测试，不是已发现的整机刷写工具。
Build ID: stfactorydemo c96979d3dab7babb48e14bab1c2c95d3；libstfactory.so 68e30d8d5e1c92ed8a85a944ae6e2e50。
不因factory字样运行它，不对eSE作测试。

## 新取得原件支持的权限边界候选
### Journey init诊断链
system/etc/init/init.journey_diag_ext_system.rc声明：
- journey_diag_ext_system，/system/bin/journey_diag_ext_system，user root，disabled；
- diag_ext_socket为seqpacket，DAC模式0666，属主system/system；
- persist.vendor.diag.journey.enabled=1/0控制启动/停止；
- sys.journey.restorecon属性触发restorecon_recursive；
- sys.journey.diag.write_misc属性触发厂商write_misc动作。

vendor对应RC也声明root诊断服务；含odm.journey.diag.factory.reset触发write_misc --wipe_data与reboot,recovery。

system/etc/init/journey.init.rc另含config.write.zero/one的路径属性展开写0/1，以及persist.config.write.zero/one的转发。并有厂商sync_file动作。

**仅确认配置字节和触发语法，不确认服务运行、socket连接权限、属性设置权限或write_misc/sync_file实现。** DAC 0666不绕过SELinux；属性名存在不等于shell可写；root init能执行动作不等于调用者能触发。禁止以设置上述属性作为探测，因为其中包含擦除/重启和持久修改。
与此前已审查的JourneyConfigService/TCS网络策略链区分：这些init/native动作不自动构成TCS到Root的调用链；没有重新宣称旧配置下载审计为新Root入口。

下一证据关卡是实际plat/vendor/system_ext/product property_contexts、对应SELinux规则、服务端二进制及调用者。先确定权限映射，不能凭字符串下利用结论。

### Qualcomm JNI和TEE代理依赖
- libDiagService.so依赖libdiag_system.so，导出Java_com_qti_diagservices_DiagJNIInterface_getNextCommand、JNI_OnLoad、android_diag_handler；静态字符串对应com/qti/diagservices/DiagJNIInterface和DiagCommand，提供可追踪JNI连接点。
- libQSEEComAPI_system.so依赖vendor.qti.hardware.qseecom@1.0.so及HIDL共享内存库；QSEEComHal::initService等符号支持其为经HIDL访问vendor服务的封装，而不是当前已取得的vendor服务实现。
- QSEECom create/wipe key等API符号不代表shell有权限、不代表任意TA可加载；不调用这些敏感API做探测。
- warehouse RC指向/vendor/bin/hw/vendor.journey.hardware.warehouse@1.0-service，system UID。该服务端原件不在本包，不能靠代理或RC判定鉴权漏洞。

## 下一步
1. 优先补充实际SELinux静态目录，确定候选属性映射和规则；不执行setprop、ctl.start、socket请求、工厂测试或任何分区写入。
2. 基于权限证据筛选需要的服务端实现；既有Permission denied缺口保留，不反复批量pull。
3. 系统数据读取/镜像提取路径仅在具备明确调用者可达性、鉴权和实现证据后才进入实机验证。
4. DSU路线维持停止；仍Locked，无Root/解锁或永久写权限成果。

## 复核方法
Python zipfile.testzip；每条目SHA256+长度查表；按清单的相对路径恢复分析副本。pyelftools提取动态段、符号表、GNU Build ID；init脚本按service段分组，只做静态声明统计。ELF解释不涵盖所有指令控制流或HIDL服务鉴权。大体积原始二进制仍仅在机主/本会话保存，GitHub保存证据索引及报告。
