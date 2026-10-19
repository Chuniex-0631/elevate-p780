import sys,pathlib,json,zipfile,argparse
sys.path.insert(0,str(pathlib.Path.cwd()/'.research-deps'))
from loguru import logger
logger.remove()
from androguard.core.axml import AXMLPrinter
parser=argparse.ArgumentParser(description='Offline manifest audit over caller inventory')
parser.add_argument('root',type=pathlib.Path)
parser.add_argument('--output',type=pathlib.Path,default=pathlib.Path(__file__).parent)
args=parser.parse_args();root=args.root
ns='{http://schemas.android.com/apk/res/android}'
out=[];errors=[]
for item in json.loads((args.output/'caller-inventory.json').read_text()):
 f=root/item['file']
 if f.suffix!='.apk':continue
 try:
  with zipfile.ZipFile(f) as z:x=AXMLPrinter(z.read('AndroidManifest.xml')).get_xml_obj()
  hits=[dict(tag=e.tag,attrs={k.replace(ns,''):v for k,v in e.attrib.items()}) for e in x.iter() if 'OEM_UNLOCK' in str(e.attrib)]
  if hits:out.append(dict(file=item['file'],sha256=item['sha256'],package=x.get('package'),sharedUserId=x.get(ns+'sharedUserId'),hits=hits))
 except Exception as e:errors.append(dict(file=item['file'],error=str(e)))
p=args.output/'permission-manifests.json';p.write_text(json.dumps(dict(hits=out,errors=errors),indent=2),encoding='utf-8')
print(p.read_text())

