---
name: commit
user-invocable: false
description: >
  Conventional commit workflow — format, stage, commit, and update project state.
  Use when any skill needs to commit changes, or when the user says "commit",
  "commit this", "save my changes", or "commit what we did". Also use when the
  user runs /commit. This skill is also referenced by other skills (review-cycle,
  project-state) whenever they need to make commits.
---

# Commit

Stage, format, and commit changes following the [Conventional Commits](https://www.conventionalcommits.org/) standard, then update `.claude/PROGRESS.md` to keep project state in sync.

## Commit Message Format

All commits MUST follow the Conventional Commits standard:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code restructuring with no behavior change |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `docs` | Documentation only |
| `build` | Build system or dependency changes |
| `ci` | CI/CD configuration |
| `chore` | Maintenance tasks (state updates, cleanup) |
| `style` | Formatting, whitespace, semicolons — no logic change |
| `revert` | Reverts a previous commit |

### Rules

- **Scope** is optional but encouraged. Use it to identify the area of the codebase (e.g., `auth`, `api`, `ui`, `db`, `state`).
- **Description** uses imperative mood, lowercase, no trailing period. Describe what the commit does, not what you did.
- **Breaking changes** add `!` after the type/scope: `feat(api)!: change response format for /users endpoint`. Include a `BREAKING CHANGE:` footer in the body explaining the impact.
- **Body** is optional. Use it for context that doesn't fit in the description — the "why", not the "what".

### Examples

```
feat(auth): add OAuth2 login flow
fix(api): handle null response from upstream service
refactor(ui): extract shared button component
chore(state): update project state
docs(readme): add deployment instructions
perf(db): add index on users.email for login query
test(auth): cover token refresh edge cases
feat(api)!: change response format for /users endpoint
```

## Commit Workflow

### Step 1: Review changes

Run `git status` and `git diff` to understand what's being committed. Group related changes into logical commits — don't lump unrelated changes together, and don't split a single logical change across commits unnecessarily.

### Step 2: Stage and commit

1. Stage the relevant files: `git add <files>`
2. Write a conventional commit message that accurately describes the change
3. Commit: `git commit -m '<type>(<scope>): <description>'`

For multi-line messages (body or footers), use a heredoc:

```bash
git commit -m "$(cat <<'EOF'
feat(auth): add OAuth2 login flow

Implements the full authorization code grant flow with PKCE.
Tokens are stored in the session, not localStorage.

Closes #142
EOF
)"
```

### Step 3: Update project state

After every source commit, update `.claude/PROGRESS.md`:

1. Add/update a row in **Recent Changes** for what was just committed
2. Update **Active Work Streams** and **Next Steps** to reflect current reality
3. Update the header: `> Last updated: YYYY-MM-DD | Last synced at: NEW_HEAD_HASH`
4. Commit state separately: `git commit -m "chore(state): update project state" -- .claude/PROGRESS.md`

This keeps the state file in sync so the next session can pick up where this one left off. Never skip this step — stale state wastes the next session's time.

## Important

- **One logical change per commit.** If you fixed a bug and refactored nearby code, those are two commits.
- **Don't commit generated files** unless they're checked in by convention (e.g., lock files).
- **Don't commit secrets** (.env, credentials, API keys). Warn the user if they ask you to.
- **State commit is always separate.** The PROGRESS.md update gets its own `chore(state)` commit, not bundled with source changes.
- **Keep PROGRESS.md under 60 lines.** Trim old Recent Changes rows when needed.
