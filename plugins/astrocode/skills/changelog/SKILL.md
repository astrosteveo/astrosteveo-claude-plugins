---
name: changelog
user-invocable: false
description: >
  Generate release notes and changelogs from git history. Parses conventional
  commits into grouped sections, supports multiple output formats (markdown,
  plain text, user-facing copy). Use when the user says "changelog", "release
  notes", "what changed", "generate changelog", "write release notes", or
  "what's new since [version/date]". Also use when the user runs /changelog.
compatibility: Requires git with conventional commit history.
metadata:
  author: astrosteveo
  version: 1.0.0
  category: release
  tags: [changelog, release-notes, git, versioning]
---

# Changelog

Generate changelogs and release notes from git commit history. Works with conventional commits to produce structured, readable output for developers, users, or app store listings.

## Instructions

### Step 1: Determine Range

Figure out what period to cover:

1. **User specifies a range:** "changelog since v1.2" or "what changed since last week" — use that.
2. **User says "changelog" with no range:** Look for the most recent tag (`git tag --sort=-creatordate | head -1`). If tags exist, use `TAG..HEAD`. If no tags, use the last 20 commits or ask the user.
3. **User specifies a date:** Convert to a git range: `git log --after="DATE" --oneline`

### Step 2: Collect Commits

```bash
git log --oneline --no-merges [RANGE]
```

Filter out `chore: update project state` and other noise commits (pure housekeeping with no user-facing impact).

### Step 3: Parse and Categorize

Group commits by conventional commit type:

| Type | Section Header | Included |
|------|---------------|----------|
| `feat` | **New Features** | Always |
| `fix` | **Bug Fixes** | Always |
| `perf` | **Performance** | If present |
| `refactor` | **Improvements** | If present |
| `docs` | *(omit unless user asks)* | On request |
| `test` | *(omit unless user asks)* | On request |
| `chore` | *(omit unless user asks)* | On request |
| `ci` | *(omit unless user asks)* | On request |
| `style` | *(omit unless user asks)* | On request |

Within each section, list items newest-first.

### Step 4: Generate Output

Produce the changelog in the requested format. If no format specified, default to **developer markdown**.

#### Format: Developer Markdown (default)

```markdown
## [version or date range]

### New Features
- **description** — brief explanation ([commit hash])
- **description** — brief explanation ([commit hash])

### Bug Fixes
- **description** — brief explanation ([commit hash])

### Performance
- **description** — brief explanation ([commit hash])
```

#### Format: User-Facing (for app stores, emails, announcements)

Translate technical commit messages into plain language. Drop implementation details. Focus on what changed for the user.

```markdown
## What's New

- You can now [feature in user terms]
- Fixed an issue where [bug in user terms]
- [Improvement] is now faster/more reliable
```

Rules for user-facing copy:
- No code references, file paths, or technical jargon
- Start each item with a verb or "You can now..."
- Group related changes into single bullet points
- Skip internal refactors, test changes, and tooling updates entirely

#### Format: Plain Text

Same as developer markdown but without formatting. For pasting into Slack, Discord, etc.

### Step 5: Present and Offer Options

Show the changelog and ask:

> "Here's the changelog. Want me to adjust the format, combine any items, or generate a user-facing version?"

## Tagging (Optional)

If the user wants to tag a release:

1. Suggest a version number based on changes:
   - Breaking changes → major bump
   - New features → minor bump
   - Fixes only → patch bump
2. Offer to create the tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
3. Do NOT push the tag unless the user explicitly asks

## Important

- **Don't fabricate changes.** Only include what's in the git history.
- **Collapse related commits.** If 3 commits all fix the same feature, present them as one item.
- **Filter noise.** "chore: update project state", merge commits, and pure refactors with no user impact should be omitted from user-facing output.
- **Respect the range.** Don't include commits outside the specified range.
- **Preserve attribution.** Keep commit hashes in developer format for traceability.
