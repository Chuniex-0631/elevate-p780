"""Verify tracked repository links, Python syntax and retained evidence identities.
Offline only; output is an optional report, not a device operation.
"""
import argparse,ast,base64,hashlib,io,json,pathlib,posixpath,re,subprocess,urllib.parse,zipfile
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path);a=p.parse_args()
paths=subprocess.check_output(['git','ls-files','-z']).decode().split('\0');paths=[x for x in paths if x]
missing=[];count=0;md_count=0;py_count=0;json_count=0
for name in paths:
 f=pathlib.Path(name)
 if name.endswith('.py'):ast.parse(f.read_text(encoding='utf-8-sig'),filename=name);py_count+=1
 if name.endswith('.json'):json.loads(f.read_text());json_count+=1
 if not name.endswith('.md'):continue
 md_count+=1
 for v in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',f.read_text()):
  u=v.strip().split()[0].strip('<>')
  if u.startswith(('#','http://','https://','mailto:','data:')):continue
  target=pathlib.Path(posixpath.normpath(str(f.parent/urllib.parse.unquote(u.split('#')[0].split('?')[0]))));count+=1
  if not target.exists():missing.append({'source':name,'target':str(target)})
assert not missing,missing
j=pathlib.Path('evidence/journey/2026-10-10');manifest=json.loads((j/'input-manifest.json').read_text());raw=base64.b64decode((j/'p780-journey-config.zip.b64').read_bytes())
assert len(raw)==manifest['zip']['bytes'] and hashlib.sha256(raw).hexdigest()==manifest['zip']['sha256']
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 assert z.testzip() is None
 for e in manifest['entries']:
  b=z.read(e['path']);assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
  name=e['path'].replace('\\','/').split('/')[-1]
  if name in ('config.xml','version.txt'):assert (j/name).read_bytes()==b
  if name=='tcs-state.txt':assert (j/'tcs-state.utf8.txt').read_text()==b.decode('utf-16').replace('\r\n','\n')
dex=pathlib.Path('evidence/framework/2026-10-10')
config=json.loads((dex/'journey-bytecode.json').read_text())['methods']
performance=json.loads((dex/'performance-decision-methods.json').read_text())
for x in config:assert hashlib.sha256(bytes.fromhex(x['instructions_hex'])).hexdigest()==x['sha256']
for x in performance:assert hashlib.sha256(bytes.fromhex(x['original_insns_hex'])).hexdigest()==x['original_insns_sha256']
structure=pathlib.Path('evidence/analysis/repository-structure-20261011.json')
if structure.exists():
 for e in json.loads(structure.read_text())['preserved_moves']:
  actual=subprocess.check_output(['git','hash-object',e['to']]).decode().strip();assert actual==e['blob_sha'],e['to']
r={'tracked_files':len(paths),'markdown_files':md_count,'relative_path_links':count,'missing_path_links':missing,'python_syntax_files':py_count,'valid_json_files':json_count,'journey_original_zip_crc_sha_and_views':'passed','config_method_instruction_hashes':len(config),'performance_decision_instruction_hashes':len(performance),'preserved_move_blobs':'passed','limitations':['Path links only, not Markdown heading anchors or public URL availability.','No verification of Root, exploitation, runtime policy switches, or unavailable original JAR bytes.']}
if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(r,ensure_ascii=False,indent=2))
