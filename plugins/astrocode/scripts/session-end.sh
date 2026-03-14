#!/usr/bin/env bash
# SessionEnd hook: mark that a session occurred. Does NOT commit.
# The skill handles content updates and git operations.

set -euo pipefail

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

if [[ -z "$CWD" ]]; then
  exit 0
fi

PROGRESS_FILE="$CWD/.claude/PROGRESS.md"

if [[ ! -f "$PROGRESS_FILE" ]]; then
  exit 0
fi

# Update the date only, preserving everything after it (e.g. "| Last synced at: HASH")
TODAY=$(date +%Y-%m-%d)

# BSD sed (macOS) requires -i '', GNU sed (Linux) requires -i without an argument
if sed --version >/dev/null 2>&1; then
  sed -i "s/^> Last updated: [0-9-]*/> Last updated: $TODAY/" "$PROGRESS_FILE"
else
  sed -i '' "s/^> Last updated: [0-9-]*/> Last updated: $TODAY/" "$PROGRESS_FILE"
fi
