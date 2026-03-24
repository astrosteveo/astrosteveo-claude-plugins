#!/bin/bash
# PreToolUse hook (Bash matcher): Block dangerous git commands
#
# Prevents broad staging, force pushes, and destructive resets before
# they execute. Reads the tool input from stdin as JSON.

# Read the tool input JSON from stdin
input=$(cat)

# Extract the command being run
command=$(echo "$input" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"command"[[:space:]]*:[[:space:]]*"//;s/"$//')

# If we can't extract a command, allow it (don't block non-Bash tools)
if [ -z "$command" ]; then
  exit 0
fi

# ── Broad staging commands ────────────────────────────────────
# Block: git add -A, git add --all, git add .
if echo "$command" | grep -qE 'git\s+add\s+(-A|--all|\.)'; then
  cat <<'EOF'
{"decision":"block","reason":"Broad staging commands (git add -A, git add --all, git add .) are not allowed. Stage specific files by name instead. This prevents accidentally staging scratch files, credentials, or files not yet in .gitignore."}
EOF
  exit 0
fi

# ── Force push ────────────────────────────────────────────────
if echo "$command" | grep -qE 'git\s+push\s+.*(-f|--force|--force-with-lease)'; then
  cat <<'EOF'
{"decision":"block","reason":"Force push is not allowed. If you need to update a remote branch, discuss with the user first. Force pushing can destroy commit history for collaborators."}
EOF
  exit 0
fi

# ── Destructive resets ────────────────────────────────────────
if echo "$command" | grep -qE 'git\s+reset\s+--hard'; then
  cat <<'EOF'
{"decision":"block","reason":"Hard reset is not allowed. This discards uncommitted work permanently. If you need to undo changes, use git stash or git checkout on specific files, and confirm with the user first."}
EOF
  exit 0
fi

# ── Destructive clean ────────────────────────────────────────
if echo "$command" | grep -qE 'git\s+clean\s+-[a-zA-Z]*f'; then
  cat <<'EOF'
{"decision":"block","reason":"git clean -f is not allowed. This permanently deletes untracked files. Confirm with the user before removing untracked files."}
EOF
  exit 0
fi

# ── Checkout that discards changes ────────────────────────────
if echo "$command" | grep -qE 'git\s+checkout\s+--\s+\.'; then
  cat <<'EOF'
{"decision":"block","reason":"git checkout -- . discards all unstaged changes permanently. Use git checkout on specific files if needed, and confirm with the user first."}
EOF
  exit 0
fi

# Allow everything else
exit 0
