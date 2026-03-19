# Status

> Part of [Project Context](CONTEXT.md)

## Current Work Streams

- **Project-state skill** — Manages vendor-neutral persistent state in `.agents/` with bootstrap and update flows. Supports multi-agent detection (Claude, Cursor, Copilot, Gemini, Windsurf). SKILL.md trimmed to delegate detail to reference files via progressive disclosure.
- **Skills-creator skill** — Stable. Interactive guide for building new Claude skills with progressive reference docs and a Python-based testing framework.

## Recent Changes

| Date | Change | Commit |
|------|--------|--------|
| 2026-03-19 | Project-state SKILL.md trimmed: removed inline agent table, pointer template, optional topic list, examples, troubleshooting — all delegated to reference files | pending |
| 2026-03-19 | Session-end hook: commit all uncommitted work + add resume note to CLAUDE.md; session-start hook: surface and clean up resume notes | pending |
| 2026-03-19 | Removed timestamp logic from session-end hook and CONTEXT.md — state is commit-based, not time-based | `94adba3` |
| 2026-03-19 | Session-end hook now commits and pushes all uncommitted work | `89fb892` |
| 2026-03-19 | Stop-gate rewritten to use git-diff detection; `.agents/` and `CLAUDE.md` committed | `010b772`, `404639a` |
| 2026-03-18 | Added project-state skill with agent detection and context structure references | `e3aa0db` |
| 2026-03-18 | Added skill testing framework with real `claude -p` integration | `14578d6` |
| 2026-03-18 | Removed deprecated skills (migration-check, perf-audit, plan, pre-deploy, review, session-reflect) | `b249036` |

## Known Issues

- None detected

## Next Steps

1. Test session-end → session-start resume note handoff end-to-end
2. Test `project-state` skill bootstrap and update flows in real projects
3. Iterate on skills-creator based on usage feedback
4. Consider adding more skills to the astrocode plugin as workflows stabilize
