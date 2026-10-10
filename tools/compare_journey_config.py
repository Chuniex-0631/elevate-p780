"""Compare vendor XML with a read-only TCS dump; no device/network access."""
import argparse, base64, collections, hashlib, json, pathlib, re, zipfile
import xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('directory',type=pathlib.Path);a=p.parse_args();d=a.directory
root=ET.parse(d/'config.xml').getroot()
t=(d/'tcs-state.txt').read_bytes();text=t.decode('utf-16') if t.startswith((b'\xff\xfe',b'\xfe\xff')) else t.decode('utf-8-sig')
records=[]
for m in re.finditer(r'^  (\S+) =\s*\n  ([^\n]+):\s*\n   package:\[([^\]]*)\]\s*\n   behavior:\[([^\]]*)\]\s*\n   area:\[([^\]]*)\]',text,re.M):
 key,label,names,behaviors,areas=m.groups();records.append(dict(key=key,label=label.strip(),names=[v for v in names.split(',') if v],behaviors=[v for v in behaviors.split(',') if v],areas=[v for v in areas.split(',') if v]))
def split(v):return [s for s in v.split(',') if s]
expected={};duplicates=[];excluded=[]
# Reviewed DEX 0x0208..0x0248: current-area match OR absent prior key + ALL.
# ALL is a comparison hypothesis, not a directly dumped property.
for e in root.findall('package'):
 names=split(e.get('names',''));areas=split(e.get('area','ALL'));behaviors=split(e.get('behavior',''))
 info=dict(label=e.get('label'),names=names,behaviors=behaviors,areas=areas)
 if 'ALL' not in areas:excluded.append(info)
 for key in names:
  if 'ALL' in areas:
   if key in expected:duplicates.append(dict(key=key,previous=expected[key],replacement=info))
   expected[key]=info
actual={r['key']:{k:v for k,v in r.items() if k!='key'} for r in records}
mismatches=[dict(key=k,expected=expected.get(k),actual=actual.get(k)) for k in sorted(set(expected)|set(actual)) if expected.get(k)!=actual.get(k)]
result=dict(xml_version=root.find('version').get('value'),vendor_version=(d/'version.txt').read_text(),runtime_version=re.search(r'mCurrentVersion:(\d+)',text).group(1),update_frequency_hours=root.find('UpdateFrequency').get('value'),xml_package_records=len(root.findall('package')),runtime_mapping_keys=len(records),unique_runtime_keys=len(actual),comparison_area_hypothesis='ALL',expected_keys=len(expected),excluded_region_records=excluded,duplicate_overwrites=duplicates,mismatches=mismatches,limitations=['Matching state does not prove vendor file was the runtime source; cache/network may have same content.','Dump lists policy keys, not installed applications or permissions.','Time fields have HH:mm only; dates and precise scheduling cannot be inferred.'])
(d/'comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('excluded_region_records','duplicate_overwrites','limitations')},ensure_ascii=False,indent=2));print('duplicate keys',[r['key'] for r in duplicates]);print('excluded records',len(excluded))
