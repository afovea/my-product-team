#!/usr/bin/env python3
"""Keep the shared sections identical in every skill, and check every skill's metadata.

  python3 scripts/sync-shared-sections.py           write or refresh the shared sections in every SKILL.md
  python3 scripts/sync-shared-sections.py --check   fail if a copy differs, or a skill lacks a tier or version

The canonical text of each shared section lives in reference/ (SECTIONS below). Each skill carries its
own copy, because skills are installed one at a time (ZIP uploads) and cannot point at a file outside
themselves. The sections sit in SECTIONS order, before "## PPoT integration", or before
"## Maintenance" where a skill has no PPoT section. Each skill also declares `metadata.model_tier`
and a semantic `metadata.version` in its frontmatter.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ['handing-over-work.md', 'model-and-sub-agents.md']
BLOCKS = [(ROOT / 'reference' / n).read_text(encoding='utf-8').strip() + '\n' for n in SECTIONS]
HEADINGS = [b.splitlines()[0] for b in BLOCKS]
TIERS = ('most-capable', 'balanced', 'fast')


def with_blocks(text: str) -> str:
    """The skill text with exactly one current copy of each shared section, in its place."""
    for heading in HEADINGS:
        text = re.sub(r'\n' + re.escape(heading) + r'\n.*?(?=\n## |\Z)', '', text, flags=re.S)
    joined = '\n'.join(BLOCKS)
    for anchor in ('## PPoT integration', '## Maintenance'):
        i = text.find('\n' + anchor + '\n')
        if i >= 0:
            return text[:i].rstrip('\n') + '\n\n' + joined + text[i:]
    return text.rstrip('\n') + '\n\n' + joined


def meta(text: str, key: str):
    fm = text.split('---', 2)[1] if text.startswith('---') else ''
    m = re.search(r'^\s+' + key + r':\s*"?([^"\s]+)"?\s*$', fm, re.M)
    return m.group(1) if m else None


def main(check: bool) -> int:
    problems = []
    skills = sorted(ROOT.glob('skills/*/SKILL.md'))
    for f in skills:
        text = f.read_text(encoding='utf-8')
        want = with_blocks(text)
        name = f.parent.name
        if meta(text, 'model_tier') not in TIERS:
            problems.append(f'{name}: metadata.model_tier must be one of {", ".join(TIERS)}')
        if not re.fullmatch(r'\d+\.\d+\.\d+', meta(text, 'version') or ''):
            problems.append(f'{name}: metadata.version must be a version number such as "1.0.0"')
        if want != text:
            if check:
                problems.append(f'{name}: a shared section is missing or differs from reference/ '
                                f'({", ".join(h[3:] for h in HEADINGS)})')
            else:
                f.write_text(want, encoding='utf-8')
                print(f'updated {name}')
    for p in problems:
        print(f'  FAIL  {p}')
    if not problems and check:
        print(f'  ok    {len(skills)} skills carry the current shared sections, a model tier and a version')
    return 1 if problems else 0


def _selfcheck():
    t = '---\nname: x\nmetadata:\n  model_tier: "fast"\n  version: "1.0.0"\n---\n\n# X\n\n## PPoT integration\n\nText.\n'
    once = with_blocks(t)
    assert all(once.count(h) == 1 for h in HEADINGS)
    assert once.index(HEADINGS[0]) < once.index(HEADINGS[1]) < once.index('## PPoT integration')
    assert with_blocks(once) == once, 'refreshing an up-to-date skill must change nothing'
    assert meta(t, 'model_tier') == 'fast' and meta(t, 'version') == '1.0.0'


if __name__ == '__main__':
    _selfcheck()
    sys.exit(main('--check' in sys.argv))
