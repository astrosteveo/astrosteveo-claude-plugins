# YAML Frontmatter Reference

The YAML frontmatter is how Claude decides whether to load your skill. It appears in Claude's system prompt at all times (Level 1 of progressive disclosure). Getting this right is the single most important part of skill creation.

## Required Format

```yaml
---
name: your-skill-name
description: >
  What it does and when to use it. Include trigger phrases.
---
```

Always use the YAML folded block scalar (`>`) for descriptions. This folds multi-line text into a single continuous string, which renders cleanly in Claude Code's system prompt. Using `|` (literal block) preserves line breaks and makes descriptions appear fragmented.

The `---` delimiters are mandatory. Missing them is a common upload error.

## Field Specifications

### name (required)

- kebab-case only (lowercase letters, hyphens)
- No spaces, capitals, or underscores
- Must match the folder name
- Cannot contain "claude" or "anthropic" (reserved)
- Maximum 64 characters

```yaml
# Correct
name: sprint-planner

# Wrong
name: Sprint Planner      # spaces and capitals
name: sprint_planner      # underscores
name: claude-helper        # reserved prefix
```

### description (required)

Must include BOTH:
- **What** the skill does
- **When** to use it (trigger conditions / phrases)

Constraints:
- Under 1024 characters
- No XML angle brackets in the description text content (the YAML `>` folding indicator is fine)
- Include specific tasks users might say
- Mention file types if relevant

See `03-descriptions-and-triggers.md` for detailed guidance and examples.

### license (optional)

Use if making the skill open source.

```yaml
license: MIT
# or
license: Apache-2.0
```

### compatibility (optional)

1–500 characters. Indicates environment requirements: intended product, required system packages, network access needs, etc.

```yaml
compatibility: Requires Claude Code with Bash access. Needs Node.js 18+.
```

### metadata (optional)

Any custom key-value pairs. Suggested fields: author, version, mcp-server, category, tags.

```yaml
metadata:
  author: Your Name
  version: 1.0.0
  mcp-server: linear
  category: productivity
  tags: [project-management, automation]
```

### allowed-tools (optional)

Restricts which tools Claude can use without permission prompts when the skill is active.

```yaml
allowed-tools: "Bash(python:*) Bash(npm:*) WebFetch"
# or as a list:
allowed-tools: Read, Grep, Glob
```

### disable-model-invocation (optional)

Prevents Claude from automatically loading the skill. The skill can only be triggered manually via `/skill-name`.

```yaml
disable-model-invocation: true
```

Use when:
- The skill performs destructive or irreversible actions
- You want explicit user intent before activation
- The skill overlaps with other skills and causes over-triggering

### user-invocable (optional)

Controls whether the skill appears in the `/` menu. Default is `true`. Set to `false` to hide from users — the skill can still be loaded by Claude automatically based on the description.

```yaml
user-invocable: false
```

### argument-hint (optional)

Shows a hint during autocomplete when the user types `/skill-name`.

```yaml
argument-hint: "[issue-number]"
# or
argument-hint: "[filename] [format]"
```

### model (optional)

Specifies which Claude model to use when the skill is active.

```yaml
model: claude-sonnet-4-5-20250514
```

### context and agent (optional)

Runs the skill in an isolated subagent context. The subagent receives SKILL.md content as its task prompt but does not have access to the current conversation history.

```yaml
context: fork
agent: Explore    # Options: Explore, Plan, general-purpose
```

Use when:
- Complex multi-step processes that benefit from fresh context
- Research or exploration workflows
- Long-running operations

**Important:** `context: fork` only makes sense for skills with explicit task instructions. Guidelines-only skills won't produce useful results in a subagent.

### hooks (optional)

Scoped hooks for skill lifecycle events.

```yaml
hooks:
  pre-tool-use:
    - command: echo "Tool being used"
  post-tool-use:
    - command: echo "Tool completed"
```

## Complete Example

```yaml
---
name: sprint-planner
description: >
  Manages Linear project workflows including sprint planning, task creation,
  and status tracking. Use when user mentions "sprint", "Linear tasks",
  "project planning", or asks to "create tickets".
license: MIT
compatibility: Requires Linear MCP server connection.
metadata:
  author: DevTeam
  version: 1.0.0
  mcp-server: linear
  category: project-management
---
```

## Security Rules

**Forbidden in frontmatter:**
- XML angle brackets (< >) — frontmatter appears in Claude's system prompt; malicious content could inject instructions
- Skills named with "claude" or "anthropic" (reserved)

**Safe to use:**
- Any standard YAML types (strings, numbers, booleans, lists, objects)
- Custom metadata fields
- Long descriptions (up to 1024 characters)
- Multi-line strings using `>` or `|` YAML syntax

## Common Mistakes

```yaml
# Wrong — missing delimiters
name: my-skill
description: Does things

# Wrong — unclosed quotes
name: my-skill
description: "Does things

# Wrong — tabs instead of spaces for indentation
name: my-skill
description:	Does things

# Correct
---
name: my-skill
description: Does things
---
```
