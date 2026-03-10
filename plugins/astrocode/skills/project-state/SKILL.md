---
name: project-state
description: >
  Use when starting a new session, or when the user asks to
  "check project state", "load progress", "initialize session", "catch up", "where did we leave off",
  or "what's the current status". Also use when the user runs /project-state.
---

# Project State

`.claude/PROGRESS.md` is the **authoritative handoff document** between Claude sessions. When you read it, you should know everything you need to start working — what was done, what's in progress, what's next, what decisions were made, and what the architecture looks like. No codebase exploration needed. No reading git logs to reconstruct context. Just read the file and go.

Every session reads it on start and updates it with every commit. If it's wrong or stale, the next session wastes time re-exploring the codebase from scratch — which is exactly what this file exists to prevent.

**Keeping PROGRESS.md accurate is a core responsibility equal to writing correct code.** If you write code but don't update PROGRESS.md, the work is incomplete.

**Prerequisite:** This skill requires a git repository. If the working directory is not a git repo, tell the user and offer to initialize one. Do not proceed without git.

## On Session Start

### Step 1: Read the state file

Read `.claude/PROGRESS.md` relative to the current working directory.

> **Path note:** PROGRESS.md lives at `.claude/PROGRESS.md`, NOT `.claude/memory/`. The `memory/` directory is managed by Claude Code's auto-memory system and will mangle files placed there.

### Step 2a: State file exists

1. Read `.claude/PROGRESS.md`.
2. **Staleness check.** Read the `Last synced at:` hash from the file header.
   - If the hash is present: `git diff --stat HASH..HEAD -- . ':!.claude/'`
   - If no hash: treat as stale.
   - **No source changes since hash**: state is current. Proceed to briefing.
   - **Source files changed**: state is stale. Show the user what changed (`git log --oneline HASH..HEAD -- . ':!.claude/'`) and update PROGRESS.md before briefing.
3. Present a **brief** status (5-10 lines max):
   - What's actively in progress
   - Any blockers
   - Top 2-3 next steps
4. Ask: "Are these priorities still right, or has something changed?"

Do NOT read back the entire file. Summarize.

### Step 2b: State file missing — First-time setup

This only happens once per project. Scan the project and create the initial state file:

1. `git log --oneline -15` for recent work.
2. Read `package.json`, `Cargo.toml`, `pyproject.toml`, or equivalent for stack info.
3. Read `CLAUDE.md` if present for project conventions.
4. Scan top-level directory structure for architecture clues.
5. Grep for `TODO`, `FIXME`, `HACK` in source files (top 10 hits).

Create `.claude/PROGRESS.md` using the template below. Tell the user what you inferred and ask them to correct anything wrong. Commit it immediately.

## During the Session — Mandatory

PROGRESS.md is the authoritative project state that hands off from session to session. It MUST be updated whenever project state changes — not only after source commits.

### After every source commit:

1. Update `.claude/PROGRESS.md`:
   - Add/update a row in **Recent Changes** for what you just committed.
   - Update **Active Work Streams** and **Next Steps** to reflect current reality.
   - Update the header: `> Last updated: YYYY-MM-DD | Last synced at: NEW_HEAD_HASH`
2. Commit it: `git commit -m "chore: update project state" -- .claude/PROGRESS.md`

### When the user reports completing an external action:

Users may complete tasks outside Claude (e.g., configuring a webhook in a dashboard, merging a PR, updating DNS). When the user tells you something from Next Steps or Known Issues is done:

1. Update PROGRESS.md **immediately** — remove or mark the item as done, update Next Steps, clear resolved blockers from Known Issues.
2. Commit it: `git commit -m "chore: update project state" -- .claude/PROGRESS.md`

Do NOT leave completed items in Next Steps or resolved blockers in Known Issues. Stale content is worse than missing content.

Keep the file under 60 lines. Trim old Recent Changes rows when needed. The Stop hook exists as a last-resort safety net — do not rely on it.

## Template

Use this structure when creating a new PROGRESS.md (pre-fill from Step 2b):

```markdown
# Project Progress

> Last updated: YYYY-MM-DD | Last synced at: SHORTHASH

## Active Work Streams

- (what's currently in progress or recently completed)

## Recent Changes

| Date | Change | Files/Areas |
|------|--------|-------------|

## Architecture & Key Decisions

- (key technical decisions, stack info, patterns)

## Known Issues & Blockers

- None detected

## Next Steps

1. (prioritized next actions)

## Project Context

- **Project:** (name and one-line description)
- **Stack:** (from dependencies and config)
- **Build/Run:** (key commands)
- **Test:** (test commands or "not configured")
```
