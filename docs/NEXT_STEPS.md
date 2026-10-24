> 2026-10-25 实测更新：perf v0.1.0 已实机 USER_COUNT_PASS，不再重复用户态计数。下一可设计项仅为自身线程包含内核时间的纯计数权限核验；本轮未制作/执行。地址、调用链和寄存器采样仍未测试。 [报告](research/p780-perf-v010-live-result-20261025.md)

## 2026-10-24 下一步（审计更新）

1. 不重复 v0.2 普通 UDP/ESP 回环或 v0.3 普通 sendfile 回环；两者已实机 PASS。
2. TINNO 5.4.61 候选源码显示旧式 IPv4 UDP sendpage 与 ESP no-COW 相关静态形态，详见 [审计报告](research/p780-dirtyfrag-tinno-5.4.61-source-audit-20261024.md)。
3. 下一项优先任务是取得或核验 P780 `_162` 对应的 5.4.233 kernel Image / vmlinux / 厂商源码，确认上述函数实现与等价安全修复是否存在；不将候选源码结论直接当成本机事实。
4. 在 running kernel 身份和共享页 ESP 路径得到可信证据前，不运行 DirtyFrag/DFRoot payload，不做页面缓存写入，不加载内核模块、不刷写 Boot/AVB/EDL。


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

