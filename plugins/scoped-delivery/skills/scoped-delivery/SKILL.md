---
description: Four-phase delivery workflow (orient, clarify, implement, review) where an independent subagent reviews the final diff so the implementer is never the reviewer. Invoke only when the user explicitly types /scoped-delivery — it should not auto-trigger.
argument-hint: "<task description>"
---

# Scoped Delivery

Take one idea from invocation to reviewed, ready-to-ship change. `$ARGUMENTS` is the user's task description — typically a one-liner along the lines of "implement X so that Y," where X is the change and Y is the measurable outcome.

Four phases, each producing a named artifact that becomes the input to the next. The final Review phase runs in a fresh subagent that did not see the implementation — that independence is what the skill is actually paying for.

**The agent does its own work.** The user brings the outcome they want; everything else — research, lookups, framing — is the agent's job, not theirs. Anything you can find out yourself, find out yourself. The user is asked only what only they can answer.

**Keep artifacts tight.** Artifacts are working scaffolding, not documents. One line per item; references over duplication; coverage over prose. The user shouldn't have to scroll to find the decision. If an artifact is growing past a screen, the task is too big for one delivery — split it, don't pad it.

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

The implementation plan lives in the Delivery Spec, not here — Orient ends when you know what you don't know and, for research-pending items, have closed them.

**Exit artifact — Orientation Brief** (in conversation; not on disk):

- Restated task (1-2 sentences — where misunderstandings surface)
- Relevant files (`path: role`)
- Patterns to match, or reasons to diverge (one line each)
- Library / external findings that shape the plan (one line each)
- Remaining unknowns, split into **user-only** (only the user can answer) and **research-pending** (the agent must close before Clarify). Only user-only items reach Clarify.

## Phase 2 — Clarify

**Goal:** resolve every open question, pin down the task's boundaries, and produce a detailed implementation plan before code is written.

**Before asking anything, triage.** For each open item, ask: can I answer this myself with Explore, docs, or a probe? If yes, do that first — do not route lookup questions through the user to manufacture a checkpoint. The user is asked only what only they can answer: intent, priorities, tradeoffs, and acceptance of recommendations. Facts about the codebase, libraries, APIs, or external systems are the agent's job, full stop.

**Default: one question at a time.** Ask the single highest-leverage open question, wait for the user's answer, then decide the next one based on what they said. Sequential questioning keeps the investigation open — each answer may surface a new unknown, trigger more research (re-spawn `Explore`, fetch more docs), or reshape the plan. Batching questions up-front freezes the tree of possibilities prematurely and invites the user to answer ones that no longer matter.

A numbered list is acceptable only when the remaining questions are genuinely independent — answering one cannot change whether the others matter. When in doubt, go one at a time.

Calibrate depth to ambiguity:

- **Ambiguous or under-specified input** — this is where most of the work lives. Actively probe *yourself first* (re-spawn Explore, fetch docs, test an API call) and only surface what remains genuinely user-only. When direction is truly open on a user-only axis, present two or three concrete approaches with tradeoffs and **mark one as recommended** so the user can skim, accept, or push back with minimum effort. Push back when an answer doesn't fit the constraints you saw in Orient. If a user answer opens a new question or a new research need, pursue it before moving on.
- **Already-crisp input** — if `$ARGUMENTS` already specifies what to build and how we'll know it's done, and Orient surfaced no real unknowns, don't manufacture questions. Restate the Spec in your own words, confirm acceptance criteria, and ask the user to approve.

In both modes, restate each answer back to the user immediately — restatement catches misunderstandings cheaply, before they're baked into the plan. Restate research findings the same way — when an Explore result or a doc lookup changes the shape of the plan, say so explicitly ("the API actually returns X, so option B no longer applies") before continuing.

**Option format.** When a question has a shortlist of plausible answers, lay them out so the user can reply with a single letter. Keep options short enough to read at a glance and always name a pragmatic recommendation with a one-sentence reason — a default makes the choice feel like "confirm or redirect," not "design from scratch."

Before drafting options, verify the premise the options sit on. If the options differ along an axis like "what the API returns" or "what the library supports," confirm that axis against docs or a probe first — otherwise you are asking the user to pick between fictions. Options anchored on unverified premises are the workflow's most expensive failure mode.

```
**Q:** <the single question>

- **A) <option>** — <one-line tradeoff>
- **B) <option>** — <one-line tradeoff>
- **C) <option>** — <one-line tradeoff>

Recommend **A** because <one short reason grounded in Orient findings or stated constraints>. Reply with a letter, or push back.
```

Only use the format when there really is a choice. For open-ended questions ("what's the deadline?", "who's the primary user?"), ask plainly — fabricating options wastes the user's time.

**Explicit approval gate.** Do not begin Phase 3 until the user writes the literal word **"approved"** (case-insensitive) in response to the assembled Delivery Spec. "Sure, go" / "looks good" / "lgtm" / silence are all insufficient. The hard keyword exists so investigation stays open as long as it needs to — the user is the only one who decides when ambiguity is gone. If new questions surface after you present the Spec, keep clarifying; do not lower the bar to move on. The gate exists to confirm intent, not to convert research into ceremony. If you find yourself inventing a question so you can reach "approved," stop — do the research and present the Spec directly for approval.

**Present in chunks, not as a wall.** Walk the Spec section by section — decisions, then scope, then acceptance, then plan — each followed by "Does this look right?" and a pause. The final "approved" closes Phase 2; intermediate checks are quick reactions, not full sign-offs. A wall of text can't be scanned; chunked sections can.

**Exit artifact — Delivery Spec** (the implementation plan, not a bare confirmation):

- **Decisions** — one line each, mapping each open question to its answer
- **Out-of-scope** — one-liners; these seed `BACKLOG.md`'s **Deferred** section
- **Acceptance criteria** — numbered, terse
- **Plan** — file-by-file in order, one line per file (`path: change`); list test commands, edge cases, and verification commands as one-liners. No phase headings, no sub-essays, no rationale prose.

Do not re-paste the Brief. If a chunk exceeds a screen, the task is too big — split it.

## Phase 3 — Implement

**Goal:** execute the plan.

Implement in the main agent, treating the Delivery Spec as the written contract. Because Clarify produced a file-by-file plan with an explicit order of operations and verification steps, Phase 3 is mostly mechanical — walk the plan in order, run the verification steps, and report. Stay in the main agent so you can course-correct live — run tests, hit the dev server, catch constraints the plan missed.

Guardrails while implementing:

- Build what the Delivery Spec describes — no more, no less. If you're about to add something that isn't in it, stop and ask.
- If something in the plan turns out to be wrong or ambiguous, do not paper over it. Return to the user, resolve it, amend the Spec, and re-secure "approved" before continuing. A drifted Spec makes Review unable to judge fidelity.
- Keep notes on deviations as you go so the Implementation Report is accurate, not reconstructed from memory.
- Capture TODOs and follow-ups inline the moment you decide to leave them — they seed `BACKLOG.md`'s **Follow-ups** section at Closeout. Record them as one-liners so they can drop straight in.

**Exit artifact — Implementation Report:**

- Files changed (`path: what changed`)
- Deviations from the Spec — one line each, with the user's sign-off referenced
- TODOs and follow-ups (one-liners, ready for `BACKLOG.md`)

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

**Present in chunks if the report is long.** Walk findings tier by tier — must-fix first (the user actually needs to decide), then should-fix, then nits — pausing for the user's call on each tier. The full Report is the artifact; the presentation is paced.

Present the Review Report to the user. They decide what to address — tight-loop fixes in the main agent for simple issues, or amend the Spec and loop back to Implement if findings are structural.

**Verify the fixes.** After any must-fix or should-fix changes land, spawn a *second* fresh `general-purpose` Agent and pass it the original Review Report plus the diff of the fixes. Its job is narrow: confirm each prior finding was actually addressed and that the fixes did not introduce new issues. The implementer is a poor judge of their own work during the fix loop too — the skill is still paying for independence here. Loop until the verification pass comes back clean.

## Phase 5 — Closeout

**Goal:** ship clean, capture what was deferred, reset for the next unit of work.

Only enter Closeout once Review is clean — no outstanding must-fix findings and the verification pass returned empty.

**Update `BACKLOG.md` at the repo root.** This is the one artifact deliberately on disk: it persists across sessions because that's its purpose. If the file doesn't exist, create it from the template in `references/backlog-template.md` — keep the four section headers stable so entries always have an obvious home.

By this point most entries already exist as one-liners — the Delivery Spec's out-of-scope list, the Implementation Report's TODOs, the Review Report's unaddressed should-fix/nit items. Closeout is mostly *reconciling* that tracked list into the right category, not inventing one from memory.

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

## Why this shape

Orient is front-loaded because implementing the wrong thing is the costly failure. Clarify's "approved" gate and one-question cadence exist because unsurfaced unknowns become unvetoed assumptions. Review runs in a fresh subagent because authors are weak reviewers of their own work — that independence is what the workflow is paying for.
