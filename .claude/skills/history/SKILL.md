---
name: history
description: Show recent git activity in readable format. Part of chief-of-staff system.
allowed-tools: Bash
---

# /history - Recent Activity

Show chief-of-staff activity from git log.

## Run

```bash
git log --since="7 days ago" --grep="cos:" --format="%ad %s" --date=short
```

Group output by day and summarize actions.
