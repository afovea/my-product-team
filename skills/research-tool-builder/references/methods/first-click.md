# Method: first click

Module: `assets/methods/first-click.js` and `first-click.css`. Version 1.0.0. Ported from the wayfinding check.

## What the participant does

Sees a working prototype and clicks where they would go first to do the task. By default the task ends on that first click; a task can instead let them keep clicking and press "I've finished".

## Content

| Field | Where | Notes |
|---|---|---|
| `prototype` | study | One self-contained HTML page: its scripts, styles and images inline (images as `data:` URIs). Anything loaded from the internet is blocked and is a content error. Add it at build time with `tool.py build … --prototype page.html` |
| `device` | study or task | `desktop` (1440×1024), `tablet` (768×1024) or `mobile` (390×844). Default desktop |
| `start` | task | The prototype route to open at, as a hash (`#home`) |
| `targets` | task | `{ "main": [ … ], "acceptable": [ … ] }`. Each target is `{ "zone": "header-orders" }` or `{ "href": "#orders" }` |
| `endOn` | task | `first-click` (default) or `finish` |

### Preparing the prototype

Mark everything you want to recognise with `data-zone="…"`: links, buttons, whole regions. A click is matched to the nearest element with a zone, and to the nearest link's `href`. Zones named in targets but missing from the prototype are warnings. Links to other pages are stopped inside the prototype, so it stays on screen; hash routes (`#orders`) work and are recorded.

## How it is shown

- The prototype runs in a sandboxed frame (scripts allowed, nothing else), at the device size, scaled down to fit the stage and framed apart from the tool.
- A small bridge script is added to the prototype. It reports `ready`, `click` (zone, href, the visible label, x and y), `route` and `search` to the tool, each carrying a code issued for that session. The tool ignores every message without it, and any message not from its own frame.
- The scale used is recorded with the run.

## Data

Events: `frame-ready`, `click` (`zone`, `href`, `label`, `x`, `y`, `first: true` on the first), `route` (`path`), `search` (`query`).

Outcome:

```json
{ "success": true, "tier": "acceptable", "firstTarget": "footer-help", "firstInteractionMs": 7042, "endHref": "#home", "clicks": 1 }
```

| `tier` | Meaning | `success` |
|---|---|---|
| `main` | The first click hit a main target | `true` |
| `acceptable` | It hit an acceptable target | `true` |
| `wrong` | It hit something else | `false` |
| `unclassified` | The task has no targets | `null` |

A give-up has no tier and `success: false`. The report rates friction from the tier (main none, acceptable minor, wrong or gave up major) and describes first clicks in the prototype's own words ("Help and contact").

## Quick figures

How many clicked the main target first, and the median time to the first click.

## Limits

- The prototype must be one page. Multi-page prototypes need building as a single page with hash routes.
- The prototype's own accessibility is outside the tool's control.
