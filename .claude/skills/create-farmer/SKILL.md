---
name: create-farmer
description: Create or schedule a context farmer. Checks existing farmers and offers to build new ones or schedule existing ones.
user-invocable: true
---

# Farmer Manager

## First Step

Check what already exists before asking the user anything:

1. **Scan existing farmers**: `Glob` for `.claude/agents/*-farmer.md`
2. **Scan scheduled triggers**: Use `/schedule` (the schedule skill) with action `list` to see what's already running — or use `RemoteTrigger` directly if available
3. **Present status**: Show the user what farmers exist and which are scheduled
4. **Ask what they need**: Build a new farmer, or schedule an existing one?

## Build a New Farmer

### 1. Source & MCP

Ask what source to farm. Then check if an MCP server is already connected — use `ToolSearch` to look for tools matching that service name. If nothing found, search for an official remote-hosted MCP server and help them connect it.

### 2. Probe the connector

Use `ToolSearch` to discover all tools for the service. Test 1-2 read-only tools to verify connectivity and understand data shape.

### 3. Gather details

Ask what to monitor (channels, senders, calendars, keywords, URLs) and any custom classification rules beyond vault defaults.

### 4. Generate the subagent

Create `.claude/agents/<name>-farmer.md`. Read an existing farmer (e.g., `slack-farmer.md`) as a structural reference.

**Frontmatter:**

```yaml
---
name: <name>-farmer
description: Farms context from <source> into the vault
model: sonnet
permissionMode: acceptEdits
---
```

Rules:
- No `tools` field — MCP tools and ToolSearch inherited from parent
- No `mcpServers` — doesn't work for remote MCPs; ToolSearch handles discovery
- Always `permissionMode: acceptEdits`
- Name must end in `-farmer` — matches `SubagentStop` hook for auto-push
- Body is the entire system prompt — no CLAUDE.md, no parent context

**Body must include:**

1. **Process** — Discover tools via ToolSearch (search by service name), use generic tool references (never hardcoded prefixed names). Then: read config, check state, read source (24hr max), classify, deduplicate, git pull, write, update state. If no new data, skip to state update.
2. **Classification Rules** — Source data → vault entity types
3. **Useful MCP Tools** — `| Tool | Purpose |` table with bare names. Read/search tools only.
4. **Guidelines** — Signal-to-noise, naming, attribution

All farmer-created files must include `source: farmer/<name>` and `farmed: <timestamp>` in frontmatter.

### 5. Allow read-only MCP tools

Add the farmer's read-only MCP tools to `.claude/settings.json` under `permissions.allow`. Only add read/search/list tools — never write/send/delete.

### 6. Update watchlists

Add a section to `context/watchlists.md` for the new source's filters.

### 7. Offer to schedule

After building, ask if they want to schedule it now. If yes, follow the scheduling flow below.

## Schedule a Farmer

Use `/schedule` to create a cloud scheduled trigger. The prompt should be `/farm <name>`.

Key details to confirm:
- **Frequency**: Daily (recommended for most), weekdays, hourly, etc.
- **Time**: Convert user's local time to UTC for cron
- **MCP connector**: Must be attached to the trigger
- **Environment**: full-access unless they specify otherwise

Farmers must run as subagents via `/farm <name>`, not inline prompts — this gives isolated context and triggers the `SubagentStop` hook for auto-push.

### Other scheduling options

- **Desktop scheduled**: Desktop app > Schedule > New local task. Needs machine on.
- **Session-scoped**: `/loop 30m /farm <name>` — active session only.
- **Manual**: `/farm <name>` — on demand.
