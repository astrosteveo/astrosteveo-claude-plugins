#!/usr/bin/env bash
# Find all Claude Code auto-memory directories
set -euo pipefail

# head closes the pipe early once it has 20 lines, which sends SIGPIPE
# to find. Under pipefail that surfaces as a failure, so allow it.
memory_dirs=$(find ~/.claude/projects/ -type d -name "memory" 2>/dev/null | head -20) || true

if [ -z "$memory_dirs" ]; then
    echo "No Claude Code auto-memory directories found under ~/.claude/projects/."
    exit 0
fi

while IFS= read -r dir; do
    file_count=$(find "$dir" -maxdepth 1 -type f | wc -l)
    dir_size=$(du -sh "$dir" | cut -f1)
    echo "$dir"
    echo "  Files: $file_count"
    echo "  Size: $dir_size"
done <<< "$memory_dirs"
