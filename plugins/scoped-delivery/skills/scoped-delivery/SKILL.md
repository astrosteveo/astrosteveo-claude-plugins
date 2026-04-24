---
description: Structured four-phase delivery workflow (orient, clarify, implement, review) with fresh subagent contexts for the implementation and review phases. Invoke only when the user explicitly types /scoped-delivery — do not auto-trigger; the ceremony is only worth it when the user has consciously opted in.
argument-hint: "<task description>"
---

# Scoped Delivery

Ship one logical story with deliberate phase separation. `$ARGUMENTS` is the user's task description — the story they want delivered.

Four phases, each producing a named artifact that becomes the input to the next. Two phases run in fresh subagent contexts (Implement and Review) — that separation is load-bearing, not ceremony. The reasoning is spelled out in the "Why this shape" section at the end; read it if you're tempted to skip steps.

## When to drop the workflow

The user opted in by typing `/scoped-delivery`, but they may have reached for it reflexively. If the task described in `$ARGUMENTS` is:

- A single-file edit, rename, or typo fix
- Already specified with complete acceptance criteria and no unknowns
- A hotfix where speed outweighs rigor

Say so plainly, recommend doing it directly, and stop. Performing the ceremony on something that doesn't need it wastes the user's time and teaches them to distrust the skill.

If the task is **several bundled stories** ("add auth, refactor billing, and update docs"), ask the user to pick one. This skill delivers *one* logical story — that's where the name comes from.

## Phase 1 — Orient

**Goal:** build enough context to ask the right questions. Not to design the solution.

Read `$ARGUMENTS` carefully. For any task touching code you don't already have context on, spawn an `Explore` subagent to locate relevant files, surrounding patterns, and constraints (tests, types, existing conventions). For narrow tasks, direct `Grep`/`Read` is fine.

Do not start sketching implementation yet. The point of Orient is to surface *what you don't know*, not to resolve it. Resolved unknowns belong in Clarify.

**Exit artifact — Orientation Brief** (keep in conversation; do not write to disk):

- Restated story in your own words (one paragraph — this is where misunderstandings surface)
- Relevant files (path + one-line role)
- Existing patterns to match, or reasons to diverge
- Open questions and unknowns (the list Clarify will resolve)

## Phase 2 — Clarify

**Goal:** resolve every open question and pin down the story's boundaries before code is written.

Present the Orientation Brief to the user. Ask the open questions as a numbered list so they can answer inline. When answers come back, restate them — restatement catches misunderstandings cheaply, before they're baked into code.

Clarify is where this skill earns its keep. Skipping it collapses the workflow into "main agent with extra steps." Do not launch Phase 3 until the user has explicitly confirmed the Delivery Spec. A nodded "sure, go" is fine; silence is not consent.

**Exit artifact — Delivery Spec:**

- Orientation Brief (unchanged)
- Resolved decisions — each open question, the user's answer, any rationale they gave
- Out-of-scope list — what we explicitly are NOT doing. This is as important as the in-scope list; without it, the implementer invents features that weren't asked for.
- Acceptance criteria — how we will know the story is delivered

## Phase 3 — Implement (subagent)

**Goal:** produce the change without the main agent losing its planning context.

Spawn a `general-purpose` Agent. Pass the entire Delivery Spec verbatim in the prompt. Instruct the subagent to:

- Implement exactly what the Delivery Spec describes
- Flag ambiguity rather than guess — if something is unclear, return and ask, don't invent
- Return a summary of changes and any deviations from the spec

Why a fresh subagent: the main agent has been collaborating with the user through Orient and Clarify. It has opinions shaped by conversational context that isn't in the Spec. Handing off to a fresh subagent gives you a focused executor that works from the written contract, not from remembered nuance. If the Spec is lossy, that's a signal to strengthen the Spec — not to patch around it from memory.

**Exit artifact — Implementation Report:**

- Files changed (path + what changed + why)
- Deviations from the spec, with reasoning
- TODOs or follow-ups left behind

If the subagent reports significant deviations or unresolved ambiguity, loop back to Clarify with the user. Do not launch Review on an unstable implementation — Review findings on a shaky base are noise.

## Phase 4 — Review (subagent)

**Goal:** independent eyes that weren't present during Implement.

Spawn a fresh `general-purpose` Agent. Pass it the Delivery Spec, the Implementation Report, and the diff. Ask for findings triaged into:

- **must-fix** — bugs, broken acceptance criteria, security issues
- **should-fix** — quality concerns worth addressing before shipping
- **nit** — preferences and minor cleanups

Also ask for a confidence read: does the change tell the story the Spec scoped, and nothing more?

Why a second fresh subagent: the implementer just wrote this code. It has a stake in the choices it made. An agent that didn't write it reads with less anchoring. This is the same reason an author is a weak reviewer of their own work — and the fix is the same: give the review to someone who wasn't in the room when the decision was made.

**Exit artifact — Review Report** (handed to the user, not to another phase):

- Findings triaged as above
- Confidence read on story completion
- Suggested next step

Present the Review Report to the user. They decide what to address — tight-loop fixes in the main agent for simple issues, or re-spawn Implement with an amended Spec if findings are structural.

## Handoff discipline

- Do not start a phase without its input artifact. Missing artifact means the previous phase didn't finish.
- Do not skip the Clarify checkpoint. If it feels skippable, the task was probably too small for the workflow — drop the workflow and say so.
- Significant deviations in the Implementation Report → loop back to Clarify, not forward to Review.
- Must-fix findings in the Review Report → user chooses: main-agent fix or re-Implement.

## Why this shape

Four phases exist because each solves a distinct failure mode:

- **Orient** exists because premature implementation is the most common failure — the agent writes working code that solves the wrong problem. A "what don't I know yet" artifact before any questions are asked is cheap insurance.
- **Clarify** exists because unknowns the agent doesn't surface become assumptions the user didn't get to veto. A numbered question list invites cheap corrections.
- **Implement in a fresh subagent** exists because the main agent's Clarify-phase conversation creates biases ("the user seemed to want X") that aren't in the written Spec. Handing off to a fresh context forces the Spec to carry the full signal — and exposes Spec weaknesses as ambiguity reports rather than as silent drift.
- **Review in a second fresh subagent** exists because authors are weak reviewers of their own work. A reader without the author's context sees the code the way the next engineer will.

Artifacts stay in conversation context rather than on disk. The cost of disk I/O, stale state, and cleanup is not worth it for a single story. If an artifact grows unwieldy, that is a signal the story is too large for one delivery — not that the artifact format is wrong.
