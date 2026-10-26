"""Parse payload_empty.bin, extract the metadata signature and verify it with
ota_cert.pem using openssl.  Mirrors update_engine's metadata check:
sha256(header + manifest) is the signed value.
"""
import os
import pathlib
import struct
import subprocess

WORK = pathlib.Path(__file__).resolve().parent
OPENSSL = os.environ.get("OPENSSL", "openssl")
b = (WORK / "payload_empty.bin").read_bytes()
assert b[:4] == b"CrAU"
ver, ms, ss = struct.unpack(">QQI", b[4:24])
metadata = b[0:24 + ms]
s = b[24 + ms:24 + ms + ss]


def vi(buf, i):
    n = 0
    sh = 0
    while True:
        x = buf[i]
        i += 1
        n |= (x & 0x7F) << sh
        sh += 7
        if not x & 0x80:
            return n, i


def field(buf, want):
    i = 0
    while i < len(buf):
        key, i = vi(buf, i)
        wire = key & 7
        if wire == 2:
            l, i = vi(buf, i)
            value = buf[i:i + l]
            i += l
            if key >> 3 == want:
                return value
        elif wire == 0:
            _, i = vi(buf, i)
        elif wire == 5:
            i += 4
        else:
            raise SystemExit("unsupported wire type")
    return None


sm = field(s, 1)
sig = field(sm, 2)
(WORK / "metadata.bin").write_bytes(metadata)
(WORK / "sigdata.bin").write_bytes(sig)
pub = WORK / "pub.pem"
pub.write_bytes(subprocess.run(
    [OPENSSL, "x509", "-in", str(WORK / "ota_cert.pem"), "-pubkey", "-noout"],
    stdout=subprocess.PIPE, check=True).stdout)
r = subprocess.run([OPENSSL, "dgst", "-sha256", "-verify", str(pub),
                    "-signature", str(WORK / "sigdata.bin"), str(WORK / "metadata.bin")],
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
print(ver, ms, ss, "sig", len(sig))
print(r.returncode, r.stdout.decode(errors="ignore").strip())
