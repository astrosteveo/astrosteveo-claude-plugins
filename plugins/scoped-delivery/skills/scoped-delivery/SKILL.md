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

**Goal:** build enough context to ask the right questions and, later, to produce a high-confidence implementation plan. Not to design the solution yet.

Read `$ARGUMENTS` carefully. If it names a measurable outcome ("so that X"), treat that as the seed for acceptance criteria — do not invent a different one in Clarify unless the user's answers reshape it.

**Do the research now, not during Implement.** Tokens spent in Orient are cheap relative to the cost of implementing the wrong thing. Err toward over-investigating; a thicker brief makes Clarify sharper and Implement shorter.

- **Codebase** — Spawn an `Explore` subagent at thoroughness "very thorough" for any task touching existing code. Ask for relevant files, surrounding patterns, existing conventions, test layout, types, callers/callees, and anything that constrains how the change must fit. Direct `Grep`/`Read` is acceptable only for genuinely narrow tasks (one-file edits, obvious-target changes).
- **Libraries and frameworks** — When the task involves a library, framework, SDK, API, or CLI tool, fetch current docs (Context7 MCP via `resolve-library-id` → `query-docs` when available). Training data may be stale; don't plan against assumptions.
- **External context** — Use `WebSearch`/`WebFetch` for anything not in the repo or library docs (RFCs, vendor behavior, known bugs, advisories).

Do not start sketching implementation yet. The point of Orient is to surface *what you don't know* and arm yourself with enough context to resolve it efficiently in Clarify. Resolved unknowns belong in Clarify; the implementation plan itself lives in the Delivery Spec.

**Exit artifact — Orientation Brief** (keep in conversation; do not write to disk):

- Restated task in your own words (one paragraph — this is where misunderstandings surface)
- Relevant files (path + one-line role)
- Existing patterns to match, or reasons to diverge
- Library/external findings that shape the plan (versions, APIs, gotchas)
- Open questions and unknowns (the list Clarify will resolve)

## Phase 2 — Clarify

**Goal:** resolve every open question, pin down the task's boundaries, and produce a detailed implementation plan before code is written.

**Default: one question at a time.** Ask the single highest-leverage open question, wait for the user's answer, then decide the next one based on what they said. Sequential questioning keeps the investigation open — each answer may surface a new unknown, trigger more research (re-spawn `Explore`, fetch more docs), or reshape the plan. Batching questions up-front freezes the tree of possibilities prematurely and invites the user to answer ones that no longer matter.

A numbered list is acceptable only when the remaining questions are genuinely independent — answering one cannot change whether the others matter. When in doubt, go one at a time.

Calibrate depth to ambiguity:

- **Ambiguous or under-specified input** — this is where most of the work lives. Actively probe. When direction is open, propose two or three concrete approaches with tradeoffs and ask which fits — people react better to options than to a blank page. Push back when an answer doesn't fit the constraints you saw in Orient. If a user answer opens a new question or a new research need, pursue it before moving on.
- **Already-crisp input** — if `$ARGUMENTS` already specifies what to build and how we'll know it's done, and Orient surfaced no real unknowns, don't manufacture questions. Restate the Spec in your own words, confirm acceptance criteria, and ask the user to approve.

In both modes, restate each answer back to the user immediately — restatement catches misunderstandings cheaply, before they're baked into the plan.

**Explicit approval gate.** Do not begin Phase 3 until the user writes the literal word **"approved"** (case-insensitive) in response to the assembled Delivery Spec. "Sure, go" / "looks good" / "lgtm" / silence are all insufficient. The hard keyword exists so investigation stays open as long as it needs to — the user is the only one who decides when ambiguity is gone. If new questions surface after you present the Spec, keep clarifying; do not lower the bar to move on.

**Exit artifact — Delivery Spec** (this is the implementation plan, not a bare confirmation):

- Orientation Brief (updated with anything Clarify surfaced)
- Resolved decisions — each open question, the user's answer, any rationale they gave
- Out-of-scope list — what we explicitly are NOT doing. This is as important as the in-scope list; without it, the implementer invents features that weren't asked for.
- Acceptance criteria — how we will know the task is delivered
- **Implementation plan** — concrete enough that Phase 3 is mostly mechanical:
  - File-by-file change list (path, what changes, why)
  - Order of operations (what gets edited first, dependencies between edits)
  - Test strategy (which tests to add or update, how they exercise the acceptance criteria)
  - Edge cases and how each is handled
  - Verification steps (commands to run, manual checks)

A thick plan here is the whole point of the workflow: heavy upfront planning means a lighter Implement phase and a Review phase that can judge fidelity against a written contract instead of chasing intent.

## Phase 3 — Implement

**Goal:** execute the plan.

Implement in the main agent, treating the Delivery Spec as the written contract. Because Clarify produced a file-by-file plan with an explicit order of operations and verification steps, Phase 3 is mostly mechanical — walk the plan in order, run the verification steps, and report. Staying in the main agent (rather than handing off to a subagent) still matters for live course-correction — running tests, trying things in a dev server, noticing a constraint the plan missed.

Guardrails while implementing:

- Build what the Delivery Spec describes — no more, no less. If you're about to add something that isn't in it, stop and ask.
- If something in the plan turns out to be wrong or ambiguous, do not paper over it. Return to the user, resolve it, amend the Spec, and re-secure "approved" before continuing. A drifted Spec makes Review unable to judge fidelity.
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

**Verify the fixes.** After any must-fix or should-fix changes land, spawn a *second* fresh `general-purpose` Agent and pass it the original Review Report plus the diff of the fixes. Its job is narrow: confirm each prior finding was actually addressed and that the fixes did not introduce new issues. The implementer is a poor judge of their own work during the fix loop too — the skill is still paying for independence here. Loop until the verification pass comes back clean.

## Phase 5 — Closeout

**Goal:** ship clean, capture what was deferred, reset for the next unit of work.

Only enter Closeout once Review is clean — no outstanding must-fix findings and the verification pass returned empty.

**Update `BACKLOG.md` at the repo root.** This is the one artifact deliberately on disk: it persists across sessions because that's its purpose. If the file doesn't exist, create it from the template in `references/backlog-template.md` — keep the four section headers stable so entries always have an obvious home.

Route anything this delivery surfaced but did not ship into the matching category:

- **Ready** — scoped enough to start a new `/scoped-delivery` session on
- **Deferred** — out-of-scope items from the Delivery Spec, and features raised in Clarify but consciously postponed
- **Follow-ups** — should-fix or nit findings the user chose not to address, and TODOs from the Implementation Report
- **Blocked** — items waiting on an external signal; name the blocker inline

Each entry is a one-liner prefixed with today's date (`[YYYY-MM-DD]`), tight but sufficient to pick up months later without the session transcript. Only record items that were *consciously deferred* — not every idea that floated past.

**Also: if this delivery fully shipped an item previously on the backlog, delete that bullet.** Don't archive it — the commit history is the audit trail, and the point of the file is to stay minimal.

**Remind the user to commit and reset.** Close the session with two lines:

- Run `/commit:commit` to land this delivery.
- Start a new session for the next task — one logical unit of work per session is what keeps scoped-delivery honest, because the next task gets its own Orient phase instead of inheriting state from this one.

Do not run the commit yourself and do not offer to chain into the next task. The fresh session is part of the design.

## Handoff discipline

- Do not start a phase without its input artifact. Missing artifact means the previous phase didn't finish.
- Do not skip the Clarify checkpoint. If it feels skippable, the task was probably too small for the workflow — drop the workflow and say so.
- Do not enter Phase 3 without the literal "approved" from the user on the Delivery Spec. Re-secure "approved" on any amendment.
- Amend the Spec before continuing if Implementation uncovers something that invalidates it.
- Must-fix findings in the Review Report → user chooses: main-agent fix or re-Implement with an amended Spec.
- After applying Review-Report fixes, run the verification pass in a fresh subagent. Do not declare Review clean on your own judgment.
- Do not enter Closeout with unresolved must-fix findings or a skipped verification pass.

## Why this shape

Four phases exist because each solves a distinct failure mode:

- **Orient** exists because premature implementation is the most common failure — the agent writes working code that solves the wrong problem. Front-loading codebase and library research here (via `Explore` and external docs) is deliberately expensive; tokens spent learning are cheap relative to tokens spent implementing the wrong thing.
- **Clarify** exists because unknowns the agent doesn't surface become assumptions the user didn't get to veto. One question at a time keeps the investigation tree open — each answer can spawn the next question or a new research need, which a batched list would suppress. The "approved" keyword gate exists because polite hedges ("looks good", "sure") get misread as consent; a literal keyword is harder to fake. The Delivery Spec is a detailed implementation plan, not a bare confirmation, because the heavier the plan, the lighter Phase 3 and the sharper Phase 4.
- **Implement in the main agent** (not a subagent) still exists because writing code benefits from live adaptation — running tests, noticing a constraint mid-edit, pausing to ask. With a thick plan from Clarify, Implement becomes closer to execution than design, which is the whole point.
- **Review in a fresh subagent** exists because authors are weak reviewers of their own work. A reader without the author's context sees the code the way the next engineer will. This is the anti-bias mechanism the skill is actually paying for — everything else is setup for this phase. The verification pass after fixes exists for the same reason: the implementer's confidence that "that finding is now addressed" is not the same as an independent check that it is.
- **Closeout** exists because the shape of the workflow only pays off if each delivery ends cleanly: one commit, one session, and a written record of what was deferred. Without `BACKLOG.md`, "out-of-scope" decays into forgotten-about. Without the session-reset reminder, state from this delivery leaks into the next one and the next Orient phase starts half-compromised.

In-flight artifacts stay in conversation context rather than on disk. The cost of disk I/O, stale state, and cleanup is not worth it for a single task. If an artifact grows unwieldy, that is a signal the task is too large for one delivery — not that the artifact format is wrong. `BACKLOG.md` is the deliberate exception: it is explicitly meant to outlive the session, which is what makes it worth the disk.
