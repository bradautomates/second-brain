---
name: new
description: Quick capture - classify and file natural language input into the vault. Part of chief-of-staff system. Use for capturing tasks, ideas, project notes, or people notes.
argument-hint: <whatever's on your mind (projects, ideas, or tasks)>
allowed-tools: Read, Glob, Write, Edit, AskUserQuestion
---

# /new - Quick Capture

Create items from natural language: `/new <input>`

Input is in $ARGUMENTS.

> **Do NOT commit manually unless explicitly asked.** A PostToolUse hook auto-commits after Write operations.

## Steps

1. **Decompose** - Extract ALL entities from input (may be multiple)
2. **Classify** each entity: task | project | person | idea
3. **Extract** structured data (due dates, tags, names)
4. **Link** entities via frontmatter fields
5. **Write** files for each entity (hook handles git commit)
6. **Respond** with summary of what was created

## Decomposition

Parse input for multiple entities. Example:

> "new project with John Smith for marketing outbound, need landing page and brainstorm names"

Entities:
- Person: John Smith
- Project: marketing-outbound (linked to John Smith)
- Task: create landing page (linked to project)
- Task: brainstorm names for workshop (linked to project)

## Classification

- Named person with context → **person**
- Ongoing work, multiple steps → **project**
- Specific actionable item → **task**
- Speculative, "what if" → **idea**
- Confidence < 0.5 → Ask for clarification

**Edge case**: "start/begin/create X" → **task** (the action of initiating), not project.
- "I need to start a content plan" → task: start content plan
- "Working on the content plan" → project: content plan (if ongoing)

## Missing Information

When creating a **task** without a due date, use AskUserQuestion:

```
Question: "When is this due?"
Header: "Due date"
Options:
  - "Today" → use today's date
  - "End of week" → use Friday of current week
  - "Next week" → use Monday of next week
  - (Other allows custom entry)
```

Apply similar pattern for other ambiguous fields when classification confidence is high but key data is missing.

## Linking

Use Obsidian wiki-style links `[[slug]]` in the markdown body to connect entities.

When creating a task linked to a project, update the project file to include `[[task-slug]]`. Same for project → person links.

Check if person/project already exists before creating (use Glob). Use Read before editing existing files.

## File Formats

**Task:**
```yaml
---
type: task
status: pending
due: YYYY-MM-DD  # optional
tags: []
---
Description here.
```

**Project:**
```yaml
---
type: project
status: active
tags: []
---
## Next Action
- First task to do
[[linked-task-slug]]

## Notes
```

**Person:**
```yaml
---
type: person
last-contact: YYYY-MM-DD
tags: []
---
## Context
Who they are, relationship.

## Follow-ups
- [ ] Pending items
```

**Idea:**
```yaml
---
type: idea
tags: []
---
Description of the idea.
```
