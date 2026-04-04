#!/usr/bin/env bash
set -euo pipefail

RELATIVE_MEMORY_DIR=".claude/memory"
SETTINGS_FILE="${CLAUDE_PROJECT_DIR}/.claude/settings.local.json"

# Check if already configured
if [ -f "$SETTINGS_FILE" ]; then
  existing=$(jq -r '.autoMemoryDirectory // empty' "$SETTINGS_FILE" 2>/dev/null || true)
  if [ "$existing" = "$RELATIVE_MEMORY_DIR" ]; then
    echo "ALREADY_CONFIGURED"
    echo "autoMemoryDirectory is already set to: $RELATIVE_MEMORY_DIR"
    exit 0
  fi
fi

# Create directories
mkdir -p "$(dirname "$SETTINGS_FILE")"
mkdir -p "${CLAUDE_PROJECT_DIR}/${RELATIVE_MEMORY_DIR}"

# Write or merge settings
if [ -f "$SETTINGS_FILE" ]; then
  tmp=$(mktemp)
  jq --arg dir "$RELATIVE_MEMORY_DIR" '. + {"autoMemoryDirectory": $dir}' "$SETTINGS_FILE" > "$tmp"
  mv "$tmp" "$SETTINGS_FILE"
else
  jq -n --arg dir "$RELATIVE_MEMORY_DIR" '{"autoMemoryDirectory": $dir}' > "$SETTINGS_FILE"
fi

echo "SETUP_COMPLETE"
echo "Settings file: $SETTINGS_FILE"
echo "Memory directory: $RELATIVE_MEMORY_DIR"
echo "autoMemoryDirectory: $RELATIVE_MEMORY_DIR"
