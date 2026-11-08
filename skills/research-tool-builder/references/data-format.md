# Session data format

Every tool exports the same structure, whatever the method. One reader, `research-reporter`'s generic converter, turns any export into a report. A method adds its own fields in exactly two places, a run's `outcome` and its event types, and nowhere else. Everything else a method needs (questions inside a task, variants, conditions, repeated sessions) is shared and set by content; [methods-catalogue.md](methods-catalogue.md) shows where each research method's data lands.

Format name `research-sessions`, version 1.

## Rules for every field

- Times are ISO 8601 in UTC (`2026-11-08T14:03:22.415Z`). Durations are whole milliseconds.
- Ids are short strings. Participant codes are letters then digits (`P3`, `M12`); no names, ever.
- Unknown is `null`, not an empty string or a missing field. Not applicable is left out.
- Readers reject a file whose `formatVersion` is higher than they understand. Adding an optional field does not change the version; renaming, removing or changing the meaning of one does.
- The same structure is kept in the tool's storage and written to export files, so a save and an export can never disagree.

## The file

```json
{
  "format": "research-sessions",
  "formatVersion": 1,
  "exportedAt": "2026-11-08T16:40:00.000Z",
  "tool": { "method": "card-sort", "methodVersion": "1.0.0", "label": "Card sort", "build": "moderator" },
  "study": { "id": "checkout-labels", "title": "Checkout labels", "delivery": "participant-file", "setup": { "facilitation": "mixed", "device": "both" } },
  "contents": { "c9f2a1e0": { "version": 3, "...": "the full study content at that version" } },
  "sessions": [ { "...": "see Session" } ],
  "imports": [ { "file": "checkout-labels_card-sort_P4_2026-11-07.json", "sha256": "…", "at": "…", "sessions": 1 } ]
}
```

| Field | Meaning |
|---|---|
| `tool.method` | The method module: `card-sort`, `classification`, `tree-test`, `first-click`, `stimulus`, … |
| `tool.label` | The module's own name for itself, so a reader that does not know the method can still name it |
| `tool.build` | `moderator` or `participant` copy |
| `study.delivery` | How the tool reached people: `moderator-device`, `participant-file`, `shared-link`, `hosted` |
| `study.setup` | The test setup the tool was built for (foundations, section 9): `facilitation` (`in-person`, `remote`, `self-run`, `mixed`) and `device` (`moderator`, `participant`, `both`) |
| `contents` | Every content version any session in this file used, keyed by content hash. Sessions point at a hash, so a file with 40 sessions on one version carries the content once |
| `imports` | Files merged into this one, with a SHA-256 of each as received |

## Session

```json
{
  "id": "s_8k2m4q",
  "studyId": "checkout-labels",
  "participant": "P3",
  "wave": 2,
  "segment": "member",
  "practice": false,
  "mode": "remote",
  "contentHash": "c9f2a1e0",
  "contentVersion": 3,
  "consent": { "notice": 2, "items": ["data-notice", "over-18", "recording"], "at": "2026-11-08T14:00:05.000Z" },
  "plan": { "seed": 913204, "order": ["T3", "T1", "T2"], "device": { "T1": "mobile" }, "itemOrder": { "T1": ["c4", "c1", "c9"] }, "conditions": { "arrival": "search" } },
  "status": "completed",
  "startedAt": "2026-11-08T14:00:00.000Z",
  "updatedAt": "2026-11-08T14:31:40.000Z",
  "finishedAt": "2026-11-08T14:31:40.000Z",
  "interruptions": 0,
  "runs": [ { "...": "see Run" } ],
  "closing": { "q-change": { "choice": "Show prices sooner" }, "q-rank": { "order": ["Reviews", "Video", "Sourcing"] } },
  "debrief": { "notes": "Hesitated on the second task", "checkedFreeText": true }
}
```

| Field | Values |
|---|---|
| `studyId` | The study the session belongs to, so a shared store holding several studies never mixes them |
| `wave` | Only in studies whose content sets `repeat: { "entries": n }` (diary studies, rounds): which of the participant's sessions this is, from 1. A code can then run up to `n` sessions; otherwise one |
| `segment` | One of the study's own segments, or `null` |
| `practice` | `true` sessions are kept but left out of every figure and report |
| `mode` | How this session was actually run: `in-person`, `remote` (moderated over a call) or `self-run`. From the setup; chosen per session in a mixed study, and correctable in a review. Older exports say `moderated`, read as `in-person` |
| `stoppedBy` | `"participant"` when the participant used Stop and kept their answers (status `ended-early`). A participant who deletes leaves no session |
| `consent.notice` | Version of the data notice shown |
| `consent.recordedBy` | `"moderator"` when the moderator read the notice out and ticked for the participant (moderator-led methods) |
| `plan` | Everything needed to replay the session: the seed, the task order, any per-task device, the order of items inside tasks that shuffle them, and `conditions`: the study's between-participant conditions this person was assigned (an entry route, a design variant), keyed by the condition ids in the content. A moderator's change to any of these is recorded in `plan.overrides` with a reason |
| `status` | `in-progress`, `completed`, `ended-early` |
| `closing` | Answers keyed by closing-question id: `{ "choice", "comment" }`, `{ "choices": [] }`, `{ "order": [] }`, `{ "text" }`, `{ "value" }` for a scale |
| `debrief.checkedFreeText` | The moderator confirmed free-text answers hold no personal details |

## Run

One attempt at one task. A retake is a new run with `attempt` + 1 and `retakeOf` pointing at the run it replaces.

```json
{
  "id": "r_q81x0c",
  "taskId": "T1",
  "attempt": 1,
  "retakeOf": null,
  "status": "completed",
  "device": "desktop",
  "variant": "B",
  "presentedAt": "2026-11-08T14:02:10.000Z",
  "beganAt": "2026-11-08T14:02:18.200Z",
  "endedAt": "2026-11-08T14:03:41.900Z",
  "readingMs": 8200,
  "durationMs": 83700,
  "outcome": { "success": true, "...": "the method's own fields" },
  "ease": 4,
  "confidence": null,
  "answers": { "recall": { "choice": "Team" }, "why": { "text": "It was highlighted" } },
  "notes": "I'd expect this under Account",
  "events": [ { "t": 0, "type": "ready" }, { "t": 2140, "type": "pick", "item": "c4" } ],
  "eventsTruncated": false,
  "moderator": { "reviewed": false, "override": null, "codes": {}, "notes": "" }
}
```

| Field | Values |
|---|---|
| `status` | `completed`, `gave-up` (used "I can't do this"), `skipped` (moderator), `interrupted` (page closed mid-task) |
| `device`, `scale` | The device size the task material was shown at, and the scale it was drawn at to fit the window (1 when not scaled) |
| `awayMs` | Time during the task when the tool's window was not in front (another tab, app or window), from the `focus-lost` and `focus-back` events. Left out when none |
| `variant` | Which design or version this run showed, for comparisons within a participant: the task's `variant` from the content, or set by the module. Left out when there is none |
| `readingMs` | Task shown to Begin pressed, tour time removed |
| `durationMs` | Begin to the end of the task |
| `outcome.success` | `true`, `false`, or `null` when only a researcher can judge it (observation tasks, routes the tool could not classify) |
| `outcome.friction` | Optional, any method: `none`, `minor` or `major`, when the method can tell how much trouble the participant had. The report uses it as the run's efficiency rating |
| `ease`, `confidence` | 1–5, or `null` when not asked (the task sets `ease: false`) or not answered |
| `answers` | Answers to the task's own `questions`, keyed by question id, in the same shapes as `closing`. Left out when the task has none. Where a question has a `correct` answer in the content, the report scores the task from it |
| `notes` | The participant's own words, verbatim |
| `events` | Ordered; `t` is milliseconds since Begin. Capped at 1,000 per run, with `eventsTruncated` set when the cap is reached |
| `moderator.override` | `{ "success": true, "reason": "…" }` when a researcher disagrees with the automatic result. The reason is required |
| `moderator.codes` | The study's observation codes the moderator ticked in a review, keyed by code id (`{ "search": true }`) |
| `moderator.notes` | The moderator's notes on this run, from a review |

### Events every method may use

| Type | Fields | When |
|---|---|---|
| `ready` | | Task material is on screen and usable |
| `focus-lost`, `focus-back` | | The tool's window lost or regained focus mid-task |
| `resize` | `w`, `h` | The window changed size mid-task |
| `help` | `topic` | The participant opened help or a hint |
| `end` | `reason` | What ended the task: `finished`, `gave-up`, `target`, `timed`, `moderator` |
| `marker` | `label` | A moment the moderator marked, to line notes up with a recording |
| `code` | `code`, `on` | The moderator ticked or unticked one of the study's observation codes |

Method event types are listed in each method's specification.

### Method outcomes

| Method | `outcome` fields beyond `success` |
|---|---|
| `card-sort` | `groups: [{ "id", "name", "fixed", "cards": [] }]`, `other: [{ "card", "reason" }]`, `unsorted: []`, `moves` |
| `classification` | `answers: { itemId: { "choice", "unsure", "unfamiliar", "note" } }`, `itemMs: { itemId: ms }`. `success` is `null`: agreement is worked out across raters, in the report |
| `tree-test` | `path: []`, `direct` (no backtracking beyond the study's tolerance), `backtracks`, `trail: [[]]` |
| `first-click` | `firstTarget`, `tier` (`main`, `acceptable`, `wrong`, `unclassified`), `firstInteractionMs`, `endHref`, `clicks` |
| `observation` | Moderator-logged: `level` (the study's outcome level, or `gave-up`), `codes`, `markers`, `loggedBy: "moderator"`, with `success` and `friction` from the level. Participant-run: `opened` (they opened the product link), `loggedBy: "participant"`, `success: null` |
| `stimulus` | `shown` (the order stimuli appeared in), `exposedMs`. `success` is `null`; the report scores tasks with `correct` answers |
| any other | Whatever the module records, plus `success` and, where it can tell, `friction`. The report reads these without knowing the method |

## File names

`{study-id}_{method}_{participant or "all"}_{YYYY-MM-DD}.json`, for example `checkout-labels_card-sort_P3_2026-11-08.json`. A CSV, when a team asks for one, has one row per run, the same name with `.csv`, and never replaces the JSON.

## Import and merge

- Sessions are matched by `id`. A session already present is kept; if the incoming copy is newer (`updatedAt`) and differs, both are kept and the moderator chooses.
- Content versions merge by hash.
- Every imported file is recorded in `imports` with its SHA-256, computed by the tool on receipt.
- A file from a different study id, or with a higher `formatVersion`, is refused with a plain explanation.

## Into research-reporter

`research-reporter` reads this format with one converter for every method, `scripts/converters/research_sessions.py`:

| research-sessions | Report data |
|---|---|
| `study.title`, last `finishedAt` | `study.title`, `study.date` |
| content `hypotheses` (id and wording) | `hypotheses[]` with their real statements |
| content tasks | `tasks[]`: id, title, stimulus, tags, script |
| sessions where `practice` is false | `participants[]`: code, segment, devices, tasks run |
| run `outcome.success` (after `moderator.override`), or the answer key of the task's questions | `results[code].done` (`null` stays `null`, still to review) |
| run `ease` | `results[code].seq`, with `study.seqScale: 5` and the 5-point labels |
| run `durationMs` | `results[code].ms` |
| `outcome.friction`, a method's friction rule, or a moderator friction code | `results[code].sev` |
| run `answers` | `survey[]`, one item per question, prefixed with the task |
| run `variant` | A finding comparing variants, when a task's runs differ |
| `plan.conditions` | A column per condition in the participant table |
| `wave` | Participants shown as `P3-e1`, `P3-e2` |
| `mode`, `study.setup`, `stoppedBy`, `consent.recordedBy` | The mode per participant, a setup line in the scoring notes, and notes on stopped sessions and moderator-recorded consent |
| `outcome.level`, `outcome.codes`, `moderator.codes`, `moderator.notes` | Findings for any method: how tasks ended, what was observed (with the code labels), and the moderator's notes |
| `awayMs` | The median time away, as a task takeaway |
| run `notes` | `quotes[]` |
| `closing` with the content's closing questions | `survey[]` |
| `consent`, `debrief.checkedFreeText` | Privacy line, and a check before building |
| sessions on more than one content version | One report per version, or one report with the difference stated in `scoringNotes` |

The report labels the ease measure from the data: a 5-point study reads "Ease (1–5)"; only a 7-point study is called the Single Ease Question, and a task that did not ask it says "Not asked". Card sorts and classification have no per-person success, so their tasks are reported as not scored, with agreement across participants in the findings. A method the converter has no findings for gets generic ones: who succeeded and who did not, the most-chosen answers, and differences between variants.

## How the four existing tools map

Checked against what each tool records today. Anything dropped is dropped on purpose.

| Today | In this format | Notes |
|---|---|---|
| Participant name typed at setup (card sort, classification, tree test) | `participant` code | Names dropped |
| `participantInternal`, `group` | `segment` | |
| `practiceRun`, `practice` | `practice` | Now always saved and flagged |
| `contentVersion` | `contentVersion` and `contentHash` | Plus the content itself in `contents` |
| `deckOrder`, `order`, wayfinding `plan` | `plan` | Seed added |
| Card sort `groups`, `other`, `unsorted`, `moves`, `trail` | `outcome` and `events` (`pick`, `place`) | Trail becomes timed events |
| Classification `answers{b,u,f,n}`, `ms{}` | `outcome.answers`, `outcome.itemMs` | |
| Classification debrief `hardest`, `confidence` | `closing` answers, `confidence` | Confidence moves to the 5-point participant scale |
| Tree test `path`, `success`, `direct`, `navTrail` | `outcome.path`, `success`, `direct`, `trail` | `backtracks` now recorded; breadcrumb jumps logged as events |
| Moderator-rated confidence 1–5 (card sort, tree test) | `moderator.codes` if still wanted | The participant's own `confidence` replaces it |
| Wayfinding `readingMs`, `durationMs`, `firstInteractionMs` | Same names | |
| Wayfinding `suggestion.tier` P/A/S/X/R | `outcome.tier` main/acceptable/wrong/wrong/unclassified (search as `search`) | Plain words instead of letters |
| Wayfinding `ease` and `confidence` 1–7 | `ease`, `confidence` 1–5 | New studies only; old exports keep their own scale |
| Wayfinding `moderator{…}`, `interruptions`, `retakeOf`, `attempt` | Same | |
| Wayfinding `closing`, `imported{sha256}` | `closing`, `imports[]` | Checksum computed by the tool itself |
| Wayfinding `events` (click, route, menu-open…) | `events` with `t` from Begin | First-click method types |
| Wayfinding `arrival` and `planOverrides` | `plan.conditions.arrival`, `plan.overrides` | Entry route is a between-participant condition |
| Wayfinding `breakpoint`, `scale`, `windowResized` | `device`, `scale`, `resize` events | |
| Wayfinding `position`, `cursor`, `phase` | Not stored | Position comes from `plan.order`; cursor and phase are the tool's working state, not data |

Tested on a real wayfinding-check export (14 sessions, 184 runs, 1,691 events): every run, rating, note, event, moderator field and closing answer maps across, no participant names come through, and the file is about half the size because content is stored once. The two things the old tool never recorded, consent and the random seed, show up as `null`, which is the point: a tool built on this format cannot leave them out.
