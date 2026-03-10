#!/usr/bin/env bash
# SessionEnd hook: mark that a session occurred. Does NOT commit.
# The skill handles content updates and git operations.

set -euo pipefail

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

if [[ -z "$CWD" ]]; then
  exit 0
fi

PROGRESS_FILE="$CWD/.claude/memory/PROGRESS.md"

if [[ ! -f "$PROGRESS_FILE" ]]; then
  exit 0
fi

# Update the timestamp only — content accuracy is the skill's job
sed -i "s/^> Last updated:.*/> Last updated: $(date +%Y-%m-%d)/" "$PROGRESS_FILE"
