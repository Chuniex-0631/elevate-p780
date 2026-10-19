# P780 SELinux ԭ����ƣ�Journey ���������socket��2026-10-18��

> �������£�2026-10-19�������� `/sys/fs/selinux/policy` �ѳɹ��������뱾ҳODM���Թ�ϣ��ͬ�����ѱȽϼ�¼���ϼ�����bitmapһ�£�header��λ���������SETools�����Ա�������[GAP-01](p780-evidence-gap-audit-20261019.md)�����ġ���������dump���������Ǳ�ҳԭʼ�׶Σ������ٵ�����δȡ������ԭ����

## ���������뷶Χ
P780-policy-20261018-222940.zip��SHA256 85f6d86d7d3d33ba940afacca6350527848ce07e29961ab92129ffcdb70a82a1��CRCͨ����55���豸��̬�ļ���pull.log����56�ļ������Ŀ¼pull�˳�0��������hwservice/mac permissions�ļ������������ܳ������������ϡ�

[���ļ���ϣ����ѯ����ͷ�Χ](../../evidence/static/20261018-222940/policy-audit.json)��

ȡ��odm/precompiled_sepolicy��881104B�����ɶԱ�������ִ��SETools�����ѯ������ֻgrep��ʽCIL����©���Լ��ϼ̳С�ԭ�����޸ġ���ִ�С�ʹ��SETools 4.4.4��ѯallow��δ����permissive���͡�

����plat/system_ext/product����sepolicy.cil��mapping/30.0.cil����SHA256���ֱ�Ϊ��
- plat 414b99ceccbf367b8bef7cd414967a232575bad89c687453b152b80917168ca6
- system_ext 07579c332e2410b267f0aaf3e60f9d10693fd60213ebf1639591c283833bf025
- product 692f32b2d0e9e85b6836c64af246540f8b08ef7e9a46e3d5c83e7d70ffd99bbb

�������������ժҪ��ODMԤ������Լ�¼ȫ��һ�¡���֧�ִ��̲����������ݣ�����/sys/fs/selinux/policyʵ�����в��ԵĶ���dump��Ҳ�����OEM��Դ��֤��

## ����ƥ���������Խ��
���ϴ�property_contexts��exact/�prefixƥ�䣺
| ������/Ŀ�� | ���� | shell����Ȩ�� |
|---|---|---|
| sys.journey.diag.*����write_misc�������� | debug_prop | �������allow |
| sys.journey.*����restorecon�������� | debug_prop | �������allow |
| config.write.*��persist.config.write.* | config_prop | ��ѯδ����allow |
| persist.vendor.diag.journey.enabled | vendor_default_prop������persist.vendor.�� | ��ѯδ����allow |
| odm.journey.diag.*����factory.reset | odm_journey_diag_prop | ��ѯδ����allow |

ԭʼ��Ч����allow shell debug_prop:property_service set;
platform CIL����ͬһ��ʽ����system_app��vendor_mmi_sys��debug_prop����allow��vendor_mmi������odm_journey_diag_prop��

�Ѳ�ѯuntrusted_app��_25/_27/_29�����debug_prop/config_prop/default_prop/odm_journey_diag_prop/vendor_default_prop��property_service set��δ����allow���˽���޶�ָ�����Ȩ�ޣ�����������Ӧ�����ĳ����Ȩ�޴�����

## ����һ��init����
system initԭ������sys.journey.diag.write_misc���Դ�������write_misc������������������չ����sys.journey.restorecon����restorecon_recursive����ϱ���debug_propӳ���shell allow���⹹�ɾ����**��̬Ȩ�ޱ߽��ѡ**�����ǽ�ƾroot/DAC�Ĳ²⡣

��ȱ�٣�
1. ��Ӧinit RC�Ƿ�ʵ�ʼ��ؼ�����builtin�Ƿ�ע�᣻
2. write_misc/sync_fileʵ�֡��������ơ�Ŀ�귶Χ����������
3. �������������ĺ�ʵ�ʵ����Ƿ�ͨ��������飻
4. ����Щ�����������ȡ��Root����Ч��������

����shell������debug_prop��дΪ�����ļ�д���������д��Root��shell���в���ϵͳ����Ȩ�ޣ����в����ɴ�Ҳ���Զ�����������Ȩ��

### socket���򽵼�
journey_diag_ext_system����Ϊroot+disabled��init socket DACģʽ0666���ϴ�file_contextsû��ƥ��diag_ext_socket��ר����Ŀ������δȡ������socket��ǩ��
������Բ�ѯshell��untrusted_app/_27/_29��vendor_mmi_sys/vendor_mmi��unix_stream_socketȨ�޾���allow����socket_device sock_file����allow��
��˲�����0666�϶������ӣ�������֧��shell/��ͨӦ��ֱ�����Ӹ�root socket��ȷ�н����������б�ǩ����������socket���󡢲���������

## ����
�������� /init��/system/bin/init��/system/bin/journey_diag_ext_system��/vendor/bin/journey_diag_ext_vendor ִ�� ls -lZ����Ϊ Permission denied����������ɲ���¼�����ظ���ȡ�����ı�Ȩ�ޡ�batch2��δ���볧��builtinʵ�֣�������[native�������](p780-native-interface-crosscheck-20261018.md)����ȱ�ڡ��������ԣ��ر�write_misc/factory.reset����������̽����дmisc/boot/vbmeta��������Recovery����������Ϸ���DSU����ֹͣ��

������ʵ������д�롢��Ȩ������������д��ɹ����µ�ʵ�ʽ�չ�Ǳ������֧��shell��Journey debug���Ե�����Ȩ�ޣ��Լ��ų�config.write/ODM reset/Ĭ����Ͽ��ص�ͬ��Ȩ���ƶϡ�


