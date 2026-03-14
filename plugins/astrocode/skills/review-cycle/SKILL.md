---
name: review-cycle
user-invocable: false
description: >
  Full codebase review cycle — audit, fix, verify, align docs, update backlog.
  Use when the user says "review cycle", "project review", "codebase review",
  "health check and fix", "what needs attention", "review and fix", or
  "clean things up". Also use when the user runs /review-cycle.
compatibility: Requires Claude Code with file system access, git, and a build system.
metadata:
  author: astrosteveo
  version: 1.0.0
  category: code-quality
  tags: [review, code-health, docs, backlog, maintenance]
---

# Review Cycle

A periodic codebase review that audits, fixes, verifies, aligns documentation, and updates the backlog. Run this every sprint or two, or before any major milestone.

This is the full loop. `/code-health` is the diagnostic (read-only report). `/review-cycle` is the doctor's visit (diagnose, treat, verify, update the chart).

## Prerequisites

- Git repository with a working build system
- `CLAUDE.md` or equivalent project documentation (read this first to discover lint/test/build commands)
- `.claude/PROGRESS.md` for state tracking (created by `/project-state` if missing)
- A build/lint/test pipeline — discover commands from CLAUDE.md, package.json, Makefile, Cargo.toml, pyproject.toml, or equivalent. If no build command exists, skip the build step but note it as a gap.

## Instructions

### Phase 1: Audit

Run the `/code-health` analysis to produce a severity-tiered report. Use parallel agents to scan:

1. **Core libraries** — duplication, error handling, security, performance, type safety
2. **API routes** — validation, auth, error handling, response consistency
3. **UI components & pages** — complexity, accessibility, error boundaries, loading states
4. **Test coverage** — gaps, quality, anti-patterns
5. **Config & dependencies** — tsconfig, package.json, eslint, deployment config

Compile into a single report organized by severity:
- **CRITICAL** — fix before next deploy
- **HIGH** — address soon
- **MEDIUM** — plan for next sprint
- **LOW** — tech debt backlog

Present the report to the user. Include an overall health score (X/10) and a recommended action plan split into "This week" and "Next sprint" buckets.

### Phase 2: Confirm Priorities

Before fixing anything, present the action plan and ask the user:

> "Here's what I'd fix in priority order. Want to proceed with all of these, or adjust the scope?"

Respect the user's choices. They may want to skip items, reorder, or add context you don't have.

### Phase 3: Fix Sprint

Work through the confirmed fixes in priority order:

1. Make the code changes
2. After each logical group of fixes, verify using the project's lint, test, and build commands (discovered from `CLAUDE.md`, `package.json`, `Makefile`, `Cargo.toml`, `pyproject.toml`, or equivalent):
   - Lint
   - Test
   - Build
   - **All three must pass before moving to the next group.**
3. Do NOT commit yet — batch related fixes into meaningful commits at the end

If a fix breaks something, stop and reassess. Don't force through.

### Phase 4: Verify

After all fixes are applied, run the full verification suite one final time:

```
lint → test → build
```

All three must pass. If any fail, fix the issue before proceeding. Do not skip the build step — it catches type errors that lint and tests miss (e.g., null vs undefined in server components).

### Phase 5: Align Documentation

Check and update these files to reflect current reality:

1. **`CLAUDE.md`** — Are test counts, library descriptions, conventions, and API route lists current? Update any stale information.
2. **Product brief / roadmap** (if exists) — Do milestones, tech stack, and phase descriptions match what's actually built? Check off completed items, correct outdated claims.
3. **`.claude/rules/`** (if exists) — Do rule files cover the patterns that caused the issues found in Phase 1? If the audit found a recurring class of bug, consider adding a rule to prevent it.

Do NOT create new documentation files unless explicitly asked. Only update existing ones.

### Phase 6: Update Backlog

Rewrite the backlog section of `.claude/PROGRESS.md`:

1. **Clear completed items** — they're in git history, don't keep them around
2. **Add forward-looking items** organized by priority tier:
   - Priority 1: What's needed next (beta, launch, current milestone)
   - Priority 2: Feature work that differentiates the product
   - Priority 3: Growth and scaling concerns
   - Priority 4: Remaining code health and tech debt
3. **Update "Current State"** to reflect where the project actually is

### Phase 7: Commit & Report

Follow the `/commit` workflow (see `astrocode:commit` skill) for all commits:

1. Stage and commit fixes using the conventional commit format: `<type>(<scope>): <description>`. Use the type that best describes the change (`fix`, `refactor`, `perf`, `style`, etc.) and scope to the affected area. Group related fixes into a single logical commit where it makes sense.
2. After source commits, update `.claude/PROGRESS.md` with the new HEAD hash and commit state separately per the `/commit` workflow.
3. Present a summary to the user:
   - What was found (count by severity)
   - What was fixed
   - What was deferred and why
   - What docs were updated
   - Current test count and build status

## Important

- **Always verify builds.** Lint + test is not enough. The production build must pass.
- **Don't fix everything.** Focus on critical and high items. Medium and low go in the backlog.
- **Respect existing patterns.** If the codebase does something consistently, that's a convention. Don't rewrite it unless it's causing real problems.
- **Ask before large refactors.** If a fix touches more than ~5 files or changes an architectural pattern, confirm with the user first.
- **No scope creep.** The review cycle is audit → fix → verify → docs → backlog. Don't add features, don't redesign the UI, don't refactor things that aren't broken.

## Examples

### Example 1: Periodic Review
User says: "Let's do a review cycle" or "What needs attention?"
Actions: Full Phase 1-7 cycle. Audit everything, present report, fix critical/high with user approval, verify, align docs, update backlog.

### Example 2: Targeted Review
User says: "Review the API routes" or "Check the auth flow"
Actions: Phase 1 scoped to the specified area. Phases 2-7 as normal but limited to relevant findings.

### Example 3: Pre-Launch Review
User says: "Are we ready to launch?" or "Launch readiness check"
Actions: Full cycle with extra emphasis on security (auth, validation, rate limiting), error handling, and user-facing correctness. Flag anything that could embarrass in front of real users.
