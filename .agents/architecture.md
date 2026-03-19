# Architecture

> Part of [Project Context](CONTEXT.md)

## Plugin Structure

Each plugin lives under `plugins/{name}/` with its own `.claude-plugin/plugin.json` manifest. The top-level `.claude-plugin/marketplace.json` indexes all plugins in the repository.

Currently one plugin exists: **astrocode** (`plugins/astrocode/`).

## Skills Pattern

- Each skill is a kebab-case folder under `plugins/{plugin}/skills/{skill-name}/`
- Required: `SKILL.md` with frontmatter (name, description, triggers)
- Optional: `references/` for progressive-disclosure docs, `scripts/` for automation, `assets/` for static files, `TESTS.yaml` for validation
- Skills set `user-invocable: false` — they don't appear un-namespaced in the `/` menu
- Commands (thin `.md` wrappers in `plugins/{plugin}/commands/`) are the user-facing entry points, namespaced as `plugin:command`

## Progressive Disclosure

Large reference material is decomposed into numbered `references/*.md` files (e.g., `01-fundamentals.md`, `02-frontmatter.md`) that are loaded on demand rather than inlined in SKILL.md. This keeps the initial skill prompt small.

## Hook System

Hooks are defined in `plugins/astrocode/hooks/hooks.json` and backed by Bash scripts in `plugins/astrocode/scripts/`:

| Script | Purpose |
|--------|---------|
| `session-start.sh` | Surfaces resume notes from CLAUDE.md, then outputs `.agents/CONTEXT.md` to orient the agent |
| `session-end.sh` | Commits all uncommitted work and adds a resume note to CLAUDE.md for the next session |
| `stop-gate.sh` | Two-phase gate: blocks stop if source files changed but `.agents/` wasn't updated (git-diff), and enforces commit before session end |

## Hook Testing

Hook tests are defined in `plugins/astrocode/hooks/TESTS.yaml` with structural and scenario layers. The test runner (`plugins/astrocode/scripts/test-hooks.py`) validates `hooks.json` schema, script syntax, and runs scenarios in isolated git repos.

## Key Conventions

- Conventional commit messages (e.g., `feat(skill-name):`, `fix(skill-name):`, `chore:`)
- `.agents/` is the primary vendor-neutral project state mechanism
- All skills are project-agnostic — no language-specific, SaaS-specific, or business-specific assumptions
- Hook scripts handle both macOS and Linux for cross-platform support
