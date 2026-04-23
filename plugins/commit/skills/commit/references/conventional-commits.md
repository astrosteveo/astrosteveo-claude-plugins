# Conventional Commits 1.0.0

Reference for the Conventional Commits specification used by the commit skill.

## Types

| Type | When to use |
|------|------------|
| `feat` | A new feature or capability |
| `fix` | A bug fix |
| `docs` | Documentation-only changes |
| `style` | Formatting, whitespace (no logic change) |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `build` | Build system or external dependency changes |
| `ci` | CI configuration changes |
| `chore` | Other changes that don't modify src or test files |

`feat` and `fix` are mandated by the spec. The others are conventional and widely adopted.

## Header

```
type[optional scope][optional !]: description
```

- **type** — A noun classifying the change
- **scope** — Optional noun in parentheses naming the affected area: `fix(parser):`, `feat(auth):`
- **`!`** — Placed immediately before the colon to flag a breaking change: `feat!:`, `feat(api)!:`. When present, the `BREAKING CHANGE:` footer may be omitted.
- **description** — Immediately follows the colon and space. Short summary in imperative mood ("add feature" not "added feature"). Keep the full header under 72 characters.

## Body

- Begins one blank line after the header
- Free-form, may contain multiple paragraphs
- Explains *why* the change was made and contrasts with previous behavior

## Footers

- Begin one blank line after the body (or header if no body)
- Format: `Token: value` or `Token #value`
- Tokens use `-` in place of spaces (e.g., `Acked-by`, `Reviewed-by`), except `BREAKING CHANGE`
- Common footers: `Refs: #123`, `Closes #456`, `BREAKING CHANGE: description`

## Breaking Changes

Must be indicated in at least one of two ways:
1. `!` before the colon: `feat(api)!: remove endpoint`
2. `BREAKING CHANGE:` footer (must be uppercase)

Both may be used together.

## Case Sensitivity

All parts are case-insensitive except `BREAKING CHANGE` which must be uppercase.

## Examples

### Single unit — new feature with tests
```
feat(auth): add JWT token refresh on expiry
```
Files: src/auth.js, tests/auth.test.js — new capability, tests included with feature.

### Multiple units from one diff

**Commit 1:**
```
fix(api): handle null response from upstream service
```
Files: src/api/handler.js — fixes a crash, not a new feature.

**Commit 2:**
```
docs: update setup instructions in README
```
Files: README.md — only markdown changes.

**Commit 3:**
```
chore: add production config template
```
Files: config/production.template.json — config template, not src or test.

### Pre-staged changes honored
User staged src/auth.js and src/config.js, plus there is an unstaged formatting fix.

**Commit 1:**
```
feat(auth): add session timeout configuration
```
Files: src/auth.js, src/config.js (pre-staged) — user intentionally grouped these.

**Commit 2:**
```
style: fix whitespace in utils
```
Files: src/utils.js — formatting only, separate from the staged feature.

### Breaking change with body and footer
```
feat(api)!: replace /v1/users with /v2/users

The /v1/users endpoint has been removed. Clients must migrate to
/v2/users which returns a paginated response format.

BREAKING CHANGE: /v1/users endpoint removed
Refs: #892
```

## Troubleshooting

**No changes detected**
Working tree is clean. Make changes before running /commit.

**Pre-commit hook failure**
Fix the issue identified by the hook, re-stage files, and create a NEW commit. Never use --amend — it modifies the previous commit, not the failed one.
