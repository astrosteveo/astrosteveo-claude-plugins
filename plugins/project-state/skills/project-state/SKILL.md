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

Search the project root for agent configuration files per `references/agent-detection.md`. Record which files exist — you will inject pointers into all of them in Step 6.

### Step 3: Create .agents/ Directory

Create `.agents/` in the project root.

IMPORTANT: `.agents/` is committed to git. It represents shared project knowledge, not personal agent preferences.

### Step 4: Generate CONTEXT.md

Create `.agents/CONTEXT.md` as the thin context index. Include only curated, slow-changing content — directory structure and recent activity are generated dynamically by the session-start hook.

```
# Project Context

## Overview

{1-3 sentence description of what this project is and does}

## Stack

- **Language(s):** {primary languages}
- **Framework(s):** {key frameworks}
- **Build:** {build tool/system}
- **Test:** {test framework}
- **CI/CD:** {pipeline tool}

## Topics

| Topic | File | Description |
|-------|------|-------------|
| Architecture | [architecture.md](architecture.md) | Structure, patterns, conventions |
| Status | [status.md](status.md) | Current work streams, recent changes |
```

NOTE: Do not add Structure or Active Work sections to CONTEXT.md. These are injected dynamically by the session-start hook from the filesystem and git log, so they are always fresh.

### Step 5: Create Initial Topic Files

Create topic files based on what you discovered. Start with these defaults:

- **`.agents/architecture.md`** — Project structure, key patterns, conventions, design decisions
- **`.agents/status.md`** — Current work streams, recent changes, known issues, next steps

Create additional topic files if the project warrants them. Consult `references/context-structure.md` for optional topic files, templates, and guidelines.

### Step 6: Inject State Pointer

For each agent file detected in Step 2, inject a pointer section. If no agent file exists, create `CLAUDE.md`.

Consult `references/agent-detection.md` for pointer templates, injection rules, and fallback behavior.

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
- Check recent `git log` for changes since the last state update
- Identify new, removed, or changed patterns
- Check if documented dependencies still match config files

### Step 3: Update Topic Files

For each topic file:
- Update stale information with current reality
- Add sections for newly discovered areas
- Remove references to things that no longer exist
- Create new topic files if new areas have emerged

### Step 4: Refresh CONTEXT.md

- Refresh Overview if the project's purpose has evolved
- Update Stack if dependencies changed
- Ensure all topic file links are accurate

NOTE: Do not add Structure or Active Work sections — these are generated dynamically by the session-start hook.
