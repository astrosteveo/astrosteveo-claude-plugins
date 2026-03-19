#!/bin/bash
# SessionStart hook: Surface resume notes and orient agent with project context
#
# 1. Check CLAUDE.md for a session resume note from a previous session
#    that ended with uncommitted work. Surface it and clean it up.
# 2. Output curated context from .agents/CONTEXT.md (overview, stack, topics)
# 3. Dynamically generate structure tree and recent git activity
# 4. Freshness check: warn if topic file references are stale

AGENTS_DIR=".agents"
CONTEXT_FILE="$AGENTS_DIR/CONTEXT.md"

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

# ── No .agents/ directory — nothing more to do ───────────────
if [ ! -d "$AGENTS_DIR" ]; then
  exit 0
fi

# ── No CONTEXT.md — warn but don't block ─────────────────────
if [ ! -f "$CONTEXT_FILE" ]; then
  echo "WARNING: .agents/ directory exists but CONTEXT.md is missing."
  echo "Run /astrocode:project-state bootstrap to reinitialize."
  exit 0
fi

# ── Curated context from CONTEXT.md ──────────────────────────
echo "=== Project Context (from .agents/CONTEXT.md) ==="
cat "$CONTEXT_FILE"
echo ""

# ── Live: directory structure ────────────────────────────────
echo "## Structure (live)"
echo '```'
if command -v tree >/dev/null 2>&1; then
  tree -a -L 3 -I '.git' --dirsfirst -n 2>/dev/null | head -60
else
  find . -maxdepth 3 -not -path './.git/*' -not -path './.git' -type d 2>/dev/null | sort | head -30
fi
echo '```'
echo ""

# ── Live: recent git activity ────────────────────────────────
echo "## Recent Activity (live)"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git log --oneline -10 2>/dev/null
else
  echo "(not a git repository)"
fi
echo ""

echo "=== End Project Context ==="
echo ""

# ── Topic files listing ─────────────────────────────────────
echo "Topic files available in .agents/:"
for f in "$AGENTS_DIR"/*.md; do
  [ "$f" = "$CONTEXT_FILE" ] && continue
  [ -f "$f" ] && echo "  - $(basename "$f")"
done

# ── Freshness check: topic file references ──────────────────
fresh=true

# Files on disk but not referenced in CONTEXT.md
for f in "$AGENTS_DIR"/*.md; do
  [ "$f" = "$CONTEXT_FILE" ] && continue
  [ -f "$f" ] || continue
  bname=$(basename "$f")
  if ! grep -q "$bname" "$CONTEXT_FILE" 2>/dev/null; then
    if $fresh; then echo ""; echo "Freshness warnings:"; fresh=false; fi
    echo "  - .agents/$bname exists but is not referenced in CONTEXT.md"
  fi
done

# References in CONTEXT.md to files that don't exist
for linked in $(grep -oE '\([a-zA-Z0-9_-]+\.md\)' "$CONTEXT_FILE" 2>/dev/null | tr -d '()'); do
  if [ ! -f "$AGENTS_DIR/$linked" ]; then
    if $fresh; then echo ""; echo "Freshness warnings:"; fresh=false; fi
    echo "  - CONTEXT.md references $linked but file not found in .agents/"
  fi
done

exit 0
