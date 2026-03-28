---
name: commit
description: "Creates Conventional Commits for each logical unit of work in the current git diff. Use when the user says 'commit', 'commit my changes', 'create commits', 'commit this work', or runs /commit. Do NOT trigger when the user is asking for help, advice, or explanations about commits — e.g. 'help me write a commit message', 'how do I write a commit message', explaining commit history, reverting commits, or understanding conventions. Only trigger when the user wants commits created from their current changes. Analyzes staged and unstaged changes, groups them into logical units, presents a commit plan for approval, then creates one well-formatted commit per unit. Follows the Conventional Commits specification (type(scope): description)."
---

# Commit

Create Conventional Commits for each logical unit of work identified in the current git diff.

## Current State

### Git Status
!`git status`

### Change Overview
!`git diff --cached --stat`
!`git diff --stat`

### Staged Changes
!`git diff --cached`

### Unstaged Changes
!`git diff`

### Untracked Files
!`git ls-files --others --exclude-standard | while read -r f; do echo "=== $f ==="; head -20 "$f"; echo; done`

### Recent Commits
!`git log --oneline -10 || echo "(no commits yet — this is a fresh repository)"`

## Instructions

### Step 1: Review State

Review the git state above. If there are no changes (clean working tree), inform the user and stop.

If the Staged Changes section is non-empty, the user has intentionally staged those files. Treat the pre-staged files as a distinct first commit group. Do not unstage them or re-stage other files into that group.

### Step 2: Analyze, Group, and Classify

Review all changes and group them into logical units of work, assigning each unit a Conventional Commit type in the same pass.

Grouping guidelines:
- If changes are already staged, those files form the first commit group
- Changes to the same feature or component typically belong together
- A bug fix and its test belong in the same commit
- Documentation updates for a code change belong with that change
- Unrelated changes should be separate commits
- Refactoring should be separate from feature/fix commits
- If all changes are part of one logical unit, create one commit

Assign each unit a type:

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

### Step 3: Present the Commit Plan

Present the plan to the user in this format:

```
Commit Plan:

1. type(scope): description
   Files: file1.js, file2.js
   Why: brief rationale for the type choice

2. type(scope): description
   Files: file3.js
   Why: brief rationale for the type choice
```

The "Why" line is especially important for borderline decisions (e.g., refactor vs. feat, fix vs. chore). Keep it to one sentence.

Wait for user approval before proceeding. If the user wants changes, adjust and re-present.

### Step 4: Execute Commits

For each approved unit of work, in order:

1. Stage the specific files by name: `git add file1.js file2.js`
2. Create the commit with the approved message
3. Verify the commit succeeded

Rules:
- If a commit group consists entirely of pre-staged files, skip `git add` — they are already staged
- For groups mixing pre-staged and unstaged files, only `git add` the files not yet staged
- Never use `git add -A`, `git add --all`, or `git add .` — stage specific files by name
- Do not add Co-Authored-By trailers — Claude Code attribution settings handle this
- Pass multi-line commit messages via a HEREDOC
- If a pre-commit hook fails, fix the issue and create a NEW commit (do not use --amend)

### Step 5: Summary

After all commits are created, show the new commits via `git log --oneline`.

## Commit Message Format

Follow the Conventional Commits 1.0.0 specification exactly.

### Structure

```
type(scope): description

body

footer(s)
```

### Header (required)

```
type[optional scope][optional !]: description
```

- **type** — A noun classifying the change. `feat` and `fix` are spec-mandated; others are conventional (see type table in Step 2).
- **scope** — Optional noun in parentheses naming the affected area: `fix(parser):`, `feat(auth):`.
- **`!`** — Optional, placed immediately before the colon to flag a breaking change: `feat!:`, `feat(api)!:`. When present, the `BREAKING CHANGE:` footer MAY be omitted and the description serves as the breaking change explanation.
- **description** — MUST immediately follow the colon and space. A short summary of the code changes in imperative mood ("add feature" not "added feature"). Keep the full header line under 72 characters (git best practice, not part of the CC spec, but strongly recommended).

### Body (optional)

- MUST begin one blank line after the description
- Free-form, may contain multiple newline-separated paragraphs
- Use the body to explain *why* the change was made and contrast with previous behavior

### Footers (optional)

- MUST begin one blank line after the body (or after the description if no body)
- Each footer: a word token, then either `: ` or ` #` as separator, then a string value
- Footer tokens MUST use `-` in place of spaces (e.g., `Acked-by`, `Reviewed-by`), except `BREAKING CHANGE` which is the sole exception
- `BREAKING CHANGE: description` — MUST be uppercase. Synonymous with `BREAKING-CHANGE:`. Indicates a breaking API change.
- `Refs: #123` or `Closes #456` — reference issues using ` #` separator

### Breaking changes

Breaking changes MUST be indicated in one of two ways (or both):
1. `!` before the colon in the header: `feat(api)!: remove endpoint`
2. `BREAKING CHANGE:` footer: `BREAKING CHANGE: /v1/users endpoint removed`

### Case sensitivity

All parts of the commit message are case-insensitive EXCEPT `BREAKING CHANGE` which MUST be uppercase.

## Examples

### Example 1: Single unit of work
User says: "/commit"
Git diff shows: auth module changes + its tests
Plan:
1. `feat(auth): add JWT token refresh on expiry`
   Files: src/auth.js, tests/auth.test.js
   Why: new capability, not modifying existing refresh behavior

### Example 2: Multiple units of work
User says: "commit my changes"
Git diff shows: bug fix in API + unrelated README update + new config file
Plan:
1. `fix(api): handle null response from upstream service`
   Files: src/api/handler.js
   Why: fixes a crash when upstream returns null, not a new feature
2. `docs: update setup instructions in README`
   Files: README.md
   Why: only markdown changes, no code affected
3. `chore: add production config template`
   Files: config/production.template.json
   Why: config template, not a source or test change

### Example 3: Pre-staged changes
User says: "/commit"
Staged changes: two files the user already staged via `git add`
Unstaged changes: unrelated formatting fix
Plan:
1. `feat(auth): add session timeout configuration`
   Files: src/auth.js, src/config.js (pre-staged)
   Why: new capability — user intentionally staged these together
2. `style: fix whitespace in utils`
   Files: src/utils.js
   Why: formatting only, no logic change

## Troubleshooting

**No changes detected**
The working tree is clean. Make changes before running /commit.

**Pre-commit hook failure**
Fix the issue identified by the hook, re-stage the files, and create a NEW commit. Do not use --amend as it would modify the previous commit.

**User disagrees with grouping**
Ask the user how they would like to group the changes. Adjust the plan and re-present for approval.
