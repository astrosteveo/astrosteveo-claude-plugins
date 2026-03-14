---
name: incident
user-invocable: false
description: >
  Systematic incident response — trace production issues through recent deploys,
  error patterns, and code changes to identify root cause and suggest fixes.
  Use when the user says "something broke", "production issue", "incident",
  "debug this error", "why is this failing", "site is down", or "users are
  reporting". Also use when the user runs /incident.
compatibility: Requires git and file system access. Enhanced with deployment logs and error monitoring if available.
metadata:
  author: astrosteveo
  version: 1.0.0
  category: operations
  tags: [incident, debugging, production, root-cause]
---

# Incident

Systematic incident response for production issues. Follow a structured runbook instead of panicking. The goal is: identify what changed, find the root cause, fix it, and prevent recurrence.

## Instructions

### Step 1: Gather Context

Ask the user (if not already provided):

1. **What's happening?** — Error message, broken behavior, user report
2. **When did it start?** — Approximate time or "after the last deploy"
3. **Who's affected?** — All users, specific accounts, specific actions
4. **What changed recently?** — Deploys, config changes, external service updates

Don't spend too long here — get the basics and start investigating.

### Step 2: Recent Changes

Check what was deployed recently:

```bash
git log --oneline --since="3 days ago"  # or adjust based on user's timeline
```

For each recent commit:
- What files were changed?
- Does the changed code touch the affected area?
- Were there any migration or config changes?

Identify the **most likely suspect commit** based on timing and relevance.

### Step 3: Error Analysis

If the user provides an error message or stack trace:

1. **Trace the error to source:** Match the stack trace to specific files and line numbers
2. **Read the surrounding code:** Understand the context, not just the failing line
3. **Check recent changes to that file:** `git log --oneline -5 [file]`
4. **Look for related errors:** Search for similar patterns in adjacent code

If no error message is available:
1. Check if the project has error monitoring (Sentry, Vercel logs)
2. Suggest the user check deployment logs: offer commands for their platform
3. Try to reproduce by reading the code path the user describes

### Step 4: Root Cause Identification

Work backward from the symptom:

1. **Is it a code change?** Compare the suspect commit's diff against the error
2. **Is it a data issue?** Could a new database state trigger the error?
3. **Is it an external service?** Check if the error involves third-party APIs or external dependencies
4. **Is it a configuration issue?** Missing or changed env vars, expired tokens, rotated keys
5. **Is it a race condition or timing issue?** Only happens under load, concurrent requests, or specific timing

State the root cause clearly: "The issue is [X] because [Y], introduced in [commit/change]."

### Step 5: Fix

Propose a fix based on the root cause:

1. **Quick fix:** The minimal change to resolve the immediate issue
2. **Proper fix:** The correct solution if different from the quick fix
3. **If they differ:** Present both and let the user choose. In an active incident, the quick fix ships first, with the proper fix following.

Implement the chosen fix. Verify with lint + test + build.

### Step 6: Verify the Fix

1. Run the full verification suite (lint → test → build)
2. If possible, trace through the code path that was failing to confirm the fix addresses it
3. Check for regression — does the fix break anything adjacent?

### Step 7: Postmortem Notes

After the fix, provide a brief summary:

```
## Incident Summary

**Symptom:** [What the user saw]
**Root cause:** [What was actually wrong]
**Fix:** [What was changed] ([commit hash])
**Introduced:** [When/how the bug was introduced]
**Prevention:** [What would have caught this — test, validation, monitoring]
```

Suggest a preventive measure:
- A test case that would have caught this
- A validation check that would have blocked the bad state
- A monitoring alert that would have detected it sooner
- A rule file entry that would prevent the pattern

## Important

- **Speed matters during incidents.** Don't over-analyze — find the likely cause, fix it, verify, then do the deep dive.
- **Don't make it worse.** Avoid broad refactors during an incident. Minimal, targeted fixes only.
- **Communicate clearly.** The user may be stressed. State findings directly: "I found the issue" or "I need more information."
- **Always verify the fix.** Never suggest deploying an unverified fix, especially during an incident.
- **Suggest prevention, don't lecture.** The postmortem note should be actionable, not a guilt trip.
