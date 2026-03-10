---
name: skills-creator
description: >
  Interactive guide for creating new Claude skills. Walks the user through
  use-case definition, frontmatter generation, instruction writing, file
  structure setup, and validation. Use when the user says "create a skill",
  "build a skill", "new skill", "make a skill", "skill creator", "help me
  write a skill", or "generate a SKILL.md". Also use when the user runs
  /skills-creator.
---

# Skills Creator

An interactive, step-by-step workflow for building well-structured Claude skills. Each phase produces a concrete artifact; the user reviews before moving on.

## Before You Begin

Read `references/01-fundamentals.md` for core concepts (what a skill is, progressive disclosure, file structure rules). Internalize the constraints — they apply to every step below.

## Phase 1: Discovery

Goal: Understand what the user wants to build and classify the skill.

1. Ask the user to describe the skill in 1–3 sentences. If they are vague, ask:
   - "What specific task should this skill automate or improve?"
   - "Who will use it — you, your team, or the public?"
   - "Does the skill need MCP tools, or is it standalone?"

2. Classify into one of three categories (consult `references/05-patterns.md` if unsure):
   - **Category 1 — Document & Asset Creation:** Output is a file, design, or artifact.
   - **Category 2 — Workflow Automation:** Multi-step process with validation gates.
   - **Category 3 — MCP Enhancement:** Adds workflow guidance on top of MCP tool access.

3. Have the user define 2–3 concrete use cases:
   ```
   Use Case: [Name]
   Trigger: User says "[phrase]"
   Steps: 1. … 2. … 3. …
   Result: [What success looks like]
   ```

4. Present the classification and use cases back to the user for confirmation before continuing.

## Phase 2: Frontmatter

Goal: Produce valid YAML frontmatter for SKILL.md.

Read `references/02-frontmatter.md` for field specs, constraints, and security rules.

1. **name** — Derive from the skill's purpose. Rules:
   - kebab-case only (lowercase, hyphens)
   - Must match the folder name
   - Cannot contain "claude" or "anthropic"

2. **description** — Draft using this formula:
   ```
   [What it does] + [When to use it / trigger phrases] + [Key capabilities]
   ```
   Read `references/03-descriptions-and-triggers.md` for good/bad examples and trigger-phrase guidance. The description MUST include both what the skill does AND when to use it. Keep under 1024 characters. No XML angle brackets.

3. **Optional fields** — Ask if any apply:
   - `license` (MIT, Apache-2.0, etc.)
   - `compatibility` (environment requirements)
   - `metadata` (author, version, mcp-server, tags)

4. Present the complete frontmatter block to the user for review. Iterate until approved.

## Phase 3: Instructions

Goal: Write the SKILL.md body — the core instructions Claude will follow.

Read `references/04-writing-instructions.md` for structure templates and best practices.

1. **Structure the body** using this skeleton:
   ```markdown
   # Skill Name

   ## Instructions

   ### Step 1: [First action]
   [Clear, specific instructions]

   ### Step 2: [Next action]
   [Continue pattern]

   ## Examples

   ### Example 1: [Common scenario]
   User says: "[trigger phrase]"
   Actions: 1. … 2. …
   Result: [Outcome]

   ## Troubleshooting

   **Error: [Common error]**
   Cause: [Why]
   Solution: [Fix]
   ```

2. **Apply best practices:**
   - Be specific and actionable — tell Claude exactly what to do, not just "handle it"
   - Include error handling for likely failure modes
   - Reference bundled resources explicitly: `references/file.md`, `scripts/tool.sh`
   - Use progressive disclosure — keep SKILL.md focused; move detailed docs to `references/`
   - Keep SKILL.md under 5,000 words

3. **Pattern-specific guidance** — consult `references/05-patterns.md` and apply the pattern matching the skill's category:
   - Sequential workflow: explicit step ordering, dependencies, rollback
   - Multi-MCP coordination: phase separation, data passing, cross-service validation
   - Iterative refinement: quality checks, refinement loops, stop criteria
   - Context-aware selection: decision trees, fallbacks, transparency
   - Domain-specific intelligence: compliance checks, audit trails, governance

4. Present the full SKILL.md to the user for review. Iterate until approved.

## Phase 4: File Structure

Goal: Create the skill's directory and all files.

1. Determine the full path. Default location:
   ```
   plugins/astrocode/skills/{skill-name}/
   ```
   Ask the user if they want a different location.

2. Create the directory structure:
   ```
   {skill-name}/
   ├── SKILL.md              # Always created
   ├── scripts/              # If the skill uses executable code
   ├── references/           # If detailed docs are needed
   └── assets/               # If templates/fonts/icons are needed
   ```

3. Write SKILL.md with the approved frontmatter and instructions.

4. Create any supporting files (scripts, references, assets) identified during Phase 3.

5. **Critical rules** — verify before writing:
   - File is named exactly `SKILL.md` (case-sensitive)
   - Folder is kebab-case
   - No `README.md` inside the skill folder
   - No XML angle brackets anywhere in SKILL.md

## Phase 5: Validation

Goal: Verify the skill meets all requirements.

Read `references/06-checklist.md` for the full validation checklist.

Run through each check:

### Structure checks
- [ ] Folder named in kebab-case
- [ ] `SKILL.md` exists with exact casing
- [ ] YAML frontmatter has `---` delimiters
- [ ] `name` field is kebab-case, matches folder name
- [ ] `description` includes WHAT and WHEN
- [ ] No XML angle brackets in any file
- [ ] No `README.md` in skill folder

### Content checks
- [ ] Instructions are clear and actionable
- [ ] Error handling included for likely failure modes
- [ ] Examples provided for common scenarios
- [ ] References clearly linked (if used)
- [ ] SKILL.md is under 5,000 words

### Trigger checks
- [ ] Description includes 3+ trigger phrases users would say
- [ ] Description is specific enough to avoid false triggers
- [ ] Description mentions relevant file types (if applicable)

Present the validation results. If any checks fail, fix them and re-validate.

## Phase 6: Next Steps

After the skill is created and validated:

1. **Test it** — Read `references/07-testing.md` for testing approaches. Suggest 3–5 test queries:
   - 2–3 that SHOULD trigger the skill
   - 1–2 that should NOT trigger it

2. **Iterate** — Tell the user:
   - "Try using the skill in a real conversation. If it doesn't trigger when expected, we can refine the description. If instructions aren't followed well, we can restructure them."
   - "Bring back edge cases or failures and we can improve the skill together."

3. **Distribute** (if relevant) — Mention options:
   - Upload to Claude.ai via Settings > Capabilities > Skills
   - Place in Claude Code skills directory
   - Host on GitHub for sharing
