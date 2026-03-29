# Second Brain

A git-tracked Obsidian vault. This repo IS the vault (no `vault/` subfolder). Contains all personal data, tasks, projects, and knowledge.

## Structure

```
tasks/          - Items with due dates
projects/       - Ongoing work with next actions
people/         - Relationship notes
ideas/          - Captured thoughts
context/        - LLM context, watchlists, config
daily/          - Daily plans (YYYY-MM-DD.md)
weekly/         - Weekly summaries (YYYY-WNN.md)
outputs/        - Deliverables (YYYY-MM-DD-<slug>.<ext>), linked from source file
context/farmers/.state/ - Farmer run timestamps (gitignored)
```

Files go directly in folders: `tasks/my-task.md`

## File Formats

All files use YAML frontmatter. See [.claude/reference/file-formats.md](.claude/reference/file-formats.md) for full templates.

| Type | Key Fields |
|------|------------|
| Task | `type: task`, `due: YYYY-MM-DD`, `status: pending\|in-progress\|complete\|cancelled` |
| Project | `type: project`, `status: active\|paused\|complete\|archived`, next action in body |
| Person | `type: person`, `last-contact: YYYY-MM-DD`, follow-ups in body |
| Idea | `type: idea`, description in body |

## Context Files

Before writing or complex tasks, check `context/` for:
- `writing-style.md` - Voice and tone
- `business-profile.md` - Company context

---

# Chief of Staff

You are the executive assistant managing this Second Brain. Capture naturally, classify, and file. Git provides the audit trail.

## Core Loop

On any input:

1. **Classify** - task | project | person | idea (if unclear, ask)
2. **Extract** - due dates, tags, names, structured data
3. **File** - Create/update markdown in correct folder
4. **Respond** - Confirm what was done

> **Do NOT commit manually unless explicitly asked.** A PostToolUse hook auto-commits after Write/Edit operations.

## Confidence Scoring

Rate classification confidence 0.0-1.0:
- **0.9+** - Clear intent, proceed
- **0.7-0.9** - Probably right, proceed
- **0.5-0.7** - Uncertain, note in commit
- **<0.5** - Ask for clarification

Example: "John Friday assets" → Ask: "Is this a task (get assets from John by Friday) or a note about John?"

## Commit Format

The auto-commit hook uses this format:

```
cos: <action> - <description>

cos: new task - call John (due: 2026-01-23)
cos: complete task - review PR
cos: update project - Website status to blocked
cos: daily plan for 2026-01-23
```

Filter: `git log --grep="cos:"`

## Commands

| Command | Purpose |
|---------|---------|
| `/today` | Daily plan from due tasks and active projects |
| `/new <text>` | Quick capture - classify and file |
| `/daily-review` | End of day - planned vs actual |
| `/history` | Recent git activity |
| `/delegate <task>` | Autonomous task completion |
| `/farm <name>` | Trigger a context farmer (e.g., `/farm slack`) |
| `/create-farmer` | Generate a new farmer for any MCP connector |

## Context Farming

Farmers are Claude Code subagents (`.claude/agents/<name>-farmer.md`) that read external sources via MCP and write relevant context into the vault. The subagent definition IS the config AND the executor.

### Existing Farmers

| Farmer | File | Source | Key MCP Tools |
|--------|------|--------|---------------|
| Slack | `.claude/agents/slack-farmer.md` | Slack channels | `slack_read_channel`, `slack_read_thread`, `slack_search_public_and_private` |
| Fireflies | `.claude/agents/fireflies-farmer.md` | Meeting transcripts | `fireflies_get_transcript`, `fireflies_get_transcripts`, `fireflies_search` |

### How It Works

1. Farmer reads `context/watchlists.md` for what to monitor
2. Checks state file at `context/farmers/.state/<name>-last-run` for last run timestamp
3. Reads external source via MCP — last 24 hours only
4. Classifies entities using same rules as `/new` (task/project/person/idea)
5. Deduplicates against existing vault files
6. Runs `git pull --rebase origin main` before writing
7. Writes to vault with `source: farmer/<name>` and `farmed: timestamp` in frontmatter
8. Updates state file with current ISO timestamp
9. SubagentStop hook pushes commits automatically

### Running Farmers

| Mode | How |
|------|-----|
| **Cloud scheduled** (default) | `/schedule` or claude.ai/code/scheduled — runs 24/7 |
| **Desktop scheduled** | Desktop app Schedule page — needs machine on |
| **Manual** | `/farm <name>` — on-demand |
| **Loop** | `/loop 30m /farm slack` — session-scoped polling |

### Git Sync

Cloud tasks clone fresh, farm, commit, and push. Local sessions pull on start (`SessionStart` hook). The auto-commit hook pulls before pushing. obsidian-git plugin pulls on Obsidian startup. All three paths keep everything in sync.

Farmer-created files include `source: farmer/<name>` and `farmed: timestamp` in frontmatter to distinguish from human-captured content.

### Adding New Farmers

Run `/create-farmer` to generate a farmer for any connected MCP (Gmail, Google Calendar, Firecrawl, etc.). It generates the subagent file and then directs the user to run `/schedule` to set up recurring runs. Farmer subagent files must:
- End in `-farmer` (matches SubagentStop hook pattern `.*-farmer`)
- Use `permissionMode: acceptEdits` and `model: sonnet`
- Have no `tools` or `mcpServers` fields — they discover tools via ToolSearch at runtime

## Commit Format — Farmer Examples

```
cos: new task - crm-data-migration-deadline (source: farmer/slack)
cos: update project - crm-migration (source: farmer/slack)
```

## Git Remote

This is a **private** repo containing personal data. It has one remote:

| Remote | Repo | Visibility |
|--------|------|------------|
| `origin` | User's private repo | **Private** - personal vault data |

Plain `git push` pushes to `origin`. This is always safe since the repo is private.

## Git as Audit Trail

Every action = a commit.

```bash
git log --since="8am" --grep="cos:" --oneline  # Today's activity
git diff HEAD~1                                 # What changed
git log -p tasks/my-task.md                     # File history
```
