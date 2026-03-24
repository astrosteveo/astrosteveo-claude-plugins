# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin repository with two plugins — **project-state** (session continuity and git discipline hooks) and **skills-creator** (interactive skill builder). The codebase is pure Markdown (skills), Bash (hook scripts), and Python (test tooling). There is no build step; plugins are loaded directly by Claude Code.

## Architecture

### Plugin Layout

Each plugin lives under `plugins/{name}/` with its own `.claude-plugin/plugin.json` manifest. The top-level `.claude-plugin/marketplace.json` is the registry index.

Two plugins:
- **`project-state`** (`plugins/project-state/`) — session continuity and git discipline hooks; no skills
- **`skills-creator`** (`plugins/skills-creator/`) — interactive 6-phase workflow for building new Claude skills

### Skills

Each skill is a kebab-case folder under `plugins/{plugin}/skills/{skill-name}/` containing:
- `SKILL.md` — frontmatter (name, description, triggers) + instructions body
- `references/` — numbered progressive-disclosure docs loaded on demand (e.g., `01-fundamentals.md`)
- `scripts/` — automation scripts
- `TESTS.yaml` — trigger and behavioral test spec

### Hooks

Defined in `plugins/project-state/hooks/hooks.json`, backed by Bash scripts in `plugins/project-state/scripts/`:

| Hook | Script | Behavior |
|------|--------|----------|
| SessionStart | `session-start.sh` | Surfaces resume notes from previous sessions; does not auto-clean them |
| PreToolUse | `pre-tool-guard.sh` | Blocks dangerous git commands (broad staging, force push, hard reset, git clean, checkout --) |
| PostCompact | `post-compact.sh` | Re-injects dirty state and recent commits after context compaction |
| Stop | `stop-gate.sh` | Blocks stop if there are any uncommitted changes; reports all dirty state categorized for single-turn resolution |
| SessionEnd | `session-end.sh` | Records uncommitted state in a CLAUDE.md resume note; does not commit or push |

Key design principles:
- Hooks never auto-commit or auto-push. They record state and let the agent/user decide what to do.
- Hooks are generic about git conventions — they enforce *that* you commit, not *how* you format the message. Commit style is left to the user's personal rules or project CLAUDE.md.
- PreToolUse hook receives JSON tool input on `stdin` (relevant for debugging and writing test scenarios).
- `session-end.sh` has macOS/Linux branching for `sed -i` — the only script with platform-specific logic.

## Testing Skills

Skill tests use a YAML-based spec (`TESTS.yaml`) with three layers:

```bash
# Layer 1 — structural validation
python plugins/skills-creator/skills/skills-creator/scripts/validate-structure.py /path/to/skill

# Layer 2 — trigger tests only
python plugins/skills-creator/skills/skills-creator/scripts/run-tests.py /path/to/skill --layer 2

# Full suite (all layers)
python plugins/skills-creator/skills/skills-creator/scripts/run-tests.py /path/to/skill
```

Test scripts live in the skills-creator skill since it owns the testing framework. Skill `TESTS.yaml` files configure model, max turns, and per-test/total cost budgets.

## Testing Hooks

Hook tests use a YAML-based spec (`hooks/TESTS.yaml`) with two layers:

- **Structural** — validates `hooks.json` schema and script syntax (free, no execution)
- **Scenarios** — runs each hook script in an isolated git repo, asserting on exit codes, stdout/stderr, file state, and git history. PreToolUse scenarios use `stdin` to pass JSON tool input.

```bash
# Run all hook tests
python plugins/project-state/scripts/test-hooks.py

# Run tests for a specific hook
python plugins/project-state/scripts/test-hooks.py --hook stop-gate

# Run a single scenario
python plugins/project-state/scripts/test-hooks.py --scenario unstaged-modifications

# JSON output
python plugins/project-state/scripts/test-hooks.py --json

# Show plan without running
python plugins/project-state/scripts/test-hooks.py --dry-run
```

## Conventions

- All skills must be project-agnostic — no language-specific, SaaS-specific, or business-specific assumptions
- SKILL.md files must stay under 500 lines; decompose into `references/` for large docs
- Folder names are kebab-case and must match the `name` field in SKILL.md frontmatter
- No XML angle brackets in SKILL.md files
- Hook scripts must handle both macOS and Linux (e.g., `sed -i ''` vs `sed -i` for in-place edits)
