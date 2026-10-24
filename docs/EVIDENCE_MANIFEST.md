## 2026-10-24：IPsec/UDP v0.3 构建证据（未实机运行）

- 源码与构建工作流：`tools/ipsec-preflight-android/` 与 `.github/workflows/p780-ipsec-preflight.yml`；版本 `0.3.0`。
- APK 构建：[run 40081265263](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/40080355011)，artifact ID `12555411610`，ZIP digest `sha256:5cb93cc46acddaa3ed9be17381784b0974da61e044bcd1bf620e8f66ef5c0ea7`。
- 仓库审计：[run 40081265231](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/40080355002)，success。
- 新增 native 诊断只通过一次 `sendfile()` 将应用私有临时文件发送到 `127.0.0.1` UDP socket，接收后比对，并验证源文件内容未变化后删除。
- **此记录仅为源码与 CI 构建证据。v0.3 尚未安装/运行；没有 v0.3 设备输出。** 不得将 v0.2 的 PASS 复制为 v0.3 结果。
- 解释与限制见 [v0.3 预检报告](research/p780-dirtyfrag-v03-sendfile-probe-20261024.md)。

## 2026-10-24：IPsec v0.2 实机回环证据登记

- 源码：`tools/ipsec-preflight-android/`，功能提交 `1bf4848b3571b20f07704f3d755091335d490ed5`。
- 构建：GitHub Actions run [40077884020](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/40077884020)，artifact `p780-ipsec-preflight-debug-apk`（ID `12554320232`）。
- 实机记录：`docs/research/p780-ipsec-v0.2-live-loopback-20261024.md`，包含机主环境结果、资源创建/释放、UDP/ESP loopback PASS 及非提权 `dumpsys ipsec` 结果。
- 分析：`docs/research/p780-dirtyfrag-v02-path-interpretation-20261024.md`。v0.2 证明正常公开 API 保护回环，不证明文件支持 UDP sendpage、共享页 ESP 解密、DirtyFrag 或 Root。
- 证据来源是仓库源码/CI 元数据及实机报告记录；设备 UI 输出由机主提供，`dumpsys` 由普通 shell 读取。没有 Root、内核 trace 或分区写入证据。

> 2026-10-20：新增 evidence/gaps/20261020/header-verification.json 与 tools/gaps/verify_policy_header.py；原件哈希匹配，header 直接重读。原始两份 policy 继续留 PC，未上传。 [详情](research/p780-policy-header-verification-20261020.md)

# ֤���ʲ��뱣��״̬

���£�2026-10-19����ҳ���ʲ���֯�����ٽ�ÿ�֡����⡱�ƻ����ʲ��ظ�׷�ӡ���ǰ�������ۼ� [STATUS](STATUS.md)���������ļ�������Դ��С���׶�ժҪ������[�������ʷ�˱�](archive/evidence-ledger-before-consolidation-20261018.md)��

## NATIVE-01 ����ʵ�������߽���֤�ݣ�2026-10-19��

[����](research/p780-native-live-endpoints-20261019.md)��[�۲�ժҪ](../evidence/native/20261019/observations.json)��[������SHA�嵥](../evidence/native/20261019/input-manifest.json)��[16����ԭʼ�ֽڼ������](../evidence/native/20261019/diag-methods.json)��[17��������](../evidence/native/20261019/diag-declarations.json)��[manifest](../evidence/native/20261019/diag-manifest.xml)��[ELF/CFI/PLT֤��](../evidence/native/20261019/diag-elf.json)���޶�����/����/������־����Git�������ֻ������ֽ���PC��ʷһ�£�ԭʼAPK/JAR/SO��PC��û��ȫ��getprop���豸���кŻ�˽��Ӧ����־��֡�DEX/ELF����SHA��ָ��ǡ��Ķ�JSON/Python��·�����������֤�����������̼���ǰ�ڴ���ơ������ܹ��߼�[native˵��](../tools/native/README.md)��

## GAP-01 ���в������ں�/���ļ���ȱ��2026-10-19��

�ɹ���������policy��881104B��SHA a4d6851e984a0232dea7cbabbf600f87eeb74b94005a260ecbbca756bcad1409������ǰconfig.gzƥ��10��10�չ鵵��journey.factory.rc����ʵ��ȷ��Ϊ0B��**ԭʼpolicy/config��������PC��δ�ڱ���Git�ύ����ȫ��ԭʼ�ֽڡ�** Git����[��������](../evidence/gaps/20261019/commands.json)��[�����嵥](../evidence/gaps/20261019/inputs.json)��[��¼�Ƚ�](../evidence/gaps/20261019/policy-record-comparison.json)��[�Ƚ���У��](../evidence/gaps/20261019/comparator-validation.json)��[����](../tools/gaps/README.md)��45391��AVTAB��¼��849��genfs��2437����������bitmapһ�£�header��λ���챣�������ܳ��ļ���ͬ�����SEToolsȫ������֤����[GAP-01](research/p780-evidence-gap-audit-20261019.md)��

## ����ȼ�

|�ȼ�|����|
|---|---|
|Gitԭ��|�ֿⱣ������¶�ȡ��ԭʼ�ֽڣ�����Base64���б�ע|
|Git��ȡ֤��|ֻ���ϣ/�嵥/����/�����/���������ܾݴ������������������|
|����PC/�Ựԭ��|�����ڷ������ɻ������棬��δ��ԭ������Git|
|δȡ��|û�п���ԭ�����ļ�����·����������־����������|

## OEMLOCK-01 ��������֤�ݣ�2026-10-19��

Settings/framework/services����PCԭ�����¼���SHA��Settingsƥ���manifest��������ƥ��DSUר�⣻��ԭ����PC��[�����嵥](../evidence/oemlock/20261019/manifest.json)��[15����ԭʼָ��/�����](../evidence/oemlock/20261019/focused-methods.json)��[��ʷ��������ѡ��](../evidence/oemlock/20261019/property-excerpts.json)����Git��ȫ��Ŀ�����114���������ύ�ؼ�15���������ȸ��Ǽ��ͨ������������������ͼ�������ڴ���֤����[Journey gate���߶�λ](research/p780-oemlock-journey-gate-20261019.md)��

OEMLOCK-02���䣺[296�����嵥](../evidence/oemlock/20261019/caller-inventory.json)��[6ֱ�ӵ��÷���](../evidence/oemlock/20261019/callers.json)��[9ȷ��������](../evidence/oemlock/20261019/confirmation-methods.json)��[Ȩ��manifest](../evidence/oemlock/20261019/permission-manifests.json)��[�������ժ¼](../evidence/oemlock/20261019/component-excerpts.json)��176APK manifest�޽����쳣������ԭʼ�ֽ�SHAȫ��У��ͨ����ֻ����ֱ��DEX���ã�������������̼�/��ӵ���/������Ȩ����[OEMLOCK-02�����߽߱�](research/p780-oemlock-caller-boundary-20261019.md)��

## ��ǰ��̬����

|�ʲ�|������|Git���淶Χ|
|---|---|---|
|PC�ɼ�manifest|1759�1131297358�ֽڣ����ǲ�������|[manifest.csv](../evidence/static/20261018-220912/manifest.csv)��[�ɼ���Χ��ȱ��](research/p780-static-corpus-inventory-20261018.md)|
|batch1 ZIP|742���ļ���Ŀȫ��ƥ��PC�嵥��194 RC��285 service������381 ELF��Ŀ����������|[��֤/����JSON](../evidence/static/20261018-220912/batch1-verified-analysis.json)��[����](research/p780-static-batch1-analysis-20261018.md)��ZIP/ȫ��ԭ��δ��Git|
|batch2 ZIP|514��ȫ��ƥ�䣻279493296�ֽڣ�509 ELF+5 bitcode|[ժҪJSON](../evidence/static/20261018-220912/batch2-verified-analysis.json)��[����](research/p780-static-batch2-analysis-20261018.md)�����������ϣ��PC manifest���ǣ�ZIPδ��Git|
|policy ZIP|55���豸�ļ�+pull.log��CRCͨ����ODMԤ�������881104�ֽڣ�3��CIL/mappingժҪƥ��|[���ļ���ϣ�Ͳ�ѯ](../evidence/static/20261018-222940/policy-audit.json)��[����](research/p780-policy-boundary-audit-20261018.md)�����Զ�����δ��Git|
|native�ӿڽ���|6���������/��ض�̬���ţ�36����Բ�ѯ��73 JAR/DEX�����ַ���ɨ��|[����֤��](../evidence/static/20261018-220912/native-interface-crosscheck.json)��[����](research/p780-native-interface-crosscheck-20261018.md)|

����ZIP SHA-256��

- batch1��`340765c47e7a9bc8d96b6eb368902117ce631d84a3d34ca0ae1d0eff2e92ca3b`
- batch2��`31aa1878b46a71fd960b7bdc5044e1a5421a2f8e6400bf919873e1efa62e5ce2`
- policy��`85f6d86d7d3d33ba940afacca6350527848ce07e29961ab92129ffcdb70a82a1`

���μ������ļ���Ŀ��������֤·�������ݻ��⣬������ӳ�Ϊȥ�غ�������̼���0�ļ���vendor/bin/vendor/lib64�ɼ�����Ϳ�journey.factory.rc���������ڲ�����/�޹��ܽ��ۡ�

## 2026-10-19 EDL ͨ��ʵ��

|�ʲ�|����״̬��߽�|
|---|---|
|QDL v2.8 Windows x64 `list` / `chipinfo`|����PC����ǰ�Ự��־���Ѻ˶� Sahara v2/HWID/PKHash �� 2026-06-12 ��¼һ�£�ԭʼ���������� PKHash δ��Git����[ר��](research/p780-qdl-qud-sahara-20261019.md)|
|bkerler/edl v3.62 COM6 NOP ʧ����־|����PC/�Ự�ն��ı���������������׶��жϣ�`END_TRANSFER status 1` ���ʽ Streaming ��ס�������� Loader ǩ���ܾ�|
|Mannar ͨ�� Firehose ��ѡ A|������ GitHub Դ����еĺ�ѡ�ļ���ƥ�� MSM �� model/PKHash ǰ׺��ͬ��ʵ��������4�� Sahara READ64 ��ͨ��ʧ�ܣ�δ�����֤�� Firehose ������ԭʼ��־ֻ�ڻ���PC/�Ự��������δ��֣�ͬ�����߽������ Qualcomm/MODEL=0000/HWID=ȫ��/VAR=MannarPkgLAB����֤�� PKHash=`d9357db8��`���뱾�������������ר��|

|B�CE ����ǩ�����߽���|ԭʼ���������� Loaders ȥ������3�ļ�����ʱ�����ر�ȥ�غ�������־���г� B�CE��A�CE ��5�ļ���3���ժҪ d935/4352/a51a�����뱾�� c19a ������ԭʼ�ն���־�Ͷ����Ʋ���֣���[����](research/p780-qdl-qud-sahara-20261019.md)|

## AVB����ֹͣDSUʵ��

|�ʲ�|����״̬��߽�|
|---|---|
|Ӳ��֤��.p7b|����Git��[��������](research/avb-attestation-confirmed-20261018.md)�����/��ԿժҪ����֤���������ߵ���У�鲻����|
|AVB/fstab�ն����|ר�����û���ԭʼ���������ԭ��vbmeta/boot����[����](research/avb-live-baseline-20261018.md)��[fstab](research/p780-fstab-avb-20261018.md)|
|Google GSI A/B������|��������PC���ֿ�ֻ���汨��/ժҪ������δ�õ�������������㡣[��ǩ����](research/p780-dsu-testroot-resign-verified-20261018.md)|
|B����ǰ����־/bugreport��ԭ����װ��APK/framework/services JAR|�����ڻỰ������δ�����ֺ�������Ϣԭ��ȫ���ύGit��[����������SHA](research/p780-dsu-closure-maintenance-route-20261018.md)|
|����ǩ��/��ȡ���߽�����|��ʷ�˱��Ǽǰ汾����Դ������ð�Ʋֿ�toolsĿ¼�Ѱ�����Щ��|

B�Ѱ�װ�������������ԭ������ʷ�˱��ġ���δ����/��װ/������ֻ��Ӧ���ڽ׶Ρ�������ʷҳ��[DSU����](archive/dsu-index-20261018.md)��

## ���к���ԭ������ȡ֤��

|���|����·��|�߽�|
|---|---|---|
|�ں�������Tracefs|[device](../evidence/device)��39170B config.gz��4096B trace raw|���ں˾���/ȷ����ַ|
|GhostLock������|[ghostlock](../evidence/ghostlock)��v0.1��v0.4ԭZIP|�����汾覴ã�CRC/SHA����Ƕ���������飬������Ȩ�ɹ�|
|��ѡ����|[actions](../evidence/actions)��Clang11/14������delta�����ֶ���ԭ��|���ղ�������run38060518994���������б���������|
|Journey���|[framework](../evidence/framework)������SHA�������ֽڡ�����ࡢ���õ�|ԭʼ��JAR/ZIPδ��Git|
|Journey����|[journey](../evidence/journey)��XML/version��TCS�Ķ���ͼ������Base64 ZIP|64����ALL����ƥ�䣻�ǹ̼�/Ȩ�ޱ�|
|ϵͳAPK|[apk](../evidence/apk)��ApeHighLights��SecureUI��SystemHelper|ʵ����Դ�鵵�������������ӿڿ�ԽȨ|
|TEE��¼|[tee](../evidence/tee)������������ȡʧ�ܼ�¼|����������TEE��������Ȩ|
|��ADB/OTA/Bugreport|[restricted](../evidence/restricted)��ԭZIP��UTF-16��־�����嵥|����δ��������������Ŀ¼û�е���ACL|
|�������Ͽ���|[web](../evidence/web)��XDA�û��ṩ��������Դ��¼|���������棬����ð�䱾������|
|�ɱ���/����|[archive](../archive)|��ʷ�������ݣ����Զ���Ϊ��ǰִ�мƻ�|

��ʷ�˱�����ֽ�����ԭʼUTF-16��ת��UTF-8�;���������֮�𣻵�ǰGit����������[����ǰ���嵥](../evidence/analysis/repository-inventory-20261018.json)Ϊ׼��Git blob SHA��SHA-256����ơ�ͬ��/ͬ��С������������ͬ��

## ��ȷδȡ��

ƥ�� `_162` �Ŀ�������OTA��boot/vendor_boot/vbmeta/vbmeta_system���������ں�vmlinux/System.map������ǩ��Firehose��init/Journey���/gsid�ؼ���ִ���ļ����ݣ�ʧ��DSU��������Чpstore/ramoops������ɹ����ӿ����ֻ�Ȩ�޾ܾ������ܲ�����Щ��ȱ��

�����Ա�׼��[֤�ݹ淶](reference/evidence-integrity.md)��ԭ����˽�߽��[SECURITY](../SECURITY.md)������������������֤��ԭ���ֽڲ��䣻��֤��Χ��[����](REPOSITORY_AUDIT.md)��

