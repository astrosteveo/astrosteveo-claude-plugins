# Status

> Part of [Project Context](CONTEXT.md)

## Current Work Streams

- **Project-state plugin** — Manages vendor-neutral persistent state in `.agents/` with bootstrap and update flows. Includes all session hooks (session-start, stop-gate, session-end). Supports multi-agent detection (Claude, Cursor, Copilot, Gemini, Windsurf).
- **Skills-creator plugin** — Stable. Interactive guide for building new Claude skills with progressive reference docs and a Python-based testing framework.

## Recent Changes

Recent activity is now injected dynamically by the session-start hook via `git log`. See the "Recent Activity (live)" section in session output.

Key architectural changes:
- Split monolithic `astrocode` plugin into two independent plugins: `project-state` and `skills-creator`
- Session-start hook generates Structure and Recent Activity dynamically from filesystem and git log
- CONTEXT.md slimmed to curated-only content (Overview, Stack, Topics)

## Known Issues

- None detected

## Next Steps

1. Test `project-state` skill bootstrap and update flows in real projects
2. Iterate on skills-creator based on usage feedback
3. Consider adding more plugins to the repository as workflows stabilize
