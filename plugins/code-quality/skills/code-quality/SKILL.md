---
description: Comprehensive codebase quality review. Use when the user says "review code quality", "audit the codebase", "check for security issues", "find tech debt", or requests a broad quality assessment. Non-breaking recommendations only.
argument-hint: "[scope: file, module, or category]"
---

# Code Quality

Comprehensive codebase quality review. Builds full project understanding before making any recommendations. Every finding is non-breaking and actionable.

If `$ARGUMENTS` specifies a scope (file, module, or category), focus the review there.

## Context Before Criticism

Never flag code as problematic without understanding why it was written that way. Read project documentation, conventions, and architecture first. Patterns that look wrong in isolation may be intentional design decisions. The goal is to find genuine issues, not impose external style preferences.

## Workflow

### Phase 1: Understand the Codebase

Before reviewing any code:

1. **Read project docs** — CLAUDE.md, README, CONTRIBUTING, architecture docs, style guides. These define what "correct" means for this project.
2. **Map the structure** — use Glob to understand module boundaries, languages, frameworks, and build systems.
3. **Identify conventions** — naming, architecture patterns, error handling style, dependency injection approach.
4. **Note exceptions** — if docs say "we do X because of Y", that is not a finding. Record it so you skip it during analysis.

This phase is not optional. Skipping it produces false positives that waste the user's time and erode trust in the review.

### Phase 2: Scope the Review

1. **Identify target** — full codebase review, or specific files, modules, or categories (e.g., "check security", "review the auth code")?
2. **Pick strategy by size:**
   - Small (under 50 files): review all source files
   - Medium (50-200): review all, prioritize core modules
   - Large (200+): fully review core modules, spot-check utilities and generated code
3. **Skip non-reviewable content** — vendored/third-party code, generated files, build artifacts, test fixtures, binaries. Note what you skipped.

For large codebases, use Agent subagents (subagent_type: Explore) to parallelize discovery, then general-purpose agents to analyze independent modules.

### Phase 3: Analyze

Review code against the categories in `references/review-categories.md`. For each file:

1. Read carefully — skimming produces bad findings
2. Check against each applicable review category
3. For each potential finding, ask:
   - Is this consistent with the project's documented conventions?
   - Does surrounding code suggest this pattern is intentional?
   - Would fixing this actually improve the codebase, or just make it different?
4. Only record genuinely problematic findings

For large codebases, launch parallel Agent subagents (subagent_type: general-purpose) to analyze independent modules. Give each agent the project conventions from Phase 1, specific files to review, and the review categories.

### Phase 4: Report

Compile findings following `references/report-format.md`:

1. **Deduplicate** — same pattern in 10 files? Report once with all locations.
2. **Prioritize** — rank by severity and impact, not discovery order.
3. **Filter** — remove low-confidence findings. A shorter high-signal report beats a noisy long one.
4. **Acknowledge strengths** — note what the codebase does well.
5. **List intentional patterns** — patterns you investigated but determined were intentional, to show you understood the codebase.

## Rules

- **Non-breaking only**: every recommendation must be safe to apply without changing external behavior. No API changes, no signature changes, no architectural rewrites.
- **No nitpicking**: skip formatting preferences, naming bikesheds, and subjective choices unless they cause genuine confusion or bugs.
- **Severity matters**: SQL injection is critical. Duplicated 3-line block is low. Rank accordingly.
- **Respect the codebase**: if the project has conventions (even unusual ones), respect them. Consistency within the project beats conformance to external ideals.
- **Actionable**: every finding includes a concrete suggestion. "This could be better" is not a finding.
- **File references**: always include `path/to/file:line_number`.

## Handling Ambiguity

- **Documented** — not a finding. Skip it.
- **Consistent across the codebase** — probably intentional. Mention as observation, not finding.
- **Appears once, contradicts the rest** — likely a finding. Flag it, note the ambiguity.
- **Can't tell** — ask the user rather than guessing.

## Examples

**Full codebase review** — "Review the code quality of this project":
1. Read all project docs for context
2. Map structure, identify modules
3. Review each module against all categories
4. Present categorized findings with severity and effort

**Targeted review** — "Check the auth code for security issues":
1. Read project docs for auth architecture context
2. Find all auth-related files
3. Deep review focused on security categories
4. Present security-focused findings only

**Tech debt scan** — "What's the worst tech debt?":
1. Read docs for known conventions and debt
2. Scan for DRY violations, dead code, complexity hotspots
3. Rank by impact and effort to fix
4. Present as prioritized list
