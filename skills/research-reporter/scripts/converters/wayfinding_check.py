"""Convert a wayfinding-check export (.json) into report data (references/data-format.md).

    python3 converters/wayfinding_check.py EXPORT.json > study.json
    python3 report.py build study.json -o report.html [--brand brand.json]

Participants are renamed P1..Pn in session order; their names never reach the
report data. To check that, pass the names file this writes with --names-out to
`report.py check --names`, and keep that file out of anything you share.

What this source means is in references/sources.md (wayfinding-check).
"""
import json
import re
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BLOCKS = [  # export block -> report area (id, heading)
    ('homepage', 'Homepage', 'Homepage'),
    ('product', 'Product', 'Product page'),
    ('navigation', 'Navigation', 'Main navigation'),
]
KIND_LABEL = {'observe': 'Observation', 'click': 'First click', 'nav': 'Navigation'}
GROUP_LABEL = {'non-member': 'Non-member', 'WC': 'Member (WC)', 'WA': 'Member (WA)'}
GROUP_PLURAL = {'Non-member': 'non-members', 'Member (WC)': 'WC members', 'Member (WA)': 'WA members'}
ARRIVAL_LABEL = {'homepage': 'Homepage', 'google': 'Google search', 'shared': 'Shared link'}
SEQ7 = ['Very difficult', 'Difficult', 'Somewhat difficult', 'Neutral', 'Somewhat easy', 'Easy', 'Very easy']

# The tool classifies each route: P = main target, A = acceptable target,
# X = somewhere else, S = a defined wrong route, R = recorded, needs review.
DONE = {'P': True, 'A': True, 'X': False, 'S': False}
SEV = {'P': 'none', 'A': 'minor', 'X': 'major', 'S': 'major'}


def day(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date()


def parse_choice(value, options):
    """'Yes: because…' -> ('Yes', 'because…'); 'Other: x' -> ('Other', 'x'); unknown text -> ('Other', text)."""
    if value in options:
        return value, None
    for opt in options + ['Other']:
        if value.startswith(opt + ':'):
            return opt, value[len(opt) + 1:].strip() or None
    return 'Other', value


def outcome(run):
    """(done, sev) for a scored task's run, or (None, None) when it needs review."""
    tier = (run.get('suggestion') or {}).get('tier')
    if run.get('end') == 'gave-up':
        return False, 'major'
    return DONE.get(tier), SEV.get(tier)


def end_point(run):
    s = run.get('suggestion') or {}
    if s.get('finalHref'):
        return s['finalHref']
    zones = s.get('zonesClicked') or []
    return zones[-1] if zones else 'no click recorded'


def targets(items):
    return '; '.join(i.get('note') or i.get('href') or i.get('zone') for i in items)


def build(export):
    content = export['content']
    sessions = sorted([s for s in export['sessions'] if not s.get('practice')], key=lambda s: s['createdAt'])
    pid = {s['id']: f'P{i + 1}' for i, s in enumerate(sessions)}
    n_all = len(sessions)

    participants = []
    for s in sessions:
        dev = Counter(r['breakpoint'] for r in s['runs'])
        participants.append({
            'id': pid[s['id']],
            'group': GROUP_LABEL.get(s['group'], s['group']),
            'arrival': ARRIVAL_LABEL.get(s['arrival'], s['arrival']),
            'devices': ' · '.join(f'{k.capitalize()} {v}' for k, v in dev.most_common()),
            'tasks': str(len(s['runs'])),
        })

    runs_by_task = {}
    for s in sessions:
        for r in s['runs']:
            if r.get('status') == 'completed':
                runs_by_task.setdefault(r['taskId'], []).append((pid[s['id']], r))

    areas, scored_rows = [], []
    for block, area_id, heading in BLOCKS:
        tasks = []
        for t in [t for t in content['tasks'] if t['block'] == block]:
            runs = runs_by_task.get(t['id'], [])
            if not runs:
                continue
            scored = t['kind'] in ('click', 'nav')
            results, findings, by = {}, [], {}
            for p, r in runs:
                res = {'seq': r.get('ease'), 'ms': r.get('durationMs')}
                if scored:
                    res['done'], sev = outcome(r)
                    if sev:
                        res['sev'] = sev
                    tier = 'G' if r.get('end') == 'gave-up' else (r.get('suggestion') or {}).get('tier')
                    by.setdefault(tier, []).append(p)
                results[p] = res

            def add(kind, text, who):
                if who:
                    findings.append({'id': f"{t['id']}-F{len(findings) + 1}", 'type': kind, 'text': text, 'who': who})

            if scored:
                add('positive', f"Went to the main target: {targets(t['primary'])}." if t['primary'] else 'Went to the main target.', by.get('P', []))
                add('minor', f"Reached an acceptable alternative instead of the main target ({targets(t['acceptable'])}).", by.get('A', []))
                missed = by.get('X', []) + by.get('S', [])
                if missed:
                    ends = Counter(end_point(r) for p, r in runs if p in missed).most_common(3)
                    add('major', 'Ended somewhere other than the target. Most common end points: ' + ', '.join(f'{e} ({c})' for e, c in ends) + '.', missed)
                add('major', 'Gave up before finishing the task.', by.get('G', []))
                add('investigate', 'Route recorded but not classified by the tool. Needs a researcher to review it.', by.get('R', []))
            elif t['codes']:
                add('investigate', 'Answers not coded yet: ' + ', '.join(c['label'] for c in t['codes']) + '.', [p for p, _ in runs])
            add('minor', 'Rated the task difficult (3 or lower out of 7).', [p for p, r in runs if (r.get('ease') or 7) <= 3])

            notes = sorted([(p, r['participantNotes'].strip()) for p, r in runs if (r.get('participantNotes') or '').strip()], key=lambda x: -len(x[1]))[:4]
            takeaway = []
            conf = [r['confidence'] for _, r in runs if r.get('confidence')]
            if conf:
                takeaway.append(f"Confidence afterwards: average {statistics.mean(conf):.1f} out of 7 from {len(conf)} answers ({t['confidence']})")
            if t['kind'] == 'click' and t['primary']:
                zones = {z['zone'] for z in t['primary'] if z.get('zone')}
                first = sum(1 for _, r in runs if (r.get('suggestion') or {}).get('firstZone') in zones)
                takeaway.append(f'First click on the main target: {first} of {len(runs)}.')

            dev = Counter(r['breakpoint'] for _, r in runs)
            task = {
                'id': t['id'],
                'title': t['title'],
                'stimulus': f"Prototype · starts at {t['start']} · " + ' / '.join(f'{k} {v}' for k, v in dev.most_common()),
                'tags': [KIND_LABEL.get(t['kind'], t['kind'])] + t['hypotheses'] + (['High risk'] if t['highRisk'] else []) + (['Reserve task'] if t['reserve'] else []),
                'scored': scored,
                'script': [t['scenario']] + t['questions'],
                'lookFor': [{'text': x.strip().rstrip('.') + '.', 'observed': None} for x in re.split(r'(?<=[.!?])\s+', t['watchFor']) if x.strip()],
                'results': results,
                'findings': findings,
                'quotes': [{'who': p, 'text': text} for p, text in notes],
                'takeaway': takeaway,
            }
            if not scored:
                task['scoreNote'] = 'Observation task: the export has no coded answers yet, so it cannot pass or fail. Code the answers to score it.'
            else:
                task['effNote'] = 'Inferred from the route: main target = no issue, acceptable alternative = minor, anywhere else or gave up = major.'
                done = [v['done'] for v in results.values() if v.get('done') is not None]
                scored_rows.append((sum(done) / len(done) if done else 1, task, sum(done), len(done)))
            tasks.append(task)
        if tasks:
            hyps = sorted({h for t in tasks for h in t['tags'] if re.fullmatch(r'CH\d+', h)}, key=lambda h: int(h[2:]))
            areas.append({'id': area_id, 'statement': heading, 'note': f"Tasks {', '.join(t['id'] for t in tasks)}. Hypotheses tested: {', '.join(hyps)}.", 'tasks': tasks})

    # Survey (closing questions)
    survey = []
    answered = [s.get('closing') or {} for s in sessions]
    for q in content['closingQuestions']:
        vals = [a[q['id']] for a in answered if q['id'] in a and a[q['id']]]
        if not vals:
            continue
        if q['kind'] == 'rank':
            items = [{'label': it, 'avg': statistics.mean(v.index(it) + 1 for v in vals if it in v), 'first': sum(1 for v in vals if v and v[0] == it)} for it in q['items']]
            survey.append({'kind': 'rank', 'prompt': q['prompt'], 'n': len(vals), 'items': items})
            continue
        opts = q['options'] + (['Other'] if q.get('other') else [])
        tally = {o: {'label': o, 'count': 0, 'comments': []} for o in opts}
        for v in vals:
            o, c = parse_choice(v, q['options'])
            tally.setdefault(o, {'label': o, 'count': 0, 'comments': []})
            tally[o]['count'] += 1
            if c:
                tally[o]['comments'].append(c)
        survey.append({'kind': 'choice', 'prompt': q['prompt'], 'n': len(vals), 'options': list(tally.values())})

    # Summary points generated from the numbers (factual; the team adds interpretation)
    insights = []
    for rate, task, d, n in sorted(scored_rows, key=lambda x: x[0])[:3]:
        miss = next((f for f in task['findings'] if f['type'] == 'major'), None)
        insights.append({'title': f"{task['title']}: {d} of {n} reached the target", 'body': (miss['text'] if miss else 'Most participants reached the target.') + f" (Task {task['id']})"})
    # Most agreed closing answer, skipping bare Yes/No answers that mean nothing without their question.
    choice = [(q, o) for q in survey if q['kind'] == 'choice' for o in q['options'] if o['label'] not in ('Yes', 'No', "Don't know", 'Other')]
    if choice:
        q, top = max(choice, key=lambda x: (x[1]['count'] / x[0]['n'], x[0]['n']))
        insights.append({'title': f"{top['count']} of {q['n']}: “{top['label']}”", 'body': f"Closing question: {q['prompt']}"})

    dates = sorted(day(s['createdAt']) for s in sessions)
    groups = Counter(p['group'] for p in participants)
    n_scored = sum(1 for a in areas for t in a['tasks'] if t['scored'])
    n_obs = sum(1 for a in areas for t in a['tasks'] if not t['scored'])
    span = f"{dates[0].day}–{dates[-1].strftime('%-d %B %Y')}" if dates[0].month == dates[-1].month else f"{dates[0].strftime('%-d %B')} – {dates[-1].strftime('%-d %B %Y')}"
    study = {
        'team': 'Website wayfinding study',
        'title': 'Wayfinding check: dōTERRA website',
        'lede': f"{n_all} participants ({', '.join(f'{v} {GROUP_PLURAL.get(k, k)}' for k, v in groups.most_common())}) ran self-guided tasks on a prototype of the website, on mobile and desktop, {span}. {n_scored} tasks were scored from where people clicked; {n_obs} observation tasks are waiting to be coded.",
        'date': dates[-1].isoformat(),
        'authoredBy': '',  # people or team who wrote the report: fill in
        'facilitatedBy': 'Self-run: no facilitator' if all(x.get('selfRun') for x in sessions) else '',
        'analysedBy': '',  # people or team who analysed the data: fill in
        'method': 'Self-run sessions on a clickable prototype',
        'privacy': f'Participants are anonymised as P1–P{n_all}. Their names stay in the source export.',
        'groupLabel': 'Area',
        'seqScale': 7,
        'seqLabels': SEQ7,
        'objectives': ['Not included in the export. Add the study objectives here.'],
        'methodDetail': [
            'Self-run (unmoderated) sessions in the wayfinding-check tool',
            f"{sum(1 for t in content['tasks'] if t['kind'] == 'click')} first-click, {sum(1 for t in content['tasks'] if t['kind'] == 'nav')} navigation and {sum(1 for t in content['tasks'] if t['kind'] == 'observe')} observation tasks, including {sum(1 for t in content['tasks'] if t['reserve'])} reserve tasks",
            'Each task ends with a 7-point ease question; some add a 1–7 confidence question',
            'Closing questions answered on screen at the end',
            f"Task content version {content.get('version')}, exported {export.get('exportedAt', '')[:10]}",
        ],
        'stimulus': [],
        'scoringNotes': [
            'First-click and navigation tasks pass when more than half of participants reach the main or an acceptable target, as classified by the tool.',
            'Friction is inferred from the route: main target = no issue, acceptable alternative = minor, anywhere else or gave up = major.',
            'Routes the tool could not classify are left out of the completion count and marked as needing review.',
            'Observation tasks are not scored: their coded answers were empty in this export.',
            'Summary points and findings were generated from the data. Review and edit them before sharing.',
        ],
    }
    return {
        'study': study,
        'participantFields': [{'key': 'group', 'label': 'Group'}, {'key': 'arrival', 'label': 'Entry route'}, {'key': 'devices', 'label': 'Devices'}, {'key': 'tasks', 'label': 'Tasks run'}],
        'participants': participants,
        'insights': insights,
        'recommendations': [],
        'hypotheses': areas,
        'survey': survey,
    }


def _selfcheck():
    assert parse_choice('Yes', ['Yes', 'No']) == ('Yes', None)
    assert parse_choice('Yes: more assurance', ['Yes', 'No']) == ('Yes', 'more assurance')
    assert parse_choice('Other: Lettering larger', ['A']) == ('Other', 'Lettering larger')
    assert parse_choice('free text', ['A']) == ('Other', 'free text')
    assert outcome({'end': 'found', 'suggestion': {'tier': 'P'}}) == (True, 'none')
    assert outcome({'end': 'found', 'suggestion': {'tier': 'R'}}) == (None, None)
    assert outcome({'end': 'gave-up', 'suggestion': {'tier': 'P'}}) == (False, 'major')


if __name__ == '__main__':
    _selfcheck()
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        raise SystemExit(__doc__)
    export = json.loads(Path(args[0]).read_text(encoding='utf-8'))
    if '--names-out' in sys.argv:
        names_file = Path(sys.argv[sys.argv.index('--names-out') + 1])
        args = [a for a in args if a != str(names_file)]
        names_file.write_text('\n'.join(s['participantId'] for s in export['sessions']), encoding='utf-8')
    print(json.dumps(build(export), ensure_ascii=False, indent=2))
