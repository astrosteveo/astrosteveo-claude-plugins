#!/bin/bash
# SessionEnd hook: Best-effort deterministic state capture
#
# Runs when the session ends (exit, crash, kill). Updates the timestamp
# in CONTEXT.md as a last-resort freshness marker. This is a catch-all
# for cases where the Stop hook didn't fire or the agent didn't comply.

AGENTS_DIR=".agents"
CONTEXT_FILE="$AGENTS_DIR/CONTEXT.md"

# No .agents/ — nothing to do
if [ ! -d "$AGENTS_DIR" ]; then
  exit 0
fi

if [ ! -f "$CONTEXT_FILE" ]; then
  exit 0
fi

# Update the "Last updated" timestamp in CONTEXT.md
date_str=$(date '+%Y-%m-%d')

if [ "$(uname)" = "Darwin" ]; then
  sed -i '' "s/> Last updated:.*/> Last updated: $date_str/" "$CONTEXT_FILE"
else
  sed -i "s/> Last updated:.*/> Last updated: $date_str/" "$CONTEXT_FILE"
fi

# Commit and push everything so no dirty state is left behind
git add -A
git diff --cached --quiet && exit 0
git commit -m "chore: update .agents/ state (session-end)" >/dev/null 2>&1
git push >/dev/null 2>&1

exit 0
