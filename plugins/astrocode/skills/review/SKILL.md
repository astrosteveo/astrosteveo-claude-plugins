---
name: review
user-invocable: false
description: >
  Unified code review — PR diffs, codebase audits, security checks, and full fix cycles.
  Auto-detects mode from context: PR review for open PRs, audit mode for read-only reports,
  fix mode for audit-then-fix cycles. Use when the user says "review", "code review",
  "review PR", "code health", "security audit", "what needs attention", "review and fix",
  "clean things up", "check for vulnerabilities", "find tech debt", or "review cycle".
  Also use when the user runs /review.
---

# Review

A unified review skill that handles PR reviews, codebase audits, and full fix cycles. The mode is determined by context — you don't need to ask which one.

## Mode Detection

Determine the mode from the user's request and context:

**PR mode** — an open PR exists for the current branch, or the user says "review PR", "code review", "check this PR"
→ Diff-focused review of the pull request.

**Audit mode** — the user says "code health", "security audit", "find tech debt", "check for vulnerabilities", "what needs refactoring", "performance check", or similar diagnostic request
→ Read-only report across the codebase. Do NOT modify code.

**Fix mode** — the user says "review and fix", "review cycle", "clean things up", "health check and fix", "what needs attention"
→ Full audit → confirm priorities → fix → verify → align docs → update backlog.

If the mode is ambiguous, ask the user: "Do you want a read-only report, or should I also fix what I find?"

---

## PR Mode

Review the specified pull request (or the current branch's open PR) as an independent senior engineer reviewer.

### Process

1. **Find the PR** — if a PR number or URL is given, use that. Otherwise find the open PR for the current branch:
   ```bash
   gh pr view --json number,title,body,baseRefName,headRefName,url
   ```

2. **Get the full diff**:
   ```bash
   gh pr diff <number>
   ```

3. **Review the diff** across all check categories (see below), scoped to changed code only.

4. **Check project-specific conventions** from `CLAUDE.md` and `.claude/rules/` if they exist.

5. **Output a structured review**:

   ```
   ## PR Review: <title>

   **Verdict:** ✅ Approve / ⚠️ Approve with suggestions / ❌ Changes requested

   ### Critical
   - (list or "None found")

   ### Important
   - (list or "None found")

   ### Minor
   - (list or "None found")

   ### What looks good
   - (positive callouts — good patterns, solid test coverage, etc.)
   ```

6. **If changes are requested**, provide specific file:line references and suggested fixes.

### PR Mode Rules
- Focus on the diff, not the entire file (unless context is needed)
- Don't suggest adding comments, docstrings, or type annotations to unchanged code
- If the PR is docs-only or config-only, keep the review brief
- Always check if tests cover the changed code paths
- If no PR is found, tell the user and ask for a PR number or URL

---

## Audit Mode

Analyze the codebase and produce a prioritized, read-only report. Do NOT modify any code.

### Scope

- **Full audit:** Broad request ("code health", "security audit") → scan the entire codebase
- **Targeted audit:** User points to specific files/directories → focus there
- **Category-specific:** User asks about security, performance, or conventions specifically → focus on that category

### Process

1. **Understand the project** — read `CLAUDE.md`, identify tech stack, note established patterns and conventions.

2. **Scan all check categories** (see below) appropriate to the scope.

3. **Compile report**:

   ```
   ## Review Report

   **Scope:** [What was analyzed]
   **Date:** [Current date]
   **Focus:** [All categories / Security / Performance / Code quality]

   ### Summary
   Brief overview of overall health — what's working well and what needs attention.

   ### Critical (Immediate action required)
   ### High (Address soon)
   ### Medium (Plan to address)
   ### Low (Improvement opportunities)

   ### For each finding:
   - **Location:** file:line_number
   - **Category:** Code quality / Security / Performance / Architecture / Conventions
   - **Description:** What the issue is and why it matters
   - **Impact:** What could happen (for security) or what it costs (for performance/quality)
   - **Recommendation:** Specific fix with code example where helpful
   - **Effort:** Quick fix / Moderate / Significant refactor

   ### Recommended Action Plan
   **This week:** Critical/high quick wins
   **Next sprint:** Medium items, larger refactors
   ```

### Audit Mode Rules
- Do NOT modify any code
- Be pragmatic — not every imperfection is worth fixing
- Respect existing patterns — consistency is a convention, not a violation
- Credit what's done well alongside issues
- If you discover critical security issues (exposed credentials), alert immediately

---

## Fix Mode

Full review cycle: audit, fix, verify, align docs, update backlog.

### Prerequisites
- Git repository with a working build system
- `CLAUDE.md` or equivalent project documentation
- `.claude/PROGRESS.md` for state tracking

### Process

#### Phase 1: Audit
Run a full audit (same as Audit Mode above) using parallel agents to scan:
1. Core libraries — duplication, error handling, security, performance, type safety
2. API routes — validation, auth, error handling, response consistency
3. UI components & pages — complexity, accessibility, error boundaries
4. Test coverage — gaps, quality, anti-patterns
5. Config & dependencies — project config, linter config, deployment config

Compile into a single report with severity tiers and an overall health score (X/10).

#### Phase 2: Confirm Priorities
Present the action plan and ask the user:
> "Here's what I'd fix in priority order. Want to proceed with all of these, or adjust the scope?"

Respect the user's choices.

#### Phase 3: Fix Sprint
Work through confirmed fixes in priority order:
1. Make the code changes
2. After each logical group of fixes, verify: lint → test → build. All three must pass before moving on.
3. Do NOT commit yet — batch related fixes for the end.

If a fix breaks something, stop and reassess.

#### Phase 4: Verify
Run the full verification suite one final time: lint → test → build. All must pass.

#### Phase 5: Align Documentation
Update existing docs to reflect current reality:
1. `CLAUDE.md` — test counts, library descriptions, conventions, API route lists
2. Product brief / roadmap (if exists) — milestones, tech stack, phase descriptions
3. `.claude/rules/` (if exists) — add rules to prevent recurring issue classes

Do NOT create new documentation files unless explicitly asked.

#### Phase 6: Update Backlog
Rewrite the backlog section of `.claude/PROGRESS.md`:
1. Clear completed items
2. Add forward-looking items organized by priority tier
3. Update "Current State" to reflect where the project actually is

#### Phase 7: Commit & Report
Follow the `/commit` workflow for all commits:
1. Stage and commit fixes using conventional commit format, grouped logically
2. Update `.claude/PROGRESS.md` with new HEAD hash, commit state separately
3. Present summary: what was found, what was fixed, what was deferred, what docs were updated

### Fix Mode Rules
- Always verify builds — lint + test is not enough
- Don't fix everything — critical and high first, medium and low go in the backlog
- Ask before large refactors (5+ files or architectural changes)
- No scope creep — don't add features or redesign during a review

---

## Check Categories

All modes draw from these categories. PR mode applies them to the diff only. Audit and fix modes apply them to the full codebase (or scoped area).

### Code Quality
- **Complexity:** Long functions, deep nesting, god objects, complex conditionals
- **Duplication:** Copy-pasted blocks, similar logic implemented differently (flag at 3+ occurrences)
- **Naming:** Inconsistent conventions, unclear names, magic numbers/strings
- **Dead code:** Unused exports/functions/variables, commented-out blocks, unreachable paths
- **Error handling:** Swallowed exceptions, generic catch-all handlers, missing error handling on I/O

### Security
- **OWASP Top 10:** Injection (SQL, XSS, command, template, path traversal), broken access control (missing auth, IDOR, CSRF, CORS), cryptographic failures (hardcoded secrets, weak hashing), insecure design (missing rate limiting, predictable tokens), security misconfiguration (debug mode, default credentials, missing headers, env var null-check bypasses), vulnerable components, auth failures (weak sessions, JWT issues), data integrity, logging failures (PII in logs), SSRF
- **Secrets scan:** API keys, tokens, passwords, connection strings, private keys in source. Check `.gitignore` coverage.
- **Dependency audit:** Known vulnerabilities, outdated packages, unmaintained dependencies

### Performance
- **N+1 queries:** Loops making one query per iteration
- **Missing indexes:** Columns in WHERE/JOIN/ORDER BY without indexes, unindexed foreign keys
- **Sequential awaits:** Independent async calls that could use `Promise.all()`
- **Response size:** `SELECT *` when subset needed, missing pagination
- **Frontend:** Unnecessary re-renders, client components that could be server components, bundle bloat, data fetching waterfalls
- **Caching:** Repeatedly fetched data that changes rarely

### Architecture
- **Separation of concerns:** Business logic in route handlers, scattered DB queries, tight coupling
- **Consistency:** Same problem solved different ways, mixed paradigms without reasoning
- **Dependency health:** Circular dependencies, fragile bottlenecks, inappropriate cross-boundary imports

### Conventions
- **Project patterns:** Deviations from the codebase's dominant patterns
- **Linter adherence:** Suppressed rules (`eslint-disable`, `noqa`, `@ts-ignore`)
- **Tech debt markers:** TODO, FIXME, HACK, XXX, TEMP, WORKAROUND comments
- **Deprecated usage:** Outdated patterns where the framework/language has better alternatives

## Important

- **Be thorough but not pedantic.** Don't flag style preferences that aren't in the project conventions.
- **Specific is actionable.** Cite exact file paths and line numbers. Vague findings waste time.
- **Distinguish "different" from "problematic."** Only report the latter.
- **Avoid false positives.** If uncertain, note your confidence level.
- **Test vs. production code.** Issues in test-only code are generally lower severity.
