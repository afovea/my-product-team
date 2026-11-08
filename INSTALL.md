# How to install

Three ways in, all fully supported. Every one is written out click by click —
none of them assume you write code.

| You are using | Time | Go to |
|---|---|---|
| **Claude Code in the desktop app** — no terminal, all 32 skills at once | 3 min | **[Part 2](#part-2--claude-code-in-the-desktop-app)** |
| **Claude Code in a terminal** — same result, typed commands | 3 min | **[Part 3](#part-3--claude-code-in-a-terminal)** |
| **Claude for chatting** — browser or the app's Chat tab | 5 min | **[Part 4](#part-4--claude-for-chatting-browser-or-chat-tab)** |

Not sure which you have? **[Part 1](#part-1--which-claude-do-you-have)** tells
you from what is on your screen.

---

## What you are installing

The suite contains 23 expert personas, eight delivery-pipeline skills, and a
Project Point of Truth practice. You can ask Claude to work as a product manager,
UX researcher, or accessibility specialist, run a coding task through the
pipeline, or use the PPoT to preserve durable project knowledge.

There is also a **delivery pipeline** for running coding tasks step by step, and
a **routing brain** that picks the right expert for you. Both are optional and
both are covered below.

---

## Part 1 — which Claude do you have?

Look at your screen.

**Claude Code, desktop app.** You have the Claude app open and there are tabs
along the top — **Chat**, **Cowork**, **Code**. You are on **Code**, and it asked
you to pick a folder when you started.
→ **[Part 2](#part-2--claude-code-in-the-desktop-app)**

**Claude Code, terminal.** A window with a blinking cursor where you type
commands, and you started it by typing `claude`.
→ **[Part 3](#part-3--claude-code-in-a-terminal)**

**Claude web.** A web browser with `claude.ai` in the address bar. A message box
and your past conversations down the side.
→ **[Part 4](#part-4--claude-for-chatting-browser-or-chat-tab)**

**Claude app, Chat tab.** The Claude app, on **Chat** rather than **Code**. Same
product as Claude web, and your skills are shared between the two — install in
one and it appears in the other.
→ **[Part 4](#part-4--claude-for-chatting-browser-or-chat-tab)** *(the menus
differ slightly; both are written out)*

These instructions assume Claude is already installed and you are signed in.

---

## Part 2 — Claude Code in the desktop app

No terminal. This installs all 32 skills in one go.

### Step 1 · Open the Code tab

Open the Claude app and click the **Code** tab. It asks you to pick a **project
folder** before you can send a message.

**Pick anything. It does not matter.** You are not setting up a project — Claude
Code just always works somewhere, so it needs a folder to point at. Your
Documents folder is fine. So is a new empty folder on your Desktop.

The install goes onto your account, not into that folder: the roles then work in
**every** folder you ever open, and nothing is written into the one you picked.

> The one exception is the optional [routing brain](#part-5--optional--let-claude-pick-the-expert),
> which is per-folder by design. Everything else here is machine-wide.

### Step 2 · Type two lines

Click into the message box at the bottom: the same one you would type a question
into. Type this and press Enter:

```
/plugin marketplace add afovea/my-product-team
```

Wait for it to say **Successfully added marketplace: productteam-skills**. Then
type this and press Enter:

```
/plugin install product-team@productteam-skills
```

> **Copy those two lines exactly.** Three names are involved: `my-product-team`
> is the GitHub repository, `productteam-skills` is the marketplace it adds, and
> `product-team` is the plugin you install.

**No luck typing `/plugin` in the app?** Click the **+** next to the message box
and choose **Add plugins** (or **Plugins**, then **Browse plugins**). Find
**product-team** and continue at Step 3. If it isn't listed, the marketplace
hasn't been added yet: run the first line once from a terminal instead
([Part 3](#part-3--claude-code-in-a-terminal)). The app and the terminal share
your plugins, so installing in one installs in both.

### Step 3 · Choose who it is for

The install line doesn't install straight away. It opens a panel showing what the
plugin adds: 32 skills and two hooks. Choose:

- **Install for you (user scope)**: every folder you open. Pick this one.
- *Install for all collaborators on this repository*, or *Install for you, in
  this repo only*: for one project. See [Advanced routes](#advanced-routes).

Then read the last line it prints:

- **Plugin is now active.** Finished. Go to Step 4.
- **Run /reload-plugins to apply.** Claude Code usually runs it for you. If it
  warns that reloading costs a little extra, type `/reload-plugins --force`.

### Step 4 · Check it worked

Type `/product-team:` in the message box and stop. A list drops down with all 32
roles, such as `/product-team:product-manager`. If that list appears, you are
installed.

### Step 5 · Use it

Type the role's full name, then **write the task on the same line** before
pressing Enter:

```
/product-team:product-manager Turn this vague feature request into a delivery-ready ticket.
```

```
/product-team:product-designer Our reports page is blank for new users. Design the empty state.
```

```
/product-team:accessibility-specialist This chart uses colour alone for four series. Problem?
```

The full name always works. The short form, `/product-manager`, works too, but
only while nothing else uses that name. Another copy of the roles takes it, such
as skills you uploaded to claude.ai or an `install.sh` copy: see
[Two copies of every role](#two-copies-of-every-role-or-a-role-starts-on-its-own).

A role with no task attached will just ask what you want, so give it the work in
the same message.

**Optional:** [Part 5](#part-5--optional--let-claude-pick-the-expert) adds a
routing brain that names the right expert when you describe a problem in plain
words.

---

## Part 3 — Claude Code in a terminal

Exactly the same result as Part 2. Use this if you prefer the terminal or do not
have the desktop app.

### Step 1 · Start Claude Code

Open a terminal:

- **Mac** — press `Cmd + Space`, type `Terminal`, press Enter.
- **Windows** — press Start, type `Terminal`, press Enter.
- **Linux** — press `Ctrl + Alt + T`.

Type this and press Enter:

```bash
claude
```

That is all. **You do not need to be in any particular folder** — a terminal is
always sitting in one already (your home folder, when you have just opened it),
and that is good enough to install from. The install goes onto your account, so
the roles then work everywhere and nothing is written into wherever you happened
to be.

<details>
<summary><b>Starting Claude Code in a specific folder, for later</b></summary>

Once you are actually using Claude Code on real files, you will want it pointed
at those files. Use `cd` — "change directory" — before starting it:

```bash
cd ~/Desktop
claude
```

`~` means your home folder, so `~/Desktop` is your Desktop.

To get a folder's path without typing it: on a Mac, type `cd ` (with the space)
then drag the folder onto the terminal window and the path fills itself in. On
Windows, right-click the folder and choose **Copy as path**, then paste.

</details>

> `claude: command not found`? This terminal cannot see Claude Code. If you have
> the desktop app, use [Part 2](#part-2--claude-code-in-the-desktop-app) instead
> — the app does not add a `claude` command to your terminal.

### Step 2 · Type two lines

You are now inside Claude Code — the prompt has changed. These go into Claude,
not into the terminal:

```
/plugin marketplace add afovea/my-product-team
```

```
/plugin install product-team@productteam-skills
```

Or do it without starting Claude Code, as ordinary terminal commands. This
installs for you in every folder (user scope), with no panel to answer:

```bash
claude plugin marketplace add afovea/my-product-team
claude plugin install product-team@productteam-skills
```

Then start `claude` and carry on at Step 4.

### Step 3, 4 and 5

Identical to Part 2: [choose who it is for](#step-3--choose-who-it-is-for),
[check it worked](#step-4--check-it-worked), [use it](#step-5--use-it).

---

## Part 4 — Claude for chatting (browser or Chat tab)

For Claude in a web browser, and the desktop app's **Chat** tab. No terminal, and
it works on the free plan.

Here you download a file for each role you want and upload it into Claude.

### Step 1 · Turn on code execution

Skills do not run without it. This is the most common reason an install "does
nothing". It works on every plan, the free one included.

1. Click your **name or profile picture**, usually bottom-left.
2. Click **Settings**, then **Capabilities**.
3. Switch on **Code execution and file creation**. In the newer settings layout
   it is called **Create and edit files**.

> **On a Team or Enterprise plan?** An owner of your organisation has to allow
> skills first, in **Organization settings → Plugins & skills**. If you can't
> find the switch, or uploads are refused, ask them.

### Step 2 · Download the roles you want

Each is one small file. **Click a link and it downloads.** Nothing opens.

**Suggested starting set** — click all six:

| Role | What it does |
|---|---|
| [product-designer.zip](https://github.com/afovea/my-product-team/raw/main/download/product-designer.zip) | UX, UI, flows, interaction design, design QA |
| [content-designer.zip](https://github.com/afovea/my-product-team/raw/main/download/content-designer.zip) | Wording, labels, error messages, onboarding copy |
| [accessibility-specialist.zip](https://github.com/afovea/my-product-team/raw/main/download/accessibility-specialist.zip) | WCAG review, inclusive design, contrast, screen readers |
| [ux-researcher.zip](https://github.com/afovea/my-product-team/raw/main/download/ux-researcher.zip) | Research planning, interviews, synthesis |
| [product-manager.zip](https://github.com/afovea/my-product-team/raw/main/download/product-manager.zip) | Scope, priorities, outcomes, PRDs, tickets |
| [ppot.zip](https://github.com/afovea/my-product-team/raw/main/download/ppot.zip) | Project briefings, decisions, assumptions, durable learning, and knowledge review |

<details>
<summary><b>All 32 — click to see the full list</b></summary>

**Shared project knowledge**
[ppot](https://github.com/afovea/my-product-team/raw/main/download/ppot.zip)

**Product and strategy**
[product-manager](https://github.com/afovea/my-product-team/raw/main/download/product-manager.zip) ·
[product-strategist](https://github.com/afovea/my-product-team/raw/main/download/product-strategist.zip) ·
[growth-product-marketing-manager](https://github.com/afovea/my-product-team/raw/main/download/growth-product-marketing-manager.zip) ·
[pricing-strategist](https://github.com/afovea/my-product-team/raw/main/download/pricing-strategist.zip) ·
[brand-guardian](https://github.com/afovea/my-product-team/raw/main/download/brand-guardian.zip)

**Research, insight and data**
[ux-researcher](https://github.com/afovea/my-product-team/raw/main/download/ux-researcher.zip) ·
[data-analyst](https://github.com/afovea/my-product-team/raw/main/download/data-analyst.zip) ·
[customer-success](https://github.com/afovea/my-product-team/raw/main/download/customer-success.zip) ·
[storm-researcher](https://github.com/afovea/my-product-team/raw/main/download/storm-researcher.zip) ·
[research-tool-builder](https://github.com/afovea/my-product-team/raw/main/download/research-tool-builder.zip) ·
[research-reporter](https://github.com/afovea/my-product-team/raw/main/download/research-reporter.zip)

**Design and experience**
[product-designer](https://github.com/afovea/my-product-team/raw/main/download/product-designer.zip) ·
[content-designer](https://github.com/afovea/my-product-team/raw/main/download/content-designer.zip) ·
[design-systems-specialist](https://github.com/afovea/my-product-team/raw/main/download/design-systems-specialist.zip) ·
[motion-designer](https://github.com/afovea/my-product-team/raw/main/download/motion-designer.zip) ·
[motion-graphics-designer](https://github.com/afovea/my-product-team/raw/main/download/motion-graphics-designer.zip) ·
[accessibility-specialist](https://github.com/afovea/my-product-team/raw/main/download/accessibility-specialist.zip)

**Engineering, delivery and quality**
[software-engineer](https://github.com/afovea/my-product-team/raw/main/download/software-engineer.zip) ·
[technical-architect](https://github.com/afovea/my-product-team/raw/main/download/technical-architect.zip) ·
[devops-engineer](https://github.com/afovea/my-product-team/raw/main/download/devops-engineer.zip) ·
[security-specialist](https://github.com/afovea/my-product-team/raw/main/download/security-specialist.zip) ·
[qa-engineer](https://github.com/afovea/my-product-team/raw/main/download/qa-engineer.zip) ·
[delivery-manager](https://github.com/afovea/my-product-team/raw/main/download/delivery-manager.zip)

**Delivery pipeline** — for running coding tasks step by step. These are built
for Claude Code and do much less in chat.
[run-pipeline](https://github.com/afovea/my-product-team/raw/main/download/run-pipeline.zip) ·
[requirements-generator](https://github.com/afovea/my-product-team/raw/main/download/requirements-generator.zip) ·
[shape-task](https://github.com/afovea/my-product-team/raw/main/download/shape-task.zip) ·
[execute-chunk](https://github.com/afovea/my-product-team/raw/main/download/execute-chunk.zip) ·
[close-chunk](https://github.com/afovea/my-product-team/raw/main/download/close-chunk.zip) ·
[cleanup-verify](https://github.com/afovea/my-product-team/raw/main/download/cleanup-verify.zip) ·
[diagnose](https://github.com/afovea/my-product-team/raw/main/download/diagnose.zip) ·
[design-critique](https://github.com/afovea/my-product-team/raw/main/download/design-critique.zip)

</details>

> **Do not unzip these.** Claude wants the `.zip` exactly as downloaded. If your
> Mac unzipped it for you, see
> [My Mac unzipped the file](#my-mac-unzipped-the-file-automatically).

### Step 3 · Upload them

About fifteen seconds each, and the same in the browser and the app:

1. Click **Customize** in the left sidebar, then **Skills**.
2. Click **+**, then **Create skill**, then **Upload a skill**.
3. Pick one of the `.zip` files you downloaded. Claude shows its name and
   description.
4. Make sure its toggle is **on**.

Repeat for each file.

You only need to do this once. Uploads attach to your account, so they appear in
the browser, the app's Chat tab, Cowork and Claude Code cloud sessions. They also
appear in Claude Code on your computer when you're signed in with the same
account. If you also install the plugin there, you'll have two copies of each
role: see [Two copies of every role](#two-copies-of-every-role-or-a-role-starts-on-its-own).

### Step 4 · Check it worked

Your Skills list should show what you uploaded, each switched **on**.

### Step 5 · Use it

Start a new chat and **say which expert you want**, in ordinary words:

> As a product designer, our reports page is blank for new users. Design the
> empty state.

> Acting as an accessibility specialist, this chart uses colour alone to tell
> four lines apart. Is that a problem?

There are no slash commands here. Naming the role in your sentence is what brings
that expert in — and giving it the actual task in the same message is what gets
you work rather than a question back.

---

## Part 5 — optional · let Claude pick the expert

**Claude Code only** (Parts 2 and 3). Adds a decision layer so you can describe a
problem in plain words and Claude works out which role it belongs to:

> "The error message when a payment fails is confusing. Rewrite it."
> → Content Designer

> "This chart tells four lines apart by colour alone."
> → Accessibility Specialist

It also defines six cross-functional squads, for questions like "is this ready to
ship?" that are not one discipline's call.

This lives in a file called `CLAUDE.md` inside your project folder, so it applies
per folder rather than everywhere.

**What it can and can't do with the plugin.** The roles never start on their own;
that's deliberate, because automatic selection picks badly. So with the plugin,
the routing brain **names** the right role and gives you its command, for example
`/product-team:content-designer`, and you run it. If you want Claude to work as the
role without that step, use a project install instead
([Advanced routes](#advanced-routes)): the skill files are then in the project,
and Claude reads and follows the right one itself.

**The easy way — ask Claude Code to do it.** Paste this into Claude Code:

```
Read https://raw.githubusercontent.com/afovea/my-product-team/main/routing.md
and append it to this folder's CLAUDE.md, creating that file if it does not
exist. Wrap it in the comment markers <!-- product-team-skills:start --> and
<!-- product-team-skills:end -->. In the role tables, replace the "Skill file"
column with each role's plugin command, e.g. `/product-team:product-manager`.
The roles only start when I run them, so when one fits, name it and give me
its command.
```

Then start a new session so it is picked up.

That only writes `CLAUDE.md`. It does not copy any skills, because you already
have them from the plugin. A second copy on disk would take the short names and
then quietly go out of date.

<details>
<summary><b>Doing it from a terminal instead — needs git</b></summary>

Identical result, done the same way every time. This is the only step in this
guide that needs `git` installed; the paste-in method above does not.

```bash
git clone https://github.com/afovea/my-product-team.git
cd my-product-team
./install.sh --routing-only /path/to/your/folder
```

</details>

---

## Part 6 — Codex, and other hosts that read `SKILL.md`

The skills are plain markdown following the [Agent Skills](https://agentskills.io)
standard, so they are not Claude's alone. Codex reads them, and so does anything
else built on the same standard. Two differences from Parts 2 and 3, both small:

- they live in **`.agents/skills/`**, not `.claude/skills/`
- you invoke one with **`$product-manager`**, not `/product-manager`

### The whole suite, in one command

```bash
git clone https://github.com/afovea/my-product-team.git
cd my-product-team
./install.sh --agents --personal
```

That puts all 32 skills in `~/.agents/skills/`, where Codex finds them in every
project. Start Codex and type `$product-` — the roles should autocomplete.

For one project instead, and to get the routing brain with it:

```bash
./install.sh --agents /path/to/your/project
```

That writes the skills to `<project>/.agents/skills/`, appends the routing brain
to the project's `AGENTS.md`, and seeds the pipeline adapter. `--agents` works
with every mode in [Advanced routes](#advanced-routes) below, including
`--routing-only` and `--submodule`.

### Committing them to a repository

`.agents/skills/` is a location Codex scans in the repository itself, so a team
can commit the skills and everyone gets them without installing anything:

```bash
./install.sh --agents /path/to/your/repo
```

then commit `.agents/`. Note that `install.sh` adds `.agents/` to `.gitignore` by
default, on the assumption it is a personal install — delete that line first if
you want the suite tracked.

### What you get

Everything Claude Code gets, including gate enforcement: the `Stop` hook that
refuses to end a turn while a project's checks are failing works on both hosts,
because both use the same event contract.

The one thing to know is that the roles do **not** fire on their own. That is
deliberate — automatic selection by keyword picks badly, so `$name` is how you
choose. The exception is `$ppot`, whose natural-language phrases are its intended
interface. See [Invoking a skill](./README.md#use-the-skills).

---

## Part 7 — Claude Code cloud sessions

For Claude Code on the web (`claude.ai/code`), and cloud sessions started from
the app or the terminal. A cloud session starts from a fresh copy of your
repository. It **doesn't** load plugins: not the ones on your computer, and not
ones a repository's `.claude/settings.json` switches on. Two things do reach it:

- **Skills committed to the repository.** Run a project install and commit the
  result, and everyone's cloud sessions on that repository get the roles and the
  routing brain:

  ```bash
  git clone https://github.com/afovea/my-product-team.git
  cd my-product-team
  ./install.sh /path/to/your/repo
  ```

  Then, in your repository, commit `.claude/skills/`, `.claude/reference/` and
  `CLAUDE.md`. `install.sh` adds `.claude/skills/` to `.gitignore` on the
  assumption that the install is personal, so remove that line first.
- **Skills switched on in claude.ai** ([Part 4](#part-4--claude-for-chatting-browser-or-chat-tab)).
  They load in your own cloud sessions, for you alone.

Gate enforcement needs the hook, and a project install doesn't add it, so in
cloud sessions the pipeline reports a failing gate but can't stop on one.

`./install.sh --verify` run against the repository says whether its skills are
committed.

---

## Keeping it up to date

Each release is tagged on GitHub as `vX.Y.Z`, and the [tags page](https://github.com/afovea/my-product-team/tags) lists them all. Each skill's own version is in the `metadata` of its `SKILL.md`. How you update depends on how you installed:

| You installed with | To update |
|---|---|
| The plugin (desktop app or terminal, Parts 2 and 3) | Type `/plugin`, open the **Installed** tab, select **product-team** and choose **Update now**. Or, in a terminal: `claude plugin update product-team@productteam-skills`. Start a new session, or type `/reload-plugins`, to load the new version. Updates are off by default for marketplaces outside Anthropic's: to make them automatic, open `/plugin`, go to the **Marketplaces** tab, select **productteam-skills** and choose **Enable auto-update** |
| ZIPs uploaded to claude.ai or the Chat tab (Part 4) | Download the skills that changed from [`download/`](./download) and upload them again, replacing the old ones. Nothing updates on its own |
| `install.sh` for Codex, a project, your personal folder, or routing only (Parts 5 and 6) | Get the latest copy of this repository (`git pull` in your clone), then run the same `install.sh` command again. `./install.sh --verify` shows what is installed afterwards |
| A submodule | In your project, `git -C .claude/skills-vendor fetch --tags`, then `git -C .claude/skills-vendor checkout vX.Y.Z` with the new tag. Run `./install.sh --submodule` again so skills added since are linked in, then commit the change |

**Installed before the repository was renamed?** If `claude plugin marketplace
list` shows the source as `afovea/product-team-skills` or
`afovea/ProductTeam-skills`, it still works, because GitHub redirects renamed
repositories, but point it at the current name when you next update. See
[Migrating from the old repo](./README.md#migrating-from-the-old-repo).

**The update reminder.** If you installed the plugin in Claude Code, it checks once a day, when a session starts, whether a newer release has been tagged. When one has, it shows one line naming the new version and how to update.
- It reads only the release tags from GitHub, and changes nothing.
- It stays silent when you're up to date, when you're offline, and in CI.
- To turn it off, set `PRODUCT_TEAM_NO_UPDATE_CHECK=1` in your environment.

---

## Something went wrong

### `Plugin "product-team" not found in marketplace "my-product-team"`

You typed the repository's name where the marketplace's name goes. The second
line is:

```
/plugin install product-team@productteam-skills
```

### `Marketplace "productteam-skills" not found`

The first line did not run, or did not finish. Run it, wait for **Successfully
added marketplace: productteam-skills**, then run the second.

### Typing `/plugin` does nothing in the app

Use the **+** button next to the message box instead: **Add plugins**, or
**Plugins** then **Browse plugins**. If **product-team** isn't listed there, add
the marketplace once from a terminal ([Part 3](#part-3--claude-code-in-a-terminal)).
The app and the terminal share your plugins.

### I installed it but the roles are not in the list

In order:

1. Are you typing the full name? Plugin roles are listed as
   `/product-team:product-manager`. Type `/product-team:` to see them all.
2. Did the install panel finish? Type `/plugin` and check the **Installed** tab
   lists **product-team** as enabled. If not, run Step 2 again and
   [choose a scope](#step-3--choose-who-it-is-for).
3. Type `/reload-plugins`, then `/reload-plugins --force` if it warns you, or
   start a new session.
4. Still missing? Open the **Errors** tab in `/plugin`, or run
   `claude plugin list` in a terminal.

### `/product-manager` runs the wrong thing, or nothing

The short name belongs to whichever skill claimed it first. Use the full name,
`/product-team:product-manager`, which always reaches the plugin. If you have
another copy of the roles, see below.

### Two copies of every role, or a role starts on its own

You have the roles from two places. Usually it's skills you uploaded to claude.ai
([Part 4](#part-4--claude-for-chatting-browser-or-chat-tab)), which also appear in
Claude Code when you're signed in with that account. Those copies are built for
chat, so Claude may pick one on its own, while the plugin's copies wait until you
run them.

Use the full plugin names, or keep one copy. To stop the uploaded ones appearing
in Claude Code, switch them off in claude.ai (**Customize → Skills**), or switch
them off in Claude Code from the **Installed** tab of `/plugin`, where they're
listed with `synced` as their source. A personal or project `install.sh` copy is
a third possible source: `./install.sh --verify` lists every copy it can find.

### It works, but behaves like an older version

Check what you have: run `claude plugin list` in a terminal, or open the
**Installed** tab in `/plugin`. Compare the version with the newest on the
[tags page](https://github.com/afovea/my-product-team/tags), then
[update](#keeping-it-up-to-date).

### Codex does not list the skills after installing them

Codex reads its skill directories when a session starts, so a session that was
already open will not see them. Quit and restart Codex, then type `$product-`.

If they are still missing, check they landed in the right place — it is
`.agents/skills/`, not `.codex/skills/`:

```bash
ls ~/.agents/skills/ | head
```

Nothing there means the install went to the Claude layout. Re-run it with
`--agents`. `./install.sh --verify` reports both layouts and will tell you which
one you actually have.

### A role fires on its own in Codex when it should not

Every role is meant to wait until you type `$name`. If one is answering
unprompted, its `agents/openai.yaml` is missing or was not copied — that file is
what carries `allow_implicit_invocation: false` to Codex. Re-run the install to
replace it:

```bash
./install.sh --agents --personal
```

`$ppot` is the deliberate exception and is supposed to respond to phrases like
"bring me up to speed".

### `claude: command not found`

You typed a Claude Code command somewhere that is not Claude Code, or Claude Code
is not installed on this computer.

The desktop app does **not** give you a `claude` terminal command. If you are
following Part 2, everything goes into Claude's own message box.

### I uploaded a skill in chat and nothing is different

1. **Is code execution on?** [Part 4 Step 1](#step-1--turn-on-code-execution). On a Team or Enterprise plan, an owner also has to allow skills.
   Most common cause. Switch them on and start a **new** chat.
2. **Is the skill toggled on?** Uploading does not always switch it on.
3. **Did you start the chat before installing?** Start a new one.
4. **Did you name the role in your message?** In chat, Claude picks the expert
   from what you wrote.

### My Mac unzipped the file automatically

Safari does this by default, leaving a folder instead of a `.zip`.

- **Quick fix:** right-click the folder → **Compress**. That makes a fresh `.zip`
  with the folder inside, which is the shape Claude wants.
- **Permanent fix:** Safari → Settings → General → untick **Open "safe" files
  after downloading**, then download again.
- Or use Chrome or Firefox, which do not unzip downloads.

### The upload was rejected or Claude says the file is invalid

Almost always an unzipped or re-zipped file — see above.

### I cannot find Customize, or Skills, or Capabilities

Menu names move between versions. Try in order: **Customize** in the sidebar ·
**Settings → Capabilities** · **Settings → Features** · profile picture →
**Settings**. You want a page listing skills with on/off switches.

### Claude keeps picking the wrong expert

**In chat:** say which one you want — "answer this as an accessibility
specialist, not a product designer". Uploading fewer roles improves its aim.

**In Claude Code:** it never picks on its own. Run the role by its full name, or
add [Part 5](#part-5--optional--let-claude-pick-the-expert) to have Claude name
the right one for you. If a role does start on its own, it's a copy uploaded to
claude.ai: see [Two copies of every role](#two-copies-of-every-role-or-a-role-starts-on-its-own).

### Nothing here matches

Open an issue at
[github.com/afovea/my-product-team/issues](https://github.com/afovea/my-product-team/issues).
Say which Claude you are using, what you clicked, and what you saw. Screenshots
help.

---

## Which route gives you what

| | The 32 skills | Delivery pipeline | Routing brain | Gate enforcement |
|---|---|---|---|---|
| Claude Code, desktop app or terminal (plugin) | ✅ all at once | ✅ | names the role, via [Part 5](#part-5--optional--let-claude-pick-the-expert) | ✅ |
| Claude Code, a project install | ✅ all at once | ✅ | ✅ follows the role itself | ❌ the hook comes with the plugin |
| Claude Code cloud sessions | ✅ committed, or switched on in claude.ai, via [Part 7](#part-7--claude-code-cloud-sessions) | ✅ | ✅ when committed | ❌ |
| Codex, and other `SKILL.md` hosts | ✅ all at once via [Part 6](#part-6--codex-and-other-hosts-that-read-skillmd) | ✅ | ✅ into `AGENTS.md` | ✅ on Codex |
| Claude for chatting | ✅ the ones you upload | partly, built for Claude Code | ❌ | ❌ |

**Gate enforcement** stops the agent ending a turn while a project's checks are
failing. It only applies to coding work, and needs a host with hooks — Claude
Code and Codex both have them; chat does not.

---

## Advanced routes

For teams and repositories. The [README](./README.md) has the detail.

| Route | Command | Adds |
|---|---|---|
| Plugin for a whole repository | `/plugin install product-team@productteam-skills`, then **Install for all collaborators on this repository** | switches the plugin on in the repository's committed `.claude/settings.json`. Each collaborator still runs the two install lines once, and cloud sessions don't load it |
| Cloud sessions | `./install.sh /path/to/repo`, then commit | the skills and routing brain in the repository, for every cloud session on it ([Part 7](#part-7--claude-code-cloud-sessions)) |
| Project | `./install.sh /path/to/project` | 32 skills on disk + the routing brain |
| Personal | `./install.sh --personal` | 32 skills on disk, every project |
| Routing only | `./install.sh --routing-only /path` | the routing brain, nothing else |
| Submodule | `./install.sh --submodule /path` | pinned to a tag, symlinked |
| Any of the above, for Codex | add `--agents` | the same, written to `.agents/skills/` and `AGENTS.md` |

`./install.sh --verify` reports every install it can find and flags conflicts.
Run it first if you are unsure what state you are in.

The ZIPs under `download/` are built by `scripts/package-skills.sh` and checked
by CI on every push, so they cannot drift from `skills/`. They differ from the
source in one way: `disable-model-invocation: true` is stripped, because chat has
no `/name` invocation and would otherwise ship skills that could never fire.
