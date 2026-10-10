#!/usr/bin/env python3
"""Read-only intake audit. Never print raw tokens, device IDs or personal log lines."""
from __future__ import annotations
import hashlib, json, re, zipfile, sys, collections, pathlib
P=pathlib.Path
def digest(x):return hashlib.sha256(x).hexdigest()
def decode(x):
    if x[:2] in (b'\xff\xfe',b'\xfe\xff'): return x.decode('utf-16','replace'),"utf-16"
    try: return x.decode("utf-8-sig"),"utf-8"
    except UnicodeDecodeError: return x.decode("latin-1","replace"),"latin-1"
def normalize(name):
    s=name.replace("\\","/").lstrip("./")
    chunks=s.split("/")
    for i,c in enumerate(chunks):
        if c in ("hand5g_final_audit","hand5g_debloat_audit"):return "/".join(chunks[i+1:])
    return s
def audit():
    files=[p for p in P('.').rglob("*") if p.is_file() and '.git' not in p.parts and not any(x in p.parts for x in ('reports',))]
    cache={str(p):p.read_bytes() for p in files if p.stat().st_size<7_000_000}
    bysha=collections.defaultdict(list)
    for p,raw in cache.items():bysha[digest(raw)].append(p)
    zips=[]
    for path,raw in cache.items():
        if not path.lower().endswith(".zip"):continue
        try:
            with zipfile.ZipFile(P(path)) as z:
                bad=z.testzip()
                entries={normalize(i.filename):(i.filename,i.file_size,digest(z.read(i))) for i in z.infolist() if not i.is_dir()}
                normalized={} 
                for key,val in entries.items():normalized[key]=val
                folder=path[:-4]
                corresponding={normalize(str(p)):(str(p),len(data),digest(data)) for p,data in cache.items() if p.startswith(folder+'/')}
                equal={key:(key in corresponding and val[2]==corresponding[key][2]) for key,val in normalized.items()}
                missing=[k for k in normalized if k not in corresponding]
                extra=[k for k in corresponding if k not in normalized]
                mismatch=[k for k in normalized if k in corresponding and not equal[k]]
                zips.append({"path":path,"bytes":len(raw),"sha256":digest(raw),"crc_ok":bad is None,"entries":len(entries),"folder":folder if corresponding else None,"folder_files":len(corresponding),
                            "missing_in_folder":missing[:80],"extra_in_folder":extra[:80],"different_vs_folder":mismatch[:80],
                            "internal_prefix_examples":[v[0] for v in list(entries.values())[:8]]})
        except Exception as e:zips.append({"path":path,"error":type(e).__name__})
    matched=[]
    pattern={
        "email": re.compile(r"(?<![.\w-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",re.I),
        "phone": re.compile(r"(?<!\d)(?:\+?81[- ]?)?0\d{1,4}[- ]?\d{2,4}[- ]?\d{3,4}(?!\d)"),
        "imei": re.compile(r"\b\d{15}\b"),
        "mac": re.compile(r"\b(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}\b",re.I),
        "ip": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        "credentials_words": re.compile(r"(?:password|passwd|secret|auth[_-]?token|session[_-]?id|bearer|cookie|imei|imsi|iccid|serialno)\b",re.I)
    }
    inspect=["hand5g_native_api_paths.txt","hand5g_tz_whitelist.txt","hand5g_update_activity.txt","hand5g_update_log.txt",
        "hand5g_packages_all_phase3.txt","hand5g_packages_installed_phase3.txt"]
    inspect.extend([p for p in cache if p.startswith("hand5g_debloat_audit/") or p.startswith("hand5g_final_audit/")])
    for path in sorted(set(inspect)):
        if path not in cache:continue
        raw=cache[path]
        txt,encoding=decode(raw)
        counts={k:len(p.findall(txt)) for k,p in pattern.items()}
        lines=txt.splitlines()
        matched.append({"path":path,"bytes":len(raw),"sha256":digest(raw),"encoding":encoding,"lines":len(lines),
            "sensitivity_signal_counts":counts,"empty":not txt.strip(),
            "line_count_package":sum(x.startswith("package:") for x in lines),
            "package_names_only":False})
    package_names={}
    for path in cache:
        if re.search(r"packages_(?:installed|all)_phase3\.txt$|/10_packages_user0\.txt$|/14_packages_including_uninstalled\.txt$|/01_packages\.txt$",path):
            txt,_=decode(cache[path])
            found=set(re.findall(r"(?:^|\n)package:([A-Za-z0-9._-]+)",txt))
            package_names[path]={"count":len(found)}
    apiApks=[]
    for path,raw in cache.items():
        if path.lower().endswith(".apk"):
            try:
                with zipfile.ZipFile(P(path)) as z:
                    apiApks.append({"path":path,"sha256":digest(raw),"size":len(raw),"valid":z.testzip() is None,
                                    "entries":len(z.namelist()),"contains_dex":any(k.endswith(".dex") for k in z.namelist()),
                                    "has_signature_metadata":any(k.startswith("META-INF/") for k in z.namelist())})
            except Exception as e:apiApks.append({"path":path,"error":str(type(e).__name__)})
    return {"file_count":len(files),"bytes":sum(len(x) for x in cache.values()),
        "identical_groups":[{"sha256":sha,"paths":paths} for sha,paths in bysha.items() if len(paths)>1],
        "zips":zips,"sensitive_text_files":matched,"package_file_counts":package_names,"apk":apiApks}
if __name__=="__main__":
    obj=audit()
    P("intake-metadata.json").write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
    print("INTAKE_RESULT_START")
    print(json.dumps(obj,ensure_ascii=False,indent=2)[:55000])
    print("INTAKE_RESULT_END")
