import struct
from pathlib import Path
b = Path(r"C:\Users\ASUS Vivobook\Desktop\RakutenHand5G\52-vuln-surface-analysis-20261025\uring.bin").read_bytes()
names = ["io_uring_setup","io_uring_enter","register_buffers","register_files"]
for i, n in enumerate(names):
    if 8*i+8 <= len(b):
        print(f"{i+1} {n:18s} -> {struct.unpack_from('<q', b, 8*i)[0]}")
