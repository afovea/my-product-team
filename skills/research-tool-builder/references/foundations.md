# Foundations

What every research tool built with this skill has in common, whatever the method. A method module decides what the participant does on the task screen and what counts as success; everything in this file is the same in every tool, so a moderator who has run one study can run the next, a participant meets the same conventions, and every export can be read by `research-reporter`.

Each rule has a reason and a way to check it. "Must" rules are not negotiable per study; change them here, for every tool, or not at all.

## 1. Build

- **Must** be one self-contained HTML file: its own CSS and plain JavaScript inline, no framework, no build step, no network calls of its own. It opens from disk and works offline.
- **Must** start `<!doctype html>`, declare `<meta charset="utf-8">`, `lang`, and a viewport, and carry a content security policy that blocks network access except what the delivery mode needs (see section 9).
- **Must** title the page "Study name · Method", e.g. "Checkout labels · Card sort".
- **Must** route every change through one state machine: a single function that takes the current state and an action, refuses any move between steps that is not allowed, and returns the next state. The screen is drawn from that state.
- Heavy test material (a prototype, a live page) runs in its own sandboxed frame. The tool never ships a second copy of a framework for itself.

*Why:* the existing tools that rebuilt the page from shared variables lost focus on every change and could reach states no one designed; the one with a guarded state machine could not.
*Check:* the tool checker reads the file for the doctype, charset, `lang`, viewport, policy and the absence of `fetch`, `XMLHttpRequest`, `WebSocket` and external `src`.

## 2. Roles and screens

- **Must** separate moderator screens (setup, results list, study content, debrief) from participant screens (brief, task, rating, closing questions, thank-you).
- **Must** hide the tool's navigation, results and other participants' data on every participant screen.
- **Must** mark every screen with its audience in a small label ("Moderator", "Participant").
- **Must** show a handoff screen whenever the device changes hands in the same room, in both directions, with one clear action for the person now holding it. Remote sessions and moderator-led methods have no hand-over.
- A participant copy has no moderator screens at all. Moderator features (results, review, content editing, import) live in the moderator copy built from the same file. On a shared link, one page serves both, and the viewer's access decides which screens they get (section 9).
- A moderator-led method (observation) keeps the device with the moderator. Participant screens then say "Moderator, with the participant", and the moderator reads them out and enters the answers.

*Why:* participants who see results, task names or other people's answers are no longer naive.
*Check:* walk every participant screen; nothing a participant sees names a target, a score or another participant.

## 3. Session flow

Every tool follows the same steps. A method adds or repeats task steps; it never reorders these.

| Step | Audience | Purpose |
|---|---|---|
| Setup | Moderator | Participant code, segment, practice flag, device check, resume or discard unfinished sessions |
| Consent | Participant | Data notice and the consent items for this study (section 4) |
| Brief | Participant | What will happen and how long it takes, in plain words. Never the purpose of any task |
| Tour | Participant | Before the first task only: how to use the task screen. Its time is not counted |
| Task | Participant | The method's own screen. Begin is pressed before timing starts |
| Rating | Participant | Ease, confidence where the task asks for it (section 6), and the task's own questions. Skipped when the task asks nothing |
| Next | Participant | "Task n of N" and a continue action |
| Closing questions | Participant | The study's own questions after the last task |
| Thank-you | Participant | Says the session is over. Shows no results. On a participant copy, saves the answers as a file to send back, and comes back to this screen after a reload until they are saved |
| Debrief | Moderator | Moderator notes and the check of written answers for personal details |
| Review | Moderator | Any finished session, including imported ones: how it was run, a judgement that differs from the tool's (with a reason), observation codes and notes per task |

- **Must** show progress as "Task n of N" and a progress bar on every participant step after consent.
- **Must not** let participants go back to a finished task. Moderators can retake a task; the retake is recorded as a new attempt.
- **Must** let the moderator end a session early behind a two-step confirmation. The session is kept with status "ended-early".
- **Must** let anyone taking part without a moderator beside them (a participant copy, a shared link, a remote or self-run session) stop at any time with a Stop button, and choose to keep what they have done (kept as ended early, `stoppedBy: "participant"`) or delete it. Deleting removes the session from the device or the shared store; nothing is sent.

## 4. Consent and privacy

- **Must** show a data notice before the first task: what is recorded, where it is kept, who sees it, how long it is kept, and how to withdraw.
- **Must** record consent in the session: which notice version, which items were agreed, and when. When the moderator reads the notice out and ticks for the participant, the consent says so (`recordedBy: "moderator"`).
- **Must** back the notice's "you can stop at any time" with a control (section 3), not only with closing the page.
- **Must** identify participants by code only (P1, M3: letters then digits). The setup screen refuses anything that looks like a name or an email address.
- **Must** keep names out of the data, the screen and file names. If the team needs to link codes to people, that list lives outside the tool.
- **Must** record the participant's segment (for example member or non-member) as a separate field, chosen from the study's own list.
- Free-text answers can contain personal details. The moderator's debrief step reminds them to check, and `research-reporter` checks again before reporting.

*Why:* three of the four existing tools stored typed names and put them in file names.

## 5. Study content

- **Must** keep study content as data, separate from the tool's code: tasks, items, groups, closing questions, consent items, segments, scales, timings. No client wording, logos or rules in the code.
- **Must** check content when it is loaded or edited: required fields, unique ids, references that resolve (a target that exists, a category that exists), and length limits. Errors block saving; research-quality warnings (a deck that is too big, a task with no acceptable answer) do not.
- **Must** give content a version number and a hash. Every session records both, and the export carries a copy of every content version its sessions used.
- **Must** let moderators edit content only when no session is in progress, and warn that existing sessions keep the version they started with.
- **Must** include the wording of each hypothesis or group the tasks test, not just a code, so a report never has to invent it.
- Questions about a task (recall after a five-second test, why someone preferred a design, a comprehension check) are the task's `questions`, in the same kinds as closing questions. They are shared, not a method's own, so every method can ask them and the report reads them the same way. Right answers go in the content as `correct`, never in the code.
- A study where each participant takes part more than once (a diary study, repeated rounds) sets `repeat: { "entries": n }`. Each session records its `wave`; without `repeat`, a code has one session.

## 6. Order, measures and ratings

- **Must** give each participant an order (tasks, and items within a task where the method shuffles) from a seeded random generator, and record the seed and the order in the session. Fixed orders for named codes and rules such as "these two tasks never run back to back" are content, not code. So are between-participant conditions (an entry route, a design variant): the content lists them, the seed assigns them, and the session records which one each person got.
- **Must** time without showing a clock: `readingMs` from the task appearing to Begin (tour time removed), `durationMs` from Begin to the end of the task.
- **Must** ask ease after every task the participant attempts, on a 5-point scale, answered by the participant: "Overall, how easy or difficult was this task?" Very difficult (1), Difficult (2), Neither easy nor difficult (3), Easy (4), Very easy (5). A task with nothing to attempt (a timed exposure, a preference, an interview topic) sets `ease: false`, and the report says "Not asked".
- Confidence is optional per task, on a 5-point scale answered by the participant: Not at all confident (1), Slightly (2), Moderately (3), Very (4), Completely confident (5). The question wording is the study's.
- **Must** label the measure "Ease (1–5)" wherever it is shown. It is not the 7-point Single Ease Question and is not compared with its benchmarks.
- **Must** record an event log for every task (see the data format) as well as the outcome.

## 7. Saving and recovery

- **Must** save on every change, including the state of a task in progress, and read the save back to confirm it landed.
- **Must** show the moderator where data is being saved and whether the last save worked. A failed save is never silent: the moderator sees it and is offered an export there and then.
- **Must** warn before the page is closed or reloaded while a task is running.
- **Must** offer to resume or discard an unfinished session on the setup screen. A task interrupted by a reload is recorded as interrupted and retaken as a new attempt; the interruption is counted.
- **Must** keep a practice session: saved, flagged practice, and left out of every figure and every report.

## 8. Interaction conventions

| Convention | Rule |
|---|---|
| Main action | One primary button per screen. Enter presses it, except while typing in a text field |
| Back out | Esc closes the topmost dialog, menu or tour step, never a screen |
| Shortcuts | `?` opens the shortcuts list. Moderator screens only: 1–3 switch views, T switches theme. During a moderated session, Ctrl+Shift+E (Cmd+Shift+E on a Mac) lets the moderator end it early, behind a confirmation |
| Destructive actions | Two steps, inline: the button becomes "Confirm …" with a cancel beside it. Focus returns where it was |
| Moving things | Every drag has a tap-to-pick, tap-to-place alternative and a keyboard path. A "holding" bar shows what is picked up |
| Choosing | Single choice is a radio group; scales are radio groups with every point labelled |
| Ending a task | The method decides what ends a task. "I can't do this" is always available and recorded as gave-up |
| Feedback | Short status messages in a live region. No toasts that vanish before they can be read |
| Undo | Moves on the task screen can be reversed until the task is ended. After that, only a moderator retake |

## 9. Test setup, delivery and storage

The setup is the user's to define. A study may be moderated or not, in a room or remote, on the moderator's device, the participant's own or both, and reach participants as a file, a link or a hosted page. None of these is the default and none is a rule: the skill asks, then builds around the answers. Before building, it asks these as multiple-choice questions, skipping any the earlier answers settle:

1. **Who runs the sessions?** Moderated in person · Moderated remotely (on a call) · Participants on their own · A mix
2. **Whose device runs the tool?** The moderator's · The participant's own · Both (the moderator takes notes on theirs while the participant uses their own)
3. **How does the participant get it?** (when it runs on their device) A file we send · A published claude.ai link · Our own website or intranet
4. **How do results come back?** (only for a hosted page) Participants save a file and send it · A server the team supplies (asked for, not built in)

`tool.py build --run … --device … --delivery …` turns the answers into the copies to build and prints who gets which file. Every session records how it was actually run (`mode`: `in-person`, `remote` or `self-run`); in a mixed study the moderator chooses per session, and a review can correct it later.

| Setup | Copies | Storage, and how results reach the report |
|---|---|---|
| Moderator's device, in person | One moderator copy, with hand-over screens | That device; the moderator exports |
| Moderator's device, participant alone (a kiosk or lab) | One moderator copy: the moderator sets up, hands over, and the participant can stop | That device; the moderator exports |
| Moderator's device, remote (the participant controls it over a call) | One moderator copy, no hand-over | That device; the moderator exports |
| Participant's device, by file or a hosted page | A participant copy to send, and a moderator copy | The participant's device; at the end they save one file, named with their code, and send it back. The moderator copy imports, merges and reviews the files. A code can travel in the link (`#P3`) |
| Participant's device, moderated remotely | As above; the moderator watches on the call | As above. The moderator adds their judgements in a review once the file arrives |
| Both devices | Both copies. A moderator-led method logs on the moderator's copy; the participant uses their own | Both; the participant's file is imported beside the moderator's session |
| Shared claude.ai link | One page: its owner and editors get the moderator screens, everyone else the participant screens | The link's shared storage. Each person reads and writes only their own sessions; editors read and review them all. Participants must be in the organisation at Contributor level to save, so for outside participants use a file or a hosted page. Falls back to the device, with a visible note, where shared storage is unavailable |

- **Must** ask the setup questions rather than assume a setup, and say before building where data will live, who can see it and how it reaches the report.
- **Must** record the setup in every export (`study.setup`) and the mode in every session.
- A participant copy keeps its sessions apart from a moderator copy on the same device, and runs the content it was sent, never a moderator's later edits.
- A team server to receive results is asked for, never assumed. Only that address is then added to the security policy.
- Export and import of files are always available, whatever the setup.

## 10. Test material

- **Must** show test material on its own stage, visibly apart from the tool's controls, so participants know what is the product and what is the test.
- A prototype runs in a sandboxed frame at a named device size (desktop, tablet, mobile), scaled to fit. Messages between the frame and the tool carry a per-session code, and the tool ignores anything without it.
- The tool, not the prototype, decides when a task starts and ends.

## 11. Accessibility

- **Must** move focus to the new screen's heading on every step change, and back to the triggering control when a dialog or confirmation closes.
- **Must** announce placements, selections and saves in a polite live region.
- **Must** make every interaction work with a keyboard alone and with a screen reader, including the method's own task (section 8's alternatives to dragging).
- **Must** use roles only with their full keyboard pattern: a "menu" moves with arrow keys, a dialog traps focus.
- **Must** respect reduced motion, keep text contrast at 4.5:1 in both themes, and make targets at least 44 px.
- The prototype under test is outside the tool's control; say so in the study's method notes rather than claiming it is accessible.

## 12. Look and brand

- **Must** use the same design tokens and brand profile format as `research-reporter` (its `references/theming.md`), so a client's tool and its report match.
- Neutral by default. A brand profile sets the owner's name, logo, fonts and colours; the layout, conventions and measures never change with the brand.
- Light and dark themes, following the device unless the moderator chooses.

## 13. Results in the tool

- Quick figures only, on the moderator's results list (with each session's review): sessions so far (practice excluded), completion per task, median time per task, and a sample-size note under five participants.
- Everything else (agreement statistics, co-occurrence, scorecards, findings) belongs to `research-reporter`, which reads the export.

## 14. Words

- Plain, neutral, and the same across tools: "Begin", "I've finished", "I can't do this", "Continue", "Task 2 of 6".
- Participant copy never hints at the answer, never praises or corrects, and never uses the names of the things being tested in instructions about how to use the tool.

## What a method module adds

A method module (see `methods/`) supplies only:

1. its content format and the checks for it
2. the task screen and its interactions, inside section 8's conventions
3. what ends a task and how its outcome is scored automatically (`success`, and `friction` where it can tell)
4. its own event types and outcome fields (see the data format)
5. the quick figures it adds to the results list, if any

It may not change the session flow, the ratings, the task questions, saving, consent, privacy, delivery, the export envelope or the look. The research methods catalogue ([methods-catalogue.md](methods-catalogue.md)) lists which methods need a module and which need only content.
