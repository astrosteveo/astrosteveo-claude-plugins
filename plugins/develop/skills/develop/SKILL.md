---
name: develop
description: >
  End-to-end development workflow for implementing features, fixing bugs,
  refactoring code, and any substantial code change touching multiple files
  or systems. Guides work through adaptive phases with user review gates
  between each phase. Use when the user says "build this feature", "implement
  this", "add [feature]", "fix this bug", "refactor this", "I need to build",
  "help me implement", "plan and implement", "walk me through building this",
  "let's develop this", "let's think through this", or describes a substantial
  code change and wants a structured approach. Also triggers when the user
  provides a bug report, feature request, or issue number and wants it
  implemented. Do NOT use for one-line fixes, simple renames, quick
  formatting, questions about code, or tasks that only touch a single file.
argument-hint: "[feature description, bug report, or issue number]"
metadata:
  author: AstroSteveo
  version: 2.0.0
  category: workflow
  tags: [development, workflow, tdd, feature, bugfix, refactor]
---

# Develop

End-to-end development workflow that adapts to the task at hand. Every phase has a user gate — nothing moves forward without explicit approval.

## Critical Rule: One Question at a Time

Throughout this entire workflow, when you need to ask the user a clarifying question, ask exactly ONE question per message. Do not bundle multiple questions. The number of questions you ask should scale with the complexity of the task — there is no right or wrong count. But each question gets its own message so the user can focus and give a complete answer. If the user says "use your best judgment" on a question, accept that and move on.

## Routing

When invoked, check for arguments:
- `/develop [description]` — Start with the given description
- `/develop #123` or `/develop [URL]` — Start seeded from a GitHub issue
- `/develop` with no arguments — Ask the user what they want to work on
- If the user mentions resuming or picking up work — Identify the current phase and re-enter there

## Phase 1: Discover

Goal: Deeply understand the task, classify it, and surface every unknown and edge case you can think of before any code is explored.

### Classify the Task

After hearing the user's description, infer the nature of the work. This is not a rigid taxonomy — use your judgment to characterize what kind of work this is. Common patterns include:

- **Feature** — New capability that doesn't exist yet. Needs the most thorough treatment: full research, multiple approaches, comprehensive test strategy.
- **Bug fix** — Something is broken. Focus shifts to reproduction, root cause analysis, and regression testing. May be simpler or deeply complex depending on the bug.
- **Refactor** — Code works but needs restructuring. Key concern is preserving existing behavior while improving internals. Tests are the safety net.
- **Integration** — Connecting systems or services. Heavy emphasis on interface design, error handling, and dependency mapping.
- **Optimization** — Code works but needs to be faster, smaller, or more efficient. Requires measurement before and after.

State your classification to the user and explain how it shapes the approach you'll take. If the task blends categories, say so.

### Probe for Unknowns

This is the most important part of this phase. Your job is to think about what the user has NOT told you — the edge cases, the implicit assumptions, the things that will bite you during implementation if left unaddressed.

Ask about:
- Constraints the user hasn't mentioned (performance, compatibility, accessibility, security)
- Edge cases in the inputs or behavior
- How this interacts with existing functionality
- What "done" looks like — concrete acceptance criteria
- Anything ambiguous in the description

Remember: one question at a time. Keep asking until you are confident you understand the full picture. The user can always say "that's enough, let's move on."

### If Seeded from a GitHub Issue

Fetch the issue first (title, body, labels, comments). Extract what you can, then ask about anything the issue leaves ambiguous.

### Gate

Present a **Discovery Summary** back to the user:

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

Goal: Understand the codebase deeply enough to propose informed approaches. Adapt depth to the task classification.

### For Features and Integrations
- Explore existing patterns relevant to this work
- Map all files and modules that will be affected
- Identify similar features and how they were built
- Trace dependency chains and integration points
- Look for existing tests that cover related functionality

### For Bug Fixes
- Attempt to understand the reproduction path from the code
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

Goal: Present three distinct approaches, weigh their tradeoffs, and collaborate with the user on a final decision.

### Develop Three Approaches

Based on Discovery and Research, design three meaningfully different ways to solve the problem. These should not be trivial variations — each should represent a genuinely different philosophy or tradeoff.

For each approach, present:

```
### Approach [N]: [Name]
**Philosophy:** [The core idea in one sentence]
**How it works:** [Brief description of the implementation]
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

After presenting all three, state which approach you recommend and why. Be transparent about the tradeoffs. This is a collaboration — the user may see angles you don't.

### Adapt to Task Complexity

For simpler tasks (straightforward bug fixes, small refactors), three full approaches may be overkill. In those cases, you may present fewer — but always present at least two distinct options so the user has a real choice. Use your judgment on when three is warranted vs. when two suffices.

### Gate

The user picks an approach (or proposes a hybrid). Do not proceed until the approach is explicitly chosen.

## Phase 4: Plan

Goal: Break the chosen approach into discrete, ordered tasks with a test strategy baked into every step.

### Build the Implementation Plan

For each task:

```
### Task [N]: [Name]
**What:** [What changes to make]
**Where:** [Which files/modules]
**How:** [The approach — new code, refactor, extend existing]
**Tests:** [What tests to write or update for this task]
**Verify:** [How to confirm this task is correct before moving on]
**Depends on:** [Which prior tasks, if any]
```

### Test Strategy

Testing is not optional and not an afterthought. The plan must include:
- **What kind of tests** — unit, integration, e2e, or a combination
- **When tests are written** — before implementation (TDD) when feasible, alongside at minimum
- **What's covered** — happy path, edge cases surfaced in Discovery, error handling, regression cases for bug fixes
- **How to run them** — the actual commands

### Gate

Present the full plan. Wait for the user to approve, reorder tasks, or adjust scope.

## Phase 5: Implement

Goal: Execute the plan task-by-task with TDD discipline and user check-ins.

### For Each Task

1. **Announce** which task you're starting
2. **Write tests first** when feasible — tests that define the expected behavior before writing the implementation
3. **Implement** the changes
4. **Run the tests** — both new tests and existing tests to catch regressions
5. **Summarize** what was done and show test results

### Between Tasks

Check in with the user:
- Show what was completed and test results
- Flag anything that deviated from the plan
- If the plan needs adjustment based on what you discovered during implementation, stop and propose changes before continuing

### If Tests Fail

Fix the issue before moving to the next task. Do not accumulate failures. If a failure reveals a deeper problem, stop and discuss with the user rather than silently working around it.

## Phase 6: Validate

Goal: The user confirms everything works. This is not your verification — this is theirs.

### Walk Through Acceptance Criteria

Go through each criterion from the Discovery Summary one by one:
- Explain how it was met
- Point to the specific code and tests that satisfy it
- Let the user verify — they may want to test manually

### Run the Full Test Suite

Execute the project's complete test suite, not just the new tests. Report results clearly.

### Review the Full Diff

Read through all changes holistically:
- Check for consistency with existing codebase patterns
- Look for leftover TODOs, debug code, or commented-out blocks
- Verify no unintended side effects

### Gate

Present a **Validation Report**:

```
## Validation Report
**Tests:** [All passing / failures noted]
**Acceptance Criteria:**
- [x] [Criterion 1] — [How verified]
- [x] [Criterion 2] — [How verified]
**Code Review Notes:** [Any concerns or observations]
```

The user must confirm the work meets their definition of done. If anything fails, loop back to fix it.

## Phase 7: Deliver

Goal: Clean up, commit, and prepare the work for review or merge.

### Clean Up
- Remove any debug code, temporary files, or scratch work
- Ensure all new files are properly organized
- Check that documentation is updated if the changes affect public APIs, configuration, or user-facing behavior
- Verify the branch is up to date with the base branch (rebase or merge as appropriate)

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

- **Simple bug fix:** Discovery can be brief, Research focuses on root cause, Strategize may only need 2 options, Plan may be a single task. But Validate is still thorough — regressions matter.
- **Large feature:** Every phase gets full depth. Discovery asks many questions. Research is comprehensive. Three full approaches. Detailed multi-task plan.
- **Refactor:** Research is heavy (must understand everything before changing it). Strategize focuses on how to restructure safely. Test coverage is the safety net — verify it exists before touching code.
- **Quick integration:** Focus on interface design in Strategize, error handling in Plan, and contract testing in Implement.

The seven phases always apply, but their weight shifts based on what you're building.

## Troubleshooting

**User wants to skip a phase**
Phases build on each other. If the user insists, acknowledge the tradeoff and proceed, but note what was skipped and why it matters.

**Task is too large for one session**
Break the Plan into milestones. Complete and commit one milestone at a time. When resuming, re-read the Discovery Summary and Plan to re-establish context.

**Acceptance criteria change mid-implementation**
Return to the Discovery Summary, update the criteria, and assess impact on the current plan. Adjust remaining tasks as needed.

**Tests fail during Validation**
Do not proceed to Deliver. Diagnose failures, fix them, and re-run. If the fix changes the implementation significantly, re-verify all acceptance criteria.

**User says "just do it" or "skip the questions"**
Respect their preference but note: "I'll proceed with my best judgment on the unknowns. If I hit something ambiguous during implementation, I'll ask then." Then compress Discovery and move faster through the phases.
