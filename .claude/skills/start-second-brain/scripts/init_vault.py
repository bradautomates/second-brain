#!/usr/bin/env python3
"""Initialize a Second Brain vault: create folders, validate privacy, and push."""

import shutil
import subprocess
import sys
from pathlib import Path

FOLDERS = ["tasks", "projects", "people", "ideas", "context", "daily", "weekly", "outputs"]

GITIGNORE = """\
# Obsidian
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/plugins/
.obsidian/core-plugins-migration.json

# macOS
.DS_Store

# Temporary files
*.tmp

# Farmer state (not synced — cloud runs use fallback window)
context/farmers/.state/
"""

CONTEXT_INDEX = """\
# Context Files

Reference documents for LLM context.

## Available Context

- `writing-style.md` - Voice, tone, and writing preferences
- `business-profile.md` - Company/work context
- `watchlists.md` - Channels, keywords, and people for context farmers

## Usage

Check relevant context files before writing or complex tasks.
"""

WATCHLISTS_TEMPLATE = """\
---
type: config
---

# Watchlists

## Slack Channels

| Channel | Watch For |
|---------|-----------|
<!-- Add channels: | general | Announcements, decisions | -->

## Keywords

### Deadline Signals
- by EOD
- due
- deadline
- by end of week
- need this by
- time-sensitive
- urgent

### Blocker Signals
- blocked
- waiting on
- stuck
- can't proceed
- dependency
- holding up

### Decision Signals
- decided
- agreed
- going with
- final call
- approved
- signed off

## People to Track

| Name | Vault Slug |
|------|------------|
<!-- Add people: | Jane Smith | jane-smith | -->

## Fireflies Meetings

| Meeting Title Pattern | Type | Watch For |
|-----------------------|------|-----------|
<!-- Add meetings: | Weekly Standup | standup | Blockers, action items | -->

## Active Projects

<!-- Add project slugs that farmers should cross-reference -->
"""


def run(cmd, cwd=None, check=True, capture=False):
    """Run a shell command, optionally capturing output."""
    result = subprocess.run(
        cmd, cwd=cwd, check=check,
        capture_output=capture, text=True if capture else None,
    )
    return result


def gh_available():
    return shutil.which("gh") is not None


def repo_is_private(path):
    """Check if the GitHub repo is private. Returns True/False/None (if can't determine)."""
    result = run(
        ["gh", "repo", "view", "--json", "visibility", "-q", ".visibility"],
        cwd=path, check=False, capture=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip().upper() == "PRIVATE"


def init_vault(path: Path):
    path = path.resolve()

    # --- Privacy check ---
    if gh_available():
        # Only check if this is already a git repo with a remote
        has_remote = (path / ".git").exists() and run(
            ["git", "remote", "get-url", "origin"],
            cwd=path, check=False, capture=True,
        ).returncode == 0

        if has_remote:
            private = repo_is_private(path)
            if private is False:
                print("✗ This repository is PUBLIC.")
                print("  Your vault will contain personal data — it must be private.")
                print()
                print("  Fix this on GitHub: Settings → Danger Zone → Change visibility → Private")
                print("  Or run: gh repo edit --visibility private")
                print()
                print("  Then re-run this script.")
                sys.exit(1)
            elif private is True:
                print("✓ Repository is private.")
            else:
                print("⚠  Could not verify repo visibility. Make sure it's private before adding personal data.")
    else:
        print("✗ gh CLI not found — required to verify repo is private.")
        print("  Install it: brew install gh  (macOS) or see https://cli.github.com")
        print("  Then authenticate: gh auth login")
        print()
        print("  Re-run this script after installing.")
        sys.exit(1)

    # --- Create folders ---
    created = []
    for folder in FOLDERS:
        folder_path = path / folder
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            created.append(folder)
    if created:
        print(f"✓ Created folders: {', '.join(created)}")
    else:
        print("✓ All folders already exist.")

    # --- Create template files (skip if they exist) ---
    files_created = []

    index_file = path / "context" / "_index.md"
    if not index_file.exists():
        index_file.write_text(CONTEXT_INDEX)
        files_created.append("context/_index.md")

    watchlists = path / "context" / "watchlists.md"
    if not watchlists.exists():
        watchlists.write_text(WATCHLISTS_TEMPLATE)
        files_created.append("context/watchlists.md")

    gitignore = path / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(GITIGNORE)
        files_created.append(".gitignore")

    if files_created:
        print(f"✓ Created files: {', '.join(files_created)}")

    # --- Initialize git if not already a repo ---
    if not (path / ".git").exists():
        run(["git", "init"], cwd=path)
        print("✓ Initialized git repository.")

    # --- Commit and push ---
    run(["git", "add", "-A"], cwd=path)
    result = run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=path, check=False,
    )
    if result.returncode != 0:
        # There are staged changes
        run(
            ["git", "commit", "-m", "cos: initialize vault structure"],
            cwd=path,
        )
        print("✓ Committed vault structure.")

        # Push to verify the pipeline works
        push_result = run(
            ["git", "push"],
            cwd=path, check=False, capture=True,
        )
        if push_result.returncode == 0:
            print("✓ Pushed to remote — everything is working.")
        else:
            stderr = push_result.stderr.strip()
            if "no upstream" in stderr.lower() or "no configured push" in stderr.lower():
                # Try setting upstream
                push_result = run(
                    ["git", "push", "-u", "origin", "main"],
                    cwd=path, check=False, capture=True,
                )
                if push_result.returncode == 0:
                    print("✓ Pushed to remote — everything is working.")
                else:
                    print(f"⚠  Push failed: {push_result.stderr.strip()}")
                    print("   You may need to push manually: git push -u origin main")
            else:
                print(f"⚠  Push failed: {stderr}")
                print("   You may need to push manually: git push -u origin main")
    else:
        print("✓ No changes to commit (vault already initialized).")

    print(f"\n✓ Vault ready at {path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize a Second Brain vault")
    parser.add_argument("path", nargs="?", default=".", help="Vault path (default: current directory)")
    args = parser.parse_args()

    init_vault(Path(args.path))
