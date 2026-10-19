# P780 ʵ����̬������һ���嵥��ˣ�2026-10-18��

> �������յ�batch1��batch2��policyԭ������ɶ�Ӧ���飻��ҳ��������嵥���ʱ�Ĳɼ���Χ�ͽ��顣��ǰ����״̬��[֤������](../EVIDENCE_MANIFEST.md)��

## �о�����
����ָ��ԭ������/ά��APK��ǰ���Ų��������������ܽ��ظ�APK���ð����·�ߡ����׶�תΪ�㸲�Ǿ�̬�������⡢init����ܡ�native���ü��汾���������DSUֹͣ���䣻����Root/����/д��ɹ���

## ����ͱ߽�
�����ϴ�manifest(2).csv��pull.log��system-packages.txt��fingerprint.txt��services.txt�����嵥/��־��ȡ�ã�1759���ļ�ԭ�����ڻ���Windows��ժҪΪ�û�PC���㣬����û�ж���У���Ӧ1.13GB�ļ���Fingerprint��Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys�������嵥201�ע������ǿɷ���������©��֤����

[ԭʼ���·��/����/SHA256�嵥](../../evidence/static/20261018-220912/manifest.csv)��

## ����
- �����嵥1759��ϼ�1131297358�ֽڣ�1653�ֲ�ͬժҪ���������ļ�ժҪ����
- APK 177��JAR 121��SO 789��RC 194������ODEX/VDEX/ART/OAT�ȱ�����
- system/lib64 514�system_ext/lib64 280�framework�����ֱ�257/258/15�ע��system/framework��pull��־����256������嵥257���������ȫ����Ŀ���ɴ˴γɹ�����õ���
- pull����281�Σ�189���˳�0��92���˳�1��Ŀ¼�ɹ������������ļ������ܳ�Ϊ189������Ŀ¼��1759��������Ч������
- vendor/bin��vendor/lib64���˳�0��0 files pulled��û��ȡ����Щnative�ļ����������豸Ŀ¼Ϊ�ա�
- system/bin��ȡ��secilc��ʧ�ܣ��������Ŀ����δ��������
- system_ext/bin����11�system/lib64����bootstrap��
- �������ֽ��system/bin/secilc����־��ȷ��ȡʧ�ܣ�����Ч�����ų�����system/etc/init/journey.factory.rc��2026-10-19ʵ��lsΪ0B��pull�˳�0����ȷ�ϱ�����ʵ�ļ�Ϊ�գ���[GAP-01](p780-evidence-gap-audit-20261019.md)����
- /data/app�еĸ��°�ϵͳӦ�ñ��ɼ��ű���������������ǰ�嵥���������ǡ�overlay/vendor APKҲ��Ȩ�޾ܾ���ODMĿ�겻���ڲ����ڲ�����ODM������

## �м�ֵ�Ľ����������
��ȡ��ȫ���Ѳɼ�init���ú�vendor/etc/fstab.default������service executable��user/group��socket��property������ϵ������framework Binder������native�����/������������ִ�й������
- init.journey_diag_ext_system.rc��init.journey_diag_ext_vendor.rc��journey.init.rc��journey.init.vendor.rc��
- vendor.journey.hardware.warehouse@1.0-service.rc��vendor.qti.hardware.factory@1.0-service.rc��
- libstfactory.so + stfactorydemo��libdiag_system*.so + libDiagService.so��
- libQSEEComAPI_system.so + vendor.qti.hardware.qseecom@1.0.so��
- framework���JAR����ȷ�е��ù�ϵʱ��ȡ��factory��������ֻ����ͨ�ӿڹ���������Ϊ©��֤�ݡ�
��GhostLock/TEE/ά��APK����Ӧ�ȶ��գ����ų������ظ�����ʵ�����ԡ�

## ��һ��
1. ����ֻ�����������files/system/etc/init��system_ext/etc/init��product/etc/init��vendor/etc/init��fstab.default�����ٴ��ֻ��زɡ�
2. ��ѹ�����ʺϣ��ټ���system_ext/bin��system_ext/lib64��system_ext/framework��Ϊ�������������ܽ�ƾ�嵥�����������ƽ��ۣ���
3. ��������ԭ�����д��Build ID��DT_NEEDED���������š�Ȩ�ޱ߽�Ƚ����Ȩ��ȱ�ڰ�·����¼�����ı�SELinux������Ȩ������ԭʼ���豸��
4. �ֽ׶���GitHub�ύ�����嵥�ͷ�����С�������ڼ�����⣬�����ԭ�������Ʋ�ֱ�Ӷѽ�Git��


