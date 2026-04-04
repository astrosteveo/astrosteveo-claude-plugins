# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin repository with five plugins — **commit** (Conventional Commits), **godot-dev** (Godot 4.x guidance), **code-quality** (codebase quality review), **reconcile-memory** (memory audit and cleanup), and **skill-creator** (interactive skill authoring toolkit). The codebase is pure Markdown (skills), Bash (scripts), and Python (test tooling). There is no build step; plugins are loaded directly by Claude Code.

## Architecture

### Plugin Layout

Each plugin lives under `plugins/{name}/` with its own `.claude-plugin/plugin.json` manifest. The top-level `.claude-plugin/marketplace.json` is the registry index.

Five plugins:
- **`commit`** (`plugins/commit/`) — Conventional Commits skill; analyzes diffs, groups changes into logical units, creates one commit per unit
- **`godot-dev`** (`plugins/godot-dev/`) — Godot 4.x development guidance with architecture patterns, conventions, and MCP workflow; extensive reference docs
- **`code-quality`** (`plugins/code-quality/`) — two skills: **code-quality** for comprehensive codebase audits (clean code, DRY, security, performance, best practices; context-first analysis with non-breaking recommendations) and **code-sniffer** for detecting code smells and AI-generated slop (cargo-culted patterns, ceremonial error handling, vibe-coded signals, ceremony-to-substance ratio)
- **`reconcile-memory`** (`plugins/reconcile-memory/`) — audit and reconcile auto-memory files: deduplication, contradiction detection, staleness assessment, context hygiene
- **`skill-creator`** (`plugins/skill-creator/`) — interactive toolkit for creating, editing, reviewing, and testing Claude skills; guided multi-phase workflow with validation and eval framework

### Skills

Each skill is a kebab-case folder under `plugins/{plugin}/skills/{skill-name}/` containing:
- `SKILL.md` — frontmatter (description, triggers) + instructions body; folder name is the skill name
- `references/` — progressive-disclosure docs loaded on demand (e.g., `01-fundamentals.md`)
- `scripts/` — automation scripts

Test specs (`TESTS.yaml`) live in `plugins/{plugin}/evals/`, not inside the skill folder.

## Conventions

- All skills must be project-agnostic — no language-specific, SaaS-specific, or business-specific assumptions
- SKILL.md files must stay under 500 lines; decompose into `references/` for large docs
- Folder names are kebab-case; the folder name IS the skill name (no `name` field needed in frontmatter)
- No XML angle brackets in SKILL.md files
