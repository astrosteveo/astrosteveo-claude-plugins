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

Keep SKILL.md focused on core instructions. Move detailed documentation to `references/` and link to it. Target: SKILL.md under 5,000 words.

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
