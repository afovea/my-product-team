# product-team-skills

A product team you can call on: **32 Agent Skills** covering strategy, research, design, engineering, quality and delivery, plus a delivery pipeline for coding work and a shared record of what the project knows.

- **Ask one expert.** A product manager for a PRD, an accessibility specialist for a review, a security specialist for a threat model, a motion designer for an interaction spec. Each one works the way that discipline works.
- **Run a whole piece of work.** [Workflows](#workflows) chain the skills from a rough idea to evidence that it worked, with the checkpoints where a person decides.
- **Build with checks that hold.** The [delivery pipeline](#delivery-pipeline) classifies a coding task, builds it in small verified chunks and won't finish while the project's checks fail.

The skills work in Claude Code, claude.ai, the Claude app and Codex, and on any codebase.

**Start here:** [Get started](#get-started) · [Install guide](./INSTALL.md) · [Workflows](./docs/workflows.md) · [What can my product team do?](./what-can-my-product-team-do.md) · [Capability map](./docs/capability-map.md) · [The Figma board](https://www.figma.com/community/file/1668354152302142589/afoveas-product-delivery-team-skills)

## Contents

- [Get started](#get-started) — install by where you use Claude, in a few lines each
- [Use the skills](#use-the-skills) — how to call a role in Claude Code, claude.ai and Codex
- [Workflows](#workflows) — seventeen recipes that chain the skills, from an idea to evidence it worked
- [The 32 skills](#the-32-skills) — every role and pipeline skill, grouped, with when to reach for it
- [How the skills work together](#how-the-skills-work-together) — the Project Point of Truth, model and sub-agent checks, and the routing brain
  - [Project Point of Truth](#project-point-of-truth)
  - [Model and sub-agents](#model-and-sub-agents)
  - [The routing brain](#the-routing-brain)
- [Delivery pipeline](#delivery-pipeline) — run-pipeline, the project adapter, and gate enforcement
- [The Figma board](#the-figma-board) — the FigJam companion a team runs the work on
- [Install options in depth](#install-options-in-depth) — every route compared, duplicates, context cost, updating and compatibility
  - [Which route](#which-route)
  - [Precedence and duplicates](#precedence-and-duplicates)
  - [Context cost, and how to turn it down](#context-cost-and-how-to-turn-it-down)
  - [Keeping it up to date](#keeping-it-up-to-date)
  - [Migrating from the old repo](#migrating-from-the-old-repo)
  - [Compatibility](#compatibility)
- [For maintainers](#for-maintainers) — repository layout, conventions, versioning and contributing
  - [Repository layout](#repository-layout)
  - [Conventions](#conventions)
  - [Versioning](#versioning)
  - [Contributing](#contributing)
- [Licence](#licence)

## Get started

Which Claude you're using decides how to install, and the methods aren't interchangeable. Find your row; [INSTALL.md](./INSTALL.md) has every step written out, with what you should see at each step, and a troubleshooting section keyed to the exact error text.

| Where you are | What to do | Step by step |
|---|---|---|
| **claude.ai** in a browser, or the Claude app's **Chat** tab | Upload the roles you want, one ZIP each | [INSTALL Part 4](./INSTALL.md#part-4--claude-for-chatting-browser-or-chat-tab) |
| **Claude Code**: the Claude app's **Code** tab, or a terminal | Two typed lines install all 32 | [Part 2](./INSTALL.md#part-2--claude-code-in-the-desktop-app) (app), [Part 3](./INSTALL.md#part-3--claude-code-in-a-terminal) (terminal) |
| **Claude Code cloud sessions** (`claude.ai/code`) | Commit a project install to the repository | [Part 7](./INSTALL.md#part-7--claude-code-cloud-sessions) |
| **Codex**, or another host that reads `SKILL.md` | One command | [Part 6](./INSTALL.md#part-6--codex-and-other-hosts-that-read-skillmd) |

### claude.ai and the Chat tab

1. **Settings → Capabilities**: switch on **Code execution and file creation** (called **Create and edit files** in the newer layout). On a Team or Enterprise plan, an owner first allows skills in **Organization settings → Plugins & skills**.
2. Download the roles you want from [`download/`](./download), for example [product-manager.zip](https://github.com/afovea/my-product-team/raw/main/download/product-manager.zip). **Don't unzip them.**
3. **Customize → Skills → + → Create skill → Upload a skill**, pick the file, and check it's switched on.
4. Ask, naming the role: *"As a product designer, our reports page is blank for new users. Design the empty state."*

Uploads belong to your account, so they appear in the browser, the app and your cloud sessions.

### Claude Code

In the Code tab's message box, or after starting `claude` in a terminal, type:

```
/plugin marketplace add afovea/my-product-team
/plugin install product-team@productteam-skills
```

The second line opens a panel: choose **Install for you (user scope)**. Then type `/product-team:` and the 32 roles appear:

```
/product-team:product-manager Turn this vague feature request into a delivery-ready ticket.
```

You get the delivery pipeline, the gate-enforcement hook and a once-a-day update reminder too. The three names differ on purpose: `my-product-team` is the repository, `productteam-skills` the marketplace, and `product-team` the plugin.

If `/plugin` does nothing in the app, use the **+** button next to the message box and choose **Add plugins**. [INSTALL.md](./INSTALL.md#typing-plugin-does-nothing-in-the-app) covers the rest.

### Claude Code cloud sessions

Cloud sessions start from a fresh copy of the repository and don't load plugins. Commit a project install instead, and every cloud session on that repository gets the roles and the routing brain:

```bash
git clone https://github.com/afovea/my-product-team.git
cd my-product-team
./install.sh /path/to/your/repo     # then commit .claude/ and CLAUDE.md in your repo
```

Skills you switch on in claude.ai also load in your own cloud sessions.

### Codex

```bash
git clone https://github.com/afovea/my-product-team.git
cd my-product-team
./install.sh --agents --personal
```

All 32 go into `~/.agents/skills/`, available in every project. Restart Codex, then:

```
$product-manager Turn this vague feature request into a delivery-ready ticket.
```

> **Installed from the old `ProductTeam-skills` repository?** It has moved here. See [Migrating](#migrating-from-the-old-repo).

[↑ Back to contents](#contents)

## Use the skills

**Give the role the actual task in the same message.** A role called with nothing to do asks you what you want.

### In Claude Code

Type `/product-team:` and the role's name, then the task:

```
/product-team:product-designer Our reports page is blank for new users. Design the empty state.
/product-team:security-specialist Review this migration for RLS gaps.
/product-team:accessibility-specialist This chart uses colour alone for four series. Problem?
/product-team:run-pipeline Add a /health route returning DB connectivity.
```

The full name always reaches the plugin. The short form, such as `/product-designer`, also works, but only while nothing else uses that name. Skills you uploaded to claude.ai, or an `install.sh` copy, take it: see [Precedence and duplicates](#precedence-and-duplicates).

### In claude.ai and the Chat tab

There are no commands. Name the role in ordinary words:

```
As a product designer, our reports page is blank for new users. Design the empty state.
Acting as an accessibility specialist, this chart uses colour alone for four series. Problem?
As a content designer, rewrite this error: "Error 4012: request failed."
```

If Claude picks the wrong expert, say so: "answer this as a content designer, not a product manager". Uploading fewer roles helps it choose.

### In Codex

Type `$` and the role's name:

```
$product-designer Our reports page is blank for new users. Design the empty state.
$run-pipeline Add a /health route returning DB connectivity.
```

### Roles wait to be asked, on purpose

In Claude Code and Codex, no role starts on its own: describing a design problem won't summon the product designer. Automatic selection matches on keywords, and testing showed it picks badly. "Payments integration" pulled in the pricing strategist, and "release risk" the delivery manager. You choose the role, or the [routing brain](#the-routing-brain) suggests one.

Claude Code is told this with `disable-model-invocation: true` in each skill. Codex is told with `policy.allow_implicit_invocation: false` in each skill's `agents/openai.yaml`, and CI checks the two stay in step.

Two exceptions:
- **`ppot`** answers natural phrases such as "bring me up to speed" and "record our decision", because those phrases are how it's meant to be used.
- **claude.ai and the Chat tab** have no commands, so Claude choosing is the only way in. The ZIPs therefore ship without the switch, and naming the role in your sentence steers the choice.

Once a role is loaded it stays for the rest of the conversation. Start a new session to drop it.

[↑ Back to contents](#contents)

## Workflows

The skills are deliberately narrow, so real product work needs several of them, in the right order. **[docs/workflows.md](./docs/workflows.md)** is the recipe book: seventeen workflows, each naming which skill runs when, what to ask it for, what it leaves behind for the next step, and where a person has to decide.

Each skill also names who it takes work from and who it hands work to, in its own "Works with" section, so a skill can point you to the next one even outside a workflow.

### The spine: from idea to evidence

Eight workflows take an idea through the product cycle, closing three gates where a person agrees the work can move on, or sends it back:

```
W17 Start ─► W1 Frame ─► W3 Define ─► Gate 1 ─► W4 Develop ─► W5 Decide ─► Gate 2
                ▲  │         ▲                     │                          │
                │  └─► W2 Test with users ◄────────┘                          ▼
                │                                         W6 Build (per ticket, many)
                │                                                             │
                └──── W11 Health check ◄── Gate 3 ◄── W8 Launch ◄── W7 Release decision
```

| | Workflow | Starts from | Ends with |
|---|---|---|---|
| W1 | [Frame the problem](./docs/workflows.md#w1--frame-the-problem) | "Is this worth pursuing?" | Evidence and the riskiest assumptions |
| W2 | [Test with users](./docs/workflows.md#w2--test-with-users) | An assumption only users can settle | A report and what it means |
| W3 | [Define the bet](./docs/workflows.md#w3--define-the-bet) | A problem with evidence | **Gate 1: Problem agreed** |
| W4 | [Develop the solution](./docs/workflows.md#w4--develop-the-solution) | An agreed problem | Two or three tested options |
| W5 | [Decide and make ready](./docs/workflows.md#w5--decide-and-make-ready) | Options | **Gate 2: Approach agreed**, ready tickets |
| W6 | [Build a ticket](./docs/workflows.md#w6--build-a-ticket) | A ready ticket | Verified code |
| W7 | [Release](./docs/workflows.md#w7--release) | Built work | **The release decision** |
| W8 | [Launch and learn](./docs/workflows.md#w8--launch-and-learn) | A release | **Gate 3: Outcome evidenced** |

### Workflows for any time

| | Workflow | Use it when |
|---|---|---|
| W9 | [Investigate a product question](./docs/workflows.md#w9--investigate-a-product-question) | A metric moved and nobody knows why |
| W10 | [Fix a bug or incident](./docs/workflows.md#w10--fix-a-bug-or-incident) | Something broke |
| W11 | [Product health check](./docs/workflows.md#w11--product-health-check) | You need to know what's wrong and what matters most |
| W12 | [Red-team a bet](./docs/workflows.md#w12--red-team-a-bet) | Before investing in an idea, or committing to a design |
| W13 | [Price and package](./docs/workflows.md#w13--price-and-package) | The commercial model is in question |
| W14 | [Stand up or audit a design system](./docs/workflows.md#w14--stand-up-or-audit-a-design-system) | A new interface, or drift between products |
| W15 | [Adopt a library or component](./docs/workflows.md#w15--adopt-a-library-or-component) | "Should we use this?" |
| W16 | [Tell stakeholders what happened](./docs/workflows.md#w16--tell-stakeholders-what-happened) | Results, numbers or progress to share |
| W17 | [Start or join a project](./docs/workflows.md#w17--start-or-join-a-project) | A new project, or a new person on one |

### What one looks like

W10, fixing a bug, in Claude Code:

1. `/product-team:diagnose Checkout totals are wrong for orders over £1,000.` It reproduces the fault, tests its hypotheses one at a time, and recommends a fix only once the cause is proven.
2. `/product-team:run-pipeline Fix the checkout total bug using the diagnosis.` It plans the change, waits for your go-ahead, builds it in small verified chunks, and runs the project's checks.
3. `/product-team:qa-engineer Write a regression test for the checkout total bug.` A test that fails without the fix, kept in CI.
4. `/product-team:ppot learn Rounding happened before tax in the checkout service.` What broke and why becomes something the project knows, once you approve it.

### Rules every workflow follows

- **Start with what's known:** `ppot brief` first, so nobody re-argues a settled decision.
- **Model and sub-agents are settled once,** at the start, with any parallel work capped by you.
- **Hand over files, not memories.** Each skill offers to save its output for the next step.
- **A person decides at every gate.** The skills recommend.
- **Knowledge goes back at the end,** as proposals you approve.
- **Whoever builds something doesn't approve it.**

The guide also has a best-use card for every skill and the ownership rules for where two skills could claim the same job. Workflows are versioned (currently 1.0.0).

[↑ Back to contents](#contents)

## The 32 skills

Run each one as `/product-team:<name>` in Claude Code, `$<name>` in Codex, or by naming the role in claude.ai. The [workflows](#workflows) say which to use when, and each skill's "Works with" section names its neighbours.

### Shared project knowledge

| Skill | Use when |
|---|---|
| `ppot` | Project briefings, facts, decisions, assumptions, durable learning, contradictions, knowledge reviews, and checking artefacts against project truth |

### Product and strategy

| Skill | Use when |
|---|---|
| `product-manager` | Value, scope, outcomes, prioritisation, PRDs, backlog structure |
| `product-strategist` | Market positioning, vision, strategic bets, competitive framing |
| `growth-product-marketing-manager` | Adoption, activation, messaging, funnel, CRO, content strategy, SEO |
| `pricing-strategist` | Pricing models, tier structure, packaging, willingness-to-pay |
| `brand-guardian` | Brand fidelity, claims and trust review, naming and strategy fit, co-branding, suspected brand misuse |

### Research, insight and data

| Skill | Use when |
|---|---|
| `ux-researcher` | Research planning, discovery, interviews, synthesis, validation |
| `data-analyst` | Metrics, dashboards, funnels, experiments, behavioural evidence |
| `customer-success` | Customer feedback, retention signals, adoption blockers |
| `storm-researcher` | Contested or strategic research — five-perspective scan, contradiction mapping, adversarial review |
| `research-tool-builder` | Consistent offline tools for any research method, from card sorts and tree tests to five-second, preference and diary studies, exporting one session format |
| `research-reporter` | Usability test results turned into a consistent, brandable, editable stakeholder report |

### Design and experience

| Skill | Use when |
|---|---|
| `product-designer` | UX, UI, flows, interaction design, design QA |
| `content-designer` | UX writing, labels, errors, onboarding, comprehension |
| `design-systems-specialist` | Components, tokens, theming, UI foundation choice, component source intake |
| `motion-designer` | Animation, transitions, micro-interactions, pointer effects, ambient/WebGL backgrounds, motion tokens, reduced motion, animation performance |
| `motion-graphics-designer` | Short animated explainers, animated charts and product walkthroughs built from your own content, exported to MP4 |
| `accessibility-specialist` | WCAG review, inclusive design, assistive-tech risk, data-visualisation accessibility |

### Engineering, delivery and quality

| Skill | Use when |
|---|---|
| `software-engineer` | Implementation, feasibility, trade-offs, library selection, version-matched API use |
| `technical-architect` | System design, integration strategy, scalability, standing-dependency evaluation |
| `devops-engineer` | CI/CD, environments, deployment and rollback, observability — risk in the *running system* |
| `security-specialist` | Threat modelling, audits, auth/RLS review, DPIA, supply chain and licence boundaries, AI safety |
| `qa-engineer` | Test planning, regression, bug reporting, durable proof of verification |
| `delivery-manager` | Delivery planning, dependencies, ceremonies — risk to *schedule and flow* |

### Delivery pipeline skills

| Skill | Use when |
|---|---|
| `run-pipeline` | **Start here for any coding task.** Classifies Small / Medium / Large and dispatches |
| `requirements-generator` | Turning a rough request into a confirmation-ready brief |
| `shape-task` | Decomposing a brief into requirements, strategy and chunks |
| `execute-chunk` | Implementing one approved chunk with scoped edits and targeted validation |
| `close-chunk` | Verifying a chunk against its acceptance criteria |
| `cleanup-verify` | Post-run sweep: regenerate artefacts, rebuild, run the gate chain, report drift |
| `diagnose` | Root-cause analysis — reproduce → isolate → verify → fix |
| `design-critique` | Final-pass design review with a SHIP / SHIP_WITH_NOTES / HOLD decision |

Several skills carry reference material that loads only when needed: `security-specialist` (a nine-category audit cookbook and a health-data domain pack), `motion-designer` (standards, libraries and component-gallery intake), `ppot` (entry schema and governance), and the two research skills (method specifications, data formats and theming).

[↑ Back to contents](#contents)

## How the skills work together

Three things tie the skills together.

### Project Point of Truth

The suite includes a `ppot` practice for consulting and maintaining a product’s
`PPoT.md` — a concise, human-governed register of durable facts, decisions,
constraints, assumptions, and learning.

Every other product-team skill is compatible with it. When relevant, a skill:

1. **pulls** established context from `PPoT.md` before working;
2. preserves the difference between confirmed knowledge and uncertainty;
3. **pushes** durable new knowledge back as a proposal after the work;
4. waits for explicit approval before the PPoT is changed.

The practice is available directly:

```text
/product-team:ppot brief
/product-team:ppot ask What do we know about enterprise onboarding?
/product-team:ppot decide We will release read-only sharing first
/product-team:ppot check docs/new-feature-prd.md
/product-team:ppot review
```

Natural language works too: “Bring me up to speed”, “Remember that users treat
archive as reversible”, or “Check this PRD against the project truth”. The PPoT
belongs in the consuming product repository; this plugin supplies the practice
and starter template, not the project’s facts.

**→ [How to use the Project Point of Truth](./docs/PPOT.md)**

Contribution practices, entry types, approval rules, natural-language examples,
and the pull/push handshake used by every skill.

### Model and sub-agents

Every skill carries the same short section, so the behaviour is the same whichever skill runs:

1. **It checks the model.** Before substantial work, the skill says in one line which model is running and which tier the task needs: `most-capable` (Opus), `balanced` (Sonnet) or `fast` (Haiku), or the host's equivalents. Each skill has a usual tier (`metadata.model_tier` in its frontmatter), moved up for high-stakes, ambiguous or long work and down for lookups and mechanical checks. If the two differ, it asks whether to switch or carry on. A skill cannot switch the model itself; you do, with `/model` or the app's model menu.
2. **It asks before sub-agents.** No skill starts sub-agents, parallel agents or a multi-agent workflow on its own. It says why they would help, what each would do and which model each would use, then asks you to set a cap: none, up to 2, up to 5, or another number. The cap covers the whole task. A cap already set in your instructions counts.

Both happen once per task. When `run-pipeline` orchestrates other skills, it settles them in its plan, and the skills it calls do not ask again.

| Usual tier | Skills |
|---|---|
| `most-capable` | diagnose, pricing-strategist, product-strategist, research-tool-builder, run-pipeline, security-specialist, storm-researcher, technical-architect |
| `fast` | cleanup-verify, requirements-generator |
| `balanced` | every other skill |

The section's text lives once, in [`reference/model-and-sub-agents.md`](./reference/model-and-sub-agents.md). Each skill keeps its own copy, because skills install one at a time; `python3 scripts/sync-shared-sections.py` refreshes every copy, and `scripts/verify.sh` fails if one drifts or a skill has no tier.

### The routing brain

[`routing.md`](./routing.md) goes in a project's `CLAUDE.md` — or its `AGENTS.md` for Codex — and decides which role or squad a request belongs to, so you can ask in prose instead of picking a skill:

> "The error message when a payment fails is confusing. Rewrite it." → Content Designer
> "This chart distinguishes four series by colour alone." → Accessibility Specialist
> "Fix the typo in the footer." → no specialist; it is a mechanical edit

With the plugin, it **names** the role and gives you its command, because the roles never start on their own. With a project install, where the skill files sit in the project, Claude reads and follows the right one itself. Install it with `./install.sh --routing-only /path/to/project` alongside the plugin, or as part of a project install; [INSTALL.md](./INSTALL.md#part-5--optional--let-claude-pick-the-expert) has both.

It also defines **six squads** for cross-functional work — Discovery, Definition, Delivery, Validation, Growth, Platform — because "is this ready to ship?" is not one discipline's call.

Squads are not the six *phases* of the product cycle, despite three of the names colliding. A squad is who you need; a phase is where you are. [`docs/capability-map.md`](./docs/capability-map.md) maps one onto the other.

Measured at **89.6% selection accuracy** across 16 cases (up from 70.8%). Two findings drove the improvement, both worth knowing if you edit it:

- **Keyword collision beats persona overlap.** A single salient word drags a request to the wrong role. Where roles genuinely overlap, routing coped fine.
- **The roles table outweighs the prose rules below it.** One case failed 0/3 across three prose edits, then passed when two words changed in the table. Put load-bearing distinctions in the table.

[↑ Back to contents](#contents)

## Delivery pipeline

`run-pipeline` is the entry point: `/product-team:run-pipeline` and the task, in Claude Code. It classifies scope, surfaces a plan for confirmation, then dispatches — Small runs a single scoped change, Medium adds requirements/shaping and a chunk loop, Large adds repository inspection and an architect plan.

Two documents make it portable:

| Document | Purpose |
|---|---|
| [`reference/project-adapter.md`](./reference/project-adapter.md) | Your project's package manager, gate chain, generated artefacts, risky paths, host integrations. Copy to `.claude/pipeline-adapter.md` and fill in |
| [`reference/state-schema.md`](./reference/state-schema.md) | The shared state contract, and how skills degrade when state is unavailable |

**It runs without an adapter.** Skills fall back to discovering commands from repository instructions, manifests, CI config and the lockfile, and state what they found. Writing the adapter makes it deterministic and lets you declare what discovery cannot infer — which gates may fail, which paths are risky, whether an independent reviewer exists.

Nothing assumes a JavaScript toolchain, a specific agent host, or a writable cache.

### Verified by running, not reading

| Testbed | Result |
|---|---|
| npm project **with** an adapter — blocking drift gate, ratcheted style gate at accepted baseline 3, deliberately stale artefact | `run-pipeline`, `execute-chunk`, `close-chunk`, `cleanup-verify` all correct |
| Python/Make project with **no adapter** and no cache | Discovery fallback correct, zero JavaScript assumptions |

Specifically observed: a "one-line" schema change correctly promoted Small → Medium; `execute-chunk` skipping the build and drift gates because the chunk did not touch a declared risk path; `close-chunk` re-running the gate chain itself rather than trusting the implementer's report; `cleanup-verify` regenerating a stale artefact, refusing to commit it, withholding the gate stamp and returning `BLOCKED`.

### Enforcing the gates

Everything above describes what the pipeline *should* do. A skill that says "run the gate chain" is an instruction, and an instruction can be skipped. `cleanup-verify` returning `BLOCKED` is a report, not a stop.

The plugin ships a `Stop` hook that makes it a stop. Hooks are the only layer in Claude Code that runs as code rather than as instruction, so the gate chain becomes non-negotiable rather than well-intentioned.

| File | Role |
|---|---|
| `scripts/gate-chain.py` | Resolves and runs the gate chain, reports a JSON result, writes a stamp |
| `hooks/gate-stop.py` | The `Stop` hook: refuses to end the turn while a blocking gate is failing |
| `hooks/update-check.py` | The `SessionStart` hook: once a day, says when a newer release is tagged ([details](./INSTALL.md#keeping-it-up-to-date)) |
| `hooks/hooks.json` | Registers both hooks. Loads automatically when the plugin is enabled |

**It only wakes up for an open run.** A `Stop` hook fires every turn, so the hook first looks for a pipeline state file under `.claude/`. No state file, no gates, no cost. Detection is by shape rather than by exact filename, so renaming the state contract does not break it. A run can opt out entirely with `"gate_required": false` in its state.

**A pass is bound to the tree it ran against.** The stamp records a fingerprint of `HEAD`, the full uncommitted diff, and the contents of every untracked file git is not ignoring. That last part matters: new source files are untracked until they are committed, and without hashing them a green result would go on vouching for a file it had only ever seen in its first version. Any subsequent edit invalidates the stamp.

**It will not trap you.** After three consecutive blocks on the same tree the hook releases the turn with a warning rather than looping.

`gate-chain.py` is standalone and dependency-free, so pipeline skills can invoke it directly instead of describing the chain in prose:

```bash
python3 scripts/gate-chain.py run --stamp     # run the chain, stamp on pass
python3 scripts/gate-chain.py status          # is there a valid stamp?
python3 scripts/gate-chain.py gates           # show the resolved chain
```

Gate resolution follows the same declare-then-discover pattern as the rest of the pipeline, first hit wins:

1. `.claude/pipeline-gates.json`
2. `.claude/pipeline-adapter.md`: a ` ```gates ` fenced block, or else the `gates: chain:` list in its YAML (the form [`reference/project-adapter.md`](./reference/project-adapter.md) documents)
3. discovery from `package.json`, `Makefile` or `pyproject.toml`

The ` ```gates ` form is one gate per line, `name: command`. Names may contain colons, because the separator is a colon followed by a space. A leading `?` marks a gate non-blocking, and `(baseline N)` turns it into a ratchet:

```gates
lint: npm run lint
contracts:validate: npm run contracts:validate
test: npm test
?style: npm run style
?check:architecture (baseline 47): npm run check:architecture
```

A ratchet's exit code is ignored. The last number in its output (or in the output of the YAML form's `baseline.read` filter) must be no higher than its baseline. A higher count, or no number at all, fails the chain like a blocking gate. A non-blocking gate without a baseline only reports.

Scratch files live in `.claude/.gate/`, which excludes itself from version control. Nothing needs adding to a consuming project's `.gitignore`.

[↑ Back to contents](#contents)

## The Figma board

**→ [Afovea's Product Delivery Team Skills — Figma Community](https://www.figma.com/community/file/1668354152302142589/afoveas-product-delivery-team-skills)**

A FigJam board that turns this repo into something a team can run in a room. The skills supply the judgement; the board supplies the order, the timings and the checkpoints. Duplicate it into your drafts and work down it.

**An introduction page** covers how the board and the repo fit together, the 28 skills and how to invoke each one, the Project Point of Truth practice, and the product cycle as a **triple diamond** — Discover → Define → Develop → Decide → Build → Deliver and learn, closed by three gates: **Problem agreed**, **Approach agreed**, **Outcome evidenced**. A detail panel per phase names each capability that earns its keep there, when to reach for it, which roles are involved, what comes out, and what it writes to the PPoT.

**Six further pages, one per phase,** hold the working boards. Each capability gets a run-sheet built as numbered zones with a time budget and a stated output, so a session has a shape rather than a blank canvas. Gates get run-sheets of their own, ending in a signed decision that can send the work back a diamond as readily as forward.

It is the visual counterpart of [`docs/capability-map.md`](./docs/capability-map.md) — the same model, laid out to be filled in rather than read. Neither one installs anything: the skills still come from a route in [Install options](#install-options-in-depth).

[↑ Back to contents](#contents)

## Install options in depth

Every route, compared. **[INSTALL.md](./INSTALL.md) walks each one through to a verified install**, with troubleshooting keyed to the exact error text.

| Route | Command | You get |
|---|---|---|
| **Plugin** *(recommended)* | `/plugin install product-team@productteam-skills` | All 32 skills **plus** the gate hook and a once-a-day update reminder. Updatable with one command ([how](./INSTALL.md#keeping-it-up-to-date)). No routing brain |
| **Desktop app** | the same two lines in the Code tab, or **+** → **Add plugins** | The same, without a terminal |
| **Cloud sessions** | `install.sh /path/to/repo`, then commit | The skills and routing brain for every cloud session on that repository. Cloud sessions don't load plugins |
| **Routing only** | `install.sh --routing-only /path/to/project` | The routing brain alone, for when the plugin already supplies the skills |
| **Per project** | `install.sh /path/to/project` | Skills in `<project>/.claude/skills/` **plus** the routing brain in its `CLAUDE.md`. Add `--agents` for `.agents/skills/` and `AGENTS.md` |
| **Personal** | `install.sh --personal` | Skills in `~/.claude/skills/` — every project. Skills only |
| **Submodule** | `install.sh --submodule /path/to/project` | Per-project, pinned to a tag, symlinked so discovery still works |
| **Claude apps** *(no terminal)* | download a ZIP from [`download/`](./download), upload it | The roles you upload, in claude.ai, the Chat tab, Cowork and your cloud sessions. No routing brain, no hook |
| **Codex / open standard** | add `--agents` to any `install.sh` route | The same, written to `.agents/skills/` and `AGENTS.md`, invoked as `$name` |

The script is in the repo, so clone first for those routes:

```bash
git clone https://github.com/afovea/my-product-team.git
cd my-product-team
./install.sh --verify                     # what is installed right now?
./install.sh /path/to/your-project
```

It copies the skills, appends the routing brain to `CLAUDE.md` — or `AGENTS.md` with `--agents` — **with the paths and invocations already rewritten for that host**, updates `.gitignore`, and seeds a pipeline adapter template. Re-running updates the routing block in place between its markers and leaves anything you wrote above it alone. Running it with no arguments prints the menu rather than guessing a target.

### Which route

- **Just want the skills?** The plugin, in the terminal or the desktop app. For cloud sessions, a committed project install.
- **Want role arbitration too?** Plugin *plus* `install.sh --routing-only` (add `--agents` on Codex). Routing lives in `CLAUDE.md` or `AGENTS.md`, which is per-project, so no plugin can carry it. Use `--routing-only` rather than a full per-project install: the latter puts a second copy of all 32 skills on disk, which takes the short `/name` and then goes stale independently of the plugin.
- **Want it pinned and tracked in the consuming repo?** Submodule.
- **On claude.ai or the desktop app's Chat tab?** Those are a different product from Claude Code — download a ZIP from [`download/`](./download) and upload it, per [INSTALL.md](./INSTALL.md#part-4--claude-for-chatting-browser-or-chat-tab).

**The repo is the source, not an installation.** Cloning it makes the skills visible nowhere. Claude Code discovers them at `~/.claude/skills/<name>/SKILL.md` or `<project>/.claude/skills/<name>/SKILL.md`, or from an installed plugin. Pick a route above, or you will not see them.

### Precedence and duplicates

Plugin skills are namespaced, as `/product-team:product-manager`, so they never collide with anything: the full name always reaches the plugin. The short `/product-manager` goes to whichever copy claims it first, and three things can claim it:

- **A filesystem copy** from `install.sh`, personal or project. It takes the short name; the plugin stays reachable by its full name.
- **Skills uploaded to claude.ai.** They appear in Claude Code when you're signed in with the same account, listed with `synced` as their source in `/plugin`. They're built for chat, so Claude may start one on its own. Switch them off in `/plugin`'s **Installed** tab, or in claude.ai, if you use the plugin.
- **Another plugin** with a skill of the same name.

Enterprise overrides personal, and personal overrides project. `./install.sh --verify` reports every copy it can find, and says which combinations are worth reducing to one.

### Context cost, and how to turn it down

Installing 32 skills is not free. Two different costs, and the second is the one that actually bites.

**Always-on** — every skill's `name` and `description` are preloaded into the system prompt so the host knows what exists. That is **about 2,700 tokens on every session**, including projects with nothing to do with product work. Nothing else loads until a skill is invoked.

**On-invoke** — the skill's body enters the conversation when you call it, and **stays there for the rest of the session**. That ranges from about 2k to 10.6k tokens depending on the skill. This is the larger number by far.

See your own figures, per skill:

```bash
claude plugin details product-team
```

The heaviest bodies are worth knowing before you invoke them casually:

| Skill | always-on | on-invoke |
|---|---:|---:|
| `motion-designer` | ~210 | ~10.6k |
| `run-pipeline` | ~80 | ~8.1k |
| `security-specialist` | ~90 | ~6.7k |
| `storm-researcher` | ~70 | ~5.9k |
| *typical role* | ~50–200 | ~2–4k |

Figures from `claude plugin details product-team` on version 1.9.

#### Turn the always-on cost off entirely

```bash
claude plugin disable product-team@productteam-skills   # off, still installed
claude plugin enable product-team@productteam-skills    # back on
claude plugin disable --all                 # every plugin
```

`disable` takes `--scope user|project|local`, so you can switch the suite off globally and leave it on in one repo, or the reverse.

#### Scope it to the projects that need it

Installing at project scope keeps the always-on cost out of every unrelated session:

```bash
claude plugin install product-team@productteam-skills --scope project
```

#### Drop skills you never use

There is no per-skill disable. Two ways to trim anyway:

- **Filesystem install** — delete the directories you do not want. `install.sh --personal` then `rm -r ~/.claude/skills/motion-designer` removes that skill and its always-on share. Losing `motion-designer` alone saves ~210 tokens per session, more than four typical roles.
- **Fork the plugin** — remove the skill directories from `skills/` and point your marketplace at your fork. Survives updates; a filesystem deletion does not.

#### Managing the on-invoke cost

- A skill loads **once** per session. Re-invoking the same one adds a short note, not a second copy.
- Start a fresh session to clear loaded skills, rather than invoking a different one to "switch".
- After auto-compaction, invoked skills are re-attached at up to 5,000 tokens each within a **combined 25,000-token budget**, most-recent first. Invoke many heavy skills in one session and the earliest ones get dropped entirely — so if a skill seems to stop influencing behaviour after a long session, re-invoke it.

### Keeping it up to date

Plugin updates are off by default for marketplaces outside Anthropic's, so turn on auto-update for `productteam-skills` in `/plugin`'s **Marketplaces** tab, or update by hand: **Installed** tab → **product-team** → **Update now**, or `claude plugin update product-team@productteam-skills`. Once you're on 1.9 or later, a once-a-day reminder says when a newer release is tagged. [INSTALL.md](./INSTALL.md#keeping-it-up-to-date) covers every route, including ZIP uploads and submodules.

### Migrating from the old repo

This suite previously lived at `afovea/ProductTeam-skills`, later renamed `afovea/product-team-skills`. If `claude plugin marketplace list` shows either as the source of `productteam-skills`, GitHub's redirect keeps it working for now, but point it at the current name:

```bash
# 1. point the marketplace at the new repo (removing it uninstalls the plugin;
#    the next two lines put it back)
claude plugin marketplace remove productteam-skills
claude plugin marketplace add afovea/my-product-team
claude plugin install product-team@productteam-skills

# 2. if you used a filesystem install from an older layout, clear the stale
#    nested pipeline directory — skills are flat now
rm -r ~/.claude/skills/pipeline            # personal installs
rm -r <project>/.claude/skills/pipeline    # project installs
```

Earlier versions nested the eight pipeline skills one level deeper, so an old install leaves that directory behind and they end up present twice. `install.sh` detects this and prints the exact command rather than deleting anything itself.

### Compatibility

The skills are plain markdown following the [Agent Skills](https://agentskills.io) standard, so they work with any host that reads `SKILL.md`. Two hosts are supported with a route of their own rather than left to you to wire up: Claude Code, and Codex.

The suite is written twice over where the two disagree, so neither is a second-class citizen:

| | Claude Code | Codex |
|---|---|---|
| Skills | `.claude/skills/` | `.agents/skills/` |
| Invocation | `/product-team:name` (plugin) or `/name` (`install.sh`) | `$name` |
| Suppress auto-selection | `disable-model-invocation` | `agents/openai.yaml` |
| Routing brain | `CLAUDE.md` | `AGENTS.md` |
| Plugin manifest | `.claude-plugin/` | `.codex-plugin/` |
| Gate enforcement | `Stop` hook | `Stop` hook |

`install.sh` writes either — add `--agents` for the second column — and `./install.sh --verify` reports both.

What survives on each surface:

| | Skills | Routing brain | Gate hook |
|---|---|---|---|
| Claude Code: terminal and desktop **Code** tab | ✅ | names the role with the plugin; ✅ with a project install | ✅ with the plugin |
| Claude Code cloud sessions | ✅ committed, or uploaded to claude.ai | ✅ when committed | ❌ |
| Codex — CLI and IDE | ✅ | ✅ with a project install | ✅ |
| Claude apps: claude.ai, desktop **Chat** tab, Cowork | ✅ ones you upload | ❌ no `CLAUDE.md` | ❌ no hooks |
| Any other `SKILL.md` host | ✅ via `--agents` | depends on the host | depends on the host |

Gate enforcement needs a host with hooks. Claude Code and Codex both have a `Stop` event that a hook can refuse, and the same script serves both. Where hooks do not exist, the pipeline skills still run and still report a failing gate — they just cannot be stopped by one.

**Observed on Codex**, not inferred from the spec: installed to `~/.agents/skills/`, the roles appear in the `$` picker carrying the display names and descriptions from their `agents/openai.yaml`, and a fresh session handed a design problem in prose answers it directly rather than summoning a role — so `allow_implicit_invocation: false` does what it claims. The extra frontmatter fields these skills carry beyond `name` and `description` are ignored rather than rejected. The `Stop` hook is the one part shared by both hosts that has so far only been exercised on Claude Code.

The desktop app's **WSL** sessions don't load plugins: use a filesystem install there.

[↑ Back to contents](#contents)

## For maintainers

The rest is for people changing the suite itself.

### Repository layout

```
my-product-team/
├── .claude-plugin/
│   ├── plugin.json                   # makes this an installable plugin
│   └── marketplace.json              # makes the repo an addable marketplace
├── .codex-plugin/
│   └── plugin.json                   # the same, for Codex. Points at skills/
│                                     #   and hooks/, so nothing is duplicated
├── skills/                           # all 32 skills, flat, one directory each
│   ├── product-manager/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml        # Codex display name + invocation policy
│   ├── ppot/                         # project knowledge practice
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml        # no policy block — this one may self-fire
│   │   ├── references/               # schema and governance
│   │   └── assets/PPoT-template.md
│   ├── brand-guardian/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml
│   ├── motion-designer/
│   │   ├── SKILL.md
│   │   └── references/motion-resources.md
│   ├── motion-graphics-designer/
│   │   ├── SKILL.md
│   │   ├── assets/template.html      # working animation to build from
│   │   └── scripts/export.mjs        # HTML → MP4, no npm dependencies
│   ├── security-specialist/
│   │   ├── SKILL.md
│   │   └── references/               # audit cookbook, healthcare pack
│   ├── run-pipeline/SKILL.md         # pipeline skills sit alongside roles
│   └── ...
├── hooks/                            # code that runs, rather than instructions
│   ├── hooks.json                    # registers both hooks
│   ├── gate-stop.py                  # blocks the turn on a failing gate
│   └── update-check.py               # once a day, says when a newer release exists
├── download/                         # one upload-ready ZIP per skill, committed
│   ├── product-designer.zip          #   so non-technical users can install
│   └── ...                           #   without a terminal. CI keeps it in sync
├── scripts/
│   ├── gate-chain.py                 # standalone gate chain runner
│   ├── sync-shared-sections.py       # keeps every skill's shared section identical
│   ├── check-handoffs.py             # every "Works with" link names a real skill, both ways
│   └── package-skills.sh             # rebuilds download/
├── reference/                        # shared docs, deliberately not skills
│   ├── handing-over-work.md          # shared section: save outputs for the next step
│   ├── model-and-sub-agents.md       # shared section: model check and sub-agent approval
│   ├── project-adapter.md
│   └── state-schema.md
├── docs/
│   ├── PPOT.md                       # product-owner usage guide
│   └── capability-map.md             # capability → phase, and what each phase records
├── routing.md                        # the routing brain
├── install.sh                        # filesystem install; --verify reports state
├── INSTALL.md                        # every install route, with troubleshooting
└── README.md
```

`reference/` holds documents that five pipeline skills share, and the canonical text of the section every skill carries. They are not skills, so they sit outside `skills/` rather than being forced into a directory that pretends otherwise.

### Conventions

- All skills use **UK English**.
- Every skill carries the standard `name` and `description`. Role and pipeline skills additionally use the repository's Claude-specific invocation and metadata fields. The PPoT practice keeps portable minimal frontmatter, adding only `metadata.model_tier` and `metadata.version`.
- Every skill also carries an `agents/openai.yaml` with its display name and short description for Codex. The 31 that set `disable-model-invocation: true` add `policy.allow_implicit_invocation: false` there, which is the same instruction in Codex's dialect; `ppot` deliberately omits it. `scripts/verify.sh` fails if the two ever disagree, so adding a skill means adding both.
- Keep skill bodies **under 500 lines**, per [Anthropic's authoring guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). Past that, move detail into that skill's `references/` and link to it with a stated trigger for when to read it.
- Every skill has a `## Works with` section naming who it takes work from and hands work to, drawn from [docs/workflows.md](./docs/workflows.md). When one changes, change the other end too; `scripts/check-handoffs.py` fails on a one-way link.
- Every skill carries two shared sections, `## Handing over work` and `## Model and sub-agents`, plus a `metadata.model_tier` and a `metadata.version`. Edit the sections only in `reference/handing-over-work.md` and `reference/model-and-sub-agents.md`, then run `python3 scripts/sync-shared-sections.py`; CI fails if a copy drifts or a skill has no tier or version.
- Every skill ends with `## Maintenance` listing its review triggers. Treat that as a versioning prompt: bump role and pipeline skill metadata when their behaviour changes, and bump the plugin version when the shared PPoT practice changes.

### Versioning

Semver, tagged `v<MAJOR>.<MINOR>.<PATCH>` on `main`.

- **MAJOR** — breaking change to a skill's contract or to installed paths.
- **MINOR** — new skill, new intent, new output type.
- **PATCH** — wording, clarifications, frontmatter fixes.

Consuming projects should pin to a tag and update deliberately.

**Tag every release.** After merging a version bump to `main`, run `git tag -a vX.Y.Z <merge commit> -m "<summary>"` and `git push origin vX.Y.Z`.
- The plugin's update reminder compares installed versions against these tags, so it can't see an untagged release.
- The submodule route pins to the newest tag when it installs.
- `scripts/verify.sh` fails if the plugin's version falls behind the newest tag.
- Versions 1.2 to 1.7 were never tagged. `v1.8.0` is the first tag after `v1.1.0`.

### Contributing

Issues and pull requests welcome.

- Follow the existing skill structure when adding one.
- Update [routing.md](./routing.md): a row in the relevant table, squad memberships if cross-functional, and an entry in the specialist-routing examples. **The table matters more than the prose** — see the routing findings above.
- Bump the skill's frontmatter `version` on behaviour-shaping changes.
- Tag a release after merge to `main`.

[↑ Back to contents](#contents)

## Licence

[MIT](./LICENSE). Use it, fork it, adapt it. Attribution appreciated but the licence only requires the copyright notice.

[↑ Back to contents](#contents)
