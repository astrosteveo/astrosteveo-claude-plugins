# Architecture

> Part of [Project Context](CONTEXT.md)

## Plugin Structure

Each plugin lives under `plugins/{name}/` with its own `.claude-plugin/plugin.json` manifest. The top-level `.claude-plugin/marketplace.json` indexes all plugins in the repository.

Two plugins:
- **project-state** (`plugins/project-state/`) — agent state management + session hooks
- **skills-creator** (`plugins/skills-creator/`) — interactive skill builder

## Skills Pattern

- Each skill is a kebab-case folder under `plugins/{plugin}/skills/{skill-name}/`
- Required: `SKILL.md` with frontmatter (name, description, triggers)
- Optional: `references/` for progressive-disclosure docs, `scripts/` for automation, `assets/` for static files, `TESTS.yaml` for validation
- Skills are invoked via namespace (e.g., `project-state:project-state`, `skills-creator:skills-creator`)

## Progressive Disclosure

Large reference material is decomposed into numbered `references/*.md` files (e.g., `01-fundamentals.md`, `02-frontmatter.md`) that are loaded on demand rather than inlined in SKILL.md. This keeps the initial skill prompt small.

## Hook System

Hooks are defined in `plugins/project-state/hooks/hooks.json` and backed by Bash scripts in `plugins/project-state/scripts/`:

| Script | Purpose |
|--------|---------|
| `session-start.sh` | Surfaces resume notes, outputs curated context from CONTEXT.md, dynamically generates structure tree and recent activity, and runs freshness checks on topic file references |
| `session-end.sh` | Commits all uncommitted work and adds a resume note to CLAUDE.md for the next session |
| `stop-gate.sh` | Two-phase gate: blocks stop if source files changed but `.agents/` wasn't updated (git-diff), and enforces commit before session end |

## Hook Testing

Hook tests are defined in `plugins/project-state/hooks/TESTS.yaml` with structural and scenario layers. The test runner (`plugins/project-state/scripts/test-hooks.py`) validates `hooks.json` schema, script syntax, and runs scenarios in isolated git repos.

## Dynamic vs Curated Context

CONTEXT.md contains only curated, slow-changing content (Overview, Stack, Topics table). The session-start hook supplements it with live data generated from the actual project state:

- **Structure** — directory tree generated from the filesystem via `tree` (with `find` fallback)
- **Recent Activity** — last 10 commits from `git log`
- **Freshness warnings** — alerts when topic files exist on disk but aren't linked in CONTEXT.md, or vice versa

This eliminates staleness for the most volatile context. Curated sections are maintained by the `project-state` skill's update flow.

## Key Conventions

- Conventional commit messages (e.g., `feat(skill-name):`, `fix(skill-name):`, `chore:`)
- `.agents/` is the primary vendor-neutral project state mechanism
- All skills are project-agnostic — no language-specific, SaaS-specific, or business-specific assumptions
- Hook scripts handle both macOS and Linux for cross-platform support
