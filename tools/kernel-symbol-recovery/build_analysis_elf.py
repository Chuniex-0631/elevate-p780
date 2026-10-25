"""Create a byte-preserving analysis ELF around a verified raw ARM64 Image.
Sections/permissions are synthetic. No relocation writes or executable patching.
This is not the original build ELF, a boot image, or a flashable artifact.
"""
import argparse,hashlib,json,pathlib,struct
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('image',type=pathlib.Path);p.add_argument('symbols',type=pathlib.Path)
p.add_argument('output',type=pathlib.Path);a=p.parse_args()
raw=a.image.read_bytes();rows=[]
for line in a.symbols.read_text().splitlines():
 addr,typ,name=line.split(' ',2);rows.append((int(addr,16),typ,name))
base=next(addr for addr,typ,name in rows if name=='_text')
end=next(addr for addr,typ,name in rows if name=='_end')
bss=next(addr for addr,typ,name in rows if name=='__bss_start')
assert bss==base+len(raw) and end-base==struct.unpack_from('<Q',raw,16)[0]
assert all(base<=addr<=end for addr,typ,name in rows)
local=[r for r in rows if r[1].islower()]
global_=[r for r in rows if not r[1].islower()]
strings=bytearray(b'\0');symbols=bytearray(24)
for addr,typ,name in local+global_:
 no=len(strings);strings+=name.encode('ascii')+b'\0'
 bind=0 if typ.islower() else (2 if typ in 'WV' else 1)
 kind=2 if typ in 'tTW' else 1
 section=2 if addr>=bss else 1
 symbols+=struct.pack('<IBBHQQ',no,(bind<<4)|kind,0,section,addr,0)
shstrings=b'\0.image\0.bss\0.symtab\0.strtab\0.shstrtab\0'
names={name:shstrings.index(name.encode()+b'\0') for name in ['.image','.bss','.symtab','.strtab','.shstrtab']}
def align(x,n=8):return (x+n-1)//n*n
image_off=0x1000;sym_off=align(image_off+len(raw));str_off=sym_off+len(symbols)
shstr_off=str_off+len(strings);shoff=align(shstr_off+len(shstrings))
out=bytearray(shoff+6*64)
out[:64]=struct.pack('<16sHHIQQQIHHHHHH',b'\x7fELF\x02\x01\x01'+bytes(9),2,183,1,base,64,shoff,0,64,56,1,64,6,5)
out[64:120]=struct.pack('<IIQQQQQQ',1,7,image_off,base,base,len(raw),end-base,0x1000)
out[image_off:image_off+len(raw)]=raw
out[sym_off:sym_off+len(symbols)]=symbols
out[str_off:str_off+len(strings)]=strings
out[shstr_off:shstr_off+len(shstrings)]=shstrings
sections=[bytes(64),
 struct.pack('<IIQQQQIIQQ',names['.image'],1,7,base,image_off,len(raw),0,0,0x1000,0),
 struct.pack('<IIQQQQIIQQ',names['.bss'],8,3,bss,image_off+len(raw),end-bss,0,0,8,0),
 struct.pack('<IIQQQQIIQQ',names['.symtab'],2,0,0,sym_off,len(symbols),4,len(local)+1,8,24),
 struct.pack('<IIQQQQIIQQ',names['.strtab'],3,0,0,str_off,len(strings),0,0,1,0),
 struct.pack('<IIQQQQIIQQ',names['.shstrtab'],3,0,0,shstr_off,len(shstrings),0,0,1,0)]
out[shoff:]=b''.join(sections)
assert out[image_off:image_off+len(raw)]==raw
a.output.write_bytes(out)
print(json.dumps({'output':a.output.name,'symbol_entries':len(rows),'image_section_sha256':hashlib.sha256(out[image_off:image_off+len(raw)]).hexdigest(),
 'bss_size':end-bss,'elf_sha256':hashlib.sha256(out).hexdigest(),'limitations':['Synthetic broad .image section; no original section permissions or function sizes.','Raw image bytes preserved; relocation records not applied.','Not original debug vmlinux, not flashable, no runtime KASLR addresses.']},indent=2))
