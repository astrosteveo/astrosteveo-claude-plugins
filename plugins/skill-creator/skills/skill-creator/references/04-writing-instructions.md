# Writing Effective Skill Instructions

The SKILL.md body (after frontmatter) is Level 2 of progressive disclosure — loaded when Claude decides the skill is relevant. This is where you tell Claude exactly what to do.

## Recommended Structure

```markdown
---
name: your-skill
description: [...]
---

# Your Skill Name

## Instructions

### Step 1: [First Major Step]
Clear explanation of what happens.

```bash
python scripts/fetch_data.py --project-id PROJECT_ID
Expected output: [describe what success looks like]
```

### Step 2: [Next Step]
[Continue the pattern]

## Examples

### Example 1: [Common scenario]
User says: "Set up a new marketing campaign"
Actions:
1. Fetch existing campaigns via MCP
2. Create new campaign with provided parameters
Result: Campaign created with confirmation link

## Troubleshooting

**Error: [Common error message]**
Cause: [Why it happens]
Solution: [How to fix]
```

## Best Practices

### Be Specific and Actionable

**Good:**
```
Run `python scripts/validate.py --input {filename}` to check data format.
If validation fails, common issues include:
- Missing required fields (add them to the CSV)
- Invalid date formats (use YYYY-MM-DD)
```

**Bad:**
```
Validate the data before proceeding.
```

### Include Error Handling

```markdown
## Common Issues

### MCP Connection Failed
If you see "Connection refused":
1. Verify MCP server is running: Check Settings > Extensions
2. Confirm API key is valid
3. Try reconnecting: Settings > Extensions > [Your Service] > Reconnect
```

### Reference Bundled Resources Clearly

```
Before writing queries, consult `references/api-patterns.md` for:
- Rate limiting guidance
- Pagination patterns
- Error codes and handling
```

### Use Progressive Disclosure

Keep SKILL.md focused on core instructions. Move detailed documentation to `references/` and link to it. Target: SKILL.md under 500 lines.

### Put Critical Instructions First

- Place the most important instructions at the top
- Use `## Important` or `## Critical` headers for must-follow rules
- Repeat key points if the skill is long

### Avoid Ambiguity

```markdown
# Bad
Make sure to validate things properly

# Good
CRITICAL: Before calling create_project, verify:
- Project name is non-empty
- At least one team member assigned
- Start date is not in the past
```

### Use Scripts for Critical Validations

For checks that must be deterministic, bundle a script rather than relying on language instructions. Code is deterministic; language interpretation isn't.

```markdown
Run `scripts/validate-config.sh` before proceeding.
If it exits non-zero, show the user the error output and do not continue.
```

## Anti-Patterns to Avoid

- **Wall of text** — Break instructions into clear, numbered steps
- **Implicit assumptions** — State prerequisites explicitly
- **Missing examples** — Always include at least one concrete example
- **Overloading SKILL.md** — Use `references/` for detailed docs, API specs, long examples
- **Vague error handling** — Be specific about what can go wrong and how to recover

## String Substitutions

Skills support variable substitution for dynamic content:

| Variable | Purpose |
|---|---|
| `$ARGUMENTS` | All arguments passed when invoking the skill |
| `$ARGUMENTS[N]` | Specific argument by 0-based index |
| `$N` | Shorthand for `$ARGUMENTS[N]` (e.g., `$0`, `$1`) |
| `${CLAUDE_SESSION_ID}` | Current session ID (useful for logging) |
| `${CLAUDE_SKILL_DIR}` | Directory containing the skill's SKILL.md |

Example:

```markdown
---
name: review-issue
argument-hint: [issue-number]
description: Reviews a GitHub issue. Use when user says "review issue".
---

# Review Issue $0

Fetch and analyze GitHub issue #$0.
Use scripts in ${CLAUDE_SKILL_DIR}/scripts/ for validation.
```

## File References

Use `@path/to/file` syntax to include file contents inline. The file content is loaded and inserted before the skill content is sent to Claude.

```markdown
---
name: style-guide
description: Enforces project style conventions. Use when user asks about code style or formatting.
---

## Project Style Rules

@.eslintrc.json
@prettier.config.js

Apply these rules when reviewing or writing code.
```

## Dynamic Context Injection

Use `` !`command` `` syntax to run shell commands before skill content is sent to Claude. The command output replaces the placeholder — Claude only sees the final rendered result.

**Inline form** — single commands:

```markdown
---
name: pr-summary
description: Summarize changes in a pull request.
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

**Block form** — multi-line commands using fenced code blocks:

````markdown
## Environment
```!
node --version
npm --version
git status --short
```
````

Each line in the block runs as a separate command. All output replaces the block.

The shell used is controlled by the `shell` frontmatter field (`bash` by default, or `powershell`).

**Security note:** Admins can disable shell execution for user/project/plugin skills by setting `"disableSkillShellExecution": true` in settings.json. Commands are replaced with a disabled message when this policy is active.

Use cases: fetching live API data, reading current file contents, getting Git history, querying databases, checking system status.

## Extended Thinking

Including the word `ultrathink` anywhere in SKILL.md content enables extended thinking mode, giving Claude deeper reasoning capabilities for complex analysis.

```markdown
---
name: complex-analysis
description: Deep analysis of complex systems.
---

Use ultrathink for thorough reasoning on this task.

## Instructions
[Complex analysis steps...]
```

## Reference File Depth

Keep reference files one level deep from SKILL.md:

- **Good:** `SKILL.md → references/api-guide.md`
- **Bad:** `SKILL.md → docs/advanced.md → details.md → actual_info.md`

Claude may partially read deeply nested files, resulting in incomplete information.
