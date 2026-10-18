# P780 native接口、JAR与SELinux交叉核对

2026-10-18，纯PC静态分析；没有运行手机二进制、Binder/HIDL请求、socket连接、属性修改或分区操作。

## 结果

|样本链|直接观察|缺失证据与判断|
|---|---|---|
|libDiagService.so → libdiag_system.so → vendor.qti.diaghal@1.0.so|JNI导出 `Java_com_qti_diagservices_DiagJNIInterface_getNextCommand`；导入diagpkt_alloc/diagpkt_tbl_reg；diag库导入Idiag::getService并依赖HIDL接口库|动态符号与依赖支持JNI/诊断传输层关系，不是已完成的方法级调用图；未取得vendor诊断服务实现或Java调用方|
|libQSEEComAPI_system.so → vendor.qti.hardware.qseecom@1.0.so|导入IQSEECom::getService，依赖HIDL共享内存/allocator；RC声明qseecom-service以system UID运行|QSEECom_clear_key等导出是客户端API，不等于任意调用已授权；缺vendor服务逻辑及安全世界鉴权|
|libmink-sock-native-api.so → libminksocket_system.so|JNI导出nativeGetMinkOpener/nativeCheckFd与对象invoke方法；传输库导入connect/sendmsg/recvmsg|不能把此客户端库冒充TZAccessService的nativeGetEnvHandle服务端实现；原QAS许可链没有新增解锁证据|
|ssgtzd / qwes_ipc|RC声明system UID、0660 system:inet socket；ssgtzd标disabled但有early-boot显式start|disabled不能解释成永不启动；需要真实运行标签/凭据和服务实现才能判断可达性|
|Journey warehouse|RC声明system UID；ODM file_contexts有专用exec类型|只取得声明与标签，未取得服务二进制，不能按warehouse名称推定可读固件|

两份diag库都含HIDL路径及open/ioctl等导入；不能据此断言只走HIDL或已经追完所有路径。相同接口/导出集合不代表二进制相同。

## 编译策略交叉

对已上传ODM预编译策略，用SETools4.4.4逐项查询allow：

|来源域（每项均查询）|目标与权限|结果|
|shell、untrusted_app、untrusted_app_25、untrusted_app_27、untrusted_app_29、system_app|vendor_hal_diaghal_hwservice / vendor_hal_qseecom_hwservice：hwservice_manager find|均未见allow|
|同上|vendor_diag_device / tee_device：chr_file open|均未见allow|
|同上|vendor_ssgtzd：unix_stream_socket connectto；vendor_ssgtzd_socket：sock_file write|均未见allow|

共36项查询。正向对照可找到vendor_hal_diaghal_client/server的find规则、vendor_hal_qseecom_server的find规则，以及vendor_tzas_app、vendor_ssg_app、vendor_feature_enabler_client到vendor_ssgtzd的connectto规则，说明不是用空结果代替全部权限分析。

这里查询的是所选域，不包括全部特权应用域或高权限代理。system_app不等同于“所有system UID进程”。磁盘策略不是运行策略dump；未见allow不能排除其它入口，单条find/open允许也不能证明具体方法授权。

## JAR范围与可复核性

扫描batch1重建目录中的73个JAR、73个DEX字符串表，对DiagJNIInterface、nativeGetMinkOpener、nativeGetEnvHandle、warehouse、QSEECom、journey.diag、/dev/diag均未命中。范围不含所有APK/OAT及未上传框架，不据此宣称调用者不存在，也没有新增Java方法级反汇编结论。

[机器可读证据](../../evidence/static/20261018-220912/native-interface-crosscheck.json)保存6个库的大小/SHA-256/依赖及相关符号、完整36项策略查询和扫描范围。输入完整性沿用[batch1验证](p780-static-batch1-analysis-20261018.md)与[策略原件核验](p780-policy-boundary-audit-20261018.md)。

本阶段增加的是客户端/服务端/权限的分界证据，没有建立任意读取、写入、Root、BL解锁或DSU可启动的能力链。下一步只在已有材料能补齐具体实现时深入；缺失端点保留为缺口。
