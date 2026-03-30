# Report Format

How to structure and present code quality findings. The goal: high signal, easy to
act on, respectful of the codebase's history and constraints.

## Report Structure

### 1. Executive Summary

2-4 sentences covering:
- Overall codebase health assessment (healthy / needs attention / concerning)
- Total findings count broken down by severity
- Top 3 priority items to address first

### 2. Strengths

Before diving into findings, acknowledge what the codebase does well. Look for:
- Consistent patterns and conventions
- Good separation of concerns
- Solid test coverage
- Clean, well-documented architecture
- Effective use of language/framework features

This is not filler — it calibrates the reader and identifies patterns worth preserving.

### 3. Findings by Category

Group findings under category headers (Clean Code, DRY, Security, etc.). Within each
category, sort by severity (critical first, info last).

### 4. Individual Finding Format

Each finding follows this structure:

**[SEVERITY] Brief descriptive title** — `path/to/file.ext:line_number`

_What_: 1-2 sentence description of the issue.

_Why it matters_: the actual impact — security risk, maintenance burden, bug potential,
performance cost. Be specific, not generic.

_Suggested fix_: concrete, non-breaking recommendation. Include a short code snippet
showing the fix if it clarifies. Keep snippets minimal — show the pattern, not a full
rewrite.

_Effort_: Trivial (minutes) | Small (under an hour) | Medium (hours)

For systemic issues (same pattern in many files), list all locations but describe the
fix once:

**[SEVERITY] Brief title** — systemic (N occurrences)
Locations: `file1.ext:10`, `file2.ext:25`, `file3.ext:42`
[rest of finding format]

### 5. Intentional Patterns

Briefly note patterns you investigated but determined were intentional:

"Investigated [pattern] in [module] — this is intentional per [documentation/convention]."

This shows the user you understood the codebase before making recommendations. It
builds trust and saves them from having to explain their own code back to you.

## Severity Levels

| Severity | Meaning | Guidance |
|----------|---------|----------|
| CRITICAL | Security vulnerability, data loss risk, crash in production | Fix immediately — these are real risks |
| HIGH | Significant bug potential, major performance issue, maintainability blocker | Fix soon — these slow the team down |
| MEDIUM | Code smell, moderate duplication, minor performance concern | Fix when you're in this code next |
| LOW | Minor improvement, small inconsistency, minor optimization | Nice to have, not urgent |
| INFO | Observation or suggestion, not a defect | Consider — no action required |

### Severity Calibration

Err on the side of lower severity. A MEDIUM issue called HIGH wastes urgency. A HIGH
issue called MEDIUM is much less harmful — the team will still see it and can escalate.

Reserve CRITICAL for actual security vulnerabilities and data integrity risks. Code
smells are never CRITICAL, no matter how ugly.

## Tone

- **Factual, not judgmental**: "This function is 120 lines with 8 branches" — not
  "This function is a mess"
- **Respectful of context**: code has history, deadlines, and constraints. Note what
  you observe, don't assume incompetence.
- **Concrete**: every finding must answer "what should I do about this?" If you can't
  answer that, it's not ready to report.
- **Proportional**: the length of discussion should match the severity. A CRITICAL
  finding deserves a paragraph. A LOW finding needs one sentence.
