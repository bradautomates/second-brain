---
name: today
description: Generate daily plan from due tasks and active projects. Part of chief-of-staff vault system.
---

# /today - Daily Planning

Generate today's plan from vault contents.

## Steps

1. Check if `daily/YYYY-MM-DD.md` exists - if so, read it first
2. **Find tasks by due date using grep** (never glob all tasks):
   - Grep for `due: YYYY-MM-DD` (today's date) → Due Today
   - Grep for dates before today → Overdue
   - If no tasks found for today/overdue, grep for dates through end of week
   - If still none, grep to find the next earliest due date
3. Read only the matching task files
4. Grep `projects/*.md` for `status: active`, read those files
5. Run `git log --since="midnight" --grep="cos:" --oneline` for today's activity
6. Create or update `daily/YYYY-MM-DD.md`

## Task Discovery (grep-first approach)

All tasks have `due: YYYY-MM-DD` in frontmatter. Use grep to find relevant tasks efficiently:

```bash
# Today's tasks (replace with actual date)
grep -l "due: 2026-01-23" tasks/*.md

# Overdue: grep for each date before today, or use date range pattern
grep -l "due: 2026-01-2[0-2]" tasks/*.md  # dates 20-22 if today is 23rd

# This week: grep for dates through end of week
grep -l "due: 2026-01-2[3-9]" tasks/*.md  # adjust pattern for week
```

Only read files returned by grep. Never glob and read all task files.

## Update Behavior

When the daily file already exists:
- Keep any `[x]` completed items as-is
- Keep any manually added items (not from vault tasks)
- Add new tasks from vault that aren't already present
- Refresh the Recent Activity section with latest git log
- Preserve any custom sections added by user

## Output Format

```markdown
---
type: daily
date: YYYY-MM-DD
---

## Due Today
- [ ] Task items from tasks/ with today's due date

## Overdue
- [ ] Tasks past due (X days overdue)

## Active Projects
- Project Name (next: next action from file)

## Recent Activity
- Items from git log
```
