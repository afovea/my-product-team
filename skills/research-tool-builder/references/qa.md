# Checking a tool before fieldwork

Run `scripts/tool.py check` first: it covers what can be read from the file. Then run the tool in a browser, served from a local address or opened from disk, and work through this list. Use a practice session, or clear the tool's storage afterwards.

## Every tool

| Check | How | Expected |
|---|---|---|
| Codes only | Type a name, then an email, as the participant code | Both refused with a plain explanation |
| Duplicate code | Start a second session with a finished participant's code | Refused, unless it is a practice run |
| Consent | Try to continue without ticking the required boxes | Continue stays disabled; the session records the notice version, the items and the time |
| Full session | Run every task to the end | Every step appears in order; each run has timings, an outcome, ease, any confidence and notes, and events |
| Tour time | Read the first task's tour slowly | `readingMs` for task 1 leaves the tour out |
| Reload mid-task | Start a task, make one move, reload | The setup screen offers the session; resuming keeps the attempt as interrupted, counts the interruption and reruns the task as attempt 2 |
| Leaving mid-task | Close the tab during a task | The browser asks before leaving |
| End early | Ctrl+Shift+E during a session, or "End early and keep" on setup | Session kept with status ended-early |
| Practice | Run a practice session | Saved and flagged, and absent from the results figures |
| Setup | Build with the user's `--run` and `--device` | The copies the build prints match the setup; each session's `mode` matches how it was run; a mixed study asks per session |
| Hand-over | In person, remote, and participant alone on the moderator's device | Hand-over screens in person and alone; none when remote or moderator-led |
| Stop | On a participant copy, a shared link, or a remote or self-run session: Stop, then each choice | Keep: ended early with `stoppedBy`, a task in progress kept as interrupted, then the save screen. Delete: the session is gone from storage and nothing saves after. No Stop when a moderator is beside the participant |
| Code in the link | Open a participant copy with `#P3` | The code box is filled |
| Unsaved answers | Finish on a participant copy, reload before saving | The save screen comes back; after saving, a reload starts afresh |
| Two copies, one device | Run the moderator and participant copies in one browser | Neither sees the other's sessions; the participant copy ignores the moderator's content edits |
| Review | Review an imported session: change the mode, give a judgement without a reason, then with one; tick codes; add notes | Refused without a reason; saved with one; the export carries the mode, `moderator.override`, `codes` and `notes` |
| Shared link roles | Open the published link as its owner, and as a Contributor in another account | The owner gets moderator screens and every session; the Contributor only participant screens and their own sessions |
| Time away | Switch to another tab during a task and back | `focus-lost` and `focus-back` events and `awayMs` on the run |
| Task questions | A task with `questions`, one `required` | Asked after the task; Continue waits for the required one; answers in `run.answers`; written answers count in the debrief's personal-details check |
| Ease off | A task with `ease: false` and nothing else to ask | The rating step is skipped and `ease` is `null` |
| Repeated entries | A study with `repeat: { "entries": 2 }`: run the same code three times | Two sessions with `wave` 1 and 2; the third is refused |
| Save failure | Block site data in the browser and reload | The moderator sees that nothing is being saved, and participants are told plainly |
| Export | Export all, and one session | Files named `{study}_{method}_{code or all}_{date}.json`; `format` is `research-sessions` |
| Import | Import a participant file, the same file again, an edited copy, another study's file and a text file | Added; "already imported"; kept beside the original and labelled; refused; refused |
| Content edit | Change the content while a session is in progress, then after | Blocked, then saved as the next version; older sessions keep theirs |
| Keyboard only | Do a whole session without a mouse | Every task can be completed; Enter presses the main button; Esc closes dialogs and cancels confirmations |
| Screen reader | Do one task with VoiceOver or NVDA | Each new screen's heading is read; placements and saves are announced |
| Phone width | 375 px wide | No sideways scrolling; targets at least 44 px |
| Both themes | Light and dark | Text readable; the stage still stands apart from the controls |
| Reduced motion | Turn on reduced motion | Nothing animates |
| Participant copy | Build a setup on the participant's device and run its participant copy | No moderator views, no segment or practice controls; ends with "Save my answers" and a copy fallback |
| Into the report | Convert an export with research-reporter | Builds without errors (phase 3) |

## Card sort

- Drag a card, tap a card then "Place here", and use only the keyboard: all three place it.
- Finish with an unnamed group of your own: blocked. With a "Doesn't fit" card and no reason: blocked. With cards left: a two-step "Finish with 2 unsorted".
- Remove a group: its cards return to the deck.
- Esc while holding a card: the card is put back.

## Tree test

- Open sections, go back up, jump with the breadcrumb: each backtrack is counted, and only a path within the tolerance is direct.
- Choose an answer, then "Keep looking": nothing is recorded as the answer. "This is my answer" ends the task.

## Classification

- Next is disabled until the item has an answer; "None of these" also needs a note.
- "I've finished" is blocked until every item is answered.

## Stimulus

- Several stimuli appear in a seeded order, recorded in `outcome.shown`; with `shuffle: false`, in content order.
- A timed task (`exposureMs`) has no finish button, hides the material and moves on by itself; `exposedMs` is close to `exposureMs` with the window in front.
- A task whose questions have `correct` answers is scored in the report; one without is reported as not scored, with the answers tallied.

## Observation

- Moderator copy: no hand-over; consent and rating say "Moderator, with the participant" and the consent records `recordedBy`. The task screen has the clock, markers, codes and outcome levels; End task waits for a level. A topic with `levels: false` ends with Next topic. "The participant gave up" records `gave-up`.
- Participant copy: the product opens in a new tab; the task waits for "I've finished"; time away is recorded.

## First click

- The prototype loads at the task's device size and route, scaled to fit, and ends the task on the first click (unless `endOn` is `finish`).
- A click on a main target, an acceptable target and anything else gives main, acceptable and wrong.
- A message posted to the tool from outside the prototype frame, or without the session's code, is ignored.
- Test tools that click by screen position cannot click into a scaled frame. Switch the scale off for automated tests; people are unaffected.

## Tested so far

Phase 2 ran the card-sort example (`assets/examples/card-sort-study.json`) through these, by script in a browser:

- codes only, duplicate code, consent, a full moderated session with the tour, closing questions and debrief
- reload mid-task, end early, practice run left out of the figures
- export, and a participant copy saved to file and imported into a clean moderator copy, plus the same file again, an edited copy, another study's file and a text file
- content edit saved as version 2, invalid content blocked, reset to the built-in content
- card sort: tap to place, pointer drag, Esc to put a card back, the finish rules
- phone width (375 px), light theme on the board

Phase 3 added, by script and real clicks in a browser, sessions for every other method, each exported and built into a report with research-reporter:

- tree test: five participants, with direct, indirect and wrong answers and a give-up
- classification: four raters, with disagreements, unsure flags and a "None of these" with its note
- card sort: four participants across an open and a closed sort, with a "Doesn't fit" card and written closing answers
- first click: three participants on desktop and mobile, with main, acceptable and wrong first clicks and a give-up, and a ranking closing question

Also checked: a message posted to the first-click tool from the page itself, carrying the right session code, and one with a wrong code, were both ignored.

The methods catalogue work added, by script in a browser:

- stimulus: three participants through a five-second test, a preference test, a comprehension test and reaction words, with a give-up, required questions, and the debrief check covering written answers to task questions. Exported and built into a report: check questions scored, preferences and words tallied, "Not asked" where ease was off
- repeated entries: one code twice, refused the third time, entries labelled in the moderator list and reported as `P1-e1`, `P1-e2`
- every earlier method's export rebuilt into a report after the converter became generic, with the same results

Found in testing: timed exposures ran about 8 seconds instead of 5 while the browser window was in the background, because browsers slow timers there. The tool records the real time; a five-second test must be run with the tool's window in front.

The test-setup work added, by script in a browser:

- observation, mixed setup on both devices: a moderator-led session on the moderator copy (in person, consent recorded by the moderator, codes, a marker, levels, an interview topic), and participant-run sessions on the participant copy opened with `#P2`: time away recorded, Stop and keep, Stop and delete (session removed, nothing saved after), the save screen returning after a reload, and saved sessions not returning
- the moderator copy importing three participant files and reviewing one: mode changed to remote, a judgement refused without a reason and saved with one, codes and notes. Exported and built into a report with modes per participant, the setup line, levels, codes, notes and time away
- a shared link with a stand-in host that enforces the published rules: two participants each saw only their own session and no moderator screens; the owner saw both and saved a review into the participant's record. The real claude.ai rules were not exercised: check them on the published link before fieldwork
- participant alone on the moderator's device (hand-over, then Stop), and remote on the moderator's device (no hand-over)
- every earlier export, including ones with the old `moderated` mode, rebuilt into a report

Found in testing and fixed: a task that asks nothing afterwards could not move on (the step table refused it); participant and moderator copies on one device shared their sessions; written answers to task questions were missed by the debrief check. The documented `focus-lost`, `focus-back` and `resize` events had never been logged; they are now. The test browser never reports the page as focused, so `focus-back` was not seen there.

Not yet run: a keyboard-only session by hand, a screen reader, the browser's leave-page prompt, blocked storage, reduced motion, the dark theme on the board, editing content during a session, and the report conversion.
