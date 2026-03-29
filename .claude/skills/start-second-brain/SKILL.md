---
name: start-second-brain
description: Initialize a new Second Brain vault from a template repo — validate privacy, create folders, push, and onboard the user.
---

# Start Second Brain

Set up a Second Brain vault after the user has created their repo from the GitHub template.

## Usage

Run from the vault's root directory:

```bash
python3 .claude/skills/start-second-brain/scripts/init_vault.py
```

## Phase 1: Init Script

The script handles mechanical setup:

1. **Privacy check** — uses `gh repo view` to verify the repo is private. Exits with an error if public. Warns if it can't determine visibility.
2. **Creates vault folders** — tasks, projects, people, ideas, context, daily, weekly, outputs (git doesn't track empty dirs, so these won't exist from the template)
3. **Creates template files** — `.gitignore`, `context/_index.md`, `context/watchlists.md` (skips if they already exist)
4. **Initializes git** — only if `.git` doesn't exist (backwards compatibility for non-template setups)
5. **Commits and pushes** — commits the new folders/files, then pushes to origin to verify the full pipeline works

## Phase 2: Obsidian-Git Setup

After the script finishes, present the obsidian-git plugin setup instructions:

> Install the **obsidian-git** community plugin, then configure:
>
> | Setting | Value |
> |---|---|
> | Auto pull on startup | Enabled |
> | Pull on interval (minutes) | 30 |
> | Auto commit-and-sync (minutes) | 10 |
> | Merge strategy | Rebase |
> | Push on commit-and-sync | Enabled |
>
> This keeps Obsidian in sync with cloud farmers and Claude Code sessions. Farmed content appears automatically when you open Obsidian each morning.

If the user asks what these settings do, explain each one. If they want to skip Obsidian setup, that's fine — move on.

## Phase 3: Context Onboarding (optional, one question)

Ask one question:

> "Want to seed your context files? Dump whatever you've got — role, company, tools, Slack channels you care about, key people, active projects — and I'll sort it into the right files. Or skip this and fill them in later."

If they provide context:
- Parse their dump and distribute across `context/business-profile.md`, `context/watchlists.md`, and `context/writing-style.md` (only update writing style if they mention preferences, otherwise leave defaults)
- Fill in the watchlists keyword signals with the defaults from the template (deadline, blocker, decision signals) — don't leave them commented out
- Write all files in one pass, then confirm what was filled in

If they skip, move on.

## Phase 4: How It All Works

Walk the user through how the system fits together. This is important. Present it conversationally, not as a wall of text. Cover:

### The sync loop

Explain how three things keep the vault in sync:

1. **Claude Code sessions** — when you use `/new`, `/today`, or any command, changes are auto-committed and pushed to the private GitHub repo
2. **Obsidian-git plugin** — pulls those changes when you open Obsidian (and every 30 min), so farmed content and Claude edits appear automatically. Your manual Obsidian edits get committed and pushed too
3. **Cloud farmers** — scheduled agents that clone the repo, read external sources (Slack, Fireflies, etc.), write findings into the vault, commit, and push. Next time Obsidian or Claude Code pulls, the farmed content is there

All three converge through git. No special sync service — just commits and pushes to the same private repo.

### Available commands

Give a quick rundown of what they can do:

| Command | What it does |
|---------|-------------|
| `/new <text>` | Quick capture — describe anything and it gets classified and filed as a task, project, person, or idea |
| `/today` | Generates a daily plan from due tasks and active projects |
| `/daily-review` | End of day — compare what you planned vs what happened |
| `/history` | See recent vault activity |
| `/farm <name>` | Manually run a farmer (e.g., `/farm slack`) |
| `/create-farmer` | Set up a new farmer for any connected service |
| `/schedule` | Schedule a farmer to run automatically on a cron |
| `/delegate <task>` | Fork a task to a background terminal session |

### Context farmers

Explain what farmers are and how to set one up:

- Farmers are scheduled agents that read external services and write relevant findings into your vault
- Built-in farmers exist for **Slack** and **Fireflies** — or you can create custom ones for Gmail, Google Calendar, Firecrawl, etc.
- To set one up: run `/create-farmer`, pick a service, configure what to watch, then `/schedule` to run it automatically
- Farmers use your `context/watchlists.md` to know what channels, people, and keywords to monitor
- Farmed content gets tagged with `source: farmer/<name>` so you can tell what was auto-captured vs manual

## Phase 5: Farmer Setup

After the walkthrough, ask if they want to set up their first farmer now:

> "Want to set up a context farmer now? If you added Slack channels or meetings to your watchlists, we can get those running. Just say which service — Slack, Fireflies, or something else — and I'll walk you through it with `/create-farmer`."

- If they have Slack channels in their watchlists, suggest the Slack farmer first
- If they mentioned meetings or Fireflies, suggest the Fireflies farmer
- To set up a farmer, invoke `/create-farmer` which walks through the interactive wizard
- After creation, offer to schedule it with `/schedule`
- If they skip, that's fine — remind them they can run `/create-farmer` anytime

## Edge Cases

- **Repo is public**: Script exits with error and instructions to make it private
- **`gh` not installed**: Script exits. Help the user install and authenticate:
  1. Install: `brew install gh` (macOS) or see [cli.github.com](https://cli.github.com) for other platforms
  2. Authenticate: tell them to run `! gh auth login` so it runs interactively in the terminal
  3. Once authenticated, re-run the init script
  - `gh` is required — privacy verification is not optional
- **Not a git repo**: Runs `git init` (backwards compat for non-template setups)
- **No remote configured**: Commits locally, warns that push failed with manual instructions
- **Context files already filled out**: Skip onboarding for those files, or ask if user wants to update
