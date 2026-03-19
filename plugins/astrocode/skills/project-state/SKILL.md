---
name: project-state
description: >
  Manages persistent, vendor-neutral project state in .agents/ directory for
  AI agent session continuity. Use when the user says "bootstrap this project",
  "initialize project state", "set up agent state", "update project state",
  "sync agent context", or "refresh .agents". Detects agent configuration files
  (CLAUDE.md, AGENTS.md, GEMINI.md) and injects state pointers. Creates and
  maintains a CONTEXT.md index with topic-based progressive disclosure files.
  DO NOT trigger for general project questions, file operations, or git operations.
compatibility: Requires file system access. Hooks require Claude Code with hooks support.
argument-hint: "[bootstrap | update]"
metadata:
  author: AstroSteveo
  version: 0.1.0
  tags:
    - project-management
    - session-persistence
    - agent-state
---

# Project State

Manages persistent, vendor-neutral project state in `.agents/` for AI agent session continuity.

## Arguments

Parse `$ARGUMENTS` to determine the action:

- **No arguments**: Auto-detect — if `.agents/` exists, run **update**; otherwise run **bootstrap**
- **`bootstrap`**: Initialize `.agents/` from scratch
- **`update`**: Refresh existing state to match current project reality

## Bootstrap

Run when `.agents/` does not exist in the project root.

### Step 1: Scan the Project

Explore the project to understand:
- Directory structure (top 2-3 levels)
- Tech stack (languages, frameworks, build tools)
- Key configuration files (package.json, pyproject.toml, Cargo.toml, etc.)
- Test infrastructure and CI/CD setup
- Architecture patterns and conventions

### Step 2: Detect Agent Configuration Files

Search the project root for agent markdown files:

| File | Agent |
|------|-------|
| `CLAUDE.md` | Claude Code |
| `AGENTS.md` | Generic / multi-agent |
| `.cursorrules` | Cursor |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `GEMINI.md` | Gemini |
| `.windsurfrules` | Windsurf |

Consult `references/agent-detection.md` for the complete list and injection templates.

Record which files exist — you will inject pointers into all of them in Step 6.

### Step 3: Create .agents/ Directory

Create `.agents/` in the project root.

IMPORTANT: `.agents/` is committed to git. It represents shared project knowledge, not personal agent preferences.

### Step 4: Generate CONTEXT.md

Create `.agents/CONTEXT.md` as the thin context index. Keep it focused and scannable.

```
# Project Context

> Last updated: {YYYY-MM-DD}

## Overview

{1-3 sentence description of what this project is and does}

## Stack

- **Language(s):** {primary languages}
- **Framework(s):** {key frameworks}
- **Build:** {build tool/system}
- **Test:** {test framework}
- **CI/CD:** {pipeline tool}

## Structure

{project root}/
├── {dir}/          # {purpose}
├── {dir}/          # {purpose}
└── {file}          # {purpose}

## Active Work

{Current priorities, in-progress features, known issues}

## Topics

| Topic | File | Description |
|-------|------|-------------|
| Architecture | [architecture.md](architecture.md) | Structure, patterns, conventions |
| Status | [status.md](status.md) | Current work streams, recent changes |
```

### Step 5: Create Initial Topic Files

Create topic files based on what you discovered. Start with these defaults:

- **`.agents/architecture.md`** — Project structure, key patterns, conventions, design decisions
- **`.agents/status.md`** — Current work streams, recent changes, known issues, next steps

Additional topic files to create only if relevant:
- `dependencies.md` — Key dependencies and their roles
- `testing.md` — Test strategy, coverage, how to run tests
- `deployment.md` — Deployment process, environments, configuration
- `api.md` — API surface, endpoints, data models

Keep each topic file focused. If one grows beyond ~200 lines, split it.

Consult `references/context-structure.md` for topic file templates and guidelines.

### Step 6: Inject State Pointer

For each agent file detected in Step 2, inject a pointer section. If no agent file exists, create `CLAUDE.md`.

Pointer template:
```
## Project State

This project maintains persistent agent state in `.agents/`.
Read `.agents/CONTEXT.md` at the start of each session to orient yourself.
Update the relevant files in `.agents/` after completing meaningful units of work.
```

Consult `references/agent-detection.md` for agent-specific injection formats.

### Step 7: Verify

After bootstrap, confirm:
- `.agents/CONTEXT.md` exists and is well-formed
- At least `architecture.md` and `status.md` exist as topic files
- Pointer injected into at least one agent configuration file
- All topic files linked from CONTEXT.md actually exist

Present a summary to the user of what was created.

## Update

Run when `.agents/` already exists and needs refreshing.

### Step 1: Read Current State

Read `.agents/CONTEXT.md` and all topic files it references.

### Step 2: Assess What Changed

Compare documented state against reality:
- Check `git log` since the last update timestamp in CONTEXT.md
- Compare documented directory structure against actual
- Identify new, removed, or changed files and patterns
- Check if documented dependencies still match config files

### Step 3: Update Topic Files

For each topic file:
- Update stale information with current reality
- Add sections for newly discovered areas
- Remove references to things that no longer exist
- Create new topic files if new areas have emerged

### Step 4: Refresh CONTEXT.md

- Update the `Last updated` timestamp
- Refresh Overview if the project's purpose has evolved
- Update Stack if dependencies changed
- Regenerate Structure from current directory layout
- Update Active Work with current priorities
- Ensure all topic file links are accurate

## Examples

### Example 1: First-time Bootstrap

User says: "bootstrap this project"

1. Scan — discover TypeScript monorepo with React frontend, Node API, PostgreSQL
2. Detect `CLAUDE.md` in project root
3. Create `.agents/` with CONTEXT.md, architecture.md, status.md
4. Inject pointer section into `CLAUDE.md`
5. Present summary

### Example 2: Mid-session Update

User says: "update project state"

1. Read current `.agents/CONTEXT.md` — last updated 3 days ago
2. Git log shows 8 commits: new API endpoint, dependency bump, test additions
3. Update `architecture.md` with new endpoint pattern
4. Update `status.md` with recent work
5. Refresh CONTEXT.md timestamp and Active Work section

## Troubleshooting

**No agent configuration file found**
Cause: Project has no CLAUDE.md, AGENTS.md, or similar.
Solution: Create `CLAUDE.md` in the project root with the state pointer.

**`.agents/` already exists during bootstrap**
Cause: State was previously initialized.
Solution: Switch to update mode. Ask user if they want to re-bootstrap (destructive) or update.

**Topic files out of sync with CONTEXT.md**
Cause: Files created or deleted without updating the index.
Solution: During update, regenerate the Topics table from actual files in `.agents/`.
