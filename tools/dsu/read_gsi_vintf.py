"""Read selected files from the existing raw ext4 GSI. Never mount/write/execute it."""
import pathlib,struct,json,hashlib,argparse
class Ext4:
 def __init__(self,path):
  self.f=path.open('rb');self.size=path.stat().st_size;s=self.read(1024,1024)
  assert s[56:58]==b'\x53\xef','Raw ext4 image required'
  self.bs=1024<<struct.unpack_from('<I',s,24)[0];self.ipg=struct.unpack_from('<I',s,40)[0];self.isize=struct.unpack_from('<H',s,88)[0];self.ds=max(32,struct.unpack_from('<H',s,254)[0]);self.gdt=2*self.bs if self.bs==1024 else self.bs
 def read(self,offset,n):
  assert offset>=0 and n>=0 and offset+n<=self.size
  self.f.seek(offset);b=self.f.read(n);assert len(b)==n;return b
 def inode(self,number):
  g,i=divmod(number-1,self.ipg);d=self.read(self.gdt+g*self.ds,self.ds)
  table=struct.unpack_from('<I',d,8)[0]
  if self.ds>=64:table|=struct.unpack_from('<I',d,40)[0]<<32
  return self.read(table*self.bs+i*self.isize,self.isize)
 def extents(self,b):
  magic,n,maximum,depth=struct.unpack_from('<4H',b);assert magic==0xf30a and n<=maximum and depth<=5
  out=[]
  for i in range(n):
   v=b[12+i*12:24+i*12]
   if depth:
    logical,lo,hi=struct.unpack_from('<IIH',v);out+=self.extents(self.read((lo+(hi<<32))*self.bs,self.bs))
   else:
    logical,length,hi,lo=struct.unpack('<IHHI',v);assert length<=32768,'Unwritten extent unsupported'
    out.append((logical,length,lo+(hi<<32)))
  return out
 def content(self,number):
  inode=self.inode(number);mode=struct.unpack_from('<H',inode)[0];assert mode&0xf000 in (0x4000,0x8000),'Only directory and regular-file inodes supported'
  size=struct.unpack_from('<I',inode,4)[0]+(struct.unpack_from('<I',inode,108)[0]<<32);assert size<16*1024*1024,'Selected metadata file exceeds bound'
  assert struct.unpack_from('<I',inode,32)[0]&0x80000,'Extent inode required'
  result=bytearray(size)
  for logical,length,physical in self.extents(inode[40:100]):
   start=logical*self.bs;n=min(length*self.bs,size-start)
   if n>0:result[start:start+n]=self.read(physical*self.bs,n)
  return bytes(result)
 def directory(self,number):
  b=self.content(number);p=0;out={}
  while p+8<=len(b):
   ino,rec,n,typ=struct.unpack_from('<IHBB',b,p);assert rec>=8 and p+rec<=len(b)
   if ino:out[b[p+8:p+8+n].decode('utf-8')]=ino
   p+=rec
  return out
 def lookup(self,path):
  number=2
  for name in pathlib.PurePosixPath(path).parts:
   if name=='/':continue
   number=self.directory(number)[name]
  return number
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('image',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();e=Ext4(a.image);a.output.mkdir(exist_ok=True,parents=True)
 print('root',list(e.directory(2)))
 base='/system/etc/vintf'
 try:d=e.directory(e.lookup(base))
 except KeyError:base='/etc/vintf';d=e.directory(e.lookup(base))
 out=[]
 for name,ino in d.items():
  if not name.endswith('.xml'):continue
  b=e.content(ino);(a.output/name).write_bytes(b);out.append(dict(path=base+'/'+name,size=len(b),sha256=hashlib.sha256(b).hexdigest()))
 (a.output/'extraction-manifest.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
