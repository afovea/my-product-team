#!/usr/bin/env python3
"""Build and check usability test reports. Standard library only.

  python3 report.py build STUDY.json [-o OUT.html] [--brand BRAND.json] [--bare]
  python3 report.py check REPORT.html [--names NAMES.txt]
  python3 report.py contrast [BRAND.json]

build     Puts the study data (references/data-format.md) and an optional brand
          profile (references/theming.md) into the template, then runs `check`.
          --bare leaves out the <!doctype>/<head> wrapper, for hosts that wrap
          the page themselves when publishing (claude.ai artifacts).
check     Validates a finished report: data references, scoring inputs, text
          encoding, participant names (--names: one real name per line, kept
          outside the report), and colour contrast in both themes.
contrast  Contrast check for a brand profile alone, or the template defaults.

Exit status is 1 when any check fails.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / 'assets' / 'report-template.html'
DATA_RE = re.compile(r'(<script type="application/json" id="study-data">)(.*?)(</script>)', re.S)
RESET = (':root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
         'body{margin:0;font:14px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}img{max-width:100%}[hidden]{display:none!important}')

# Text/background pairs the page actually draws, all held to WCAG AA (4.5:1).
PAIRS = [
    ('ink', 'bg'), ('ink', 'surface'), ('muted', 'surface'), ('muted', 'bg'),
    ('accent', 'surface'), ('surface', 'accent'), ('accent', 'accent-soft'),
    ('pass', 'pass-soft'), ('minor', 'minor-soft'), ('major', 'major-soft'), ('inv', 'inv-soft'),
    ('q1-on', 'q1'), ('q2-on', 'q2'), ('q3-on', 'q3'), ('q4-on', 'q4'), ('q5-on', 'q5'),
]
COLOUR_KEYS = {'bg', 'surface', 'ink', 'muted', 'line', 'accent', 'accent-soft', 'pass', 'pass-soft', 'minor', 'minor-soft',
               'major', 'major-soft', 'inv', 'inv-soft', 'frame', 'q1', 'q1-on', 'q2', 'q2-on', 'q3', 'q3-on', 'q4', 'q4-on', 'q5', 'q5-on'}
MOJIBAKE = re.compile(r'Â[ -¿]|â€|Ã[\u0080-¿]')


# ---------------------------------------------------------------- colour

def rgb(hex_: str):
    h = hex_.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    if not re.fullmatch(r'[0-9a-fA-F]{6}', h):
        return None
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a: str, b: str):
    ca, cb = rgb(a), rgb(b)
    if not ca or not cb:
        return None
    la, lb = sorted((luminance(ca), luminance(cb)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a: str, b: str, t: float) -> str:
    """t of the way from colour a to colour b."""
    ca, cb = rgb(a), rgb(b)
    return '#' + ''.join(f'{round(x + (y - x) * t):02X}' for x, y in zip(ca, cb))


def tokens(block: str) -> dict:
    return dict(re.findall(r'--([\w-]+):\s*([^;]+);', block))


def template_tokens(html: str):
    css = re.search(r'<style id="page-style">(.*?)</style>', html, re.S).group(1)
    light = tokens(re.search(r'^:root \{(.*?)^\}', css, re.S | re.M).group(1))
    dark = tokens(re.search(r'^:root\[data-theme="dark"\] \{(.*?)^\}', css, re.S | re.M).group(1))
    return light, dark


def contrast_report(light: dict, dark: dict):
    problems, lines = [], []
    for theme, t in (('light', light), ('dark', dark)):
        for fg, bg in PAIRS:
            if fg not in t or bg not in t:
                continue
            r = ratio(t[fg], t[bg])
            if r is None:
                lines.append(f'  warn  {theme}: cannot check {fg} on {bg} ({t[fg]} / {t[bg]}): use hex colours')
            elif r < 4.5:
                problems.append(f'{theme}: {fg} on {bg} is {r:.2f}:1, needs 4.5:1 ({t[fg]} on {t[bg]})')
    return problems, lines


# ----------------------------------------------------------------- brand

def font_stack(f: dict) -> str:
    return f'"{f["family"]}", {f.get("fallback", "system-ui, sans-serif")}'


def brand_layers(brand: dict, base_light: dict, base_dark: dict):
    """Return (css for the brand-style block, Google Fonts URL or None, effective light, effective dark)."""
    light = {k: v for k, v in (brand.get('light') or {}).items() if k in COLOUR_KEYS}
    dark = {k: v for k, v in (brand.get('dark') or {}).items() if k in COLOUR_KEYS}
    if 'accent' in light and 'accent-soft' not in light:
        light['accent-soft'] = mix(light['accent'], '#FFFFFF', 0.88)
    if 'accent' in light and 'accent' not in dark:
        # No dark palette given: keep the template's dark neutrals, tint the soft fill with the brand
        # accent, and lift the accent until it reads on both the surface and that fill.
        surface = dark.get('surface', base_dark['surface'])
        soft = dark.get('accent-soft') or mix(surface, light['accent'], 0.22)
        for t in (0.35, 0.45, 0.55, 0.65, 0.75, 0.85):
            acc = mix(light['accent'], '#FFFFFF', t)
            if min(ratio(acc, surface) or 0, ratio(acc, soft) or 0) >= 4.5:
                break
        dark['accent'], dark['accent-soft'] = acc, soft

    fonts = brand.get('fonts') or {}
    font_vars = {f'f-{role}': font_stack(f) for role, f in fonts.items() if role in ('display', 'body', 'mono') and f.get('family')}
    faces = ''.join(
        f'@font-face{{font-family:"{f["family"]}";src:url("{f["src"]}");font-weight:{f.get("weight", "100 900")};font-style:{f.get("style", "normal")};font-display:swap}}'
        for f in brand.get('fontFaces') or [])
    google = [f['google'] for f in fonts.values() if f.get('google')]
    url = ('https://fonts.googleapis.com/css2?' + '&'.join(f'family={g}' for g in google) + '&display=swap') if google else None

    decl = lambda d: ' '.join(f'--{k}: {v};' for k, v in d.items())
    css = faces
    if light or font_vars:
        css += f':root {{ {decl({**light, **font_vars})} }}'
    if dark:
        css += (f'@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ {decl(dark)} }} }}'
                f':root[data-theme="dark"] {{ {decl(dark)} }}')
    return css, url, {**base_light, **light}, {**base_dark, **dark}


# ----------------------------------------------------------------- build

def build(study: dict, brand: dict | None, bare: bool) -> str:
    html = TEMPLATE.read_text(encoding='utf-8')
    s = study.setdefault('study', {})
    if not s.get('brand'):  # the brand profile names the report's owner; the default profile otherwise
        s['brand'] = (brand or json.loads((HERE.parent / 'assets' / 'brand-default.json').read_text(encoding='utf-8'))).get('name', '')
    if brand:
        if brand.get('docType'):
            s.setdefault('docType', brand['docType'])
        if brand.get('logo'):
            s.setdefault('logo', brand['logo'])
        base_light, base_dark = template_tokens(html)
        css, url, _, _ = brand_layers(brand, base_light, base_dark)
        html = html.replace('<style id="brand-style"></style>', f'<style id="brand-style">{css}</style>', 1)
        if url:
            html = re.sub(r'(<link id="brand-fonts" rel="stylesheet" href=")[^"]*(">)', lambda m: m.group(1) + url.replace('&', '&amp;') + m.group(2), html, count=1)

    data = json.dumps(study, ensure_ascii=False, indent=2).replace('<', '\\u003c')
    html = DATA_RE.sub(lambda m: m.group(1) + '\n' + data + '\n' + m.group(3), html, count=1)
    title = s.get('title', 'Usability testing report')
    date = s.get('date', '')
    html = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}{" · " + date if date else ""}</title>', html, count=1)
    if bare:
        return html
    html = html.replace('<meta charset="utf-8">\n', '', 1)
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'<style>{RESET}</style></head><body>' + html + '</body></html>')


def esc(t: str) -> str:
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ----------------------------------------------------------------- check

def validate(d: dict) -> list[str]:
    """Problems that would make the report wrong or misleading."""
    p = []
    for key in ('study', 'participants', 'hypotheses'):
        if key not in d:
            p.append(f'missing "{key}"')
    if p:
        return p
    s = d['study']
    scale = s.get('seqScale', 5)
    if len(s.get('seqLabels') or []) not in (0, scale):
        p.append(f'seqLabels has {len(s["seqLabels"])} labels for a {scale}-point scale')
    pids = [x.get('id') for x in d['participants']]
    if len(set(pids)) != len(pids):
        p.append('participant IDs are not unique')
    known = set(pids)
    fids = []
    for h in d['hypotheses']:
        for t in h.get('tasks', []):
            tid = t.get('id', '?')
            for pid, r in (t.get('results') or {}).items():
                if pid not in known:
                    p.append(f'{tid}: result for unknown participant {pid}')
                if r.get('seq') is not None and not (1 <= r['seq'] <= scale):
                    p.append(f'{tid}: {pid} ease {r["seq"]} is outside 1–{scale}')
                if r.get('sev') not in (None, 'none', 'minor', 'major'):
                    p.append(f'{tid}: {pid} friction "{r["sev"]}" is not none, minor or major')
                if 'done' in r and r['done'] not in (True, False, None):
                    p.append(f'{tid}: {pid} done must be true, false or null')
            if t.get('override') and not (t['override'].get('reason') or '').strip():
                p.append(f'{tid}: verdict override has no reason')
            for f in t.get('findings', []):
                fids.append(f.get('id'))
                if f.get('type') not in ('major', 'minor', 'investigate', 'positive'):
                    p.append(f'{f.get("id")}: unknown finding type "{f.get("type")}"')
                for w in f.get('who', []):
                    if w not in known:
                        p.append(f'{f.get("id")}: names unknown participant {w}')
            for q in t.get('quotes', []):
                if q.get('who') not in known:
                    p.append(f'{tid}: quote from unknown participant {q.get("who")}')
    if len(set(fids)) != len(fids):
        p.append('finding IDs are not unique')
    for r in d.get('recommendations', []):
        for e in r.get('evidence', []):
            if e not in fids:
                p.append(f'recommendation "{r.get("title", "")[:40]}" cites {e}, which is not a finding')
    return p


def check(html: str, names: list[str]) -> int:
    fails, warns = [], []
    m = DATA_RE.search(html)
    if not m:
        print('  FAIL  no study-data block')
        return 1
    try:
        data = json.loads(m.group(2).replace('\\u003c', '<'))
    except json.JSONDecodeError as e:
        print(f'  FAIL  study data is not valid JSON: {e}')
        return 1
    fails += validate(data)

    text = html
    if MOJIBAKE.search(text):
        fails.append(f'garbled characters (e.g. "{MOJIBAKE.search(text).group(0)}"): the file was read with the wrong encoding')
    if '<!doctype' in html.lower()[:200] and '<meta charset="utf-8">' not in html[:400]:
        fails.append('standalone file without a UTF-8 declaration in its head')
    leaked = sorted({n for n in names if n and n in text})
    if leaked:
        fails.append(f'{len(leaked)} participant name(s) appear in the report')

    base_light, base_dark = template_tokens(html)
    brand_css = (re.search(r'<style id="brand-style">(.*?)</style>', html, re.S) or [None, ''])[1]
    light = {**base_light, **tokens((re.search(r'^(?:@font-face\{[^}]*\})*:root \{(.*?)\}', brand_css) or [None, ''])[1])}
    dark = {**base_dark, **tokens((re.search(r':root\[data-theme="dark"\] \{(.*?)\}', brand_css) or [None, ''])[1])}
    cp, cl = contrast_report(light, dark)
    fails += cp
    warns += cl

    s = data.get('study', {})
    for key, label in (('authoredBy', 'Authored by'), ('analysedBy', 'Analysed by')):
        if not (s.get(key) or s.get('author' if key == 'authoredBy' else '')):
            warns.append(f'  warn  "{label}" is not set')
    if not data.get('recommendations'):
        warns.append('  warn  no recommendations yet')

    for w in warns:
        print(w)
    for f in fails:
        print(f'  FAIL  {f}')
    if not fails:
        n_tasks = sum(len(h.get('tasks', [])) for h in data['hypotheses'])
        print(f'  ok    {len(data["participants"])} participants, {n_tasks} tasks, data references resolve, encoding clean, contrast passes in both themes')
    return 1 if fails else 0


# ------------------------------------------------------------------ main

def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in ('build', 'check', 'contrast'):
        print(__doc__)
        return 1
    cmd, args = argv[1], argv[2:]
    opt = lambda name: args[args.index(name) + 1] if name in args else None
    pos = [a for i, a in enumerate(args) if not a.startswith('--') and a != '-o' and (i == 0 or args[i - 1] not in ('-o', '--brand', '--names'))]

    if cmd == 'contrast':
        html = TEMPLATE.read_text(encoding='utf-8')
        light, dark = template_tokens(html)
        if pos:
            _, _, light, dark = brand_layers(json.loads(Path(pos[0]).read_text(encoding='utf-8')), light, dark)
        problems, lines = contrast_report(light, dark)
        for l in lines:
            print(l)
        for pr in problems:
            print(f'  FAIL  {pr}')
        if not problems:
            print('  ok    contrast passes in both themes')
        return 1 if problems else 0

    if cmd == 'build':
        src = Path(pos[0])
        study = json.loads(src.read_text(encoding='utf-8'))
        brand = json.loads(Path(opt('--brand')).read_text(encoding='utf-8')) if opt('--brand') else None
        out = Path(opt('-o') or src.with_suffix('.html'))
        html = build(study, brand, '--bare' in args)
        out.write_text(html, encoding='utf-8')
        print(out)
        return check(html, [])

    html = Path(pos[0]).read_text(encoding='utf-8')
    names = Path(opt('--names')).read_text(encoding='utf-8').splitlines() if opt('--names') else []
    return check(html, [n.strip() for n in names])


def _selfcheck():
    assert round(ratio('#000000', '#FFFFFF'), 1) == 21.0
    assert mix('#000000', '#FFFFFF', 0.5) == '#808080'
    assert validate({'study': {}, 'participants': [{'id': 'P1'}], 'hypotheses': [{'tasks': [{'id': 'T1', 'results': {'P2': {'seq': 9}}, 'findings': [], 'quotes': []}]}]}) \
        == ['T1: result for unknown participant P2', 'T1: P2 ease 9 is outside 1–5']


if __name__ == '__main__':
    _selfcheck()
    sys.exit(main(sys.argv))
