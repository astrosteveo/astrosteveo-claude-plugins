---
name: pre-deploy
user-invocable: false
description: >
  Pre-deploy safety checklist — verifies a changeset is safe to ship. Checks build
  integrity, debug artifacts, secrets exposure, validation coverage, env var documentation,
  and migration safety. Use when the user says "pre-deploy", "ready to deploy",
  "ship check", "safe to push", "deploy checklist", or "pre-ship". Also use when
  the user runs /pre-deploy.
compatibility: Requires git, a build system, and file system access.
metadata:
  author: astrosteveo
  version: 1.0.0
  category: deployment
  tags: [deploy, checklist, safety, shipping]
---

# Pre-Deploy

A fast, focused safety check on the current changeset before deploying. Run this before every push to production. Unlike `/review` in fix mode (periodic, deep), this is lightweight and scoped to "is what I'm about to ship safe?"

## Instructions

### Step 1: Identify the Changeset

Determine what's being deployed:

1. Check `git status` for uncommitted changes
2. Check `git log --oneline origin/main..HEAD` for unpushed commits (adjust branch name if needed)
3. Get the full diff: `git diff origin/main..HEAD` (or against the last deployed commit if known)

If there are no changes to deploy, tell the user and stop.

### Step 2: Build Integrity

Run the project's full verification suite. Discover commands from `CLAUDE.md`, `package.json`, `Makefile`, or equivalent.

```
lint → test → build
```

**All three must pass.** If any fail, stop and report the failure. Do not proceed with other checks until the build is green — everything else is moot if it doesn't compile.

### Step 3: Debug Artifacts

Scan **changed files only** (not the entire codebase) for leftover debug code:

- `console.log` / `console.debug` / `console.warn` that aren't intentional logging (skip `console.error` — those are usually intentional)
- `debugger` statements
- Commented-out code blocks that look like debug leftovers
- `TODO` or `FIXME` comments added in this changeset (existing ones are fine)
- Hard-coded `localhost` URLs or test values in non-test files

Report findings with file:line. Not all are blockers — flag them and let the user decide.

### Step 4: Secrets Exposure

Scan the diff for accidentally committed secrets:

- API keys, tokens, or passwords (look for high-entropy strings, common key patterns)
- `.env` values that leaked into source files
- Hardcoded connection strings with credentials
- Private keys or certificates

**If secrets are found, alert immediately.** This is the only blocking check besides build failure.

### Step 5: API Route Safety

For any **new or modified API routes** in the changeset:

- [ ] Input validation present (request body parsed in try-catch, fields validated)
- [ ] Auth check present (session, token, or webhook signature verification)
- [ ] Error responses don't leak internal details
- [ ] Rate limiting on public-facing mutation endpoints

Skip this step if no API routes were changed.

### Step 6: Environment Variables

Check if the changeset introduces new environment variable references:

1. Extract all env var names referenced in changed files (e.g., `process.env.*`, `os.environ`, `env::var`, `ENV[]`, etc. depending on the language)
2. Compare against `.env.example` (or equivalent)
3. Flag any new env vars that aren't documented

If new env vars are found, remind the user to update `.env.example` and verify they're set in the deployment environment.

### Step 7: Database Changes

If the changeset includes SQL migration files or schema changes:

- Flag destructive operations (DROP, DELETE, TRUNCATE, column removal)
- Check for backward compatibility (can the previous version of the app still work with this schema?)
- Note if migrations need to be run manually before/after deploy

If no schema changes, skip this step.

### Step 8: Report

Present a concise pass/fail checklist:

```
## Pre-Deploy Check

**Changeset:** [N commits, M files changed]

| Check | Status | Notes |
|-------|--------|-------|
| Build (lint + test + build) | PASS/FAIL | |
| Debug artifacts | PASS/WARN | [count] findings |
| Secrets scan | PASS/FAIL | |
| API route safety | PASS/WARN/SKIP | |
| New env vars | PASS/WARN/SKIP | |
| Schema changes | PASS/WARN/SKIP | |

**Verdict:** Safe to deploy / Needs attention
```

If everything passes, tell the user they're clear to ship. If there are warnings, list them and let the user decide. If there are failures (build or secrets), block the deploy.

## Important

- **Speed matters.** This should take under 2 minutes. Don't deep-dive into architecture — that's what `/review` is for.
- **Only scan the changeset.** Don't audit the entire codebase. The question is "is this diff safe?" not "is the whole project healthy?"
- **Warnings are not blockers.** A `console.log` in a new feature might be intentional logging. Flag it, don't block on it.
- **Build failure IS a blocker.** Never suggest deploying a broken build.
- **Secrets ARE a blocker.** Never suggest deploying exposed credentials.
