"""Read original DEX tables and disassemble with androguard's instruction decoder.
No DEX rewriting, device access or network access. Target and callers are scanned.
"""
import pathlib,zipfile,struct,json,hashlib,collections
from loguru import logger
logger.remove()
from androguard.core.dex import DCode
TARGET='Lcom/android/server/am/JourneyPerformanceService'
def uleb(b,p):
 v=0;s=0
 while True:
  x=b[p];p+=1;v|=(x&127)<<s
  if x<128:return v,p
  s+=7
class MethodRef:
 def __init__(self,c,n,d):self.c,self.n,self.d=c,n,d
 def get_class_name(self):return self.c
 def get_name(self):return self.n
 def get_descriptor(self):return self.d
class Tables:
 def __init__(self,b):
  self.b=b
  class Packers(dict):
   def __missing__(self,k):self[k]=struct.Struct('<'+k);return self[k]
  self.packer=Packers()
  sizes=struct.unpack_from('<12I',b,56);sc,so,tc,to,pc,po,fc,fo,mc,mo,cc,co=sizes
  self.strings=[]
  for i in range(sc):
   p=struct.unpack_from('<I',b,so+4*i)[0];_,p=uleb(b,p);self.strings.append(b[p:b.index(0,p)].decode('utf-8',errors='replace'))
  self.types=[self.strings[struct.unpack_from('<I',b,to+4*i)[0]] for i in range(tc)]
  protos=[]
  for i in range(pc):
   _,ret,off=struct.unpack_from('<III',b,po+12*i);params=[]
   if off:
    count=struct.unpack_from('<I',b,off)[0];params=[self.types[x] for x in struct.unpack_from('<'+str(count)+'H',b,off+4)]
   protos.append('('+' '.join(params)+')'+self.types[ret])
  self.methods=[]
  for i in range(mc):
   c,p,n=struct.unpack_from('<HHI',b,mo+8*i);self.methods.append(MethodRef(self.types[c],self.strings[n],protos[p]))
  self.fields=[]
  for i in range(fc):
   c,t,n=struct.unpack_from('<HHI',b,fo+8*i);self.fields.append((self.types[c],self.types[t],self.strings[n]))
  self.definitions=[]
  for i in range(cc):
   v=struct.unpack_from('<8I',b,co+32*i);off=v[6]
   if not off:continue
   counts=[]
   for _ in range(4):x,off=uleb(b,off);counts.append(x)
   for _ in range(counts[0]+counts[1]):_,off=uleb(b,off);_,off=uleb(b,off)
   for count in counts[2:]:
    mid=0
    for _ in range(count):
     diff,off=uleb(b,off);_,off=uleb(b,off);code,off=uleb(b,off);mid+=diff
     if code:self.definitions.append((mid,code))
 def get_method_ref(self,i):return self.methods[i]
 def get_field(self,i):return self.fields[i]
 def get_type(self,i):return self.types[i]
 def get_string(self,i):return self.strings[i]
 def get_odex_format(self):return False
if __name__ == '__main__':
 root=pathlib.Path('framework-audit');hits=[];methods=[];inputs=[]
 for f in sorted(root.glob('*.jar')):
  with zipfile.ZipFile(f) as z:
   for n in z.namelist():
    if not n.endswith('.dex'):continue
    raw=z.read(n);entry=dict(jar=f.name,dex=n,sha256=hashlib.sha256(raw).hexdigest(),target_descriptor_present=TARGET.encode() in raw);inputs.append(entry)
    if not entry['target_descriptor_present']:continue
    cm=Tables(raw)
    for mid,code in cm.definitions:
     ref=cm.methods[mid];target=ref.c.startswith(TARGET)
     size=struct.unpack_from('<I',raw,code+12)[0];b=raw[code+16:code+16+size*2];ins=[];offset=0;refs=[]
     for x in DCode(cm,0,size,b).get_instructions():
      op=x.get_name();args=x.get_output() if target or op.startswith(('invoke-','iget','iput','sget','sput','new-','check-cast','instance-of','const-class','filled-new-array')) else ''
      ins.append(dict(offset=offset,op=op,args=args));offset+=x.get_length()
      if TARGET in args:refs.append(len(ins)-1)
     assert offset == len(b), (ref.c,ref.n,offset,len(b))
     if refs and not target:
      ins=[];offset=0
      for x in DCode(cm,0,size,b).get_instructions():
       ins.append(dict(offset=offset,op=x.get_name(),args=x.get_output()));offset+=x.get_length()
     identity=dict(jar=f.name,dex=n,class_name=ref.c,method=ref.n+ref.d,code_item_offset=code)
     if target:methods.append({**identity,'instructions':ins,'original_insns_sha256':hashlib.sha256(b).hexdigest()})
     else:
      for i in refs:hits.append({**identity,'target':ins[i],'context':ins[max(0,i-6):i+7]})
 (root/'performance-methods.json').write_text(json.dumps(methods,indent=2)+'\n');(root/'performance-callsites.json').write_text(json.dumps(hits,indent=2)+'\n');(root/'performance-scan-inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
 (root/'performance-disassembly.txt').write_text('\n'.join('\nCLASS '+m['class_name']+'\nMETHOD '+m['method']+'\n'+'\n'.join(f"{x['offset']:04x} {x['op']} {x['args']}" for x in m['instructions']) for m in methods)+'\n')
 print('methods',len(methods),'refs',len(hits),'caller methods',len(set((h['class_name'],h['method']) for h in hits)))
 for h in hits:print(h['class_name'],h['method'],'=>',h['target']['args'])
