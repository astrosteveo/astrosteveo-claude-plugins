# Project Context

## Overview

Curated Claude Code plugins for engineers. Two plugins: **project-state** (persistent agent context management with session hooks) and **skills-creator** (interactive guide for building new skills).

## Stack

- **Language(s):** Markdown (skills), Bash (hooks/scripts), Python (test tooling)
- **Framework(s):** Claude Code plugin system (skills, hooks)
- **Build:** None — plugins are loaded directly by Claude Code
- **Test:** Manual via Claude Code conversations; Python-based test runner for skill validation
- **CI/CD:** None

## Topics

| Topic | File | Description |
|-------|------|-------------|
| Architecture | [architecture.md](architecture.md) | Plugin structure, skill patterns, hook system |
| Status | [status.md](status.md) | Current work streams, recent changes, next steps |
