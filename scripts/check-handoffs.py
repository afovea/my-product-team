#!/usr/bin/env python3
"""Check that skill handoffs name real skills and go both ways.

Every skill says who it takes work from and hands work to, in a "## Works with" section (or, for
skills with a Handoffs table, the table plus a "Takes work from" line). If A hands to B, B should
say it takes from A, and the reverse; otherwise a skill cannot route back the way it came.
`ppot` and `route` are exempt: every skill reads ppot, and route hands to every skill.
The router's roster must list every other skill, or it cannot send work there.

  python3 scripts/check-handoffs.py      exits non-zero on any problem
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXEMPT = {'ppot', 'route'}
NAME = re.compile(r'`([a-z][a-z-]+)`')


def links(text: str):
    take = re.search(r'\*\*Takes work from:\*\*(.*)', text) or re.search(r'\nTakes work from (.*?)\. Workflows', text)
    hand = re.search(r'\*\*Hands work to:\*\*(.*)', text)
    table = re.search(r'\n## Handoffs\n(.*?)\n\n', text, re.S)
    hands = set(NAME.findall(hand.group(1))) if hand else set()
    if table:
        hands |= set(NAME.findall(table.group(1)))
    return (set(NAME.findall(take.group(1))) if take else None), hands


def main() -> int:
    skills = {p.name for p in (ROOT / 'skills').iterdir() if (p / 'SKILL.md').is_file()}
    take, hand, problems = {}, {}, []
    for n in sorted(skills):
        t, h = links((ROOT / 'skills' / n / 'SKILL.md').read_text(encoding='utf-8'))
        if t is None:
            problems.append(f'{n}: no "Works with" section saying who it takes work from')
            t = set()
        take[n], hand[n] = t, h
        for x in sorted((t | h) - skills - {'brief', 'ask', 'learn'}):
            problems.append(f'{n}: names `{x}`, which is not a skill')
    for a in sorted(skills):
        for b in sorted(hand[a] & skills - EXEMPT):
            if a not in EXEMPT and a not in take[b]:
                problems.append(f'{a} hands work to {b}, but {b} does not say it takes work from {a}')
        for b in sorted(take[a] & skills - EXEMPT):
            if a not in EXEMPT and a not in hand[b]:
                problems.append(f'{a} takes work from {b}, but {b} does not say it hands work to {a}')
    route = ROOT / 'skills' / 'route' / 'SKILL.md'
    if route.is_file():
        roster = route.read_text(encoding='utf-8').split('## Roster', 1)[-1].split('\n## ', 1)[0]
        for n in sorted(skills - {'route'} - set(NAME.findall(roster))):
            problems.append(f'route: the roster does not list `{n}`, so the router cannot send work there')
    for p in problems:
        print(f'  FAIL  {p}')
    if not problems:
        print(f'  ok    {len(skills)} skills name real skills, and every handoff goes both ways')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
