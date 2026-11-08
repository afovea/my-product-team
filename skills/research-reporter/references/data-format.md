# Report data format

Every source is converted into this one structure. The template reads nothing else, so two reports built from it read the same way, and an editor's in-page changes are saved back into it.

It lives in the report as `<script type="application/json" id="study-data">`. `scripts/report.py build` writes it there; `scripts/report.py check` validates it. The template's own example (Larkspur Energy) is a complete instance: read it before writing a converter.

## Top level

| Key | Required | What it is |
|---|---|---|
| `study` | yes | Title, dates, credits, method, scales. See below |
| `participants` | yes | `[{ "id": "P1", …fields }]`. IDs are P1..Pn, never names |
| `participantFields` | no | `[{ "key": "group", "label": "Group" }]`: which participant fields the appendix table shows, in order. Default: every key except `id` |
| `hypotheses` | yes | The task groups, in reading order. See below |
| `insights` | yes (may be empty) | `[{ "title", "body" }]` for the summary |
| `recommendations` | yes (may be empty) | `[{ "priority": "High"·"Medium"·"Low"·"Investigate", "title", "detail", "owner", "effort": "Small"·"Medium"·"Large", "evidence": ["T2.1-F1"] }]` |
| `survey` | no | Closing questions. See below |

## `study`

| Key | Notes |
|---|---|
| `title`, `lede`, `team` | Shown in the header. The lede says who took part, what they used, and when |
| `date` | ISO date of the last session. The page title becomes "Title · date" |
| `authoredBy`, `facilitatedBy`, `analysedBy` | People or teams, free text. Empty shows "Not set". Older reports' `author` becomes `authoredBy` |
| `method`, `privacy` | One line each. Privacy says how participants are anonymised |
| `brand`, `docType`, `logo` | Normally filled from the brand profile at build time (`references/theming.md`) |
| `seqScale`, `seqLabels` | Ease scale: 5 or 7 points, with one label per point |
| `groupLabel` | What a group of tasks is called. Default `Hypothesis`; use `Area` (or similar) when tasks are grouped by place, not by claim |
| `objectives`, `methodDetail` | Lists for the appendix |
| `stimulus` | `[{ "label", "url" }]` links to prototypes and files |
| `scoringNotes` | Lists any study-specific scoring assumption, shown in the appendix. Required whenever a converter infers anything |

## A group (`hypotheses[]`)

`{ "id": "H1", "statement": "…", "note": "…", "tasks": [ … ] }`. `statement` is the hypothesis wording, or the area name when `groupLabel` is not `Hypothesis`. Never invent hypothesis wording: if the source has only codes, group by area and put the codes in task `tags`.

## A task

| Key | Notes |
|---|---|
| `id`, `title`, `stimulus` | `stimulus` names what they used: prototype, page, device mix |
| `tags` | Short chips: task type, hypothesis codes, "High risk", "Reserve task" |
| `scored` | `false` for tasks that cannot pass or fail yet (uncoded observation tasks). Default `true` |
| `scoreNote` | Why an unscored task is unscored, shown instead of the completion count |
| `effNote` | How friction was rated, when it was inferred rather than observed |
| `results` | `{ "P1": { "done": true, "sev": "none", "seq": 6, "ms": 74519 } }`. One entry per participant who attempted the task |
| `override` | `{ "verdict": "pass"·"fail", "reason": "…" }`: a researcher's call against the computed verdict. The reason is required |
| `findings` | `[{ "id": "T1.2-F1", "type": "major"·"minor"·"investigate"·"positive", "text", "who": ["P2", "P5"] }]`. IDs stay stable: recommendations cite them |
| `quotes` | `[{ "who": "P4", "text": "…" }]`, verbatim |
| `screens` | Optional. `{ "device": "mobile"·"desktop", "asIs": {…}, "toBe": {…} }`. Each version is `{ "src": "data:image/…", "caption" }` for a screenshot, or a wireframe spec (`title`, `caption`, `blocks`) as in the example |
| `takeaway` | Short points. Generated facts are fine; interpretation is the researcher's |
| `script`, `lookFor` | Session materials, folded away by default. `lookFor`: `[{ "text", "observed": true·false·null }]`; `null` means not recorded |

### A result

| Field | Values | Meaning |
|---|---|---|
| `done` | `true`, `false`, `null` | Completed, did not, or waiting for review (left out of the completion count) |
| `sev` | `none`, `minor`, `major`, absent | Friction. Absent on every result → efficiency shows "Not rated" |
| `seq` | 1..`seqScale` | Single Ease Question answer |
| `ms` | number | Time on task. Adds a median time |

## `survey`

Choice question: `{ "kind": "choice", "prompt", "n", "options": [{ "label", "count", "comments": [] }] }`. `comments` holds the free text from answers like "Yes: because…" or "Other: …".

Ranking: `{ "kind": "rank", "prompt", "n", "items": [{ "label", "avg", "first" }] }`, where `avg` is the average position (1 = top) and `first` how many people put it first.
