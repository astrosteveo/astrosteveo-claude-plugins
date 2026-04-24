---
description: Four-phase delivery workflow (orient, clarify, implement, review) where an independent subagent reviews the final diff so the implementer is never the reviewer. Invoke only when the user explicitly types /scoped-delivery — it should not auto-trigger.
argument-hint: "<task description>"
---

# Scoped Delivery

Take one idea from invocation to reviewed, ready-to-ship change. `$ARGUMENTS` is the user's task description — typically a one-liner along the lines of "implement X so that Y," where X is the change and Y is the measurable outcome.

Four phases, each producing a named artifact that becomes the input to the next. The final Review phase runs in a fresh subagent that did not see the implementation — that independence is what the skill is actually paying for. The reasoning is in "Why this shape" at the end; read it if you're tempted to skip steps.

## When to drop the workflow

The user opted in by typing `/scoped-delivery`, but they may have reached for it reflexively. If the task described in `$ARGUMENTS` is:

- A single-file edit, rename, or typo fix
- Already specified with complete acceptance criteria and no unknowns
- A hotfix where speed outweighs rigor

Say so plainly, recommend doing it directly, and stop. Running the workflow on something that doesn't need it wastes the user's time and teaches them to distrust the skill.

If the user asked for **several bundled changes** ("add auth, refactor billing, and update docs"), ask them to pick one. This skill delivers *one* unit of work — that's where the name comes from.

## Phase 1 — Orient

**Goal:** build enough context to ask the right questions. Not to design the solution.

Read `$ARGUMENTS` carefully. If it names a measurable outcome ("so that X"), treat that as the seed for acceptance criteria — do not invent a different one in Clarify unless the user's answers reshape it. For any task touching code you don't already have context on, spawn an `Explore` subagent to locate relevant files, surrounding patterns, and constraints (tests, types, existing conventions). For narrow tasks, direct `Grep`/`Read` is fine.

Do not start sketching implementation yet. The point of Orient is to surface *what you don't know*, not to resolve it. Resolved unknowns belong in Clarify.

**Exit artifact — Orientation Brief** (keep in conversation; do not write to disk):

- Restated task in your own words (one paragraph — this is where misunderstandings surface)
- Relevant files (path + one-line role)
- Existing patterns to match, or reasons to diverge
- Open questions and unknowns (the list Clarify will resolve)

## Phase 2 — Clarify

**Goal:** resolve every open question and pin down the task's boundaries before code is written.

Clarify scales with ambiguity. Calibrate the depth to what `$ARGUMENTS` and the Orientation Brief actually need:

- **Ambiguous or under-specified input** — this is where most of the work lives. Actively probe; don't just log the ambiguity and wait. Ask the open questions as a numbered list so the user can answer inline. When direction is open, propose two or three concrete approaches with tradeoffs and ask which fits — people react better to options than to a blank page. Push back when an answer doesn't fit the constraints you saw in Orient. If a user answer opens a new question, ask it. Keep going until both of you believe you're building the same thing.
- **Already-crisp input** — if `$ARGUMENTS` already specifies what to build and how we'll know it's done, and Orient surfaced no real unknowns, don't manufacture questions. Restate the Spec in your own words, confirm the acceptance criteria you inferred, and ask the user to sign off. A tight confirmation beat is the whole phase.

In both modes, restate answers (or the Spec) back to the user — restatement catches misunderstandings cheaply, before they're baked into code.

Clarify is where this skill earns its keep. Skipping it collapses the workflow into "main agent with extra steps." Do not begin Phase 3 until the user has explicitly confirmed the Delivery Spec. A nodded "sure, go" is fine; silence is not consent.

**Exit artifact — Delivery Spec:**

- Orientation Brief (unchanged)
- Resolved decisions — each open question, the user's answer, any rationale they gave
- Out-of-scope list — what we explicitly are NOT doing. This is as important as the in-scope list; without it, the implementer invents features that weren't asked for.
- Acceptance criteria — how we will know the task is delivered

## Phase 3 — Implement

**Goal:** produce the change.

Implement in the main agent, treating the Delivery Spec as the written contract. Staying in the main agent (rather than handing off to a subagent) is deliberate: implementation benefits from live course-correction — running tests, trying things in a dev server, noticing a constraint mid-edit and pausing to ask the user. A fresh subagent can't do any of that, and the Review phase already provides the bias-free reading of the final diff.

Guardrails while implementing:

- Build what the Delivery Spec describes — no more, no less. If you're about to add something that isn't in it, stop and ask.
- If something turns out to be ambiguous or wrong in the Spec, do not paper over it. Return to the user, resolve it, and amend the Spec before continuing. A drifted Spec makes Review unable to judge fidelity.
- Keep notes on deviations as you go so the Implementation Report is accurate, not reconstructed from memory.

**Exit artifact — Implementation Report:**

- Files changed (path + what changed + why)
- Deviations from the Spec, with reasoning and the user's sign-off where it applied
- TODOs or follow-ups left behind

If there are open deviations the user hasn't signed off on, resolve them before Review — findings on a shaky base are noise.

## Phase 4 — Review (fresh subagent)

**Goal:** independent eyes that weren't present during Implement. This is the phase the whole workflow is built around.

Spawn a fresh `general-purpose` Agent. Pass it **only** the Delivery Spec, the Implementation Report, and the diff — not the conversation history, not your own running commentary. The subagent should read the code the way the next engineer on the team would: without your rationalizations in its ear.

Ask for findings triaged into:

- **must-fix** — bugs, broken acceptance criteria, security issues
- **should-fix** — quality concerns worth addressing before shipping
- **nit** — preferences and minor cleanups

Also ask for a confidence read: does the change deliver what the Spec scoped, and nothing more?

**Exit artifact — Review Report** (handed to the user, not to another phase):

- Findings triaged as above
- Confidence read on completion
- Suggested next step

Present the Review Report to the user. They decide what to address — tight-loop fixes in the main agent for simple issues, or amend the Spec and loop back to Implement if findings are structural.

## Handoff discipline

- Do not start a phase without its input artifact. Missing artifact means the previous phase didn't finish.
- Do not skip the Clarify checkpoint. If it feels skippable, the task was probably too small for the workflow — drop the workflow and say so.
- Amend the Spec before continuing if Implementation uncovers something that invalidates it.
- Must-fix findings in the Review Report → user chooses: main-agent fix or re-Implement with an amended Spec.

## Why this shape

Four phases exist because each solves a distinct failure mode:

- **Orient** exists because premature implementation is the most common failure — the agent writes working code that solves the wrong problem. A "what don't I know yet" artifact before any questions are asked is cheap insurance.
- **Clarify** exists because unknowns the agent doesn't surface become assumptions the user didn't get to veto. A numbered question list invites cheap corrections.
- **Implement in the main agent** (not a subagent) exists because writing code benefits from live adaptation — running tests, noticing a constraint mid-edit, pausing to ask. A subagent can't do any of that; forcing the handoff trades a real benefit for a formalism. The Delivery Spec is the written contract, and the Review phase catches drift.
- **Review in a fresh subagent** exists because authors are weak reviewers of their own work. A reader without the author's context sees the code the way the next engineer will. This is the anti-bias mechanism the skill is actually paying for — everything else is setup for this phase.

Artifacts stay in conversation context rather than on disk. The cost of disk I/O, stale state, and cleanup is not worth it for a single task. If an artifact grows unwieldy, that is a signal the task is too large for one delivery — not that the artifact format is wrong.
