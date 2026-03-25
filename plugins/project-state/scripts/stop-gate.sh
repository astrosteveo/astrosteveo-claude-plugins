#!/bin/bash
# Stop hook: Ensure work is committed and memory is evaluated before stopping
#
# Checks all dirty state in a single pass and reports everything at once,
# so the agent can resolve it all in one turn. Also prompts the agent to
# evaluate whether session learnings should be saved to auto-memory.

# Not a git repo — can't enforce, allow stop
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

# Collect all dirty state in one pass
staged=$(git diff --cached --name-only 2>/dev/null)
unstaged=$(git diff --name-only 2>/dev/null)
untracked=$(git ls-files --others --exclude-standard 2>/dev/null)

# Nothing dirty — allow stop
if [ -z "$staged" ] && [ -z "$unstaged" ] && [ -z "$untracked" ]; then
  exit 0
fi

# Report everything at once so the agent can fix it in one turn
{
  echo "BLOCKED: You have uncommitted changes."
  echo ""

  if [ -n "$staged" ]; then
    echo "Staged (ready to commit):"
    echo "$staged" | sed 's/^/  /'
    echo ""
  fi

  if [ -n "$unstaged" ]; then
    echo "Modified (not staged):"
    echo "$unstaged" | sed 's/^/  /'
    echo ""
  fi

  if [ -n "$untracked" ]; then
    echo "Untracked (new files):"
    echo "$untracked" | sed 's/^/  /'
    echo ""
  fi

  echo "Resolve ALL of the above in a single turn:"
  echo "  1. Stage the files that belong to your current unit of work"
  echo "  2. Commit with a descriptive commit message"
  echo "  3. If any files should NOT be committed (scratch files, experiments),"
  echo "     add them to .gitignore or ask the user what to do"
  echo "  4. Do not use 'git add -A' or 'git add .'"
  echo ""
  echo "MEMORY: Before stopping, evaluate whether you learned anything this session"
  echo "that should be saved to auto-memory:"
  echo "  - User preferences, role, or expertise (user type)"
  echo "  - Feedback on your approach — corrections or confirmations (feedback type)"
  echo "  - Project context, decisions, or deadlines (project type)"
  echo "  - External resources or references (reference type)"
  echo "Save any relevant learnings before attempting to stop again."
} >&2

exit 2
