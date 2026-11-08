# Method: observation

Module: `assets/methods/observation.js` and `observation.css`. Version 1.0.0.

For anything the tool cannot see inside: a live website, a native app, a physical product, or a conversation. It runs two ways, chosen by the test setup rather than by the study:

| Way | Where | What happens |
|---|---|---|
| Moderator-logged | A moderator copy (unless the study sets `"observer": "participant"`) | The device stays with the moderator. No hand-over: the moderator reads the consent, task and questions out, enters the answers, and logs the task while it happens |
| Participant-run | A participant copy, a shared link, or a moderator copy with `"observer": "participant"` | The participant opens the product from the task screen, does the task there and comes back to press "I've finished". The tool records the time and how long they were away from it |

With `--device both`, both happen in one study: the moderator logs on their copy while the participant uses their own, and the participant's file is imported beside the moderator's session.

## Content

| Field | Where | Notes |
|---|---|---|
| `scenario` | task | The task, or the interview topic, as read out or shown |
| `link` | task | `{ "url": "https://…", "label": "Open the website" }`. Participant-run: opens the product in a new tab. Must be https |
| `levels` | study | How a task can end, for the moderator to choose: `[{ "id", "label", "success": true / false / null, "friction": "none" / "minor" / "major" }]`. Default: Completed (success, no friction), Completed with help (success, minor), Did not complete (failure, major), Not attempted (not judged) |
| `levels: false` | task | No outcome: an interview topic or an activity to observe. Ends with Next topic |
| `codes` | study | Shared base: observation codes, `[{ "id", "label" }]`, ticked during the task and in reviews |
| `observer` | study | `"participant"` to run participant-run even on a moderator copy (a kiosk study of a live site) |
| `questions`, `ease` | task | Shared base. Participant-run tasks should ask "Did you manage it?" and, where possible, a check question with a `correct` answer ("What was the setting called?"), since the tool cannot see the product |

## Data

Events: `marker` (`label`), `code` (`code`, `on`), `open-product` (`url`), and the shared `focus-lost` and `focus-back`.

Moderator-logged outcome:

```json
{ "success": true, "friction": "minor", "level": "with-help", "codes": ["search", "help"], "markers": 1, "loggedBy": "moderator" }
```

"The participant gave up" gives `level: "gave-up"`, `success: false`, `friction: "major"`.

Participant-run outcome:

```json
{ "success": null, "opened": true, "loggedBy": "participant" }
```

with the run's `awayMs` and the answers to the task's questions. Success then comes from a check question's `correct` answer, or from a moderator's review of the imported session.

## Quick figures

How tasks ended, by level.

## Limits

- The tool sees only what the moderator logs or the participant reports. Clicks and pages inside the product need the product's own analytics, or a screen recording.
- Recordings stay in the call or recording software. Markers carry their time from the start of the task, to line notes up with a recording.
- Time away counts any time the tool's window is not in front, not only time in the product.
