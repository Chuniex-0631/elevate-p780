import struct
from pathlib import Path
b = Path(r"C:\Users\ASUS Vivobook\Desktop\RakutenHand5G\52-vuln-surface-analysis-20261025\uring2.bin").read_bytes()
names = ["setup_fd","sq_mmap","cq_mmap","sqes_mmap","enter_rc","cqe_user_data","cqe_res"]
for i, n in enumerate(names):
    if 8*i+8 <= len(b):
        print(f"{n:14s} -> {struct.unpack_from('<q', b, 8*i)[0]}")
