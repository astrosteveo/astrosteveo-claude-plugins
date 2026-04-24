# BACKLOG.md template

Structure for `BACKLOG.md` at the repo root — the one artifact this skill puts on disk. When the file doesn't yet exist, create it from the template below verbatim. When it already exists, keep the four section headers stable (even when a section is empty) so the file stays easy to scan and so new entries have an obvious home.

## Template

Copy the block between the two `---` fences into `BACKLOG.md`:

---

```markdown
# Backlog

Work consciously deferred from past `/scoped-delivery` sessions. Remove entries when they ship — the commit history is the audit trail.

Format: one bullet per item, prefixed with the date it was added (`[YYYY-MM-DD]`). Keep context tight but sufficient to pick the item up months later without the session transcript.

## Ready

<!-- Scoped enough to start a new /scoped-delivery session on. Top of the list is what's most likely next. -->

## Deferred

<!-- Raised in Clarify or declared out-of-scope by a past Delivery Spec; not yet ready to pick up. -->

## Follow-ups

<!-- Should-fix findings, nits, and TODOs left behind by past Implementations. -->

## Blocked

<!-- Waiting on an external signal — name the blocker inline. -->
```

---

## Categories

The four sections are fixed. Items move between them as state changes.

- **Ready** — scoped enough that the next `/scoped-delivery` session could pick it up. Top of the list is the most-likely next.
- **Deferred** — out-of-scope items from a past Delivery Spec, or features raised in Clarify and consciously postponed. Not yet ready to pick up; missing scope, dependencies, or a decision.
- **Follow-ups** — should-fix findings the user chose not to address, nits, and TODOs left behind by past Implementations.
- **Blocked** — anything waiting on an external signal. Name the blocker inline (e.g., `blocked on: upstream v2 release`).

Typical transitions: `Deferred → Ready` once the item gets scoped; `Ready → Blocked` when a dependency surfaces; `Follow-ups → Ready` when a small cleanup gets promoted to its own delivery.

## Entry format

One line per item:

```
- [YYYY-MM-DD] Short description — optional why/source
```

- The date is when the item was **added** to the backlog, not when it was picked up. Leave it untouched when moving an item between categories so staleness stays visible.
- If an entry needs more than one line to be intelligible, it probably belongs in an issue tracker. Link out rather than expanding inline.
- Include source when useful for follow-ups (e.g., `— from Review Report on auth refactor`).

## Rules

- **Remove on ship, don't archive.** When a delivery lands an item, delete the bullet. No "Done" section — git log is the audit trail and an archive would grow forever.
- **Keep empty headers.** Don't delete a section just because it's empty; the header tells future readers where a new item belongs.
- **Only record consciously deferred work.** Not every idea that floated past in Clarify — just the ones the user explicitly chose to postpone.
- **One item, one place.** If something could go in two categories, pick the one that reflects its current state (Blocked over Ready, Ready over Deferred).
