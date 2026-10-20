"""Offline header check only; not a policy parser or semantic diff."""
import argparse, hashlib, json, pathlib, struct
p=argparse.ArgumentParser(description=__doc__)
p.add_argument("live",type=pathlib.Path)
p.add_argument("disk",type=pathlib.Path)
p.add_argument("--output",type=pathlib.Path,required=True)
a=p.parse_args()
expected=["a4d6851e984a0232dea7cbabbf600f87eeb74b94005a260ecbbca756bcad1409","77f077d8c95b38929aed0434c9c56ca6158c24d90c169ee2644d490684111b79"]
items=[]
for label,path,want in zip(["running","disk"],[a.live,a.disk],expected):
    raw=path.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=want: raise SystemExit("Unexpected input hash: "+label)
    magic,n=struct.unpack_from("<II",raw)
    if magic!=0xf97cff8c or raw[8:8+n]!=b"SE Linux": raise SystemExit("Unexpected header")
    version,config,symbols,objects=struct.unpack_from("<4I",raw,8+n)
    items.append(dict(role=label,size=len(raw),sha256=digest,version=version,
        config_offset=12+n,config=hex(config),config_bytes=raw[12+n:16+n].hex(),
        symbol_tables=symbols,object_tables=objects))
result=dict(date="2026-10-20",inputs=items,header_xor=hex(int(items[0]["config"],16)^int(items[1]["config"],16)),
    semantic_diff_status="BLOCKED_TOOLING",limitations=[
    "Independent direct header read; no reuse of the pair-specific record comparator.",
    "No SETools/libsepol semantic comparison performed.",
    "No header normalization, phone access, or source modification."])
a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
