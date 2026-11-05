from loguru import logger
logger.remove()
from androguard.core.dex import DEX
import pathlib,zipfile,json,hashlib,struct,zlib
root=pathlib.Path('framework-audit');hits=[];inputs=[]
for f in root.glob('*.jar'):
 b=f.read_bytes();z=zipfile.ZipFile(f);inputs.append({'name':f.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'dex':[]})
 for n in z.namelist():
  if not n.endswith('.dex'):continue
  raw=z.read(n);inputs[-1]['dex'].append({'name':n,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()});
  # Exclude hidden-API map section from a parser-only copy; keep original hashes.
  tmp=bytearray(raw); off=struct.unpack_from("<I",tmp,52)[0]; count=struct.unpack_from("<I",tmp,off)[0]
  entries=[bytes(tmp[off+4+i*12:off+16+i*12]) for i in range(count)]
  kept=[e for e in entries if struct.unpack_from("<H",e)[0]!=0xf000]
  struct.pack_into("<I",tmp,off,len(kept));tmp[off+4:off+4+len(kept)*12]=b"".join(kept)
  tmp[12:32]=hashlib.sha1(tmp[32:]).digest();struct.pack_into("<I",tmp,8,zlib.adler32(tmp[12:]) & 0xffffffff)
  d=DEX(bytes(tmp))
  for c in d.get_classes():
   if c.get_name().startswith('Lcom/journey/server/JourneyConfigService'):continue
   for m in c.get_methods():
    if not m.get_code():continue
    # Only inspect methods whose bytecode references the service.
    ins=list(m.get_instructions())
    refs=[(i,x.get_output()) for i,x in enumerate(ins) if 'Lcom/journey/server/JourneyConfigService' in x.get_output()]
    for i,target in refs:
     hits.append({'jar':f.name,'dex':n,'class':c.get_name(),'method':m.get_name()+m.get_descriptor(),'target':target,'context':[x.get_name()+' '+x.get_output() for x in ins[max(0,i-5):i+5]]})
(root/'journey-callsites.json').write_text(json.dumps(hits,ensure_ascii=False,indent=2)+'\n');(root/'input-manifest.json').write_text(json.dumps(inputs,indent=2)+'\n');print('callsites',len(hits))
