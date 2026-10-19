import sys,pathlib,json,re,io,lzma,argparse,hashlib
project=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(project/'.research-deps'))
from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
parser=argparse.ArgumentParser(description='Offline AArch64 JNI ELF audit; no execution')
parser.add_argument('--capture-dir',type=pathlib.Path,required=True)
args=parser.parse_args();dest=args.capture_dir
p=dest/'libDiagService.so'
with p.open('rb') as f:
 e=ELFFile(f);sym=e.get_section_by_name('.dynsym');symbols=[];funcs=[]
 for s in sym.iter_symbols():
  if not s.name:continue
  symbols.append(dict(name=s.name,address=s['st_value'],size=s['st_size'],section=s['st_shndx']))
  if s['st_info']['type']=='STT_FUNC' and s['st_shndx']!='SHN_UNDEF' and s['st_size']:
   sec=e.get_section(s['st_shndx']);b=sec.data()[s['st_value']-sec['sh_addr']:s['st_value']-sec['sh_addr']+s['st_size']]
   ins=[dict(address=i.address,op=i.mnemonic,args=i.op_str) for i in Cs(CS_ARCH_ARM64,CS_MODE_ARM).disasm(b,s['st_value'])]
   assert len(ins)*4==len(b)
   funcs.append(dict(name=s.name,address=s['st_value'],size=len(b),sha256=hashlib.sha256(b).hexdigest(),insns_hex=b.hex(),instructions=ins))
 dynamic=e.get_section_by_name('.dynamic');deps=[t.needed for t in dynamic.iter_tags() if t.entry.d_tag=='DT_NEEDED']
 rel=[]
 for sec in e.iter_sections():
  if not hasattr(sec,'iter_relocations'):continue
  st=e.get_section(sec['sh_link'])
  for r in sec.iter_relocations():
   if r['r_info_sym']:rel.append(dict(offset=r['r_offset'],symbol=st.get_symbol(r['r_info_sym']).name))
 sections=[dict(name=s.name,address=s['sh_addr'],offset=s['sh_offset'],size=s['sh_size']) for s in e.iter_sections()]
 debug=e.get_section_by_name('.gnu_debugdata')
 if debug:
  mini=ELFFile(io.BytesIO(lzma.decompress(debug.data())));st=mini.get_section_by_name('.symtab')
  for s in st.iter_symbols():
   if s['st_info']['type']!='STT_FUNC' or not s['st_size']:continue
   for sec in e.iter_sections():
    if sec['sh_addr']<=s['st_value']<sec['sh_addr']+sec['sh_size']:
     b=sec.data()[s['st_value']-sec['sh_addr']:s['st_value']-sec['sh_addr']+s['st_size']]
     ins=[dict(address=i.address,op=i.mnemonic,args=i.op_str) for i in Cs(CS_ARCH_ARM64,CS_MODE_ARM).disasm(b,s['st_value'])]
     assert len(ins)*4==len(b)
     funcs.append(dict(name=s.name,address=s['st_value'],size=len(b),sha256=hashlib.sha256(b).hexdigest(),insns_hex=b.hex(),instructions=ins));break
 plt=e.get_section_by_name('.plt');rp=e.get_section_by_name('.rela.plt');rs=e.get_section(rp['sh_link'])
 plt_entries=[dict(address=plt['sh_addr']+32+i*16,symbol=rs.get_symbol(r['r_info_sym']).name) for i,r in enumerate(rp.iter_relocations())]
 for func in funcs:
  for ins in func['instructions']:
   if ins['op']=='bl' and ins['args'].startswith('#0x'):
    target=int(ins['args'][1:],16)
    matches=[x['symbol'] for x in plt_entries if x['address']==target]
    if matches:ins['target_symbol']=matches[0]
 result=dict(needed=deps,symbols=symbols,relocations=rel,plt_entries=plt_entries,sections=sections,functions=funcs,strings=[m.group().decode('ascii') for m in re.finditer(rb'[ -~]{5,}',p.read_bytes())])
(dest/'diag-elf.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(dest/'diag-native-disassembly.txt').write_text('\n'.join(x['name']+'\n'+'\n'.join(f"{i['address']:x} {i['op']} {i['args']}" for i in x['instructions']) for x in funcs),encoding='utf-8')
print('NEEDED',deps);print('SYMBOLS',json.dumps(symbols));print('STRINGS',json.dumps(result['strings']))
