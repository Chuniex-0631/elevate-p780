"""Fixed read-only ADB checks. No writes, service calls, shell scripts or retries on device."""
import pathlib,subprocess,json,datetime,hashlib,argparse
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=pathlib.Path,required=True);args=parser.parse_args();dest=args.output
dest.mkdir(parents=True,exist_ok=True)
events=[]
def run(label,args):
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        p=subprocess.run(['adb',*args],capture_output=True,timeout=25)
        result=dict(label=label,args=args,started_utc=started,exit_code=p.returncode,stdout=p.stdout.decode('utf-8','replace'),stderr=p.stderr.decode('utf-8','replace'))
    except subprocess.TimeoutExpired:
        result=dict(label=label,args=args,started_utc=started,error='timeout; not retried')
    events.append(result)
    (dest/'commands-local.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
    print(label,result.get('exit_code'),result.get('stdout','')[:500],result.get('stderr','')[:300],flush=True)
    return result
if run('device-state',['get-state']).get('stdout','').strip()!='device':raise SystemExit('ADB device unavailable or ambiguous')
for label,cmd in [
    ('kernel-release',['uname','-r']),('kernel-version',['cat','/proc/version']),
    ('kernel-notes-metadata',['ls','-l','/sys/kernel/notes']),
    ('kheaders-metadata',['ls','-l','/sys/kernel/kheaders.tar.xz']),
    ('btf-directory',['ls','-ld','/sys/kernel/btf']),
    ('kallsyms-sample',['head','-n','3','/proc/kallsyms']),
    ('kptr-restrict',['cat','/proc/sys/kernel/kptr_restrict']),
    ('dmesg-restrict',['cat','/proc/sys/kernel/dmesg_restrict']),
    ('bpf-restriction',['cat','/proc/sys/kernel/unprivileged_bpf_disabled']),
    ('perf-restriction',['cat','/proc/sys/kernel/perf_event_paranoid']),
    ('modules-disabled',['cat','/proc/sys/kernel/modules_disabled']),
    ('factory-rc-metadata',['ls','-l','/system/etc/init/journey.factory.rc']),
]:run(label,['shell',*cmd])
for label,remote,name in [
    ('kernel-notes','/sys/kernel/notes','kernel-notes.bin'),
    ('current-config','/proc/config.gz','current-config.gz'),
    ('running-policy','/sys/fs/selinux/policy','running-policy.bin'),
    ('factory-rc','/system/etc/init/journey.factory.rc','journey.factory.rc')
]:
    if label=='kernel-notes' and next(x for x in events if x['label']=='kernel-notes-metadata').get('exit_code')!=0:
        continue
    r=run(label,['pull',remote,str(dest/name)])
    p=dest/name
    if r.get('exit_code')==0 and p.exists():
        r['file']=dict(name=name,size=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
# Header export can be large. Pull only if the single metadata check succeeded and it is <=64 MiB.
meta=next(x for x in events if x['label']=='kheaders-metadata')
if meta.get('exit_code')==0:
    fields=meta['stdout'].split()
    if len(fields)>4 and fields[4].isdigit() and int(fields[4])<=64*1024*1024:
        r=run('kernel-headers',['pull','/sys/kernel/kheaders.tar.xz',str(dest/'kheaders.tar.xz')])
        p=dest/'kheaders.tar.xz'
        if r.get('exit_code')==0 and p.exists():r['file']=dict(name=p.name,size=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
(dest/'commands-local.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')

