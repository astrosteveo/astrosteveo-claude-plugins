#!/bin/bash
# SessionEnd hook: Commit uncommitted work and flag for next session
#
# If there are uncommitted changes when the session ends, commit them
# and add a resume note to CLAUDE.md so the next session can surface
# what happened and ask the user if they want to resume.

# Not a git repo — nothing to do
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

# Check for uncommitted changes
git add -A
git diff --cached --quiet && exit 0

# Capture the list of files being committed
changed_files=$(git diff --cached --name-only)

# Commit the uncommitted work
git commit -m "chore: commit uncommitted work (session-end)" >/dev/null 2>&1

# Remove any existing resume note from CLAUDE.md before adding a new one
if [ -f "CLAUDE.md" ]; then
  if [ "$(uname)" = "Darwin" ]; then
    sed -i '' '/^## Session Resume Note$/,/^## End Session Resume Note$/d' CLAUDE.md
  else
    sed -i '/^## Session Resume Note$/,/^## End Session Resume Note$/d' CLAUDE.md
  fi
fi

# Append resume note to CLAUDE.md (create it if it doesn't exist)
file_list=$(echo "$changed_files" | sed 's/^/- /')
cat >> CLAUDE.md << RESUME_EOF

## Session Resume Note

The previous session ended with uncommitted changes that were auto-committed:
${file_list}

Ask the user if they would like to resume where the previous session left off.

## End Session Resume Note
RESUME_EOF

git add CLAUDE.md
git commit -m "chore: add session resume note" >/dev/null 2>&1
git push >/dev/null 2>&1

exit 0
