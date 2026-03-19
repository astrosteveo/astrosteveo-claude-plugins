# Status

> Part of [Project Context](CONTEXT.md)

## Current Work Streams

- **Project-state skill** — Manages vendor-neutral persistent state in `.agents/` with bootstrap and update flows. Supports multi-agent detection (Claude, Cursor, Copilot, Gemini, Windsurf). SKILL.md trimmed to delegate detail to reference files via progressive disclosure.
- **Skills-creator skill** — Stable. Interactive guide for building new Claude skills with progressive reference docs and a Python-based testing framework.

## Recent Changes

| Date | Change | Commit |
|------|--------|--------|
| 2026-03-19 | Project-state SKILL.md trimmed — delegated detail to reference files | `e35c3cd` |
| 2026-03-19 | Stop-gate: added commit enforcement (two-phase gate) | `847f02c` |
| 2026-03-19 | Hook testing framework added; stop-gate blocking fix | `0c53d60` |
| 2026-03-19 | Session resume handoff between session-end and session-start | `aba8359` |
| 2026-03-19 | Removed timestamp logic — state is commit-based | `94adba3` |
| 2026-03-19 | Session-end hook: commit and push all changes | `89fb892` |
| 2026-03-19 | Stop-gate rewritten to git-diff detection | `010b772` |
| 2026-03-18 | Added project-state skill with agent detection and context structure references | `e3aa0db` |
| 2026-03-18 | Added skill testing framework with real `claude -p` integration | `14578d6` |
| 2026-03-18 | Removed deprecated skills | `b249036` |

## Known Issues

- None detected

## Next Steps

1. Test `project-state` skill bootstrap and update flows in real projects
2. Iterate on skills-creator based on usage feedback
3. Consider adding more skills to the astrocode plugin as workflows stabilize
