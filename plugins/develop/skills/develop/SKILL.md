---
name: develop
description: End-to-end development workflow for implementing features, fixing bugs, refactoring code, and any substantial code change touching multiple files or systems. The main chat orchestrates — discovering requirements, researching the codebase, planning the work — then dispatches implementation agents with precise briefs and a review agent for final validation. Use when the user says "build this feature", "implement this", "add [feature]", "fix this bug", "refactor this", "I need to build", "help me implement", "plan and implement", "walk me through building this", "let's develop this", "let's think through this", or describes a substantial code change and wants a structured approach. Also triggers when the user provides a bug report, feature request, or issue number and wants it implemented. Do NOT use for one-line fixes, simple renames, quick formatting, questions about code, or tasks that only touch a single file.
argument-hint: "[feature description, bug report, or issue number]"
---

# Develop

Orchestrator-driven development workflow. The main chat stays clean — it understands the problem, plans the work, and dispatches agents. Implementation happens in fresh agent contexts with precise briefs. A separate review agent validates everything at the end.

## Core Architecture

You are the **orchestrator**. You do NOT write implementation code yourself. Your job:

1. Understand the problem deeply (Discover)
2. Research the codebase (Research)
3. Design the approach (Strategize)
4. Break work into dispatchable tasks (Plan)
5. Dispatch implementation agents — parallel when independent, sequential when dependent (Implement)
6. Dispatch a review agent to validate all changes (Review)
7. Handle delivery — commits and PRs (Deliver)

Every phase has a user gate. Nothing moves forward without explicit approval.

## Critical Rule: One Question at a Time

When you need a clarifying question, ask exactly ONE per message. The number of questions scales with complexity, but each gets its own message. If the user says "use your best judgment," accept that and move on.

## Routing

When invoked, check for arguments:
- `/develop [description]` — Start with the given description
- `/develop #123` or `/develop [URL]` — Start seeded from a GitHub issue
- `/develop` with no arguments — Ask the user what they want to work on
- If the user mentions resuming or picking up work — Identify the current phase and re-enter there

## Phase 1: Discover

Goal: Deeply understand the task, classify it, and surface every unknown before any code is explored.

### Classify the Task

After hearing the user's description, infer the nature of the work:

- **Feature** — New capability. Full treatment: thorough research, multiple approaches, comprehensive test strategy.
- **Bug fix** — Something is broken. Focus on reproduction, root cause, and regression testing.
- **Refactor** — Code works but needs restructuring. Preserve behavior, improve internals.
- **Integration** — Connecting systems. Interface design, error handling, dependency mapping.
- **Optimization** — Code works but needs to be faster/smaller/more efficient. Measure before and after.

State your classification and explain how it shapes the approach. If the task blends categories, say so.

### Probe for Unknowns

Think about what the user has NOT told you — edge cases, implicit assumptions, things that will bite during implementation.

Ask about:
- Constraints not mentioned (performance, compatibility, accessibility, security)
- Edge cases in inputs or behavior
- Interactions with existing functionality
- What "done" looks like — concrete acceptance criteria
- Anything ambiguous

One question at a time. Keep asking until you're confident. The user can say "that's enough, let's move on."

### If Seeded from a GitHub Issue

Fetch the issue first (title, body, labels, comments). Extract what you can, then ask about anything left ambiguous.

### Gate

Present a **Discovery Summary**:

```
## Discovery Summary
**Task:** [1-2 sentence description]
**Classification:** [Type and why]
**Scope:** [What's in / what's out]
**Acceptance Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]
**Key Constraints:** [Anything surfaced during questioning]
**Assumptions:** [Anything you're assuming — call it out explicitly]
```

Wait for approval before proceeding.

## Phase 2: Research

Goal: Understand the codebase deeply enough to write precise agent briefs. This is YOUR context-building phase — agents won't have it, so you need to gather everything they'll need.

### For Features and Integrations
- Explore existing patterns relevant to this work
- Map all files and modules that will be affected
- Identify similar features and how they were built
- Trace dependency chains and integration points
- Look for existing tests that cover related functionality

### For Bug Fixes
- Understand the reproduction path from the code
- Trace the code path where the bug likely lives
- Identify what changed recently in the affected area (git log)
- Find existing tests that should have caught this (and didn't)

### For Refactors and Optimizations
- Map the current implementation thoroughly
- Identify all callers and consumers of the code being changed
- Find the test coverage for the affected code
- Understand why the code is structured the way it is before changing it

### Gate

Present a **Research Summary**:

```
## Research Summary
**Relevant Patterns:** [What exists today that informs our approach]
**Affected Areas:** [Files/modules that will change, with line references]
**Dependencies:** [What this work depends on or what depends on it]
**Test Coverage:** [What's tested today, what gaps exist]
**Risks:**
- [Risk 1 — impact and mitigation]
- [Risk 2 — impact and mitigation]
**Open Questions:** [Anything still unclear after research]
```

If there are open questions, ask them now — one at a time. Wait for approval before proceeding.

## Phase 3: Strategize

Goal: Present distinct approaches, weigh tradeoffs, and collaborate with the user on a decision.

### Develop Approaches

Based on Discovery and Research, design meaningfully different ways to solve the problem — not trivial variations, but genuinely different philosophies or tradeoffs.

For each approach:

```
### Approach [N]: [Name]
**Philosophy:** [Core idea in one sentence]
**How it works:** [Brief implementation description]
**Pros:**
- [Advantage 1]
- [Advantage 2]
**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]
**Complexity:** [Low / Medium / High]
**Risk:** [Low / Medium / High]
**Test strategy:** [How this approach would be tested]
```

### Make a Recommendation

State which approach you recommend and why. Be transparent about tradeoffs.

### Adapt to Task Complexity

For simpler tasks, two options may suffice. For complex tasks, present three. Use your judgment.

### Gate

The user picks an approach (or proposes a hybrid). Do not proceed until explicitly chosen.

## Phase 4: Plan

Goal: Break the chosen approach into discrete, ordered tasks — each one a dispatchable unit of work for an agent. This is the most critical orchestration phase.

### Build the Implementation Plan

Design each task as a self-contained agent brief. Each task must include everything an agent with zero prior context needs to execute correctly.

For each task:

```
### Task [N]: [Name]
**What:** [What changes to make]
**Where:** [Specific files and line ranges]
**How:** [The approach — be precise about patterns to follow, functions to call, structures to use]
**Context:** [Relevant codebase patterns, conventions, existing code the agent needs to know about]
**Tests:** [What tests to write or update — specific test file paths and test descriptions]
**Verify:** [How to confirm this task is correct — specific commands to run]
**Depends on:** [Which prior tasks, if any — "none" if independent]
```

### Dependency Graph

After listing all tasks, present the dependency structure:

```
## Execution Plan
**Parallel group 1:** Tasks [X, Y] (independent — will dispatch simultaneously)
**Sequential after group 1:** Task [Z] (depends on X)
**Parallel group 2:** Tasks [A, B] (independent, but depend on Z)
**Sequential after group 2:** Task [C] (depends on A and B)
```

### Test Strategy

Testing is not optional. The plan must include:
- **What kind of tests** — unit, integration, e2e, or a combination
- **When tests are written** — before implementation (TDD) when feasible, alongside at minimum
- **What's covered** — happy path, edge cases from Discovery, error handling, regression cases
- **How to run them** — the actual commands

### Gate

Present the full plan with the execution graph. Wait for the user to approve, reorder, or adjust scope.

## Phase 5: Implement

Goal: Dispatch agents to execute the plan. You stay in the orchestrator role — you do not write implementation code yourself.

### Dispatching Agents

For each task (or parallel group of tasks), dispatch using the Agent tool. Structure each agent's prompt using this template:

```
## Task: [Name from the plan]

### Objective
[1-2 sentences: what this agent must accomplish]

### Codebase Context
- Project uses [language/framework] with [relevant conventions]
- Related file: `path/to/file.ext` — [what it does and how it relates to this task]
- Existing pattern to follow: [describe the pattern, include function signatures or code snippets]
- Test framework: [what's used, how to run tests]

### What to Change
1. [Specific change 1 — file, location, what to add/modify]
2. [Specific change 2]

### Boundaries
- Files you SHOULD touch: [list]
- Files you must NOT touch: [list]

### Tests
Write tests first when feasible. Specifically:
- [Test 1: description, expected behavior]
- [Test 2: description, expected behavior]
- Test file location: `path/to/test/file`

### Verification
Run these commands when done and confirm they pass:
- `[test command]`
- `[lint command, if applicable]`
```

The goal is that the agent can execute without asking questions — every decision is already made.

### Dispatch Rules

- **Independent tasks:** Dispatch in parallel using multiple Agent tool calls in a single message.
- **Dependent tasks:** Wait for the dependency to complete and verify success before dispatching the next task.
- **Agent failures:** If an agent reports a problem, diagnose it yourself (read the code, understand the issue) and either re-dispatch with a corrected brief or adjust the plan. Do NOT blindly retry.

### Between Dispatches

After each agent (or parallel group) completes:
1. Read and summarize the agent's results for the user
2. Verify the work — check that tests pass, code looks right
3. Flag anything that deviated from the plan
4. If the plan needs adjustment, stop and propose changes before continuing

### If Something Goes Wrong

- **Agent couldn't complete the task:** Read its output, understand why, and decide whether to re-dispatch with better instructions, split the task, or adjust the plan.
- **Tests fail after an agent completes:** Fix it before moving on. If the failure reveals a deeper issue, discuss with the user.
- **Tasks conflict with each other:** If parallel agents made conflicting changes, resolve the conflict yourself or re-dispatch one of the tasks with updated context.

## Phase 6: Review

Goal: Dispatch a dedicated review agent to validate all changes holistically. This is a fresh set of eyes — the reviewer has no context from the implementation and evaluates the work on its own merits.

### Dispatch the Review Agent

Send a single Agent with a prompt structured like this:

```
## Code Review

### What Was Built
[Paste the Discovery Summary — task description, classification, scope]

### Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

### Changed Files
- `path/to/file1.ext` — [what changed and why]
- `path/to/file2.ext` — [what changed and why]

### Your Job
1. Read every changed file. Evaluate code quality, consistency, and correctness.
2. Check each acceptance criterion against the actual implementation. Mark pass/fail.
3. Run the full test suite: `[command]`. Report results.
4. Look for: leftover TODOs, debug code, commented-out blocks, unintended side effects.
5. Check for security issues, performance concerns, and unhandled edge cases.
6. Verify new code is consistent with existing codebase patterns.
7. Produce a Validation Report using the format below.

### Validation Report Format
[Paste the report template from Phase 6]
```

### Handle the Review

When the review agent returns:
1. Present the Validation Report to the user
2. If the reviewer flagged issues, discuss with the user and dispatch fix-up agents as needed
3. If fixes were made, re-dispatch the review agent on the affected areas

### Validation Report Format

The review agent should produce:

```
## Validation Report
**Tests:** [All passing / failures noted with details]
**Acceptance Criteria:**
- [x] [Criterion 1] — [How verified]
- [x] [Criterion 2] — [How verified]
**Code Quality:**
- [Observation 1]
- [Observation 2]
**Issues Found:**
- [Issue 1 — severity and recommendation]
- [Issue 2 — severity and recommendation]
**Security/Performance Notes:** [Any concerns]
**Verdict:** [Ready to ship / Needs fixes]
```

The user must confirm the work meets their definition of done. If anything fails, loop back to fix it.

## Phase 7: Deliver

Goal: Clean up, commit, and prepare the work for review or merge.

### Clean Up
- Remove any debug code, temporary files, or scratch work
- Ensure all new files are properly organized
- Check that documentation is updated if changes affect public APIs, configuration, or user-facing behavior
- Verify the branch is up to date with the base branch

### Commit
- Group changes into logical Conventional Commits
- Each commit should be a coherent unit of work
- Use the project's commit conventions

### Create a PR (if applicable)
- Draft a PR title and description summarizing the work
- Reference the original issue if one was provided
- Include acceptance criteria and how they were verified
- Note any follow-up work identified during implementation

### Gate

Present a final summary:

```
## Delivery Summary
**What was built:** [1-3 sentence summary]
**Commits:** [List of commits created]
**PR:** [Link if created]
**Acceptance criteria:** [All met / any caveats]
**Follow-up items:** [Anything identified but out of scope]
**Documentation updated:** [Yes/No — what was updated]
```

## Adapting Depth

Not every task needs the same treatment. Use your judgment:

- **Simple bug fix:** Discovery can be brief, Research focuses on root cause, Strategize may only need 2 options, Plan may be a single task. But Review is still thorough — regressions matter.
- **Large feature:** Every phase gets full depth. Discovery asks many questions. Research is comprehensive. Multiple approaches. Detailed multi-task plan with parallel groups.
- **Refactor:** Research is heavy (must understand everything before changing it). Test coverage is the safety net — verify it exists before dispatching agents.
- **Quick integration:** Focus on interface design in Strategize, error handling in Plan, and contract testing in agent briefs.

The seven phases always apply, but their weight shifts based on what you're building.

## Examples

### Example: Feature request with parallel dispatch

User says: "/develop add a webhook notification system to the API"

1. **Discover:** Classify as Feature. Probe for unknowns — what events trigger webhooks? What payload format? Retry policy? Produce Discovery Summary with acceptance criteria.
2. **Research:** Find existing event system, identify where hooks should fire, map the database schema, check test patterns. Present Research Summary.
3. **Strategize:** Present approaches — polling vs push, sync vs async dispatch, in-process vs queue-backed. Recommend async with a queue. User approves.
4. **Plan:** Break into tasks:
   - Task 1: Webhook registration model and migrations (depends on: none)
   - Task 2: Webhook delivery service with retry logic (depends on: none)
   - Task 3: Wire events to delivery service (depends on: 1 and 2)
   - Task 4: Admin API endpoints for managing webhooks (depends on: 1)
   - Execution plan: Tasks 1 and 2 in parallel, then 3 and 4 in parallel after their dependencies complete.
5. **Implement:** Dispatch Tasks 1 and 2 simultaneously. Both complete. Dispatch Tasks 3 and 4 simultaneously. Summarize results after each group.
6. **Review:** Dispatch review agent with the Discovery Summary, acceptance criteria, and all changed files. Reviewer returns a Validation Report — one issue found (missing rate limit on delivery). Dispatch a fix-up agent. Re-review passes.
7. **Deliver:** Group into commits, create PR referencing the original request.

### Example: Bug fix with single agent

User says: "/develop users are getting 500 errors when uploading avatars over 2MB"

1. **Discover:** Classify as Bug fix. Quick — user provides the error, reproduction is clear.
2. **Research:** Trace the upload path, find the size validation, check the error handler. Discover the middleware rejects the file but the error isn't caught by the controller.
3. **Strategize:** Two options — catch at controller level vs increase middleware limit with proper validation. Recommend controller-level catch.
4. **Plan:** Single task — add error handling in the upload controller, write a regression test.
5. **Implement:** Dispatch one agent with the brief. Agent completes.
6. **Review:** Dispatch review agent. Clean pass.
7. **Deliver:** One commit, done.

## Troubleshooting

**User wants to skip a phase**
Phases build on each other. If the user insists, acknowledge the tradeoff and proceed, but note what was skipped and why it matters.

**Task is too large for one session**
Break the Plan into milestones. Complete and commit one milestone at a time. When resuming, re-read the Discovery Summary and Plan to re-establish context.

**Acceptance criteria change mid-implementation**
Return to the Discovery Summary, update the criteria, and assess impact on the current plan. Adjust remaining tasks as needed.

**Agent keeps failing on a task**
The brief is probably incomplete or the task is too large. Split it into smaller pieces or add more context to the brief. If you've re-dispatched twice without success, implement that piece yourself and move on.

**Tests fail during Review**
Do not proceed to Deliver. Diagnose failures, dispatch fix-up agents, and re-run the review.

**User says "just do it" or "skip the questions"**
Respect their preference but note: "I'll proceed with my best judgment on the unknowns. If I hit something ambiguous, I'll ask then." Compress Discovery and move faster through the phases.
