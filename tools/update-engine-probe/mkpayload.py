"""Build a minimal update_engine full payload (empty partition list) and a
1135-byte otacerts.zip replacement containing our test certificate.

Requires: openssl on PATH (or OPENSSL env), ota_key.pem and ota_cert.pem in
this directory.  Outputs payload_empty.bin and otacerts_ours.zip.
"""
import os
import pathlib
import struct
import subprocess
import zipfile

WORK = pathlib.Path(__file__).resolve().parent
OPENSSL = os.environ.get("OPENSSL", "openssl")
KEY = WORK / "ota_key.pem"
CERT = WORK / "ota_cert.pem"


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


def fld_varint(field, value):
    return tag(field, 0) + varint(value)


def fld_bytes(field, data):
    return tag(field, 2) + varint(len(data)) + data


def fld_fixed32(field, value):
    return tag(field, 5) + struct.pack("<I", value)


def build_manifest():
    # DeltaArchiveManifest: block_size=3. Empty partitions list.
    return fld_varint(3, 4096)


def build_signatures(sig):
    sig_msg = fld_bytes(2, sig) + fld_fixed32(3, len(sig))
    return fld_bytes(1, sig_msg)


def main():
    manifest = build_manifest()
    sigs_len = len(build_signatures(b"\0" * 128))
    header = (b"CrAU" + struct.pack(">Q", 2) +
              struct.pack(">Q", len(manifest)) + struct.pack(">I", sigs_len))
    metadata = header + manifest
    sig = subprocess.run([OPENSSL, "dgst", "-sha256", "-sign", str(KEY)],
                         input=metadata, stdout=subprocess.PIPE, check=True).stdout
    sigs = build_signatures(sig)
    assert len(sigs) == sigs_len
    (WORK / "payload_empty.bin").write_bytes(header + manifest + sigs)
    (WORK / "metadata.bin").write_bytes(metadata)
    print("payload", 24 + len(manifest) + len(sigs),
          "metadata", len(metadata), "signature", len(sig))

    target = 1135  # original /system/etc/security/otacerts.zip size
    base = WORK / "otacerts_ours.zip"
    with zipfile.ZipFile(base, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(CERT, "releasekey.x509.pem")
    pad = target - len(base.read_bytes())
    if pad < 2:
        raise SystemExit("certificate zip does not fit in 1135 bytes")
    for extra in range(64):
        with zipfile.ZipFile(base, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(CERT, "releasekey.x509.pem")
            z.comment = b"A" * max(0, pad - 2 - extra)
        data = base.read_bytes()
        if len(data) == target:
            break
        if len(data) < target:
            base.write_bytes(data + b"\0" * (target - len(data)))
            break
    print("otacerts size", base.stat().st_size)


if __name__ == "__main__":
    main()
