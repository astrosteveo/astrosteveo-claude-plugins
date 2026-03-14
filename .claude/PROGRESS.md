# Project Progress

> Last updated: 2026-03-14 | Last synced at: 17c719c

## Active Work Streams

- Skills-creator plugin complete as standalone plugin
- Astrocode plugin: commands as namespaced entry points, skills hidden from `/` menu

## Recent Changes

| Date | Change | Files/Areas |
|------|--------|-------------|
| 2026-03-14 | Added `plan` skill (feature scoping/design) and unified `review` skill (merges code-review, code-health, security-audit, review-cycle into one skill with auto-detected modes); deleted merged skills; updated cross-references in commit and pre-deploy | `plugins/astrocode/skills/plan/`, `skills/review/`, `commands/plan.md`, `commands/review.md`, `skills/commit/`, `skills/pre-deploy/` |
| 2026-03-14 | Genericized all skills for project-agnostic usage: removed Node.js-specific, SaaS-specific, and business-specific examples; fixed cross-platform sed in session-end.sh | `plugins/astrocode/skills/*/SKILL.md`, `scripts/session-end.sh` |
| 2026-03-14 | Added standalone `commit` skill; refactored `project-state` to focus on PROGRESS.md lifecycle; updated cross-references | `plugins/astrocode/skills/commit/`, `commands/commit.md`, `skills/project-state/` |
| 2026-03-13 | Set `user-invocable: false` on all skills; commands are the user-facing entry points | `plugins/astrocode/skills/*/SKILL.md` |
| 2026-03-13 | Added thin wrapper commands for all skills | `plugins/astrocode/commands/` |
| 2026-03-10 | Added skills-creator skill with 7 progressive reference docs | `plugins/skills-creator/` |

## Architecture & Key Decisions

- **Plugin structure:** Each plugin lives under `plugins/{name}/` with `.claude-plugin/plugin.json`
- **astrocode plugin:** `plugins/astrocode/` — hooks + skills + thin wrapper commands
- **skills-creator plugin:** `plugins/skills-creator/` — standalone skill for building skills
- **Skills pattern:** Each skill is a kebab-case folder under `plugins/{plugin}/skills/` with `SKILL.md` + optional `references/`, `scripts/`, `assets/`. Skills set `user-invocable: false` so they don't appear un-namespaced in the `/` menu.
- **Commands pattern:** Thin `.md` wrappers in `plugins/{plugin}/commands/` that delegate to corresponding skills; `name` omitted from frontmatter to inherit as `plugin:filename`. These are the user-facing entry points (namespaced in `/` menu).
- **Progressive disclosure:** Large reference material decomposed into numbered `references/*.md` files loaded on demand rather than inlined in SKILL.md
- **Commit standard:** `astrocode:commit` skill owns the conventional commit format; other skills reference it for all commit operations
- **Hooks:** Stop hook enforces commit discipline + PROGRESS.md freshness; SessionEnd hook timestamps PROGRESS.md
- **Skill consolidation:** Review-related skills (code-review, code-health, security-audit, review-cycle) merged into unified `review` skill with 3 auto-detected modes: PR, audit, fix

## Known Issues & Blockers

- None detected

## Next Steps

1. Test `plan` and `review` skills in real conversations to verify triggering and mode detection
2. Consider whether `perf-audit` should remain standalone or fold into `review` audit mode
3. Iterate on skills-creator based on usage feedback

## Project Context

- **Project:** astrosteveo-claude-plugins — curated Claude Code plugins for engineers
- **Stack:** Markdown skills + Bash hook scripts
- **Build/Run:** No build step; plugins are loaded by Claude Code directly
- **Test:** Manual testing via Claude Code conversations
