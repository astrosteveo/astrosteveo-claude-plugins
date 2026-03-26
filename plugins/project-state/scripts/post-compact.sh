#!/bin/bash
# PostCompact hook: Re-inject orientation and memory awareness after compaction
#
# When the context window gets compacted, the agent may lose track of
# learnings from earlier in the conversation. This hook provides recent
# commit context for orientation and reminds the agent to persist
# important context to auto-memory before it is lost.

echo "=== Post-Compaction Context ==="

# Show recent commits for orientation if in a git repo
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Recent commits:"
  git log --oneline -5 2>/dev/null
  echo ""
fi

echo "MEMORY: Context was just compacted. If you learned anything important"
echo "earlier in this conversation — user preferences, feedback on your approach,"
echo "project decisions, or external references — save it to auto-memory now"
echo "before it is permanently lost."
echo "=== End Post-Compaction Context ==="

exit 0
