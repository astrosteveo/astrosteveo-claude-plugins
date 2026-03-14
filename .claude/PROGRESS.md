# Project Progress

> Last updated: 2026-03-14 | Last synced at: cadaba1

## Active Work Streams

- Skills-creator plugin complete as standalone plugin
- Astrocode plugin: commands as namespaced entry points, skills hidden from `/` menu

## Recent Changes

| Date | Change | Files/Areas |
|------|--------|-------------|
| 2026-03-14 | Genericized all skills for project-agnostic usage: removed Node.js-specific, SaaS-specific, and business-specific examples; fixed cross-platform sed in session-end.sh | `plugins/astrocode/skills/*/SKILL.md`, `scripts/session-end.sh` |
| 2026-03-14 | Added standalone `commit` skill; refactored `project-state` to focus on PROGRESS.md lifecycle; updated `review-cycle` and `stop-check.sh` to reference commit skill | `plugins/astrocode/skills/commit/`, `commands/commit.md`, `skills/project-state/`, `skills/review-cycle/`, `scripts/stop-check.sh` |
| 2026-03-13 | Set `user-invocable: false` on all skills; commands are the user-facing entry points | `plugins/astrocode/skills/*/SKILL.md` |
| 2026-03-13 | Added thin wrapper commands for all 5 skills | `plugins/astrocode/commands/` |
| 2026-03-13 | Added code-health and security-audit skills | `plugins/astrocode/skills/code-health/`, `plugins/astrocode/skills/security-audit/` |
| 2026-03-10 | Added skills-creator skill with 7 progressive reference docs | `plugins/skills-creator/` |
| 2026-03-10 | Moved skills-creator to its own plugin (out of astrocode) | `plugins/skills-creator/`, `marketplace.json` |

## Architecture & Key Decisions

- **Plugin structure:** Each plugin lives under `plugins/{name}/` with `.claude-plugin/plugin.json`
- **astrocode plugin:** `plugins/astrocode/` — hooks + skills + thin wrapper commands
- **skills-creator plugin:** `plugins/skills-creator/` — standalone skill for building skills
- **Skills pattern:** Each skill is a kebab-case folder under `plugins/{plugin}/skills/` with `SKILL.md` + optional `references/`, `scripts/`, `assets/`. Skills set `user-invocable: false` so they don't appear un-namespaced in the `/` menu.
- **Commands pattern:** Thin `.md` wrappers in `plugins/{plugin}/commands/` that delegate to corresponding skills; `name` omitted from frontmatter to inherit as `plugin:filename`. These are the user-facing entry points (namespaced in `/` menu).
- **Progressive disclosure:** Large reference material decomposed into numbered `references/*.md` files loaded on demand rather than inlined in SKILL.md
- **Commit standard:** `astrocode:commit` skill owns the conventional commit format; other skills reference it for all commit operations
- **Hooks:** Stop hook enforces commit discipline + PROGRESS.md freshness; SessionEnd hook timestamps PROGRESS.md

## Known Issues & Blockers

- None detected

## Next Steps

1. Test skills-creator skill in a real conversation to verify triggering and workflow
2. Consider adding more skills to the astrocode plugin
3. Iterate on skills-creator based on usage feedback

## Project Context

- **Project:** astrosteveo-claude-plugins — curated Claude Code plugins for engineers
- **Stack:** Markdown skills + Bash hook scripts
- **Build/Run:** No build step; plugins are loaded by Claude Code directly
- **Test:** Manual testing via Claude Code conversations
