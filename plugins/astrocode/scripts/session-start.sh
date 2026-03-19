#!/bin/bash
# SessionStart hook: Surface resume notes and orient agent with project context
#
# 1. Check CLAUDE.md for a session resume note from a previous session
#    that ended with uncommitted work. Surface it and clean it up.
# 2. If .agents/CONTEXT.md exists, output project context.

AGENTS_DIR=".agents"
CONTEXT_FILE="$AGENTS_DIR/CONTEXT.md"

# Check for session resume note in CLAUDE.md
if [ -f "CLAUDE.md" ] && grep -q "^## Session Resume Note$" CLAUDE.md; then
  echo "=== Session Resume Note ==="
  # Extract content between the markers, excluding the markers themselves
  sed -n '/^## Session Resume Note$/,/^## End Session Resume Note$/{
    /^## Session Resume Note$/d
    /^## End Session Resume Note$/d
    p
  }' CLAUDE.md
  echo "=== End Session Resume Note ==="
  echo ""

  # Remove the resume note from CLAUDE.md
  if [ "$(uname)" = "Darwin" ]; then
    sed -i '' '/^## Session Resume Note$/,/^## End Session Resume Note$/d' CLAUDE.md
  else
    sed -i '/^## Session Resume Note$/,/^## End Session Resume Note$/d' CLAUDE.md
  fi

  # Commit the cleanup
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git add CLAUDE.md
    git commit -m "chore: remove session resume note" >/dev/null 2>&1
    git push >/dev/null 2>&1
  fi
fi

# No .agents/ directory — nothing more to do
if [ ! -d "$AGENTS_DIR" ]; then
  exit 0
fi

# No CONTEXT.md — warn but don't block
if [ ! -f "$CONTEXT_FILE" ]; then
  echo "WARNING: .agents/ directory exists but CONTEXT.md is missing."
  echo "Run /astrocode:project-state bootstrap to reinitialize."
  exit 0
fi

# Output context for the agent to read
echo "=== Project Context (from .agents/CONTEXT.md) ==="
cat "$CONTEXT_FILE"
echo ""
echo "=== End Project Context ==="
echo ""
echo "Topic files available in .agents/:"
for f in "$AGENTS_DIR"/*.md; do
  [ "$f" = "$CONTEXT_FILE" ] && continue
  [ -f "$f" ] && echo "  - $(basename "$f")"
done

exit 0
