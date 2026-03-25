#!/bin/bash
# SessionStart hook: Surface resume notes and prime auto-memory awareness
#
# If the previous session ended with uncommitted work, a resume note
# was written to CLAUDE.md. Surface it so the agent can review with the
# user, then let the agent handle cleanup.
#
# Also reminds the agent to read existing auto-memories and actively
# maintain them throughout the session.

# ── Resume note handling ──────────────────────────────────────
if [ -f "CLAUDE.md" ] && grep -q "^## Session Resume Note$" CLAUDE.md; then
  echo "=== Session Resume Note ==="
  sed -n '/^## Session Resume Note$/,/^## End Session Resume Note$/{
    /^## Session Resume Note$/d
    /^## End Session Resume Note$/d
    p
  }' CLAUDE.md
  echo "=== End Session Resume Note ==="
  echo ""
  echo "ACTION: After reviewing with the user, remove the Session Resume Note"
  echo "section from CLAUDE.md and commit the cleanup."
  echo ""
fi

# ── Auto-memory awareness ────────────────────────────────────
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
