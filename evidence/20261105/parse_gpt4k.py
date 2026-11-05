import struct, zlib, sys
b=open(sys.argv[1] if len(sys.argv)>1 else r"C:\Users\ASUSVI~1\AppData\Local\Temp\gpt_sde.bin","rb").read()
S=4096
h=b[S:S+92]
print("sig",h[0:8],"hsize",struct.unpack_from("<I",h,12)[0])
crc=struct.unpack_from("<I",h,16)[0]
ent_lba=struct.unpack_from("<Q",h,72)[0]; num=struct.unpack_from("<I",h,80)[0]; esize=struct.unpack_from("<I",h,84)[0]; ecrc=struct.unpack_from("<I",h,88)[0]
print("crc",hex(crc),"ent_lba",ent_lba,"num",num,"esize",esize,"ecrc",hex(ecrc))
ents=b[ent_lba*S:ent_lba*S+num*esize]
print("ecrc calc",hex(zlib.crc32(ents)&0xffffffff))
for i in range(num):
    e=ents[i*esize:(i+1)*esize]
    if e[0:16]==b"\0"*16: continue
    name=e[56:128].decode("utf-16le").rstrip("\0")
    attr=struct.unpack_from("<Q",e,48)[0]
    if name in ("boot_a","boot_b","vbmeta_a","vbmeta_b","vendor_boot_a","vendor_boot_b","misc"):
        print(i,name,"attr",hex(attr),"entry_off",hex(ent_lba*S+i*esize))