# Status

> Part of [Project Context](CONTEXT.md)

## Current Work Streams

- **Project-state skill** — Recently added (2026-03-18). Manages vendor-neutral persistent state in `.agents/` with bootstrap and update flows. Supports multi-agent detection (Claude, Cursor, Copilot, Gemini, Windsurf).
- **Skills-creator skill** — Stable. Interactive guide for building new Claude skills with progressive reference docs and a Python-based testing framework.

## Recent Changes

| Date | Change | Commit |
|------|--------|--------|
| 2026-03-18 | Rewrote stop-gate hook: now uses git-diff to detect source vs .agents/ drift (replaces 5-min timestamp heuristic) | uncommitted |
| 2026-03-18 | Bootstrapped `.agents/` directory and `CLAUDE.md` with state pointer | uncommitted |
| 2026-03-18 | Added project-state skill with agent detection and context structure references | `e3aa0db` |
| 2026-03-18 | Added .gitignore for Python cache files | `7bc87bd` |
| 2026-03-18 | Added skill testing framework with real `claude -p` integration | `14578d6` |
| 2026-03-18 | Aligned skills-creator references with official docs | `36f5190` |
| 2026-03-18 | Removed deprecated skills (migration-check, perf-audit, plan, pre-deploy, review, session-reflect) | `b249036` |

## Known Issues

- None detected

## Next Steps

1. Commit `.agents/`, `CLAUDE.md`, and stop-gate.sh changes
2. Test `project-state` skill bootstrap and update flows in real projects
3. Iterate on skills-creator based on usage feedback
4. Consider adding more skills to the astrocode plugin as workflows stabilize
