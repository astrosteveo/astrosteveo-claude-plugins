# YAML Frontmatter Reference

The YAML frontmatter is how Claude decides whether to load your skill. It appears in Claude's system prompt at all times (Level 1 of progressive disclosure). Getting this right is the single most important part of skill creation.

## Required Format

```yaml
---
name: your-skill-name
description: What it does and when to use it. Include trigger phrases.
---
```

The `---` delimiters are mandatory. Missing them is a common upload error.

## Field Specifications

### name (required)

- kebab-case only (lowercase letters, hyphens)
- No spaces, capitals, or underscores
- Must match the folder name
- Cannot contain "claude" or "anthropic" (reserved)

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
- No XML angle brackets (< or >)
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
