# Method: card sort

Module: `assets/methods/card-sort.js` and `card-sort.css`. Version 1.0.0. The reference module: read it before writing another.

## What the participant does

Sorts a deck of cards into groups. Three modes:

| Mode | Groups available |
|---|---|
| `open` | Only groups the participant makes and names |
| `closed` | Only the study's categories |
| `hybrid` | The study's categories, plus groups the participant makes |

With `allowOther`, a "Doesn't fit anywhere" area takes cards that belong nowhere, each with a reason.

## Content, per task

| Field | Required | Notes |
|---|---|---|
| `mode` | yes | `open`, `closed` or `hybrid` |
| `cards` | yes | `[{ "id", "label" }]`, at least two, ids and labels unique. Warning above 40 |
| `categories` | closed and hybrid | `[{ "id", "label" }]`, at least two |
| `allowOther` | no | Adds the "Doesn't fit" area |
| `shuffle` | no | `false` keeps the deck in content order. Default: shuffled per participant from the session seed |
| `scenario` | yes | The instruction shown on the task screen |

Plus the shell's task fields: `id`, `title`, `hypothesis`, `confidence`, `notesPrompt`.

## Interaction

- **Three ways to move a card, always:** drag it onto a group; tap it to pick it up, then tap "Place here"; or the same with Tab, Enter and Space. A holding bar shows what is picked up, and Esc puts it back.
- Tapping a placed card picks it up again. "Put back in the cards to sort" returns it to the deck.
- "Start a new group with it" (open and hybrid) creates a group and moves focus to its name.
- "Remove group" sends its cards back to the deck. No confirmation: nothing is lost.
- Every placement is announced in the live region ("Track my parcel placed in Delivery").

## Finishing

| State | "I've finished" |
|---|---|
| A group the participant made has cards but no name | Blocked: "Give every group you made a name" |
| A card in "Doesn't fit" has no reason | Blocked |
| Cards still in the deck | Two-step: "Finish with 2 unsorted" |
| Otherwise | Finishes |

## Data

Events (`t` from Begin): `pick` (`item`, `from`, `via: "drag"` when dragged), `place` and `return` (`item`, `from`, `to`), `group-add`, `group-name` (`group`, `name`), `group-remove` (`group`, `returned`), `other-reason` (`item`).

Outcome:

```json
{
  "success": null,
  "groups": [{ "id": "c-payments", "name": "Payments and billing", "fixed": true, "cards": ["d2", "d4"] }],
  "other": [{ "card": "c6", "reason": "Not a help question" }],
  "unsorted": [],
  "moves": 12
}
```

`success` is always `null`: a card sort has no right answer per participant. Agreement and co-occurrence are worked out across participants, in the report.

## Quick figures

Median number of groups used, and how many participants left cards unsorted.
