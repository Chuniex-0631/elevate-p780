"""Build deterministic navigation and evidence hashes from tracked files, offline."""
import argparse
import hashlib
import subprocess
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


def render(root=ROOT):
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode('utf-8')
    paths = [root / name for name in sorted(name for name in names.split('\0') if name)]
    evidence = [p for p in paths if p.relative_to(root).parts[0] == 'evidence']
    total = sum(p.stat().st_size for p in evidence)
    lines = ['# 证据清单', '', '> 由 `tools/build_research_index.py` 从 Git 跟踪文件生成。',
             '> 每项给出仓库内路径、字节数与 SHA-256；摘要说明见各专题报告。', '',
             f'共 **{len(evidence)}** 个文件，合计 **{total/1024/1024:.1f} MiB**。', '',
             '| 路径 | 字节 | SHA-256 |', '|---|---:|---|']
    for path in evidence:
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        lines.append(f'| `{path.relative_to(root).as_posix()}` | {path.stat().st_size} | `{digest}` |')
    manifest = '\n'.join(lines) + '\n'
    groups = {}
    for path in paths:
        if path.suffix == '.md' and path != root / 'docs/index.md':
            parts = path.relative_to(root).parts
            groups.setdefault(parts[0] if len(parts) > 1 else '根目录', []).append(path)
    lines = ['# 文档索引', '', '> 由 `tools/build_research_index.py` 从 Git 跟踪文件生成。',
             '> 当前结论优先阅读 STATUS 与最新专题；历史报告保留阶段性假设。', '']
    for name, documents in groups.items():
        lines += [f'## {name}（{len(documents)}）', '', '| 文档 | 标题 |', '|---|---|']
        for path in documents:
            content = path.read_text(encoding='utf-8-sig')
            title = next((line.lstrip('# ').strip() for line in content.splitlines()
                          if line.startswith('#')), path.stem).replace('|', '\\|')
            if '\ufffd' in content:
                title += '（部分损坏）'
            relative = path.relative_to(root).as_posix()
            lines.append(f'| [{relative}](../{quote(relative, safe="/.-_")}) | {title} |')
        lines.append('')
    return {'docs/EVIDENCE_MANIFEST.md': manifest, 'docs/index.md': '\n'.join(lines) + '\n'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail on stale generated files without writing')
    args = parser.parse_args()
    stale = []
    for name, content in render().items():
        path = ROOT / name
        if not path.exists() or path.read_text(encoding='utf-8-sig') != content:
            stale.append(name)
            if not args.check:
                path.write_text(content, encoding='utf-8', newline='\n')
    if args.check and stale:
        parser.exit(1, 'Stale documents: ' + ', '.join(stale) + '\nRun python tools/build_research_index.py\n')
    print('Generated documents are current.' if args.check else 'Updated: ' + (', '.join(stale) or 'no changes'))


if __name__ == '__main__':
    main()
