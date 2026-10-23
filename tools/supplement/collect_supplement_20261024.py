"""Fixed read-only collection of previously missing static VINTF/OTA trust inputs."""
import argparse,pathlib,subprocess,json,datetime,hashlib
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();d=a.output;d.mkdir(parents=True,exist_ok=True);events=[]
def run(label,args):
 try:
  r=subprocess.run(['adb',*args],capture_output=True,timeout=40)
  e=dict(label=label,args=args,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=r.returncode,stdout=r.stdout.decode('utf-8','replace'),stderr=r.stderr.decode('utf-8','replace'))
 except subprocess.TimeoutExpired:e=dict(label=label,args=args,error='timeout; no retry')
 events.append(e);(d/'commands-local.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8');print(label,e.get('exit_code'),e.get('stdout','')[:350],e.get('stderr','')[:250],flush=True);return e
if run('device-state',['get-state']).get('stdout','').strip()!='device':raise SystemExit('One authorized device required')
for prop in ['ro.build.fingerprint','ro.build.version.security_patch','ro.vendor.build.security_patch','ro.boot.slot_suffix','ro.boot.flash.locked','ro.boot.verifiedbootstate','ro.boot.vbmeta.digest']:
 run(prop,['shell','getprop',prop])
for label,cmd in [('bootctl-current-slot',['bootctl','get-current-slot']),('bootctl-hal-info',['bootctl','hal-info']),('payload-key-dir',['ls','-l','/system/etc/update_engine']),('update-engine-config',['ls','-l','/system/etc/update_engine.conf'])]:run(label,['shell',*cmd])
for part in ['vendor','odm','system','system_ext','product']:
 target=d/'vintf'/part;target.mkdir(parents=True,exist_ok=True)
 run('vintf-'+part,['pull','/'+part+'/etc/vintf/.',str(target)])
for label,remote,name in [('ota-certs','/system/etc/security/otacerts.zip','otacerts.zip'),('update-config','/system/etc/update_engine.conf','update_engine.conf')]:
 if label=='update-config' and next(x for x in events if x['label']=='update-engine-config').get('exit_code')!=0:continue
 run(label,['pull',remote,str(d/name)])
files=[]
for f in d.rglob('*'):
 if not f.is_file() or f.name in ('commands-local.json','files.json'):continue
 b=f.read_bytes();files.append(dict(path=f.relative_to(d).as_posix(),size=len(b),sha256=hashlib.sha256(b).hexdigest()))
(d/'files.json').write_text(json.dumps(files,indent=2)+'\n',encoding='utf-8');print('files',len(files))
