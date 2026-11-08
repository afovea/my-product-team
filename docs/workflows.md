# Workflows

How to chain the 33 skills into complete pieces of product work.

**Version 1.0.1** · 8 November 2026 · for product-team skills 1.10.0. Each workflow carries its own version; see [Maintenance](#maintenance) for when they change.

The skills are deliberately narrow. Each one names who it takes work from and hands work to, in its "Works with" section, but a pair of handoffs is not a plan. This guide supplies the sequencing: which skill runs when, what it should leave behind for the next one, where a person has to decide, and when to go back.

Read it alongside two other documents:
- [what-can-my-product-team-do.md](../what-can-my-product-team-do.md) is the catalogue of jobs.
- [capability-map.md](./capability-map.md) places those jobs on the product cycle.

This guide is the recipe for each job. **[Product Team Workflows](https://claude.ai/artifact/KMSuAh18cm7HfATKLSyt1D)** is the same content as an interactive page, with a clickable map of the cycle and a skill finder. Not sure which workflow fits? `/product-team:route` (or `$route` in Codex) picks one from a plain description of the problem and starts its first step.

## Contents

- [How every workflow runs](#how-every-workflow-runs)
- [The workflows at a glance](#the-workflows-at-a-glance)
- [The spine: from idea to outcome](#the-spine-from-idea-to-outcome)
  - [W1 · Frame the problem](#w1--frame-the-problem)
  - [W2 · Test with users](#w2--test-with-users)
  - [W3 · Define the bet](#w3--define-the-bet)
  - [W4 · Develop the solution](#w4--develop-the-solution)
  - [W5 · Decide and make ready](#w5--decide-and-make-ready)
  - [W6 · Build a ticket](#w6--build-a-ticket)
  - [W7 · Release](#w7--release)
  - [W8 · Launch and learn](#w8--launch-and-learn)
- [Recurring workflows](#recurring-workflows)
  - [W9 · Investigate a product question](#w9--investigate-a-product-question)
  - [W10 · Fix a bug or incident](#w10--fix-a-bug-or-incident)
  - [W11 · Product health check](#w11--product-health-check)
  - [W12 · Red-team a bet](#w12--red-team-a-bet)
  - [W13 · Price and package](#w13--price-and-package)
  - [W14 · Stand up or audit a design system](#w14--stand-up-or-audit-a-design-system)
  - [W15 · Adopt a library or component](#w15--adopt-a-library-or-component)
  - [W16 · Tell stakeholders what happened](#w16--tell-stakeholders-what-happened)
  - [W17 · Start or join a project](#w17--start-or-join-a-project)
- [Composite: run as a fractional product department](#composite-run-as-a-fractional-product-department)
- [Getting the most from each skill](#getting-the-most-from-each-skill)
- [Who owns what when skills overlap](#who-owns-what-when-skills-overlap)
- [Built into the skills](#built-into-the-skills)
- [Outside the suite](#outside-the-suite)
- [Maintenance](#maintenance)

## How every workflow runs

Six rules apply to every workflow below.

1. **Start with what the project already knows.** Run `ppot brief`, or `ppot init` if the project has no `PPoT.md` yet. In Claude Code with the plugin that's `/product-team:ppot brief`; skills are written here by name, and run as `/product-team:<name>` in Claude Code or `$<name>` in Codex. Every later step reads it. Nobody should re-argue a confirmed decision.
2. **Settle the model and sub-agents once.** Every skill checks the model against its usual tier, and asks before starting sub-agents. In a workflow, do it once, at the start. Steps marked **⇉** can run in parallel, but only with your approval and within the cap you set. Without approval they run one after another in the conversation. The result is the same; it is just slower.
3. **Hand over files, not memories.** The next skill only gets what was written down. Every skill offers to save its output as a file in the project, for example `product/<work-item>/03-evidence.md` (its "Handing over work" section). Say yes whenever a later step needs it, and point the next skill at the file. The build pipeline, the research skills and `ppot` keep their own files in their own places.
4. **A person decides at every gate.** The skills recommend; they do not approve. Each gate names the evidence the decision needs. Sending work back through a gate is a normal outcome, not a failure.
5. **Offer knowledge back at the end, not along the way.** Close every workflow with the PPoT proposals its skills raised, and have the owner approve them in one go. `ppot` holds durable knowledge. It is not a backlog, a meeting log or a changelog, so the working files from rule 3 stay where they are.
6. **Keep the builder, the verifier and the approver apart.** The skill that made something is never the one that signs it off: `execute-chunk` builds, `close-chunk` verifies, `design-critique` approves the design, and a person approves the release.

Each step names the skill, the intent to ask it for, and its usual model tier. **most-capable** is Opus-class, **balanced** is Sonnet-class and **fast** is Haiku-class. Move up a tier when a step carries more risk than usual.

## The workflows at a glance

| | Workflow | Version | Phase | Starts from | Ends with |
|---|---|---|---|---|---|
| W1 | Frame the problem | 1.0.0 | Discover | "Is this worth pursuing?" | Evidence summary and the riskiest assumptions |
| W2 | Test with users | 1.0.0 | Any | An assumption only users can settle | A report and its interpretation |
| W3 | Define the bet | 1.0.0 | Define | A problem with evidence | **Gate 1: Problem agreed** |
| W4 | Develop the solution | 1.0.0 | Develop | An agreed problem | Two or three tested options |
| W5 | Decide and make ready | 1.0.0 | Decide | Options | **Gate 2: Approach agreed**, tickets that meet Ready |
| W6 | Build a ticket | 1.0.0 | Build | A ready ticket | Verified, gated code |
| W7 | Release | 1.0.0 | Build → Deliver | Built work | **Release decision** |
| W8 | Launch and learn | 1.0.0 | Deliver and learn | A release | **Gate 3: Outcome evidenced** |
| W9 | Investigate a product question | 1.0.0 | Discover, Deliver | "Why did this move?" | Probable causes with confidence |
| W10 | Fix a bug or incident | 1.0.0 | Build | A fault | A verified fix and the lesson recorded |
| W11 | Product health check | 1.0.0 | Discover, Deliver | An existing product | A prioritised list for the next Discover |
| W12 | Red-team a bet | 1.0.0 | Define, Decide | A bet or a committed design | What survived |
| W13 | Price and package | 1.0.0 | Develop | A commercial question | A model, tiers and a pricing experiment |
| W14 | Stand up or audit a design system | 1.0.0 | Develop, Build | An interface, or drift | Tokens, components and governance |
| W15 | Adopt a library or component | 1.0.0 | Develop, Build | "Should we use this?" | An admission verdict with an owner |
| W16 | Tell stakeholders what happened | 1.0.0 | Any | Results to share | A report, a chart or a status update |
| W17 | Start or join a project | 1.0.0 | Any | A new project or contributor | A briefed team and a working PPoT |

## The spine: from idea to outcome

W1 to W8 run in order and take a product idea all the way to evidence that it worked. Each workflow can also run on its own, starting from whatever an earlier one would have left behind.

```
W17 Start ─► W1 Frame ─► W3 Define ─► Gate 1 ─► W4 Develop ─► W5 Decide ─► Gate 2
                ▲  │         ▲                     │                          │
                │  └─► W2 Test with users ◄────────┘                          ▼
                │                                         W6 Build (per ticket, many)
                │                                                             │
                └──── W11 Health check ◄── Gate 3 ◄── W8 Launch ◄── W7 Release decision
```

### W1 · Frame the problem

**Version:** 1.0.0

**Phase:** Discover · **Entry:** "Is this worth pursuing?" or a raw idea · **Feeds:** W2, W3

| # | Skill (tier) | Ask it for | Leaves behind |
|---|---|---|---|
| 1 | `ppot` (balanced) | `brief` | What is already known, decided and assumed |
| 2 | `product-manager` (balanced) | Problem framing | Problem statement, affected users, assumptions, outcome, next decision |
| 3 ⇉ | `ux-researcher` (balanced) | Evidence review | Sources, strength, contradictions, gaps |
| 3 ⇉ | `data-analyst` (balanced) | Funnel analysis or metric definition | Baseline, drop-off, instrumentation needed |
| 3 ⇉ | `customer-success` (balanced) | Feedback synthesis | Themes with frequency, product versus operational causes |
| 3 ⇉ | `product-strategist` (most-capable) | Opportunity framing | Segment, value, evidence, risks, what not to pursue |
| 4 | `storm-researcher` (most-capable) | Contradiction analysis, or a blind-spot review | Contradiction map, alternatives nobody raised. Use it when the evidence disagrees or one story dominates |
| 5 | `product-manager` (balanced) | Prioritisation of the assumptions | Evidence summary, riskiest assumptions ranked, and a recommendation: pursue, investigate further, pivot or stop |

**Goes back** to step 3 when step 5 finds a gap only one lens can fill.
**Next:** W2 for any riskiest assumption that only users can settle; otherwise W3.
**PPoT:** facts, assumptions and risks.

### W2 · Test with users

**Version:** 1.0.0

**Phase:** any. In Discover it tests a problem, in Develop it compares options, and in Deliver and learn it checks what shipped.
**Entry:** an assumption, or a set of options, that only people can settle.
**Feeds:** whichever workflow sent it.

| # | Skill (tier) | Ask it for | Leaves behind |
|---|---|---|---|
| 1 | `ux-researcher` (balanced) | Research planning | The decision to inform, hypotheses, and a method chosen from research-tool-builder's [methods catalogue](../skills/research-tool-builder/references/methods-catalogue.md), participants and an analysis plan |
| 2 | `ux-researcher` (balanced) | Usability testing, or an interview guide | Tasks, success criteria, a severity scale, an observation guide |
| 3 | `content-designer` (balanced) | Content critique of the tasks and consent wording | Neutral wording that never names the target |
| 4 | `security-specialist` (most-capable) | Privacy review | Where participant data may live and for how long. Needed when answers leave the device or the data is sensitive |
| 5 | `research-tool-builder` (most-capable) | New research tool | The method, the test setup (who runs it, whose device, how it is delivered), the copies that setup needs, a practice session, and proof that its export builds a report |
| 6 | — | Fieldwork | People run the sessions. No skill does this |
| 7 | `research-reporter` (balanced) | Report from data | A checked, self-contained HTML report with every finding traced to participants |
| 8 | `ux-researcher` (balanced) | Synthesis | Insights with confidence, separating what was seen from what it means |
| 9 | `product-manager` (balanced) | Prioritisation, or tickets | Findings turned into backlog items |

**Options:**
- To brand the tool and report for a client, add `design-systems-specialist` (token design) before step 5.
- When the prototype or the participants need more than the tool's accessibility baseline, add `accessibility-specialist`.

**Shortcut:** when results already exist, from another tool or a spreadsheet, start at step 7.
**PPoT:** assumptions validated or invalidated, and what was learnt.

### W3 · Define the bet

**Version:** 1.0.0

**Phase:** Define · **Entry:** a problem with evidence (W1) · **Closes:** **Gate 1: Problem agreed**

| # | Skill (tier) | Ask it for | Leaves behind |
|---|---|---|---|
| 1 | `product-strategist` (most-capable) | Strategic bet assessment | Rationale, upside, downside, capabilities needed, sequencing, and what not to do |
| 2 | `pricing-strategist` (most-capable) | Pricing model. Only when the commercial model is in question | The value metric and the behaviour the price should drive |
| 3 | `product-manager` (balanced) | PRD | Problem, users, scope and an MVP boundary, success criteria |
| 4 | `data-analyst` (balanced) | Metric definition | North star, supporting and guardrail metrics, event definitions |
| 5 | `technical-architect` (most-capable) and `software-engineer` (balanced) | Feasibility: system design at a coarse level, and a feasibility review | Whether it can be built, where it would live, the unknowns |
| 6 | W12 | Red-team the bet. Optional, but worth it for anything large | What survived |

**Gate 1, Problem agreed.** The product owner decides, with these in hand:
- the problem statement and evidence summary
- the riskiest assumptions and how each will be handled
- the success measures
- what is out of scope

They can agree it, send it back to W1 or W2, or stop it.
**PPoT:** decisions, constraints, outcomes, metric definitions and assumptions.

### W4 · Develop the solution

**Version:** 1.0.0

**Phase:** Develop · **Entry:** an agreed problem · **Feeds:** W5

| # | Skill (tier) | Ask it for | Leaves behind |
|---|---|---|---|
| 1 | `product-designer` (balanced) | Flows and interaction design, then prototype strategy | Flows with every state (empty, loading, success, error, permissions); what the prototype must make realistic |
| 2 | `content-designer` (balanced) | UI copy, error messages, empty states, onboarding | The words, with rationale and alternatives |
| 3 | `design-systems-specialist` (balanced) | Pattern governance, component specification | For each pattern: reuse, adapt or create; specs for anything new |
| 4 | `motion-designer` (balanced) | Motion design. Only where the interface changes state in a way people need to follow | State-transition specs, including reduced motion |
| 5 | `accessibility-specialist` (balanced) | Accessibility audit of the design | Issues, the people affected, fixes and pass criteria, while they are still cheap to fix |
| 6 | `technical-architect` (most-capable) | System design, with alternatives | Options for the build, with trade-offs |
| 7 | `software-engineer` (balanced) | Implementation planning, as a spike on the hardest real case | What actually breaks, before anyone commits |
| 8 | W2 | Compare options with a preference, first-click or tree test | Which option works, with evidence |

**Goes back** from step 8 to step 1 when no option survives.
**PPoT:** almost nothing. Options are not yet knowledge.

### W5 · Decide and make ready

**Version:** 1.0.0

**Phase:** Decide · **Entry:** options with evidence · **Closes:** **Gate 2: Approach agreed**

| # | Skill (tier) | Ask it for | Leaves behind |
|---|---|---|---|
| 1 | `storm-researcher` (most-capable), or W12 | Adversarial review of the chosen design | The weak points of the design you are about to commit to |
| 2 | `technical-architect` (most-capable) | ADR, and a dependency evaluation for anything that becomes a standing dependency | The decision, the options turned down, consequences, owner and review date |
| 3 | `security-specialist` (most-capable) | Threat model, or a secure design review. Needed when the change touches auth, data access, payments, AI or external integrations | STRIDE findings, mitigations and regression guards |
| 4 | `product-manager` (balanced) | Tickets in the [standard structure](../routing.md#standard-ticket-structure) | Tickets with testable acceptance criteria |
| 5 | `qa-engineer` (balanced) | Acceptance-criteria review, then test planning | Criteria rewritten until they can be tested, and a test plan |
| 6 | `delivery-manager` (balanced) | Delivery planning, then sprint readiness | Milestones, dependencies, owners, and a check against the [Definition of Ready](../routing.md#definition-of-ready-for-development) |

**Gate 2, Approach agreed.** The product owner and the technical lead decide, with these in hand:
- the ADR
- the threat model, where one was needed
- tickets that meet Ready
- the test plan
- the delivery plan

**PPoT:** the most of any phase. Decisions, constraints, risks and disagreements.

### W6 · Build a ticket

**Version:** 1.0.0

**Phase:** Build · **Entry:** a ticket that meets Ready · **Repeats:** once per ticket

| # | Skill (tier) | Ask it for | Leaves behind |
|---|---|---|---|
| 1 | `run-pipeline` (most-capable) | The ticket | A pipeline plan: the tier, the flow, the model, and sub-agents with your cap. Wait for `go` |
| 2 | `requirements-generator` (fast) → `shape-task` (balanced) | Run by the pipeline in Medium and Large | A confirmed brief; requirements, strategy and chunks in `pipeline.json` |
| 3 | `execute-chunk` (balanced) ↔ `close-chunk` (balanced) | Run by the pipeline, chunk by chunk | Each chunk built, then verified independently: PASS, PASS WITH NOTES or FAIL |
| 4 | `cleanup-verify` (fast) | Run by the pipeline at the end | The full gate sweep and drift check: CLEAN, CLEAN-WITH-NOTES, REGRESSION or BLOCKED |
| 5 | `software-engineer` (balanced) | Code review. Only when the project declares no independent reviewer | Severity-ranked issues and gaps in the tests |

`run-pipeline` offers these role skills at four points, which it calls its seams, and lists the ones that apply in its plan. You can turn the offers off with `-seams`:

| When | Bring in | Why |
|---|---|---|
| A chunk FAILs and the cause is not obvious | `diagnose` (most-capable) | It records the cause in the pipeline's notes, so the next `execute-chunk` fixes the cause rather than the symptom |
| A chunk with a UI closes | `design-critique` (balanced), compact | It catches design drift chunk by chunk rather than at release |
| A chunk touches a risky path (auth, billing, schema, infrastructure) | `security-specialist` (most-capable), security audit of the diff | The pipeline already raises the tier for these paths; this gives them the review they need |
| The scope guard stops the run | `product-manager` (balanced) | The decision is about scope, not code. Then back to the pipeline's plan |

**PPoT:** almost nothing, with one exception: when something broke, record why.

### W7 · Release

**Version:** 1.0.0

`run-pipeline` ends a clean run by naming the steps of this workflow that apply to the change. It does not deploy.

**Phase:** Build → Deliver and learn · **Entry:** built and gated work · **Closes:** **Release decision**

| # | Skill (tier) | Ask it for | Leaves behind |
|---|---|---|---|
| 1 | `qa-engineer` (balanced) | Release readiness | What was tested, unresolved issues, risk, recommendation |
| 2 | `design-critique` (balanced) | A full review of what was built | SHIP, SHIP_WITH_NOTES or HOLD |
| 3 | `accessibility-specialist` (balanced) | Accessibility audit of the build | Issues found in the real thing, not the design |
| 4 | `security-specialist` (most-capable) | Security audit, or an RLS review. Only when the change touched trust boundaries | Findings from Critical to Low, with file and line, and regression guards |
| 5 | `brand-guardian` (balanced) | Brand review, or a claims review. When the release is public, makes claims or carries partner material | Ready, Ready with changes, or Hold for owner review |
| 6 | `devops-engineer` (balanced) | Deployment planning, observability, runbook | Pre-flight checks, a rollback plan, alerts, and what to do when it breaks |
| 7 | `delivery-manager` (balanced) | Status reporting | Progress, risks and the decisions needed, in one place |

Steps 2 to 5 are independent of each other **⇉**.

**Release decision.** The release owner decides from one table of the verdicts from steps 1 to 6:
- Any HOLD, or Hold for owner review, blocks the release.
- The owner can accept it anyway, in writing, giving the reason.
- A release with no rollback plan is not ready.

### W8 · Launch and learn

**Version:** 1.0.0

**Phase:** Deliver and learn · **Entry:** a release · **Closes:** **Gate 3: Outcome evidenced**

| # | Skill (tier) | Ask it for | Leaves behind |
|---|---|---|---|
| 1 | `data-analyst` (balanced) | Dashboard planning, before launch | The dashboard that will answer "did it work?", with its events instrumented |
| 2 | `growth-product-marketing-manager` (balanced) | Launch planning, messaging | Positioning, channels, sequence, metrics with guardrails |
| 3 | `brand-guardian` (balanced) | Claims review | Every claim checked against its evidence |
| 4 | `content-designer` (balanced) | Onboarding | The in-product messages that carry the launch |
| 5 | `motion-graphics-designer` (balanced) | Product walkthrough, or an animated explainer | An MP4 built from your own screenshots and words, with a text summary to post alongside |
| 6 | `customer-success` (balanced) | Adoption risk, customer brief | Blockers by journey stage, interventions, success signals |
| 7 | `data-analyst` (balanced) | Experiment analysis or a metric readout, after launch | What changed, with confidence and caveats |
| 8 | `product-manager` (balanced) | Outcome review against the success criteria from W3 | Did it work, and the next decision |

**Gate 3, Outcome evidenced.** The product owner decides, with the readout against the W3 success criteria in hand: keep, iterate, roll back or retire.
**Next:** W11, which feeds the next W1.
**PPoT:** a lot, and it closes the loop. Facts, decisions and retirements.

## Recurring workflows

These run whenever they are needed, on their own or inside the spine.

### W9 · Investigate a product question

**Version:** 1.0.0

**Entry:** "Why has activation fallen?" or any metric that moved · **Phase:** Discover, or Deliver and learn

1. **`data-analyst`: data quality review, then funnel analysis.** Rule out a broken metric before explaining a real one.
2. **⇉ Look for causes in parallel:**
   - `customer-success`: feedback synthesis.
   - `ux-researcher`: evidence review.
   - `product-designer`: flows review of the affected journey.
   - `content-designer`: content critique.
   - `accessibility-specialist`: audit of the changed screens.
   - `software-engineer` and `devops-engineer`: recent releases and failures.
3. **`storm-researcher`: contradiction analysis**, when the explanations disagree.
4. **`product-manager`: synthesis.** Probable causes with supporting and contradicting evidence, confidence, unknowns, the next investigations and candidate interventions.

**Next:** W10 if the cause is a fault, W2 if only users can confirm it, W3 if it changes the bet.

### W10 · Fix a bug or incident

**Version:** 1.0.0

**Entry:** a bug report, failing test, incident or regression · **Phase:** Build

1. **`devops-engineer`: runbook**, during a live incident only. Stop the bleeding first.
2. **`diagnose` (most-capable)**: reproduce, isolate, hypothesise, verify. It recommends the smallest fix that stops the damage, and a proper fix separately.
3. **`run-pipeline`** with the diagnosis. It is usually Small or Medium; risky paths raise it. `execute-chunk` reads the diagnosis from the pipeline's notes.
4. **`qa-engineer`: regression.** A test that fails without the fix, kept in CI.
5. **`ppot`: `learn`.** The underlying cause is the one thing from Build worth recording.

### W11 · Product health check

**Version:** 1.0.0

**Entry:** "What's wrong with this product, what matters most, and what should we do about it?" · **Phase:** Discover, or Deliver and learn

Five panels look at the product at the same time **⇉**. With sub-agents capped at five, that is one panel each; with a lower cap, run the panels in turn.

| Panel | Skills |
|---|---|
| Strategy and money | `product-strategist`, `pricing-strategist`, `growth-product-marketing-manager` |
| Customers and evidence | `ux-researcher`, `customer-success`, `data-analyst` |
| Experience | `product-designer`, `content-designer`, `accessibility-specialist`, `design-systems-specialist`, `motion-designer` |
| Engineering | `technical-architect`, `software-engineer`, `devops-engineer`, `qa-engineer` |
| Trust | `security-specialist`, `brand-guardian` |

Then **`product-manager`** turns the findings into a prioritised roadmap. Its chain is: critical problems → evidence → opportunities → interventions.

**Next:** W1 for each priority. `ppot review` for anything the check found stale.

### W12 · Red-team a bet

**Version:** 1.0.0

**Entry:** a bet before investment (Define), or a design before commitment (Decide)

1. **`storm-researcher`: adversarial review.** It attacks the reasoning itself, through its five lenses and nine kinds of contradiction.
2. **⇉ Each discipline attacks its own assumption:**
   - `ux-researcher`: the evidence.
   - `product-strategist`: differentiation.
   - `data-analyst`: scale and measurement.
   - `technical-architect`: feasibility.
   - `security-specialist`: risk.
   - `product-designer`: usability.
   - `accessibility-specialist`: exclusion.
   - `growth-product-marketing-manager`: acquisition.
   - `pricing-strategist`: monetisation.
   - `customer-success`: adoption and retention.
3. **`product-manager`: "what survived?"** What still stands, what fell, and what would have to be true.

### W13 · Price and package

**Version:** 1.0.0

**Entry:** a commercial question · **Phase:** Develop

1. **`pricing-strategist`: pricing model.** It names the value metric.
2. **`data-analyst`: usage segments and churn signals**, and **`customer-success`: retention risk.** Together they show who pays for what today.
3. **W2**, if there is no willingness-to-pay evidence: a questionnaire or comprehension test, run by `ux-researcher` and `research-tool-builder`.
4. **`pricing-strategist`: tier design and packaging.**
5. **`pricing-strategist` or `growth-product-marketing-manager`: pricing experiment**, with a guardrail metric.
6. **`brand-guardian`: claims review** of the pricing page.
7. **`product-manager`: the decision.**

### W14 · Stand up or audit a design system

**Version:** 1.0.0

**Entry:** a new interface, or drift between products · **Phase:** Develop, then Build

1. **`design-systems-specialist`: design system audit.** Inconsistencies, and patterns that should become components.
2. **`design-systems-specialist`: token design**, from primitive to semantic, component and theme.
3. **`design-systems-specialist`: UI foundation selection.** Headless, styled, copy-in or custom elements, with who owns what. Hand any new standing dependency to W15.
4. **`design-systems-specialist`: component specifications**, with **`accessibility-specialist`** on each, and **`motion-designer`: motion system** for motion tokens.
5. **W6 per component**, with `software-engineer` building.
6. **`design-critique`** on each component, then a drift check every quarter.

### W15 · Adopt a library or component

**Version:** 1.0.0

**Entry:** "Should we use this?" · **Phase:** Develop, Build

1. **Decide whose question it is.**
   - One feature: `software-engineer`, dependency selection.
   - Every product, as a standing dependency: `technical-architect`, dependency evaluation.
2. **`security-specialist`: dependency and supply-chain audit, and a licence check** at package and feature level.
3. **Intake for anything copied into the codebase:**
   - UI components: `design-systems-specialist`, component source intake.
   - Animated components: `motion-designer`, motion component intake.
4. **`accessibility-specialist`** checks what it actually renders. Generated markup proves nothing on its own.
5. **Record the decision.** Upstream origin, version, licence, owner and exit cost go in the ADR, and the decision itself goes in `ppot`.

### W16 · Tell stakeholders what happened

**Version:** 1.0.0

**Entry:** results to share · **Phase:** any

| You have | Use | You get |
|---|---|---|
| Usability test results | `research-reporter`, branded if need be | A self-contained report people can filter and edit |
| A number that moved | `data-analyst` (the readout), then `motion-graphics-designer` (animated chart) | A chart with one claim, for a deck or an all-hands |
| A plan or a launch | `motion-graphics-designer` (animated explainer), with `content-designer` on the words | A short MP4 and its text summary |
| Delivery progress | `delivery-manager` (status reporting) | Progress, risks and the decisions needed |

Before anything leaves the team, put it through `brand-guardian` if it goes outside, and `accessibility-specialist` for contrast and motion.

### W17 · Start or join a project

**Version:** 1.0.0

**Entry:** a new project, or a new person on one

1. **`ppot`: `init`** for a new project, or `brief` for a new person. `review` if it has gone quiet for a month or more.
2. **`brand-guardian`: configuration**, recorded in `PPoT.md`: which brands, where the guidance lives, who owns exceptions.
3. **The pipeline adapter.** Copy [`reference/project-adapter.md`](../reference/project-adapter.md) to `.claude/pipeline-adapter.md`, and fill in the commands, gates and risky paths before the first W6.
4. **`delivery-manager`: ceremony design.** When, and who, the gates meet.

## Composite: run as a fractional product department

For a founder or small team without every discipline, run the spine end to end and keep it turning:

**W17 → W1 → W2 (as needed) → W3 → Gate 1 → W4 → W5 → Gate 2 → W6 for each ticket → W7 → W8 → Gate 3 → W11 → back to W1**

Each workflow's files from rule 3 become the next one's input. `PPoT.md` carries only what was decided and learnt. That is what lets the third time round start where the second left off.

## Getting the most from each skill

What each skill is best at, what to give it, and the mistake to avoid.

| Skill | Reach for it to | Give it | Avoid |
|---|---|---|---|
| `ppot` | Brief, answer, record and check against what the project knows | The question, or the candidate entry | Treating "remember this" as approval; using it as a backlog |
| `product-strategist` | Choose where to play and, as importantly, what not to do | Market, customer and commercial evidence | Asking it for a roadmap; it sets direction |
| `product-manager` | Frame problems, write PRDs and tickets, prioritise, synthesise across disciplines | Evidence from the other skills | Using it for discovery itself; it frames and decides |
| `pricing-strategist` | Model, tiers, packaging and pricing experiments around one value metric | Usage, revenue and churn data | Defaulting to freemium; financial modelling |
| `growth-product-marketing-manager` | Activation, messaging, launches, funnels, content and SEO, each with a guardrail | Funnel data and positioning | Conversion at the expense of trust (pair it with `brand-guardian`) |
| `brand-guardian` | Check claims, naming, partner material and suspected misuse | The brand configuration (ideally in `PPoT.md`) and the guidance | Expecting approval or legal advice; it recommends |
| `customer-success` | Turn tickets and accounts into product signal, with frequency | CRM notes, tickets, usage | One loud account; it says how often |
| `ux-researcher` | Choose a proportionate method, script it, and interpret results | The decision the research must inform | Running a study without a decision behind it |
| `storm-researcher` | Stress-test contested or high-stakes questions from five lenses | A question and the decision at stake | Simple lookups; it is slow on purpose |
| `data-analyst` | Define metrics properly, read funnels and experiments, check data quality | Access to the data, or exports | Causal claims from correlation; it will say so |
| `research-tool-builder` | Build the tool a study runs on, for any method and any setup | The study plan from `ux-researcher` | Inventing tasks; it builds, it does not design studies |
| `research-reporter` | Turn any test results into a scored, branded, checked report | The export, spreadsheet or notes | Asking it what findings mean; that is `ux-researcher` |
| `product-designer` | Cover a whole experience end to end when breadth matters more than depth | The problem and constraints | Using it where a specialist exists and depth matters (see below) |
| `content-designer` | Words that help people act and recover | The screens and the brand voice | Marketing copy; legal wording |
| `design-systems-specialist` | Tokens, components, foundations and intake of copied code | The existing components and token files | A third component that does the same job as two others |
| `accessibility-specialist` | Find exclusion early, and check the built thing late | Designs or the running implementation | Treating automated scans as the whole truth |
| `motion-designer` | Decide whether and how interface motion should happen, with reduced-motion and performance budgets | Surface type, input, frequency and existing tokens | Starting from keyframes rather than state |
| `motion-graphics-designer` | Make a short animation from the team's own content, exported to MP4 | The source and the audience | Fake UI or invented numbers; footage or voices |
| `design-critique` | Make the final design call: SHIP, SHIP_WITH_NOTES or HOLD | The brief and the implementation | Asking it to fix what it finds |
| `technical-architect` | System design, ADRs, integrations and standing dependencies | Architecture docs and requirements | Detailed implementation |
| `software-engineer` | Feasibility, plans, code review, debugging and per-feature library choice, against the installed versions | The codebase | Final architecture authority |
| `devops-engineer` | Make release and running the system repeatable, observable and recoverable | CI/CD, infrastructure and incident history | Expecting it to touch infrastructure itself |
| `security-specialist` | Threat models, audits, RLS, privacy, supply chain and AI safety | Code, schema and policies | Certification or penetration testing |
| `qa-engineer` | Make behaviour testable early, and give release confidence late | Acceptance criteria | Saving it for the end; criteria review is its best early use |
| `delivery-manager` | Make dependencies, risks and decisions visible and time-bound | The tracker and the plan | Product decisions |
| `run-pipeline` | Any code change with verification: it classifies, confirms and dispatches | The ticket | Advice-only work |
| `requirements-generator` | A quick, confirmable brief for a coding task | The request | Discovery; it is a thin intake |
| `shape-task` | Requirements, strategy and safe chunks before code | A confirmed brief | Starting to build |
| `execute-chunk` | One approved chunk, the smallest correct change | A chunk with acceptance criteria | Absorbing gaps in the requirements silently |
| `close-chunk` | Decide independently whether a chunk can close | The chunk and its evidence | Letting the builder close its own work |
| `cleanup-verify` | Run the full gate sweep and drift check on first-hand evidence | The adapter's gates | Fixing things; it reports |
| `diagnose` | Find the cause before anyone patches the symptom | The symptom and how to reproduce it | Unverified fixes |

## Who owns what when skills overlap

| Job | Owner | Others | The split |
|---|---|---|---|
| Research planning, synthesis, accessibility, content, design QA | The specialist | `product-designer` | `product-designer` for breadth on a small team or an early pass; the specialist when depth matters or the work is high-risk |
| Pre-release design decision | `design-critique` | `product-designer` (design QA), `brand-guardian` | `design-critique` owns SHIP or HOLD; `brand-guardian` owns brand and claims; both feed the release decision in W7 |
| Positioning | `product-strategist` | `growth-product-marketing-manager`, `pricing-strategist` | Strategist: where to play and the positioning statement. Growth: messaging in flows and launches. Pricing: the price position |
| Experiments | The one who owns the question | `data-analyst` | Growth or pricing designs the experiment; the analyst reads it out |
| Customer evidence | `ux-researcher` | `customer-success`, `data-analyst` | Research gathers new evidence; customer success reads accounts and tickets; the analyst reads behaviour |
| Debugging | `diagnose` | `software-engineer` | `diagnose` finds the cause; the engineer, or the pipeline, fixes it |
| Code review | Independent reviewer, else `software-engineer` | `security-specialist` | The engineer for correctness; security for the risky paths |
| Dependencies | `software-engineer` (one feature), `technical-architect` (standing) | `security-specialist` | Security checks licence and supply chain for both |
| Copied component code | `design-systems-specialist` | `motion-designer`, `accessibility-specialist` | Design systems for components; motion for animated ones; accessibility checks the render |
| Release readiness | The release owner | `qa-engineer`, `devops-engineer`, `delivery-manager` | QA: quality. DevOps: the running system. Delivery: schedule and flow |
| Motion | `motion-designer` (in the product) | `motion-graphics-designer` (to watch) | Already split, in both skills |
| Interface motion and video accessibility | `accessibility-specialist` | Both motion skills | The floors are not negotiable on any surface |

## Built into the skills

The skills now carry what these workflows rely on, so the recipes above work without extra setup:

- **Handoffs.** Each skill's "Works with" section names who it takes work from and who it hands work to. `scripts/check-handoffs.py` fails CI if a link goes one way or names a skill that doesn't exist.
- **Working files.** Each skill's "Handing over work" section offers to save its output for the next step (rule 3).
- **Model and sub-agents.** Each skill checks the model against the task, and asks before starting sub-agents, with a cap you set (rule 2).
- **Seams and release.** `run-pipeline` offers `diagnose`, `design-critique`, `security-specialist` and `product-manager` at the four seams in W6. It ends a clean run by naming the W7 release steps.
- **Gates that hold.**
  - The Stop hook recognises a `run-pipeline` run and stops gating once the run is complete.
  - `scripts/gate-chain.py` reads the adapter's gate list, including gate names that contain a colon, and fails a ratchet whose count gets worse.
  - `close-chunk` hands the run to the final sweep instead of closing it.
  - Skills inside a pipeline run no longer reset its id.
  - The state contract matches what the skills write.
  - `cleanup-verify` writes both gate stamps in one run.
- **Versions.** Every skill has a version, checked by CI, and so does every workflow in this guide.

## Outside the suite

These belong to people or to other tools. The workflows show where they come in:
- legal and regulatory review
- market sizing and financial modelling
- participant recruitment and research ethics
- localisation
- sales enablement
- high-fidelity visual design production

## Maintenance

Review this guide when:
- a skill is added, removed or renamed, or its intents change
- a squad changes in `routing.md`
- the pipeline gains a step
- a gap above is fixed, in which case remove it and simplify the workflow that worked around it
- a workflow's handoffs change, in which case update the "Works with" sections of the skills involved; `scripts/check-handoffs.py` fails if a link ends up going one way

**Versioning.** Workflows follow the suite's semver:
- **Major:** a workflow is removed, or its gate changes what a person decides.
- **Minor:** steps, skills or a gate's evidence change.
- **Patch:** wording only.

Bump the document's version to match the largest change in it, and note which suite version it was checked against.

The [interactive page](https://claude.ai/artifact/KMSuAh18cm7HfATKLSyt1D) carries the same workflows, skill cards and ownership rules: republish it whenever this guide's version changes, so the two stay the same.

Keep the workflows as recipes that point at skills. A skill's own detail belongs in its `SKILL.md`, and a phase's place in the cycle belongs in `capability-map.md`.
