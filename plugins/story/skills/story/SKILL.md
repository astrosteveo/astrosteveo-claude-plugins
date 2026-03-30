---
name: story
description: >
  Structured, phased feature development workflow inspired by Agile methodology.
  Guides implementation through six phases: Discovery, Research, Design,
  Implementation, Verification, and Wrap-up — with user review gates between
  each phase. Use when the user says "start a story", "build a feature",
  "implement this feature", "feature dev cycle", "let's build", or runs /story.
  Also triggers when the user says "implement issue #123" or provides a GitHub
  issue to implement. Do NOT trigger for quick bug fixes, one-line changes,
  or simple refactors that don't need a formal workflow.
argument-hint: "[feature description or issue number]"
metadata:
  author: AstroSteveo
  version: 1.0.0
  category: workflow
  tags: [agile, feature-development, workflow, story]
---

# Story

Structured, phased feature development workflow. Each phase produces a concrete artifact; the user reviews and approves before moving on.

## Routing

When invoked, check for arguments:
- `/story [description]` — Start a new story with the given feature description
- `/story #123` or `/story [URL]` — Start a story seeded from a GitHub issue
- `/story` with no arguments — Ask the user what they want to build
- If the user mentions resuming or picking up work — Identify the current phase and re-enter there

## Phase 1: Discovery

Goal: Understand the feature, define scope, and establish acceptance criteria.

1. If a GitHub issue was provided, fetch it first:
   - Read the issue title, body, labels, and comments
   - Extract requirements, constraints, and any linked PRs or discussions
   - Present a summary to the user

2. If starting from a description (or after reading the issue), work through these questions with the user:
   - **What:** What is the feature? What problem does it solve?
   - **Why:** What's the motivation? Who benefits?
   - **Scope:** What's in scope and explicitly out of scope?
   - **Acceptance criteria:** How do we know it's done? Define 3-5 concrete, testable criteria.

3. Present a **Story Card** for the user to review:

   ```
   ## Story Card
   **Title:** [Feature name]
   **Description:** [1-3 sentence summary]
   **Motivation:** [Why this matters]
   **Scope:** [In scope] / [Out of scope]
   **Acceptance Criteria:**
   - [ ] [Criterion 1]
   - [ ] [Criterion 2]
   - [ ] [Criterion 3]
   ```

4. Wait for the user to approve or refine the Story Card before proceeding.

## Phase 2: Research & Analysis

Goal: Understand the codebase context, identify affected areas, and surface risks.

1. **Explore the codebase** to understand:
   - Existing patterns relevant to this feature
   - Files and modules that will be touched
   - How similar features were implemented (if any)
   - Dependencies and integration points

2. **Identify risks and open questions:**
   - Technical risks (complexity, fragile areas, performance concerns)
   - Dependencies on external systems or other teams
   - Anything unclear from the Story Card that needs resolution

3. Present a **Research Summary**:

   ```
   ## Research Summary
   **Relevant Patterns:** [What exists today that's similar]
   **Affected Areas:** [Files/modules that will change]
   **Dependencies:** [What this feature depends on]
   **Risks:**
   - [Risk 1 and mitigation]
   - [Risk 2 and mitigation]
   **Open Questions:** [Anything needing user input]
   ```

4. Wait for the user to review, answer open questions, and approve before proceeding.

## Phase 3: Design & Planning

Goal: Produce a concrete implementation plan with clear tasks.

1. Based on Discovery and Research, draft an **Implementation Plan**:
   - Break the work into discrete, ordered tasks
   - Each task should be small enough to verify independently
   - Identify which tasks depend on others
   - Note any decision points where the approach could vary

2. For each task, specify:
   - **What:** What changes to make
   - **Where:** Which files/modules
   - **How:** The approach (new code, refactor, extend existing pattern)
   - **Verify:** How to confirm this task is correct before moving on

3. Present the plan:

   ```
   ## Implementation Plan

   ### Task 1: [Name]
   **What:** [Description]
   **Where:** [Files]
   **How:** [Approach]
   **Verify:** [How to check]

   ### Task 2: [Name]
   ...

   **Task Order:** 1 -> 2 -> 3 (with dependencies noted)
   **Estimated Scope:** [Number of files, rough size of changes]
   ```

4. Wait for the user to approve the plan, reorder tasks, or adjust scope.

## Phase 4: Implementation

Goal: Execute the plan task-by-task with verification gates.

1. Work through each task from the approved plan in order.

2. For each task:
   - Announce which task you're starting
   - Implement the changes
   - Run the verification step defined in the plan
   - Present a brief summary of what was done

3. **Between tasks**, pause and check in with the user:
   - Show what was completed
   - Flag anything that deviated from the plan
   - Confirm the user is ready to proceed to the next task

4. If a task reveals that the plan needs adjustment:
   - Stop and explain what changed
   - Propose an updated approach
   - Wait for approval before continuing

5. Do NOT skip verification steps. If a verification fails, fix the issue before moving on.

## Phase 5: Verification

Goal: Validate the complete feature against acceptance criteria.

1. **Run the test suite** — execute existing tests to check for regressions:
   - Run the project's test command(s)
   - If any tests fail, fix them before proceeding

2. **Walk through acceptance criteria** from the Story Card one by one:
   - For each criterion, verify it's met (run tests, read code, or demonstrate)
   - Mark each as passed or failed
   - If any fail, loop back to fix

3. **Review the full diff** — read through all changes holistically:
   - Check for consistency with existing codebase patterns
   - Look for anything missed, leftover TODOs, or debug code
   - Verify no unintended side effects

4. Present a **Verification Report**:

   ```
   ## Verification Report
   **Tests:** [Pass/Fail — details]
   **Acceptance Criteria:**
   - [x] [Criterion 1] — [How verified]
   - [x] [Criterion 2] — [How verified]
   - [ ] [Criterion 3] — [What's missing]
   **Code Review Notes:** [Any concerns or observations]
   ```

5. Wait for the user to review and approve before wrapping up.

## Phase 6: Wrap-up

Goal: Commit the work and prepare it for review.

1. **Create commits** — group changes into logical Conventional Commits:
   - Use the project's commit conventions
   - Each commit should be a coherent unit of work

2. **Offer to create a PR** — if the user wants one:
   - Draft a PR title and description summarizing the feature
   - Reference the original issue if one was provided
   - Include the acceptance criteria and how they were verified

3. **Present a summary**:

   ```
   ## Story Complete
   **Feature:** [Name]
   **Commits:** [List of commits created]
   **PR:** [Link if created]
   **What was built:** [1-3 sentence summary]
   **Acceptance criteria:** [All met / any caveats]
   ```

## Troubleshooting

**User wants to skip a phase**
Phases build on each other — skipping Research may lead to missed risks, skipping Design
may lead to unstructured implementation. If the user insists, acknowledge the tradeoff
and proceed, but note what was skipped.

**Feature is too large for one session**
Break the Implementation Plan into milestones. Complete and commit one milestone at a time.
When resuming, re-read the Story Card and Plan to re-establish context.

**Acceptance criteria change mid-implementation**
Return to the Story Card, update the criteria, and assess impact on the current plan.
Adjust remaining tasks as needed.

**Tests fail during Verification**
Do not proceed to Wrap-up. Diagnose failures, fix them, and re-run. If the fix changes
the implementation significantly, re-verify all acceptance criteria.
