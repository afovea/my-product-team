# Data sources

One converter per source tool, in `scripts/converters/`. Each turns that tool's export into the report data format and prints it as JSON. Add a section here for every converter: what the source means is knowledge the next person needs.

## Writing a converter for a new source

1. Read a real export end to end before mapping anything. Summarise its structure for the user.
2. List every code, tier or status value the source uses, and ask the user what each means. Do not infer meaning from a code's letter.
3. Map to `references/data-format.md`:
   - participants become P1..Pn in session order; write the real names to a separate file only for `report.py check --names`
   - a task with no way to pass or fail yet is `"scored": false` with a `scoreNote`
   - a result the tool could not classify is `"done": null`
   - friction is only inferred when the user agrees how; put the rule in the task's `effNote` and in `study.scoringNotes`
   - generated findings state facts with "x of n": what happened, where people ended up. No interpretation
   - quotes are verbatim free text from participants
4. Put every assumption in `study.scoringNotes`. A reader of the report should be able to see how it was scored.
5. Add a `_selfcheck()` with asserts for the parsing and mapping rules, run before conversion.
6. Run it on the real export, then `report.py build` and `report.py check --names`.

## research-sessions (tools built with research-tool-builder)

Every tool built with the `research-tool-builder` skill exports the same format, `research-sessions` version 1, whatever its method. One converter reads them all:

```bash
python3 scripts/converters/research_sessions.py export.json [more.json …] > study.json
```

| Method | Scored per person | Findings generated |
|---|---|---|
| `tree-test` | Yes: the chosen answer against the accepted paths | Direct and indirect success, most common wrong answers, give-ups |
| `first-click` | Yes: the first click's tier | Main and acceptable first clicks, most common wrong first clicks in the prototype's own words, give-ups |
| `card-sort` | No | Closed and hybrid: agreement per card. Open: cards grouped together by 75% or more, cards with no consistent home, group names used |
| `classification` | No | Agreement between raters, items everyone agreed on, items under 70% agreement, unsure and unfamiliar flags |
| `stimulus`, and any method without its own findings | Where the run's `outcome.success` is set, or the task's questions have `correct` answers | Who succeeded and who did not (with the check questions they got wrong), give-ups, runs left to judge, and the most-chosen answer to each question with no right answer |

Common to all: participants by code and segment, how each session was run (moderated in person, moderated remotely or self-run, and whether the participant stopped early), the test setup in the scoring notes, a column per between-participant condition, entries as `P3-e1`, `P3-e2` in repeated studies, a comparison by variant when a task's runs showed different ones, answers to each task's own questions in the survey section (correct answers marked), `outcome.friction` as efficiency where a module sets it, "Not asked" for tasks without the ease question, findings from moderator-recorded outcome levels, observation codes and moderator notes (including reviews of imported sessions), time away from the tool, the content's own hypothesis wording, ease on a 5-point scale labelled "Ease (1–5)", confidence where asked, the four longest notes per task as quotes, closing questions (choice, multiple choice, scale, ranking and written answers), and low-ease findings. Practice sessions, unresolved imported copies and sessions still in progress are left out. Sessions on a different content version from the majority are left out and named in the scoring notes.

## wayfinding-check

Exports from the wayfinding-check prototype testing tool (`"app": "wayfinding-check"`): self-run, unmoderated sessions on a clickable prototype, mobile and desktop.

| In the export | Means | In the report |
|---|---|---|
| `content.tasks[].kind` | `observe` (spoken or written answers), `click` (first click), `nav` (find a page through the menu) | Tags. `observe` tasks are unscored until coded |
| `content.tasks[].block` | Site area: `homepage`, `product`, `navigation` | Groups, with `groupLabel: "Area"` |
| `content.tasks[].hypotheses` | Hypothesis codes (CH1…). The export has no wording for them | Task tags |
| `runs[].suggestion.tier` | `P` main target, `A` acceptable target, `X` somewhere else, `S` a defined wrong route, `R` recorded but not classified | `done`: P/A true, X/S false, R null |
| `runs[].end` | `found`, `destination`, `gave-up` | `gave-up` is not done, major friction |
| `runs[].ease`, `.confidence` | 1–7 answers | `seq` on a 7-point scale; confidence in the takeaway |
| `runs[].durationMs` | Time on task | `ms` |
| `runs[].participantNotes` | The participant's written answer | Quotes (up to the four longest per task) |
| `runs[].moderator` | Coding by a researcher. Empty in every export seen so far | Not used yet: coded observation answers are a known gap |
| `sessions[].closing` | Closing-question answers, some as "Yes: reason" or "Other: text" | `survey` |
| `sessions[].group` | `non-member`, `WC`, `WA` | Participant field. The tool asks for members and non-members to be reported apart; the template cannot split results by group yet |

Friction is inferred from the route (main target none, acceptable minor, elsewhere or gave up major). The tier meanings above were read from the data and confirmed against the task definitions, not from the tool's documentation: confirm them with the team that runs the tool before relying on a report.
