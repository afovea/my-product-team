# Research methods catalogue

Every research method a product team is likely to run, set against what this skill builds. Drawn up with `ux-researcher`. Use it to answer three questions before building: can the shared base run this method, which module does it need, and what does its data look like when it reaches the report?

No method is out of scope because no module exists for it yet. Every method also runs in whichever test setup the user chooses (moderated or not, in a room or remote, on whose device; foundations, section 9): the shell handles the setup, so no method is tied to one. A method falls into one of four states:

| State | Meaning | What to do |
|---|---|---|
| **Built** | A module exists | Write the content and build |
| **Content** | An existing module runs it, through content alone | Write the content from the pattern below and build |
| **New module** | The shared base and format already hold its data; only the task screen is missing | Write the module on the contract (SKILL.md, "New method module"), using the outline below |
| **Partly** | A browser tool can capture part of it; the rest needs other equipment or analysis | Build the part the tool can capture, and say plainly what it does not do |

## How any method fits the format

A method never needs a new export format. Everything a method records lands in one of these places, all set out in [data-format.md](data-format.md):

| What the method produces | Where it goes |
|---|---|
| What the participant did on the task screen | The run's `outcome` (method fields) and `events` (method event types) |
| Whether they succeeded | `outcome.success`: `true`, `false`, or `null` when a person must judge it |
| How much friction, when the method can tell | `outcome.friction`: `none`, `minor` or `major` |
| Answers to questions about the task (recall, preference, comprehension, a questionnaire) | `run.answers`, from the task's `questions` in the content, in the same shapes as closing questions |
| Right answers to those questions | `correct` on the question, in the content; the report scores against it |
| Which design or variant the run showed | `run.variant`, from the task's `variant` or set by the module |
| Which condition a participant was assigned (between-participant) | `plan.conditions` |
| The order things were shown in | `plan.order`, `plan.itemOrder`, or the module's own outcome field |
| More than one session per participant (diary, rounds) | `session.wave`, when the content sets `repeat` |
| Observations, codes and judgements by the moderator | `moderator.codes`, `moderator.notes`, `moderator.override`, `debrief.notes` |
| Answers at the end of the session | `closing` |

The report converter reads any method: the four with their own findings, and every other method through generic findings built from the fields above. So a new module produces a report on the day it is written, and earns method-specific findings only if the team needs them.

## Sort and organise

Testing how people group and label things: information architecture.

| Method | State | What the participant does | Success per person | Main measures |
|---|---|---|---|---|
| Open card sort | Built (`card-sort`, mode `open`) | Groups cards and names the groups | No | Which cards end up together, group names |
| Closed card sort | Built (`card-sort`, mode `closed`) | Sorts cards into given groups | No | Agreement per card |
| Hybrid card sort | Built (`card-sort`, mode `hybrid`) | Sorts into given groups and may add their own | No | Agreement, new groups |
| Classification | Built (`classification`) | Puts items into defined categories one at a time | No | Agreement between raters, unsure flags |
| Tree test | Built (`tree-test`) | Finds where something lives in a text-only menu | Yes | Success, directness, path |
| Reverse card sort | Content (`tree-test`) | Same as a tree test with the categories as the tree | Yes | As a tree test |
| Similarity rating | New module | Rates how alike pairs of items are | No | Pair scores. Outcome: `pairs: [{ a, b, value }]` |

## Find it on a design

Testing whether people can find their way on a design.

| Method | State | What the participant does | Success per person | Main measures |
|---|---|---|---|---|
| First-click test | Built (`first-click`) | Clicks where they would go first on a prototype | Yes | First click by tier, time to first click |
| Click test on a screenshot | Content (`first-click`) | The same, on a prototype page that is one image with `data-zone` regions | Yes | As first click |
| Navigation task on a prototype | Content (`first-click`, `endOn: finish`) | Keeps clicking until they think they are done | Yes, by where they end | End route (`endHref`), clicks, route events. The module scores the first click; whether the end route is right is a moderator override or analysis, until the module scores end routes |
| Task on a live website or native app | Built (`observation`) | Uses the real product: watched by a moderator who logs it, or on their own, coming back to the tool when done | Moderator judges, or a check question | Outcome level, observed codes, markers; or time and time away, self-report and check answers. The tool cannot see inside another site or app |

## Look and react

Showing material and asking about it.

| Method | State | What the participant does | Success per person | Main measures |
|---|---|---|---|---|
| Five-second test | Content (`stimulus`, `exposureMs: 5000`) | Sees a design briefly, then answers recall questions | Optional, via `correct` | Recall answers, real exposure time |
| Preference test (A/B or more) | Content (`stimulus`, several stimuli) | Compares options shown side by side in a shuffled order, chooses one, says why | No | Choice split, reasons, order shown |
| Desirability (reaction words) | Content (`stimulus`, a `choices` question) | Picks the words that describe a design | No | Word counts |
| Concept test | Content (`stimulus`, scale and text questions) | Reads or sees a concept and rates appeal, clarity and likelihood to use | No | Ratings, comments |
| Comprehension test | Content (`stimulus`, questions with `correct`) | Reads content, then answers questions about it | Yes, all check questions right | Correct answers per question |
| Highlighter test | New module (`highlight`) | Marks phrases in a passage as clear or confusing | No | Marks per phrase. Outcome: `marks: [{ start, end, kind }]` |

## Answer questions

Questionnaires, on their own or around tasks.

| Method | State | What the participant does | Success per person | Main measures |
|---|---|---|---|---|
| Survey or questionnaire | Content (`stimulus` with text stimuli and `ease: false`, or closing questions) | Answers questions | No | Answers |
| Standard questionnaires: SUS, UMUX-Lite, NPS, CSAT, NASA-TLX | Content (scale questions with the instrument's exact wording and labels) | Rates statements | No | The instrument's score. Use the published wording unchanged and tag each item with `instrument` (`"sus"`). The report tallies each item; working out the instrument's score is analysis, not yet done by the converter, and never by the tool |
| Top-tasks or priority ranking | Content (a `rank` question) | Puts items in order | No | Average rank, times ranked first |
| Kano | Content (pairs of `choice` questions per feature) | Says how they would feel with and without a feature | No | Kano category per feature, from the pair. Give both questions the same `feature`; categorising is analysis, outside the converter |
| MaxDiff (best–worst) | New module (`maxdiff`) | Picks the best and worst from repeated sets | No | Best and worst counts. Sets come from the seed and go in `plan.itemOrder` |
| Conjoint | Partly (`maxdiff`-like module for the choice sets) | Chooses between bundles of features | No | Choices. Utility estimation needs specialist analysis outside the tool |
| Screener | Outside this skill | Answers eligibility questions before a study | – | Recruitment, not research data; keep it out of the study's sessions |

## Talk and observe

Moderated sessions where the moderator records what happens.

| Method | State | What the participant does | Success per person | Main measures |
|---|---|---|---|---|
| Moderated usability test (think-aloud) | Built: any method above, or `observation` when the product is outside the tool | Does tasks and talks aloud | Yes, judged by the tool or the moderator | As the method, plus moderator codes and notes, in the task or in a review |
| Interview | Content (`observation`, tasks as topics with `levels: false` and `ease: false`) | Talks through topics with the moderator | No | Moderator notes and codes per topic, markers. Recording stays in the call software |
| Contextual inquiry or field visit | Content (`observation`) | Works as normal while observed | No | Observations per activity |
| Accessibility session with assistive-technology users | Any method, moderated | Uses their own setup | As the method | Record the setup as a closing question, never a name. Hand the plan to `accessibility-specialist` |
| Expert review or heuristic evaluation | Content (`observation`, the evaluator as participant, heuristics as tasks) | An evaluator rates the design against heuristics | No | Issues by heuristic and severity. Not user research; label it so in the report |
| Focus group | Partly | Several people discuss together | No | One session per group, moderator notes only. The format records one participant per session, so individual answers are not recorded |

### The `observation` module

Built, and runs whichever way the setup asks: moderator-logged on a moderator copy (the device stays with the moderator), participant-run on a participant copy or a shared link (the participant opens the product, does the task and comes back). See [methods/observation.md](methods/observation.md).

## Over time

| Method | State | What the participant does | Success per person | Main measures |
|---|---|---|---|---|
| Diary study | Content (any module, `repeat: { entries: n }`) | Makes an entry each day or after each event | Varies | Each entry is a session with `wave`; the report shows entries as `P3-e1`, `P3-e2` |
| Longitudinal or benchmark rounds | Content (`repeat`, or one study per round with the same task ids) | Repeats the same tasks months apart | As the method | Compare rounds in the report: same tasks, different content versions or study ids |
| Experience sampling (prompted at random times) | Partly | Answers when prompted | No | The tool cannot send prompts by itself. Send links from a scheduler; each answer is an entry |

## Compare designs

| Method | State | How | Main measures |
|---|---|---|---|
| Within-participant comparison | Content (any module) | One task per design, each with `variant`, in a shuffled or counterbalanced order (`shuffleTasks`, `fixedOrders`) | Per variant: success, ease, time. The report splits a task's runs by variant when they differ |
| Between-participant comparison | Content (any module, `conditions`) | Each participant is assigned one design by the seed | The condition is shown for each participant in the report |
| Live A/B experiment on the product | Outside this skill | Analytics and an experiment platform | Hand to `data-analyst` |

## What a browser tool cannot do

Say so in the study plan rather than building a weak version.

| Need | Why not | Instead |
| Seeing a moderator's and a participant's devices live together | Needs shared storage on both and a live connection | Each device records its own session; the moderator imports the participant's file and adds their judgements in a review |
|---|---|---|
| Eye tracking, biometrics | Needs hardware; webcam estimates are too inaccurate to report | A lab or a specialist service |
| Storing audio, video or screen recordings | Large, highly identifying files on a participant's device | Record in the call or recording software. Use `marker` events and timestamps to line notes up with the recording |
| Seeing inside a live website or native app | Browsers stop one site reading another | The `observation` module: the moderator records what happens, or the participant comes back and answers a check question |
| Sending prompts at random times | A page cannot wake itself | A scheduler or messaging tool sends the link |
| Statistical modelling (conjoint utilities, SUS benchmarks, significance tests) | Analysis, not data capture | The report, `data-analyst`, or a specialist package |
| Panel recruitment and payment | Needs the panel's own systems | Panels link to a hosted or shared-link tool. Never put names or emails in the link |

## Adding a method

1. Find it in this catalogue. If it is **Content**, stop: write the content.
2. If it is **New module**, write the module on the contract, using the outline here. Its outcome must carry `success` (or `null`), and `friction` if the method can tell.
3. Write its specification in `methods/<id>.md`, with an example study.
4. Build an example, run sessions, export, and build the report. The generic findings will appear without any change to the converter.
5. Add method-specific findings to research-reporter's `research_sessions.py` only when the generic ones are not enough to act on.
6. Add the method here and move it to **Built**.
