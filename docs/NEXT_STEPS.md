## 2026-10-24 下一步（最新计划）

1. v0.2 已完成；不要重复运行普通 UDP/ESP loopback。
2. v0.3.0 APK 已由 CI 成功构建，加入纯 UDP file-backed sendfile 回环检查；目前**未安装、未在 P780 上运行**。
3. 下一步先由机主确认是否安装并单独运行 v0.3 第 4 项。若同意，使用应用私有 1 KiB 临时文件和 127.0.0.1；不启用 IPsec，不构造 ESP，不修改系统文件，不尝试利用式页面缓存操作或 Root。
4. 无论 PASS/FAIL，都只记录 sendfile-to-UDP 路径结果，不将其升级为 DirtyFrag 漏洞结论。仍缺 running kernel 的可信源码身份和共享页 ESP 解密原语证据；不运行通用 DirtyFrag/DFRoot payload。

详见 [v0.3 sendfile 预检报告](research/p780-dirtyfrag-v03-sendfile-probe-20261024.md)。


> 2026-10-20 GAP-01：header 原件核验已完成，正文方向已纠正；独立 SETools 语义复核仍 BLOCKED_TOOLING（当前无可用 WSL/SETools）。只在工具环境就绪后比较既有原件，不重复采集或归一化输入冒充通过。 [详情](research/p780-policy-header-verification-20261020.md)

# ��һ���о��ƻ�

���£�2026-10-19��ֻ������ǰ������ʵ�������� [STATUS](STATUS.md)��DSUֹͣ��Root/BL����δ��ɡ�2026-10-19 �Ѱ�������Ҫ������������ EDL ������ʵ�飻ʵ������׶�����Ϊ��С������

|���ȼ�|����|���������뽻����|��ɻ�ֹͣ����|
|---|---|---|---|
|����ɽ׶�|OEMLOCK-01�Ѷ�λ��OEMLOCK-02����������δ�ҵ�·��|296��ȥ��APK/JAR��6��ֱ�ӵ��õ㣬ΨһӦ�ò�true����Settings�ڲ�ȷ����������Ȩ��Ϊsignature/privileged����[OEMLOCK-02�����߽߱�](research/p780-oemlock-caller-boundary-20261019.md)|ֹͣ�ظ�ɨ�����ϻ����ԡ�ֻ���������/�����ԭ���ɲ�����ȷ��������ؿ�����ִ��setter�������������ԡ���дFRP��|
|����ɽ׶�|NATIVE-01���ж˵������Java/JNI����|�����Ѻ˶����Ӧ��16������JNI��ʵCFIʵ�֡�����ʧ����־������UIDȨ�޼����б�ǩ����[����](research/p780-native-live-endpoints-20261019.md)|���ٰѸ�APK��Ϊ����OEM������û�е���������ڣ�����ʱHIDL����ʧ�ܡ���Ҫ������������ط������Դ���|
|����ɽ׶�|GAP-01����policy/config/���ļ���ʵ|����policy�ѵ������޶�v30��¼�Ƚ���ODM����/��������ͬ��config.gz�������һ�£�journey.factory.rcȷΪ�ա���[GAP-01](research/p780-evidence-gap-audit-20261019.md)|�ں�notes/kheaders/kallsyms������sysctl�Ѳ���Ϊ�ܾ������ظ���Ϊ��ִ�У�perf=-1����Ϊ��������|
|�������ߺ���|��PC����policy������SETools����Ƚϲ�����header config����|ԭ��λ�ڻ���PC 12-evidence-gaps/running-policy.bin ���ODM precompiled����ǰWindowsδ���ÿ���WSL���������о����԰�װ|�޶���¼�Ƚ��Ѿ���ɣ�����ʵ�ֿ��ú󸴺ˣ����ظ������ֻ�������������36�����|
|1��������ѡ��|NATIVE-02 Journey root��Ϸ��� / init builtinʵ��|����root������ȷ��running������ȡ��ͬ��������init/��Ϸ����ԭ�����ӦԴ��󣬺˶�debug_prop����������Լ�������������|ʵ��ȡ�÷�֧BLOCKED�����м�����vendor��ȡPermission denied���ظ����ԣ����������ԡ�����socket������running��Ϊ����д����|
|2|�˶���δȡ��ԭ���ļ�ֵ|�Ⱥ˶�PC�����嵥�����ϴ���Χ��ֻ����ȷ�ܲ�����������ʱ������С��������|���ظ�Ҫ���ѱ�Permission denied�ܾ���init/Journey/gsid�ļ�������δȡ��������Ϊ������|
|3|����ͬ�ͺŹ̼���Դ����֤��|��ԭ���������ͺš���������Դ����ϣ��Դ��ظ����Ӧ `_162` ��5.4.233˵��|����֤��Դ�����߼��boot/vbmeta/�ںˣ�����A52s���TINNO���������|
|EDL�ܿ�ʵ��|QDL v2.8 ���� QUD/COM6 �ɹ����� Sahara v2 ������Ϣ����ѡ A ��ʵ������4�� READ64������ȡ��һ�� Sahara ��ʧ�ܣ�δȡ�� END OF IMAGE��DONE �� Firehose��������ȷ�ϻָ� Android��������غ�ѡ������֤���Ų���ɡ������ PKHash ����ƥ�䣬��ͣʵ���Դ����������ҿ���ͬ�ͺ�ԭ��ǩ�� programmer����[ʵ����ʵ��߽�](research/p780-qdl-qud-sahara-20261019.md)|�� EARLY_SAHARA_READ64_FAILURE / CAUSE_UNDETERMINED ��ǲ�ֹͣ�޲������ԣ����������ֳɹ��ƶ� Root/����/дȨ�ޡ�|
|������֧|GhostLock�ָ��о�|ȡ�������ں��޲�״̬�����Ŷ�����/����/���Ͳ��֣��ܺ��鱾����������|��ǰBLOCKED�������п����payload�����ú�ѡ���ֹ���ƫ��|

## �ѽ������ݻ������ظ���Ϊ����

- Attestation��Կ���ݡ�fstab��ȡ��Google OTAָͬ�Ʋ�ѯ��A/B������ǩ��B�ϻ����˺�SELinux����ժҪ�˶Ծ��������Ӧ�׶Ρ�
- DSU������������ֹͣ��װ��Restart����ǩ���Ͳ����Դ���������[������֤��](research/p780-dsu-closure-maintenance-route-20261018.md)�����˸���δ֪��
- ����APK/�˵���Journey����������Ӧ�ñ�������������飬����֤�ݲ��ؿ�ͬһ·�ߡ�
- ���������getprop����OTAָ�ƻ��޼�¼�����Firehose�����߷������ʼ�����������ϵRakuten��
- ��ǰ��ѡshell/��ͨӦ����δ��diag/QSEE����Ȩ�޼�Ŀ���豸�ڵ�/ssgtzdȨ�ޣ��ȱ���Ȩ�޾��󣬲�����ֱ�ӷ�������

## �ƽ���׼

�½��۱�������������ݡ�ֱ�ӹ۲졢�����ƶϡ���֤��ȱ�ڡ�ֻ���õ�����ʵ�ֺ�Ȩ��֤�ݣ��������һ�׶���С��֤���ֽ׶β����ù������ԡ��������socket�����дmisc/boot/vbmeta������ EDL ���Կ����漰����������ȷ�豸���ա�

ÿ��ʵ�ʽ׶�ͬ��ר�⡢STATUS��EVIDENCE_MANIFEST��CHANGELOG��READMEֻ����ժҪ���Զ����/�ʼ�����״̬�뵥���˶ԣ��ֿ����ֲ��������״̬���ɼƻ���[��ʷ�ƻ�](archive/next-steps-before-dsu-20261018.md)��[DSU��ʷ����](archive/dsu-index-20261018.md)��

