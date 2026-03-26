---
name: commit
description: "Creates Conventional Commits for each logical unit of work in the current git diff. Use when the user says 'commit', 'commit my changes', 'create commits', 'commit this work', or runs /commit. Analyzes staged and unstaged changes, groups them into logical units, presents a commit plan for approval, then creates one well-formatted commit per unit. Follows the Conventional Commits specification (type(scope): description)."
---

# Commit

Create Conventional Commits for each logical unit of work identified in the current git diff.

## Instructions

### Step 1: Gather State

Run these commands in parallel to understand the current state:

1. `git status` — see all tracked/untracked changes (never use `-uall` flag)
2. `git diff` — see unstaged changes
3. `git diff --cached` — see staged changes
4. `git log --oneline -10` — see recent commits for context and style

If there are no changes (clean working tree), inform the user and stop.

### Step 2: Analyze and Group Changes

Review all changes and group them into logical units of work. A unit of work is a cohesive set of changes that belong together in a single commit.

Grouping guidelines:
- Changes to the same feature or component typically belong together
- A bug fix and its test belong in the same commit
- Documentation updates for a code change belong with that change
- Unrelated changes should be separate commits
- Refactoring should be separate from feature/fix commits
- If all changes are part of one logical unit, create one commit

### Step 3: Determine Commit Types

For each unit of work, assign a Conventional Commit type:

| Type | When to use |
|------|------------|
| `feat` | A new feature or capability |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Formatting, whitespace (no logic change) |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `build` | Build system or external dependency changes |
| `ci` | CI configuration changes |
| `chore` | Other changes that don't modify src or test files |

Scope is optional. Use it when the change is clearly scoped to a specific area (e.g., `feat(auth):`, `fix(api):`).

For breaking changes, add `!` before the colon: `feat!:` or `feat(api)!:`

### Step 4: Present the Commit Plan

Present the plan to the user in this format:

```
Commit Plan:

1. type(scope): description
   Files: file1.js, file2.js

2. type(scope): description
   Files: file3.js
```

Wait for user approval before proceeding. If the user wants changes, adjust and re-present.

### Step 5: Execute Commits

For each approved unit of work, in order:

1. Stage the specific files by name: `git add file1.js file2.js`
2. Create the commit with the approved message
3. Verify the commit succeeded

Rules:
- Never use `git add -A`, `git add --all`, or `git add .` — stage specific files by name
- Do not add Co-Authored-By trailers — Claude Code attribution settings handle this
- Pass multi-line commit messages via a HEREDOC
- If a pre-commit hook fails, fix the issue and create a NEW commit (do not use --amend)

### Step 6: Summary

After all commits are created, show the new commits via `git log --oneline`.

## Commit Message Guidelines

- First line: `type(scope): description` — keep under 72 characters
- Focus on the "why" not the "what"
- Use imperative mood: "add feature" not "added feature"
- Body (optional): explain motivation and contrast with previous behavior
- Footer (optional): reference issues, note breaking changes

## Examples

### Example 1: Single unit of work
User says: "/commit"
Git diff shows: auth module changes + its tests
Plan: `feat(auth): add JWT token refresh on expiry`
Files: src/auth.js, tests/auth.test.js

### Example 2: Multiple units of work
User says: "commit my changes"
Git diff shows: bug fix in API + unrelated README update + new config file
Plan:
1. `fix(api): handle null response from upstream service`
2. `docs: update setup instructions in README`
3. `chore: add production config template`

### Example 3: Refactor with tests
User says: "create commits for this work"
Git diff shows: extracted utility functions + updated imports + new tests
Plan:
1. `refactor: extract date formatting into shared utilities`
2. `test: add unit tests for date formatting utilities`

## Troubleshooting

**No changes detected**
The working tree is clean. Make changes before running /commit.

**Pre-commit hook failure**
Fix the issue identified by the hook, re-stage the files, and create a NEW commit. Do not use --amend as it would modify the previous commit.

**User disagrees with grouping**
Ask the user how they would like to group the changes. Adjust the plan and re-present for approval.
