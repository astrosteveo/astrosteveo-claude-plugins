# astrosteveo-claude-plugins

The Claude Code plugins I actually use, day in and day out. Nothing fancy under the hood — just Markdown files, written by pairing with Claude, for the workflows I kept reaching for. No brand, no roadmap, no launch — this isn't a curated subset, it's the whole shelf.

If they save you some keystrokes too, glad they're here.

## Plugins

### commit

Conventional Commits skill for Claude Code. Analyzes diffs, groups changes into logical units, and creates one well-formatted commit per unit.

Invoke with `/commit:commit` or say "commit my changes".

### code-quality

Codebase quality review — clean code, DRY, security, performance, and best practices. Builds full codebase understanding before making recommendations. Bundles two skills: `code-quality` for comprehensive audits, `code-sniffer` for detecting code smells and AI slop.

Invoke with `/code-quality:code-quality` or say "review code quality". Use `/code-quality:code-sniffer` for the smell check.

### reconcile-memory

Audit and reconcile Claude Code auto-memory files — deduplication, contradiction detection, staleness assessment, and context hygiene. Identifies entries that silently degrade session quality and proposes a reconciliation plan for explicit approval.

Invoke with `/reconcile-memory:reconcile-memory`.

### scoped-delivery

Structured four-phase delivery workflow (orient, clarify, implement, review) where a fresh subagent reviews the final diff so the implementer isn't the reviewer. The phase separation is load-bearing: each phase produces a named artifact that becomes the input to the next.

Invoke with `/scoped-delivery:scoped-delivery <task description>`. Explicit invocation only — does not auto-trigger.

## Installation

Add the marketplace in Claude Code:

```
/plugin marketplace add astrosteveo/astrosteveo-claude-plugins
```

Install a plugin by name:

```
/plugin install <name>@astrosteveo-claude-plugins
```

(For example: `/plugin install scoped-delivery@astrosteveo-claude-plugins`.)

Or browse everything interactively with `/plugin`.

To pull in new versions later: `/plugin marketplace update astrosteveo-claude-plugins`. To remove a plugin: `/plugin uninstall <name>@astrosteveo-claude-plugins`. After any of these, run `/reload-plugins` to activate changes without restarting.
