# astrosteveo-claude-plugins

Curated Claude Code plugins for engineers.

## Plugins

### commit

Conventional Commits skill for Claude Code. Analyzes diffs, groups changes into logical units, and creates one well-formatted commit per unit.

Invoke with `/commit` or say "commit my changes".

### code-quality

Codebase quality review — clean code, DRY, security, performance, and best practices. Builds full codebase understanding before making recommendations. Bundles two skills: `code-quality` for comprehensive audits, `code-sniffer` for detecting code smells and AI slop.

Invoke with `/code-quality` or say "review code quality". Use `/code-quality:code-sniffer` for the smell check.

### reconcile-memory

Audit and reconcile Claude Code auto-memory files — deduplication, contradiction detection, staleness assessment, and context hygiene. Identifies entries that silently degrade session quality and proposes a reconciliation plan for explicit approval.

Invoke with `/reconcile-memory:reconcile-memory`.

### scoped-delivery

Structured four-phase delivery workflow (orient, clarify, implement, review) where a fresh subagent reviews the final diff so the implementer isn't the reviewer. The phase separation is load-bearing: each phase produces a named artifact that becomes the input to the next.

Invoke with `/scoped-delivery <task description>`. Explicit invocation only — does not auto-trigger.

## Installation

Add this repository as a Claude Code plugin source:

```
https://github.com/astrosteveo/astrosteveo-claude-plugins
```

