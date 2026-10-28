import hashlib
from pathlib import Path
import tempfile
import unittest

from audit import audit, inspect_log, read_saved, RC, XML


class AuditTests(unittest.TestCase):
    def test_missing_evidence_stays_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = audit(Path(tmp))
        self.assertEqual(len(report["missing"]), 7)
        self.assertEqual(report["verdicts"]["slot_switch"], "undetermined")

    def test_rc_and_manifest_are_separate_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rc, xml = root / RC, root / XML
            rc.parent.mkdir(parents=True)
            xml.parent.mkdir(parents=True)
            rc.write_text(" interface android.hardware.boot@1.0::IBootControl default\n"
                          " interface android.hardware.boot@1.1::IBootControl default\n")
            xml.write_text('<manifest><hal><name>android.hardware.boot</name>'
                           '<fqname>@1.1::IBootControl/default</fqname></hal></manifest>')
            before = rc.read_bytes(), xml.read_bytes()
            report = audit(root)
            self.assertEqual(before, (rc.read_bytes(), xml.read_bytes()))
        self.assertEqual(len(report["rc_interfaces"]), 2)
        self.assertEqual(len(report["manifest_fqnames"]), 1)
        self.assertEqual(report["verdicts"]["runtime_hal_registration"], "unverified")

    def test_unrelated_and_missing_success_logs_prove_nothing(self):
        report = inspect_log("no SetActiveBootSlot log\nAll post-install commands succeeded\n")
        self.assertEqual(report["events"], [])
        self.assertEqual(report["slot_switch_verdict"], "undetermined")

    def test_multiple_attempts_are_not_collapsed_into_a_verdict(self):
        report = inspect_log("InstallPlan: switch_slot_on_reboot: false\n"
            "ErrorCode::kUpdatedButNotActive\n"
            "InstallPlan: switch_slot_on_reboot: true\n"
            "Unable to call SetActiveBootSlot for slot A: denied\n"
            "https://example.invalid/?token=secret\n")
        self.assertEqual([e["value"] for e in report["events"] if
                          e["kind"] == "switch_slot_on_reboot"], ["false", "true"])
        self.assertEqual(report["slot_switch_verdict"], "undetermined")
        self.assertNotIn("secret", str(report))

    def test_local_hash_and_nonregular_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "log"
            path.write_bytes(b"line\r\n")
            text, digest = read_saved(path)
            self.assertEqual(text, "line\r\n")
            self.assertEqual(digest, hashlib.sha256(b"line\r\n").hexdigest())
            with self.assertRaises(ValueError):
                read_saved(Path(tmp))


if __name__ == "__main__":
    unittest.main()
