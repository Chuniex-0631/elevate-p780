"""Offline repository checks. Importing this module performs no checks or writes."""
import argparse
import ast
import base64
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import urllib.parse
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def tracked_paths(root):
    raw = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root)
    return [p for p in raw.decode('utf-8').split('\0') if p]


def check_sources(root, paths):
    missing = []
    counts = dict(markdown_files=0, relative_path_links=0,
                  python_syntax_files=0, valid_json_files=0)
    for name in paths:
        path = root / name
        if path.suffix == '.py':
            ast.parse(path.read_text(encoding='utf-8-sig'), filename=name)
            counts['python_syntax_files'] += 1
        elif path.suffix == '.json':
            json.loads(path.read_text(encoding='utf-8-sig'))
            counts['valid_json_files'] += 1
        elif path.suffix == '.md':
            counts['markdown_files'] += 1
            for value in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8-sig')):
                value = value.strip()
                if not value:
                    continue
                url = value[1:value.index('>')] if value.startswith('<') and '>' in value else value.split()[0]
                parsed = urllib.parse.urlsplit(url)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = path.parent / urllib.parse.unquote(parsed.path)
                counts['relative_path_links'] += 1
                if not target.exists():
                    missing.append(dict(source=name, target=parsed.path))
    if missing:
        raise ValueError('Missing local links: ' + json.dumps(missing, ensure_ascii=False))
    return dict(counts, missing_path_links=missing)


def check_evidence(root):
    j = root.joinpath('evidence/journey/2026-10-10')
    manifest = json.loads((j / 'input-manifest.json').read_text(encoding='utf-8-sig'))
    raw = base64.b64decode((j / 'p780-journey-config.zip.b64').read_bytes())
    if not (len(raw) == manifest['zip']['bytes'] and hashlib.sha256(raw).hexdigest() == manifest['zip']['sha256']):
        raise ValueError("Evidence integrity mismatch: len(raw) == manifest['zip']['bytes'] and hashlib.sha256(raw).hexdigest() == manifest['zip']['sha256']")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if not z.testzip() is None:
            raise ValueError('Evidence integrity mismatch: z.testzip() is None')
        for e in manifest['entries']:
            archive_path = e['path'].replace('\\', '/')
            archive_names = {name.replace('\\', '/'): name for name in z.namelist()}
            b = z.read(archive_names[archive_path])
            if not (len(b) == e['bytes'] and hashlib.sha256(b).hexdigest() == e['sha256']):
                raise ValueError("Evidence integrity mismatch: len(b) == e['bytes'] and hashlib.sha256(b).hexdigest() == e['sha256']")
            name = e['path'].replace('\\', '/').split('/')[-1]
            if name in ('config.xml', 'version.txt'):
                if not (j / name).read_bytes() == b:
                    raise ValueError('Evidence integrity mismatch: (j / name).read_bytes() == b')
            if name == 'tcs-state.txt':
                if not (j / 'tcs-state.utf8.txt').read_text(encoding='utf-8-sig') == b.decode('utf-16').replace('\r\n', '\n'):
                    raise ValueError("Evidence integrity mismatch: (j / 'tcs-state.utf8.txt').read_text(encoding='utf-8-sig') == b.decode('utf-16').replace('\\r\\n', '\\n')")
    dex = root.joinpath('evidence/framework/2026-10-10')
    config = json.loads((dex / 'journey-bytecode.json').read_text(encoding='utf-8-sig'))['methods']
    performance = json.loads((dex / 'performance-decision-methods.json').read_text(encoding='utf-8-sig'))
    for x in config:
        if not hashlib.sha256(bytes.fromhex(x['instructions_hex'])).hexdigest() == x['sha256']:
            raise ValueError("Evidence integrity mismatch: hashlib.sha256(bytes.fromhex(x['instructions_hex'])).hexdigest() == x['sha256']")
    for x in performance:
        if not hashlib.sha256(bytes.fromhex(x['original_insns_hex'])).hexdigest() == x['original_insns_sha256']:
            raise ValueError("Evidence integrity mismatch: hashlib.sha256(bytes.fromhex(x['original_insns_hex'])).hexdigest() == x['original_insns_sha256']")
    structure = root.joinpath('evidence/analysis/repository-structure-20261011.json')
    if structure.exists():
        for e in json.loads(structure.read_text(encoding='utf-8-sig'))['preserved_moves']:
            actual = subprocess.check_output(['git', 'hash-object', e['to']], cwd=root).decode().strip()
            if not actual == e['blob_sha']:
                raise ValueError(e['to'])

    return dict(journey_original_zip_crc_sha_and_views='passed',
                config_method_instruction_hashes=len(config),
                performance_decision_instruction_hashes=len(performance),
                preserved_move_blobs='passed')


def verify(root=ROOT):
    paths = tracked_paths(root)
    return dict(tracked_files=len(paths), **check_sources(root, paths),
                **check_evidence(root), limitations=[
                    'Path links only, not Markdown heading anchors or public URL availability.',
                    'No verification of Root, exploitation, runtime policy switches, or unavailable original JAR bytes.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional JSON report; relative to current directory')
    args = parser.parse_args()
    try:
        report = verify()
    except (ValueError, OSError, SyntaxError, KeyError, zipfile.BadZipFile, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Verification failed: {error}\n')
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding='utf-8')
    print(rendered, end='')


if __name__ == '__main__':
    main()
