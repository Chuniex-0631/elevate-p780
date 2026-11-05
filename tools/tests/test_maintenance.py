"""Regression tests for offline maintenance; no device or network access."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify = load('verify_repository')
index = load('build_research_index')


class MaintenanceTests(unittest.TestCase):
    def test_links_unicode_spaces_and_external_schemes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'a b.md').write_text('# Target', encoding='utf-8')
            (root / 'README.md').write_text(
                '[space](a%20b.md) [angle](<a b.md>) [anchor](#ok) '
                '[web](https://example.org) [other](custom://resource)', encoding='utf-8')
            result = verify.check_sources(root, ['README.md'])
            self.assertEqual(result['relative_path_links'], 2)

    def test_missing_link_has_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'README.md').write_text('[bad](missing.md)', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'README.md'):
                verify.check_sources(root, ['README.md'])

    def test_invalid_source_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'bad.json').write_text('{', encoding='utf-8')
            with self.assertRaises(json.JSONDecodeError):
                verify.check_sources(root, ['bad.json'])
            (root / 'bad.py').write_text('def broken(', encoding='utf-8')
            with self.assertRaises(SyntaxError):
                verify.check_sources(root, ['bad.py'])

    def test_generator_tracks_only_versioned_files_and_detects_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'evidence').mkdir()
            (root / 'evidence/data.bin').write_bytes(b'original')
            (root / 'evidence/local.bin').write_bytes(b'ignored')
            (root / 'README.md').write_text('# Hello | title', encoding='utf-8')
            (root / 'local.md').write_text('# Ignore', encoding='utf-8')
            (root / 'Z.md').write_text('# Uppercase', encoding='utf-8')
            (root / 'a.md').write_text('# Lowercase', encoding='utf-8')
            names = b'a.md\0Z.md\0README.md\0evidence/data.bin\0'
            with patch.object(index.subprocess, 'check_output', return_value=names):
                first = index.render(root)
                self.assertEqual(first, index.render(root))
                self.assertLess(first['docs/index.md'].index('[Z.md]'), first['docs/index.md'].index('[a.md]'))
                self.assertNotIn('local.bin', first['docs/EVIDENCE_MANIFEST.md'])
                self.assertNotIn('local.md', first['docs/index.md'])
                self.assertIn('Hello \\| title', first['docs/index.md'])
                (root / 'evidence/data.bin').write_bytes(b'modified')
                self.assertNotEqual(first, index.render(root))

    def test_tampered_evidence_fails_explicitly(self):
        import base64
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            journey = root / 'evidence/journey/2026-10-10'
            journey.mkdir(parents=True)
            (journey / 'input-manifest.json').write_text(
                json.dumps({'zip': {'bytes': 999, 'sha256': 'wrong'}}), encoding='utf-8')
            (journey / 'p780-journey-config.zip.b64').write_bytes(base64.b64encode(b'bad'))
            with self.assertRaises(ValueError):
                verify.check_evidence(root)

    def test_verifier_works_outside_repository_under_optimization(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, '-O', str(TOOLS / 'verify_repository.py')],
                                    cwd=temp, capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['preserved_move_blobs'], 'passed')


if __name__ == '__main__':
    unittest.main()
