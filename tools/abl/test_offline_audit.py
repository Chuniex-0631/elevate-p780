"""Offline regression checks: malformed DER, hash semantics, PE bounds, real ABL."""
import datetime
import hashlib
import tempfile
import subprocess
import sys
import unittest
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from firehose_screen import der_end, screen
from control_flow_audit import audit


class OfflineTests(unittest.TestCase):
    def test_truncated_der(self):
        for data in (b'', b'0', b'0\x80', b'0\x84\x01', b'0\x82\xff\xffx'):
            self.assertIsNone(der_end(data, 0))

    def test_certificate_hash_and_storage_hints(self):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Synthetic offline test')])
        now = datetime.datetime.now(datetime.timezone.utc)
        cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
            .public_key(key.public_key()).serial_number(1).not_valid_before(now)
            .not_valid_after(now+datetime.timedelta(days=1)).sign(key, hashes.SHA256()))
        raw = cert.public_bytes(serialization.Encoding.DER)
        target = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/'test.bin'
            original = b'not a loader\0UFS\0'+raw+b'0\x82\xff\xff'
            p.write_bytes(original)
            report = screen(p, target)
            self.assertEqual(len(report['certificates']), 1)
            self.assertTrue(report['root_der_digest_match_offsets'])
            self.assertEqual(report['ufs_compatibility'], 'unverified')
            self.assertEqual(report['device_acceptance'], 'not_tested')
            self.assertNotEqual(report['certificates'][0]['spki_sha256'], target)
            self.assertEqual(p.read_bytes(), original)
            self.assertEqual(screen(p, '0'*64)['signature_screen'], 'no_scanned_root_der_digest_match')
            script = str(Path(__file__).with_name('firehose_screen.py'))
            for args in ([str(p), '--output', str(p)], [str(p), '--pkhash', 'c19a5029']):
                result = subprocess.run([sys.executable, script]+args, capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(p.read_bytes(), original)

    def test_real_abl_identity_and_loop(self):
        p = Path(__file__).resolve().parents[2]/'evidence/20261026/abl/abl_lzma.bin'
        b, off, sections, instructions, refs = audit(p)
        self.assertEqual(hashlib.sha256(b).hexdigest(), '8bca951a25f8bd19a38bca333843f7a982b589d738d6a518bbb934c5afd87437')
        self.assertEqual(off, 0xb8)
        by_addr = {x.address:x for x in instructions}
        self.assertEqual(by_addr[0x310ec].op_str, '#0x312d0')
        self.assertEqual(by_addr[0x3120c].op_str, 'w8, w8, #1')
        with tempfile.TemporaryDirectory() as folder:
            bad = Path(folder)/'bad.bin'
            bad.write_bytes(b'\0'*128)
            with self.assertRaises(ValueError):
                audit(bad)


if __name__ == '__main__':
    unittest.main()
