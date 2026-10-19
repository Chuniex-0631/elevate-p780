import sys, pathlib, zipfile, json, hashlib, struct, argparse
project=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(project/'.research-deps'))
sys.path.insert(0,str(project/'research/oemlock'))
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent/'oemlock'))
from dex_tables import Tables,DCode
from androguard.core.axml import AXMLPrinter
from androguard.core.dex import DEX
from loguru import logger
logger.remove()
parser=argparse.ArgumentParser(description='Offline QTIDiagServices audit; no device requests')
parser.add_argument('--capture-dir',type=pathlib.Path,required=True)
parser.add_argument('--historical-root',type=pathlib.Path,required=True)
args=parser.parse_args();root=args.historical_root;dest=args.capture_dir
f=dest/'QTIDiagServices.apk'
out=[];declared=[]
with zipfile.ZipFile(f) as z:
    xml=AXMLPrinter(z.read('AndroidManifest.xml')).get_xml()
    (dest/'diag-manifest.xml').write_bytes(xml)
    for n in z.namelist():
        if not n.endswith('.dex'):continue
        raw=z.read(n); cm=Tables(raw)
        d=DEX(raw)
        declared.extend(dict(cls=m.get_class_name(),name=m.get_name(),descriptor=m.get_descriptor(),flags=m.get_access_flags_string()) for c in d.get_classes() for m in c.get_methods())
        for mid,code in cm.definitions:
            ref=cm.methods[mid]; size=struct.unpack_from('<I',raw,code+12)[0]
            b=raw[code+16:code+16+size*2]; ins=[]; offset=0
            for x in DCode(cm,0,size,b).get_instructions():
                ins.append(dict(offset=offset,op=x.get_name(),args=x.get_output()));offset+=x.get_length()
            assert offset==len(b)
            out.append(dict(dex=n,cls=ref.c,method=ref.n+ref.d,offset=code,sha256=hashlib.sha256(b).hexdigest(),insns_hex=b.hex(),instructions=ins))
(dest/'diag-declarations.json').write_text(json.dumps(declared,indent=2),encoding='utf-8')
(dest/'diag-methods.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
(dest/'diag-disassembly.txt').write_text('\n'.join(m['cls']+' '+m['method']+'\n'+'\n'.join(f"{x['offset']:04x} {x['op']} {x['args']}" for x in m['instructions']) for m in out),encoding='utf-8')
manifest=[]
for name,old in [('QTIDiagServices.apk','09/P780-static-20261018-220912/files/system_ext/app/QTIDiagServices/QTIDiagServices.apk'),('libDiagService.so','09/P780-static-20261018-220912/files/system_ext/lib64/libDiagService.so'),('services.jar','09/P780-services.jar')]:
    p=dest/name;sha=hashlib.sha256(p.read_bytes()).hexdigest()
    manifest.append(dict(name=name,size=p.stat().st_size,sha256=sha,historical_file=old,historical_match=hashlib.sha256((root/old).read_bytes()).hexdigest()==sha))
(dest/'input-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2));print('methods',len(out))
