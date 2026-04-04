---
description: Detects code smells and AI-generated slop. Use when the user says "sniff this code", "check for AI slop", "is this vibe coded", "smell check", or asks whether code looks AI-generated or over-engineered. Any language or framework.
argument-hint: "[target: file, directory, or PR]"
---

# Code Sniffer

Detect code smells and AI-generated slop. Two detection layers: general code smells indicating careless or low-quality code, plus AI-slop signals indicating code was generated without thought.

If `$ARGUMENTS` specifies a target, sniff exactly that.

## How This Differs From Code Quality

Fast and opinionated. Does not build a full project mental model first. Hunts for specific smell patterns and AI slop signals. For comprehensive, context-aware quality audits, use code-quality instead.

## Workflow

### Step 1: Scope

1. **Target specified** — sniff exactly what the user asked for (file, directory, PR).
2. **No target** — ask: "What should I sniff? A specific file, directory, PR, or the whole codebase?"
3. **Whole codebase** — map source files with Glob, skip vendored/generated/build artifacts. For 200+ files, use parallel Agent subagents to map and sniff independent modules.

### Step 2: Sniff

Read the code and check against both detection layers. Consult `references/smell-catalog.md` for the full catalog of patterns and detection guidance.

**Layer 1 — General Code Smells:** Dead abstractions, cargo-culted patterns, ceremonial error handling, god files/functions, copy-paste variations, wrapper tax, premature configuration.

**Layer 2 — AI Slop Signals:** Docstring-on-everything, defensive code against impossible states, high ceremony-to-substance ratio, tests that don't test, apologetic comments, born-complete files, ceremonial security, inconsistent style, backwards-compatibility for new code, over-specified types.

### Step 3: Check Git History

Git history is a powerful slop signal. For suspicious code:

1. **Birth check** — `git log --follow --diff-filter=A` on the file. Born fully-formed in a single commit? Strong AI slop signal.
2. **Iteration check** — healthy edit history, or created once and never touched?
3. **Commit message check** — vague messages ("add feature", "update code") alongside large diffs suggest vibe-coded sessions.

Git signals are context, not proof. Some legitimate code is correct the first time.

### Step 4: Report

Produce a smell report following `references/report-format.md`.

For each finding:
1. Identify the smell by catalog name
2. Show specific code location (`path/to/file:line_number`)
3. Explain why it smells — what suggests thoughtlessness?
4. Rate the stink level
5. Flag AI slop signals explicitly

Then produce:
- **Smell summary** — counts by category and stink level
- **AI Slop Assessment** — verdict with specific evidence for and against
- **Worst offenders** — top 3-5 files/modules by smell density

## Rules

- **Be specific** — "this smells" is not a finding. Name the pattern and explain the problem.
- **No false morality** — simple code that works is good code. The enemy is unnecessary complexity, not simplicity.
- **Respect intentional patterns** — consistent patterns (even unusual ones) are probably intentional. Flag inconsistency, not unfamiliarity.
- **Git signals are context, not proof** — a file born in one commit might be a well-prepared migration.
- **AI slop is a spectrum** — code can have some signals without being entirely vibe-coded. Calibrate your assessment.
- **File references always** — `path/to/file:line_number` for every finding.

## Examples

**Sniffing a directory** — "sniff src/auth/":
1. Read all source files in src/auth/
2. Check against both layers
3. Git log on suspicious files
4. Smell report scoped to src/auth/

**AI slop check** — "is this PR vibe coded?":
1. Get PR diff, read changed files in full (context matters, not just the diff)
2. Check against AI slop signals
3. Check commit history and messages
4. Focused AI slop assessment

**Full codebase sniff** — "how smelly is this codebase?":
1. Map source files, identify modules
2. Parallel agents for large codebases
3. Sniff each module against both layers
4. Full smell report with AI slop assessment
