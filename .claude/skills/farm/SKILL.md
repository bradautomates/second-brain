---
name: farm
description: Manually trigger a context farmer subagent. Usage - /farm <name> (e.g., /farm slack)
user-invocable: true
---

# Farm

Run a context farmer to pull information from an external source into the vault.

## Argument

`$ARGUMENTS` is the farmer name (e.g., `slack`).

## Workflow

1. **Validate argument**: If `$ARGUMENTS` is empty, list available farmers by globbing `.claude/agents/*-farmer.md` and ask the user which one to run.

2. **Validate farmer exists**: Check that `.claude/agents/$ARGUMENTS-farmer.md` exists. If not, list available farmers and report the error.

3. **Run the farmer**: Launch the farmer subagent using the Agent tool:
   - Use the agent name `$ARGUMENTS-farmer`
   - Prompt: "Execute your farming instructions now."

4. **Report results**: After the farmer completes, summarize what was captured:
   - Number of new files created
   - Number of existing files updated
   - List of entities with their types (task/project/person/idea)
   - Any issues encountered
