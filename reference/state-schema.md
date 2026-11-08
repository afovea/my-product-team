# Pipeline state schema

Version: `1`

The delivery pipeline shares state between skills through two JSON files. This document is the contract. Skills referencing pipeline state must conform to it.

Both files live under a host-writable cache directory. The default is `.claude/cache/`, but the location is declared by the consuming project — see [`project-adapter.md`](./project-adapter.md), key `state.directory`. Everywhere below, `<cache>/` means that directory.

| File | Owner | Purpose |
|---|---|---|
| `<cache>/pipeline.json` | `run-pipeline` | Run state for Medium and Large flows |
| `<cache>/last-gate.json` | `cleanup-verify` (final stamp) | Records when the full gate chain last passed, so other skills can skip a redundant re-run |

Small-tier runs do not touch either file.

## Availability is not guaranteed

State is an optimisation, not a dependency. Every skill that reads it must work without it, and every skill that writes it must degrade cleanly:

- If the cache directory does not exist or the host denies Write, report results in chat and continue. Do not fail the skill.
- If `pipeline.json` is absent, missing a field, or fails to parse, treat that as "no prior state" and proceed from the information in the conversation.
- Never block work on a cache write.

A project that provides no writable cache location still runs the whole pipeline; it just repeats some validation.

## `pipeline.json`

```jsonc
{
  "schemaVersion": 1,

  "run": {
    "id": "pipeline-2026-07-29T13:04:49Z",   // "pipeline-<ISO-8601>", or "shape-<ISO-8601>" when shape-task runs on its own
    "task": "raw user request, verbatim",
    "startedAt": "2026-07-29T13:04:49Z",
    "updatedAt": "2026-07-29T13:40:12Z",     // every skill that writes the file sets it
    "completedAt": "2026-07-29T14:11:02Z",   // set on terminal status only
    "status": "shaping",
    "tier": "medium",                        // "small" | "medium" | "large"
    "reviewRuns": 0,                         // independent-review invocations; see cap below
    "cleanupVerify": "CLEAN"                 // verdict recorded by cleanup-verify
  },

  "designBrief":   { },                      // confirmed intake brief (requirements-generator)
  "requirements":  { },                      // shaped requirements (shape-task)
  "strategy":      { },                      // implementation strategy (shape-task)
  "repoFindings":  { },                      // repository inspection digest (Large only)
  "architectPlan": { },                      // architect plan digest (Large only)

  "chunks": [
    {
      "id": "C1",
      "objective": "one line",
      "acceptanceCriteria": ["testable statement"],
      "size": "small",                       // "small" | "medium" | "large", from shape-task
      "status": "pending",
      "filesChanged": ["path/to/file.ts"],
      "validation": { "lint": "pass", "check": "pass", "test": "pass", "at": "…" },  // null for a step not run
      "closure": { "decision": "PASS", "at": "…", "reason": "one line" }
    }
  ],

  "scratchpad": {
    "notes": ["free-text breadcrumbs; append-only"]
  },

  "lastGate": { "at": "…", "scope": "full", "success": true }  // mirror; see below
}
```

### `run.status`

| Value | Meaning | Set by |
|---|---|---|
| `shaping` | Brief and chunks being established | run-pipeline, Phase B; shape-task when run on its own |
| `ready` | Shaped and waiting for the first chunk; only when shape-task runs outside a pipeline run | shape-task |
| `executing` | Chunk loop in progress | run-pipeline, before first chunk |
| `verifying` | All chunks closed; final sweep and review still to run | run-pipeline, wrap-up; close-chunk, when it closes the last chunk of a pipeline run |
| `blocked` | Stopped on a failure or scope breach | any skill that stops the run |
| `complete` | Finished clean | run-pipeline, final phase; close-chunk, only for a run that is not a pipeline run (no final sweep follows) |
| `complete_with_findings` | Finished with unresolved review findings after the cap | run-pipeline, final phase |

### `chunks[].status`

`pending` → `executing` → `passed` (execute-chunk succeeded) → `closed` (close-chunk returned PASS or PASS_WITH_NOTES).

Other values:
- `blocked`: execute-chunk stopped before editing, for example on the scope guard.
- `failed`: execute-chunk's validation failed, or close-chunk returned FAIL.
- `split`: shape-task or close-chunk decomposed the chunk into sub-chunks, which carry on in its place.

When a chunk is `blocked` or `failed`, the run status goes to `blocked`. Do not mark a chunk `closed` without a `closure.decision`.

### Who owns the run

A run whose `run.id` starts with `pipeline-` belongs to `run-pipeline`. The skills it dispatches update their own parts (`designBrief`, `requirements`, `strategy`, `chunks[]`, `scratchpad`) but never reset `run.id`, `run.task`, `run.tier` or `run.startedAt`, and never set a terminal status: only run-pipeline ends its own run, after the final sweep and review.

### `chunks[].closure.decision`

`PASS` | `PASS_WITH_NOTES` | `FAIL`. Only `close-chunk` writes this.

## `last-gate.json`

```jsonc
{
  "at": "2026-07-29T14:10:58Z",   // ISO-8601, when the chain finished
  "scope": "full",                // "full" | "per-chunk"
  "success": true
}
```

`scope` is the load-bearing field:

- **`full`** — the project's entire gate chain ran end-to-end and passed, with no known-failing gates. Only claim this when every gate in `gates.chain` (see the project adapter) returned success.
- **`per-chunk`** — a narrower or partial validation passed. Informational. Must not be used to skip a full run.

### Freshness

A `full` stamp may be inherited instead of re-running the chain if `at` is within the project's `state.gateStampTtlSeconds` (adapter key; default **300 seconds**). Beyond that, re-validate.

Some skills use a tighter window than the TTL for their own purposes — `run-pipeline` inherits only within 240s before a Small-tier change. A skill may be stricter than the TTL; it must never be looser.

### Stamp only on first-hand evidence

Write `last-gate.json` only for a chain **you just ran and observed in this session**. Never stamp from a `validation` block you read out of `pipeline.json`, from a prior chunk's record, or from a user's assertion that tests pass. The marker exists to let other skills skip work; a stamp written from hearsay silently disables verification.

The `lastGate` key inside `pipeline.json` is a convenience mirror for reporting. `last-gate.json` is authoritative.

### The hook's stamp

`scripts/gate-chain.py` keeps a second stamp, `<config>/.gate/stamp.json`, for the Stop hook. It is keyed to the exact working tree (HEAD, status, diff and untracked files), not to a time window, so any edit invalidates it. The two answer different questions: `last-gate.json` lets skills skip a re-run within the TTL; the hook's stamp proves this exact tree passed. When `gate-chain.py` is available, `cleanup-verify` runs the chain through it with `--stamp`, so one run writes both.

## Concurrency

There is no locking. Assume a single pipeline run at a time per workspace.

On entry, `run-pipeline` reads `pipeline.json`; if `run.status` is `shaping` or `executing` and `run.task` differs from the current request, it must warn the user and ask whether to resume, discard, or append rather than overwriting silently.

## Changing this schema

Bump `schemaVersion` on any breaking field change. A skill reading a `schemaVersion` higher than it recognises should treat the state as unavailable and proceed without it rather than guessing.
