# Second Brain

> Your AI-powered Chief of Staff — captures, organizes, and farms context while you work

A git-tracked Obsidian vault powered by Claude Code. Natural language in, organized knowledge out. Hooks auto-commit every action, farmers pull context from Slack and meetings on a schedule, and delegation forks work to specialized AI employees across repos. Git is the database — every change is a timestamped, filterable commit.

---

## What It Does

- **Captures naturally** — Say "meeting with Sarah Friday about Q2 planning" and it creates linked person notes, tasks, and project files
- **Plans your day** — Aggregates due tasks, overdue items, and active projects into a daily plan
- **Farms context automatically** — Subagents read Slack, meeting transcripts, and other sources on a schedule, classifying what matters into your vault
- **Delegates work** — Forks terminal sessions to AI employees that work autonomously across repos
- **Tracks everything** — Every action auto-commits with `cos:` prefix for easy filtering

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **Claude Pro/Max** | [claude.ai](https://claude.ai) — subscription for Claude Code access |
| **Claude Code** | Anthropic's agentic CLI ([install below](#installation)) |
| **Obsidian** | Free markdown editor — [obsidian.md/download](https://obsidian.md/download) |
| **Git** | Pre-installed on macOS |

---

## Installation

### 1. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

On first run, Claude Code prompts you to authenticate with your Anthropic account.

> **Prefer a GUI?** Claude Code is also available as a [VS Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code), desktop app, and [web app](https://claude.ai/code).

### 2. Create Your Vault

1. Click **"Use this template"** → **"Create a new repository"** at the top of this repo
2. **Set visibility to Private** — your vault will contain personal data
3. Clone your new repo locally:

```bash
git clone https://github.com/YOUR-USERNAME/second-brain.git
cd second-brain
```

4. Open Obsidian → **"Open folder as vault"** → select the `second-brain` folder

### 3. Start

```bash
claude
```

Run the setup command:

```
/start-second-brain
```

This validates your repo is private, creates the vault folder structure, pushes to verify everything is connected, and walks you through context onboarding (role, writing style, business profile). Once complete, try:

```
/new remember to review quarterly report by Friday
/today
/history
```

---

## Commands

| Command | Purpose |
|---------|---------|
| `/new <text>` | Quick capture — classify and file natural language input |
| `/today` | Generate daily plan from due tasks and active projects |
| `/daily-review` | End of day — compare planned vs actual, update statuses |
| `/history` | Recent git activity (last 7 days) |
| `/farm <name>` | Trigger a context farmer (e.g., `/farm slack`) |
| `/create-farmer` | Build a new farmer or schedule an existing one |
| `/delegate <task>` | Fork terminal for autonomous work |

When you use `/new`, the system decomposes your input into entities (tasks, projects, people, ideas), extracts dates and tags, links them via `[[wiki-style]]` references, and writes files to the appropriate folders. If classification confidence is below 0.5, it asks for clarification.

---

## Context Farming

Context farmers are Claude Code subagents that read external sources via MCP and write relevant context into the vault automatically. Each farmer is defined in `.claude/agents/<name>-farmer.md` — the subagent file is both the config and the executor.

### How It Works

1. Reads `context/watchlists.md` for what to monitor
2. Checks state file for last run time — only processes the last 24 hours
3. Reads external source via MCP, classifies entities (task, project, person, idea)
4. Deduplicates against existing vault files
5. Pulls latest changes, writes files with `source: farmer/<name>` in frontmatter
6. `SubagentStop` hook auto-pushes commits when done

### Built-In Farmers

| Farmer | Source | What It Captures |
|--------|--------|-----------------|
| `slack` | Slack channels | Action items, decisions, blockers, people mentions |
| `fireflies` | Meeting transcripts | Action items, decisions, status updates, new contacts |

### Watchlists

Farmers are configured through `context/watchlists.md` — which channels to monitor, keyword signals (deadline, blocker, decision), people to track, meeting title patterns, and active project slugs for cross-referencing.

### Scheduling

| Mode | How |
|------|-----|
| **Cloud scheduled** | `/schedule` or [claude.ai/code/scheduled](https://claude.ai/code/scheduled) — runs 24/7 |
| **Desktop scheduled** | Desktop app > Schedule page — machine must be on |
| **Loop** | `/loop 30m /farm slack` — session-scoped polling |
| **Manual** | `/farm slack` — on-demand |

### Creating New Farmers

Run `/create-farmer` to build a farmer for any connected MCP (Gmail, Google Calendar, Firecrawl, etc.). It verifies the MCP connection, gathers your monitoring preferences, generates the subagent file, updates permissions and watchlists, and offers to schedule it.

---

## Delegation

> **Credit:** Based on [IndieDev Dan's](https://github.com/disler) [fork-repository-skill](https://github.com/disler/fork-repository-skill). Check out his [YouTube channel](https://www.youtube.com/@indydevdan) for more Claude Code content.

The `/delegate` command forks a new terminal window for autonomous work:

```
/delegate write the quarterly report based on project notes
```

A separate Claude instance spawns, works the task, updates the task file with output locations, and plays a notification sound when done.

### Cross-Repo Delegation

AI employees are separate Claude Code repos with specialized skills. Configure them in `.claude/reference/employees.json`:

```json
{
  "head-of-content": "~/Documents/GitHub/head-of-content"
}
```

Then delegate: `/delegate head-of-content: research YouTube content for AI productivity niche`

- **[Head of Content](https://github.com/bradautomates/head-of-content)** — Researches winning content across social platforms ([video](https://www.youtube.com/watch?v=sXGrFTe0ZfE))
- **[SEO Specialist](https://github.com/bradautomates/seo)** — SEO research and optimization ([video](https://www.youtube.com/watch?v=v7MvQvQO2kU))

---

## Under the Hood

### Hooks

Four hooks in `.claude/settings.json` automate the vault lifecycle:

| Hook | Trigger | Purpose |
|------|---------|---------|
| **Auto-Commit** | `PostToolUse` (Write/Edit) | Commits vault changes with `cos:` prefix, pulls then pushes |
| **Session Sync** | `SessionStart` | Pulls remote changes, recovers detached HEAD |
| **Subagent Push** | `SubagentStop` (`.*-farmer`) | Pushes commits after a farmer finishes |
| **Stop Sound** | `Stop` (if `CLAUDE_DELEGATED=1`) | Notification when delegated task completes |

### Git as Audit Trail

Every action generates a commit: `cos: <action> - <description>`

```bash
git log --since="8am" --grep="cos:" --oneline   # Today's activity
git log --grep="farmer/"                          # Farmer-only activity
git diff HEAD~1                                   # What changed last
git log -p tasks/my-task.md                       # File history
```

### File Formats

All files use YAML frontmatter. Four entity types:

| Type | Key Fields | Folder |
|------|------------|--------|
| **Task** | `type: task`, `due: YYYY-MM-DD`, `status: pending\|in-progress\|complete\|cancelled` | `tasks/` |
| **Project** | `type: project`, `status: active\|paused\|complete\|archived` | `projects/` |
| **Person** | `type: person`, `last-contact: YYYY-MM-DD` | `people/` |
| **Idea** | `type: idea` | `ideas/` |

Farmer-created files add `source: farmer/<name>` and `farmed: <timestamp>` to frontmatter.

Full templates: [`.claude/reference/file-formats.md`](.claude/reference/file-formats.md)

### Directory Structure

```
second-brain/
├── tasks/                  # Items with due dates
├── projects/               # Ongoing work
├── people/                 # Relationship notes
├── ideas/                  # Captured thoughts
├── context/                # LLM context, watchlists, farmer state
├── daily/                  # Daily plans (YYYY-MM-DD.md)
├── weekly/                 # Weekly summaries
├── outputs/                # Deliverables
└── .claude/
    ├── agents/             # Context farmer subagents
    ├── hooks/              # auto-commit, session-sync, subagent-push, stop-sound
    ├── skills/             # Slash command definitions
    └── reference/          # File format templates, employee config
```

---

## Troubleshooting

**Auto-commit not working** — Check that `.claude/settings.json` allows `Bash(git add:*)` and `Bash(git commit:*)`. Verify hook is executable: `chmod +x .claude/hooks/auto-commit.sh`. Confirm the file is in a tracked directory.

**Tasks not appearing in /today** — Ensure `due: YYYY-MM-DD` in frontmatter with exact ISO format. File must be in `tasks/`.

**Classification asking too many questions** — Be more specific: "task: call John by Friday" instead of "John Friday".

---

## Design Philosophy

1. **Git is the database** — No separate storage, just markdown and commits
2. **Natural language first** — Say what you mean, let classification handle the rest
3. **Auto-commit everything** — Hooks ensure nothing is lost
4. **Farm, don't fetch** — Context comes to you on a schedule
5. **Cross-repo awareness** — Delegation maintains context across projects

---

## License

MIT License — Feel free to modify and distribute.

---

## Implement AI in Your Business

Learn how to implement AI tools and workflows that actually move the needle for your business on [YouTube](https://www.youtube.com/@bradbonanno).

Join the [Enterprise Skills Marketplace](https://brad-b.kit.com/f9a7349a1c) waiting list.

Connect on [LinkedIn](https://www.linkedin.com/in/bradbonanno/).
