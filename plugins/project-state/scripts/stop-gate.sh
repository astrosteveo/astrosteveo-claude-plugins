#!/bin/bash
# Stop hook: Prompt auto-memory evaluation before stopping
#
# Reminds the agent to evaluate whether session learnings should be
# saved to auto-memory. Does not block stopping.

echo "=== Auto-Memory ===" >&2
echo "Before stopping, evaluate whether you learned anything this session" >&2
echo "that should be saved to auto-memory:" >&2
echo "  - User preferences, role, or expertise (user type)" >&2
echo "  - Feedback on your approach — corrections or confirmations (feedback type)" >&2
echo "  - Project context, decisions, or deadlines (project type)" >&2
echo "  - External resources or references (reference type)" >&2
echo "Save any relevant learnings before attempting to stop again." >&2
echo "=== End Auto-Memory ===" >&2

exit 0
