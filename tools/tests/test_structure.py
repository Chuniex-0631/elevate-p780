"""Check the complete tool catalog, compatibility entry points and source moves."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]


class StructureTests(unittest.TestCase):
    def test_catalog_covers_all_tracked_tool_directories(self):
        names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        directories = {p.split('/')[1] for p in names if p.startswith('tools/') and len(p.split('/')) > 2}
        catalog = json.loads((ROOT/'tools/catalog.json').read_text(encoding='utf-8-sig'))
        listed = [Path(row['path']).name for row in catalog]
        self.assertEqual(len(listed), len(set(listed)))
        self.assertEqual(directories, set(listed))
        for row in catalog:
            self.assertTrue((ROOT/row['path']/'README.md').is_file(), row['path'])

    def test_relocated_code_retains_git_bytes(self):
        migration = json.loads((ROOT/'docs/reference/structure-migration.json').read_text(encoding='utf-8-sig'))
        for move in migration['moves']:
            if Path(move['to']).suffix not in ('.py', '.c'):
                continue
            raw = subprocess.check_output(['git', 'show', ':'+move['to']], cwd=ROOT)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), move['sha256'], move['to'])

    def test_legacy_config_import_remains_compatible(self):
        legacy = runpy.run_path(str(ROOT/'tools/summarize_config.py'))
        canonical = runpy.run_path(str(ROOT/'tools/kernel-config/summarize_config.py'))
        self.assertEqual(legacy['IMPORTANT'], canonical['IMPORTANT'])
        self.assertTrue(callable(legacy['read_config']))

    def test_release_version_and_notes_agree(self):
        version = (ROOT/'VERSION').read_text(encoding='utf-8-sig').strip()
        self.assertTrue((ROOT/'docs/releases'/f'v{version}.md').is_file())
        self.assertTrue((ROOT/'release/Elevate-1.0.apk').is_file())


if __name__ == '__main__':
    unittest.main()
