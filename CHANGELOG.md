> 2026-10-24：准备 IPsec/UDP diagnostics v0.3.0 file-backed sendfile 预检；CI APK 构建与仓库审计均成功。该探针仅将应用私有临时文件经一次 sendfile 发送至 127.0.0.1 UDP，校验接收字节及源文件完整性；不启用 IPsec/ESP，且尚未实机运行。需机主另行确认设备执行。[v0.3 报告](docs/research/p780-dirtyfrag-v03-sendfile-probe-20261024.md)

> 2026-10-24：归档 IPsec diagnostics v0.2.0 实机回环 PASS；普通 UDP 与一个经公开 API 保护的 ESP transport 数据报均在 loopback 成功收发，dumpsys ipsec 资源计数归零。明确区分正常 ESP 路径与文件支持 UDP sendpage/共享页解密原语；DirtyFrag 仍 UNDETERMINED。下一候选为不启用 IPsec 的 file-backed UDP sendfile 回环探针，运行前另行确认。[实机结果](docs/research/p780-ipsec-v0.2-live-loopback-20261024.md) · [分析](docs/research/p780-dirtyfrag-v02-path-interpretation-20261024.md)

> 2026-10-24：审计新出现的公开 P780AE 设备树候选。固定提交含少量 P780/AVB 参数，但主体仍是 Xiaomi `veux` 实验性移植，无配套 P780 kernel/vendor、构建产物或真机成功记录；登记为待验证线索，不改变 Locked/无 Root/无写入通道结论。[详情](docs/research/public-p780ae-device-tree-audit-20261024.md)

> 2026-10-20：核对两份 policy 原件哈希及 header；修正 running=0x1、disk=0x80000001 的旧文颠倒；新增独立 header 工具/结果及源码对照。SETools 语义比较因工具缺失仍 BLOCKED_TOOLING，未新增设备权限能力。 [详情](docs/research/p780-policy-header-verification-20261020.md)

# �鵵ά����־

���°��׶α��浱ʱ���ۣ���ʷ��Ŀ�еġ�δ��װ/���⡱���������ڡ���ǰ״̬ͳһ��[STATUS](docs/STATUS.md)��

## 2026-10-19 �� GAP-01 ���в������ں�֤�ݲ�ȱ

- ADBȡ�ô�ǰȱʧ������SELinux policy��881104B����ODMԭ����ϣ��ͬ���޶�v30�������Ƚ�45391��AVTAB/849��genfs/2437������bitmap�ȼ�¼����ͬ��header 0x80000001��0x1���챣����δð��������������ȼۡ�
- ���µ�����config.gz��10��10�չ鵵ѹ���ֽ�һ�£�journey.factory.rcʵ������0��pull�ɹ��������ɴ�ȷ���notes/kheaders/kallsyms/����sysctl�ܾ���BTFĿ¼���ɼ���perf_event_paranoid=-1����дΪ����perf��Root��
- ������������/�嵥/�Ƚ�/����Ƚ���У���빤�ߣ��޶�״̬���ƻ���֤�������;�ר�⣻ԭʼpolicy/config��PC��������/�����޸ġ�������󡢰�װ��������ˢд����[����](docs/research/p780-evidence-gap-audit-20261019.md)��

## 2026-10-19 �� NATIVE-01 ʵ���˵������JNIʧ����

- ADBֻ��ȷ��customer=1��locked/green/_b/Enforcing�����µ��������APK/JNI/services����SHA��ƥ����ʷ��
- �����73JARɨ��ȱʧ�����Java���÷�������16������/17������JNI CFI��ʵʵ�֡�����������־��ʧ����С��Diag_LSM_Init����HIDL��������д�ɵ����Ҳ���SO��Ҳδȷ��SELinuxΪΨһ����
- ���Ӧ��UID1000��OEM������Ȩ�����ڿɵ��ô�������������޶���������ڣ�Handler��reboot������Journey root����ȷ��running����socket��ǩ���ɶ���vendor�˵�ԭ�����ܣ�NATIVE-02����������ʵ����ƣ����������Ի򷢰���
- ͬ��[����](docs/research/p780-native-live-endpoints-20261019.md)������֤�ݡ����߹��ߡ�STATUS/NEXT_STEPS/EVIDENCE_MANIFEST��û��Root����������������װ�����д�룻δ��sourcesͬ�����ϡ�

## 2026-10-19 �� OEMLOCK-02 ��������Ȩ�ޱ߽�

- ����ɨ��296��ȥ��APK/JAR��176/120������λ6��ֱ�����õ��õ㣬Ӧ�ò����õ��Settingsȷ�ϻص�������6������9ȷ��������ԭʼָ�SHA��
- ԭ��framework-res manifestȷ��MANAGE_USER/CARRIER/READȨ��Ϊ0x12��signature/privileged����176APK manifest�������쳣������Ȩ�޲�ð��ʵ����Ȩ������UID�ͼ�ӵ������з�Χ�߽硣
- ��������δ������ͨ�����߿ɴ����Ȩ������ֹͣ��Ϊ�ϻ���ѡ��δ�����ֻ���δдFRP���޸��������ԡ�ͬ��״̬���ƻ���֤��������[����](docs/research/p780-oemlock-caller-boundary-20261019.md)��

## 2026-10-19 �� OEMLOCK-01 Journey customer gate ��λ

- ����Settings/framework/servicesԭ��SHA�����߽���114Ŀ�귽��������15�ؼ��������ֽڡ�ƫ�ơ�SHA�ͷ���ࡣ
- Settings��ط�֧��AOSPһ�£�����OemLockService carrier getter����Ҫ�� !IS_CUSTOMER_VERSION��framework��ro.boot.journey.customer��ʼ����������ʷͬfingerprint����Ϊ1������PDB/���û����Ƶ���ɫ��
- getter/setter��鲻һ����ΪOEMLOCK-02��̬��ѡ��ϵͳȨ��������shell������֤ʵ��ͨ������·�����޽���/Root����¼��һ���ۺϲ�ѯ��ֻ��Э��ƫ�ǰ��Ȩ���쳣�����ֲ������ֻ���
- ͬ��STATUS��NEXT_STEPS��EVIDENCE_MANIFEST��[ר��](docs/research/p780-oemlock-journey-gate-20261019.md)��

## 2026-10-19 �� OEMLOCK-01 �����׶��û������ų���Settings ����λ

- ʵ����ǰ�û�Ϊ0���� Restrictions:none��device policy global:null��local:none��effective:none��Guest ���Ʋ���ͬ���û�0���ơ�
- Android ��ǰ Settings λ�� /system_ext/priv-app/Settings/Settings.apk����� PC �嵥�Ǽ�һ�£���δ������������� SHA������������ Documents/P780-EDL ����Ŀ¼������Ӧ�� Desktop/RakutenHand5G ��С���ؽ���ֻ����ȡ APK �����߱Ƚ� OEM ������������
- �����ȷ�� PDB ��������û�0���ƣ���һ����С��ɫ����ԭ����δ��λ�豸���м�飬�� Bootloader ������ Root������[ר��](docs/research/p780-oemlock-first-results-20261019.md)��

## 2026-10-19 �� OEMLOCK-01 �ڶ��׶�ȷ�� PersistentDataBlockLock

- ���� logcat ֱ���ṩ `OemLock HAL not present on device` �� `Using persistent data block based lock`��ȷ�ϱ��� Android OEM Lock ʵ�ʺ�ˣ�compatibility_matrix ֻ������������������ HAL ʵװ֤�ݡ�
- �û�����ɸѡ�ظ��� `no_factory_reset` �� `no_oem_unlock`���� AOSP δ�� PDB carrier �ж���Ӧ���� carrier��Ȼ�� UI ����ʾ carrier/connectivity �İ�����ì����δ���ͣ���Ӧֱ���Ʋ�������������
- PC manifest ��λ����ǰ�ɼ��� P780 Settings.apk����¼65,392,240�ֽں� SHA256���½׶����Ⱥ˶������ļ������߼�鳧�� Settings OEM ���������߼����ǵ��� Binder ��� FRP����[�ڶ��׶�����֤��](docs/research/p780-oemlock-first-results-20261019.md)��

## 2026-10-19 �� OEMLOCK-01 ��һ�׶�ʵ�ʽ��

- �������� OEM unlocking ���ػ�ɫ����ʾ�������ӵ�����������������Ӫ����ϵ������ Android 11 AOSP `oem_unlock_enable_disabled_summary_connectivity_or_locked` ����ԭ������һ�£�����ʾ������Ӫ������״̬����� `DISALLOW_FACTORY_RESET` ���ơ�
- ADB ȷ�� supported=1��allowed=0��flash.locked=1��Framework oem_lock �� persistent_data_block �����ע�ᡣlshal �� OEMLock ���е�ö���д������棻�û�/�豸����ɸѡ����ȷ���С�����δȷ�� Vendor HAL vs PDB ��ʵ�� carrier allowance��
- �ѹ鵵[ʵ��С��](docs/research/p780-oemlock-first-results-20261019.md)�͵ڶ��׶ν��۲� OemLock ��־��VINTF �������û����Ƶ����δִ�� Binder transaction������д������������

## 2026-10-19 �� OEMLOCK-01 �²��Ե㣨���ʱ��δʵ�⣩

- �˶� Android 11 AOSP Settings �� OemLockService��ȷ�ϻ�ɫ���ؿ�������Ӫ�� HAL��PDB���û�/�豸���Եȶ��ַ�֧��ɣ�P780 ����֧����������ʷ Fastboot unknown command ���ܵ���ȷ����ϲ㡣
- ����[ֻ��ʵ��Э��](docs/research/p780-oemlock-gate-probe-20261019.md)����һ��ֻ��ѯ����/����/HAL/�û����豸���ԣ������� Binder ����д��� EDL/DSU�������� Root/BL ����������

## 2026-10-19 �� Mannar A�CE ���ѡ����ǩ������᰸

- ��������ʱ���������������йرվ� Loader ���ݿ�ȥ�غ󣬳ɹ�ȡ�� B�CE ȫ��֤��������������������־һ�¡�
- A/B/C ��Ϊ d9357db8����D Ϊ 4352b3bf����E Ϊ a51a1c2e��������ͬ�� P780 c19a5029����ֻ�� A ��ʵ�� READ64��B�CE δ����ʵ����֤��û���κκ�ѡ��� Firehose��
- ����ר�⡢README��STATUS��NEXT_STEPS��HISTORY��EVIDENCE_MANIFEST����ͣ����5����ƥ��ǩ���� Loader �����ϻ������Կ���ͬ�ͺŻָ�����ǩ�� programmer ��չ���ߵ��顣ԭʼ���������ݵ���־����⡣

## 2026-10-19 �� ��ѡ A ����ǩ������ȷ��

- �����ɹ�ͨ�� `fhloaderparse` ���� 698440B Mannar ��ѡ A��OEM Qualcomm��MODEL 0000������ HWID ȫ�㡢SWID 3��QCVER `BOOT.XF.4.2-00269-MANNARLAZ-1`��VAR `MannarPkgLAB`���� PKHash `d9357db8��` �� P780 `c19a5029��` ��ƥ�䡣
- `Duplicate` ��ԭ Loader ���ݿ���ǩ�������ظ�ʶ�𣬲�����ԭʼ�ļ��𻵡��ڲ� HWID ���ļ������ܻ�ͬ���ú�ѡ���ٽ����ٴ��ϻ����Ĵ� READ64 �ж���δȡ���豸����֤�����룬���������Ѿ�֤����������
- ����ר�⡢STATUS��NEXT_STEPS��EVIDENCE_MANIFEST������ԭʼ�豸��־����֡�

## 2026-10-19 �� �豸�ָ������� Loader ��Դ�Ų�

- ����ȷ�� QDL ����ʧ�ܺ� ADB �豸���ߣ�`sys.boot_completed=1`���豸����������ԭ�� Android��û���ɴ����� Firehose �ɹ���
- �Զ������ Loader �ֿ�ĵݹ��ļ�·������ֻ��������δ�����ļ�������ƥ�� P780 HWID/PKHash ǰ׺�� programmer�����Ƕ��������ݲ�������������һ���� PC ���߽���ʵ��֤������ɸѡ��
- ԭʼ�豸���кż�������ֿ⡣��� QDL ʵ��ר�⡣

## 2026-10-19 �� Mannar A ���� READ64 �ж�

- QDL QUD/COM6 �����Ĵ� Sahara image 13 READ64 �������δȡ����һ�� Sahara ��Ӧ��δ�� END OF IMAGE��DONE��Firehose ���л�洢���ʡ�
- ��ѡ PKHash ǰ׺��������֤�ܾ������Ʋ�������Ѳ���� NAK������ `EARLY_SAHARA_READ64_FAILURE / CAUSE_UNDETERMINED`����� EDL ʵ��ר�⡣

## 2026-10-19 �� P780 Windows QUD/Sahara ʵ��ͨ��ͻ��

- ������ Windows ʹ�� QDL v2.8���ٷ� Windows x64 Release�������Ա� v2.8-dirty��ͨ�� QUD/COM6 ö�� 05c6:9008�����ɹ�ִ�� Sahara v2 chipinfo��HWID/MSM/OEM/model ���������ڼ�¼һ�£�PKHash ǰ׺Ҳ�Ǻϡ�
- bkerler/edl v3.62 ����ģʽ��ʼ HELLO δ�������գ�����ط��� Firehose XML NOP ��ת�� Streaming/HDLC�������� seriallib ���̶�ȡ���ȵı����޲�δ�����QDL v2.8 ���� QUD �� HELLO �������ɴ��󲻵ó�Ϊ��ѡ A ���ܡ�
- ��¼ Mannar ��ѡ A �� MSM ƥ���� model/ǩ����ϣǰ׺��ƥ�䣻�������θ���**δ�ϴ� Loader���� Firehose���޷�����д���� Root/BL ����**��
- ����[ר��](docs/research/p780-qdl-qud-sahara-20261019.md)��ͬ�� STATUS��NEXT_STEPS��HISTORY��EVIDENCE_MANIFEST���豸ҳ��������README�������������кŻ����� PKHash ԭ������ֿ⡣


## 2026-10-18 �� ȫ���ܽᡢ��ǰ״̬������native�������

- �������ǰ289�ļ�����������87��Markdown/Python/���������ݣ���дREADME��STATUS��NEXT_STEPS���ĵ�������֤������������B��δ�ϻ�����Attestation�����⡱��SELinux����ȡ���ȵ�ǰ��ڳ�ͻ��
- ����֤���˱���10/11�ṹ���ն���鵵��DSU��ר�Ᵽ��·���뼼�����ݲ�����ֹͣ״̬������ʱ���ߺ͵�ǰ�о�ȥ��
- ����6��native����/������36�������Բ�ѯ��δ����ֱ��shell�ɴ����Ȩ��ڣ������ӿڿ⵱����ʵ�֡�
- �������м���֤��ԭ������ʷ���������ģ�������ͬSHAäĿȥ�أ���̬֤��Ŀ¼���������Թ�����������Χ��
- Դ���ʼ�����10/10����ĵ�10/11�в��죬��Ϊ���ʼ�ͷ�˶ԣ�����û�����²��������ļ������
- ��ϸ��Χ����֤��[��������](docs/REPOSITORY_AUDIT.md)���ֻ��ޱ��ֲ�����DSUֹͣ��Root/BL״̬���䡣

## 2026-10-18 �� ��̬�ɼ���batch1/batch2��SELinux�׶�

- PC�嵥1759�batch1 742�batch2 514���С/SHA256ȫ��ƥ�䣻policy��55�豸�ļ�+��־��3��CIL/mappingժҪ���ס�
- ST factoryΪNFC��������Journey debug�����Ǿ�̬Ȩ�޺�ѡ��ͨ��write_misc_partition�����ڳ���builtin���ؼ�����ԭ����ȱ��

## 2026-10-18 �� DSUʵ���׶�����

- B�Ѱ�װ������ԭ��dynsystem���������ջ�ԭ���������ָ��������ٱ���ԭ��Loader���ˣ������ȷֹͣ·�ߡ�
- ������B��δ�ϻ����ĵ�ǰ״̬��ʧ�ܽ׶�δ֪�����϶����̽�ֹDSU��������Root������������д�롣

## 2026-10-18 �� ��ʮ���֣�Android15 ���Ը�ǩ�� GSI �������ɣ�ԭ������ǩ�� AVB ������֤ͨ��

- �û�Windows��ʵ����v1.1���߲��ϴ�AVBԭʼ/��ǩinfo�����TXT��3���ļ����ֶ�������SHA256��AOSP `avbtool verify_image` ��������ʵ1.9GB������֤footer/VBMeta RSA4096ǩ���� system Hashtree �ɹ���**��ǰ���߽�ģ����֤��״̬�ѱ���ʵʵ����ȡ����**
- A��ԭ��Google Android15 system��ԿSHA256 `e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925`��Q Developer GSI����B����ǩΪAOSP Root testkey SHA256 `7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`����P780 TEE Boot Rootƥ�䡣B���������� SHA256 `fd98af142b11263e997adba190810c544857c7b750fd905a663e87256a71d880`��ԭ��SHA256 `27321f9655530f014c884a690f49a53e6f3beeda71f4f27cbc141b17a8e86954`��PC���棩��
- ���߽ű��˶�VBMeta offset1899151360/size2432���ֶ�SHA�Ƚ�ȷ��VBMetaǰ/�������ֽڲ��䣻�ļ�ϵͳ��Merkle Hashtree��FEC��Footer��image��С��Flags0��RollbackIndex��SPL��ȫ��ͬ��VBMeta��������˳��ͬ��������ͬ�����ֶ����Ƚ�AVBԪ����28���Ч�ֶν���Կ�����仯��û������/�ϴ�������GB���������ֲ��ٴι�ϣ��
- �½� [��ʮ����Windows AVBʵ֤����](docs/research/p780-dsu-testroot-resign-verified-20261018.md)��ͬ���о�״̬����һ����**������ǩ�ɹ���P780 Loaded/����/Root**������������ʵramdisk��Կ������Ҫ�ϻ�B�飬���ȱ��ݡ��滮����ԭʼDSU��Recoveryʧ�ָܻ���ʹ�÷�Root��װ��ͣ��Restart֪ͨ������ȷ�ϲ�������

## 2026-10-18 �� Windows OpenSSL ǰ�ü��ʧ�ܣ��ṩ���� DSU ��ǩ���� v1.1

- ����Windows PowerShellִ��v1��������`[1/4]`�׶���`OpenSSL CLI is not on PATH`��ȫ��ֹ��ϵͳ����δ�޸ģ�����AVB��ǩ�����Ҳû������P780��
- �Ѵ����Ự���� `P780-DSU-testroot-offline-tools-v1.1.zip`��10708B��SHA256 `467c36c5c89957a044c2ddcb2adfaf21ed180e797c965bf8db447878f3ff17e4`�����������ɷ��ֵ�ǰPATH��Git for Windows�ͳ���Windows��װĿ¼��OpenSSL����ʵ�����а汾���ԣ�ֻΪ��ǰ��������PATH����ȱ��OpenSSL����ʾ�ٷ�Winget��`ShiningLight.OpenSSL.LTS.Light`��װ��ʽ��
- ����Pythonǩ������û�б����ZIP CRC��Python�﷨�Լ�ͨ����**��δ���û�Windows����/��ʵ1.9GB GSI������°汾ǩ������**���о�����������NEXT_STEPS��ͬ����δ�����ֻ���Bootloader��LOCKED��δRoot��


## 2026-10-18 �� ��ʮ��������ǩ������ v1��VBMeta-only����ǩ�������ֽڿ��Ʊ���У��

- ����û�ͬ���Windows PC�˿����ع��߰� `P780-DSU-testroot-offline-tools-v1.zip`��9769B SHA256 `189d3a4b6e92eea0cc21e24dfde29950a981b35bef72c6997925bcc26ee4dab6`����Python�ű���PowerShell������������README��ԭ����Root����˽Կ�������������д�AOSP����Դ���أ�Python��У����AVB��ԿSHA256��P780 TEE��֤ʵAOSP���Ը�һ�¡�
- Ϊ���ٱ����������������**���ؽ� Hashtree �� FEC**��ֱ�ӱ���ԭAndroid15ϵͳ�����fs/verity tree/FEC/footer�ͷ������ȣ�������ǩ�� `system.img` ��2432BǶ��ʽVBMeta���¾ɷ�VBMeta���ݷ�������SHA256���һ�£�ǰ�����һ��AOSP `avbtool verify_image`��ʼ��Flags0�Ҳ���ʹ�ùٷ�ZIP��Flags2��ͨ�� `vbmeta.img`��
- ���Python�﷨/��ʵ����AVB metadata����/ģ��avbtool�˵��˲��ԣ�**��δ������1.9GB�澵���Windows+ԭ��avbtool����ʵ����**�����״̬�������߽������ȴ��û�ִ�С�����ADB/Fastboot/EDL���ֻ�δд�롢δroot�������
- ��� [��ʮ������ǩ��GSIר��](docs/research/p780-dsu-custom-testkey-gsi-hypothesis-20261018.md)�� [NEXT_STEPS](docs/NEXT_STEPS.md)��ʵ�������ͨ��PC��AVBǩ��/����һ����У�飬Ҳ����֤ʵP780��first-stage `avb_keys`������������Root��

## 2026-10-18 �� ��ʮ���֣�������P780 AVB������Կ©������ǩ��DSU GSI���Ʊ���ʵ��

- �����������ȻJVN#47427200/CVE-2026-107153ȷ��P780ʹ��AOSP����AVB����Կ���ܷ����������һ������GSI������DSU Sideloader����BL Locked��������������JVN�ٷ������� Android�ٷ� DSU �Զ��徵��ǩ�����ƣ�**���ۿ��ԣ���Root of Trust �� first-stage standalone GSI�����Ĺ�Կ����ͬһ�����ж�**��
- ͨ��AOSP `fs_avb.cpp` Դ��ȷ�� Locked ��GSIϵͳ���������Կ���������ϸ�ƥ�䣬δ֪��Կ���ܺ��ԣ��û�ʵ��fstabֻ����ͨQ/R/S key��Google Android15ʵ��system��Q Developer��Կ����������Կǩ�ĸİ澵��Ҳ�����������Կ���ʧ�ܡ����ܰ�©���������ɡ�DSUһ�����ƹ�AVB����
- ��VegaBobo DSU Sideloader�ٷ�README����Root ADB/Shizukuģʽֻ��DSU Installerǰ�ˣ������Զ���ǩ������Ŀ������BL��Ϊһ��Ҫ����P780��ֻ��**ʵ���豸���θþ���**��������̬�ɹ����ᡣ
- �½� [ʵ�鷽����CVE-2026-107153 �� AOSP���Ը���ǩGSI �� DSU Sideloader](docs/research/p780-dsu-custom-testkey-gsi-hypothesis-20261018.md)����ѡ�̶�����Android15�ļ�ϵͳ�����������Android������PC������ǩAVB����������verify�����뵥��ͬ���ұ��ݺ�ſ���ʵ��DSU��װ��������**��������ǩ���������ֻ���������Root��BL����**��

## 2026-10-18 �� ��ʮ�����ش�֤�ݣ�Android15 system��Կȷ��ΪQ Developer��generic vbmeta����֤��������

- �û�����PC������ȡ���ϴ����AVBԪ����/��Կ�ļ����ٷ�ZIP SHA256��PC�౨��У��ͨ�������ֱ��ض�����ϣ������ʵ1032B��Կ��Android15 `system.img` SHA1=`1ffb1af796b18ebf40d18faed213f686720f73f2`��SHA256=`e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925`��**��ȷƥ��Q Developer GSI��Կ**��
- ��P780ԭ��fstab����ȷ�ϵ���ͨ q/r/s GSI ��Կ·���γ�����̬ AVB �������ò����**ǿ�ɵ�**����Ŀǰû�� `_162` ramdiskʵ��key�� first-stage AVB�ܾ���־�����Բ��ܽ���Ǽ�Ϊ��ȷ��root cause��Ҳ�����ų�image mapping/active slot����ʧ�ܡ�
- ͬZIP `vbmeta.img` Ƕ�� SHA256=`7728e30f...`��AOSP RSA4096����root��ǡ����P780 TEE attested rootһ�£�**��Flags=2Ϊverification_disabled����system chain descriptor��ԿSHA1=`cdbb7717...`���������AOSP RSA2048 testkey������ʵ system q-developer��Կ��ƥ��**������generic vbmeta���ܵ���ϵͳ��ͨ��AVB��ͨ��֤��Ҳ��Ӧˢ���ֻ���
- �½� [��ʮ������ʵ��Կ��AVB��ʽԪ�������](docs/research/p780-dsu-android15-avb-key-verified-20261018.md)�����µ�ʮ������ǰЭ�顢Locked����ר�NEXT_STEPS��STATUS��EVIDENCE/README�������о��ص���P780 `_162`����Boot/Ramdisk��ǩ����Կ���ϡ�δ���ֻ�ִ���κ��²�����

## 2026-10-18 �� ��ʮ���� DSU ������Կȡ֤��׼�� Google Android15 GSI ZIP PC У���� AVB Key ��ȡ

- �û�ͬ�������ȡ Google Android15 ��GMS ARM64 ����ʵ GSI signing pubkey����֮ǰ�Ѻ���Ĺٷ� `vic/gsi-dsc.json` �� Google�ٷ�����˵��ȷ��Ϊ `aosp_arm64-exp-BP1A.250405.005.C1-13151952-61d23231.zip`������ SHA256 `61d232315ad773bd4820c76c175efe6a61cd8a9a257508db588032be213e15f7`��
- ���ɵ�ǰ��������� `p780_gsi_avb_run.ps1` �� `p780_gsi_avb_extract.py`��Դ��SHA��˵���� [��ʮ���ֲ���Э��](docs/research/p780-dsu-android15-avb-extraction-plan-20261018.md)�������߻���֤����SHA��ֻ��ȡ `system.img`/`vbmeta*.img`������AOSP�ٷ� `avbtool info_image --output_pubkey` �����ʵAVB key�ֽ���SHA1/SHA256��Python�﷨��ģ���������̲���ͨ����**��δ�������ٷ�GB��ZIP��������ʵ��**��
- ǿ�������õ�Android15��ʵǩ����Կ����**����֤��P780 ramdisk�Ƿ����θ���Կ**����Ϊ `_162` ʵ��ramdisk�����AVB�ļ���ȱ�����ݹ���AOSP q/r/s��ͨ/Developer��Կֻ��Ϊ�ο��������Ų� first-stage DSU slot/mapping ������֤�ݵع��AVB��
- ���� NEXT_STEPS ���о��������ȴ�����PC�����������P780����ˢ�������ظ�DSU Restart��Root/BL Locked״̬�ޱ仯��

## 2026-10-18 �� DSU ���� Locked BL �𣿺��鹫Կ���η��磬�����о����ȼ�

- �ش������δ����BL�Ƿ�ʹDSU�޷����ء��Ĺؼ����ʣ�AOSP�ٷ� **֧�� LOCKED + Verified Boot����**�� Developer GSI������Ԥװ��Ӧ�����ι�Կ�����ǡ�DSUһ��Ҫ��������Locked �豸��δ֪GSI AVBǩ��ʱ��`fs_avb` �ܾ�������֤�����Ź�Կ�Ƿ�����Ǿ������֤�����������
- �� P780 fstab ���õ�**��ͨ** q/r/s-GSI��Կ�� Google AOSP **Developer GSI** q/r/s-developer��Կ�ϸ����֣���� Google 2021-12-22 �Ƴ���ͨ�Ϲ� GSI ��Կ�����ֻ�� VTS ���ύ���������ò����ǿ�ɵ㡣��ǰ��û�ж�ȡP780ʵ�� first-stage ramdisk�е�����keys��Ҳδȡ��Android15 GSIʵ�� AVBǩ����Կ��**�ܾ��Ѽ�˵д��AVBǩ��ʧ��ʵ֤**��
- Android11 `gsi_tool status`Դ��֤ʵ��rootֻ��� installed/disabled��Root�Ŵ�ӡ��װGSIǩ��key SHA1����ͨ shell ���ɻ�ã�����������Ȩ�ޡ�AOSP��ǰ GSI release makefile ����ʽ֧��30��34��VNDK snapshot��Ŀ��BP1A��δ������֤����
- �½� [LOCKED/Developer GSI ����������](docs/research/p780-dsu-locked-bl-vs-gsi-trust-20261018.md)������NEXT_STEPS/STATUS/֤��/README���ĵ�����������Ϊ first-stage activeDSU��MapAllImages��ֱ�ӷ���ԭ���߼��Ƕ����߼�ֵ��ѡ�����ֽ�Դ���о������û���ADB��ҲδRoot/����/ˢ������

## 2026-10-18 �� ��ʮ���֣�P780 Bugreport ȫ����ƣ�LAST KMSG �� LAST LOGCAT ���޷�ȡ��

- �յ�������ʵ `adb bugreport` ZIP��362��Ա��ԭ��SHA256 `64a097d0911e35675c75dff09d68a7e28b5aa15bd342ed796387d12758d5f141`��������������ȡ��TXT 19.7 MB / Լ240,297�У�δ�����ܺ��˺�/�豸MAC/�����¼������ԭ���ϴ�GitHub��
- �ҵ� `persist.sys.boot.reason.history` ������ `reboot,dynsystem`������ΪUTC+8 2026-10-18 06:30:31��06:31:30��ȷ�ϻ������������ֶ�����DSUר������������ `gsid.image_installed=1`��`ro.gsid.image_running=0` ��ԭ��B��dmӳ��֤���ռ�����ʱGSI�����С�
- `dumpstate` ���ܶ�ȡ `/proc/last_kmsg`���ļ������ڣ���incidentd���ܴ����� `console-ramoops`��last_kmsg��`logcat -L`ʧ�ܡ���ǰ `dmesg`�������ǿ���943������û�а���ʧ�ܵ�early initʱ�Σ��޷�ȷ��ӳ��/AVB/�����������⡣**��ƥ�䲻��д�������**��
- �½� [P780 Bugreport 13��ȡ֤����](docs/research/p780-dsu-bugreport-audit-20261018.md)������ STATUS/NEXT_STEPS��֤�ݱ���ֹͣ�ظ�ͬ·��bugreport/logcat/kernel������ϲ����DSU Restart��ת����� `_162` boot/ramdisk/first-stage ��Կ������ǩ����������Դ�о���**����δ��������GSI�������豸�����Root/BL������**

## 2026-10-18 �� �ҵ������ٴ������� DSU early boot ȡ֤;����Bugreport��

- �о� AOSP framework/native `dumpstate.cpp::DoKmsg()` ֤ʵ�ٷ� Bugreport �᳢�Զ�ȡ `/sys/fs/pstore/console-ramoops`��`console-ramoops-0` �� `/proc/last_kmsg` ������ `LAST KMSG`����ͨ ADB shell pstore Permission denied��kernel logcat 0B **�����Զ��ų�** dumpstate �Գ־û� early boot ��־�ķ��ʡ�
- �� [DSU ��������ר��](docs/research/p780-dsu-stock-fallback-20261018.md) �� [NEXT_STEPS](docs/NEXT_STEPS.md) ����������ѡ�� `adb bugreport .\P780-DSU-Bugreport.zip`��**��ǰ��δ�� P780 ִ��**������Ҫ�ٴ� Restart��Ҳ������ boot/vbmeta��������û�б��� pstore ����������ݡ�
- Bugreport ���ܰ����˺�/����/�豸��ʶ��ǿ���ȱ��ر�����������ŷ���������δ���˶Ե�ԭʼ ZIP �ύ˽�л򹫿� Github���������ֻ�ʵ�������Root/����/DSU �������Խ��۲��䡣

## 2026-10-18 �� DSU ����ʧ�ܺ��ִ�о��ߣ�ֹͣ�ظ��Դ������� first-stage ��֧

- �������� `installed/disabled`��`reboot,dynsystem`��������������ԭ����Kernel logcat 0B �� pstoreȨ�޾ܾ����϶���ʱû����֤������ root cause �ĵ�һ�׶δ�����־��
- �˶� AOSP Android11 `UseDsuIfPresent()` �� `CanBootIntoGsi`��`GetActiveDsu`��`MapAllImages`��`MarkSystemAsGsi` �ȿ�������·����one-shot ������һ�γ�����Ԥ�Ƚ�**��һ��**״̬��disabled�����ܽ������º� `disabled` �ж� enableʧ�ܡ�
- ���� [DSU first-stage ��Ͼ���](docs/research/p780-dsu-stock-fallback-20261018.md) �� [NEXT_STEPS](docs/NEXT_STEPS.md)��û������Ϲ۲���ʱ�����ظ� Restart�������� `-s` �� `gsi_tool enable` sticky mode����ð�ջ� Android16/Recovery wipe�����Ȳ�����P780 `_162` ��Ӧ�Ŀ���֤ boot ramdisk��DSUǩ��֤�ݡ�
- ����**û���µ��û� ADB ʵ�⡢û�о������ػ��ֻ��Ķ�**���������ռ�֤���ϵ�Դ������뷽�����¡�Root��BL ����ԭ������д��״̬���䡣

## 2026-10-18 �� ��ʮ���֣�DSU reboot reason ��֤ʵ��һ����������ԭ�����ں˻�������

- ������ȷ DSU Restart ��**������������ֱ�ӻ� Android11 ԭ��ϵͳ**��û�й۲쵽 GSI ϵͳ�����ڶ����Զ�������`ro.boot.bootreason=reboot,dynsystem`��`sys.boot.reason=reboot,dynsystem`��֤���ô�����Я���ٷ� DSU ר��ԭ�򣻲����ٰ����ⶨλ�ڡ�֪ͨ��ťû�����������ϡ�
- `adb shell logcat -g` ��ʾ kernel buffer ��� 2MiB����ǰ��¼**0B**��ɸѡ `logcat -b kernel -d` ���κ��У�ǰ�� pstore Permission denied��˵���޷�ȡ�ñ���ʧ��ǰ�� first-stage ���󣬲�֤���ں��޴���
- [AOSP Android11 `UseDsuIfPresent()`](https://android.googlesource.com/platform/system/core/+/9583e92257ab85075231b014f0999d5a5dab9910/init/first_stage_mount.cpp) ����������״̬��DSU slot��ӳ��ӳ�䡢indicator �Ȼ���ʧ�ܾ����ܷ�������ϵͳ���� one-shot ����ʹ�º� status=disabled �����������ۺϻ���ֻ����һ�εĹ۲죬**�����о��״������׶�����**��AVB/ӳ��ʧ�ܾ��������δ֤ʵ��
- ͬ�� DSU���ר�⡢NEXT_STEPS��STATUS��README��֤�ݱ���ֹͣ�ظ�������֤�ݵ� `logcat kernel`����ͨ getprop ��DSU Restart����ǰ�豸�Կɽ���ԭ�� Android11��δRoot/������

## 2026-10-18 �� ��ʮһ�� DSU ��־������һ��������״̬���ѻ���ȷ��

- �������� GSID��`gsi_tool status`= `installed` + `disabled`����ǰ�� `_b`��`ro.gsid.image_running` �գ�pstore���ʱ�SELinux/Ȩ�޾ܾ���UI�ظ�����ԭ��ϵͳ��һ����õ��˰�װbackend�Ķ���֤�ݡ�
- ���ض��������û��ϴ��� UTF-16LE 4.1MB Logcat��15455�У�SHA256 `955c9775371658b36d59e749c648149193a05746a72d26807f09a3f97de6e970`�������й�����־��SHA256 `333d7ac1de09d46f4a77a3611842a38d47c0ec14819d2b2b23d6ebfb2a74cf76`����ֱ����ȡ `DynamicSystemService: isInstalled(): true`��`NOTIFY_IF_IN_USE` ��������֪ͨ��δ���� first-stage/AVB/����ӳ�����ԭʼ��¼��**���ύԭʼ������־**��
- Android 11 AOSP `libgsi.cpp::CanBootIntoGsi` ��Ĭ��one-shotģʽ**���γ��Լ���ǰ**�ͱ����һ��Ϊdisabled������ڵ�ǰԭ��ϵͳ����disabled���ܼ���ϳɡ�UIδ����������ǡ���AOSP first_stage���� images map��AVB/fstab��֤�Ⱥ������裬��������ֱ����־��
- ���� [��ʮһ�ֵ���ר��](docs/research/p780-dsu-stock-fallback-20261018.md)��STATUS��NEXT_STEPS��֤���嵥��README�������������ں���־������/bootreasonֻ�����ģ����ظ��������������ء�Root���޸�GSID����״̬��

## 2026-10-18 �� �״� DSU ��װ��ʾ�ɹ������������Է���ԭ��ϵͳ����ϴ��ռ���

- ����ʵ�ʲ��� DSU��GSI ������ɡ�ϵͳ��ʾ��� Restart�����������ֶ�������豸��������ԭ�� Android11���������ʾ DSU Restart ֪ͨ��**ԭ��ϵͳ�������ã���δ�ɹ����� Android15 GSI���������������Զ� bootloop��**
- �ֱ� UI �����ʾ�� GSID��ʵ installed/enabled/early boot��ǩ������ֱ�� status��pstore��logcat �Ͱ�װ build ID��AVB ��Կ��ƥ�䡢one-shot״̬���á�DSUӳ��ӳ��ʧ�ܡ�init/HAL���϶�ֻ�Ǵ�֤��˵��
- �½� [������ԭ��ϵͳר��](docs/research/p780-dsu-stock-fallback-20261018.md)������ STATUS��NEXT_STEPS��EVIDENCE_MANIFEST������ʵ��Э����˵����������ͣ�ظ� Restart���ݻ� Discard�Ա���֤�ݣ����õ�ǰԭ��ϵͳ������־��״̬��ѯ����ֹäĿ `gsi_tool enable/disable/wipe` ������ˢд��

## 2026-10-18 �� �û������ƽ� DSU �״�ʵ�����飬���÷ֽ׶ΰ�ȫ����

- ������Ϊ DSU ������ԭϵͳ���Ը��ʵ�ʳ��ԡ��Ѻ˶� Google [�ٷ� DSU](https://developer.android.com/topic/dsu) �� [Android15 GSI ��֪����](https://developer.android.com/topic/generic-system-image/releases)����׼ DSU ����д��ԭ�� system/boot�������޸� userdata��ʧ���� Recovery factory reset/���ݶ�ʧ���գ������ɾ�������֤��
- ����ʵ�� ARM64/VNDK30/Treble/�ռ����������������ѡ�� Google Android15 QPR2 `GSI ARM64` �� GMS `BP1A.250405.005.C1` ��Ϊ��һ���ܿ������ѡ����δ֤�� AVB/GSIǩ�����λ� HAL ���У�����ѡ GMS/Android16���� fastboot/EDL ǿˢ��
- �½� [DSU �״�ʵ���ֶ�����Э��](docs/research/p780-dsu-first-trial-protocol-20261018.md)������ȷ�Ͽɶ�ʧ����/������ USB ADB���׶� A �� Settings ����/��װ����֪ͨ Restart/Discard ����ͣ���׶� B ����ȷ�Ϻ��ʵ�������� GSI��
- ��ǰֻ��׼���ĵ����û���Ȩ���������ذ�װ������ʵ�����豸�� LOCKED/δRoot������ STATUS��NEXT_STEPS ��֤���嵥���ȴ����������׶� A ʵ�������ٸ��½����

## 2026-10-18 �� �ھ��� DSU ǩ�������������ݹ��� GSI AVB ��Կ��ϣ�� AOSP ������������

- ������� Android11 `target/product/gsi_keys.mk`��`developer_gsi_keys.mk` �� `rootdir/avb/Android.mk`����ȷ�����׼ q/r/s-GSI �� Developer q/r/s-GSI ��Կ�ֱ���ڣ�P780 fstab ֻ����**��׼** q/r/s-GSI �ļ������ɰ�������ͳ���� Developer GSI key��
- ���� GitHub ���� Android11 Դ�뾵���� q/r/s ��ͨ�� Developer ������ RSA4096 AVB ��Կ�����ƣ�1032B/�ݣ���JS SHA256 �� abc �����Բ��������ϣ������ժҪ����ͬ�� P780 TEE KeyAttestation AVB Test ����ԿժҪ��ȫ�� SHA��Git blob ��ϣ��AOSP Դ��֤�ݼ� [�����ھ��ֱ���](docs/research/p780-dsu-trust-chain-audit-20261018.md)��**û��ֱ�ӷ��� P780 boot ramdisk �ֽڣ�������Կֵ�Ǻ�ѡ֤�ݣ����ǻ��ϼ���ʵ�⡣**
- AOSP �� Settings DSU JSON ɸѡ����װ�ڿ�ѡ��ԿԤ���/�������� first-stage AVB �������Ź�Կ��֤�ֿ���ȱ�� JSON pubkey ������ǩ���ƹ�����ȱ Android15/16ʵ��ϵͳ���� AVB Footer ǩ��Կ�׺� P780 ʵ������ʱ����Կ�ס�
- �� Google �ٷ� Android15/16 GSI ����ҳ��˶�δ��ZIP SHA�������ֲ����豸����/���� GSI ʧ��ʱ������ Recovery ��� userdata���˷��ղ�������ƾ DSU �ǡ���ʱϵͳ�����ŵ������ˣ��ݲ����ء���װ������ GSI����Ӱ�� locked/δ Root ��״��
- ͬ�� STATUS��NEXT_STEPS��DSU ��ר�⡢������֤���������������ظ�����ɵ� Treble��KeyAttestation/JSON ץȡ��

## 2026-10-18 �� DSU ����Ŀ¼����Ԫ�����Ѻ��飺24��ȫ�� VNDK/pubkey��CP11 ����

- �����ϴ� `p780-dsu-catalog-detail.zip`��4073B / SHA-256 `ad732d61aa7751aeaa6f2a148e3a1998aeee645beb5fe3f344fff98d9ca74c74`��������֤ZIPȫ��8�����Ŀ¼ԭʼ�ֽ�SHA��report����ƥ�䣬�޶�ȡ����24�� GSI JSON ��¼�Ѿ�����������
- 4�� P780 �˵���Ŀȷϵ Google `vic` Android15��BP1A����� `baklava` Android16��CP11�������ͼ�������� JSON ���պ�ȷ�� **CP11��������1��**�����Ǿɽű�Ŀ�� `CPI1`�����Զ� report.matches ֻ��4�� BP1A����x86����©��Android16��������ʧ�ܡ������˴����Թ���ƣ�����Ҫ���ظ�ץȡ��
- **���Ľ��ۣ�ȫ��24�� JSON��ȱ `vndk` �� `pubkey`**���ͻ��˻�����ȱʧ�ֶζ�Ӧ��Ԥɸ������˵����ֲ��ܱ�ʾ VNDK30��ȷ֧�ֻ� GSIǩ���ѱ��豸���Ρ�R/S/T/U�ɾ���İ�ȫ��������P780 2024-02������SPL���˽�����Android15/16��ARM64��2��
- �½� [��������](docs/research/p780-dsu-gsi-catalog-verified-20261018.md)������DSU��ר�⡢�ƻ���״̬��֤���嵥��README����һ��������Դ������߶��� GSIǩ����Կ��P780 q/r/s-GSI��������δ���ذ�װGSI ZIP��δˢ����/����/Root/������

## 2026-10-18 �� DSU Google �������Ѻ��飬����Ŀ¼����

- ������ Windows �ɹ�ȡ�� `gsi-src.json` ԭʼ�ļ���508 bytes����SHA-256 `0A1970ABFCEB6BF3962177881B255E6AF9D4F43903AAC3BA9AEF2C1E5B4A2D09`�������츽��Ҳ�����߶��ι�ϣ��ȫƥ�䡣���� P780 ��������ץ����
- ��Ŀ¼���� Google `rvc/sc/tm/udc/vic/baklava` ������Ŀ¼ `gsi-dsc.json`������û�� `images`���ʴ�ǰ���� BP1A/CPI1 �� VNDK30/��Կ�����Բ�������Ϊʵ����ۡ�AOSP DSU JSON ֧�ֵݹ� include����ѡ vndk/pubkey��Ԫ���ݱ�����ʵ����Ŀ¼��ԭʼ��ӦΪ׼��
- ��ǰ�о������޷�ֱ��ץȡ Google ��Ŀ¼�����ڱ�������������ģ�����ͨ���� Python metadata-only �����ű������ɻ����� Windows �Թ̶� Google allowlist С��Χ������ JSON��У�� SHA ���ϴ� ZIP���������� GSI ����ִ�� ADB ���д P780��
- ͬ�� [DSU ר��](docs/research/p780-dsu-locked-gsi-20261018.md)��[�о��ƻ�](docs/NEXT_STEPS.md)��֤���ܱ������ظ����л��� Treble/KeyAttestation ʵ������Root/Bootloader/�̼�����д��״̬���ޱ仯��

## 2026-10-18 �� ������ DSU Treble/VNDK ���룺��������ٷ�ǰ�ü�����

- ���� Treble Check ��ͼ��ʾ Treble��A/B��ARM64��System-as-root ֧�֣�ͬʱ��ͨ ADB `ro.treble.enabled=true`������ʱ `/linkerconfig/ld.config.txt` ����(90,115B)��`[vendor] namespace.default.isolated=true` ��ȷλ�ڵ�370�У��Ұ�����ʵ Vendor/ODM linker search paths���� `/system/etc/ld.config*` ������ֻ��·�����졣
- ���ϴ�ǰʵ�� VNDK=30��CPU=`arm64-v8a` �Ϳ��пռ䱨�棬Google �ٷ� GSI ������ָ�ϵ� Treble��Vendor ���롢ABI ����Ҫ����ȷ�ϣ������о����ģ�**�� DSU ��װ GSI �Ŀ��Ź�Կ�������� VNDK 30��HAL��ϵͳ����״̬��δȷ��**��
- AOSP �� Android15 ������µ� VNDK��ͬʱ������14�� VNDK APEX ���� Vendor ʹ�ã����ܽ�ƾ�� Android �汾���Ʋ����ݣ�Ҳ���ܼ����κ� GSI ������������һ��ת���ͼ������ GSI �� Google DSU ԭʼ JSON Ԫ���ݣ����� PC ֻ����ȡ�����ߺ˶� vndk/pubkey �ȣ���ˢ���������ش���
- [DSU ר��](docs/research/p780-dsu-locked-gsi-20261018.md)��[NEXT_STEPS](docs/NEXT_STEPS.md)��STATUS��֤���嵥ͬ���޶����ֻ��� Bootloader LOCKED��δ Root��

## 2026-10-18 �� DSU �����ֻ���Ԥ�죺VNDK30��ARM64�����ݿռ䱨�� 103G

- ��������ֻ�������DSU `.list` �������Կա�`ro.vndk.version=30`��`ro.product.cpu.abi=arm64-v8a`��`df -h /data` �� dm-11 ��106G/����3.2G/����103G/4%��Mounted on ָ�� `/storage/emulated/0/Android/obb`���������Ϊ�ù��ص���� `/data` ��������ʵ���豸�ڵ㣩��
- AOSP `DSULoader.java` �� cpu_abi ����ֵɸѡ��`os_version`/`vndk`/`spl` ֻ�� JSON �г�ʱ��ɸѡ����� DSU Loader ��ʾ����**����**�Զ�֤������ÿһ����� VNDK30��ǩ�����ջ� HAL ���ݡ��ٷ� GSI �ĵ���Ҫ����ȷ�� `ro.treble.enabled` �� vendor linker namespace isolation ��֧�ֿ� Android �汾��
- DSU ��װ���ָ��ɹ�����ǰ�ֵǼǣ����ֲ����ظ���������µ���������ʵ�⡢״̬�� NEXT_STEPS�������ֹ�������Ϊֻ�� Treble/ld.config ��ѯ��û��ѡ�� GSI�����ذ�װ/���������� locked д���õ� Root��

## 2026-10-18 �� P780 DSU �ٷ���װ����ָ��ɹ����ƽ���ֻ��������Ԥ��

- ������ʽִ�� `cmd package install-existing --user 0 com.android.dynsystem`���豸���� `Package com.android.dynsystem installed for user: 0`��`pm path` �ѻָ���ʾԭ�� `DynamicSystemInstallationService.apk`��`dumpsys` ֤�� `installed=true`���ɻָ�ǰ `false` ��Ϊ `true`����`enabled=0` ʼ��Ϊ PackageManager DEFAULT��
- ����ͨ���û�����װ�Ǽǻָ�Ԥװ��������� Root���ָ�������APK ���ػ�ˢ����`stopped=false` / `notLaunched=false` ������ DSU/GSI �Ѱ�װ������������
- ���޶� DSU ר�STATUS �� NEXT_STEPS �еľɡ�installed=false ��ǰ״̬ / δ�ָ�����������ʷȡ֤�׶α���׷�ݡ���һ�׶ν��� `settings_dynamic_system.list`��`ro.vndk.version`��ABI��`df -h /data` ֻ����飻��ѡ�н�ͼ�н��� Google GSI��Ҳ����������/��װ/������
- ���� P780 locked GSI ����ʵ֤����δȡ�� boot/vbmeta ԭʼ����Root ����֤ʵ����д��ͨ����

## 2026-10-18 �� ���� DSU Loader ���������������ָ�����

- ����ȷ�ϴ�δ������װ GSI��Ը���Ҫʱ�ָ�ԭ�������� AOSP Android 11 DSU Loader �� Settings `DSULoader.java`�����뿪����ѡ��� Settings �� HTTPS DSU JSON �б�ץȡԪ���ݲ��� ABI/OS/VNDK/SPL ɸѡ����ʾ�ĸ�Զ�̺�ѡ��**����ʾ**�����ڱ����������ء�
- AOSP Ĭ��Ŀ¼ URL `https://dl.google.com/developers/android/gsi/gsi-src.json`���� OEM ��ͨ�� `persist.sys.fflag.override.settings_dynamic_system.list` ��д��֮ǰ��ѯ�� `persist.sys.fflag.override.settings_dynamic_system` ���� `.list`�����������ֵȷ��Ŀ¼��Դ������ֻ�� getprop ���顣
- ��׼ϵͳ APK �� `/system/priv-app/DynamicSystemInstallationService`������ǰ user0 `installed=false`������ҪΪ�˵����ָ��������̨�ֻ�����װ�̼��� Root���������б�Ҫ�һ���ͬ�⣬�� `cmd package install-existing --user 0 com.android.dynsystem` �ָ�ԤװӦ�ã�δʵ��ִ�У��ݲ�ѡ��������°汾 GSI��
- ��ͬ�� [DSU ���ͺ�ֻ������](docs/research/p780-dsu-locked-gsi-20261018.md) �� NEXT_STEPS������û���µ�д��ͨ����Root �� Bootloader ����֤�ݡ�

## 2026-10-18 �� DSU ��װ���� user0 ȷ��ж�أ�Settings ����ѡ������Կ�ʹ��

- �����ύ DSU Loader �����ͼ��`Select DSU Package` ��ʾ 4 �� ARM64 GSI/GMS ѡ�BP1A.250405.005.C1 �� CPI1.251209.009.A1����֤��������ѡ��ɼ������Ͼ��� JSON Ŀ¼������ GSI �Ѱ�װ���������
- ADB ȫ���жϱջ�����ǰ�û� `0`������ pm list packages �Ҳ��� `com.android.dynsystem`��`-u -f` �б��ҵ�ϵͳԭ APK `/system/priv-app/DynamicSystemInstallationService/DynamicSystemInstallationService.apk`��`dumpsys` ��ȷ `installed=false`��**��˴�ǰ�Ʋ���û���ж���ѻ��ֱ��ʵ��ȷ��**��
- У����Ҫ�ֶΣ�`enabled=0` ��ʾ PackageManager Ĭ���������״̬������ `disabled`����������ִ�� `pm enable`����ʷ���� debloat �ű�����Ŀ���������ȷ�������������û�о���ж��ʱ������ɹ���־��
- ���� Android �ٷ� DSU Loader JSON��Settings �˵�����װ������ƣ����͡���ж�ذ�װ���񡢵� Settings ����ʾ���� GSI ѡ�������BP1A ѡ���Ӧ Google �ٷ� Android 15 QPR2 GSI������ Android 11 vendor ��ʵ�����м���δ֪���б���ɸѡ������ǰ�ȫ��ŵ��
- �ѽ� `install-existing --user 0` ��Ϊ**��������ͬ���ִ��**��ϵͳ���ָ�ѡ��д�뱨�漰 NEXT_STEPS��û�а�װ�����ػ��޸��豸���ֿ�ԭ�� `.p7b` �� DSU ��ͼ��δ�ϴ���

## 2026-10-18 �� ʵ�� DSU Loader ���ȷ�ϣ����ݷ��־���ű�������װ��

- �������濪����ѡ����ʵ���� DSU Loader��`pm list packages -u` ���� `com.android.dynsystem`��`gsid.rc` 590B �ļ���ʵ���ڣ�`/metadata/gsi` Ȩ�޾ܾ������������������˽��**�Ʒ�**��ǰ������û�� DSU Loader ��ڡ��ı���������δ֤������ʵ�����ذ�װ GSI��
- �ٷ� ADB �ĵ����� `-u` �б���ж�ذ���ԭ�� `pm path com.android.dynsystem` �����������һ������ user0 `installed=` ״̬���»ز���ʷ���� P780 ADB Ӧ�þ���ű����� `com.android.dynsystem` Ϊж��Ŀ�꣬�� phase3 ��װ�嵥���������ʷִ�гɹ����**����֤��**��ֻ�ܵǼ�Ϊ����֤���û���ж�ؼ�˵��
- AOSP `gsid.rc` Ϊ `/metadata/gsi` ���� root:system `0771`����ͨ `shell` Permission denied �Ǻ���Ȩ�����ƣ����� Root�������ܴӾܾ������жϷ�����ʹ�á�
- �Ѹ��� [DSU/GSI ר��](docs/research/p780-dsu-locked-gsi-20261018.md)��STATUS��NEXT_STEPS��EVIDENCE_MANIFEST����һ������ user0 ������״̬��ֻ�����`install-existing` �������ȷͬ�⣬δִ���κλָ�/��װ/�豸������

## 2026-10-18 �� DSU/GSI ��һ��ʵ��ֻ���Ų�� AOSP ���¹���

- �������β�ѯ��׼ `com.android.dynsystem` ��װ����δ����·������`gsi_tool`��������Ϊ 47,016B����`gsid`��Permission denied����������� getprop�����գ������� `/avb` GSI ��Կ����ͨϵͳ·�������ڣ���û�н����κΰ�װ/����/����д�롣
- AOSP Android 11 `gsid.rc` �� GSID ��Ϊ `disabled`/`oneshot`�������ɿ��������Զ������ȱʧ��Android 11 �׽׶� Ramdisk �����������и�����ͷţ����ܸ��� shell Ŀǰ�Ҳ��� `/avb/*` ���� fstab ����������ѡԿ�ס�
- �ֽ� DSU ���ĵ���Ϊ���ײ㹤��ʵ�����ڣ���׼ Loader û�гɹ������������û�������**δ֪**��ֻʣһС��ֻ���˶԰��� `gsid.rc` �ļ�ֵ�������޶�����װ���򿪷���ѡ����ڣ����� DSU ֧�ߣ������̼�/�޸�ͨ������ϡ�
- �½���Ѱ� [DSU �о�����](docs/research/p780-dsu-locked-gsi-20261018.md) ����ʵ����󣬸��� STATUS/NEXT_STEPS/EVIDENCE_MANIFEST��δ�� DSU ���� Bootloader ������ Root �ɹ���

## 2026-10-18 �� DSU/GSI ����̬�ٷ�����������ͨ·�Ŀ������о�

- ����ʵ��ȷ�� AVB Ĭ�� RSA4096 ���Ը���Կ�󣬶���ȱԭ������locked д����������ϵ����������������ظ���ͨ AVB/Key Attestation/OTA �ɼ���
- AOSP �ٷ� Android 11 DSU �ĵ�ָ�������̿�Ԥ�� Developer GSI ��Կ������ Bootloader ���� LOCKED ʱ��ʱ����������֤�� GSI��`fs_mgr_fstab.cpp` �� `BuildGsiSystemFstabEntry()` ʹ���� P780 ���� fstab ��ȫһ�µ� `/avb/q-gsi...:/avb/r-gsi...:/avb/s-gsi...` ·����
- P780 ����ʵ�� Android 11����̬������F2FS `/data`��`/metadata` �׽׶ι��ؼ� dm-verity �� DSU ����Ҫ�����ݣ���**��δȷ��** DSU ǰ��/���񡢹�Կ�ļ�����ʱ�ɷ��ʡ����� HAL ��ǩ�� GSI ʵ�ʿ�������**û�а�װ�����ı��ֻ�״̬**�������ƶ� Root / BL ���� / ��������д�롣
- ���� [LOCKED DSU/GSI ר���о�](docs/research/p780-dsu-locked-gsi-20261018.md) �봿��ѯ���AOSP `gsi_tool status` �ڲ��ְ汾�ᰴ������ `gsid`������״ν������ȡ app/������/����/·������ִ�а�װ�����á��رջ� setprop��
- ��ԭ `docs/NEXT_STEPS.md` ��ʷ���ݹ鵵�� [2026-10-18 ����](docs/archive/next-steps-before-dsu-20261018.md)����дΪ�����ִ�мƻ����Ƴ��Գ�Ӳ��֤����δ���ԡ��ȹ�ʱ/�ظ����ۣ�ͬ�� STATUS��README���ĵ������� Fstab ר�⡣�ٷ������е�����Կ�뱻����д��������Ƕ��������������� LOCKED��δ Root��

## 2026-10-18 �� P780 Ӳ��֤����ȷȷ�� AOSP AVB RSA4096 Ĭ�ϲ�����Կ���ؼ�ͻ�ƣ�

- ��������ʵ P780 `_162` ͨ�� KeyAttestation ���� 3475B `.p7b`���ڶ������� Python �������� 4 �� X.509 ֤��� Key Attestation v3 ��չ��Google 2019 Ӳ��֤�� Root DER �ֽ���ȫ��ͬ��Root ��ǩ�� Root��CA1��CA2��Leaf ����ǩ����֤ͨ����TEE �� Keymaster ��ȫ����� TrustedEnvironment�����ߵ���״̬��δ������������У�顣
- ȡ�� `deviceLocked=true`��`verifiedBootState=Verified`��`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2`�����ǰ ADB VBMeta Digest **���ֽ�һ��**��
- **����Ҫ����**��`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`����ȫ���� AOSP RSA4096 `testkey_rsa4096_pub.pem` ʹ�ùٷ� `avbtool.py` RSAKey �������ɵ� **1032 �ֽ� AVB ��Կ blob �� SHA-256**��SPKI DER��PKCS1 DER ��ģ����ʽ��ϣ������ͬ����ȷ����ȷ����ͱ�������Կ���ݡ�
- �½� [������֤����](docs/research/avb-attestation-confirmed-20261018.md)��ͬ�� README��STATUS��NEXT_STEPS��֤���嵥�����ڼ�˵ר�⡣û�н��豸֤��ԭ���ϴ� Git��**û�� Root����������֤ʵ P780 locked д������**����������ԭ�� VBMeta/chain descriptors/rollback index ������ʵ֤�ݵ�д���ֶΡ�

## 2026-10-18 �� ��ͣ OTA���۽�Ӳ�� Key Attestation��ʵ�����⣩

- ������ Google OTA ̽��֧���ݻ����о�ת������ԭ���̼��� OEM �ظ��� Android Keystore `RootOfTrust`��
- �˲� Android �ٷ� Keystore/Key Attestation��Google ASN.1 `RootOfTrust`��Trusty Keymaster ʵ�ּ���Դ KeyAttestation app v1.8.4 ��Ĭ����Ϊ��APP �����Զ�����ͨ KeyStore ֤�������ص� `verifiedBootKey` Ϊʮ�����ƣ�`verifiedBootHash` ��ȱʧ��
- �����ؼ��������ƣ�Bootloader ��ֱ���ṩ ��32 �ֽڹ�ԿժҪ��Keymaster ��ԭ��ת�����ṩԭʼ key >32 �ֽڲ��� Keymaster SHA-256����˲���Ԥ�� attested hash ���κε�һ��ʽ�� AOSP AVB ��Կ blob ��ϣֱ����ȡ�
- �ѽ���С��Ҫ�ɼ��ֶΡ�֤�����θ�/���������ա���ʱ�����б�����˽�߽�����о�ר��� NEXT_STEPS������ P780 Ӳ��֤��ʵ�⣬Root/BL ״̬���䡣

## 2026-10-18 �� �����ⲿ AI �� P780 OTA �� AVB ǩ������

- ����������ʵ CLI�����������ڵ� `--device`��source/target fingerprint ������ `devices.json` �ļ����񶨺�����Դ�� `264��151/120` �ַ�����д��Ϊ�ɹ���֤�ݡ�
- AOSP �ٷ� `signapk` �� APK/OTA ZIP ǩ������ AVB ǩ����AVB ʹ�� `avbtool`/libavb��Magisk + signapk �����Զ�ʵ�� locked P780 ǿˢ��
- AOSP payload Full/Delta ���־��������ܷ����������ָ�����ν Google ����ֱ���̶���Сʱ���ڻ��ڱ����ɰ���ȱ�� P780 ֤�ݡ�
- �����S������ 2024-07-31 ��ʵ `_161` �յ� `_162` OTA ��ʾ����װʧ�ܵ���ʷ���ϣ���ȱ�ɰ����� fingerprint��OTA URL �ͷַ����������ݡ�
- ͬ�� [Google OTA Prober �˶�ר��](docs/research/google-ota-prober-p780-20261018.md) �� NEXT_STEPS���豸�޸Ķ���Root/BL ���³ɹ�֤�ݡ�

## 2026-10-18 �� P780 Google OTA ������ URL / ʵ�� Fstab ���η���ȷ��

- ������ Windows ִ�� `python probe.py --fingerprint "Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys" --model P780`�����򷵻� `No OTA URL found for your build`���� HTTP ״̬���� Google OTA URL������ `_162` �����µĵ��θ����ѯ����֤ʵ P780 ��ʹ�� Google OTA�����ٶ���ͬ fingerprint �ظ���ѯ��
- ����ͨ�� ADB **ʵ�ʶ�ȡ����Ϊ���츽���ύ** `fstab.default` �� `fstab.emmc` ȫ�ġ������ļ��� `system/system_ext/product` ������ `avb=vbmeta_system`���� `vendor/odm` ������ͨ `avb`����������� vbmeta ������ dm-verity �������ݣ����Բ��� Bootloader chain descriptor ԭ����
- ���ⷢ�� `/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey` ֻ�� `system` �� `avb_keys` ѡ���г��֡�AOSP fs_mgr ������֤���� GSI ��Կ��ʧ�ܺ����Ĭ�� AVB �Ĵ���·���Ѻ˶ԣ�**���ܽ� GSI ��Կ����������ǩ����Կ���ֳɽ���·��**��
- ���� [Fstab AVB ר��](docs/research/p780-fstab-avb-20261018.md)���޶�ԭ�ȡ���δ��ȡ Fstab / ��δ��ѯ P780���Ĺ�ʱ״̬������ Google OTA ר�⡢AVB ȡ֤�ƻ���STATUS��֤��������README ���ĵ�������������Դ�ȼ����Ựԭʼ����� Git ��ԭʼ�ļ������ƣ��豸�� locked��δ Root����ԭ������


## 2026-10-18 �� P780 Google OTA Prober Դ��������ͬ OEM ��������֤

- �����ṩ `Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys` ���� fingerprint��ADB �г� `/vendor/etc/fstab.default`��`fstab.emmc`��`fstab.qcom` �����ڡ���Ϊֻ��ǰ����ʵ���ļ�����ͣ���賧�� fstab ���ơ�
- ���� [tangalbert919/google-ota-prober](https://github.com/tangalbert919/google-ota-prober) `README/probe.py/config.yml/utils`��ͨ�� Google `android.googleapis.com/checkin` �� `fetchSystemUpdates=1` �� OTA URL��ֻ�в��� Google OTA �������Ļ��Ͳ����ã�������ͨ�ó��� OTA ����������Ҳ���ͨ����ǰ���հ� `_162` �Ĳ�ѯ�޽���ų���ʷ Google OTA��
- ���� [mouseos OTA Archive](https://github.com/mouseos/ota-archive) �� Rakuten/Tinno C330 (Rakuten Mini) �ٷ� Google OTA ��ʷ 530��620��620��830��TINNO P710 ���� fingerprint ���� OTA��δ���� P780 ��Ŀ����**��δʵ��������ģ�ⷢ�� P780 Check-in ����**�����ܽ� C330/P710 ��Ϊ P780 ����
- ���� [Google OTA Prober �� P780 ר��](docs/research/google-ota-prober-p780-20261018.md)������ README��STATUS��NEXT_STEPS���̼�ר�⡢֤���嵥�뵼����ֻ����ȡ�ÿ��� P780 OTA URL ʱ�Ž�һ�����ߺ˶� `pre-build`/`post-build`��������ԭ�������ϵ��δ��װ�̼���δ������δ Root��


## 2026-10-18 �� �� AVB / TEE / Keystore / CTS ������ȡ֤���

- ������Ҫ������� `green/locked`��`ro.boot.vbmeta.digest`�����豸 `0600 root`��TEE/Keymaster �Լ�˫�� VBMeta ��Ϣ���н��������
- AOSP Key Attestation `RootOfTrust.verifiedBootKey` �ɰ����������ι�Կ��ϣ��`verifiedBootHash` �ɰ��� VBMeta Digest��Android CTS Դ����� `verifiedBootHash` �� `ro.boot.vbmeta.digest`���������ԭ������Root ����ͨ Keystore ֤���о�·����**P780 ��δ���У��������ܳɹ�**��
- �˶Թ�����Դ KeyAttestation Ӧ�ã�vvb2060���ٷ� latest v1.8.4��minSdk 24��Դ�� Manifest �� INTERNET ���󣩣�����Ϊ������ѡ������װ���飬���Զ���װ����Ҫ�� Shizuku ���豸��ʶ���ݣ�Ӳ��֤��������֤ǩ������TEE ����͵�����Ϣ����˽֤��������ֱ�ӹ�����
- AOSP fstab ���� `avb=vbmeta_system` ȷ���߼������ĵ�һ�׶ι���Ŀ�꣬������ѡֻ���˲飻AOSP Ĭ�� RSA4096 ����Կ�׳�Ϊ�г����ĺ�ѡ���Բ���ֱ���϶� P780 ʹ�ø���Կ��
- ���� [AVB �޾������·��ר��](docs/research/avb-attestation-alternative-20261018.md)��ͬ�� README��STATUS��NEXT_STEPS��δ�������á���ȡ root-only ԭʼ���豸��Ķ��ֻ���Root/BL ״̬���䡣

## 2026-10-18 �� AVB �о���Դ�������

- �����ж��ظ��ʼ���ѯ�����ƽ������� TINNO Դ���ʼ����޿��óɹ���**ֹͣ�� JVN/����/�о���������ѯ��Ϊ��Ҫ����**��JV N �����Ų��䣬��ϵ��Ϣ������ʷ��¼��������ԭ�ʼ������ȴ��Ϳɺ���ظ������������߰��ʼ���
- �Թ����� CVE-2026-107153 �������ϡ�P780 VBMeta����Կ֤�ݼ��̼������ټ�������δȡ�� P780 ר�� PoC�������ɸ�����Կָ�ơ����ƶϲ�����˽���о������
- �������������ڲ������ʼ��ظ��Ĺ���ԭ�������߱ȶԣ�ȱ�ٱ��� vbmeta / locked д��ͨ���ĸ�����ϲ��䣻�����豸��չ�߷��ղ��ԡ�


## 2026-10-18 �� �̼�ϡȱ�µ� AVB �ֽ׶��о�����

- û�пɿ�ȡ��ƥ�� `_162` ������ OTA���������ٰ������̼���Ϊ**̽���Բ�����Կʶ��**��Ψһǰ�ᣬ����Ѱ�Ҹ���Դ���汾�͹�ϣ������ P780 �汾 `vbmeta*.img`������ AVB ��Կָ������С�ɺ����ǩ���������
- ǿ�� **���ͼ�̽�� �� ���� `_162` ��ȷƥ��**�������汾������ Rakuten/ͬ SoC �豸����ֱ�Ӵ��汾������Root/Bootloader/EDL ·��״̬���䡣
- JVN �ѹ�������©����������ԭ���ѣ�[JVN �ٷ���ϵҳ](https://jvn.jp/contact/) �ṩ `jvn@jvn.jp`��ֻ�ǿɿ��ǵĹ�����Ϣ��ѯ��ڣ�**δ�����ʼ�**��Ҳ��Ԥ�豨���߳��пɷ��� PoC ��̼���
- ͬ�� AVB ר���� NEXT_STEPS����������Ի���������Ч���ظ� getprop/�̼��ؼ��ʲɼ���

## 2026-10-18 �� P780 ʵ�� AVB Green/Locked ������ֻ���о�·��

- �û��ṩ�� ADB �����`green`��`locked`��`flash.locked=1`����� `_b` �� VBMeta digest `33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2`����Ϊ�û��ṩʵ��֤�ݣ��зǶ����ز������ȡ��
- ���� [AVB ����ר��](docs/research/avb-live-baseline-20261018.md) �� [Windows ADB ֻ��ȡ֤�ű�](tools/p780-avb-readonly.ps1)������ Android 11 �ٷ� avbtool ����ʽ VBMeta digest ���塢NCC Group ���Թ�Կʶ�𹤾ߣ���ȷֻƾ digest �޷����Ƴ�ǩ��Կ�ס�
- ͬ�� README��STATUS��NEXT_STEPS��ר������������˵���빫��ר�⡣��ȱ `_162` ԭ�� `vbmeta/boot`������֤�� locked д��ͨ����δִ��ˢ���� Root��
- ���ʱ GitHub API ���� visibility=public���ͼ��� Private �İ�������SECURITY/README ����ʾ����ԭ�����գ������ȷ�����ò���� Git ��ʷ��

## 2026-10-18 �� �ڶ��� AVB ֻ��ȡ֤��ֿ�Ȩ�޸���

- �û����� `ro.boot.vbmeta.hash_alg=sha256`��`ro.boot.vbmeta.size=7744`��`ro.boot.avb_version=1.1`���Լ� `vbmeta_b��sde31` / `vbmeta_system_b��sda11` �� A/B ����ӳ�䡣AOSP ʵ��ȷ�� `size` Ϊ���������� VBMeta �ṹ�ܳ��ȡ�
- ��ȷ `vbmeta_system_b` ����ʽ���ֵ�ǿ��ѡ����ʵ��ǩ������������ȷ�����ݣ�����ȱԭ�� `_162` ���񡢹�Կָ�Ƽ�����֤д��ͨ����
- ���� AVB ר�⡢STATUS��NEXT_STEPS��README �� PowerShell �ɼ��ű���������ѡ��ԿժҪ���ԡ�mapper �����Ӽ�Ȩ��ֻ���鿴����δʵʩ Root ��ˢд��
- �������ֿ���� Private��GitHub API ���� `visibility=private`��SECURITY/README ͬ��������������ǰ Public ״̬��Ǳ�ڱ�¶˵����

## 2026-10-18 �� AVB �����֣��汾��dm-verity��root-only ������ COW

- ���� ADB ֤ʵ����ԿժҪ����Ϊ�ա�`ro.boot.vbmeta.avb_version=1.0`��Bootloader libavb����`ro.boot.avb_version=1.1`��Android fs_mgr libavb����`ro.boot.veritymode=enforcing`��AOSP VINTF ����˵���汾���첢���쳣��
- `/dev/block/sde31`��`/dev/block/sda11` Ȩ�� `brw------- root root`���� root Shell ֻ���г�������ֱ����ȡ�� VBMeta ���ݡ���� B ���߼����� dm-0..4��`system_b-cow` dm-5����� dm-verity dm-6..10 ��ԭ����¼��COW ��Ϊ OTA ���պ�ѡ����д��� Root �ɹ���
- ͬ�� AVB ר�⡢STATUS��NEXT_STEPS��README��֤�������� PowerShell ֻ��ȡ֤���ߣ��¹��߲��� Virtual A/B �� VBMeta device �Ŀ�ѡ���Բ�ѯ���豸��ˢ�����вۣ������������ `_162` ԭ�� AVB ����������̬д��;����

## 2026-10-18 �� AVB �����֣���̬����ȷ�ϡ�����ȡ֤����

- �û�ʵ����`ro.boot.dynamic_partitions=true`��`ro.virtual_ab.enabled`��`ro.virtual_ab.compression.enabled`��`ro.boot.vbmeta.device` ��Ϊ�ա���̬������ȷ֤��Virtual A/B �;��������������Կն����ȷ�ϻ���ϡ�
- AOSP �ĵ���Android 11 Virtual A/B ʹ�� kernel COW��Android 12 ����ѹ�����գ�`system_b-cow` ��ֻ�к�ѡ֤�ݵȼ���δ���������������л���ֿ�����д��·����
- ���� AVB ר�⡢STATUS��NEXT_STEPS���̼�/OTA ר�⡢README �� EVIDENCE_MANIFEST����ʽ��ͣ��ͨ ADB getprop �ظ��ɼ�������ת����� `_162` OTA/����AVB ��Կ�� Descriptor �����߱ȶԣ��Լ� P780 ����̬д����ƿɺ�����Դ��
- ��������δȡ��ƥ�� `_162` �Ŀ��ž��񹤼����������е� XDA �̼�����������δ��ȡ��������ҳ�򸽼�����ð�����ҵ��̼������豸�޸ģ�Root/BL ״̬���䡣

## 2026-10-17 �� XDA ���Ĳ����� Recovery ��ǩ�߽�

- ԭ�������û��ṩ�� XDA 4805241 ���ģ���ע��Դ����δ��������״̬���ر�ͬһ�����˹���ȡ���ѣ����������ʼ���ʷ��
- ���� OTA ZIP ֤���� AVB ����Կ�ף���ǩ��ʧ���޶�Ϊ�ð�/�ôβ��Խ������¼ whole-file ǩ�������ṹ����Կ��������־ȱ�ڡ�
- ͬ�� README��STATUS��NEXT_STEPS��֤���嵥������ר�⣻OPG105 ��Ϊδ��֤������fastboot boot δ�гɹ�֤�ݣ�EDL ������֤ʵΨһͨ����
- ��������ԭ��������ɺ���д��ͨ����δʵʩʵ��ʵ�飬Root/BL ״̬���䡣

## 2026-10-15 �� JVN/CVE ���������뵵

- �鵵 2026-10-14 ������ JVN#47427200��JVNDB-2026-000147��CVE-2026-107153 �� Rakuten ԭ���棺ȷ�� Rakuten Hand 5G ȫ�汾�� AVB ʹ����֪ AOSP ����Կ�ס�
- ���� JVN ���õ� AVBTestKeyInTheWild ���ģ���¼�޸ġ���ǩ���ؽ� vbmeta���豸�ض������Ľ׶Σ���ȷ������ʾ���Ͳ��� P780�������д�뷽��������Ϊ����֤�ݡ�
- ͬ���޶� README��STATUS��NEXT_STEPS���̼�/OTA �Ͷ�����ȫ����ר�⣻�Ѻ����ؿ�����Ϊ `_162` ԭ�� boot/vbmeta ֤���� P780 ����̬д��ͨ����
- ����ֻ���������Ϻ˶����ĵ�ά����û������©��������ִ�в����ų����ˢд�豸��������δ Root��δ������Firehose �� `_162` ԭ����������ȱ��

## 2026-10-11 �� ȫ��ṹ������������

- ����ö�� main �� 254 ���ļ���������ǰ�̶��ύΪ��׼������ָ���֧ archive/pre-restructure-20261011��
- �ĵ�������ר��/��Դ�淶/�׶���ʷ�ֲ㣻����ԭ����λ evidence/device������ʧ�ܲ���֤�ݹ�λ run 38060293186��ԭʼ Blob SHA ���ֲ��䡣
- ɾ��������չ����ͬ���ֽ���ͬ�� critical-delta.txt������ critical-delta.md�������������ظ�֤�ݱ�����Դ�����ġ�
- ��д README���ĵ�/֤��/���ߵ�������죬����ʱ���ߡ���ʷ���������ĺ͵�ǰԭ��Ǩ��״̬��ȫ���޸�������Ӽ�����������·����
- ��ѡ��������ʷ�����Ϊ�ֶ��������Զ��鵵��鱣�������� Journey ����ԭ����ÿ��������������Ϊ��ǰ GitHub ���ߣ�����ʵ��������֪ͨ��ͬ����
- ʵ�ʽṹ�ύ�� Actions #38069160978 ȫ��ͨ����258 �ļ���48 Markdown��337 �����·������/0 ʧЧ��10 Python/35 JSON��25 Ǩ�� Blob ���ݼ�ԭ��/��ͼ/�ֽڹ�ϣ���ͨ����
- �����ǵ���������δ��ȡ Root/����/ƥ��ԭ��������� docs/REPOSITORY_AUDIT.md��

## 2026-10-10 �� Journey ��������ƥ������˶�

- ��ȡ���ܷ����ڲ��� 134 ���д��뷽��������֮�� 79 ������/25 �������߷��������淴��ࡢ���������ġ�6 �����߷�����ԭʼ�ֽڼ��� DEX SHA��
- ��λ OOM/���������뱣����Service/Provider �������ж�����ʵĩβ�Ǻ�ǰ׺ƥ���뾫ȷ����ѯ��ͬ��RootProcess ΪӦ�������̸��
- ���� DEX �������������ʱ����������ԭʼ DEX ����ָ���ȡ��54 ���������÷�����ƫ��/�ֽڽ������ͨ����ȫ����ɨ�跽��ָ��ȼ��ͨ����
- �ϲ��������� Journey ר�⡢��ҳ��STATUS��NEXT_STEPS��֤���嵥��δ��ʵ����Ϊʵ�飬δ�����µ� OTA/Root/������ڡ��ݻ������֧�ߣ�����ϵͳ������ʵ�Է��ּ������ơ�


## 2026-10-10 �� Journey ʵ�����ú˶����

- У����� 3,940 B ���� ZIP������ɻ�ԭȫ��ԭʼ�ֽڵ� Base64������ SHA��vendor XML/version �� TCS �Ķ���ͼ��
- XML��version.txt�����а汾�� 42��39 �� XML ���� ALL ����õ� 64 �����Լ�����ʵ�� dump ��ȫ���ֶ���ȫһ�¡�
- ��ʵ panda��qqdownloader �ظ������ǣ����Ѳ�����Ŀ����Ϊ��װ/ϵͳȨ�ޣ�������Դ�Բ����ų�ͬ���ݻ��档
- ͳһ�޶����� Journey ���桢README��STATUS��NEXT_STEPS ��֤���嵥����һ�׶�תΪ����������׷�ټ�ƥ��ԭ���̼�֤�ݣ�Root/BL �ɹ����䡣


## 2026-10-10 OTA ��ʵ�� framework �������

��ͬ�� OTA ����/֤�ݣ�6 ��������־��Ϊ����������δ�õ��̼����������� JAR �� 54 �� Journey ����ԭʼ�ֽڡ�8 �෴��ࡢ17 ���ⲿ���������� SHA����λӦ����Ϊ XML �� JourneyPerformanceService��δ֤ʵ OTA/Root ����ͳһ�޶� README��STATUS��NEXT_STEPS��OTA ��֤����������¼�׶�ͬ��ά��Լ����ԭʼ 18MB framework ZIP/JAR ��δǨ�� Git�������ϴ���Դ��


## 2026-10-10 �� �����о��������������ѡ�ṹ����

- ����ɨ�� 24 ����ʧ���ŵ� Kconfig/C/H/S/Makefile ���ã����ñ���ԭʼ���ú� provenance��
- ���� FORTIFY_SOURCE �� Clang �������ơ�REFCOUNT_FULL ��ʵ���滻�����ɴ� NFC �˵���δ�����ù��������ǵ����á�
- ���Ӻ�ѡ�ṹ̽��� Kbuild ���������ȡ���̣��̶�����Դ���� Android Clang11������ÿ�ֳɹ���ʧ�ܹ�����
- ���� TINNO �����ű�ȱִ��Ȩ���Ѽ�¼���޸���̽�� TASK_SIZE �������ں˺��ͻ�Ѹ��������� 32 �������Լ�飻����ǰ���ֽ������ð���������֡�
- ���� [#38060518994](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38060518994) ȫ��ͨ�������ù̶����� 32 ��������ȡ��0 ����죻���ñ���ȫ��ԭʼ������
- ר�⣺[�����벼���о�](docs/research/config-layout.md)����ѡ���ֲ�����ԭ�������ƣ�δʵ�� Root/BL ������


## 2026-10-10 �� ��һ��ԭʼ�豸���Ϲ鵵��ȥ��

- ���յ� 2 �� ADB ��Ƽ�����ѹ���������� Bugreport������ APK������ OTA ��־��TEE �������� JNI ����·����¼��phase3 ���嵥��
- GitHub Actions У��֤ʵ��`hand5g_debloat_audit.zip` ��Ӧչ���� 22 ���ļ���`hand5g_final_audit.zip` ��Ӧչ���� 9 ���ļ�**���ֽ���ͬ**��ɾ�� 31 ���ظ�չ���ļ����ܼ� 7,576,640 B���������� ZIP �������ָ���֧��
- ��ԭ��������֯Ϊ `evidence/restricted/`��`evidence/apk/`��`evidence/tee/`�����������ݷ��յ�ϵͳ��־���ٶѷŸ�Ŀ¼�����ݷ�֧ [archive/pre-cleanup-20261010](https://github.com/Chuniex-0631/p780-kernel-research/tree/archive/pre-cleanup-20261010) ����������ǰ�����ļ���
- ���վ��ļ��嵥���ر�������ʷ 1,742 B �ͱ��� 376,662 B ��ͬ����� ZIP����������Ϊͬһ���ֽ�ԭ����
- ���� [�ļ�ȥ�ر���](docs/archive/20261010-import-dedup.md)��[TEE/APK ����](docs/research/tee-system-apks.md) �� [OTA/Bugreport ����](docs/research/ota-bugreport.md)�������� README��״̬����ʱ���ߡ��̼���Ӧ������ר�⡣
- �������Ϊֻ�������о�����ά����û��ʵ�� Root/BL �������ȡ���� OTA ���³ɹ�֤�ݡ�


## 2026-10-10 �� ���շ�����գ��� GitHub ʵ�ʺ˲飩

- �������ϴ��� **4 �� GhostLock �о� ZIP** �� **4,096 B �� Tracefs ԭʼ�ļ�**�Ѿ�ȫ����֣�����Դ����;�ƶ��� `evidence/ghostlock/` �� `evidence/device/`��ʹ�� Git ���� Blob �����ֽڲ��䡣
- �½� [�����Ա���](docs/reference/evidence-integrity.md)��Actions [#38055450831](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055450831)��[#38055530285](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055530285) ��֤ѹ���� CRC��SHA-256��ZIP �ڲ� `CHECKSUMS.sha256`���İ���Ƕ�豸֤������ԭ�����ֽ�һ���ԡ�
- �ĸ� ZIP �ֱ���� **13 / 16 / 17 / 27** ���ļ���v0.4 ԭʼ README ���д����� v0.3������ʵ�� [�汾����](docs/archive/ghostlock-package-versions.md) ��ǣ����޸�ԭ����
- ���� README��GhostLock��Next Steps���ļ��嵥����ʷʱ����������ĵ��С�ԭ����δ�ϴ����ľ���������д�ֿ���ҳ����ȷ�о������δ������
- ��ʱ��δǨ��Ĳ�������**���һ�������ϴ�**�в��ֲ��루Bugreport������ APK��OTA/ADB ��־����������������嵥������ԭ����δ��ɷ������������������־�Ϸ��ĺ���������¼��
- �ѷ��� [�������ձ���](docs/archive/20261010-archive-review.md) ��ȫ��˫��֤������������Ϊ**��������**��û����ʵ�������©����ˢ��̼������ Root ����� Bootloader��


## 2026-10-10 �� �״���������

- ������ **2026-06-12 EDL / Fastboot ��¼**���ָ����鵵ϵͳ�汾��Sahara��Bootloader��A/B ��������ʷʧ����Ϣ��
- �� 2026-10-03��04 ���ļ����ָ� **QAS/PFM/Mink/TZAccessService** ���������������豸�����ű�/ժҪ��
- �鵵�ɰ� **GhostLock v0.1�Cv0.4** ���ʲ��嵥��ʵ�� Kernel Config��Tracefs ȡ֤���ۺ�ֻ���˶Թ��ߣ��˳��ڼ�¼�ں��������շ�����ա��׶��Ѳ�ȫȫ���ķ� ZIP ԭ����
- ���� **2026-10-10** Qualcomm 5.4.233 ��ѡԴ���ԭ�� Kconfig��Android Clang11.0.2/14 ������̣��Լ���ʵ�� `rtmutex.o`��
- �� GitHub Actions ԭʼ����תΪ `evidence/actions/` �¿ɳ��ô洢�� Git �ļ������� CI �������ڵ��µ����϶�ʧ��
- �����豸���ߡ����Ŷȱ���ʱ���ߡ��ٷ� OTA/��ȫ���桢��˽���������嵥�͵�ǰ���������
- ��ȷ˵����**�豸�� locked��Root/BL ������δ���**��ԭ�� `_162` ������ʵ��ƥ��� `vmlinux` δȡ�á�


## δ��ÿ��ά��Ҫ��

��ʵ�������ͬ�����£�`docs/STATUS.md` �� ��Ӧר�ⱨ�� �� `docs/EVIDENCE_MANIFEST.md` �� ���ļ���

δ�����˵Ľ��ֻ���롰����/����֤�������ܸ���Ϊ���ɹ���״̬������ GitHub Actions ����Ҫ�������б�š�Դ�� commit���������汾����־����Ҫ����Ӧ�鵵�� Git ��ʷ��



## 2026-10-11 �� �ٷ�Դ������

- �� TINNO ���������������䷢�� P780 `_162` / 5.4.233 Դ���Ӧ��ϵ���룬��Ҫ��ת����Դ�Ϲ沿�ţ�Rakuten Mobile ���޿ɿ�����Դ��ר�����䣬�ѱ�����ٷ��ͷ��ĸ嵫δ�ύ���� `docs/official-source-request-log.md`��

