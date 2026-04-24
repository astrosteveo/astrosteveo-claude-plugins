# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin repository with four plugins — **commit** (Conventional Commits), **code-quality** (codebase quality review), **reconcile-memory** (memory audit and cleanup), and **scoped-delivery** (four-phase delivery workflow). The codebase is pure Markdown (skills) and Bash (scripts). There is no build step; plugins are loaded directly by Claude Code.

## Architecture

### Plugin Layout

Each plugin lives under `plugins/{name}/` with its own `.claude-plugin/plugin.json` manifest. The top-level `.claude-plugin/marketplace.json` is the registry index.

Four plugins:
- **`commit`** (`plugins/commit/`) — Conventional Commits skill; analyzes diffs, groups changes into logical units, creates one commit per unit
- **`code-quality`** (`plugins/code-quality/`) — two skills: **code-quality** for comprehensive codebase audits (clean code, DRY, security, performance, best practices; context-first analysis with non-breaking recommendations) and **code-sniffer** for detecting code smells and AI-generated slop (cargo-culted patterns, ceremonial error handling, vibe-coded signals, ceremony-to-substance ratio)
- **`reconcile-memory`** (`plugins/reconcile-memory/`) — audit and reconcile auto-memory files: deduplication, contradiction detection, staleness assessment, context hygiene
- **`scoped-delivery`** (`plugins/scoped-delivery/`) — four-phase delivery workflow (orient, clarify, implement, review) with fresh subagent contexts for the implementation and review phases; explicit-invocation only

For authoring new skills, use Anthropic's official `skill-creator` plugin from the `anthropics/claude-plugins-official` marketplace.

### Skills

Each skill is a kebab-case folder under `plugins/{plugin}/skills/{skill-name}/` containing:
- `SKILL.md` — frontmatter (description, triggers) + instructions body; folder name is the skill name
- `references/` — progressive-disclosure docs loaded on demand (e.g., `fundamentals.md`)
- `scripts/` — automation scripts

## Conventions

- All skills must be project-agnostic — no language-specific, SaaS-specific, or business-specific assumptions
- SKILL.md files must stay under 500 lines; decompose into `references/` for large docs
- Folder names are kebab-case; the folder name IS the skill name (no `name` field needed in frontmatter)
