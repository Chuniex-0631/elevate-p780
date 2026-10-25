> 2026-10-25 新增 `dirtyfrag-probe/`：探针 JNI 层、钩子桩、补丁生成与零引用扫描工具。 [说明](dirtyfrag-probe/README.md) · [报告](../docs/research/p780-dirtyfrag-live-exploit-20261025.md)

# ��ǰ���߹���

������������ڹ���Ŀ¼��ȡ�ļ����������ֻ���**`p780-avb-readonly.ps1` Ϊ����**����ͨ������Ȩ ADB ִ��ֻ�����Բ�ѯ���������ö�٣�����ȡ��������Ҳ�������豸���о�����ͱ߽�� [�ĵ�����](../docs/README.md)����ʷ�豸�����ű����� [archive/scripts](../archive/scripts)�����޸��ֻ�״̬��

| �ļ� | ��; |
|---|---|
| [p780-avb-readonly.ps1](p780-avb-readonly.ps1) | Windows PowerShell / ADB ������ AVB ���������������ֻ���ɼ����μ� [2026-10-18 AVB ����](../docs/research/avb-live-baseline-20261018.md) |
| [native/README.md](native/README.md) | ���APK DEX��JNI ELF/CFI����ʷ����SHA������ƣ��������ֻ� |
| [gaps/README.md](gaps/README.md) | �̶�ADBֻ����ȱ�嵥���޶�policy-v30���߼�¼�Ƚϣ������/�ܾ���ظ�ִ�� |
| [dsu/README.md](dsu/README.md) | DSU固定只读快照与已有ext4 GSI的VINTF提取、内核config子集比较；不试装 |
| [verify_repository.py](verify_repository.py) | ȫ�����·�����ӡ�Python/JSON ��ʽ��Journey ԭ��/��ͼ�뱣��Ǩ�� Blob ���ݼ�� |
| [summarize_config.py](summarize_config.py) | ԭʼ/���/��������ò��� |
| [audit_missing_config.py](audit_missing_config.py) | ȱʧ CONFIG ���ŵĹ̶�Դ������ɨ�� |
| [derive_candidate_layout.py](derive_candidate_layout.py)��[p780-layout-probe.c](p780-layout-probe.c) | ��ʵ�� Kbuild ���������ѡ�ṹ̽�� |
| [compare_candidate_layouts.py](compare_candidate_layouts.py) | �����к�ѡ���ֱȽ� |
| [scan_journey_framework.py](scan_journey_framework.py) | ԭ�� JourneyConfigService ֱ������ɨ�裻���ڴ渱������ hidden-API �������� |
| [read_performance_dex.py](read_performance_dex.py) | ֱ�Ӷ�ȡԭʼ DEX ������ȡ���ܷ�������õ㣻����ԭ�����޸� |
| [compare_journey_config.py](compare_journey_config.py) | vendor XML ��ֻ�� TCS dump ���գ�ALL ����Ϊ�Ƚϼ��� |

DEX ������Ҫ Python��androguard��loguru�����ӵ�ǰĿ¼�� framework-audit/ ��ȡ services.jar �� framework.jar���������߷����ļ������ö����÷���`python tools/compare_journey_config.py <��ѹĿ¼>`��Ŀ¼���� config.xml��version.txt ��ԭʼ tcs-state.txt�������������ߵĲ����������Խű�����Ӧ�ֶ� workflow Ϊ׼��

ԭʼ framework ����δǨ�� Git�����ܽ���¡��������� DEX ��ȡ������ SHA �ͷ�Χ�� [Journey ר��](../docs/research/journey-config.md)����ѡ���ֲ��ǿ�ֱ������ʵ���Ĳ�����

