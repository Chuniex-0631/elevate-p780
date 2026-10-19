"""Bounded binary record comparison for this Android policy-v30 pair.
Not a general policy parser, SELinux evaluator, or replacement for SETools.
Record layouts reference Linux v5.4 security/selinux/ss/{policydb,avtab,ebitmap}.c.
The symbol-table/AVTAB boundary is a caller-supplied audited offset, never guessed.
"""
import argparse,struct,hashlib,json,collections,pathlib
class Reader:
 def __init__(self,data,offset):self.data=data;self.p=offset;self.sections={};self.counts={}
 def take(self,n):
  if n<0 or self.p+n>len(self.data):raise ValueError('Truncated record')
  b=self.data[self.p:self.p+n];self.p+=n;return b
 def u32(self):return struct.unpack('<I',self.take(4))[0]
 def text(self):
  n=self.u32()
  if n>65536:raise ValueError('Excessive string')
  return self.take(n)
 def bitmap(self):
  size,high,n=struct.unpack('<III',self.take(12))
  if size!=64 or n>10000:raise ValueError('Unsupported bitmap')
  self.take(12*n)
 def mls(self):
  n=self.u32()
  if n not in (1,2):raise ValueError('Unsupported MLS range')
  self.take(4*n)
  for _ in range(n):self.bitmap()
 def context(self):self.take(12);self.mls()
 def section(self,name,records,start):
  self.sections[name]=collections.Counter(records);self.counts[name]=dict(records=len(records),offset=start,end=self.p)
 def avtab(self):
  start=self.p;n=self.u32();rs=[]
  if n>1000000:raise ValueError('Excessive AVTAB size')
  for _ in range(n):
   p=self.p;s,t,c,k=struct.unpack('<4H',self.take(8))
   if not s or not t or not c or k not in (1,2,4,16,32,64,256,512,1024):raise ValueError('Unexpected AVTAB key')
   self.take(34 if k&0x700 else 4);rs.append(self.data[p:self.p])
  self.section('unconditional_avtab',rs,start)
 def suffix(self):
  # These tables are empty in both audited inputs. Fail closed for other layouts.
  for name in ['conditional_rules','role_transitions','role_allows']:
   start=self.p;n=self.u32()
   if n:raise ValueError('Nonempty '+name+' not supported')
   self.section(name,[],start)
  start=self.p;rs=[]
  for _ in range(self.u32()):
   p=self.p;self.text();self.take(16);rs.append(self.data[p:self.p])
  self.section('filename_transitions',rs,start)
  for cls in range(7):
   start=self.p;rs=[]
   for _ in range(self.u32()):
    p=self.p
    if cls==0:self.take(4);self.context()
    elif cls in (1,3):self.text();self.context();self.context()
    elif cls==2:self.take(12);self.context()
    elif cls==4:self.take(8);self.context()
    elif cls==5:self.take(4);self.text();self.context()
    elif cls==6:self.take(32);self.context()
    rs.append(self.data[p:self.p])
   self.section('ocontext_'+str(cls),rs,start)
  start=self.p;rs=[];genfs_keys=[]
  for _ in range(self.u32()):
   fs=self.text()
   for _ in range(self.u32()):
    p=self.p;path=self.text();cl=self.take(4);genfs_keys.append((fs,path,cl));self.context();rs.append(struct.pack('<I',len(fs))+fs+self.data[p:self.p])
  assert len(genfs_keys)==len(set(genfs_keys)),'Duplicate genfs lookup keys; cannot disregard ordering'
  self.section('genfs_contexts',rs,start)
  start=self.p;rs=[]
  for _ in range(self.u32()):
   p=self.p;self.take(12);self.mls();rs.append(self.data[p:self.p])
  self.section('range_transitions',rs,start)
  # Attribute bitmap index is semantic, so compare the entire trailing byte sequence in order.
  start=self.p;n=0
  while self.p<len(self.data):self.bitmap();n+=1
  self.section('ordered_type_attribute_bitmaps',[self.data[start:self.p]],start)
  self.counts['ordered_type_attribute_bitmaps']['bitmap_count']=n
def compare(a,b,offset):
 def header(d):
  magic,n=struct.unpack_from('<II',d)
  assert magic==0xf97cff8c and d[8:8+n]==b'SE Linux'
  ver,flags,sym,ocon=struct.unpack_from('<4I',d,8+n)
  assert ver==30 and sym==8 and ocon==7
  return dict(version=ver,config=hex(flags),config_offset=12+n)
 ha,hb=header(a),header(b)
 # Require all symbol-table bytes and header bytes other than config to match.
 pa,pb=bytearray(a[:offset]),bytearray(b[:offset]);co=ha['config_offset']
 pa[co:co+4]=b'\0'*4;pb[co:co+4]=b'\0'*4
 assert pa==pb,'Prefix differs beyond header config; unsupported pair'
 x,y=Reader(a,offset),Reader(b,offset);x.avtab();y.avtab();x.suffix();y.suffix()
 sections={}
 for name in x.sections:
  live,disk=x.sections[name],y.sections[name]
  sections[name]=dict(live=x.counts[name],disk=y.counts[name],record_multiset_equal=live==disk,only_live=sum((live-disk).values()),only_disk=sum((disk-live).values()))
 return dict(live=dict(size=len(a),sha256=hashlib.sha256(a).hexdigest(),header=ha),disk=dict(size=len(b),sha256=hashlib.sha256(b).hexdigest(),header=hb),binary_equal=a==b,prefix_equal_except_config=True,avtab_offset=offset,sections=sections,all_compared_records_equal=all(v['record_multiset_equal'] for v in sections.values()),limitations=['Pair-specific v30 parser with externally audited AVTAB offset; not a general binary-policy reader.','Header config difference is retained and not silently treated as semantically irrelevant.','No independent SETools semantic diff or live access operation was performed.'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('live',type=pathlib.Path);p.add_argument('disk',type=pathlib.Path);p.add_argument('--avtab-offset',type=lambda x:int(x,0),required=True);p.add_argument('--output',type=pathlib.Path,required=True);args=p.parse_args()
 r=compare(args.live.read_bytes(),args.disk.read_bytes(),args.avtab_offset)
 args.output.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))

