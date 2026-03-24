#!/bin/bash
# PostCompact hook: Re-inject git state awareness after context compaction
#
# When the context window gets compacted, the agent may lose track of
# uncommitted work. This hook re-injects the current dirty state so the
# agent stays oriented.

# Not a git repo — nothing to inject
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

# Collect dirty state
staged=$(git diff --cached --name-only 2>/dev/null)
unstaged=$(git diff --name-only 2>/dev/null)
untracked=$(git ls-files --others --exclude-standard 2>/dev/null)

# Nothing dirty — just show recent activity for orientation
if [ -z "$staged" ] && [ -z "$unstaged" ] && [ -z "$untracked" ]; then
  echo "=== Post-Compaction Context ==="
  echo "Working tree is clean. Recent commits:"
  git log --oneline -5 2>/dev/null
  echo "=== End Post-Compaction Context ==="
  exit 0
fi

# Dirty state exists — make sure the agent knows about it
echo "=== Post-Compaction Context ==="
echo "IMPORTANT: You have uncommitted changes that must be committed before stopping."
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

echo "Recent commits:"
git log --oneline -5 2>/dev/null
echo ""
echo "=== End Post-Compaction Context ==="

exit 0
