#!/usr/bin/env bash
# Stop hook: block exit if there are uncommitted source changes.
# Claude will commit + update PROGRESS.md, then stop cleanly on the next pass.

set -euo pipefail

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

if [[ -z "$CWD" ]]; then
  echo '{"decision": "approve"}'
  exit 0
fi

cd "$CWD" || { echo '{"decision": "approve"}'; exit 0; }

# Not a git repo — nothing to commit
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo '{"decision": "approve"}'
  exit 0
fi

# Check for uncommitted source changes (ignore .claude/ internals)
# Include both tracked modifications and untracked files
CHANGES=$(git status --porcelain -- . ':!.claude/' 2>/dev/null | head -20)

if [[ -z "$CHANGES" ]]; then
  # No uncommitted changes — but check if PROGRESS.md is stale
  # (source commits exist since the last synced hash)
  PROGRESS_FILE=".claude/PROGRESS.md"
  if [[ -f "$PROGRESS_FILE" ]]; then
    SYNCED_HASH=$(grep -oP 'Last synced at: \K[a-f0-9]+' "$PROGRESS_FILE" 2>/dev/null || true)
    if [[ -n "$SYNCED_HASH" ]]; then
      # Check for source commits between synced hash and HEAD (ignore .claude/)
      SOURCE_DRIFT=$(git log --oneline "$SYNCED_HASH"..HEAD -- . ':!.claude/' 2>/dev/null | head -5)
      if [[ -n "$SOURCE_DRIFT" ]]; then
        STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
        if [[ "$STOP_HOOK_ACTIVE" != "true" ]]; then
          cat <<DRIFTEOF
{
  "decision": "block",
  "reason": "PROGRESS.md is stale — source commits exist since last sync (hash $SYNCED_HASH). Before stopping: 1) Update .claude/PROGRESS.md to reflect all work done this session (Recent Changes, Active Work Streams, Next Steps, Known Issues). 2) Set 'Last synced at:' to the current HEAD hash. 3) Commit: git commit -m 'chore(state): update project state' -- .claude/PROGRESS.md"
}
DRIFTEOF
          exit 0
        fi
      fi
    fi
  fi
  echo '{"decision": "approve"}'
  exit 0
fi

# Prevent infinite loop: if stop_hook_active is set, we already asked once
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [[ "$STOP_HOOK_ACTIVE" == "true" ]]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# There are uncommitted changes — block and tell Claude to commit
cat <<EOF
{
  "decision": "block",
  "reason": "You have uncommitted source changes. Before stopping: 1) Stage and commit all meaningful changes using the conventional commit format: <type>(<scope>): <description>. 2) Update .claude/PROGRESS.md to reflect what was done this session (keep it under 60 lines, set 'Last synced at:' to the new HEAD hash). 3) Commit the PROGRESS.md update separately: git commit -m 'chore(state): update project state' -- .claude/PROGRESS.md"
}
EOF
exit 0
