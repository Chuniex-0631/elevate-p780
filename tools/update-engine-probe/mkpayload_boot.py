"""Build a test payload that writes one 4096-byte block to partition "boot"
(target slot A when the device is on slot B).

This is the smallest payload that exercises update_engine's real block-write
path: partition info + REPLACE operation + payload signature.  The data is a
0xAA pattern; the target slot is already unbootable, so this is a write-path
test, not a flashing step.
"""
import hashlib
import os
import pathlib
import struct
import subprocess

WORK = pathlib.Path(__file__).resolve().parent
OPENSSL = os.environ.get("OPENSSL", "openssl")
KEY = WORK / "ota_key.pem"


def varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def tag(field, wire):
    return varint((field << 3) | wire)


def fv(field, value):
    return tag(field, 0) + varint(value)


def fb(field, data):
    return tag(field, 2) + varint(len(data)) + data


def sig_blob(sig):
    return fb(1, fb(2, sig) + tag(3, 5) + struct.pack("<I", len(sig)))


def sign(data):
    return subprocess.run([OPENSSL, "dgst", "-sha256", "-sign", str(KEY)],
                          input=data, stdout=subprocess.PIPE, check=True).stdout


def build():
    block = 4096
    data = b"\xAA" * block
    extent = fv(1, 0) + fv(2, 1)
    op = (fv(1, 0) + fv(2, 0) + fv(3, len(data)) +
          fb(8, hashlib.sha256(data).digest()) + fb(6, extent))
    pinfo = fv(1, len(data)) + fb(2, hashlib.sha256(data).digest())
    part = fb(1, b"boot") + fb(7, pinfo) + fb(8, op)

    sigs_len = len(sig_blob(b"\0" * 256))
    manifest = (fv(3, block) + fv(14, 4102444800) +
                fv(4, len(data)) + fv(5, sigs_len) + fb(13, part))
    header = (b"CrAU" + struct.pack(">Q", 2) +
              struct.pack(">Q", len(manifest)) + struct.pack(">I", sigs_len))
    metadata = header + manifest
    meta_sigs = sig_blob(sign(metadata))

    # update_engine hashes header+manifest (metadata) and the data blobs into
    # the payload signature; the metadata-signature blob itself is skipped.
    signed_region = header + manifest + data
    payload_sigs = sig_blob(sign(signed_region))
    assert len(payload_sigs) == sigs_len

    payload = header + manifest + meta_sigs + data + payload_sigs
    (WORK / "payload_bootblock.bin").write_bytes(payload)
    print("payload", len(payload), "metadata", len(metadata),
          "signature", len(meta_sigs))


if __name__ == "__main__":
    build()
