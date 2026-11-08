"""Convert a research-sessions export (from tools built with research-tool-builder) into report data.

    python3 converters/research_sessions.py EXPORT.json [MORE.json ...] > study.json
    python3 report.py build study.json -o report.html [--brand brand.json]

Works for every method. Card sort, classification, tree test and first click get their own findings;
any other method (stimulus, or one added later) gets generic findings from outcome.success,
outcome.friction, the task's own questions and any variants, so a new method needs no change here
to produce a report. Several files from the same study are merged by session id. Practice
sessions, unresolved imported copies and sessions still in progress are left out. The format is in research-tool-builder's references/data-format.md.
"""
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

EASE5 = ['Very difficult', 'Difficult', 'Neither easy nor difficult', 'Easy', 'Very easy']
METHOD_LABEL = {'card-sort': 'Card sort', 'classification': 'Classification', 'tree-test': 'Tree test', 'first-click': 'First click'}
MODE_LABEL = {'in-person': 'moderated in person', 'remote': 'moderated remotely', 'self-run': 'self-run', 'moderated': 'moderated in person'}
DEVICE_LABEL = {'moderator': "the moderator's device", 'participant': "participants' own devices", 'both': "participants' own devices, with the moderator logging on theirs"}
DELIVERY_LABEL = {'participant-file': 'a file sent to each participant', 'shared-link': 'a shared claude.ai link', 'hosted': 'a hosted page'}
OBS_LEVELS = [{'id': 'completed', 'label': 'Completed'}, {'id': 'with-help', 'label': 'Completed with help'},
              {'id': 'failed', 'label': 'Did not complete'}, {'id': 'not-attempted', 'label': 'Not attempted'}, {'id': 'gave-up', 'label': 'Gave up'}]


def moderated(mode):
    return mode in ('in-person', 'remote', 'moderated')


def shared_findings(task, runs, content):
    """For every method: how tasks ended where a moderator recorded it, observation codes, moderator notes, time away."""
    f = []
    names = {l['id']: l['label'] for l in (content.get('levels') or []) + OBS_LEVELS}
    levels = Counter((r.get('outcome') or {}).get('level') for _, r in runs if (r.get('outcome') or {}).get('level'))
    if levels:
        f.append(('investigate', 'How the task ended, as the moderator recorded it: ' + ', '.join(f'{names.get(k, k)} ({n})' for k, n in levels.most_common()) + '.',
                  [p for p, r in runs if (r.get('outcome') or {}).get('level')]))
    labels = {c['id']: c['label'] for c in content.get('codes') or []}
    seen = defaultdict(set)
    for p, r in runs:
        for c in list((r.get('outcome') or {}).get('codes') or []) + [k for k, v in ((r.get('moderator') or {}).get('codes') or {}).items() if v]:
            seen[c].add(p)
    if seen:
        f.append(('investigate', 'Observed: ' + '; '.join(f'{labels.get(c, c)} ({share(len(ps), len(runs))})' for c, ps in sorted(seen.items(), key=lambda x: -len(x[1]))) + '.',
                  sorted({p for ps in seen.values() for p in ps}, key=pcode)))
    for p, r in runs:
        note = ((r.get('moderator') or {}).get('notes') or '').strip()
        if note:
            f.append(('investigate', f'Moderator noted: {note}', [p]))
    return f


def load(paths):
    files = [json.loads(Path(p).read_text(encoding='utf-8')) for p in paths]
    for f in files:
        if f.get('format') != 'research-sessions':
            raise SystemExit('Not a research-sessions file. For other tools, use their own converter.')
        if f.get('formatVersion', 1) > 1:
            raise SystemExit('This file was made by a newer tool than this converter understands.')
    studies = {f['study']['id'] for f in files}
    if len(studies) > 1:
        raise SystemExit('These files are from different studies: ' + ', '.join(sorted(studies)))
    contents, sessions = {}, {}
    for f in files:
        contents.update(f.get('contents') or {})
        for s in f.get('sessions') or []:
            have = sessions.get(s['id'])
            if not have or (s.get('updatedAt') or '') > (have.get('updatedAt') or ''):
                sessions[s['id']] = s
    return files[0], contents, list(sessions.values())


def latest_runs(s):
    """The last real attempt at each task: interrupted attempts are replaced by their retake."""
    out = {}
    for r in s['runs']:
        if r['status'] == 'interrupted':
            continue
        if r['taskId'] not in out or r['attempt'] > out[r['taskId']]['attempt']:
            out[r['taskId']] = r
    return out


def success(r):
    o = (r.get('moderator') or {}).get('override')
    return o['success'] if o else (r.get('outcome') or {}).get('success')


def friction(method, r, task=None):
    """How much friction a run shows, where the method can tell. None when it cannot."""
    if r['status'] == 'gave-up':
        return 'major'
    o = r.get('outcome') or {}
    if o.get('friction') in ('none', 'minor', 'major'):  # any module may rate it itself
        return o['friction']
    if method == 'tree-test':
        return 'none' if o.get('direct') else 'minor' if o.get('success') else 'major'
    if method == 'first-click':
        return {'main': 'none', 'acceptable': 'minor', 'wrong': 'major'}.get(o.get('tier'))
    if method not in METHOD_FINDINGS:
        ok = task_success(task or {}, r)
        return None if ok is None else 'none' if ok else 'major'
    return None


def keyed(task):
    """The task's questions that carry a correct answer (comprehension, recall)."""
    return [q for q in task.get('questions') or [] if q.get('correct') is not None]


def task_success(task, r):
    """Success from the method, a moderator override, or else the answer key of the task's questions."""
    ok = success(r)
    if ok is not None or not keyed(task) or r['status'] == 'gave-up':
        return False if r['status'] == 'gave-up' and keyed(task) else ok
    a = r.get('answers') or {}
    return all(right(q, a.get(q['id'])) for q in keyed(task))


def right(q, v):
    v = v or {}
    want = q['correct'] if isinstance(q['correct'], list) else [q['correct']]
    got = v.get('choices') or ([v['choice']] if v.get('choice') else [])
    return sorted(got) == sorted(want)


def generic_findings(task, runs):
    """For methods without their own findings: who succeeded, who did not, and what was left to judge."""
    f, ok, bad, gave, open_ = [], [], [], [], []
    for p, r in runs:
        (gave if r['status'] == 'gave-up' else open_ if task_success(task, r) is None else ok if task_success(task, r) else bad).append(p)
    if ok:
        f.append(('positive', 'Succeeded' + (' (answered every check question correctly)' if keyed(task) else '') + '.', ok))
    if bad:
        f.append(('major', 'Did not succeed' + (': ' + '; '.join(f'"{q["prompt"]}" answered wrongly by {sum(1 for p, r in runs if p in bad and not right(q, (r.get("answers") or {}).get(q["id"])))}' for q in keyed(task)) if keyed(task) else '') + '.', bad))
    if gave:
        f.append(('major', 'Gave up.', gave))
    if open_ and (ok or bad):
        f.append(('investigate', 'Not judged by the tool: review these runs.', open_))
    for q in task.get('questions') or []:  # what most people chose, where there is no right answer
        if q['kind'] not in ('choice', 'choices') or q.get('correct') is not None:
            continue
        picks = [(p, c) for p, r in runs for v in [(r.get('answers') or {}).get(q['id']) or {}] for c in (v.get('choices') or [v.get('choice')]) if c]
        if picks:
            top = Counter(c for _, c in picks).most_common(3)
            people = len({p for p, _ in picks})
            f.append(('investigate', f'"{q["prompt"]}" Most chosen: ' + ', '.join(f'{c} ({share(n, people)})' for c, n in top) + '.', sorted({p for p, _ in picks}, key=pcode)))
    return f


def variant_findings(task, runs):
    """When runs of one task showed different variants: success and ease for each."""
    by = defaultdict(list)
    for p, r in runs:
        if r.get('variant'):
            by[r['variant']].append((p, r))
    if len(by) < 2:
        return []
    parts = []
    for v, rs in sorted(by.items()):
        judged = [x for x in (task_success(task, r) for _, r in rs) if x is not None]
        eases = [r['ease'] for _, r in rs if r.get('ease')]
        parts.append(f'{v}: {len(rs)} run{"s" if len(rs) != 1 else ""}' + (f', {sum(judged)} of {len(judged)} succeeded' if judged else '') + (f', ease {statistics.mean(eases):.1f}' if eases else ''))
    return [('investigate', 'By variant: ' + '; '.join(parts) + '. Small groups: treat differences as signals.', [p for p, _ in runs])]


def summarise(questions, answer_sets, prefix=''):
    """Tally answers to questions (closing or a task's own) into report survey items."""
    out = []
    for q in questions:
        vals = [a[q['id']] for a in answer_sets if a.get(q['id'])]
        if not vals:
            continue
        prompt = prefix + q['prompt']
        if q['kind'] == 'rank':
            items = q.get('items') or q.get('options')
            orders = [v['order'] for v in vals if v.get('order')]
            out.append({'kind': 'rank', 'prompt': prompt, 'n': len(orders),
                        'items': [{'label': it, 'avg': statistics.mean(o.index(it) + 1 for o in orders if it in o), 'first': sum(1 for o in orders if o and o[0] == it)} for it in items]})
        elif q['kind'] in ('choice', 'choices', 'scale'):
            opts = (q.get('options') or q.get('labels') or []) + (['Other'] if q.get('other') else [])
            tally = {o: {'label': o + (' (correct)' if q.get('correct') is not None and o in (q['correct'] if isinstance(q['correct'], list) else [q['correct']]) else ''), 'count': 0, 'comments': []} for o in opts}
            for v in vals:
                picked = v.get('choices') or ([v['choice']] if v.get('choice') else []) or ([opts[v['value'] - 1]] if v.get('value') else [])
                for o in picked:
                    tally.setdefault(o, {'label': o, 'count': 0, 'comments': []})['count'] += 1
                if v.get('comment') and picked:
                    tally[picked[0]]['comments'].append(v['comment'])
            out.append({'kind': 'choice', 'prompt': prompt, 'n': len(vals), 'options': list(tally.values())})
        elif q['kind'] == 'text':
            texts = [v['text'].strip() for v in vals if (v.get('text') or '').strip()]
            if texts:
                out.append({'kind': 'text', 'prompt': prompt, 'n': len(texts), 'answers': texts})
    return out


def share(n, d):
    return f'{n} of {d}'


def open_sort_findings(task, runs, labels):
    """Open sorts: names differ between people, so look at which cards end up together."""
    pairs, seen = Counter(), Counter()
    names = Counter()
    for p, r in runs:
        groups = [g for g in (r.get('outcome') or {}).get('groups', []) if g['cards']]
        placed = [c for g in groups for c in g['cards']]
        for c in placed:
            seen[c] += 1
        for g in groups:
            names[(g['name'] or '').strip().capitalize() or '(unnamed)'] += 1
            cs = sorted(g['cards'])
            for i in range(len(cs)):
                for j in range(i + 1, len(cs)):
                    pairs[(cs[i], cs[j])] += 1
    n = len(runs)
    together = [(a, b, k) for (a, b), k in pairs.most_common() if k / n >= 0.75]
    best = {c: max([k for (a, b), k in pairs.items() if c in (a, b)] or [0]) for c in seen}
    loners = sorted(labels.get(c, c) for c, k in best.items() if k / n < 0.5)
    everyone = sorted({p for p, _ in runs}, key=pcode)
    f = []
    if together:
        f.append(('positive', 'Grouped together by most people (75% or more): ' + '; '.join(f'{labels.get(a, a)} + {labels.get(b, b)} ({share(k, n)})' for a, b, k in together[:8]) + '.', everyone))
    if loners:
        f.append(('investigate', 'No consistent home (never with the same card for half the people or more): ' + ', '.join(loners) + '.', everyone))
    f.append(('investigate', 'Group names people used: ' + ', '.join(f'{nm} ({k})' for nm, k in names.most_common(8)) + '.', everyone))
    return f


def card_sort_findings(task, runs):
    """Closed and hybrid sorts: agreement per card on the study's categories. Open sorts: see open_sort_findings."""
    labels = {c['id']: c['label'] for c in task.get('cards', [])}
    if task.get('mode') == 'open':
        f = open_sort_findings(task, runs, labels)
        other = [(p, x['card']) for p, r in runs for x in (r.get('outcome') or {}).get('other', [])]
        if other:
            f.append(('minor', "Placed in \"Doesn't fit\": " + ', '.join(f'{c} ({k})' for c, k in Counter(labels.get(c, c) for _, c in other).most_common()) + '.', sorted({p for p, _ in other}, key=pcode)))
        return f
    places = defaultdict(list)
    other = []
    for p, r in runs:
        o = r.get('outcome') or {}
        for g in o.get('groups', []):
            key = (g['name'] or '').strip().lower() or '(unnamed)'
            for c in g['cards']:
                places[c].append((p, key, g['name']))
        for x in o.get('other', []):
            places[x['card']].append((p, "doesn't fit", "Doesn't fit"))
            other.append((p, x['card']))
    strong, split = [], []
    for c, ps in places.items():
        top, n = Counter(k for _, k, _ in ps).most_common(1)[0]
        shown = next(name for _, k, name in ps if k == top)
        (strong if n / len(ps) >= 0.7 else split if n / len(ps) < 0.5 else []).append((labels.get(c, c), shown, n, len(ps), [p for p, _, _ in ps]))
    f = []
    if strong:
        f.append(('positive', 'Strong agreement (70% or more put it in the same group): ' + '; '.join(f'{c} → {g} ({share(n, d)})' for c, g, n, d, _ in sorted(strong)) + '.',
                  sorted({p for *_, ps in strong for p in ps}, key=pcode)))
    if split:
        f.append(('investigate', 'Split opinion (under half agree): ' + '; '.join(f'{c} (most often {g}, {share(n, d)})' for c, g, n, d, _ in sorted(split)) + '.',
                  sorted({p for *_, ps in split for p in ps}, key=pcode)))
    if other:
        cards = Counter(labels.get(c, c) for _, c in other)
        f.append(('minor', "Placed in \"Doesn't fit\": " + ', '.join(f'{c} ({n})' for c, n in cards.most_common()) + '.', sorted({p for p, _ in other}, key=pcode)))
    left = [p for p, r in runs if (r.get('outcome') or {}).get('unsorted')]
    if left:
        f.append(('minor', 'Left cards unsorted.', left))
    return f


def classification_findings(task, runs):
    """Agreement between raters per item, and how often they were unsure."""
    texts = {i['id']: i['text'] for i in task.get('items', [])}
    names = {c['code']: c['label'] for c in task.get('categories', [])}
    names['NONE'] = 'None of these'
    by_item = defaultdict(list)
    unsure = Counter()
    for p, r in runs:
        for item, a in ((r.get('outcome') or {}).get('answers') or {}).items():
            by_item[item].append((p, a.get('choice')))
            if a.get('unsure') or a.get('unfamiliar'):
                unsure[p] += 1
    if len(runs) < 2:
        return [('investigate', 'Agreement needs at least two raters; only one so far.', [p for p, _ in runs])]
    full, split = [], []
    for item, xs in by_item.items():
        top, n = Counter(c for _, c in xs).most_common(1)[0]
        (full if n == len(xs) else split if n / len(xs) < 0.7 else []).append((texts.get(item, item), names.get(top, top), n, len(xs)))
    total = sum(len(x) for x in by_item.values())
    agreed = sum(Counter(c for _, c in xs).most_common(1)[0][1] for xs in by_item.values())
    raters = [p for p, _ in runs]
    f = [('positive' if agreed / total >= 0.8 else 'minor', f'Overall, {round(agreed / total * 100)}% of answers matched the most common answer for their item.', raters)]
    if full:
        f.append(('positive', f'Every rater agreed on {len(full)} of {len(by_item)} items, for example: ' + '; '.join(f'"{t}" → {c}' for t, c, *_ in sorted(full)[:4]) + '.', raters))
    if split:
        f.append(('investigate', 'Raters disagreed (under 70% the same): ' + '; '.join(f'"{t}" (most often {c}, {share(n, d)})' for t, c, n, d in sorted(split)) + '.', raters))
    if unsure:
        f.append(('minor', 'Marked items unsure or unfamiliar: ' + ', '.join(f'{p} ({n})' for p, n in sorted(unsure.items(), key=lambda x: pcode(x[0]))) + '.', sorted(unsure, key=pcode)))
    return f


def tree_findings(task, runs):
    direct = [p for p, r in runs if (r.get('outcome') or {}).get('direct')]
    indirect = [p for p, r in runs if (r.get('outcome') or {}).get('success') and not (r.get('outcome') or {}).get('direct')]
    wrong = [(p, r) for p, r in runs if (r.get('outcome') or {}).get('success') is False and r['status'] != 'gave-up']
    gave = [p for p, r in runs if r['status'] == 'gave-up']
    f = []
    if direct:
        f.append(('positive', 'Went straight to the right answer, without backtracking.', direct))
    if indirect:
        f.append(('minor', 'Found the right answer after backtracking.', indirect))
    if wrong:
        ends = Counter(' › '.join((r.get('outcome') or {}).get('path') or ['no answer']) for _, r in wrong).most_common(3)
        f.append(('major', 'Chose a wrong answer. Most common: ' + ', '.join(f'{e} ({n})' for e, n in ends) + '.', [p for p, _ in wrong]))
    if gave:
        f.append(('major', 'Gave up before choosing an answer.', gave))
    return f


def clicked(r):
    """What the participant clicked first, in the prototype's own words where the click recorded them."""
    e = next((e for e in r.get('events', []) if e.get('type') == 'click' and e.get('first')), {})
    target = (r.get('outcome') or {}).get('firstTarget')
    return f'"{e["label"]}"' if e.get('label') else (target or 'unlabelled')


def first_click_findings(task, runs):
    tiers = defaultdict(list)
    for p, r in runs:
        tiers[(r.get('outcome') or {}).get('tier') if r['status'] != 'gave-up' else 'gave-up'].append((p, r))
    f = []
    if tiers.get('main'):
        f.append(('positive', 'Clicked the main target first.', [p for p, _ in tiers['main']]))
    if tiers.get('acceptable'):
        f.append(('minor', 'Clicked an acceptable alternative first: ' + ', '.join(f'{t} ({n})' for t, n in Counter(clicked(r) for _, r in tiers['acceptable']).most_common()) + '.', [p for p, _ in tiers['acceptable']]))
    if tiers.get('wrong'):
        f.append(('major', 'Clicked somewhere else first. Most common: ' + ', '.join(f'{t} ({n})' for t, n in Counter(clicked(r) for _, r in tiers['wrong']).most_common(3)) + '.', [p for p, _ in tiers['wrong']]))
    if tiers.get('gave-up'):
        f.append(('major', 'Gave up without clicking.', [p for p, _ in tiers['gave-up']]))
    if tiers.get('unclassified') or tiers.get(None):
        f.append(('investigate', 'First click not classified: the task has no targets. Review the clicks.', [p for p, _ in tiers.get('unclassified', []) + tiers.get(None, [])]))
    return f


METHOD_FINDINGS = {'card-sort': card_sort_findings, 'classification': classification_findings, 'tree-test': tree_findings, 'first-click': first_click_findings}
SCORED = {'tree-test', 'first-click'}
NOT_SCORED_NOTE = {
    'card-sort': 'A card sort has no right answer for each person, so it does not pass or fail. Agreement across participants is in the findings.',
    'classification': 'Classification measures agreement between raters, not individual right answers. Agreement is in the findings.',
}
GENERIC_NOT_SCORED = 'This task has no right answer for each person, so it does not pass or fail. Answers are summarised in the survey section.'


def label_of(head, method):
    return METHOD_LABEL.get(method) or head['tool'].get('label') or method.replace('-', ' ').capitalize()


def who(s):
    """The participant as the report shows them: the code, plus the entry number in repeated studies."""
    return s['participant'] + (f"-e{s['wave']}" if s.get('wave') else '')


def pcode(p):
    m = re.match(r'([A-Za-z]+)(\d+)', p)
    return (m.group(1), int(m.group(2))) if m else (p, 0)


def build(head, contents, sessions):
    method = head['tool']['method']
    label = label_of(head, method)
    keep = [s for s in sessions if not s.get('practice') and not s.get('conflictWith') and s.get('status') in ('completed', 'ended-early')]
    if not keep:
        raise SystemExit('No finished, non-practice sessions to report.')
    by_hash = Counter(s['contentHash'] for s in keep)
    main_hash = by_hash.most_common(1)[0][0]
    content = contents[main_hash]
    other_versions = [h for h in by_hash if h != main_hash]
    keep.sort(key=lambda s: (pcode(s['participant']), s.get('wave') or 0))
    seg_label = {x['id']: x['label'] for x in content.get('segments', [])}
    conds = content.get('conditions') or []

    participants = []
    for s in keep:
        dev = Counter(r.get('device') for r in latest_runs(s).values() if r.get('device'))
        participants.append({'id': who(s), **{'c-' + c['id']: ((s.get('plan') or {}).get('conditions') or {}).get(c['id']) or '–' for c in conds}, 'segment': seg_label.get(s.get('segment'), s.get('segment') or ''),
                             'mode': MODE_LABEL.get(s.get('mode'), s.get('mode') or '') + (' (stopped early)' if s.get('stoppedBy') == 'participant' else ''),
                             'devices': ' · '.join(f'{k.capitalize()} {v}' for k, v in dev.most_common()) or '–',
                             'status': 'Completed' if s['status'] == 'completed' else 'Ended early'})

    tasks_by_id = {t['id']: t for t in content['tasks']}
    task_out = {}
    scored_rows = []
    for t in content['tasks']:
        runs = [(who(s), latest_runs(s)[t['id']]) for s in keep if t['id'] in latest_runs(s)]
        generic = method not in METHOD_FINDINGS
        scored = method in SCORED or (generic and (bool(keyed(t)) or any(task_success(t, r) is not None for _, r in runs)))
        results = {}
        for p, r in runs:
            res = {'seq': r.get('ease'), 'ms': r.get('durationMs')}
            if scored:
                res['done'] = task_success(t, r)
            sev = friction(method, r, t)
            if sev:
                res['sev'] = sev
            results[p] = res
        findings = (METHOD_FINDINGS.get(method, generic_findings)(t, runs) + variant_findings(t, runs) + shared_findings(t, runs, content)) if runs else []
        hard = [p for p, r in runs if (r.get('ease') or 5) <= 2]
        if hard:
            findings.append(('minor', 'Rated the task difficult (2 or lower out of 5).', hard))
        notes = sorted([(p, r['notes'].strip()) for p, r in runs if (r.get('notes') or '').strip()], key=lambda x: -len(x[1]))[:4]
        conf = [r['confidence'] for _, r in runs if r.get('confidence')]
        takeaway = [f"Confidence afterwards: average {statistics.mean(conf):.1f} out of 5 from {len(conf)} answers ({t['confidence']})"] if conf and t.get('confidence') else []
        away = [r['awayMs'] for _, r in runs if r.get('awayMs')]
        if away:
            takeaway.append(f"Time away from the tool during the task (in the product, or elsewhere): median {round(statistics.median(away) / 1000)} s, for {len(away)} of {len(runs)} participants")
        out = {'id': t['id'], 'title': t['title'],
               'stimulus': label + (f" · {t['device']}" if t.get('device') else ''),
               'tags': [label] + ([t['hypothesis']] if t.get('hypothesis') else []) + ([f"Mode: {t['mode']}"] if t.get('mode') else []),
               'scored': scored,
               **({'easeAsked': False} if t.get('ease') is False else {}),
               'script': [x for x in [t.get('scenario') or t.get('prompt')] if x],
               'lookFor': [],
               'results': results,
               'findings': [{'id': f"{t['id']}-F{i + 1}", 'type': k, 'text': txt, 'who': who} for i, (k, txt, who) in enumerate(findings)],
               'quotes': [{'who': p, 'text': n} for p, n in notes],
               'takeaway': takeaway}
        if not scored:
            out['scoreNote'] = NOT_SCORED_NOTE.get(method, GENERIC_NOT_SCORED)
        elif keyed(t):
            out['scoreNote'] = 'Success means every check question was answered correctly: ' + '; '.join(f'"{q["prompt"]}" → {q["correct"]}' for q in keyed(t)) + '.'
        if method == 'tree-test':
            out['effNote'] = 'From the path: straight to the answer = no issue, after backtracking = minor, wrong answer or gave up = major.'
        if method == 'first-click':
            out['effNote'] = 'From the first click: main target = no issue, acceptable alternative = minor, anywhere else or gave up = major.'
        if scored:
            judged = [v['done'] for v in results.values() if v.get('done') is not None]
            if judged:
                scored_rows.append((sum(judged) / len(judged), out, sum(judged), len(judged)))
        task_out[t['id']] = out

    groups = []
    for h in content.get('hypotheses', []):
        ts = [task_out[t['id']] for t in content['tasks'] if t.get('hypothesis') == h['id'] and t['id'] in task_out]
        if ts:
            groups.append({'id': h['id'], 'statement': h['statement'], 'tasks': ts})
    loose = [task_out[t['id']] for t in content['tasks'] if not t.get('hypothesis') and t['id'] in task_out]
    if loose:
        groups.append({'id': 'Other', 'statement': 'Tasks not tied to a hypothesis', 'tasks': loose})

    survey = summarise(content.get('closing', []), [s.get('closing') or {} for s in keep])
    for t in content['tasks']:
        if t.get('questions'):
            sets = [latest_runs(s)[t['id']].get('answers') or {} for s in keep if t['id'] in latest_runs(s)]
            survey += summarise(t['questions'], sets, f"Task {t['id']} · ")

    insights = []
    for rate, task, d, n in sorted(scored_rows, key=lambda x: x[0])[:3]:
        lead = next((f for f in task['findings'] if f['type'] == 'major'), None) or (task['findings'][0] if task['findings'] else None)
        insights.append({'title': f"{task['title']}: {d} of {n} succeeded", 'body': (lead['text'] if lead else '') + f" (Task {task['id']})"})
    if not scored_rows:
        for task in task_out.values():
            lead = next((f for f in task['findings'] if f['type'] in ('investigate', 'positive')), None)
            if lead:
                insights.append({'title': task['title'], 'body': lead['text'] + f" (Task {task['id']})"})
            if len(insights) == 3:
                break

    finished = sorted(s['finishedAt'] for s in keep if s.get('finishedAt'))
    first, last = datetime.fromisoformat(finished[0].replace('Z', '+00:00')), datetime.fromisoformat(finished[-1].replace('Z', '+00:00'))
    span = last.strftime('%-d %B %Y') if first.date() == last.date() else f"{first.strftime('%-d %B')} – {last.strftime('%-d %B %Y')}"
    segs = Counter(p['segment'] for p in participants if p['segment'])
    people = len({s['participant'] for s in keep})
    modes = Counter(MODE_LABEL.get(s.get('mode'), s.get('mode') or 'self-run') for s in keep)
    run_as = modes.most_common(1)[0][0] if len(modes) == 1 else ', '.join(f'{n} {m}' for m, n in modes.most_common())
    setup = (head.get('study') or {}).get('setup') or {}
    notes = [f"Built from {len(keep)} sessions exported by a research-tool-builder {label.lower()} tool. Practice sessions and unresolved imported copies are left out."]
    if any(t['scored'] for t in task_out.values()):
        notes.append('Success is the tool\'s automatic result (or, where a task has check questions, every one answered correctly), unless a moderator recorded an override with a reason.')
    if not all(t['scored'] for t in task_out.values()):
        notes.append(NOT_SCORED_NOTE.get(method, GENERIC_NOT_SCORED))
    if any(s.get('wave') for s in keep):
        notes.append(f"Each participant could take part up to {(content.get('repeat') or {}).get('entries', '?')} times. Each entry is reported separately, as code-e1, code-e2 and so on.")
    if setup.get('device'):
        notes.append(f"Setup: sessions {run_as}, on {DEVICE_LABEL.get(setup['device'], setup['device'])}" +
                     (f", reached through {DELIVERY_LABEL[head['study']['delivery']]}" if head['study'].get('delivery') in DELIVERY_LABEL else '') + '.')
    stopped = sum(1 for s in keep if s.get('stoppedBy') == 'participant')
    if stopped:
        notes.append(f"{stopped} participant(s) stopped early and chose to keep what they had done; their unfinished tasks are left out.")
    if any((s.get('consent') or {}).get('recordedBy') == 'moderator' for s in keep):
        notes.append('Where the moderator ran the tool, consent was read to the participant and recorded by the moderator.')
    if conds:
        notes.append('Between-participant conditions (' + ', '.join(c.get('label') or c['id'] for c in conds) + ') are shown in the participant table.')
    if any(t.get('ease') is not False for t in content['tasks']):
        notes.append('Ease is a 5-point question ("Overall, how easy or difficult was this task?"), not the 7-point Single Ease Question.')
    if other_versions:
        notes.append(f"{sum(by_hash[h] for h in other_versions)} session(s) ran on another content version and are not included. Build a separate report for them.")
    notes.append('Findings and summary points were generated from the data. Review and edit them before sharing.')
    study = {
        'title': content['title'], 'team': '', 'lede':
            f"{people} participant{'s' if people != 1 else ''}" +
            (f" ({'; '.join(x for x in [f'{len(keep)} entries' if len(keep) != people else '', ', '.join(f'{k} {v}' for k, v in segs.most_common())] if x)})" if segs or len(keep) != people else '') +
            f" took part in {'an' if label[0].lower() in 'aeiou' else 'a'} {label.lower()}{'' if method in METHOD_LABEL else ' study'} ({run_as}), {span}.",
        'date': last.date().isoformat(), 'authoredBy': '', 'facilitatedBy': '' if any(moderated(s.get('mode')) for s in keep) else 'Self-run: no facilitator', 'analysedBy': '',
        'method': f'{label}, {run_as}',
        'privacy': 'Participants are identified only by codes. Consent was recorded in every session.' if all(s.get('consent') for s in keep) else 'Participants are identified only by codes.',
        'seqScale': 5, 'seqLabels': EASE5, 'easeLabel': 'Ease (1–5)',
        'groupLabel': 'Hypothesis' if content.get('hypotheses') else 'Area',
        'objectives': [h['statement'] for h in content.get('hypotheses', [])] or ['Add the study objectives here.'],
        'methodDetail': [f"{label}, {len(content['tasks'])} task{'s' if len(content['tasks']) != 1 else ''}", ('A 5-point ease question after each task' if all(t.get('ease') is not False for t in content['tasks']) else 'A 5-point ease question after some tasks' if any(t.get('ease') is not False for t in content['tasks']) else 'No ease question') + (', and a confidence question where the task asks for one' if any(t.get('confidence') for t in content['tasks']) else ''),
                         'Closing questions after the last task' if content.get('closing') else 'No closing questions', f"Content version {content.get('version', 1)}"],
        'stimulus': [], 'scoringNotes': notes,
    }
    return {'study': study,
            'participantFields': [{'key': 'c-' + c['id'], 'label': c.get('label') or c['id'].capitalize()} for c in conds] + [{'key': 'segment', 'label': 'Segment'}, {'key': 'mode', 'label': 'Mode'}, {'key': 'devices', 'label': 'Devices'}, {'key': 'status', 'label': 'Status'}],
            'participants': participants, 'insights': insights, 'recommendations': [], 'hypotheses': groups, 'survey': survey}


def _selfcheck():
    r = {'status': 'completed', 'outcome': {'success': True, 'direct': False, 'tier': 'acceptable'}, 'moderator': {'override': None}}
    assert friction('tree-test', r) == 'minor' and friction('first-click', r) == 'minor' and friction('card-sort', r) is None
    assert success({'outcome': {'success': False}, 'moderator': {'override': {'success': True, 'reason': 'x'}}}) is True
    assert latest_runs({'runs': [{'taskId': 'T1', 'attempt': 1, 'status': 'interrupted'}, {'taskId': 'T1', 'attempt': 2, 'status': 'completed'}]})['T1']['attempt'] == 2
    assert sorted(['P10', 'P2', 'P1'], key=pcode) == ['P1', 'P2', 'P10']
    t = {'questions': [{'id': 'q', 'kind': 'choice', 'prompt': 'x', 'options': ['a', 'b'], 'correct': 'b'}]}
    assert task_success(t, {'status': 'completed', 'outcome': {'success': None}, 'answers': {'q': {'choice': 'b'}}}) is True
    assert task_success(t, {'status': 'completed', 'outcome': {'success': None}, 'answers': {'q': {'choice': 'a'}}}) is False
    assert task_success({}, {'status': 'completed', 'outcome': {'success': None}}) is None
    assert friction('stimulus', {'status': 'completed', 'outcome': {'success': None, 'friction': 'minor'}}) == 'minor'
    assert who({'participant': 'P3', 'wave': 2}) == 'P3-e2' and who({'participant': 'P3'}) == 'P3'
    runs = [('P1', {'outcome': {'level': 'with-help', 'codes': ['search']}, 'moderator': {'codes': {'help': True}, 'notes': 'Looked for a save button'}})]
    got = shared_findings({}, runs, {'codes': [{'id': 'search', 'label': 'Used search'}]})
    assert 'Completed with help (1)' in got[0][1] and 'Used search (1 of 1)' in got[1][1] and got[2][1] == 'Moderator noted: Looked for a save button'


if __name__ == '__main__':
    _selfcheck()
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    print(json.dumps(build(*load(sys.argv[1:])), ensure_ascii=False, indent=2))
