# astrosteveo-claude-plugins

Curated Claude Code plugins for engineers.

## Plugins

### commit

Conventional Commits skill for Claude Code. Analyzes diffs, groups changes into logical units, and creates one well-formatted commit per unit.

Invoke with `/commit` or say "commit my changes".

### skill-creator

Interactive guide for creating new Claude Code skills. Walks you through a 6-phase workflow: discovery, frontmatter, trigger design, instruction writing, file structure, and validation.

Invoke with `/skill-creator` or say "create a skill".

### godot-dev

Godot 4.x development skill with engine conventions, architecture patterns, and MCP workflow guidance.

Triggers automatically in projects containing `project.godot`, or invoke with `/godot-dev`.

### code-quality

Codebase quality review — clean code, DRY, security, performance, and best practices. Builds full codebase understanding before making recommendations.

Invoke with `/code-quality` or say "review code quality".

## Installation

Add this repository as a Claude Code plugin source:

```
https://github.com/astrosteveo/astrosteveo-claude-plugins
```

## Testing

```bash
# Structural validation (free, instant)
python plugins/skill-creator/skills/skill-creator/scripts/validate-structure.py /path/to/skill

# Trigger tests
python plugins/skill-creator/skills/skill-creator/scripts/run-tests.py /path/to/skill --layer 2

# Full suite
python plugins/skill-creator/skills/skill-creator/scripts/run-tests.py /path/to/skill
```
