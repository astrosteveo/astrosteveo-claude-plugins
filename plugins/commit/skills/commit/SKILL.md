---
description: Creates Conventional Commits for each logical unit of work. Use when the user says "commit", "commit my changes", "create commits", or "commit this work". Not for commit advice, history, or reverting.
argument-hint: "[optional message]"
---

# Commit

Look at the uncommitted changes. Group them into logical units. Write a Conventional Commits message for each. Commit.

If `$ARGUMENTS` is non-empty, use it as message guidance.

Conventional Commits format and type list: see `references/conventional-commits.md`.

## Diff
!`git status`
!`git diff --cached`
!`git diff`
!`git log --oneline -10`
