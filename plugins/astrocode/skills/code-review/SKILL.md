---
name: code-review
user-invocable: false
description: >
  Review a pull request for bugs, edge cases, security issues, and code quality.
  Acts as an independent senior engineer reviewer. Use when the user says "review PR",
  "code review", "review this PR", "check this PR", or "review pull request".
  Also use when the user runs /code-review.
---

# Code Review

Review the specified pull request (or the current branch's open PR) as an independent reviewer. Act as a senior engineer who did NOT write the code.

## Process

1. **Find the PR** — if a PR number or URL is given, use that. Otherwise find the open PR for the current branch:
   ```bash
   gh pr view --json number,title,body,baseRefName,headRefName,url
   ```

2. **Get the full diff**:
   ```bash
   gh pr diff <number>
   ```

3. **Review the diff** looking for:

   ### Critical (must fix before merge)
   - Security vulnerabilities (injection, XSS, auth bypass, exposed secrets)
   - Data loss risks (destructive migrations, missing WHERE clauses)
   - Broken functionality (logic errors, missing null checks, unhandled errors)
   - Race conditions or concurrency bugs

   ### Important (should fix)
   - Missing input validation at API boundaries
   - Error handling gaps (unhandled promise rejections, missing try/catch)
   - Missing or incorrect type safety
   - Performance issues (N+1 queries, missing indexes, unnecessary re-renders)
   - Plan-tier gating gaps (feature accessible to wrong plan)

   ### Minor (nice to fix)
   - Code clarity improvements
   - Inconsistency with existing patterns/conventions
   - Missing edge cases in tests
   - Naming or organization suggestions

4. **Check for project-specific conventions** (from CLAUDE.md and .claude/rules/ if they exist):
   - Does the project have a pre-commit checklist? Are all checks passing?
   - Input validation on API routes?
   - Env var safety: no inline `process.env.X` comparisons?
   - Error responses: user-friendly messages only, no internal details?
   - Idempotent operations where applicable?

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

## Rules

- Be thorough but not pedantic — don't flag style preferences that aren't in the project conventions
- Don't suggest adding comments, docstrings, or type annotations to unchanged code
- Focus on the diff, not the entire file (unless context is needed to understand the change)
- If the PR is docs-only or config-only, say so and keep the review brief
- Always check if tests cover the changed code paths
- If no PR is found, tell the user and ask for a PR number or URL
