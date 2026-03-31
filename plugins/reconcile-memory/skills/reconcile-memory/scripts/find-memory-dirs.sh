#!/usr/bin/env bash
# Find all Claude Code auto-memory directories
set -euo pipefail

memory_dirs=$(find ~/.claude/projects/ -type d -name "memory" 2>/dev/null | head -20) || true

if [ -z "$memory_dirs" ]; then
    echo "NO_MEMORY_DIRS_FOUND"
    exit 0
fi

while IFS= read -r dir; do
    file_count=$(ls "$dir" 2>/dev/null | wc -l) || true
    dir_size=$(du -sh "$dir" 2>/dev/null | cut -f1) || true
    echo "$dir"
    echo "  Files: $file_count"
    echo "  Size: $dir_size"
done <<< "$memory_dirs"
