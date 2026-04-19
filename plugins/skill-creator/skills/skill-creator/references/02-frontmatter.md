# YAML Frontmatter Reference

The YAML frontmatter is how Claude decides whether to load your skill. It appears in Claude's system prompt at all times (Level 1 of progressive disclosure). Getting this right is the single most important part of skill creation.

## Standard Format

```yaml
---
description: What it does and when to use it. Include trigger phrases like "do something" or "run the thing".
---
```

The skill name comes from the folder name — no `name` field needed. Only add `name` if you need to override the directory name (rare).

Values are unquoted. Do not wrap descriptions or other values in single or double quotes — Claude Code's frontmatter parser handles special characters (colons, double quotes, brackets) without quoting.

Write descriptions as a single-line string. Do NOT use YAML block scalars (`>` or `|`) — they break the description across multiple lines in the file, making it harder to read and edit. Keep the entire description on one line after `description: `.

The `---` delimiters are mandatory. Missing them is a common upload error.

## Field Specifications

### name (optional)

Usually omitted — defaults to the directory name, just like slash commands. Only set this if you need to override the folder name.

- kebab-case only (lowercase letters, hyphens)
- No spaces, capitals, or underscores
- Cannot contain "claude" or "anthropic" (reserved)
- Maximum 64 characters

```yaml
# Best — omit name, let folder name be the skill name
# folder: sprint-planner/
---
description: Manages Linear project workflows...
---

# Override — only if the folder name differs (rare)
name: sprint-planner
```

### description (recommended)

Must include BOTH:
- **What** the skill does
- **When** to use it (trigger conditions / phrases)

Constraints:
- No XML angle brackets in the description text content
- Include specific tasks users might say
- Mention file types if relevant
- If omitted, defaults to the first paragraph of the SKILL.md body

**Character budget:** The combined `description` + `when_to_use` is truncated at **1,536 characters** in the skill listing (the listing is what Claude reads to decide when to load the skill). Front-load the most important info — what the skill does and key trigger phrases — so it survives truncation.

See `03-descriptions-and-triggers.md` for detailed guidance and examples.

### when_to_use (optional)

Additional context for when Claude should invoke the skill — extra trigger phrases, example user requests, or edge-case clarifications. This field is appended to `description` in the skill listing and counts toward the combined 1,536-character cap.

Use when the `description` is already rich on "what" but you want to add more "when" guidance without cluttering the primary description.

```yaml
---
description: Analyzes Figma design files and generates developer handoff documentation.
when_to_use: Trigger when the user uploads .fig files, asks for "design specs", mentions "component documentation", or requests a "design-to-code handoff".
---
```

### version (optional)

Semantic version of the skill. Can be specified at the top level or under `metadata`. Top-level `version` is preferred.

```yaml
version: 1.0.0
```

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
# Space-separated string:
allowed-tools: Read Write Edit

# Bash with command filters:
allowed-tools: Read Bash(git:*) Bash(npm:*)

# Array format:
allowed-tools:
  - Read
  - Write
  - Bash(git:*)
  - Bash(python:*)
  - Bash(docker:*)
```

**Bash patterns:** `Bash(prefix:*)` restricts Bash to commands starting with that prefix. Use this for fine-grained control over shell access.

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
argument-hint: [issue-number]
# or
argument-hint: [filename] [format]
```

### model (optional)

Specifies which Claude model to use when the skill is active. Accepts model aliases or full model IDs.

```yaml
model: sonnet
```

### effort (optional)

Sets the reasoning effort level when the skill is active. Overrides the session effort level.

```yaml
effort: high
```

Valid values: `low`, `medium`, `high`, `xhigh`, `max`. Available levels depend on the model.

### paths (optional)

Glob patterns that limit when Claude auto-activates the skill. When set, the skill only loads automatically when working with files matching the patterns.

```yaml
# Comma-separated string
paths: **/*.ts, **/*.tsx

# Array format
paths:
  - **/*.ts
  - **/*.tsx
  - **/*.js
```

### shell (optional)

Shell used for inline commands (`` !`command` `` and ` ```! ` blocks) within the skill content. Default is `bash`.

```yaml
shell: bash
# or
shell: powershell
```

Note: `powershell` requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` environment variable.

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

Scoped hooks for skill lifecycle events. Uses the same structure as settings.json hooks but in YAML. Hooks only run while the skill is active.

Event names use PascalCase (e.g., `PreToolUse`, `PostToolUse`, `SessionStart`). Each event takes a list of matcher groups, each containing a `matcher` regex and a `hooks` array of handler objects.

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
          timeout: 30
          statusMessage: "Validating command..."
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/lint-check.sh"
```

Handler types: `command`, `http`, `prompt`, `agent`. Common optional fields: `timeout`, `statusMessage`, `once` (run once per session then remove), `if` (permission rule filter for tool events), `async` (command only).

## Complete Example

Assuming the skill lives in a folder named `sprint-planner/`:

```yaml
---
description: Manages Linear project workflows including sprint planning, task creation, and status tracking. Use when user mentions "sprint", "Linear tasks", "project planning", or asks to "create tickets".
license: MIT
compatibility: Requires Linear MCP server connection.
metadata:
  author: DevTeam
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
- Long single-line strings for descriptions

## Common Mistakes

```yaml
# Wrong — missing delimiters
name: my-skill
description: Does things

# Wrong — tabs instead of spaces for indentation
name: my-skill
description:	Does things

# Wrong — using block scalars
name: my-skill
description: >
  Does things across
  multiple lines

# Correct
---
name: my-skill
description: Does things. Use when user says "do the thing" or asks for help.
---
```
