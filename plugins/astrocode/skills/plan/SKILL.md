---
name: plan
user-invocable: false
description: >
  Feature planning and design — scope requirements, explore the codebase, identify
  architectural approach and tradeoffs, break down into tasks. Use when the user says
  "plan", "design this", "how should we build", "scope this out", "break this down",
  "what's the approach", or "plan the implementation". Also use when the user runs /plan.
---

# Plan

Scope, design, and break down a feature or change before implementation begins. The goal is alignment — make sure the approach is solid before writing code.

## Process

### Step 1: Gather Requirements

Understand what needs to be built:

1. **What:** What is the feature, change, or fix? Get a concrete description from the user.
2. **Why:** What problem does it solve? Who benefits? This shapes tradeoff decisions later.
3. **Constraints:** Deadlines, backward compatibility requirements, performance targets, dependencies on other work, or anything that limits the solution space.

If the user's request is vague, ask clarifying questions before proceeding. A plan built on assumptions wastes time.

### Step 2: Explore the Codebase

Read relevant code to understand the current state:

1. Read `CLAUDE.md` (if present) for project conventions, architecture, and tech stack.
2. Read `.claude/PROGRESS.md` (if present) for current work streams and context.
3. Identify the files, modules, and patterns that the change will touch or interact with.
4. Note existing patterns — the plan should work with them, not against them.
5. Check for related prior work (git log, existing implementations of similar features).

Use parallel agents to explore multiple areas simultaneously when the feature spans several parts of the codebase.

### Step 3: Design the Approach

Based on requirements and codebase understanding, design the solution:

1. **Architectural approach:** How does this fit into the existing architecture? What patterns should it follow?
2. **Key decisions:** Identify the 2-3 most important design decisions and the tradeoffs for each option.
3. **Risks:** What could go wrong? What assumptions are we making? Are there unknowns that need investigation first?
4. **Scope boundaries:** What's in scope and what's explicitly out of scope? This prevents creep during implementation.

### Step 4: Break Down into Tasks

Create an ordered list of implementation steps:

1. Each task should be a single logical unit of work (one commit's worth).
2. Order tasks so that each builds on the previous — avoid tasks that depend on unfinished work later in the list.
3. Identify which tasks are independent and could be parallelized.
4. Note any tasks that need user input or decisions before proceeding.
5. Flag tasks that carry risk (migrations, breaking changes, new dependencies) so the user knows where to pay extra attention.

### Step 5: Present the Plan

Output a structured plan for user review:

```
## Plan: <feature/change name>

### Context
Brief summary of what and why.

### Approach
Description of the architectural approach and key decisions.

### Key Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| ... | ... | ... |

### Tasks
1. [ ] Task description — files affected, what changes
2. [ ] Task description — files affected, what changes
...

### Risks / Open Questions
- Risk or question that needs resolution

### Out of Scope
- Things explicitly excluded from this work
```

### Step 6: Iterate

After presenting the plan, ask the user:

> "Does this approach look right? Anything you'd change, add, or cut?"

Incorporate feedback and update the plan. The plan is not final until the user confirms it. Once confirmed, the user can begin implementation — either manually or by asking you to execute the tasks.

## Important

- **Don't write code during planning.** The output is a plan, not an implementation. Code snippets are fine for illustrating an approach, but don't build the feature.
- **Be opinionated but flexible.** Recommend the approach you think is best, but present alternatives for key decisions. The user makes the call.
- **Keep it proportional.** A bug fix needs 3 lines of plan, not a design document. A new subsystem needs a thorough breakdown. Match the depth to the complexity.
- **Surface unknowns early.** If something needs investigation or a spike before you can plan it properly, say so. A plan with known gaps is better than a confident plan built on guesses.
- **Respect existing architecture.** Don't propose a rewrite when an extension will do. Work with the patterns that are already there unless there's a strong reason to change them.
