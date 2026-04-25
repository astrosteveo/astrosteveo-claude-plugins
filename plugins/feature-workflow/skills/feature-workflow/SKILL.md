---
name: feature-workflow
description: Implements new features through a structured workflow.
when_to_use: Use when the user asks to create, implement, design, build, add, or scope a feature, when resuming work ("where were we," "what's next," "what should I work on"), or when brainstorming about future work.
argument-hint: "[optional feature description]"
---

# Feature workflow

Two jobs:

1. Run a structured workflow when the user asks to build something, so orientation happens before code.
2. Maintain `.claude/PROJECT.md` as the single source of truth for what is in flight, planned, and deferred.

## Why

Real engineers orient before writing code: read the ask, read the code, plan, then build. AI sessions tend to skip that. Ideas surfaced in conversation ("we should also do X") evaporate at session end without a place to land them. This skill provides the path and the file that keep both behaviors durable.

This skill sequences the steps. Code is always available to write.

## The state file

`.claude/PROJECT.md` — three sections, current state only:

```markdown
# Project state

## In progress
- **<title>** — one or two sentences on what this is and where it stands.

## Planned
- **<title>** — one or two sentences on what this is.

## Deferred
- **<title>** — one or two sentences (optional: why deferred).
```

Rules:

- When work ships, remove the item. Git history is the record of completed work.
- Keep entries to one or two sentences. Detail lives in conversation during the work.
- Update the file the moment state changes — when work starts, when an idea is parked, when work ships.
- Create the file the first time something concrete needs to be tracked.
- A section with no items can be omitted or marked as `_(empty)_`.

## The workflow

Always start with Step 0. The rest scales to the ask — small work gets a small version of each step, real features get the full thing.

### 0. Read state

Read `.claude/PROJECT.md` if it exists. Mention what is there only when it is relevant to the current ask.

### 1. Understand the ask

If `$ARGUMENTS` is non-empty, use it as the initial feature description and proceed from there.

Ask focused clarifying questions when the request is genuinely ambiguous and the answer cannot be found in the codebase. Good clarifications target scope edges, sync vs async, persistent vs in-memory, interaction with existing features, and what "done" means. Resolve everything else by reading the code first.

For small, clear asks (one-line fix, rename, obvious tweak), do the work directly. The workflow applies to real features.

### 2. Research

Read the files that would change, plus their callers and relevant tests. Surface anything that shapes the plan: existing patterns to match, gotchas, places that must change in lockstep.

### 3. Plan

Produce a real plan, proportional to the ask:

- What changes, and where
- The order changes land in
- Anything tricky and how it will be handled
- Assumptions being made — so the user can correct them before code is written

Match plan length to the work. The plan lives in the conversation.

### 4. Record

Add the new work to **In progress** in `.claude/PROJECT.md` before writing code. If the conversation surfaced follow-ups or parking-lot items, drop them in **Planned** or **Deferred** in the same edit. Create the file if it does not exist yet.

### 5. Implement

Write the code per the plan. If a different approach turns out to be right mid-flight, say so and adjust the plan before continuing.

### 6. Review

Review runs in a fresh context, separate from the context that wrote the code. A separate context catches blind spots and resists rationalizing the choices it just made.

Spawn a subagent via the `Agent` tool (`general-purpose`). A fresh context applying a review skill is the right shape: independent reviewer, focused tooling.

Pass the subagent:

- The diff or specific changed file paths to review
- The plan it was supposed to follow
- The acceptance criteria
- An instruction to use the right review skill for the change

**Pick the review skill based on what is being reviewed:**

- **`code-quality`** — the default. Comprehensive review for bugs, edge cases, error paths, mismatches with existing project patterns, dead code, complexity. Non-breaking recommendations only. Reads project conventions first so flagged items respect intentional decisions. The "colleague looks at your diff" tool.
- **`code-sniffer`** — narrow AI-slop detector. Conservative by design — when it flags, the finding is almost certainly real. Especially worth running here because the diff is AI-generated and slop is the failure mode it is tuned for. Low overhead; runs as a complementary pass alongside `code-quality` for substantial slices.

For most features: instruct the subagent to run `code-quality` scoped to the changed files. For substantial slices, also run `code-sniffer` — it catches things `code-quality` misses, because they are tuned for different failure modes.

Relay findings to the user verbatim. Some findings will be real; some may be false positives or matters of taste. The user weighs which to act on.

### 7. Fix

Address what the user agrees is real. Set false positives aside.

### 8. Verify

Confirm the change actually works. Method depends on the change:

- Tests exist → run them
- UI → exercise it in a browser, check golden path and obvious edges
- CLI or script → run it on realistic input
- Library code without UI → write or run a test that proves it

If verification is not possible (no environment, no fixtures, no way to exercise it), say so explicitly.

### 9. Close out

Remove the item from **In progress** in `.claude/PROJECT.md`. If anything new surfaced during the work that should be tracked, add it to the appropriate section in the same edit.

## Brainstorming mode

When the user opens with "let's think about X" or "what should we build" rather than "implement X":

- Read `.claude/PROJECT.md` for context on what is already in flight or planned
- Talk it through. Begin writing code once something concrete emerges.
- When something concrete emerges, add it to **Planned** (or **Deferred** if it is interesting-but-not-now)
- **Deferred** is a fine resting place for ideas that are not yet ripe. Let them sit there until they sharpen.

## Resume questions

For "where were we," "what's next," "what should I work on": read `.claude/PROJECT.md` and summarize the state in a few sentences. When **In progress** is non-empty, that is the answer. Otherwise the top of **Planned**. When both are empty, ask the user.
