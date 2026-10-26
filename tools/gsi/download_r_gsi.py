import urllib.request, shutil, os, sys, time
url='https://dl.google.com/developers/android/rvc/images/gsi/aosp_arm64-exp-RP1A.200720.009-6720564-019b517d.zip'
out=r'55-avb-gsi-20261026\aosp_arm64_R_RP1A.200720.009.zip'
req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
t0=time.time()
with urllib.request.urlopen(req, timeout=60) as r, open(out,'wb') as f:
    total=int(r.headers.get('Content-Length','0'))
    got=0
    while True:
        b=r.read(1024*1024)
        if not b: break
        f.write(b); got+=len(b)
        if got % (64*1024*1024) < 1024*1024:
            print(f'{got/1048576:.0f} MiB / {total/1048576:.0f} MiB', flush=True)
print('done', os.path.getsize(out), 'bytes in', round(time.time()-t0,1), 's', flush=True)
