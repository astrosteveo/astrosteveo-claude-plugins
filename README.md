# astrosteveo-claude-plugins

Claude Code plugins for skill creation and development workflows.

## Plugins

### skills-creator

Interactive guide for creating new Claude Code skills. Walks you through a 6-phase workflow: discovery, frontmatter, trigger design, instruction writing, file structure, and validation.

Invoke with `/skills-creator` or say "create a skill".

## Installation

Add this repository as a Claude Code plugin source:

```
https://github.com/astrosteveo/astrosteveo-claude-plugins
```

## Testing

### Skill tests

```bash
# Structural validation
python plugins/skills-creator/skills/skills-creator/scripts/validate-structure.py /path/to/skill

# Trigger tests
python plugins/skills-creator/skills/skills-creator/scripts/run-tests.py /path/to/skill --layer 2

# Full suite
python plugins/skills-creator/skills/skills-creator/scripts/run-tests.py /path/to/skill
```
