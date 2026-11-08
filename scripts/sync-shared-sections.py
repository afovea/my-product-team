#!/usr/bin/env python3
"""Keep the shared "Model and sub-agents" section identical in every skill.

  python3 scripts/sync-shared-sections.py           write or refresh the section in every SKILL.md
  python3 scripts/sync-shared-sections.py --check   fail if any skill's copy differs, or its tier is missing

The canonical text is reference/model-and-sub-agents.md. Each skill carries its own copy, because
skills are installed one at a time (ZIP uploads) and cannot point at a file outside themselves.
The section sits before "## PPoT integration", or before "## Maintenance" where a skill has no PPoT
section. Each skill's usual tier is `metadata.model_tier` in its frontmatter.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCK = (ROOT / 'reference' / 'model-and-sub-agents.md').read_text(encoding='utf-8').strip() + '\n'
HEADING = BLOCK.splitlines()[0]
TIERS = ('most-capable', 'balanced', 'fast')


def with_block(text: str) -> str:
    """The skill text with exactly one current copy of the section, in its place."""
    text = re.sub(r'\n' + re.escape(HEADING) + r'\n.*?(?=\n## |\Z)', '', text, flags=re.S)
    for anchor in ('## PPoT integration', '## Maintenance'):
        i = text.find('\n' + anchor + '\n')
        if i >= 0:
            return text[:i].rstrip('\n') + '\n\n' + BLOCK + text[i:]
    return text.rstrip('\n') + '\n\n' + BLOCK


def tier(text: str):
    fm = text.split('---', 2)[1] if text.startswith('---') else ''
    m = re.search(r'^\s+model_tier:\s*"?([a-z-]+)"?\s*$', fm, re.M)
    return m.group(1) if m else None


def main(check: bool) -> int:
    problems = []
    skills = sorted(ROOT.glob('skills/*/SKILL.md'))
    for f in skills:
        text = f.read_text(encoding='utf-8')
        want = with_block(text)
        name = f.parent.name
        if tier(text) not in TIERS:
            problems.append(f'{name}: metadata.model_tier must be one of {", ".join(TIERS)}')
        if want != text:
            if check:
                problems.append(f'{name}: the "{HEADING[3:]}" section is missing or differs from reference/model-and-sub-agents.md')
            else:
                f.write_text(want, encoding='utf-8')
                print(f'updated {name}')
    for p in problems:
        print(f'  FAIL  {p}')
    if not problems and check:
        print(f'  ok    {len(skills)} skills carry the current "{HEADING[3:]}" section and a model tier')
    return 1 if problems else 0


def _selfcheck():
    t = '---\nname: x\nmetadata:\n  model_tier: "fast"\n---\n\n# X\n\n## PPoT integration\n\nText.\n'
    once = with_block(t)
    assert once.count(HEADING) == 1 and once.index(HEADING) < once.index('## PPoT integration')
    assert with_block(once) == once, 'refreshing an up-to-date skill must change nothing'
    assert tier(t) == 'fast'


if __name__ == '__main__':
    _selfcheck()
    sys.exit(main('--check' in sys.argv))
