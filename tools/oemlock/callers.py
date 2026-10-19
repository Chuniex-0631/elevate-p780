import sys,pathlib,zipfile,json,hashlib,struct,argparse
sys.path.insert(0,str(pathlib.Path.cwd()/'.research-deps'))
from dex_tables import Tables,DCode
parser=argparse.ArgumentParser(description='Offline scan of existing P780 corpus; no device access')
parser.add_argument('root',type=pathlib.Path)
parser.add_argument('--output',type=pathlib.Path,default=pathlib.Path(__file__).parent)
args=parser.parse_args();root=args.root
files=list((root/'09/P780-static-20261018-220912/files').rglob('*.apk'))+list((root/'09/P780-static-20261018-220912/files').rglob('*.jar'))+[root/'10-oem-unlock/Settings.apk',root/'10-oem-unlock/framework.jar',root/'09/P780-services.jar']
seen={};inventory=[];hits=[]
for f in files:
 sha=hashlib.sha256(f.read_bytes()).hexdigest()
 if sha in seen:continue
 seen[sha]=f.name;entry=dict(file=str(f.relative_to(root)),sha256=sha,size=f.stat().st_size,dex=[]);inventory.append(entry)
 with zipfile.ZipFile(f) as z:
  for n in z.namelist():
   if not n.endswith('.dex'):continue
   raw=z.read(n)
   if b'setOemUnlockAllowedByUser' not in raw:continue
   cm=Tables(raw); entry['dex'].append(n)
   for mid,code in cm.definitions:
    ref=cm.methods[mid];size=struct.unpack_from('<I',raw,code+12)[0];b=raw[code+16:code+16+size*2];ins=[];offset=0;match=False
    for x in DCode(cm,0,size,b).get_instructions():
     op=x.get_name();a=x.get_output() if op.startswith('invoke-') else ''
     if '->setOemUnlockAllowedByUser(' in a:match=True
     offset+=x.get_length()
    assert offset==len(b)
    if not match:continue
    offset=0
    for x in DCode(cm,0,size,b).get_instructions():
     ins.append(dict(offset=offset,op=x.get_name(),args=x.get_output()));offset+=x.get_length()
    hits.append(dict(file=entry['file'],dex=n,cls=ref.c,method=ref.n+ref.d,code_offset=code,sha256=hashlib.sha256(b).hexdigest(),insns_hex=b.hex(),instructions=ins))
out=args.output;out.mkdir(parents=True,exist_ok=True)
(out/'caller-inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
(out/'callers.json').write_text(json.dumps(hits,indent=2),encoding='utf-8')
print('unique inputs',len(inventory),'callers',len(hits))
for h in hits:print(h['file'],h['cls'],h['method'])

