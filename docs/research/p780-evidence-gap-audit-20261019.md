# GAP-01�����в��ԡ��ں�֤������ļ���ʵ��2026-10-19��

���ֲ��������ȱ�ڣ�**�ɹ�ȡ�������� SELinux policy ԭ�����ֻ��ں�������10��10���������ֽ�һ�£�journey.factory.rc ȷΪ���ֽ��ļ���** δ�õ��µ� Root/�����������ȡ/д��ͨ����

## ������

|��ȱ��|����ֱ�ӹ۲�|״̬��߽�|
|---|---|---|
|û�����в���dump|ADB pull `/sys/fs/selinux/policy` �ɹ���881104 B��SHA256 `a4d6851e984a0232dea7cbabbf600f87eeb74b94005a260ecbbca756bcad1409`|��ȡ�ã���ǰԭ����PC��Git�����嵥���ȽϽ���͹��ߣ���ð������ԭ������Git|
|���в����Ƿ������һ��|��ODM precompiledΪ881104 B��SHA256 `77f077d8c95b38929aed0434c9c56ca6158c24d90c169ee2644d490684111b79`�������ֽ�һ��|���ּ�¼���Ƚ����£���������SETools���帴���Դ����|
|�ں������Ƿ����þ�����|���µ��� `/proc/config.gz`��39170 B��SHA256 `0ff9cbb1844e043e1211b527509f5f435862cace25649bab6641d5d62c7bbce0`|��10��10�չ鵵ѹ���ֽڡ���ѹ�ı���һ�£��Բ�֤���ں˶����ƻ�©���޲�״̬��ͬ|
|�����ں�����|uname��/proc/versionΪ `5.4.233-qgki-gea5245e94afe-dirty`��Clang11.0.2/r383902b1������ʱ���ַ��� `Tue Feb 20 18:01:03 CST 2024`|�汾/������ȷ�ϣ�����GNU Build ID���������豸��ǰʱ��|
|�ɷ�ֱ��ȡ��Build ID|`/sys/kernel/notes` Ԫ���ݼ�ͬ��pull�� Permission denied|δȡ�ã�������Ϊ�����ڣ�����ɼ�����Ԫ���ݾܾ����Գ���һ��pull����������Ϊʧ�ܺ�������ԭʼ���γ��Ծ�����|
|CONFIG_IKHEADERS=y�ܷ�ȡ��ͷ�ļ�|`/sys/kernel/kheaders.tar.xz` Ԫ���� Permission denied��δ����pull|����֧�ֲ�����shell�ɶ�����ʹȡ��ͷ�ļ�Ҳ��������к����ֽڻ�DWARF|
|����������ϢBTF|`/sys/kernel/btf` ���� No such file or directory���ֻ����� `CONFIG_DEBUG_INFO_BTF` δ����|�ñ�׼����Ŀ¼���ڱ��οɼ�·���У�������Ϊϵͳû���κε�������|
|����/���Ʋ����ɷ��ȡ|kallsymsǰ���С�kptr_restrict��dmesg_restrict��unprivileged_bpf_disabled��modules_disabled�� Permission denied|û�еõ���Ӧֵ�����Գ���Ĭ��ֵ����|
|perfȨ��״̬|`/proc/sys/kernel/perf_event_paranoid` �ɶ���ֵΪ `-1`��������CONFIG_PERF_EVENTS=y|����sysctl����perf_event_open�ɹ���SELinux���ɡ���ַй¶��©��������֤��������û������perf/trace�¼�����Գ���|
|���ֽ� journey.factory.rc|�ֻ�lsΪregular file������0��pull�˳�0���õ����ļ���SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`|�ɾ�̬�嵥��һ���ɴ�ȷ������Ϊ����ʵ��ȷ�ϣ�system/bin/secilc�����ֽ�����ʧ�ܲ���������֮����|

## ���ݲ��Եļ�¼������Ƚ�

��������Linux5.4�� [avtab����](https://raw.githubusercontent.com/torvalds/linux/v5.4/security/selinux/ss/avtab.c) �� [policydb����](https://raw.githubusercontent.com/torvalds/linux/v5.4/security/selinux/ss/policydb.c)��ʵ���޶�����Android policy v30����ԵıȽ�����AVTAB�߽�Ϊ�˹��˶Ե� `0x25602`������ͨ���Զ���λ��������

- �����ļ���v30��8���ű���7���������ı���AVTAB֮ǰ�������ֽڳ�header config�ֶ���һ�£��������š�Լ����ǰ��bitmap��ԭʼ���С�
- AVTAB��45391�����������ظ�������ԭʼ��¼���ؼ��ϱȽϣ�������/ɾ��/���ݲ��죻������ͨallow��¼42548�������ܰ�45391ȫ����allow��
- �������򡢽�ɫת������ɫallow�����գ�5��filename transition��27����ʼSID��19��fs_use��849��genfs��¼�����ؼ�����ͬ������������ocontext����range transition��Ϊ�ա�
- 2437��β����������bitmap������˳����������β�����ֽ�һ�£�����ǡ�õ���EOF��
- genfs�� `(filesystem,path,class)` ��������ظ������ڱȽϼ�¼����ʱ��������λ�ã������������ļ�ϵͳ������Ϊ����̬��֤��
- 2026-10-20 原件复核纠正：running header config 为 `0x1`，disk precompiled 为 `0x80000001`；旧文两端写反。额外高位解释和独立 SETools 语义比较仍未完成，见[复核报告](p780-policy-header-verification-20261020.md)。

��Ϊ��[���Ծ���](p780-policy-boundary-audit-20261018.md)��������ԭ��֧�֣�δ�����ȽϹ��򼯺ϳ����������У��Բ��ܰѾ�̬allow/��allow�������Binder/HIDL/�ļ����������

Windows����δ���ÿ���WSL������û�а�װWSL����������������ֻ����͹��ߡ����δ���ж�����SETools sediff���Ƚ���ͨ���������롢����AVTAB datum�仯������bitmap�仯���ض����롢ǰ׺�仯��header�仯����У�飻��Щ���Բ��������ʵ�֡�

## ֤�������

[����������־](../../evidence/gaps/20261019/commands.json)��[�����嵥������ժ¼](../../evidence/gaps/20261019/inputs.json)��[���Լ�¼�Ƚ�](../../evidence/gaps/20261019/policy-record-comparison.json)��[�Ƚ���У��](../../evidence/gaps/20261019/comparator-validation.json)���汾��֤�ݡ���־�е�PC�������Ŀ¼�滻Ϊ `<CAPTURE_DIR>`��û���ռ��˻���IMEI��SIM���豸���кš�

�����ǹ̶�ֻ����ѯ/�ļ�������û���޸�SELinux���������ԡ�OEM Binder���á���Ȩ���ԡ���Ϸ�������װ�����������������δ������ǰ�ѱ��ܵ�init/Journey/vendorģ��ԭ�����ɼ��ű��޶���� [tools/gaps˵��](../../tools/gaps/README.md)����������ظ��Ѿܾ�·������Ҫ��Ϊ���߿ɸ��þ�������������嵥��

��һ��������������Ч����������PC����policy�Ķ���SETools����Ƚϲ�����headerλ��ȡ�ÿ���ͬ�����ں�/���̷����ʵ�ֺ����󲹶���builtin����ñ߽硣��ǰkernel notes/kheaders/kallsyms�ܾ��Ѽ�Ϊ�Ѳ���ȱ�ڣ�����������ִ�����OEM/DSU/��Loader������ؿ���

