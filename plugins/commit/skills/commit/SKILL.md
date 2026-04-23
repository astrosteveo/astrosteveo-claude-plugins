---
description: Creates Conventional Commits for each logical unit of work. Use when the user says "commit", "commit my changes", "create commits", or "commit this work". Not for commit advice, history, or reverting.
argument-hint: "[optional message]"
---

# Commit

Create Conventional Commits for each logical unit of work in the current diff.

If `$ARGUMENTS` is non-empty, use it as guidance for commit message wording or scope.

## Git State

### Status
!`git status`

### Staged Changes
!`git diff --cached --stat`
!`git diff --cached`

### Unstaged Changes
!`git diff --stat`
!`git diff`

### Untracked Files
!`git ls-files --others --exclude-standard | while read -r f; do echo "=== $f ==="; head -20 "$f"; echo; done`

### Recent Commits
!`git log --oneline -10 || echo "(no commits yet)"`

## Workflow

### 1. Review

Examine the git state above. If the working tree is clean, inform the user and stop.

Check whether any changes are pre-staged (appear in Staged Changes). Pre-staged files represent intentional user grouping — treat them as a distinct first commit group. Never unstage or mix other files into a pre-staged group.

### 2. Group and Classify

Group all changes into logical units of work and assign each a Conventional Commit type in the same pass.

**Grouping:**
- Pre-staged files form the first group as-is
- Related feature/component changes belong together
- A bug fix and its test belong in the same commit
- Documentation for a code change belongs with that change
- Unrelated changes get separate commits
- Refactoring is separate from feature/fix work
- If everything is one logical unit, make one commit

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`

See `references/conventional-commits.md` for when to use each type.

**Scope** is optional — use when the change targets a specific area: `feat(auth):`, `fix(api):`

**Breaking changes** — add `!` before the colon: `feat!:` or `feat(api)!:`

### 3. Execute

Present the plan, then create each commit. For each unit:

1. Stage specific files: `git add file1.js file2.js`
2. Commit with the message
3. Verify the commit succeeded

**Rules:**
- Never use `git add -A`, `git add --all`, or `git add .` — always stage by filename. Bulk adds can sweep in unintended files like secrets (`.env`, credentials), build artifacts, or unrelated work-in-progress.
- Skip `git add` for groups that are entirely pre-staged
- For mixed groups (pre-staged + unstaged), only `git add` the unstaged files
- Do not add Co-Authored-By trailers — Claude Code handles attribution
- Do not commit files that likely contain secrets (.env, credentials, API keys) — warn the user instead
- Pass multi-line messages via HEREDOC:

```
git commit -m "$(cat <<'EOF'
type(scope): description

Body text here.
EOF
)"
```

- If a pre-commit hook fails: fix the issue, re-stage, and create a NEW commit (never --amend, which would modify the previous commit)

### 4. Summary

Show the new commits: `git log --oneline`

## Message Format

```
type[optional scope][optional !]: description

[optional body]

[optional footer(s)]
```

- **Header** (required): Imperative mood, under 72 characters. Example: `feat(auth): add token refresh on expiry`
- **Body** (optional): Blank line after header. Explains *why* the change was made.
- **Footers** (optional): `Refs: #123`, `Closes #456`, `BREAKING CHANGE: description` (must be uppercase)

Full specification and examples in `references/conventional-commits.md`.
