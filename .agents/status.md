# Status

> Part of [Project Context](CONTEXT.md)

## Current Work Streams

- **Project-state skill** — Manages vendor-neutral persistent state in `.agents/` with bootstrap and update flows. Supports multi-agent detection (Claude, Cursor, Copilot, Gemini, Windsurf). SKILL.md trimmed to delegate detail to reference files via progressive disclosure.
- **Skills-creator skill** — Stable. Interactive guide for building new Claude skills with progressive reference docs and a Python-based testing framework.

## Recent Changes

Recent activity is now injected dynamically by the session-start hook via `git log`. See the "Recent Activity (live)" section in session output.

Key architectural changes:
- Session-start hook generates Structure and Recent Activity dynamically from filesystem and git log
- CONTEXT.md slimmed to curated-only content (Overview, Stack, Topics)
- Freshness check warns about stale topic file references at session start

## Known Issues

- None detected

## Next Steps

1. Test `project-state` skill bootstrap and update flows in real projects
2. Iterate on skills-creator based on usage feedback
3. Consider adding more skills to the astrocode plugin as workflows stabilize
