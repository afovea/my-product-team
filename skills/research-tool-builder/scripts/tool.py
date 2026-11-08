#!/usr/bin/env python3
"""Build and check research tools. Standard library only.

  python3 tool.py build STUDY.json --method METHOD --run RUN --device DEVICE [--delivery DELIVERY]
                        [--only moderator|participant] [--brand BRAND.json] [--prototype PAGE.html] [-o TOOL.html]
  python3 tool.py check TOOL.html

build   Builds every copy the test setup needs, each a single HTML file with the shared shell
        (assets/shell.html), one method module (assets/methods/), the study content and the setup,
        checks each one, and prints who gets which file, where data is kept and how it comes back.
        The setup is the answers to the setup questions (references/foundations.md, section 9):
          --run       in-person | remote | self-run | mixed      who runs the sessions
          --device    moderator | participant | both             whose device runs the tool
          --delivery  how the participant gets it, when it runs on their device:
                        participant-file   a file you send them
                        shared-link        a published claude.ai link (one page for moderators and participants;
                                           built without the page wrapper and policy the host supplies)
                        hosted             your own website or intranet
                      moderator-device when only the moderator's device runs it (the default then)
        --only builds one of the copies. METHOD is a module in assets/methods/:
        card-sort, classification, tree-test, first-click, stimulus, observation.
        --brand takes a research-reporter brand profile, so tools and reports match.
        --prototype embeds a self-contained HTML page as the first-click prototype.
check   Reads a built tool without running it: document basics, the security policy, no network calls,
        a registered method, content that parses, codes rather than names, and colour contrast.

Exit status is 1 when any check fails.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / 'assets'
REPORTER = HERE.parents[1] / 'research-reporter' / 'scripts'
DELIVERIES = ('moderator-device', 'participant-file', 'shared-link', 'hosted')
RUNS = {'in-person': 'moderated in person', 'remote': 'moderated remotely', 'self-run': 'run by participants alone', 'mixed': 'a mix, chosen per session'}
DEVICES = {'moderator': "the moderator's device", 'participant': "the participant's own device", 'both': 'both: the moderator logs while the participant uses their own'}
CSP = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'{style}; font-src data:{font}; "
       "img-src data: blob:; frame-src blob: data:; form-action 'none'; base-uri 'none'")
NETWORK = re.compile(r'\b(fetch\s*\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon|importScripts)')


def brand_layers(brand: dict):
    """Theme the tool with research-reporter's brand profile, when that skill is installed alongside."""
    if not (REPORTER / 'report.py').exists():
        raise SystemExit('Branding needs the research-reporter skill installed next to this one.')
    sys.path.insert(0, str(REPORTER))
    import report  # noqa: E402
    shell = (ASSETS / 'shell.html').read_text(encoding='utf-8')
    light = report.tokens(re.search(r'^:root \{(.*?)^\}', shell, re.S | re.M).group(1))
    dark = report.tokens(re.search(r'^:root\[data-theme="dark"\] \{(.*?)^\}', shell, re.S | re.M).group(1))
    css, url, eff_light, eff_dark = report.brand_layers(brand, light, dark)
    problems, _ = report.contrast_report(eff_light, eff_dark)
    if problems:
        raise SystemExit('The brand fails contrast:\n  ' + '\n  '.join(problems))
    return css, url


def plan(run: str, device: str, delivery: str | None) -> tuple[str, list[str], list[str]]:
    """From the setup answers: the delivery, the copies to build, and what to tell the user."""
    if run not in RUNS:
        raise SystemExit('--run must be one of: ' + ', '.join(RUNS) + '. Ask the user who runs the sessions.')
    if device not in DEVICES:
        raise SystemExit('--device must be one of: ' + ', '.join(DEVICES) + ". Ask the user whose device runs the tool.")
    if device == 'moderator':
        delivery = delivery or 'moderator-device'
        if delivery == 'participant-file':
            raise SystemExit("participant-file sends the tool to participants, but --device moderator keeps it on the moderator's. Use --device participant.")
    elif delivery not in ('participant-file', 'shared-link', 'hosted'):
        raise SystemExit('--delivery must be participant-file, shared-link or hosted when the tool runs on the participant\'s device. Ask the user how they will get it.')
    copies = ['moderator'] if device == 'moderator' or delivery == 'shared-link' else ['moderator', 'participant']
    notes = []
    if run == 'self-run' and device == 'moderator':
        notes.append("Participants work alone on the moderator's device: the moderator starts each session and hands it over.")
    if run == 'remote' and device == 'moderator':
        notes.append("The participant controls the moderator's screen remotely; check the call software allows it.")
    if run in ('in-person', 'remote') and device != 'moderator' and delivery != 'shared-link':
        notes.append("The moderator watches while the participant uses their own copy, then imports the participant's file to review it.")
    if delivery == 'shared-link':
        notes.append('Participants need claude.ai access in your organisation, at Contributor level, to save their answers. '
                     'For people outside it, build with --delivery participant-file or hosted instead.')
        notes.append('Publish with the capabilities: ' + json.dumps(SHARED_CAPABILITIES))
    if delivery == 'hosted':
        notes.append('Results come back as files participants save and send, unless your team supplies a server to receive them (not built).')
    return delivery, copies, notes


# Shared links: each person reads and writes only their own sessions; the link's owner and editors read and review them all.
SHARED_CAPABILITIES = {'db': {'rules': [{'path': 'config', 'read': 'view', 'write': 'admin'},
                                        {'path': 'sessions', 'read': 'admin', 'write': 'admin'},
                                        {'path': 'sessions/{self}', 'read': 'interact', 'write': 'interact'}]},
                       'user': {}, 'downloads': True}


def handover(copy: str, run: str, device: str, delivery: str) -> str:
    if delivery == 'shared-link':
        return 'one page: its owner and editors see the moderator screens, everyone else only the participant screens; sessions saved to the link\'s shared storage'
    if copy == 'participant':
        how = {'participant-file': 'send it to each participant', 'hosted': 'put it on your site and send each participant the link'}[delivery]
        return f'{how}, adding #P3 (their code) to fill it in. Their answers stay on their device until they save a file and send it back'
    if device == 'moderator':
        return 'open it on the moderator\'s device; sessions are kept there until exported'
    return 'for the moderator: import the files participants send back, review sessions, export for the report' + ('; also run moderator-logged tasks on it' if device == 'both' else '')


def build(study: dict, method: str, delivery: str, build_for: str, brand: dict | None, setup: dict | None = None) -> str:
    shell = (ASSETS / 'shell.html').read_text(encoding='utf-8')
    js = ASSETS / 'methods' / f'{method}.js'
    if not js.exists():
        raise SystemExit(f'No method module "{method}". Available: ' + ', '.join(p.stem for p in (ASSETS / 'methods').glob('*.js')))
    css_file = js.with_suffix('.css')
    config = {'method': method, 'delivery': delivery, 'build': build_for, 'setup': setup or {}}
    brand_css, font_url = '', None
    if brand:
        brand_css, font_url = brand_layers(brand)
        config['brand'] = {'name': brand.get('name'), 'logo': brand.get('logo')}

    def safe_json(o):
        return json.dumps(o, ensure_ascii=False, indent=1).replace('<', '\\u003c')

    title = f"{study.get('title', 'Study')} · {method.replace('-', ' ').capitalize()}"
    out = (shell.replace('{{TITLE}}', title.replace('&', '&amp;').replace('<', '&lt;'))
           .replace('{{CONFIG}}', safe_json(config))
           .replace('{{CONTENT}}', safe_json(study))
           .replace('{{BRAND_CSS}}', brand_css)
           .replace('{{METHOD_CSS}}', css_file.read_text(encoding='utf-8') if css_file.exists() else '')
           .replace('{{METHOD_JS}}', js.read_text(encoding='utf-8')))
    fonts = f'<link id="brand-fonts" rel="stylesheet" href="{font_url.replace("&", "&amp;")}">' if font_url else ''
    out = out.replace('<!--FONTS-->', fonts)
    if delivery == 'shared-link':
        # The host wraps the page and enforces its own policy; keep only what goes in the body.
        head = re.search(r'<head>(.*?)</head>', out, re.S).group(1)
        head = re.sub(r'<meta charset="utf-8">\s*|<meta name="viewport"[^>]*>\s*|<!--CSP-->\s*', '', head)
        body = re.search(r'<body>(.*)</body>', out, re.S).group(1)
        return '<meta charset="utf-8">\n<meta name="claude:viewport-fit-sides" content="cover">\n' + head.strip() + '\n' + body.strip() + '\n'
    policy = CSP.format(style=' https://fonts.googleapis.com' if font_url else '', font=' https://fonts.gstatic.com' if font_url else '')
    return out.replace('<!--CSP-->', f'<meta http-equiv="Content-Security-Policy" content="{policy}">')


def check(html: str) -> int:
    fails, warns = [], []
    shared = not html.lstrip().lower().startswith('<!doctype')
    if not shared:
        for what, pat in (('<!doctype html>', r'^\s*<!doctype html>'), ('lang', r'<html[^>]*\blang="[a-z-]+"'), ('UTF-8 charset', r'<meta charset="utf-8">'),
                          ('viewport', r'<meta name="viewport"'), ('security policy', r'http-equiv="Content-Security-Policy"')):
            if not re.search(pat, html, re.I):
                fails.append(f'missing {what}')
        policy = (re.search(r'http-equiv="Content-Security-Policy" content="([^"]*)"', html) or [None, ''])[1]
        if "default-src 'none'" not in policy:
            fails.append("the security policy does not start from default-src 'none'")
    scripts = re.findall(r'<script(?![^>]*type="application/json")[^>]*>(.*?)</script>', html, re.S)
    code = '\n'.join(scripts)
    if re.search(r'<script[^>]+\bsrc=', html):
        fails.append('loads an external script')
    m = NETWORK.search(code)
    if m:
        fails.append(f'makes network calls of its own ({m.group(1).strip()})')
    if 'Shell.register(' not in code:
        fails.append('no method module is registered')
    try:
        content = json.loads(re.search(r'id="study-content">(.*?)</script>', html, re.S).group(1).replace('\\u003c', '<'))
        config = json.loads(re.search(r'id="tool-config">(.*?)</script>', html, re.S).group(1).replace('\\u003c', '<'))
    except (AttributeError, json.JSONDecodeError) as e:
        print(f'  FAIL  content or config does not parse: {e}')
        return 1
    for k in ('studyId', 'title', 'tasks', 'consent'):
        if not content.get(k):
            fails.append(f'study content has no "{k}"')
    if config.get('delivery') not in DELIVERIES:
        fails.append(f'unknown delivery "{config.get("delivery")}"')
    setup = config.get('setup') or {}
    if setup.get('facilitation') not in RUNS or setup.get('device') not in DEVICES:
        fails.append('no test setup (who runs it, whose device): rebuild with --run and --device')
    for code_ in (content.get('fixedOrders') or {}):
        if not re.fullmatch(r'[A-Za-z]{1,3}\d{1,4}', code_):
            fails.append(f'fixed order keyed by "{code_}", which is not a participant code')
    tasks = content.get('tasks') or []
    if len({t.get('id') for t in tasks}) != len(tasks):
        fails.append('task ids are not unique')
    hyp = {h.get('id') for h in content.get('hypotheses') or []}
    for t in tasks:
        if t.get('hypothesis') and t['hypothesis'] not in hyp:
            fails.append(f'task {t.get("id")} refers to hypothesis {t["hypothesis"]}, which is not listed')
    if not content.get('hypotheses'):
        warns.append('  warn  no hypotheses with wording: the report will have to group tasks some other way')
    if re.search(r'Â[ -¿]|â€', html):
        fails.append('garbled characters: a file was read with the wrong encoding')
    for w in warns:
        print(w)
    for f in fails:
        print(f'  FAIL  {f}')
    if not fails:
        print(f'  ok    {config["method"]} tool, {len(tasks)} tasks, delivery {config["delivery"]}'
              f'{", participant copy" if config.get("build") == "participant" else ""}: no network calls, content parses')
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[1] not in ('build', 'check'):
        print(__doc__)
        return 1
    args = argv[2:]
    opt = lambda n: args[args.index(n) + 1] if n in args else None
    if argv[1] == 'check':
        return check(Path(args[0]).read_text(encoding='utf-8'))
    run, device = opt('--run'), opt('--device')
    if not run or not device:
        raise SystemExit('Give the test setup: --run (' + ' | '.join(RUNS) + ') and --device (' + ' | '.join(DEVICES) + '). Ask the user.')
    delivery, copies, notes = plan(run, device, opt('--delivery'))
    only = opt('--only') or opt('--build')
    if only:
        if only not in copies:
            raise SystemExit(f'This setup has no {only} copy; it builds: ' + ', '.join(copies))
        copies = [only]
    src = Path(args[0])
    study = json.loads(src.read_text(encoding='utf-8'))
    if opt('--prototype'):  # first-click: embed the prototype page in the study content
        study['prototype'] = Path(opt('--prototype')).read_text(encoding='utf-8')
    brand = json.loads(Path(opt('--brand')).read_text(encoding='utf-8')) if opt('--brand') else None
    method = opt('--method') or 'card-sort'
    setup = {'facilitation': run, 'device': device}
    base = Path(opt('-o') or src.with_name(f"{study['studyId']}_{method}.html"))
    print(f'Setup: {RUNS[run]}, on {DEVICES[device]}' + ('' if delivery == 'moderator-device' else f', delivered as {delivery}'))
    status = 0
    for copy in copies:
        out = base if copy == 'moderator' else base.with_name(base.stem + '_participant' + base.suffix)
        html = build(study, method, delivery, copy, brand, setup)
        out.write_text(html, encoding='utf-8')
        print(f"{'Shared page' if delivery == 'shared-link' else copy.capitalize() + ' copy'}: {out}\n  {handover(copy, run, device, delivery)}")
        status |= check(html)
    for n in notes:
        print('  note  ' + n)
    return status


def _selfcheck():
    assert plan('remote', 'participant', 'participant-file')[1] == ['moderator', 'participant']
    assert plan('self-run', 'participant', 'shared-link')[1] == ['moderator']
    assert plan('in-person', 'moderator', None)[:2] == ('moderator-device', ['moderator'])
    assert NETWORK.search('x = fetch (url)') and not NETWORK.search('prefetchable')
    assert re.fullmatch(r'[A-Za-z]{1,3}\d{1,4}', 'P12') and not re.fullmatch(r'[A-Za-z]{1,3}\d{1,4}', 'Jane Smith')


if __name__ == '__main__':
    _selfcheck()
    sys.exit(main(sys.argv))
