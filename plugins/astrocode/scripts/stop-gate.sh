#!/bin/bash
# Stop hook: Two-phase gate ensuring work is documented and committed
#
# Phase 1: If source files changed but .agents/ wasn't updated, block
#          until the agent updates project state.
# Phase 2: If there are any uncommitted changes, block until the agent
#          commits with a descriptive message.
#
# This ensures each unit of work is both documented (.agents/) and
# committed before the agent finishes responding.

AGENTS_DIR=".agents"

# Not a git repo — can't enforce, allow stop
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

# ── Phase 1: .agents/ freshness ──────────────────────────────────
# Only enforced when .agents/ directory exists
if [ -d "$AGENTS_DIR" ]; then
  source_changes=$(git diff HEAD --name-only -- . ':(exclude).agents' 2>/dev/null)
  untracked_source=$(git ls-files --others --exclude-standard -- . ':(exclude).agents' 2>/dev/null)

  if [ -n "$source_changes" ] || [ -n "$untracked_source" ]; then
    agents_changes=$(git diff HEAD --name-only -- .agents/ 2>/dev/null)
    untracked_agents=$(git ls-files --others --exclude-standard -- .agents/ 2>/dev/null)

    if [ -z "$agents_changes" ] && [ -z "$untracked_agents" ]; then
      echo "BLOCKED: Source files have changed but .agents/ has not been updated." >&2
      echo "You must update project state before stopping:" >&2
      echo "  1. Update the relevant topic files in .agents/ to reflect your changes" >&2
      echo "  2. Refresh .agents/CONTEXT.md with current status" >&2
      exit 2
    fi
  fi
fi

# ── Phase 2: Uncommitted work ───────────────────────────────────
# Block if there are staged, unstaged, or untracked changes
if ! git diff --cached --quiet 2>/dev/null \
   || ! git diff --quiet 2>/dev/null \
   || [ -n "$(git ls-files --others --exclude-standard 2>/dev/null)" ]; then
  echo "BLOCKED: You have uncommitted changes." >&2
  echo "Stage only the files from your current unit of work and commit with a descriptive message." >&2
  echo "Do not use 'git add -A'. Make a targeted commit for the work you just completed." >&2
  exit 2
fi

exit 0
