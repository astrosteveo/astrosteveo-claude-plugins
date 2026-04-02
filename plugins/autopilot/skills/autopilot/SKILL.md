---
name: autopilot
description: >
  Autonomous development mode where Claude continuously analyzes the codebase,
  decides what to work on next, and implements improvements in a loop. Use when
  the user says "go on autopilot", "autopilot mode", "just do your thing",
  "run autonomously", "free roam", or runs /autopilot. Accepts an optional
  prompt to steer the direction of work. Runs until the user asks it to stop.
  Do NOT trigger for general coding requests, single tasks, or when the user
  asks for help with a specific problem.
argument-hint: "[optional direction]"
metadata:
  author: astrosteveo
  version: 1.0.0
  category: development
  tags: [autonomous, development, creative]
---

# Autopilot

Autonomous development mode. You analyze the codebase, decide what's most valuable to work on, implement it, and repeat — until the user tells you to stop.

## Critical Rules

- Each iteration MUST be independently valuable — never start something you can't finish in one cycle
- NEVER touch sensitive files (.env, credentials, secrets, CI/CD pipelines) without explicit user confirmation
- NEVER make destructive changes (deleting files, dropping data, force-pushing) without asking
- Prefer real improvements over busywork — no reformatting, no adding comments to obvious code, no shuffling imports
- Be transparent — the user should always be able to follow what you're doing and why
- Respect the project's existing conventions, patterns, and architecture

## Phase 1: Initialization

When the skill activates, orient yourself before doing anything.

### Step 1: Build context

Read in parallel:
- Project root for CLAUDE.md, README, package configs, or build files
- Git log (last 20 commits) to understand recent momentum and direction
- Directory structure (top two levels) to map the codebase

### Step 2: Identify the north star

If the user passed a direction via arguments:
- Treat it as a loose north star, not a rigid constraint
- Work should generally move toward that direction, but you have creative latitude

If no arguments were passed:
- You have full creative freedom — pick whatever you think adds the most value

### Step 3: Announce

Print a brief status:

```
AUTOPILOT ENGAGED
Direction: [user's prompt, or "Full creative freedom"]
Codebase: [language/framework/size summary]
Starting first survey...
```

Then immediately begin the loop.

## Phase 2: The Loop

Each iteration follows five steps. Use ultrathink during the Survey and Decide steps to reason deeply about what's most valuable.

### Step 1: Survey

Explore the codebase to identify 3-5 candidates for your next unit of work. Look broadly across these dimensions:

- Missing or weak test coverage
- Code that's hard to read or overly complex
- TODOs, FIXMEs, or HACKs left in the code
- Missing error handling at system boundaries
- Performance issues (N+1 queries, unnecessary allocations, blocking calls)
- Features that are partially implemented
- Documentation gaps that actually hurt usability
- DRY violations — duplicated logic that should be consolidated
- Security issues (unsanitized input, exposed secrets, injection vectors)
- Developer experience improvements (better scripts, tooling, configs)
- Anything else that catches your eye as genuinely valuable

Don't just read files — use Grep, Glob, and targeted reads to actually understand the landscape. Each candidate should be something concrete, not a vague "improve X."

### Step 2: Decide

Pick one candidate. Choose based on:

1. **Value** — How much does this improve the project?
2. **Feasibility** — Can you complete it in one focused cycle?
3. **Risk** — Lower risk is better for autonomous work
4. **Variety** — Avoid doing the same type of work repeatedly across iterations

Print your decision:

```
ITERATION [N]
Working on: [brief description]
Why: [one sentence justification]
Type: [feature | refactor | test | fix | docs | dx | perf | security]
```

### Step 3: Implement

Do the work. This should be a focused, bounded chunk — think "one solid PR's worth" or less.

Guidelines:
- Write code that matches the project's existing style and conventions
- If you're adding a feature, add tests for it
- If you're fixing a bug, add a regression test
- If you're refactoring, make sure existing tests still pass
- Run any available test suite or linter after your changes to verify nothing broke
- If something goes wrong mid-implementation, revert cleanly rather than leaving broken code

### Step 4: Reflect

After completing the work, print a brief reflection:

```
COMPLETED: [what you did]
Changed: [list of files touched]
Learned: [anything interesting about the codebase]
Impact: [what's better now]
```

### Step 5: Continue or Pivot

Before starting the next iteration:

1. **Check for user messages** — if the user sent a message while you were working:
   - If it's a redirect ("focus on X instead"), acknowledge and shift your north star
   - If it's a stop signal ("stop", "pause", "that's enough"), go to Phase 3
   - If it's feedback on your work, incorporate it
   - If it's a question, answer it, then continue the loop

2. **Assess momentum** — if you've done 5+ iterations, briefly reassess:
   - Are you still finding high-value work?
   - Is the direction still productive?
   - Should you suggest pausing to the user?

3. **Start the next iteration** — go back to Step 1 (Survey)

## Phase 3: Landing

When the user asks you to stop (or you've run out of high-value work to do):

### Step 1: Wrap up cleanly

If you're mid-implementation:
- Finish if you're close (under a minute of work remaining)
- Otherwise, revert any partial changes so the codebase is clean

### Step 2: Flight log

Present a summary of the entire session:

```
AUTOPILOT DISENGAGED

Session summary:
- Iterations completed: [N]
- Direction: [what you were working toward]

Work log:
1. [Type] [Description] — [files changed]
2. [Type] [Description] — [files changed]
...

Key observations:
- [Anything notable about the codebase worth mentioning]
- [Suggestions for future work you didn't get to]
```

## Handling Edge Cases

**Empty or tiny codebase:**
If the project has very little code, focus on scaffolding, project setup, documentation, or foundational architecture rather than refactoring.

**No obvious improvements:**
If the codebase is in great shape and you're struggling to find valuable work, say so. Suggest the user provide a direction, or recommend specific areas that could benefit from new features.

**Conflicting conventions:**
If you find inconsistent patterns in the codebase, don't try to unify everything in one iteration. Pick the dominant convention and apply it to the area you're working in. Note the inconsistency in your reflection.

**Tests failing before you start:**
If the test suite is already failing when you begin, note it in your initialization. Don't count pre-existing failures against your own changes.
