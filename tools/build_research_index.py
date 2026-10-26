"""Rebuild document navigation and evidence hashes from repository files, offline."""
import hashlib
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


def main():
    evidence = sorted(p for p in (ROOT/'evidence').rglob('*') if p.is_file())
    total = sum(p.stat().st_size for p in evidence)
    lines = ['# 证据清单', '', '> 由 `tools/build_research_index.py` 从实际文件生成（2026-10-26）。',
             '> 每项给出仓库内路径、字节数与 SHA-256；摘要说明见各专题报告。', '',
             f'共 **{len(evidence)}** 个文件，合计 **{total/1024/1024:.1f} MiB**。', '',
             '| 路径 | 字节 | SHA-256 |', '|---|---:|---|']
    for p in evidence:
        b = p.read_bytes()
        lines.append(f'| `{p.relative_to(ROOT).as_posix()}` | {len(b)} | `{hashlib.sha256(b).hexdigest()}` |')
    (ROOT/'docs/EVIDENCE_MANIFEST.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    groups = {}
    for directory in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name != '.git'):
        for p in directory.rglob('*.md'):
            if p != ROOT/'docs/index.md':
                groups.setdefault(p.relative_to(ROOT).parts[0],[]).append(p)
    groups['根目录'] = list(ROOT.glob('*.md'))
    lines = ['# 文档索引', '', '> 由 `tools/build_research_index.py` 生成（2026-10-26），含全部目录 Markdown。',
             '> 当前结论优先阅读 STATUS 与最新审计专题；历史报告保留阶段性假设。', '']
    for name, paths in groups.items():
        lines += [f'## {name}（{len(paths)}）', '', '| 文档 | 标题 |', '|---|---|']
        for p in sorted(paths):
            s = p.read_text(encoding='utf-8-sig')
            title = next((x.lstrip('# ').strip() for x in s.splitlines() if x.startswith('#')),p.stem)
            title = title.replace('|','\\|')
            if '\ufffd' in s:
                title += '（部分损坏）'
            rel = p.relative_to(ROOT).as_posix()
            link = '../'+quote(rel, safe='/.-_')
            lines.append(f'| [{rel}]({link}) | {title} |')
        lines.append('')
    (ROOT/'docs/index.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(f'Indexed {sum(map(len,groups.values()))} documents and {len(evidence)} evidence files')


if __name__ == '__main__':
    main()
