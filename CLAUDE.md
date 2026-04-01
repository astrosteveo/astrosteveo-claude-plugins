# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin repository with six plugins — **commit** (Conventional Commits), **skill-creator** (interactive skill builder), **godot-dev** (Godot 4.x guidance), **code-quality** (codebase quality review), **reconcile-memory** (memory audit and cleanup), and **develop** (end-to-end development workflow). The codebase is pure Markdown (skills), Bash (scripts), and Python (test tooling). There is no build step; plugins are loaded directly by Claude Code.

## Architecture

### Plugin Layout

Each plugin lives under `plugins/{name}/` with its own `.claude-plugin/plugin.json` manifest. The top-level `.claude-plugin/marketplace.json` is the registry index.

Six plugins:
- **`commit`** (`plugins/commit/`) — Conventional Commits skill; analyzes diffs, groups changes into logical units, creates one commit per unit
- **`skill-creator`** (`plugins/skill-creator/`) — interactive 6-phase workflow for building new Claude skills
- **`godot-dev`** (`plugins/godot-dev/`) — Godot 4.x development guidance with architecture patterns, conventions, and MCP workflow; extensive reference docs
- **`code-quality`** (`plugins/code-quality/`) — two skills: **code-quality** for comprehensive codebase audits (clean code, DRY, security, performance, best practices; context-first analysis with non-breaking recommendations) and **code-sniffer** for detecting code smells and AI-generated slop (cargo-culted patterns, ceremonial error handling, vibe-coded signals, ceremony-to-substance ratio)
- **`reconcile-memory`** (`plugins/reconcile-memory/`) — audit and reconcile auto-memory files: deduplication, contradiction detection, staleness assessment, context hygiene
- **`develop`** (`plugins/develop/`) — end-to-end development workflow with adaptive phases for features, bug fixes, refactors, and substantial code changes; TDD-driven with user gates between every phase

### Skills

Each skill is a kebab-case folder under `plugins/{plugin}/skills/{skill-name}/` containing:
- `SKILL.md` — frontmatter (name, description, triggers) + instructions body
- `references/` — numbered progressive-disclosure docs loaded on demand (e.g., `01-fundamentals.md`)
- `scripts/` — automation scripts
- `TESTS.yaml` — trigger and behavioral test spec

## Testing Skills

Skill tests use a YAML-based spec (`TESTS.yaml`) with three layers:

```bash
# Layer 1 — structural validation
python plugins/skill-creator/skills/skill-creator/scripts/validate-structure.py /path/to/skill

# Layer 2 — trigger tests only
python plugins/skill-creator/skills/skill-creator/scripts/run-tests.py /path/to/skill --layer 2

# Full suite (all layers)
python plugins/skill-creator/skills/skill-creator/scripts/run-tests.py /path/to/skill
```

Test scripts live in the skill-creator skill since it owns the testing framework. Layer 1 is free (structural checks only); Layers 2 and 3 spawn headless `claude -p` processes and consume API tokens — always confirm with the user before running them. Skill `TESTS.yaml` files configure model, max turns, and per-test/total cost budgets.

Additional `run-tests.py` options:
```bash
# Layer 1 only (structural, free, instant)
python plugins/skill-creator/skills/skill-creator/scripts/run-tests.py /path/to/skill --layer 1

# Parallel execution (4 workers)
python plugins/skill-creator/skills/skill-creator/scripts/run-tests.py /path/to/skill --parallel 4

# Flakiness detection (run 3 times)
python plugins/skill-creator/skills/skill-creator/scripts/run-tests.py /path/to/skill --runs 3

# Compare against baseline
python plugins/skill-creator/skills/skill-creator/scripts/run-tests.py /path/to/skill --compare latest
```

## Conventions

- All skills must be project-agnostic — no language-specific, SaaS-specific, or business-specific assumptions
- SKILL.md files must stay under 500 lines; decompose into `references/` for large docs
- Folder names are kebab-case and must match the `name` field in SKILL.md frontmatter
- No XML angle brackets in SKILL.md files
