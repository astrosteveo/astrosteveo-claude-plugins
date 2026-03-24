#!/bin/bash
# SessionStart hook: Surface resume notes from a previous session
#
# If the previous session ended with uncommitted work, a resume note
# was written to CLAUDE.md. Surface it so the agent can review with the
# user, then let the agent handle cleanup.

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
fi

exit 0
