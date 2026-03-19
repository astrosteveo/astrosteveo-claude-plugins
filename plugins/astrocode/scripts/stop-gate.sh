#!/bin/bash
# Stop hook: Enforce project state update before session ends
#
# Checks if .agents/ exists and whether CONTEXT.md was updated during
# this session. If state is stale, returns non-zero to prompt the agent
# to update before stopping.

AGENTS_DIR=".agents"
CONTEXT_FILE="$AGENTS_DIR/CONTEXT.md"

# No .agents/ directory — no enforcement needed
if [ ! -d "$AGENTS_DIR" ]; then
  exit 0
fi

# No CONTEXT.md — can't enforce, just warn
if [ ! -f "$CONTEXT_FILE" ]; then
  exit 0
fi

# Check if CONTEXT.md was modified recently (within last 5 minutes)
# This heuristic assumes if it was touched recently, the agent updated it
if [ "$(uname)" = "Darwin" ]; then
  last_modified=$(stat -f %m "$CONTEXT_FILE" 2>/dev/null)
else
  last_modified=$(stat -c %Y "$CONTEXT_FILE" 2>/dev/null)
fi

current_time=$(date +%s)

if [ -n "$last_modified" ]; then
  diff=$((current_time - last_modified))
  # Updated within last 5 minutes — state is fresh
  if [ "$diff" -lt 300 ]; then
    exit 0
  fi
fi

# State is stale — prompt the agent to update
echo "You have not updated the project state (.agents/) during this session."
echo "Before finishing, update .agents/ with the work you've done:"
echo "  1. Update relevant topic files in .agents/"
echo "  2. Refresh .agents/CONTEXT.md with current status"
echo ""
echo "Or run: /astrocode:project-state update"
exit 1
