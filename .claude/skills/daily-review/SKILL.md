---
name: daily-review
description: End of day review - compare planned vs actual, update task statuses. Part of chief-of-staff system.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# /daily-review - End of Day Review

Compare planned vs actual for today.

## Steps

1. Read `daily/YYYY-MM-DD.md` for today's plan
2. Run `git log --since="8am" --grep="cos:"` for activity
3. Find relevant tasks efficiently (don't read all tasks):
   - Search for tasks due today: `grep -l "due: YYYY-MM-DD" task/*.md`
   - Find task files modified today: `git diff --name-only HEAD@{8am}..HEAD -- task/`
4. Read only the relevant task files identified above
5. Update task statuses (`status: done` for completed items)
6. Append review section to daily note
7. Commit: `cos: daily review for YYYY-MM-DD`

## Append to Daily Note

```markdown
## Review

### Completed
- ✅ Items that got done

### Incomplete
- ⏳ Items carrying forward

### Observations
- Patterns noticed, suggestions for tomorrow
```
