#!/bin/bash
# SessionEnd hook: Commit and push any uncommitted work
#
# Runs when the session ends (exit, crash, kill). Ensures nothing
# is left dirty in the working tree.

# Not a git repo — nothing to do
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

# Commit and push everything so no dirty state is left behind
git add -A
git diff --cached --quiet && exit 0
git commit -m "chore: commit uncommitted work (session-end)" >/dev/null 2>&1
git push >/dev/null 2>&1

exit 0
