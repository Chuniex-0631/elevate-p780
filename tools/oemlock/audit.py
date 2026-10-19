import sys, pathlib, zipfile, hashlib, json, struct, argparse
sys.path.insert(0,str(pathlib.Path.cwd()/'.research-deps'))
from dex_tables import Tables, DCode
parser=argparse.ArgumentParser(description='Offline OEM Lock DEX audit; no device access')
parser.add_argument('inputs',nargs='+',type=pathlib.Path)
parser.add_argument('--output',type=pathlib.Path,default=pathlib.Path(__file__).parent)
args=parser.parse_args()
paths=args.inputs
targets=['Lcom/android/settings/development/OemUnlockPreferenceController;', 'Lcom/android/server/oemlock/', 'Landroid/service/oemlock/OemLockManager;', 'Lcom/journey/system/JourneyDebugFeature;']
out=[]; manifest=[]
for f in paths:
 manifest.append(dict(file=f.name,size=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
 with zipfile.ZipFile(f) as z:
  for n in z.namelist():
   if not n.endswith('.dex'): continue
   raw=z.read(n); cm=Tables(raw)
   for mid,code in cm.definitions:
    ref=cm.methods[mid]
    if not any(ref.c.startswith(t) for t in targets): continue
    size=struct.unpack_from('<I',raw,code+12)[0]; b=raw[code+16:code+16+size*2]; ins=[]; offset=0
    for x in DCode(cm,0,size,b).get_instructions():
     ins.append(dict(offset=offset,op=x.get_name(),args=x.get_output()));offset+=x.get_length()
    assert offset==len(b)
    out.append(dict(file=f.name,dex=n,cls=ref.c,method=ref.n+ref.d,code_offset=code,sha256=hashlib.sha256(b).hexdigest(),insns_hex=b.hex(),instructions=ins))
dest=args.output
dest.mkdir(parents=True,exist_ok=True)
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(dest/'methods.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
(dest/'disassembly.txt').write_text('\n'.join('\nFILE '+m['file']+' '+m['dex']+'\nCLASS '+m['cls']+'\nMETHOD '+m['method']+'\n'+'\n'.join(f"{x['offset']:04x} {x['op']} {x['args']}" for x in m['instructions']) for m in out),encoding='utf-8')
print('Methods:',len(out))

