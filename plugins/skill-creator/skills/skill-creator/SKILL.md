---
description: Interactive toolkit for creating, editing, and testing Claude skills. Use when the user says "create a skill", "new skill", "edit a skill", "test a skill", or "generate a SKILL.md". Three modes - create, edit, and test.
argument-hint: [create | edit path/to/skill | test path/to/skill]
---

# Skill Creator

Interactive toolkit for creating, editing, and testing Claude skills.

## Routing

When invoked, check for arguments. If no arguments are provided, present the user with these options and wait for their choice:

1. **Create** — Build a new skill from scratch (guided multi-phase workflow)
2. **Edit** — Review and improve an existing skill (provide the path to the skill folder)
3. **Test** — Run the eval framework against a skill (provide the path to the skill folder)

If the user provides arguments:
- `/skill-creator create` or `/skill-creator` with a description of what they want to build -- **Create flow**
- `/skill-creator edit path/to/skill` or the user mentions editing/reviewing/fixing a skill -- **Edit flow**
- `/skill-creator test path/to/skill` or the user mentions testing/validating/running evals -- **Test flow**

If the intent is ambiguous, ask.

---

## Create Flow

An interactive, step-by-step workflow for building well-structured Claude skills. Each phase produces a concrete artifact; the user reviews before moving on.

### Before You Begin

Read `references/01-fundamentals.md` for core concepts (what a skill is, progressive disclosure, file structure rules). Internalize the constraints — they apply to every step below.

### Critical: Save Location

**BEFORE writing any files, you MUST ask the user where to save the skill.** Do NOT assume a location. Do NOT create directories without explicit confirmation. Present these options and wait for an answer:

- `~/.claude/skills/{skill-name}/` — Personal, available across all projects
- `.claude/skills/{skill-name}/` — Project-local, scoped to the current repo
- A plugin directory — if the user has a plugin setup (ask them for the path)
- Somewhere else — let them specify

This question should be asked during Phase 1 (Discovery) alongside the other scoping questions. Do NOT defer it to Phase 4. The save location must be confirmed before any files are created.

### Phase 1: Discovery

Goal: Understand what the user wants to build, classify the skill, and confirm where to save it.

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

4. Note: these use cases will feed directly into trigger test cases in Phase 5. Capture the trigger phrases clearly.

5. **Ask where to save the skill** (see "Critical: Save Location" above). This MUST be answered before proceeding to any later phase.

6. Present the classification, use cases, and save location back to the user for confirmation before continuing.

### Phase 2: Frontmatter

Goal: Produce valid YAML frontmatter for SKILL.md.

Read `references/02-frontmatter.md` for field specs, constraints, and security rules.

1. **Folder name** — The folder name IS the skill name. No `name` field needed in frontmatter — it defaults to the directory name. Rules:
   - kebab-case only (lowercase, hyphens)
   - Cannot contain "claude" or "anthropic"

2. **description** — Draft using this formula:
   ```
   [What it does] + [When to use it / trigger phrases] + [Key capabilities]
   ```
   Read `references/03-descriptions-and-triggers.md` for good/bad examples and trigger-phrase guidance. The description MUST include both what the skill does AND when to use it. Combined `description` + `when_to_use` is truncated at 1,536 characters in the skill listing — front-load the most important info. No XML angle brackets.

3. **Optional fields** — Ask if any apply (see `references/02-frontmatter.md` for full details):
   - `name` (override the directory name — rarely needed)
   - `when_to_use` (extra trigger phrases / example requests; appended to `description` in the listing)
   - `argument-hint` (autocomplete hint, e.g. `[issue-number]`)
   - `allowed-tools` (tools auto-approved when skill is active)
   - `disable-model-invocation` (manual-only via `/skill-name`)
   - `user-invocable` (set `false` to hide from `/` menu)
   - `model` (override Claude model)
   - `effort` (reasoning effort: low, medium, high, xhigh, max — available levels depend on the model)
   - `paths` (glob patterns to limit auto-activation, e.g. `**/*.ts`)
   - `context: fork` + `agent:` (run in isolated subagent — Explore, Plan, or general-purpose)
   - `hooks` (lifecycle hooks scoped to this skill)
   - `shell` (shell for inline `` !`command` `` blocks: bash or powershell)

4. **`$ARGUMENTS` placeholder** — If the skill accepts user input via `/skill-name [args]`, use `$ARGUMENTS` in the SKILL.md body where the input should be substituted. See `references/04-writing-instructions.md` for `$0`/`$1` positional variants.

5. Present the complete frontmatter block to the user for review. Iterate until approved.

### Phase 3: Instructions

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
   - Keep SKILL.md under 500 lines

3. **Pattern-specific guidance** — consult `references/05-patterns.md` and apply the pattern matching the skill's category:
   - Sequential workflow: explicit step ordering, dependencies, rollback
   - Multi-MCP coordination: phase separation, data passing, cross-service validation
   - Iterative refinement: quality checks, refinement loops, stop criteria
   - Context-aware selection: decision trees, fallbacks, transparency
   - Domain-specific intelligence: compliance checks, audit trails, governance
   - Plan-validate-execute: structured plans, script validation, user confirmation gates
   - MCP tool naming: use fully qualified `ServerName:tool_name` format
   - Subagent execution: `context: fork` for isolated processing

4. Present the full SKILL.md to the user for review. Iterate until approved.

### Phase 4: File Structure

Goal: Create the skill's directory and all files.

1. Use the save location confirmed by the user in Phase 1. If it was not confirmed, STOP and ask now — do NOT assume a path.

2. Create the directory structure:
   ```
   {skill-name}/
   ├── SKILL.md              # Always created
   ├── scripts/              # If the skill uses executable code
   ├── references/           # If detailed docs are needed
   └── assets/               # If templates/fonts/icons are needed
   ```

   **Do NOT put TESTS.yaml, test results, or eval scratch files in the skill folder.** These are dev-time artifacts that must not ship with the skill. They belong in the ephemeral eval workspace (Phase 5), which is gitignored and outside the skill directory.

3. Write SKILL.md with the approved frontmatter and instructions.

4. Create any supporting files (scripts, references, assets) identified during Phase 3.

5. **Critical rules** — verify before writing:
   - File is named exactly `SKILL.md` (case-sensitive)
   - Folder is kebab-case
   - No `README.md` inside the skill folder
   - No XML angle brackets anywhere in SKILL.md

### Phase 5: Validation & Testing

Goal: Verify the skill meets all requirements, then run the full test suite. You handle this end-to-end — do NOT hand the user commands to run themselves.

Read `references/06-checklist.md` for the full validation checklist.

#### Step 1: Manual checklist

Run through each check yourself by reading the files and verifying:

**Structure checks:**
- [ ] Folder named in kebab-case
- [ ] `SKILL.md` exists with exact casing
- [ ] YAML frontmatter has `---` delimiters
- [ ] Folder name is kebab-case (this is the skill name — no `name` field needed)
- [ ] `description` includes WHAT and WHEN
- [ ] No XML angle brackets in any file
- [ ] No `README.md` in skill folder

**Content checks:**
- [ ] Instructions are clear and actionable
- [ ] Error handling included for likely failure modes
- [ ] Examples provided for common scenarios
- [ ] References clearly linked (if used)
- [ ] SKILL.md is under 500 lines

**Trigger checks:**
- [ ] Description includes 3+ trigger phrases users would say
- [ ] Description is specific enough to avoid false triggers
- [ ] Description is written in third person
- [ ] Description mentions relevant file types (if applicable)

Fix any failures before proceeding.

#### Step 2: Generate TESTS.yaml in an ephemeral eval workspace

**Test specs do not ship with the skill.** The eval workspace is ephemeral, gitignored, and lives outside the skill folder. Never put TESTS.yaml, results, or scratch files inside the skill directory — they must not be committed or distributed with the skill.

1. Resolve the ephemeral workspace path using the Python cross-platform helper (works on Windows, macOS, Linux):
   ```
   python -c "import tempfile, os; p = os.path.join(tempfile.gettempdir(), 'skill-evals', '{skill-name}'); os.makedirs(p, exist_ok=True); print(p)"
   ```
   Use the printed path as `EVAL_DIR` for subsequent commands. Alternatively, if the user wants a project-local workspace (e.g., for debugging), use `{project-root}/.skill-evals/{skill-name}/` — this pattern is already covered by `.gitignore`.

2. Write TESTS.yaml to `EVAL_DIR/TESTS.yaml` with:
   - Default to exactly 3 eval scenarios: 1 `should_trigger`, 1 `should_not_trigger`, 1 `edge_case`
   - Pick the most representative query for each — one clear positive, one clear negative, one ambiguous
   - Only add more scenarios if the user explicitly asks for broader coverage
   - See `references/08-testing-framework.md` for the full TESTS.yaml format

#### Step 3: Run the automated test suite

**You MUST run these tests yourself.** Do not suggest the user run them. Do not print commands for them to copy. Execute them directly using the Bash tool.

The test scripts live in `${CLAUDE_SKILL_DIR}/scripts/`. Run them against the newly created skill, passing the ephemeral TESTS.yaml via `--tests`:

1. **Layer 1 — Structural validation** (free, instant):
   ```
   python ${CLAUDE_SKILL_DIR}/scripts/validate-structure.py /path/to/created/skill
   ```

2. **Layer 2 — Trigger tests** (requires `claude` CLI):
   ```
   python ${CLAUDE_SKILL_DIR}/scripts/run-tests.py /path/to/created/skill --tests $EVAL_DIR/TESTS.yaml --layer 2
   ```

3. **Layer 3 — Behavioral tests** (if TESTS.yaml has behavioral entries):
   ```
   python ${CLAUDE_SKILL_DIR}/scripts/run-tests.py /path/to/created/skill --tests $EVAL_DIR/TESTS.yaml --layer 3
   ```

4. **Full suite** (all layers):
   ```
   python ${CLAUDE_SKILL_DIR}/scripts/run-tests.py /path/to/created/skill --tests $EVAL_DIR/TESTS.yaml
   ```

Run at minimum Layer 1. Ask the user if they want to run Layer 2 and 3 as well (these spawn headless `claude -p` processes and consume tokens — Layer 2 is lightweight, Layer 3 can use more tokens depending on `max_turns`). If they say yes, run them. If they say run everything, run the full suite.

#### Step 4: Handle failures

If any tests fail:
1. Read the failure output carefully
2. Diagnose the root cause
3. Fix the skill files directly
4. Re-run the failing tests to confirm the fix
5. Repeat until all tests pass

Present a summary of results to the user when done.

### Phase 6: Next Steps

After the skill is created, validated, and tests pass:

1. **Iterate** — Tell the user:
   - "Try using the skill in a real conversation. If it doesn't trigger when expected, or instructions aren't followed well, bring it back and we'll refine it."

2. **Distribute** (if relevant) — The skill was already saved to the location confirmed in Phase 1. If the user wants copies in additional locations, offer:
   - Global: `~/.claude/skills/`
   - Project-local: `.claude/skills/`
   - Plugin: user specifies path

### Examples

#### Example: Building a code review skill

User says: "Help me create a skill for code reviews"

1. **Discovery:** Classify as Category 2 (Workflow Automation). Define use cases: "review this PR", "check code quality".
2. **Frontmatter:** description with trigger phrases, `allowed-tools: Read Grep Glob`. Folder name `code-review/` becomes the skill name.
3. **Instructions:** Step-by-step workflow — fetch diff, analyze patterns, check for issues, present findings.
4. **File Structure:** `code-review/SKILL.md` + `references/review-checklist.md`.
5. **Validation:** Run checklist, verify triggers, test with sample PRs.

#### Example: Building an MCP-enhanced skill

User says: "I have Linear MCP connected, make a skill for sprint planning"

1. **Discovery:** Classify as Category 3 (MCP Enhancement). Use cases: "plan this sprint", "create tickets from backlog".
2. **Frontmatter:** `compatibility: Requires Linear MCP server`, `metadata: { mcp-server: linear }`. Folder name `sprint-planner/` becomes the skill name.
3. **Instructions:** Use fully qualified tool names (`Linear:create_issue`), phase-based workflow, error handling for MCP connection failures.
4. **File Structure:** `sprint-planner/SKILL.md` + `references/linear-api-patterns.md`.
5. **Validation:** Test triggers, verify MCP calls work, check for over-triggering on general project queries.

### Troubleshooting

**Frontmatter parse errors**
Cause: Missing `---` delimiters or tabs instead of spaces.
Solution: Verify YAML syntax — use spaces for indentation, ensure both `---` delimiters are present. Values do not need quoting.

**Skill doesn't trigger after creation**
Cause: Description too vague, missing trigger phrases, or skill context budget exceeded.
Solution: Add specific trigger phrases users would actually say. Run `/context` to check if the skill was excluded due to budget limits.

**Skill triggers for unrelated queries**
Cause: Description too broad or keywords overlap with other domains.
Solution: Add negative triggers ("Do NOT use for..."), narrow scope, or set `disable-model-invocation: true` for manual-only activation.

**Instructions not followed consistently**
Cause: Instructions are ambiguous, too verbose, or critical steps are buried.
Solution: Put critical instructions first, use numbered steps, keep SKILL.md under 500 lines, use `scripts/` for deterministic validations.

---

## Edit Flow

Review and improve an existing skill. The user provides a path to a skill folder.

### Step 1: Read and Assess

1. Read the skill's `SKILL.md`, all `references/` files, and any `scripts/`.
2. Read `references/01-fundamentals.md` to internalize the constraints.
3. Run the structural validator to get an immediate health check:
   ```
   python ${CLAUDE_SKILL_DIR}/scripts/validate-structure.py /path/to/skill
   ```
4. Review against the checklist in `references/06-checklist.md`.

### Step 2: Present Findings

Present a summary to the user covering:

- **Structural issues** — anything the validator caught (XML brackets, naming, missing fields)
- **Content quality** — are instructions clear and actionable? Are examples concrete? Is the skill under 500 lines?
- **Trigger quality** — does the description include enough trigger phrases? Is it too broad or too narrow?
- **Domain accuracy** — does the skill give correct, factual guidance for its domain? Flag anything that looks invented, overstated, or inaccurate.
- **What's good** — call out what works well so the user knows what to keep

Ask the user what they want to fix, or offer to fix everything you found.

### Step 3: Make Changes

1. Fix issues directly — do not just describe what needs changing
2. After making changes, re-run the structural validator to confirm fixes
3. Present a summary of what changed

### Step 4: Optional — Run Full Test Suite

Ask the user if they want to run the eval framework against the edited skill. If yes, follow the Test flow below.

---

## Test Flow

Run the eval framework against an existing skill. The user provides a path to a skill folder.

### Step 1: Confirm the Skill and Test Spec

1. Verify the skill path exists and contains a `SKILL.md`
2. Ask the user for the path to their TESTS.yaml (test specs live outside the skill folder, in an ephemeral eval workspace)
   - If they don't have one, offer to generate one in the ephemeral workspace:
     ```
     python -c "import tempfile, os; p = os.path.join(tempfile.gettempdir(), 'skill-evals', '{skill-name}'); os.makedirs(p, exist_ok=True); print(p)"
     ```
   - Or use `{project-root}/.skill-evals/{skill-name}/` for a gitignored project-local workspace
3. Read the TESTS.yaml and show the user a summary:
   - Number of `should_trigger` entries
   - Number of `should_not_trigger` entries
   - Number of edge cases
   - Number of behavioral tests
   - Model configured for tests

### Step 2: Run Tests

Run the test suite yourself using the Bash tool. Do NOT hand the user commands to run.

The test scripts live in `${CLAUDE_SKILL_DIR}/scripts/`.

1. **Always run Layer 1 first** (structural validation — no tokens consumed):
   ```
   python ${CLAUDE_SKILL_DIR}/scripts/validate-structure.py /path/to/skill
   ```

2. **Ask about Layers 2 and 3** — these spawn headless `claude -p` processes and consume additional tokens:
   - Layer 2 (trigger tests) is lightweight — one turn per test
   - Layer 3 (behavioral tests) uses more tokens — multiple turns per test, varies by `max_turns`
   - If the user says "run everything" or "full suite", run all layers:
   ```
   python ${CLAUDE_SKILL_DIR}/scripts/run-tests.py /path/to/skill --tests /path/to/TESTS.yaml
   ```

### Step 3: Report Results

Present results clearly:
- Pass/fail counts per layer
- Any failures with the specific assertion that failed and why
- Token usage

### Step 4: Fix Failures

If tests fail:
1. Diagnose the root cause from the failure output
2. Fix the skill files directly
3. Re-run the failing layer to confirm
4. Repeat until all tests pass

Ask the user before making changes if the fix involves altering the skill's behavior (not just structural fixes).
