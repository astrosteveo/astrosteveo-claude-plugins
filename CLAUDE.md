# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin repository. Each plugin packages one or more skills (and optionally hooks) for distribution via the marketplace. The codebase is pure Markdown (skills), Bash (scripts), and Python (test tooling). There is no build step; plugins are loaded directly by Claude Code.

## Architecture

### Plugin Layout

The top-level `.claude-plugin/marketplace.json` is the registry index. Each plugin lives under `plugins/{name}/` with its own `.claude-plugin/plugin.json` manifest.

Current plugins:
- **`commit`** — Conventional Commits skill
- **`skills-creator`** — interactive 6-phase workflow for building new Claude skills; also owns the shared test framework (`scripts/validate-structure.py`, `scripts/run-tests.py`)
- **`godot-dev`** — Godot 4.x development conventions and patterns

### Skill Structure

Each skill is a kebab-case folder under `plugins/{plugin}/skills/{skill-name}/` containing:
- `SKILL.md` — YAML frontmatter (name, description, triggers) + instructions body
- `references/` — numbered progressive-disclosure docs loaded on demand
- `scripts/` — automation scripts (optional)
- `TESTS.yaml` — trigger and behavioral test spec

### Two-level Registry

Adding a new plugin requires entries in both:
1. `plugins/{name}/.claude-plugin/plugin.json` — plugin manifest
2. `.claude-plugin/marketplace.json` — top-level registry (array entry under `plugins`)

## Testing

Skill tests use a YAML-based spec (`TESTS.yaml`) with three layers. Test scripts live in the skills-creator plugin.

```bash
# Layer 1 — structural validation (free, no LLM calls)
python plugins/skills-creator/skills/skills-creator/scripts/validate-structure.py /path/to/skill

# Layer 2 — trigger tests only
python plugins/skills-creator/skills/skills-creator/scripts/run-tests.py /path/to/skill --layer 2

# Full suite (all layers)
python plugins/skills-creator/skills/skills-creator/scripts/run-tests.py /path/to/skill
```

`TESTS.yaml` files configure model, max turns, and per-test/total cost budgets.

## Conventions

- All skills must be project-agnostic — no language-specific, SaaS-specific, or business-specific assumptions
- SKILL.md files must stay under 500 lines; decompose into `references/` for large docs
- Folder names are kebab-case and must match the `name` field in SKILL.md frontmatter
- No XML angle brackets in SKILL.md files
