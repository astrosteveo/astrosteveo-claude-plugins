---
name: code-quality
description: Reviews codebases for quality issues: clean code, DRY violations, security vulnerabilities, performance problems, error handling, architecture smells, and best practice deviations. Builds full codebase understanding before making recommendations. All suggestions are non-breaking. Use when the user says "review code quality", "audit the codebase", "check code quality", "find code smells", "security audit", "performance review", "check for DRY violations", "code review the project", "find tech debt", "review code health", "check for security issues", "codebase audit", or asks for a broad quality assessment of the project. Do NOT use for writing new code, fixing a specific bug, implementing a feature, single-file edits, or general coding assistance.
---

# Code Quality

Comprehensive codebase quality review. Understands the full project context before
making any recommendations. Every finding is non-breaking and actionable.

Use ultrathink for thorough reasoning throughout this review.

## Critical: Context Before Criticism

NEVER flag code as problematic without understanding why it was written that way.
Read project documentation, conventions, and architecture first. Some patterns that
look wrong in isolation are intentional design decisions. The goal is to find genuine
issues, not to impose external style preferences on a codebase that has its own
coherent conventions.

## Workflow

### Phase 1: Understand the Codebase

Before reviewing ANY code, build a mental model of the project:

1. **Read project docs** — CLAUDE.md, README, CONTRIBUTING, architecture docs, style
   guides, any design documents. These define what "correct" looks like for THIS project.
2. **Map the directory structure** — use Glob to understand module boundaries, identify
   languages, frameworks, and build systems.
3. **Identify conventions** — note patterns the project uses intentionally: naming,
   architecture patterns, error handling style, dependency injection approach, etc.
4. **Note documented exceptions** — if docs say "we do X because of Y", that is NOT a
   finding. Record it so you skip it during analysis.

This phase is NOT optional. Skipping it produces false positives that waste the user's
time and erode trust in the review.

### Phase 2: Scope the Review

Determine what to review and how deeply:

1. **Identify target** — is this a full codebase review, or did the user specify files,
   modules, or categories (e.g., "check security", "review the auth code")?
2. **Estimate size** — count source files to pick a strategy:
   - Small (under 50 files): review all source files
   - Medium (50-200 files): review all, prioritize core modules
   - Large (200+ files): fully review core modules, spot-check utilities and generated code
3. **Skip non-reviewable content** — vendored/third-party code, generated files, build
   artifacts, test fixtures, binary assets. Note what you skipped.

For large codebases, use Agent subagents (subagent_type: Explore) to parallelize
discovery across independent modules. Each subagent explores one module and returns
findings.

### Phase 3: Analyze

Review code against the categories in `references/review-categories.md`. For each file:

1. Read the code carefully — skim produces bad findings
2. Check against each applicable review category
3. For each potential finding, ask yourself:
   - "Is this consistent with the project's documented conventions?"
   - "Does the surrounding code suggest this pattern is intentional?"
   - "Would fixing this actually improve the codebase, or just make it different?"
4. Only record findings that are genuinely problematic after considering context

For large codebases, launch parallel Agent subagents (subagent_type: general-purpose)
to analyze independent modules simultaneously. Give each subagent:
- The project conventions you learned in Phase 1
- The specific files/module to review
- The review categories to check
- Instructions to return structured findings

### Phase 4: Synthesize and Report

Compile findings into a clear report following `references/report-format.md`:

1. **Deduplicate** — if the same pattern appears in 10 files, report it once with all
   locations, not 10 separate findings
2. **Prioritize** — rank by severity and impact, not by order discovered
3. **Filter** — remove anything you're not confident about. A shorter report with high
   signal is better than a long report with noise.
4. **Acknowledge strengths** — note what the codebase does well. A report that's all
   negatives is inaccurate and unhelpful.
5. **List excluded patterns** — briefly note patterns you investigated but determined
   were intentional, to show you understood the codebase.

## Rules

- **Non-breaking only**: every recommendation must be safe to apply without changing
  external behavior. No API changes, no signature changes, no architectural rewrites.
- **No nitpicking**: skip formatting preferences, naming style bikesheds, and subjective
  choices unless they cause genuine confusion or bugs.
- **Severity matters**: a SQL injection is critical. A duplicated 3-line block is low.
  Rank accordingly.
- **Respect the codebase**: if the project has conventions (even unusual ones), respect
  them. Consistency within the project beats conformance to external ideals.
- **Actionable**: every finding must include a concrete suggestion. "This could be
  better" is not a finding.
- **File references**: always include `path/to/file:line_number` so the user can
  navigate directly to each finding.

## Handling Ambiguity

When you're unsure whether something is intentional:

- **If documented** — not a finding. Skip it.
- **If the pattern is consistent across the codebase** — probably intentional. Mention
  it as an observation, not a finding.
- **If it appears once and contradicts the rest of the codebase** — likely a finding.
  Flag it, but note the ambiguity.
- **If you genuinely can't tell** — ask the user rather than guessing.

## Examples

### Example 1: Full codebase review
User says: "Review the code quality of this project"
1. Read CLAUDE.md and all referenced architecture docs
2. Map directory structure, identify all source modules
3. Review each module against all categories
4. Present categorized findings with severity and effort

### Example 2: Targeted security review
User says: "Check the authentication code for security issues"
1. Read project docs for auth architecture context
2. Find all auth-related files
3. Deep review focused on security categories from references
4. Present security-focused findings only

### Example 3: Tech debt scan
User says: "What's the worst tech debt in this codebase?"
1. Read project docs for known conventions and debt
2. Scan for DRY violations, dead code, complexity hotspots
3. Rank by impact (how much it slows development) and effort to fix
4. Present top findings as a prioritized list
