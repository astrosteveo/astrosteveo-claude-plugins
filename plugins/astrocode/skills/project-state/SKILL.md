---
name: project-state
description: >
  Use when starting a new session, cold-booting into a project, or when the user asks to
  "check project state", "load progress", "initialize session", "catch up", "where did we leave off",
  or "what's the current status". Also use when the user runs /project-state.
---

# Project State — Cold Boot Recovery

You are starting a new session with no prior context. Your job: get oriented fast and brief the user in under 10 lines.

**Prerequisite:** This skill requires a git repository. If the working directory is not a git repo, tell the user and offer to initialize one. Do not proceed without git.

## Instructions

### Step 1: Find the state file

Look for `.claude/memory/PROGRESS.md` relative to the current working directory.

### Step 2a: State file exists — Staleness check and brief

1. Read `.claude/memory/PROGRESS.md`.
2. **Staleness check.** Read the `Last synced at:` hash from the file header.
   - If the hash is present: `git diff --stat HASH..HEAD -- . ':!.claude/'`
   - If no hash (legacy file or first run): treat as stale.
   - **No source changes since hash**: state is current. Proceed to briefing.
   - **Source files changed**: state is stale. Show the user what changed (`git log --oneline HASH..HEAD -- . ':!.claude/'`) and update PROGRESS.md before briefing.
3. Present a **brief** status (aim for 5-10 lines max):
   - What's actively in progress
   - Any blockers
   - Top 2-3 next steps
4. Ask: "Are these priorities still right, or has something changed?"

Do NOT read back the entire file. Summarize.

### Step 2b: State file missing — Bootstrap from project signals

Scan the project first, then create a pre-populated state file:

1. `git log --oneline -15` for recent work.
2. Read `package.json`, `Cargo.toml`, `pyproject.toml`, or equivalent for stack info.
3. Read `CLAUDE.md` if present for project conventions.
4. Scan top-level directory structure for architecture clues.
5. Grep for `TODO`, `FIXME`, `HACK` in source files (top 10 hits).

Create `.claude/memory/PROGRESS.md` pre-populated with what you found. Tell the user what you inferred and ask them to correct anything wrong.

### Step 3: Keep it current

Update PROGRESS.md at these moments during a session:

- **After completing a feature or fix** — add to Recent Changes
- **After making an architectural decision** — add to Architecture & Key Decisions
- **When discovering a bug or blocker** — add to Known Issues

A SessionEnd hook updates the timestamp automatically. You do not need to handle session close.

**Every time you update PROGRESS.md:**
- Set `Last synced at:` to the current HEAD short hash (`git rev-parse --short HEAD`)
- Keep Recent Changes to the last ~10 entries (drop oldest)
- Keep the whole file under 60 lines
- Write as if briefing a stranger — specific, concise, no ambiguity
- Stage and commit: `git commit -m "chore: update project state" -- .claude/memory/PROGRESS.md`

## Template

When creating a new PROGRESS.md, use this structure (pre-fill from Step 2b):

```markdown
# Project Progress

> Last updated: YYYY-MM-DD | Last synced at: SHORTHASH

## Active Work Streams

- (inferred from recent git commits or user input)

## Recent Changes

| Date | Change | Files/Areas |
|------|--------|-------------|

## Architecture & Key Decisions

- (inferred from project structure and config)

## Known Issues & Blockers

- None detected

## Next Steps

1. (inferred or ask user)

## Project Context

- **Project:** (from package.json name/description or repo name)
- **Stack:** (from dependencies and config files)
- **Build/Run:** (from scripts in package.json or Makefile)
- **Test:** (from test scripts or test directory presence)
```
