---
name: delegate-task
description: Delegate a task by forking a terminal session to a new terminal window. Use this when the user requests 'delegate' or 'create a new terminal' or 'new terminal: <command>' or 'fork session: <command>'.
---

# Purpose

Fork a new terminal session to a new terminal window using one Claude Code.
Follow the `Instructions`, execute the `Workflow`.

## Variables

DEFAULT_MODEL: opus
HEAVY_MODEL: opus
BASE_MODEL: sonnet
FAST_MODEL: haiku

## Employees

If user specifies "delegate to <name>", read `.claude/reference/employees.json` to get the repo path.

## Instructions

- Before executing the command, run `claude --help` to understand the command and its options.
- Always use interactive mode (leave off -p flag)
- For the --model argument, use DEFAULT_MODEL if not specified. If 'fast' is requested, use FAST_MODEL. If 'heavy' is requested, use HEAVY_MODEL.
- Always run with `--dangerously-skip-permissions`

### Cross-Repo Context (CRITICAL)

When delegating to a different repo (employee), the agent operates in THEIR directory, not yours. Before crafting the prompt:

1. **Capture source repo path**: Run `pwd` to get current working directory (SOURCE_REPO)
2. **Use absolute paths** in prompt for all source repo references:
   - Source tasks: `{SOURCE_REPO}/tasks/...`
   - Context files: `{SOURCE_REPO}/context/...`
   - Output directory: `{SOURCE_REPO}/outputs/`

3. **Instruct agent to use its skills**: Include in prompt: "First, check your available skills at .claude/skills/ and use any relevant ones for this task."

4. **Specify output location explicitly**: "Save deliverables to {SOURCE_REPO}/outputs/YYYY-MM-DD-<slug>.md"

### File Handling

- Instruct delegated agents to update existing vault files (tasks/, projects/, people/) directly—never create duplicates
- For deliverables, save to source repo's `outputs/YYYY-MM-DD-<slug>.<ext>` using absolute path
- Link from the reference file under `## Outputs` using the obsidian [[slug]] schema

### Source Task Callback

When delegating work related to an existing task or project:
1. Identify the source file (e.g., `tasks/next-weeks-video-idea.md`)
2. Include in the prompt: "When complete, update {absolute_path_to_source_file} with status and link to your output."

### Fork Summary User Prompts

- IF: The user requests a fork terminal with a summary.
- THEN: 
  - Read, and REPLACE the `.claude/skills/delegate/references/fork_summary_user_prompt.md` with the history of the conversation between you and the user so far. 
  - Include the next users request in the `Next User Request` section.
  - This will be what you pass into the PROMPT parameter of the agentic coding tool.
  - IMPORTANT: To be clear, don't update the file directly, just read it, fill it out IN YOUR MEMORY and use it to craft a new prompt in the structure provided for the new fork agent.
  - Let's be super clear here, the fork_summary_user_prompt.md is a template for you to fill out IN YOUR MEMORY. Once you've filled it out, pass that prompt to the agentic coding tool.
  - XML Tags have been added to let you know exactly what you need to replace. You'll be replacing the <fill in the history here> and <fill in the next user request here> sections.
- EXAMPLES:
  - "fork terminal use claude code to <xyz> summarize work so far"
  - "spin up a new terminal request <xyz> using claude code include summary"
  - "create a new terminal to <xyz> with claude code with summary"

## Workflow

1. Understand the user's request.
2. Craft a clear, complete prompt describing the task for the delegated agent.
3. Build the claude command with prompt: `claude --model <MODEL> --dangerously-skip-permissions "<PROMPT>"`
   - CRITICAL: The prompt MUST be included as a positional argument. Without it, Claude opens with no task.
4. Execute fork:
   - **Default (same repo):** `.claude/skills/delegate/scripts/fork_terminal.py '<full command>'`
   - **Different repo:** `.claude/skills/delegate/scripts/fork_terminal.py '<full command>' --repo '<employee_path>'`
   - Use single quotes around the full command, double quotes around the prompt.

## Examples

User says: "delegate research on X"
Execute: `.claude/skills/delegate/scripts/fork_terminal.py 'claude --model opus --dangerously-skip-permissions "Research X and summarize findings"'`

User says: "fork terminal to build feature Y"
Execute: `.claude/skills/delegate/scripts/fork_terminal.py 'claude --model opus --dangerously-skip-permissions "Implement feature Y in this codebase"'`

User says: "delegate to head-of-content: research video ideas"
-> Run `pwd` to capture SOURCE_REPO
-> Read employees.json, get path for "head-of-content"
-> Craft prompt with: (1) instruction to use .claude/skills/, (2) absolute paths to SOURCE_REPO files
Execute: `.claude/skills/delegate/scripts/fork_terminal.py 'claude --model opus --dangerously-skip-permissions "First check .claude/skills/ for relevant skills. Research video ideas. Context: {SOURCE_REPO}/context/... Output to: {SOURCE_REPO}/outputs/..."' --repo '<employee_path>'`


