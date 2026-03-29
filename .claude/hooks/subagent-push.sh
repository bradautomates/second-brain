#!/bin/bash
# Push any unpushed commits after a farmer subagent finishes

cd "$CLAUDE_PROJECT_DIR" || exit 0

# Recover from detached HEAD before pushing
if ! git symbolic-ref --quiet HEAD >/dev/null 2>&1; then
  echo "subagent-push: HEAD is detached, recovering to origin/main"
  git fetch origin main
  git checkout main 2>/dev/null || git checkout -b main origin/main
  git reset --hard origin/main
  exit 0
fi

# Quick check: if local HEAD matches origin/main, nothing to push — exit without touching git state
LOCAL_HEAD=$(git rev-parse HEAD 2>/dev/null)
REMOTE_HEAD=$(git rev-parse origin/main 2>/dev/null)
if [ "$LOCAL_HEAD" = "$REMOTE_HEAD" ]; then
  exit 0
fi

# There are local commits — fetch and push
git fetch origin main 2>/dev/null
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
if [ "$AHEAD" -gt 0 ]; then
  if ! git pull --rebase; then
    git rebase --abort 2>/dev/null
    git pull --no-rebase
  fi
  git push -u origin main || true
fi

exit 0
