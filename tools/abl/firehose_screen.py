"""Read local candidate files only; extract DER certificate and UFS hints.

Requires cryptography. A root DER digest match is a screening lead, never
proof of a valid Qualcomm image signature, target acceptance or UFS operation.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def der_end(data, off):
    if off+2 > len(data) or data[off] != 0x30:
        return None
    size = data[off+1]
    head = 2
    if size & 0x80:
        n = size & 0x7f
        if not 1 <= n <= 4 or off+2+n > len(data):
            return None
        size = int.from_bytes(data[off+2:off+2+n], 'big')
        head += n
    end = off+head+size
    return end if end <= len(data) else None


def screen(path, expected=None):
    data = Path(path).read_bytes()
    certs = []
    offset = 0
    while True:
        offset = data.find(b'\x30', offset)
        if offset < 0:
            break
        end = der_end(data, offset)
        if end is not None:
            raw = data[offset:end]
            try:
                cert = x509.load_der_x509_certificate(raw)
                # Require exact DER object, disallow trailing data interpretations.
                if cert.public_bytes(Encoding.DER) != raw:
                    raise ValueError('noncanonical certificate')
            except ValueError:
                cert = None
            if cert is not None:
                self_signed = False
                if cert.subject == cert.issuer:
                    try:
                        cert.verify_directly_issued_by(cert)
                        self_signed = True
                    except Exception:
                        # Unsupported algorithms and invalid signatures remain unverified.
                        self_signed = False
                certs.append(dict(offset=offset, bytes=len(raw),
                    subject=cert.subject.rfc4514_string(), issuer=cert.issuer.rfc4514_string(),
                    self_signature_verified=self_signed,
                    der_sha256=hashlib.sha256(raw).hexdigest(),
                    der_sha384=hashlib.sha384(raw).hexdigest(),
                    spki_sha256=hashlib.sha256(cert.public_key().public_bytes(
                        Encoding.DER, PublicFormat.SubjectPublicKeyInfo)).hexdigest()))
                offset = end
                continue
        offset += 1
    strings = [(m.start(), m.group().decode('ascii')) for m in re.finditer(rb'[\x20-\x7e]{4,}', data)]
    hints = [dict(offset=o, text=s[:240]) for o,s in strings
             if re.search(r'ufs|emmc|MemoryName|MSM_ID|HW_ID|OEM_ID|MODEL_ID|SW_ID|SOC_VERS',s,re.I)]
    roots = [c for c in certs if c['self_signature_verified']]
    match = [c['offset'] for c in roots if expected and expected in (c['der_sha256'], c['der_sha384'])]
    return dict(file=Path(path).name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
        elf_magic=data.startswith(b'\x7fELF'), certificates=certs, storage_and_id_hints=hints,
        expected_pkhash_supplied=bool(expected), root_der_digest_match_offsets=match,
        signature_screen=('root_der_digest_match_needs_image_validation' if match else
                          'no_scanned_root_der_digest_match' if expected else 'not_compared'),
        ufs_compatibility='unverified', device_acceptance='not_tested',
        limitations=['DER scan does not bind certificates to a Qualcomm signing header or verify image signature.',
                    'A root may be absent, malformed, multi-root or use another hash scheme; no match is not a universal rejection.',
                    'Strings and file names do not prove storage initialization, LUN support, authorization or read capability.'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('files', nargs='+', type=Path)
    p.add_argument('--pkhash', help='full SHA256/SHA384 root DER digest, never an abbreviated prefix')
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    if a.output and any(a.output.resolve() == f.resolve() for f in a.files):
        p.error('output must not overwrite an input file')
    expected = a.pkhash.lower().removeprefix('0x') if a.pkhash else None
    if expected and not re.fullmatch(r'(?:[0-9a-f]{64}|[0-9a-f]{96})', expected):
        p.error('--pkhash requires 64 or 96 hex digits')
    result = [screen(f, expected) for f in a.files]
    text = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
    if a.output:
        a.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
