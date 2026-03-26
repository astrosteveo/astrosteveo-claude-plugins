# astrosteveo-claude-plugins

Claude Code plugins for auto-memory awareness and skill creation.

## Plugins

### project-state

Auto-memory awareness hooks for Claude Code. No skills — just hooks that prompt the agent to maintain its memory system.

**Hooks:**

| Hook | What it does |
|------|-------------|
| **SessionStart** | Primes auto-memory awareness for the session |
| **PostCompact** | Shows recent commits for orientation; reminds agent to persist learnings before they are lost |
| **Stop** | Prompts auto-memory evaluation before stopping; does not block |

Hooks never block, auto-commit, or auto-push. They prompt the agent and let it decide what to do.

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
python plugins/project-state/scripts/test-hooks.py --scenario outputs-memory-prompt

# JSON output
python plugins/project-state/scripts/test-hooks.py --json

# Show plan without running
python plugins/project-state/scripts/test-hooks.py --dry-run
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
