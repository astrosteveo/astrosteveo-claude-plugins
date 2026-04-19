# Writing Effective Descriptions and Triggers

The `description` field is the most impactful part of your skill. It's the first level of progressive disclosure — always present in Claude's system prompt — and determines whether your skill loads at the right time.

## Formula

```
[What it does] + [When to use it / trigger phrases] + [Key capabilities]
```

**Important:** The combined `description` + `when_to_use` is truncated at **1,536 characters** in the skill listing (the listing is what Claude reads at Level 1 progressive disclosure). Front-load the most critical information — what the skill does and key trigger phrases — so it survives truncation if you have many skills loaded and the character budget is tight. If you need more trigger detail than fits cleanly in `description`, move it into `when_to_use` (see `02-frontmatter.md`).

## Point of View

Write descriptions in **third person**. The description is injected into Claude's system prompt — first or second person creates confusion about who is speaking.

```yaml
# Correct — third person
description: Analyzes Figma design files and generates developer handoff docs.

# Wrong — first person
description: I can help you analyze Figma design files.

# Wrong — second person
description: You can use this to analyze Figma design files.
```

## Good Descriptions

```yaml
# Specific and actionable
description: Analyzes Figma design files and generates developer handoff documentation. Use when user uploads .fig files, asks for "design specs", "component documentation", or "design-to-code handoff".

# Includes trigger phrases
description: Manages Linear project workflows including sprint planning, task creation, and status tracking. Use when user mentions "sprint", "Linear tasks", "project planning", or asks to "create tickets".

# Clear value proposition
description: End-to-end customer onboarding workflow for PayFlow. Handles account creation, payment setup, and subscription management. Use when user says "onboard new customer", "set up subscription", or "create PayFlow account".
```

## Bad Descriptions

```yaml
# Too vague — Claude can't determine when to load
description: Helps with projects.

# Missing triggers — no "when to use" guidance
description: Creates sophisticated multi-page documentation systems.

# Too technical, no user triggers
description: Implements the Project entity model with hierarchical relationships.
```

## Trigger Phrase Guidelines

Include phrases users would **actually say** — natural language, not technical jargon.

**Effective triggers:**
- Quoted exact phrases: `"create a sprint"`, `"plan this sprint"`
- Action verbs: "set up", "generate", "review", "create", "analyze"
- Domain terms users know: "sprint", "onboarding", "handoff"
- Slash command reference: `Also use when the user runs /skill-name`

**Avoid:**
- Internal jargon only developers would use
- Overly broad terms that match everything ("help", "do", "make")
- Technical implementation details

## Preventing Over-Triggering

If your skill loads for unrelated queries, add specificity:

```yaml
# Add negative triggers
description: Advanced data analysis for CSV files. Use for statistical modeling, regression, clustering. Do NOT use for simple data exploration (use data-viz skill instead).

# Be more specific
description: Processes PDF legal documents for contract review. Do NOT use for general document processing.

# Clarify scope
description: PayFlow payment processing for e-commerce. Use specifically for online payment workflows, not for general financial queries.
```

## Preventing Under-Triggering

If your skill doesn't load when it should:
- Add more trigger phrases covering paraphrased requests
- Include relevant file types or domain keywords
- Add technical terms alongside their plain-language equivalents

## Debugging Triggers

Ask Claude: "When would you use the [skill name] skill?"

Claude will quote the description back. Adjust based on what's missing or overly broad.
