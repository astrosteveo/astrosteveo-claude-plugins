# Project Context

## Overview

Curated Claude Code plugins for engineers. The main plugin (`astrocode`) provides skills and hook-based workflows for cold-starting Claude Code in any project — including a skills-creator for building new skills and a project-state manager for persistent agent context.

## Stack

- **Language(s):** Markdown (skills/commands), Bash (hooks/scripts), Python (test tooling)
- **Framework(s):** Claude Code plugin system (skills, commands, hooks)
- **Build:** None — plugins are loaded directly by Claude Code
- **Test:** Manual via Claude Code conversations; Python-based test runner for skill validation
- **CI/CD:** None

## Topics

| Topic | File | Description |
|-------|------|-------------|
| Architecture | [architecture.md](architecture.md) | Plugin structure, skill patterns, hook system |
| Status | [status.md](status.md) | Current work streams, recent changes, next steps |
