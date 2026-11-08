# Method: classification

Module: `assets/methods/classification.js` and `classification.css`. Version 1.0.0. Ported from the query-sorting tool.

## What the participant does

Puts each item (a search query, a support message, a page title) into one of the study's categories, one item at a time, using each category's description. Used to test whether a set of categories is clear enough that different people classify the same way. Participants are usually raters: staff or experts, not customers.

## Content, per task

| Field | Required | Notes |
|---|---|---|
| `categories` | yes | `[{ "code", "label", "definition" }]`, at least two. Codes unique; `NONE` is reserved. A missing definition is a warning |
| `items` | yes | `[{ "id", "text", "gloss", "lang" }]`, at least two. `gloss` is an optional translation or explanation; `lang` marks the text's language. Warning above 60 |
| `allowNone` | no | Default `true`: adds "None of these", which needs a note |
| `noneLabel` | no | Wording for that option |
| `shuffle` | no | `false` keeps content order. Default: shuffled per participant |

## Interaction

- One item per screen, with "Item n of N · x answered". Previous and Next move between items; Next needs an answer (and a note for "None of these").
- Categories are a native radio group, so arrow keys move between them.
- Two flags per item: "Unsure: I am guessing" and "Unfamiliar: I don't know what this means".
- "I've finished" is blocked until every item is answered. One ease rating covers the whole set.

## Data

Events: `item` (`item`, `index`) on moving, `choose` (`item`, `choice`), `flag` (`item`, `flag`, `on`), `note` (`item`).

Outcome:

```json
{
  "success": null,
  "answers": { "Q1": { "choice": "B", "unsure": false, "unfamiliar": false, "note": "" } },
  "itemMs": { "Q1": 4120 }
}
```

`success` is always `null`: agreement between raters is worked out in the report (share of answers matching each item's most common answer, items every rater agreed on, items under 70% agreement, flags). Statistics such as Cohen's kappa belong there too, not in the tool.

## Quick figures

Share of answers marked unsure, and share answered "None of these".
