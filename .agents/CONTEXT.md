# Project Context

## Overview

Curated Claude Code plugins for engineers. The main plugin (`astrocode`) provides skills and hook-based workflows for cold-starting Claude Code in any project — including a skills-creator for building new skills and a project-state manager for persistent agent context.

## Stack

- **Language(s):** Markdown (skills/commands), Bash (hooks/scripts), Python (test tooling)
- **Framework(s):** Claude Code plugin system (skills, commands, hooks)
- **Build:** None — plugins are loaded directly by Claude Code
- **Test:** Manual via Claude Code conversations; Python-based test runner for skill validation
- **CI/CD:** None

## Structure

```
astrosteveo-claude-plugins/
├── .agents/                  # Persistent agent state (this directory)
├── .claude-plugin/           # Top-level plugin marketplace metadata
│   └── marketplace.json
├── plugins/
│   └── astrocode/            # Main plugin
│       ├── .claude-plugin/   # Plugin manifest
│       ├── hooks/            # Hook definitions (hooks.json)
│       ├── scripts/          # Bash hook scripts (session-start, session-end, stop-gate)
│       └── skills/           # Skill definitions
│           ├── project-state/  # Persistent agent state management
│           └── skills-creator/ # Interactive skill building guide
│               └── templates/  # Reusable templates (e.g., TESTS.yaml)
├── .gitignore
└── The-Complete-Guide-to-Building-Skills-for-Claude.md
```

## Active Work

- Two active skills: `project-state` and `skills-creator`
- Stop-gate uses git-diff detection (no timestamps)
- Session-end hook commits and pushes all uncommitted work

## Topics

| Topic | File | Description |
|-------|------|-------------|
| Architecture | [architecture.md](architecture.md) | Plugin structure, skill patterns, hook system |
| Status | [status.md](status.md) | Current work streams, recent changes, next steps |
