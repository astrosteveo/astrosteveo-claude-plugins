# astrosteveo-claude-plugins

Claude Code plugins for session continuity, git discipline, and skill creation.

## Plugins

### project-state

Session continuity and git discipline hooks for Claude Code. No skills — just hooks that keep your work safe across sessions.

**Hooks:**

| Hook | What it does |
|------|-------------|
| **SessionStart** | Surfaces resume notes from previous sessions so you can pick up where you left off |
| **PreToolUse** | Blocks dangerous git commands — broad staging (`git add -A`), force push, hard reset, `git clean`, `checkout -- .` |
| **PostCompact** | Re-injects dirty state and recent commits after context compaction |
| **Stop** | Blocks the agent from stopping if there are uncommitted changes; categorizes all dirty state for single-turn resolution |
| **SessionEnd** | Records uncommitted state in a CLAUDE.md resume note for the next session |

Hooks never auto-commit or auto-push. They surface state and let you decide what to do.

### skills-creator

Interactive guide for creating new Claude Code skills. Walks you through a 6-phase workflow: discovery, frontmatter, trigger design, instruction writing, file structure, and validation.

Invoke with `/skills-creator` or say "create a skill".

## Installation

Add this repository as a Claude Code plugin source:

```
https://github.com/astrosteveo/astrosteveo-claude-plugins
```

## Testing

### Hook tests

```bash
# All hooks
python plugins/project-state/scripts/test-hooks.py

# Single hook
python plugins/project-state/scripts/test-hooks.py --hook stop-gate

# Single scenario
python plugins/project-state/scripts/test-hooks.py --scenario unstaged-modifications
```

### Skill tests

```bash
# Structural validation
python plugins/skills-creator/skills/skills-creator/scripts/validate-structure.py /path/to/skill

# Trigger tests
python plugins/skills-creator/skills/skills-creator/scripts/run-tests.py /path/to/skill --layer 2

# Full suite
python plugins/skills-creator/skills/skills-creator/scripts/run-tests.py /path/to/skill
```
