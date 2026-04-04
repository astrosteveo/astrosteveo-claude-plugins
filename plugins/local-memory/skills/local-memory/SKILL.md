---
name: local-memory
description: Configure auto-memory to live inside the project directory so it can be version controlled. Creates .claude/settings.local.json with autoMemoryDirectory pointing to .claude/memory/. Use when the user says "local memory", "setup local memory", "project memory", runs /local-memory, or wants auto-memory stored in the repo instead of ~/.claude/projects/.
---

# Local Memory Setup

Configure this project's auto-memory to live inside the project directory.

## Instructions

1. Tell the user you're setting up local project memory, then run the setup script:

!`bash ${CLAUDE_SKILL_DIR}/scripts/setup-local-memory.sh`

2. Read the script output and tell the user:
   - If `ALREADY_CONFIGURED`: memory is already set up, no changes needed
   - If `SETUP_COMPLETE`: `.claude/settings.local.json` now has `autoMemoryDirectory` set to `.claude/memory/`, the directory was created, both should be committed to version control, and the setting takes effect next session (restart Claude Code)
