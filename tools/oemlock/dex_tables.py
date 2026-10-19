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


