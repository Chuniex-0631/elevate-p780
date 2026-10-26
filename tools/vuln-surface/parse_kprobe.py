import struct
from pathlib import Path
b = Path(r"C:\Users\ASUS Vivobook\Desktop\RakutenHand5G\52-vuln-surface-analysis-20261025\kprobe.bin").read_bytes()
names = ["netlink","packet","rawip","io_uring","perf_event","bpf","kgsl","ion","binder","dma_heap"]
for i, n in enumerate(names):
    if 8*i+8 <= len(b):
        v = struct.unpack_from("<q", b, 8*i)[0]
        print(f"{i+1:2d} {n:10s} -> {v}")
