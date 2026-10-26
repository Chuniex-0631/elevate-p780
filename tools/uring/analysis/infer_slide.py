import bisect
import collections
import pathlib
import re

base = pathlib.Path("work/kernel/P780-kernel-symbol-recovery")
syms = []
for line in (base / "kernel.kallsyms").read_text().splitlines():
    p = line.split()
    if len(p) >= 3:
        try:
            syms.append((int(p[0], 16), p[2]))
        except ValueError:
            pass
syms.sort()
addrs = [a for a, _ in syms]

def size_of(a):
    i = bisect.bisect_right(addrs, a)
    return (addrs[i] - a) if i < len(addrs) else 0x100

hot_names = [
    "__arm64_sys_getuid", "netlink_recvmsg", "__arm64_sys_recvmsg",
    "__arm64_sys_recvfrom", "el0_svc", "invoke_syscall", "do_el0_svc",
    "el0_svc_common", "netlink_getname", "__arm64_sys_getsockname",
    "sock_recvmsg", "__arm64_sys_geteuid", "__arm64_sys_getgid",
]
hot = []
for a, n in syms:
    base_name = n.split("$")[0]
    if base_name in hot_names:
        hot.append((base_name, a, size_of(a)))
print("hot funcs:", [(n, hex(a), hex(s)) for n, a, s in hot])

ips = []
for line in pathlib.Path("work/ipdump.txt").read_text(errors="ignore").splitlines():
    m = re.search(r"IP (0x[0-9a-f]+)", line)
    if m:
        ips.append(int(m.group(1), 16))
print("samples:", len(ips))

votes = collections.Counter()
for ip in ips:
    for _, a, s in hot:
        b = ip - a
        o = b % 0x200000
        if 0 < o < s:
            votes[b - o] += 1

print("top votes:")
for sl, c in votes.most_common(6):
    print(f"  slide={sl:#x} votes={c}")

# coverage score for top candidates
def in_any_func(x):
    i = bisect.bisect_right(addrs, x) - 1
    if i < 0:
        return False
    return x < addrs[i] + size_of(addrs[i])

for sl, c in votes.most_common(3):
    cov = sum(1 for ip in ips if in_any_func(ip - sl))
    hotcov = sum(1 for ip in ips for _, a, s in hot if a <= ip - sl < a + s)
    print(f"slide={sl:#x} votes={c} coverage={cov}/{len(ips)} hot={hotcov}")
