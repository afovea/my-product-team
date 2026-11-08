# Method: stimulus

Module: `assets/methods/stimulus.js` and `stimulus.css`. Version 1.0.0.

## What the participant does

Sees material (one image or passage, or several side by side), for as long as they like or for a fixed time, then answers the task's own questions. One module covers five-second tests, preference tests, desirability, concept tests, comprehension tests and plain questionnaires; see [the catalogue](../methods-catalogue.md) for the pattern each uses.

## Content

| Field | Where | Notes |
|---|---|---|
| `stimuli` | task | `[{ "id", "label", "image" or "text", "alt" }]`. Images are `data:` URIs (nothing loads from the internet) and need `alt` text. `label` is shown under each when there are several; otherwise "Option 1", "Option 2" |
| `shuffle` | task | Several stimuli are shown in a seeded random order unless `false`. The order shown is recorded |
| `exposureMs` | task | Optional. Hides the material and ends the task after this long (5000 for a five-second test). There is then no finish button |
| `questions` | task | Shared base: asked after the task, in the closing-question kinds (`choice`, `choices`, `scale`, `rank`, `text`), with `required` where an answer is needed. Answers go in `run.answers` |
| `correct` | question | On `choice` or `choices` questions: the right answer, or a list of them. The report counts the task as a success when every question with `correct` is answered right |
| `ease` | task | Shared base: `false` when there is nothing to rate (a five-second exposure, a preference). Keep it for tasks that take effort, such as comprehension |
| `notesPrompt`, `questionsHeading` | task | Shared base: `false` hides the notes box; the heading for the questions screen when ease is off |

## Data

Events: `stimulus-shown` (`order`), `stimulus-hidden` (when the exposure time ends).

Outcome:

```json
{ "success": null, "shown": ["B", "A"], "exposedMs": 5012 }
```

`success` is always `null` from the module: it does not judge. The report scores tasks that have `correct` answers and leaves the rest as not scored, with the answers tallied in the survey section and the most-chosen answers as findings.

`exposedMs` is the real time the material was on screen. Browsers slow timers in background tabs, so a timed task in a window the participant has moved away from runs long. Check `exposedMs` against `exposureMs` before reporting a five-second test.

## Quick figures

Median viewing time, for untimed tasks.

## Limits

- Material is images and plain text. A working prototype belongs in `first-click`.
- Very large images make the export large, since the content travels with it. Keep images under about 300 KB each.
