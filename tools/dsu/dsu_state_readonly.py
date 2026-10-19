"""Snapshot a fixed DSU read-only whitelist; never install/enable/disable/remove/reboot."""
import argparse,subprocess,pathlib,json,datetime
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
props=['ro.build.fingerprint','gsid.image_installed','ro.gsid.image_running','init.svc.gsid','ro.boot.bootreason','sys.boot.reason','persist.sys.boot.reason.history','ro.vndk.version','ro.vendor.api_level','ro.product.first_api_level','ro.treble.enabled','ro.boot.dynamic_partitions','ro.boot.force_normal_boot','ro.build.ab_update','ro.boot.slot_suffix','ro.boot.flash.locked','ro.boot.verifiedbootstate','ro.vendor.build.security_patch','ro.build.version.security_patch','ro.product.cpu.abilist','ro.build.system_root_image','ro.boot.veritymode']
commands=[('gsi_status',['shell','gsi_tool','status'])]+[(x,['shell','getprop',x]) for x in props]+[('gsiservice_dump',['shell','dumpsys','gsiservice']),('dynamic_system_dump',['shell','dumpsys','dynamic_system'])]
out=[]
for label,args in commands:
 r=subprocess.run(['adb',*args],capture_output=True,timeout=20)
 out.append(dict(label=label,args=args,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=r.returncode,stdout=r.stdout.decode('utf-8','replace').replace('\r\r\n','\n').replace('\r\n','\n'),stderr=r.stderr.decode('utf-8','replace').replace('\r\r\n','\n').replace('\r\n','\n')))
(a.output/'state-snapshot.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({x['label']:x['stdout'].strip() or x['stderr'].strip() for x in out},ensure_ascii=False,indent=2))
