#!/bin/bash
# SessionStart hook: Orient agent from .agents/CONTEXT.md if it exists
#
# If the project has been bootstrapped with .agents/, output the context
# so the agent starts the session with full project orientation.

AGENTS_DIR=".agents"
CONTEXT_FILE="$AGENTS_DIR/CONTEXT.md"

# No .agents/ directory — nothing to do
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
