> 2026-10-20 GAP-01 补证：两份原件哈希核对通过；running config=0x1，disk=0x80000001，纠正旧专题两端写反。独立 SETools 语义复核 BLOCKED_TOOLING；有限记录一致不升级为完全等价。 [详情](research/p780-policy-header-verification-20261020.md)

# ��ǰ�о�״̬

���£�2026-10-19��Asia/Shanghai�������ǵ�ǰ���۵�ͳһ��ڣ�����ϸ�ڼ� [ʱ����](HISTORY.md) ��ר�⡣**Locked / δ Root / δȡ������֤�����÷���д��������DSU ��ֹͣ��**

## �豸��汾����

|�ֶ�|�Ѽ�¼ֵ|�߽�|
|---|---|---|
|�豸|Rakuten Hand 5G / TINNO P780��Qualcomm holi / mannar|����������ƽ̨|
|�̼�|Android 11��`P780AE_11.0_RMN_JP_162` / `_162_CFC`|�ڲ������� fingerprint ��Ų�ͬ|
|Fingerprint|`Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`|������ 162 �滻���� 264|
|�ں�|`5.4.233-qgki-gea5245e94afe-dirty`��Android Clang 11.0.2 r383902b1|��ѡԴ�벻�ǳ���������|
|����״̬|`flash.locked=1`��verified boot `green`����ʷ��� `_b`|ÿ�βɼ��Ŀ��գ�����֤�Ժ󲻱�|

��Դ��[�豸](research/device-and-boot.md)��[AVB ����](research/avb-live-baseline-20261018.md)��[���˺�״̬](research/p780-dsu-closure-maintenance-route-20261018.md)���ָ�������İ�״̬����������ǰ������ա�

## ·������

|·��|��֤ʵ�������|ʣ��ȱ�� / ����|
|---|---|---|
|AVB ��Կ����|����Ӳ��֤��֤��ǩ������ Google ��ƥ�䣻`verifiedBootKey` ƥ�� AOSP AVB RSA4096 Ĭ�ϲ��Թ�Կ��`verifiedBootHash` ƥ�䱾�� digest|���ߵ�������У��δ��ɣ���ʵ VBMeta chain descriptors��rollback index ��ԭ��������ȱ����[ȷ�ϱ���](research/avb-attestation-confirmed-20261018.md)|
|Fstab / ��̬����|���� fstab �Ѷ���system/system_ext/product ʹ�� `avb=vbmeta_system`��vendor/odm Ĭ�� avb��system �� q/r/s-GSI key ·��|���ò��������ʵ�������� first-stage ʵ�ʹ�Կ����[fstab](research/p780-fstab-avb-20261018.md)|
|DSU A/B|Windows A/B ��ͨ�� AVB ��֤��B ����ԭ����װ����װ������ dynsystem ���������ջص�ԭ����installed/disabled|**ֹͣ**��δ���� GSI��ʧ�ܽ׶�δ֪���ָ�������ԭ�� Loader �����ǻ����۲죬��������δ��ʵ����[����](research/p780-dsu-closure-maintenance-route-20261018.md)|
|OEM Unlock ��ɫ����|ԭ�����߶�λ����� carrier getter ����Ҫ�� !JourneyDebugFeature.IS_CUSTOMER_VERSION��framework��ʼ����ȡ ro.boot.journey.customer��������ʷͬfingerprint����Ϊ1������ADB�ٴζ���customer=1������PDB/���û������Ի�ɫ|��̬�����Ѷ�λ��2026-10-19����pull��services.jar SHAƥ����ʷ��δ���˵�ǰ�ڴ档OEMLOCK-02��ɨ��296��APK/JAR����6��ֱ�ӵ��õ㣻ȷ������signature/privilegedȨ���Ѻ��飬��������δ�ҵ��ɴ�д����ڡ���[OEMLOCK-02�����߽߱�](research/p780-oemlock-caller-boundary-20261019.md)��[Journey gate](research/p780-oemlock-journey-gate-20261019.md)|
|native���ж˵� / ���JNI|QTIDiagServices��libDiagService��services�����ֻ�ԭ��SHAƥ����ʷ������16��DEX�������JNI CFIʵ�֣�������־��λDiag_LSM_Init����HIDLʧ�ܣ�����Journey root��Ϸ�����������|���APK�����������û��OEM������HIDLʧ������ԭ��δ����vendor����˶�ȡ���ܾ���Journey init builtinʵ����ȱ����[���н��汨��](research/p780-native-live-endpoints-20261019.md)|
|Fastboot / EDL|���� unlock ���� unknown command��2026-10-19 QDL v2.8 ʹ�� Windows QUD/COM6 ���� Sahara v2/HWID/PKHash��������ʵ���Ǻ�|����֤ Sahara command-mode��**A ���������� READ64��B�CE �����߷�����A�CE ��3��ǩ�������뱾�� PKHash ������δ�ɹ����� Firehose**��δȡ�ÿ���ǩ�� Loader ��ԭ�� boot/vbmeta����[ʵ�ⱨ��](research/p780-qdl-qud-sahara-20261019.md)|
|OTA|6 ����ʷ������־û�� payload����ȷ fingerprint �� Google OTA Prober ��ѯδ���� URL|**�ݻ��ظ�̽��**����֤�����г����������ް�����[OTA ���](research/ota-log-audit.md)��[��ѯ](research/google-ota-prober-p780-20261018.md)|
|Դ�����ں˹���|��ʵ config.gz 5238 ����ȷ�����ƥ�� Clang11 ���� rtmutex.o��A52s ��ѡ����ֵ�仯0����ʧ24������322�����ú�ѡ��32��ֲ���һ��|����ԭ�� vmlinux/ABI��TINNO ��5.4.61ԭ�������ʧ46������14����ͬʵ�����ֲ��ɻ��á���[����](research/config-layout.md)|
|�ں�֤�ݲ�ȱ|�ֻ�config.gz��10��10�չ鵵ѹ���ֽ�һ�£�notes/kheaders/kallsyms��ȡ�ܾ���BTF��׼Ŀ¼���ɼ���perf_event_paranoid=-1|����/����sysctl��֤�������Ʋ��������ͻ�ʵ��perf���ʣ�ԭ��Image/Build ID/������ȱ����[GAP-01](research/p780-evidence-gap-audit-20261019.md)|
|GhostLock|��Դ��ģʽ�����á�Tracefs ���Ĵ��������鵵|**BLOCKED**��ȱ�����ں�©��ȷ�ϡ�������/����/�𹹽�ƫ�ơ���[ר��](research/ghostlock.md)|
|Journey Ӧ������|TCS/vendor XML �汾42��64���� ALL ����һ�£������߶�λ�������� Service/Provider ����|�����·��δ������ѧ��ǩ������ OTA/Root �������ظ���Ϊ�¹�����ڡ���[ר��](research/journey-config.md)|
|QAS / Mink / PFM|class119��eMBMS feature700��XR feature2100�����ִ�����־��UID/PID��ƾ��·�����з���|����������������Ȩ�ɹ���δ���� OEM Unlock����[ר��](research/qas-tee-pfm.md)|
|��̬����|1759��PC�嵥��batch1 742�batch2 514������ƥ�䣻���߰�55�豸�ļ�+��־|�嵥���������̼���ZIPδȫ����Git��vendor/bin��vendor/lib64���޲ɼ����ݡ���[֤������](EVIDENCE_MANIFEST.md)|
|Journey init / SELinux|��ȡ������policy��45391��AVTAB/849��genfs��¼��2437������bitmap���ODM��¼��ͬ��debug_prop�Ⱦɹ��������������ԭ��֧�֣�����Journey root������ȷ��running|�ļ���ϣ��ͬ����¼˳����header config��λ���챣��������SETools����diffδ����builtin/����/����˼�socket��ǩ��ȱ���ܾ�·�����ظ����ԡ���[GAP-01](research/p780-evidence-gap-audit-20261019.md)��[�ɾ���](research/p780-policy-boundary-audit-20261018.md)|
|native �ӿڽ���|Diag JNI��diag���HIDL������QSEE HIDL��װ��Mink JNI������������֣�6����ѡ���36����Բ�ѯδ��allow|���޿�ֱ�ӵ��õ���Ȩ��ڣ�����˺;��巽����Ȩδ�롣��[���汨��](research/p780-native-interface-crosscheck-20261018.md)|
|�ٷ�Դ������|���� TINNO �������󣻼���2026-10-18����δ���ֳ��̻ظ�|����δ���¼������䣻����������10/10��10/11��¼���죬���ʼ�ͷ�˶ԡ�Rakuten�ݲ���ϵ����[�����¼](official-source-request-log.md)|

## ����ժҪ�����ͱ߽�

- AVB ��Կ SHA-256��1032�ֽ� AVB ��ʾ����`7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`��
- ���� VBMeta digest��`33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2`������ VBMeta �ܳ���7744�ֽڣ����ǵ��������ȡ�
- B������ SHA-256��`fd98af142b11263e997adba190810c544857c7b750fd905a663e87256a71d880`����ֵ��A/B���ݶ�һ�������Ի���PC���������û������1.9GB����������㡣
- ͨ�� `write_misc_partition` �����ڳ��� `write_misc` builtin��DT_NEEDED/������������������ͼ��δ�����ַ�����֤��ʵ�ֲ����ڡ�
- ����Ԥ���� SELinux ����������ժҪ�Ǻϣ����������ں˲��� dump������ allow��root UID��socket 0666 �����ܵ���֤���˵��˲����ɹ���

֤�ݷ�Ϊ��ʵ��ԭʼ���/�����۲졢ԭ����̬����������Դ���������ο���δ��֤���衣ÿ��ע����Դ��������ͬ�ȼ������������һ��ͳһ�� [�ж��嵥](NEXT_STEPS.md)��

