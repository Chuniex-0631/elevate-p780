# P780 system/lib64 第二批静态分析（2026-10-18）

本次只在电脑读取上传文件，未在手机执行二进制、设置属性、连接诊断 socket、写分区或重启。设备仍无已证实的 Root/解锁能力，DSU 路线保持停止。

## 来源与完整性

- ZIP：P780-system-lib64-batch2.zip
- SHA-256：31aa1878b46a71fd960b7bdc5044e1a5421a2f8e6400bf919873e1efa62e5ce2
- ZIP CRC 检查通过；514 个文件、279493296 字节。
- 514 项大小及 SHA-256 全部匹配已归档机主 PC 清单，零不匹配。
- 509 个 ELF 成功读取动态节/动态符号；其余 5 个为 libclcore 系列 LLVM bitcode，不是解析失败。
- 分析目录曾有一个不属于 ZIP 的临时文件产生节表越界错误，已从样本范围排除；上传文件没有该错误。
- 这是两次采集材料的一致性核验，不是厂商签名、完整固件真实性或当前运行内核的核验。

## 交叉分析结果

|观察|能支持的判断|不能支持的判断|
|---|---|---|
|libbootloader_message.so 导出 write_misc_partition、write_bootloader_message、clear_bootloader_message、wipe package 等函数|已取得通用 bootloader message 工具库|不等于取得 Journey init 的 write_misc 命令实现；不证明 shell 能写 misc|
|write_misc 原始子串仅命中上述库的 C++ 符号 write_misc_partition|子串搜索命中已有具体解释|不能当作同名厂商 builtin，也没有建立 RC 到此函数的调用链|
|本批未命中 journey_diag_ext、sys.journey.diag、odm.journey.diag 字符串|本批没有这些明文定位点|不排除静态链接、剥离、编码或间接调用|
|sync_file 子串位于 libc、libsync、libui、libhwui 等通用库|该子串不具有厂商实现唯一性|不能直接认定 Journey sync_file 实现已取得|
|合并已解析的 batch1/batch2，未见 DT_NEEDED 引用 libbootloader_message.so，也未见动态导入其 bootloader_message/write_misc 符号|当前样本中未建立直接动态依赖链|不排除缺失可执行文件、dlopen/dlsym 或静态链接|
|libfs_mgr_binder.so 有 Bp/Bn GSI/Image 接口符号；libgsi.so 有状态/槽位辅助函数|可区分接口与辅助库|接口名称不证明已取得服务端授权逻辑或设备可启动 DSU；不恢复该路线|

两批已解析 ELF 共 890 个条目（batch1 的 381 含编译产物，不等于共享库数），DT_NEEDED 共 7477 条。按文件基本名匹配，有 11 个不同依赖名未在这两批 ELF 集合找到，包括 libnativehelper.so、libandroidicu.so、libstatssocket.so、libstatspull.so、libnativeloader.so 和部分 CNE 接口。此计算不模拟 linker namespace、APEX、搜索路径或 ABI；未匹配不能称为设备缺库，匹配也不能保证运行时可加载。

## 与权限证据的关系

此前 ODM 预编译策略允许 shell 设置 debug_prop，Journey sys 属性映射到该类型；这仍只是静态属性边界候选。缺少 init 自定义命令注册表、参数处理、路径限制、具体执行域及目标文件访问校验，不能从 RC 的 root 声明、属性 allow 或库中写函数拼接出“任意写入”或“提权成功”。

机主已实测 /init、/system/bin/init 和两个 Journey 诊断可执行文件的 ls -lZ 均 Permission denied。这不证明文件不存在，也不安排重复 pull 或权限绕过。

## 当前下一步

停止以泛搜字符串重复包装 Journey 线索。优先利用已有框架/JAR 与 native 样本建立“调用者 → Binder/HIDL 接口 → 已有策略许可 → 服务实现是否取得”的证据表，明确哪些只是客户端封装。优先补齐已有样本的调用关系；缺失服务端保持缺口，不试发诊断命令。已有工程 APK 排查不重复；GhostLock 等路线仍受本机构建与内核原件不足限制。

机器可读摘要见 [batch2 验证摘要](../../evidence/static/20261018-220912/batch2-verified-analysis.json)，完整文件哈希仍由同目录 manifest.csv 覆盖。结果只说明静态样本与依赖关系，没有新的实机能力结论。
