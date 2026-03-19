#!/bin/bash
# Stop hook: Enforce project state update when source files have changed
#
# If there are uncommitted source file changes (outside .agents/), but no
# uncommitted changes inside .agents/, prompt the agent to update state
# before stopping.

AGENTS_DIR=".agents"

# No .agents/ directory — no enforcement needed
if [ ! -d "$AGENTS_DIR" ]; then
  exit 0
fi

# Not a git repo — can't diff, skip enforcement
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

# Check for uncommitted source changes (everything outside .agents/)
source_changes=$(git diff HEAD --name-only -- . ':(exclude).agents' 2>/dev/null)
untracked_source=$(git ls-files --others --exclude-standard -- . ':(exclude).agents' 2>/dev/null)

if [ -z "$source_changes" ] && [ -z "$untracked_source" ]; then
  # No source changes — nothing to document
  exit 0
fi

# Source files changed — check if .agents/ was also updated
agents_changes=$(git diff HEAD --name-only -- .agents/ 2>/dev/null)
untracked_agents=$(git ls-files --others --exclude-standard -- .agents/ 2>/dev/null)

if [ -n "$agents_changes" ] || [ -n "$untracked_agents" ]; then
  # .agents/ has changes too — state is being maintained
  exit 0
fi

# Source changed but .agents/ didn't — prompt update
echo "Source files have changed but .agents/ has not been updated." >&2
echo "Before finishing, update .agents/ with the work you've done:" >&2
echo "  1. Update relevant topic files in .agents/" >&2
echo "  2. Refresh .agents/CONTEXT.md with current status" >&2
echo "" >&2
echo "Or run: /astrocode:project-state update" >&2
exit 1
