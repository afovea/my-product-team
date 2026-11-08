# Method: tree test

Module: `assets/methods/tree-test.js` and `tree-test.css`. Version 1.0.0. Ported from the wayfinding trial.

## What the participant does

Finds where something lives in a text-only menu: no design, just labels. They open sections, go back up when they need to, and choose the item they would expect to hold the answer. The task ends when they confirm their answer, so there is no "I've finished" button.

## Content

| Field | Where | Notes |
|---|---|---|
| `tree` | study, or a task to override it | `[{ "label", "children": [] }]`; an item without children is an answer |
| `accepted` | task | `[["Help", "Returns", "Refund timing"]]`: every path that counts as right. Each must exist in the tree |
| `backtrackTolerance` | task | Backtracks allowed while still counting as direct. Default `0` |
| `scenario` | task | What the participant is trying to do, in their words, without the target's label |

A task with no accepted answer is a warning: success cannot be worked out.

## Interaction

- A breadcrumb shows where they are; every earlier level is a link. "Back up" goes one level up. Both count as backtracks.
- Sections show an arrow. Choosing an answer opens an inline "Is X your answer?" with "This is my answer" and "Keep looking". Esc closes it.
- "I can't do this" is always available.

## Data

Events: `open` (`path`), `up` (`path`), `jump` (`path`), `select` (`path`), `unselect`, `answer` (`path`).

Outcome:

```json
{ "success": true, "path": ["Help", "Returns", "Refund timing"], "direct": false, "backtracks": 1, "trail": [[], ["Help"], ["Help", "Payments"], ["Help"], ["Help", "Returns"]] }
```

`success` is `true` when the chosen path matches an accepted one (case is ignored), `false` for a wrong answer or a give-up, and `null` when the task has no accepted answers. `direct` is success with backtracks within the tolerance.

The report rates friction from this: direct is no issue, success after backtracking is minor, wrong or gave up is major.

## Quick figures

Direct success: how many found the answer without backtracking.
