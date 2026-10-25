"""Read-only, image-specific independent kallsyms verification.
No imports from vmlinux-to-elf. Offsets are discovery outputs, not guessed again.
Checks encoding, all markers, relative-base relocation, every name/address,
and structural anchors. Does not prove vulnerability or runtime addresses.
"""
import argparse, collections, hashlib, json, pathlib, struct
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('image',type=pathlib.Path)
p.add_argument('symbols',type=pathlib.Path)
p.add_argument('output',type=pathlib.Path)
a=p.parse_args(); raw=a.image.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='6df574af40d260c670c32bdee9ceaca023739850d62851d55f77234b89d4f373'
O={'offsets':0x17e3a18,'relative_base':0x188cc70,'num_syms':0x188cc78,
   'names':0x188cc80,'markers':0x1c349e0,'token_table':0x1c35478,'token_index':0x1c357a0,
   'rela_start':0x2308758,'rela_end':0x25af028}
n=struct.unpack_from('<Q',raw,O['num_syms'])[0]; assert n==173205
base_records=[]
for off in range(O['rela_start'],O['rela_end'],24):
    addr,info,addend=struct.unpack_from('<QQq',raw,off)
    base=addend & ((1<<64)-1)
    if info==1027 and addr-base==O['relative_base']:
        base_records.append((off,base))
assert len(base_records)==1
base=base_records[0][1]
assert struct.unpack_from('<Q',raw,O['relative_base'])[0]==0
ix=struct.unpack_from('<256H',raw,O['token_index'])
tokens=[]; pos=O['token_table']; offsets=[]
for i in range(256):
    offsets.append(pos-O['token_table'])
    end=raw.index(b'\0',pos,O['token_index'])
    tokens.append(raw[pos:end]);pos=end+1
assert tuple(offsets)==ix
assert not any(raw[pos:O['token_index']])
rows=[line.split(' ',2) for line in a.symbols.read_text().splitlines()]
assert len(rows)==n
marker_count=(n+255)//256
markers=struct.unpack_from('<%dI'%marker_count,raw,O['markers'])
pos=O['names']; decoded=[]; marker_matches=0
for i in range(n):
    if i%256==0:
        assert markers[i//256]==pos-O['names']; marker_matches+=1
    size=raw[pos];pos+=1
    assert size>0 and pos+size<=O['markers']
    text=b''.join(tokens[t] for t in raw[pos:pos+size]).decode('ascii');pos+=size
    assert text[0] in 'ABCDGIRSTUVWabcdgirstuvwNn?'
    relative=struct.unpack_from('<I',raw,O['offsets']+i*4)[0]
    addr=base+relative
    assert rows[i]==[f'{addr:016x}',text[0],text[1:]],(i,rows[i],text)
    decoded.append((addr,text[0],text[1:]))
assert pos<=O['markers'] and not any(raw[pos:O['markers']])
assert O['offsets']+n*4<=O['relative_base']
addresses=[r[0] for r in decoded]
assert all(x<=y for x,y in zip(addresses,addresses[1:]))
by_name=collections.defaultdict(list)
for addr,typ,name in decoded: by_name[name].append(addr)
anchors={}
for name,offset in [('_text',0),('_head',0),('kallsyms_offsets',O['offsets']),
 ('kallsyms_relative_base',O['relative_base']),('kallsyms_num_syms',O['num_syms']),
 ('kallsyms_names',O['names']),('kallsyms_markers',O['markers']),
 ('kallsyms_token_table',O['token_table']),('kallsyms_token_index',O['token_index'])]:
    if name.startswith('kallsyms_') and name not in by_name:
        anchors[name]='NOT_IN_SYMBOL_NAMES; table checked structurally'
    else:
        assert by_name[name]==[base+offset],(name,by_name[name])
        anchors[name]='PASS'
assert len(by_name['linux_banner'])==1
banner_offset=by_name['linux_banner'][0]-base
assert raw[banner_offset:].startswith(b'Linux version 5.4.233-qgki-gea5245e94afe-dirty ')
anchors['linux_banner']='PASS'
header_size=struct.unpack_from('<Q',raw,16)[0]
assert by_name['_end']==[base+header_size]
assert len(by_name['__bss_start'])==1
bss_start=by_name['__bss_start'][0]-base
result={'input_sha256':hashlib.sha256(raw).hexdigest(),'tool':'independent Python standard-library verifier',
 'symbols_checked':n,'all_names_and_addresses_match':True,'token_count':256,
 'markers_checked':marker_matches,'all_markers_match':True,'addresses_nondecreasing':True,
 'relative_base_source':'R_AARCH64_RELATIVE record; raw slot is zero before relocation',
 'relative_base_relocation_file_offset':hex(base_records[0][0]),
 'static_link_base':hex(base),'anchors':anchors,
 'symbol_types':dict(collections.Counter(r[1] for r in decoded)),
 'unique_names':len(by_name),'duplicate_names':sum(len(v)>1 for v in by_name.values()),
 'image_file_size':len(raw),'header_image_size':header_size,
 'end_symbol_offset':by_name['_end'][0]-base,'bss_start_offset':bss_start,
 'file_ends_at_bss_start':len(raw)==bss_start,
 'symbols_beyond_file':sum(x>=base+len(raw) for x in addresses),
 'all_symbols_within_header_span_inclusive':all(base<=x<=base+header_size for x in addresses),
 'names_decoded_end':hex(pos),'table_file_offsets':{k:hex(v) for k,v in O.items()},
 'limitations':['Discovery offsets come from vmlinux-to-elf 1.4.0; this independently validates decoding, not independent table discovery.',
 'Static link addresses are not the running KASLR addresses.',
 'No original DWARF, C types, exact structure layouts, or vulnerability assessment recovered.',
 'No original boot header or chunk acquisition logs supplied; these checks do not authenticate acquisition.']}
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
