#!/bin/bash
# Pull remote changes on session start (catches cloud farmer commits)
cd "$CLAUDE_PROJECT_DIR" || exit 0

# Abort any in-progress rebase from a prior crashed session
git rebase --abort 2>/dev/null

# Recover from detached HEAD — origin/main is always source of truth
if ! git symbolic-ref --quiet HEAD >/dev/null 2>&1; then
  echo "session-sync: HEAD is detached, recovering to origin/main"
  git fetch origin main
  git checkout main 2>/dev/null || git checkout -b main origin/main
  git reset --hard origin/main
  exit 0
fi

# Ensure we're on main, not some other branch
BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null)
if [ "$BRANCH" != "main" ]; then
  echo "session-sync: on branch '$BRANCH', switching to main"
  git checkout main 2>/dev/null
fi

# Pull with rebase — don't swallow errors
git pull --rebase --autostash
exit 0
