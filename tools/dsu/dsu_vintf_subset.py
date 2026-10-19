"""Offline kernel-config subset comparison, not a complete libvintf checker."""
import pathlib,argparse,gzip,xml.etree.ElementTree as E,json,hashlib
from read_gsi_vintf import Ext4
p=argparse.ArgumentParser();p.add_argument('--capture',type=pathlib.Path,required=True);p.add_argument('--config',type=pathlib.Path,required=True);p.add_argument('--image',type=pathlib.Path,required=True);a=p.parse_args();d=a.capture
cfg={}
for line in gzip.decompress(a.config.read_bytes()).decode().splitlines():
 if line.startswith('CONFIG_'):key,value=line.split('=',1);cfg[key]=value.strip('"')
 elif line.startswith('# CONFIG_') and line.endswith(' is not set'):cfg[line[2:-11]]='n'
vendor=E.parse(d/'vendor-manifest.xml').getroot();matrix=E.parse(d/'gsi-vintf/compatibility_matrix.5.xml').getroot()
def match(c):
 key=c.findtext('key');v=c.find('value');kind=v.get('type');want=v.text or '';actual=cfg.get(key)
 if kind=='tristate':ok=(actual if actual is not None else 'n')==want
 elif kind=='string':ok=actual==want
 else:raise ValueError('Unsupported kernel config value type '+str(kind))
 return dict(key=key,kind=kind,expected=want,actual=actual,match=ok,absent_matches_disabled=actual is None and kind=='tristate' and want=='n')
rows=[];groups=[]
for i,k in enumerate(matrix.findall('kernel')):
 if k.get('version')!='5.4.61':continue
 cond=k.find('conditions');conditions=[] if cond is None else [match(c) for c in cond.findall('config')]
 active=all(c['match'] for c in conditions);groups.append(dict(index=i,conditions=conditions,selected=active,config_count=len(k.findall('config'))))
 if active:rows.extend(dict(group=i,**match(c)) for c in k.findall('config'))
imagefs=Ext4(a.image);prop=imagefs.content(imagefs.lookup('/system/build.prop'));selected={}
for line in prop.decode().splitlines():
 if line.startswith(('ro.build.fingerprint=','ro.build.version.security_patch=','ro.build.id=','ro.system.build.fingerprint=','ro.system.build.version.security_patch=')):
  k,v=line.split('=',1);selected[k]=v
with a.image.open('rb') as f:image_sha=hashlib.file_digest(f,'sha256').hexdigest()
r=dict(vendor_manifest=vendor.attrib,gsi_matrix=matrix.attrib,kernel_branch=dict(actual='5.4.233',minimum_in_selected_matrix='5.4.61',patchlevel_meets_minimum=True,scope='Version tuple comparison only; no patch-state inference'),image=dict(size=a.image.stat().st_size,sha256=image_sha,build_prop_sha256=hashlib.sha256(prop).hexdigest(),selected_properties=selected),config_sha256=hashlib.sha256(a.config.read_bytes()).hexdigest(),groups=groups,checked_configs=rows,count=len(rows),mismatches=[x for x in rows if not x['match']],limitations=['This only compares the selected 5.4.61 FCM5 kernel branches against the exported config.','No full merged framework/device manifests, APEX fragments, HAL version/range matching, VNDK or sepolicy compatibility evaluation.','The ext4 reader handles only bounded regular files/directories with extents; no filesystem checksum validation or independent extractor used.','Successful config subset matching does not prove DSU boot, AVB trust, early mounting or runtime HAL compatibility.'])
(d/'vintf-subset.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:r[k] for k in ['vendor_manifest','gsi_matrix','image','count','mismatches']},ensure_ascii=False,indent=2))
