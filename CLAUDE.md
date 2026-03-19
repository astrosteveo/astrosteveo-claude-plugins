# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin repository providing the **astrocode** plugin — a collection of skills, hooks, and commands for cold-starting Claude Code in any project. The codebase is pure Markdown (skills/commands), Bash (hook scripts), and Python (test tooling). There is no build step; plugins are loaded directly by Claude Code.

## Architecture

### Plugin Layout

The sole plugin lives at `plugins/astrocode/`. Its manifest is at `plugins/astrocode/.claude-plugin/plugin.json`. The top-level `.claude-plugin/marketplace.json` is the registry index.

### Skills

Each skill is a kebab-case folder under `plugins/astrocode/skills/{skill-name}/` containing:
- `SKILL.md` — frontmatter (name, description, triggers) + instructions body
- `references/` — numbered progressive-disclosure docs loaded on demand (e.g., `01-fundamentals.md`)
- `scripts/` — automation scripts
- `TESTS.yaml` — trigger and behavioral test spec

Skills set `user-invocable: false`; user-facing entry points are thin `.md` command wrappers in `plugins/astrocode/commands/` (currently removed — skills are invoked directly via namespace).

Two active skills:
- **`project-state`** — bootstraps/updates vendor-neutral `.agents/` state for multi-agent session continuity
- **`skills-creator`** — interactive 6-phase workflow for building new Claude skills

### Hooks

Defined in `plugins/astrocode/hooks/hooks.json`, backed by Bash scripts in `plugins/astrocode/scripts/`:

| Hook | Script | Behavior |
|------|--------|----------|
| SessionStart | `session-start.sh` | Outputs `.agents/CONTEXT.md` to orient the agent |
| Stop | `stop-gate.sh` | Blocks stop if `.agents/` exists but wasn't updated in last 5 min |
| SessionEnd | `session-end.sh` | Best-effort timestamp update on CONTEXT.md |

### `.agents/` Directory

Committed to git. Contains `CONTEXT.md` (thin index) and topic files (`architecture.md`, `status.md`). This is the vendor-neutral project state that any AI agent can read. The stop hook enforces freshness.

## Testing Skills

Skill tests use a YAML-based spec (`TESTS.yaml`) with three layers:

```bash
# Layer 1 — structural validation
python plugins/astrocode/skills/skills-creator/scripts/validate-structure.py /path/to/skill

# Layer 2 — trigger tests only
python plugins/astrocode/skills/skills-creator/scripts/run-tests.py /path/to/skill --layer 2

# Full suite (all layers)
python plugins/astrocode/skills/skills-creator/scripts/run-tests.py /path/to/skill
```

Test scripts live in the skills-creator skill since it owns the testing framework.

## Conventions

- All skills must be project-agnostic — no language-specific, SaaS-specific, or business-specific assumptions
- SKILL.md files must stay under 500 lines; decompose into `references/` for large docs
- Folder names are kebab-case and must match the `name` field in SKILL.md frontmatter
- No XML angle brackets in SKILL.md files
- Conventional commit messages (e.g., `feat(skill-name):`, `fix(skill-name):`, `chore:`)
- Hook scripts must handle both macOS (`stat -f`) and Linux (`stat -c`) for cross-platform support

## Project State

This project maintains persistent agent state in `.agents/`.
Read `.agents/CONTEXT.md` at the start of each session to orient yourself.
Update the relevant files in `.agents/` after completing meaningful units of work.
