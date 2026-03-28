#!/bin/bash
# SessionStart hook: Prime auto-memory awareness for the session
#
# Reminds the agent to read existing auto-memories and actively
# maintain them throughout the session.

echo "=== Auto-Memory ==="
echo "Check your auto-memory for this project and read any existing memories"
echo "to restore context from previous sessions."
echo ""
echo "Throughout this session, actively maintain your auto-memory:"
echo "  - User preferences, role, or expertise (user type)"
echo "  - Feedback on your approach — corrections AND confirmations (feedback type)"
echo "  - Project context, decisions, or deadlines (project type)"
echo "  - External resources or references (reference type)"
echo ""
echo "Save learnings as they happen — do not wait until the session ends."
echo "=== End Auto-Memory ==="

exit 0
