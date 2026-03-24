#!/bin/bash
# SessionEnd hook: Record uncommitted state for the next session
#
# If there are uncommitted changes when the session ends, write a resume
# note to CLAUDE.md listing what was left dirty. Does NOT commit or push —
# the next session (or the user) decides what to do with the changes.

# Not a git repo — nothing to do
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

# Collect dirty state: staged, unstaged, and untracked
staged=$(git diff --cached --name-only 2>/dev/null)
unstaged=$(git diff --name-only 2>/dev/null)
untracked=$(git ls-files --others --exclude-standard 2>/dev/null)

# Nothing dirty — nothing to record
if [ -z "$staged" ] && [ -z "$unstaged" ] && [ -z "$untracked" ]; then
  exit 0
fi

# Remove any existing resume note from CLAUDE.md before adding a new one
if [ -f "CLAUDE.md" ]; then
  if [ "$(uname)" = "Darwin" ]; then
    sed -i '' '/^## Session Resume Note$/,/^## End Session Resume Note$/d' CLAUDE.md
  else
    sed -i '/^## Session Resume Note$/,/^## End Session Resume Note$/d' CLAUDE.md
  fi
fi

# Build the resume note with categorized file lists
{
  echo ""
  echo "## Session Resume Note"
  echo ""
  echo "The previous session ended with uncommitted changes."
  echo ""

  if [ -n "$staged" ]; then
    echo "**Staged (ready to commit):**"
    echo "$staged" | sed 's/^/- /'
    echo ""
  fi

  if [ -n "$unstaged" ]; then
    echo "**Modified (not staged):**"
    echo "$unstaged" | sed 's/^/- /'
    echo ""
  fi

  if [ -n "$untracked" ]; then
    echo "**Untracked (new files):**"
    echo "$untracked" | sed 's/^/- /'
    echo ""
  fi

  echo "Review these changes with the user. Some may be intentional work-in-progress,"
  echo "others may be scratch files or experiments meant to be discarded."
  echo ""
  echo "## End Session Resume Note"
} >> CLAUDE.md

exit 0
